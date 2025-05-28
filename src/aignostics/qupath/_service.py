"""Service of the QuPath module."""

import contextlib
import os
import platform
import queue
import re
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile
from collections.abc import Callable
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import appdirs
import requests
from packaging.version import Version
from pydantic import BaseModel, computed_field

from aignostics.utils import BaseService, Health, __project_name__, get_logger

from ._settings import Settings

logger = get_logger(__name__)

DOWNLOAD_CHUNK_SIZE = 1024 * 1024


class InstallProgressState(StrEnum):
    """Enum for download progress states."""

    CHECKING = "Trying to find QuPath ..."
    DOWNLOADING = "Downloading QuPath archive ..."
    EXTRACTING = "Extracting QuPath archive ..."


class InstallProgress(BaseModel):
    status: InstallProgressState = InstallProgressState.CHECKING
    archive_version: str | None = None
    archive_path: Path | None = None
    archive_size: int | None = None
    archive_downloaded_size: int = 0
    archive_download_chunk_size: int | None = None

    @computed_field  # type: ignore
    @property
    def archive_download_progress_normalized(self) -> float:
        """Compute normalized archive download progress in range 0..1.

        Returns:
            float: The normalized archive download progress in range 0..1.
        """
        if (not self.archive_size) or self.archive_size is None:
            return 0.0
        return min(1, float(self.archive_downloaded_size) / float(self.archive_size))


class Service(BaseService):
    """Service of the bucket module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)

    def info(self) -> dict[str, Any]:
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        application_path = Service.find_qupath()
        return {
            "application_path": str(application_path) if application_path else "Not found",
            "paquo": {
                "settings": self.get_paquo_settings(),
                "defaults": self.get_paquo_defaults(),
            },
        }

    def health(self) -> Health:
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={
                "application": self._determine_application_health(),
            },
        )

    @staticmethod
    def _determine_application_health() -> Health:
        """Determine we can reach a well known and secure endpoint.

        - Checks if health endpoint is reachable and returns 200 OK
        - Uses requests library for a direct connection check without authentication

        Returns:
            Health: The healthiness of the network connection via basic unauthenticated request.
        """
        try:
            path = Service.find_qupath()
            if not path:
                message = "QuPath executable not found."
                return Health(status=Health.Code.DOWN, reason=message)
        except Exception as e:
            message = f"Exception while checking health of QuPath application {e!s}"
            logger.exception(message)
            return Health(status=Health.Code.DOWN, reason=message)
        return Health(status=Health.Code.UP)

    @staticmethod
    def get_paquo_defaults() -> dict[str, Any]:
        """Get settings for this service.

        Returns:
            str: Default settings in TOML format.
        """
        from paquo._config import settings  # noqa: PLC0415, PLC2701

        toml = files("paquo").joinpath(".paquo.defaults.toml").read_text(encoding=str(settings.ENCODING_FOR_DYNACONF))
        return tomllib.loads(toml)

    @staticmethod
    def get_paquo_settings() -> dict[str, Any]:
        """Get settings for this service.

        Returns:
            str: Default settings in TOML format.
        """
        from paquo._config import settings  # noqa: PLC0415, PLC2701

        return dict(settings.to_dict(internal=False))

    @staticmethod
    def find_qupath() -> Path | None:
        """Check if QuPath is installed.

        Raises:
            ValueError: If the QuPath executable is not found or if the installation is invalid.

        Returns:
            Path | None: Path to the QuPath executable if found, otherwise None.
        """
        from paquo._config import settings, to_kwargs  # noqa: PLC0415, PLC2701
        from paquo.jpype_backend import find_qupath as paquo_find_qupath  # noqa: PLC0415

        try:
            app_dir, _, _, _ = paquo_find_qupath(**to_kwargs(settings))
        except ValueError as e:
            message = f"No QuPath installation found: {e!s}"
            return None
        system = platform.system()

        if system == "Linux":
            (qupath,) = Path(app_dir).parent.parent.joinpath("bin").glob("QuPath*")

        elif system == "Darwin":
            (qupath,) = Path(app_dir).parent.joinpath("MacOS").glob("QuPath*")

        elif system == "Windows":
            qp_exes = list(Path(app_dir).parent.glob("QuPath*.exe"))
            if len(qp_exes) != 2:  # noqa: PLR2004
                message = (
                    f"Expected to find exactly 2 QuPath executables, got {qp_exes}. "
                    "Please ensure you have the correct QuPath installation."
                )
                raise ValueError(message)
            (qupath,) = (qp for qp in qp_exes if "console" in qp.stem)

        if not qupath.is_file():
            return None
        return qupath

    @staticmethod
    def get_installation_path() -> Path:
        """Get the installation directory of QuPath.

        Returns:
            Path: The directory QuPath will be installed into.
        """
        return Path(appdirs.user_data_dir(__project_name__))

    @staticmethod
    def _download_qupath(  # noqa: C901, PLR0912, PLR0915
        version: str,
        path: Path,
        download_progress: Callable | None = None,  # type: ignore[type-arg]
        install_progress_queue: queue.Queue[InstallProgress] | None = None,
        system: str | None = None,
    ) -> Path:
        """Download qupath from GitHub.

        Args:
            version (str): Version of QuPath to download.
            path (Path): Path to directory save the downloaded file to.
            download_progress (Callable | None): Callback function for download progress.
            install_progress_queue (Any | None): Queue for download progress updates, if applicable.
            system (str, optional): The system platform. If None, it will use platform.system().

        Raises:
            ValueError: If the platform.system() is not supported.
            RuntimeError: If the download fails or if the file cannot be saved.
            Exception: If there is an error during the download.

        Returns:
            Path: The path object of the downloaded file.
        """
        if system is None:
            system = platform.system()

        if system == "Linux":
            sys = "Linux"
            ext = "tar.xz"
        elif system == "Darwin":
            sys = "Mac"
            ext = "pkg"
        elif system == "Windows":
            sys = "Windows"
            ext = "zip"
        else:
            error_message = f"unsupported platform.system() == {system!r}"
            raise ValueError(error_message)

        if not version.startswith("v"):
            version = f"v{version}"

        if Version(version) > Version("0.4.4"):
            if system == "Darwin":
                sys = "Mac-arm64" if platform.machine() == "arm64" else "Mac-x64"
            name = f"QuPath-{version}-{sys}"
        elif Version(version) > Version("0.3.2"):
            if system == "Darwin":
                sys = "Mac-arm64" if platform.machine() == "arm64" else "Mac"
            name = f"QuPath-{version[1:]}-{sys}"
        elif "rc" not in version:
            name = f"QuPath-{version[1:]}-{sys}"
        else:
            name = f"QuPath-{version[1:]}"

        url = f"https://github.com/qupath/qupath/releases/download/{version}/{name}.{ext}"

        filename = Path(urlsplit(url).path).name
        filepath = path / filename

        try:  # noqa: PLR1702
            with requests.get(url, stream=True, timeout=60) as stream:
                stream.raise_for_status()
                download_size = int(stream.headers.get("content-length", 0))
                downloaded_size = 0
                with open(filepath, mode="wb") as file:
                    for chunk in stream.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                        if chunk:
                            downloaded_size += len(chunk)
                            file.write(chunk)
                            if download_progress:
                                download_progress(filepath, download_size, len(chunk))
                            if install_progress_queue:
                                progress = InstallProgress(
                                    status=InstallProgressState.DOWNLOADING,
                                    archive_version=version,
                                    archive_path=filepath,
                                    archive_size=download_size,
                                    archive_downloaded_size=downloaded_size,
                                    archive_download_chunk_size=len(chunk),
                                )
                                install_progress_queue.put_nowait(progress)
        except requests.RequestException as e:
            message = f"Failed to download QuPath from {url}="
            logger.exception(message)
            raise RuntimeError(message) from e
        except Exception:
            logger.exception("Error downloading QuPath from %s", url)
            with contextlib.suppress(OSError):
                filepath.unlink(missing_ok=True)
            raise
        else:
            return filepath

    @staticmethod
    def _extract_qupath(  # noqa: C901, PLR0912, PLR0915
        archive_path: Path, installation_path: Path, overwrite: bool = False, system: str | None = None
    ) -> Path:
        """Extract downloaded QuPath installation archive to the specified destination directory.

        Args:
            archive_path (Path): Path to the downloaded QuPath archive.
            installation_path (Path): Path to the directory where QuPath should be extracted.
            overwrite (bool): If True, will overwrite existing files in the installation path.
            system (str | None): The system platform. If None, it will use platform.system().

        Raises:
            ValueError: If there is broken input.
            RuntimeError: If an unexpected error happens.

        Returns:
            Path: The path to the extracted QuPath application directory.
        """
        m = re.match(
            r"QuPath-v?(?P<version>[0-9]+[.][0-9]+[.][0-9]+(-rc[0-9]+|-m[0-9]+)?)",
            archive_path.name,
        )
        if not m:
            message = f"file: {archive_path.name} does not match expected QuPath filename pattern"
            logger.error(message)
            raise ValueError(message)

        if system is None:
            system = platform.system()

        if system in {"Linux", "Windows"}:
            app_dir = f"QuPath-{m.group('version')}"
        elif system == "Darwin":
            app_dir = f"QuPath-{m.group('version')}.app"
        else:
            message = f"unsupported platform.system() == {system!r}"
            raise ValueError(message)

        if not installation_path.is_dir():
            message = f"installation path '{installation_path!r}' is not a directory"
            logger.error(message)
            raise ValueError(message)

        destination = installation_path / app_dir

        if destination.is_dir() and not overwrite:
            message = "QuPath installation directory already exists at '{destination_dir!r}'. "
            logger.warning(message)
            return destination

        if system == "Linux":
            if archive_path.suffix != ".tar.xz":
                message = f"archive '{archive_path!r}' does not end with `.tar.xz`"
                logger.error(message)
                raise ValueError(message)
            with tempfile.TemporaryDirectory() as tmp_dir:
                with tarfile.open(archive_path, mode="r:xz") as tf:
                    tf.extractall(tmp_dir)  # nosec: B202  # noqa: S202
                    for path in Path(tmp_dir).iterdir():
                        name = path.name
                        if name.startswith("QuPath") and path.is_dir():
                            break
                        message = f"expected QuPath directory, got {name!r}"
                        logger.error(message)
                        raise RuntimeError(message)
                extract_dir = Path(tmp_dir) / name
                if (extract_dir / "QuPath").is_dir():
                    # in some cases there is a nested QuPath directory
                    extract_dir /= "QuPath"
                shutil.move(extract_dir, installation_path)
            return destination

        if system == "Darwin":
            if archive_path.suffix != ".pkg":
                message = f"archive '{archive_path!r}' does not end with `.pkg`"
                logger.error(message)
                raise ValueError(message)
            if shutil.which("7z") is None:
                message = "7z is required to extract QuPath on macOS, run: `brew install p7zip`"
                logger.error(message)
                raise ValueError(message)

            with tempfile.TemporaryDirectory() as tmp_dir:
                expanded_pkg_dir = Path(tmp_dir) / "expanded_pkg"  # pkgutil will create the directory
                try:
                    subprocess.run(  # noqa: S603
                        ["pkgutil", "--expand", str(archive_path.resolve()), str(expanded_pkg_dir.resolve())],  # noqa: S607
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
                    message = f"Failed to expand .pkg file: {e!s}\nstderr:\n{stderr_output}"
                    logger.exception(message)
                    raise RuntimeError(message) from e

                payload_path = None
                for path in Path(tmp_dir).rglob("Payload*"):
                    if path.is_file() and (path.name == "Payload" or path.name.startswith("Payload")):
                        payload_path = path
                        break
                if not payload_path:
                    message = "No Payload file found in the expanded .pkg"
                    logger.error(message)
                    raise RuntimeError(message)
                payload_extract_dir = Path(tmp_dir) / "payload_contents"
                payload_extract_dir.mkdir(parents=True, exist_ok=True)
                try:
                    subprocess.run(  # noqa: S603
                        [  # noqa: S607
                            "sh",
                            "-c",
                            f"cd '{payload_extract_dir.resolve!s}' && cat '{payload_path!s}' | gunzip -dc | cpio -i",
                        ],
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
                    message = f"Failed to expand .pkg file: {e!s}\nstderr:\n{stderr_output}"
                    logger.exception(message)
                    raise RuntimeError(message) from e

                for root, dirs, _ in os.walk(payload_extract_dir):
                    for name in dirs:
                        if name.startswith("QuPath") and name.endswith(".app"):
                            app_path = Path(root) / name
                            shutil.move(app_path, installation_path)
                            return installation_path

                message = "No QuPath application found in the extracted contents"
                logger.error(message)
                raise RuntimeError(message)

        if system == "Windows":
            if archive_path.suffix != ".zip":
                message = f"archive '{archive_path!r}' does not end with `.zip`"
                logger.error(message)
                raise ValueError(message)

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                with zipfile.ZipFile(archive_path, mode="r") as zf:
                    zf.extractall(tmp_path)  # nosec: B202  # noqa: S202
                    for item in tmp_path.iterdir():
                        if item.name.startswith("QuPath") and item.is_dir():
                            pth = item
                            break
                        if item.name.startswith("QuPath") and item.suffix == ".exe" and item.is_file():
                            pth = tmp_path
                            break
                    else:
                        message = "No QuPath extracted?"
                        logger.error(message)
                        raise RuntimeError(message)
                shutil.move(str(pth), installation_path)
            return installation_path

        message = f"unsupported platform.system() == {system!r}"
        logger.error(message)
        raise RuntimeError(message)

    @staticmethod
    def install_qupath(
        version: str = "0.5.1",
        path: Path | None = None,
        download_progress: Callable | None = None,  # type: ignore[type-arg]
        extract_progress: Callable | None = None,  # type: ignore[type-arg]
        progress_queue: queue.Queue[InstallProgress] | None = None,
    ) -> Path:
        """Install QuPath application.

        Args:
            version (str): Version of QuPath to install. Defaults to "0.5.1".
            path (Path | None): Path to install QuPath to.
                If not specified, the home directory of the user will be used.
            download_progress (Callable | None): Callback function for download progress.
            extract_progress (Callable | None): Callback function for extraction progress.
            progress_queue (queue.Queue[InstallProgress] | None): Queue for download progress updates, if applicable.

        Raises:
            RuntimeError: If the download fails or if the file cannot be extracted.
            Exception: If there is an error during the download or extraction.

        Returns:
            Path: The path to the executable of the installed QuPath application.
        """
        path = Service.get_installation_path()

        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                message = f"Failed to create directory {path}: {e!s}"
                logger.exception(message)
                raise RuntimeError(message) from e
        try:
            archive_path = Service._download_qupath(
                version=version,
                path=path,
                download_progress=download_progress,
                install_progress_queue=progress_queue,
                system=None,
            )
            application_pathname = Service._extract_qupath(
                archive_path=archive_path, installation_path=path, system=platform.system()
            )
            if extract_progress:
                extract_progress(archive_path, application_pathname)
            application_path = Path(application_pathname)
            if not application_path.is_dir():
                message = f"QuPath directory not found as expected: {application_path}"
                logger.error(message)
                raise RuntimeError(message)  # noqa: TRY301
            if extract_progress:
                application_size = 0
                for file_path in application_path.glob("**/*"):
                    if file_path.is_file():
                        application_size += file_path.stat().st_size
                extract_progress(application_path, application_size=application_size)
            qupath_executable = Service.find_qupath()
            if not qupath_executable:
                message = "QuPath executable not found after installation."
                logger.error(message)
                raise RuntimeError(message)  # noqa: TRY301
            qupath_executable.chmod(0o755)  # Make sure the executable is runnable
            return qupath_executable
        except Exception as e:
            message = f"Failed to download QuPath version {version} to {path}: {e!s}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def launch_qupath() -> bool:
        """Launch QuPath application.

        Returns:
            bool: True if QuPath was launched successfully, False otherwise.

        """
        application_path = Service.find_qupath()
        message = f"QuPath executable found at: {application_path}"
        logger.debug(message)
        if not application_path:
            logger.error("QuPath executable not found.")
            return False
        match platform.system():
            case "Linux":
                command = [str(application_path)]
            case "Darwin":
                command = [str(application_path)]
            case "Windows":
                command = [str(application_path), "--console"]
            case _:
                message = f"Unsupported platform: {platform.system()}"
                logger.error(message)
                raise NotImplementedError(message)
        subprocess.Popen(command, start_new_session=True)  # noqa: S603
        return True


os.environ["PAQUO_QUPATH_SEARCH_DIRS"] = str(Service.get_installation_path())
