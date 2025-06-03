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
import time
import tomllib
import zipfile
from collections.abc import Callable
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import appdirs
import ijson
import requests
from packaging.version import Version
from pydantic import BaseModel, computed_field

from aignostics.utils import BaseService, Health, __project_name__, get_logger

from ._settings import Settings

logger = get_logger(__name__)

QUPATH_VERSION = "0.6.0-rc5"
DOWNLOAD_CHUNK_SIZE = 10 * 1024 * 1024
LAUNCH_MAX_WAIT_TIME = 60  # seconds, maximum wait time for QuPath to start

IMAGE_SUFFIXES = {".dcm", ".tiff", ".tif", ".svs"}
PROJECT_FILENAME = "project.qpproj"
ANNOTATIONS_BATCH_SIZE = 500000


class QuPathVersion(BaseModel):
    """Class to store QuPath version information."""

    version: str
    build_time: str | None = None
    commit_tag: str | None = None


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
        return min(1, float(self.archive_downloaded_size + 1) / float(self.archive_size))


class AddProgressState(StrEnum):
    """Enum for download progress states."""

    INITIALIZING = "Initializing ..."
    CREATING_PROJECT = "Creating project ..."
    FINDING_IMAGES = "Finding images ..."
    ADDING_IMAGES = "Adding images ..."
    COMPLETED = "Completed."


class AddProgress(BaseModel):
    status: AddProgressState = AddProgressState.INITIALIZING
    image_count: int | None = None
    image_index: int = 0
    image_path: Path | None = None

    @computed_field  # type: ignore
    @property
    def progress_normalized(self) -> float:
        """Compute normalized progress in range 0..1.

        Returns:
            float: The normalized progress in range 0..1.
        """
        if not self.image_count:
            return 0.0
        return min(1, float(self.image_index + 1) / float(self.image_count))


class AnnotateProgressState(StrEnum):
    """Enum for download progress states."""

    INITIALIZING = "Initializing ..."
    OPENING_PROJECT = "Opening project ..."
    FINDING_IMAGE = "Finding image ..."
    COUNTING = "Counting annotations ..."
    ANNOTATING = "Annotating image ..."
    COMPLETED = "Completed."


class AnnotateProgress(BaseModel):
    status: AnnotateProgressState = AnnotateProgressState.INITIALIZING
    image_path: Path | None = None
    annotation_count: int | None = None
    annotation_index: int = 0
    annotation_path: Path | None = None

    @computed_field  # type: ignore
    @property
    def progress_normalized(self) -> float:
        """Compute normalized progress in range 0..1.

        Returns:
            float: The normalized progress in range 0..1.
        """
        if not self.annotation_count:
            return 0.0
        return min(1, float(self.annotation_index) / float(self.annotation_count))


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
        version = Service.get_version()
        return {
            "qupath": {
                "application_path": str(application_path) if application_path else "Not found",
                "version": dict(version) if version else None,
            },
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
            version = Service.get_version()
            if not version:
                message = "QuPath not installed."
                return Health(status=Health.Code.DOWN, reason=message)
            if version.version != Service.get_expected_version():
                message = f"QuPath version mismatch: expected {QUPATH_VERSION}, got {version.version}"
                logger.warning(message)
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
    def _app_dir_from_qupath_dir_for_platform_override(qupath_dir: Path, platform_system: str) -> Path:
        """Get the QuPath application directory based on the platform system.

        Args:
            qupath_dir (Path): The QuPath installation directory.
            platform_system (str): The system platform (e.g., "Linux", "Darwin", "Windows").

        Returns:
            str: The path to the QuPath application directory.

        Raises:
            FileNotFoundError: If the QuPath application directory does not exist.
        """
        if platform_system == "Linux":
            app_dir = qupath_dir / "lib" / "app"

        elif platform_system == "Darwin":
            app_dir = qupath_dir / "Contents" / "app"

        elif platform_system == "Windows":
            app_dir = qupath_dir / "app"

        if not (app_dir.is_dir()):
            message = f"QuPath installation directory is not a directory: s{app_dir!s}"
            raise FileNotFoundError(message)

        return app_dir

    @staticmethod
    def is_installed(
        platform_system: str | None = None,
    ) -> bool:
        """Check if QuPath is installed.

        Args:
            platform_system (str | None): The system platform. If None, it will use platform.system().

        Returns:
            bool: True if QuPath is installed, False otherwise.
        """
        return Service.get_version(platform_system=platform_system) is not None

    @staticmethod
    def get_expected_version() -> str:
        """Get expected version.

        Returns:
            QuPathVersion | None: The version of QuPath if installed, otherwise None.
        """
        return QUPATH_VERSION

    @staticmethod
    def get_version(platform_system: str | None = None) -> QuPathVersion | None:
        """Get the version of the installed QuPath.

        Args:
            platform_system (str | None): The system platform. If None, it will use platform.system().

        Returns:
            QuPathVersion | None: The version of QuPath if installed, otherwise None.
        """
        path = Service.find_qupath(platform_system=platform_system)
        # Open the QuPath with --version and read version info.

        if not path:
            logger.warning("QuPath executable not found.")
            return None

        try:
            result = subprocess.run(  # noqa: S603
                [str(path), "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

            output = result.stdout.strip()
            logger.debug("QuPath version output: %s", output)

            # Handle version patterns with or without "-rc" suffix
            # First try to match the standard "Version:" pattern
            version_match = re.search(r"Version:\s+([0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?)", output)

            # If standard pattern fails, try to match "QuPath vX.X.X" pattern
            if not version_match:
                version_match = re.search(r"QuPath\s+v([0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?)", output)

            build_time_match = re.search(r"Build time:\s+(.+)", output)
            commit_tag_match = re.search(r"Latest commit tag:\s+[\"']?(.+?)[\"']?(?:\s|$)", output)

            if version_match:
                version = version_match.group(1)
                build_time = build_time_match.group(1) if build_time_match else None
                commit_tag = commit_tag_match.group(1) if commit_tag_match else None

                return QuPathVersion(version=version, build_time=build_time, commit_tag=commit_tag)
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            logger.warning("Failed to get QuPath version from executable: %s", e)
        except Exception:
            logger.exception("Unexpected error getting QuPath version")

        return None

    @staticmethod
    def find_qupath(
        platform_system: str | None = None,
    ) -> Path | None:
        """Check if QuPath is installed.

        Args:
            platform_system (str | None): The system platform. If None, it will use platform.system().

        Raises:
            ValueError: If the QuPath executable is not found or if the installation is invalid.

        Returns:
            Path | None: Path to the QuPath executable if found, otherwise None.
        """
        from paquo._config import settings, to_kwargs  # noqa: PLC0415, PLC2701
        from paquo.jpype_backend import find_qupath as paquo_find_qupath  # noqa: PLC0415

        system = platform.system() if platform_system is None else platform_system

        try:
            app_dir, _, _, _ = paquo_find_qupath(**to_kwargs(settings))
        except ValueError as e:
            # Unluckily paquo does not stringently allow to override the system,
            # so we have to do it ourselves.
            if (platform_system is not None) and (platform_system != platform.system()):
                qupath_dirs = [
                    d
                    for d in Service.get_installation_path().iterdir()
                    if d.is_dir() and re.match(r"(?i)qupath.*", d.name)
                ]
                if not qupath_dirs:
                    message = f"No QuPath directory found at {Service.get_installation_path()!s}"
                    logger.debug(message)
                    raise ValueError(message) from e

                app_dir = Service._app_dir_from_qupath_dir_for_platform_override(
                    qupath_dir=qupath_dirs[0],
                    platform_system=platform_system,
                )
            else:
                # We don't log, to not spam the logs because this is a common case
                return None

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
    def is_qupath_installed() -> bool:
        """Check if QuPath is installed.

        Returns:
            bool: True if QuPath is installed, False otherwise.
        """
        return Service.find_qupath() is not None

    @staticmethod
    def get_installation_path() -> Path:
        """Get the installation directory of QuPath.

        Returns:
            Path: The directory QuPath will be installed into.
        """
        return Path(appdirs.user_data_dir(__project_name__))

    @staticmethod
    def _download_qupath(  # noqa: C901, PLR0912, PLR0913, PLR0915, PLR0917
        version: str,
        path: Path,
        platform_system: str | None = None,
        platform_machine: str | None = None,
        download_progress: Callable | None = None,  # type: ignore[type-arg]
        install_progress_queue: queue.Queue[InstallProgress] | None = None,
    ) -> Path:
        """Download QuPath from GitHub.

        Args:
            version (str): Version of QuPath to download.
            path (Path): Path to directory save the downloaded file to.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine  (str | None): The machine architecture. If None, it will use platform.machine().
            download_progress (Callable | None): Callback function for download progress.
            install_progress_queue (Any | None): Queue for download progress updates, if applicable.

        Raises:
            ValueError: If the platform.system() is not supported.
            RuntimeError: If the download fails or if the file cannot be saved.
            Exception: If there is an error during the download.

        Returns:
            Path: The path object of the downloaded file.
        """
        system = platform.system() if platform_system is None else platform_system
        machine = platform.machine() if platform_machine is None else platform_machine
        logger.debug("Downloading QuPath version %s for system %s and machine %s", version, system, machine)

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
                sys = "Mac-arm64" if machine == "arm64" else "Mac-x64"
            name = f"QuPath-{version}-{sys}"
        elif Version(version) > Version("0.3.2"):
            if system == "Darwin":
                sys = "Mac-arm64" if machine == "arm64" else "Mac"
            name = f"QuPath-{version[1:]}-{sys}"
        elif "rc" not in version:
            name = f"QuPath-{version[1:]}-{sys}"
        else:
            name = f"QuPath-{version[1:]}"

        url = f"https://github.com/qupath/qupath/releases/download/{version}/{name}.{ext}"

        logger.debug("Downloading QuPath from %s", url)

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
            logger.debug("Downloaded QuPath archive to '%s'", filepath)
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
    def get_app_dir(
        version: str, installation_path: Path, platform_system: str | None = None, platform_machine: str | None = None
    ) -> Path:
        """Get the the QuPath application directory.

        Args:
            version (str): Version of QuPath.
            installation_path (Path): Path to the installation directory.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine (str | None): The machine architecture. If None, it will use platform.machine().

        Returns:
            str: The version of QuPath extracted from the

        Raises:
            ValueError: If the version does not match the expected pattern or if the system is unsupported.
        """
        system = platform.system() if platform_system is None else platform_system
        machine = platform.machine() if platform_machine is None else platform_machine
        logger.debug(
            "Getting QuPath application directory for version '%s', installation path '%s' on system '%s'",
            version,
            installation_path,
            system,
        )

        m = re.match(
            r"v?(?P<version>[0-9]+[.][0-9]+[.][0-9]+(-rc[0-9]+|-m[0-9]+)?)",
            version,
        )
        if not m:
            message = f"version '{version}' does not match expected QuPath version pattern"
            logger.error(message)
            raise ValueError(message)
        version = m.group("version")

        if system == "Windows":
            return installation_path / Path(f"QuPath-{version}")
        if system == "Linux":
            return installation_path / Path("QuPath")
        if system == "Darwin":
            arch = "arm64" if machine == "arm64" else "x64"
            return installation_path / Path(f"QuPath-{version}-{arch}.app")
        message = f"unsupported platform.system() == {system!r}"
        raise ValueError(message)

    @staticmethod
    def _extract_qupath(  # noqa: C901, PLR0912, PLR0915
        archive_path: Path,
        installation_path: Path,
        overwrite: bool = False,
        platform_system: str | None = None,
        platform_machine: str | None = None,
    ) -> Path:
        """Extract downloaded QuPath installation archive to the specified destination directory.

        Args:
            archive_path (Path): Path to the downloaded QuPath archive.
            installation_path (Path): Path to the directory where QuPath should be extracted.
            overwrite (bool): If True, will overwrite existing files in the installation path.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine (str | None): The machine architecture. If None, it will use platform.machine().

        Raises:
            ValueError: If there is broken input.
            RuntimeError: If an unexpected error happens.

        Returns:
            Path: The path to the extracted QuPath application directory.
        """
        system = platform.system() if platform_system is None else platform_system
        logger.debug("Extracting QuPath archive '%s' to '%s' for system %s", archive_path, installation_path, system)

        destination = Service.get_app_dir(
            version=QUPATH_VERSION,
            installation_path=installation_path,
            platform_system=platform_system,
            platform_machine=platform_machine,
        )

        if destination.is_dir():
            if overwrite:
                with tempfile.TemporaryDirectory() as nirvana:
                    message = (
                        f"QuPath installation directory already exists at '{destination!s}', moving to nirvana ..."
                    )
                    logger.warning(message)
                    shutil.move(destination, nirvana)
            else:
                message = f"QuPath installation directory already exists at '{destination!s}', breaking. "
                logger.warning(message)
                return destination

        if system == "Linux":
            if not archive_path.name.endswith(".tar.xz"):
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
                    else:
                        message = "No QuPath directory found in the extracted contents."
                        logger.error(message)
                        raise RuntimeError(message)
                extract_dir = Path(tmp_dir) / name
                if (extract_dir / "QuPath").is_dir():
                    # in some cases there is a nested QuPath directory
                    extract_dir /= "QuPath"
                shutil.move(extract_dir, installation_path)
            archive_path.unlink(missing_ok=True)  # remove the archive after extraction
            return destination

        if system == "Darwin":
            if archive_path.suffix != ".pkg":
                message = f"archive '{archive_path!s}' does not end with `.pkg`"
                logger.error(message)
                raise ValueError(message)

            if platform.system() not in {"Darwin", "Linux"}:
                message = f"Unsupported platform.system() == {platform.system()!r} for pkgutil"
                logger.error(message)
                raise ValueError(message)

            with tempfile.TemporaryDirectory() as tmp_dir:
                expanded_pkg_dir = Path(tmp_dir) / "expanded_pkg"  # pkgutil will create the directory
                try:
                    command = (
                        ["pkgutil", "--expand", str(archive_path.resolve()), str(expanded_pkg_dir.resolve())]
                        if platform.system() == "Darwin"
                        else ["7z", "x", str(archive_path.resolve()), "-o" + str(expanded_pkg_dir.resolve())]
                    )
                    subprocess.run(  # noqa: S603
                        command,
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
                    message = f"Failed to expand .pkg file: {e!s}\nstderr:\n{stderr_output}"
                    logger.exception(message)
                    raise RuntimeError(message) from e

                payload_path = None
                for path in expanded_pkg_dir.rglob("Payload*"):
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
                    command = (
                        [
                            "sh",
                            "-c",
                            f"cd '{payload_extract_dir.resolve()!s}' && "
                            f"cat '{payload_path.resolve()!s}' | gunzip -dc | cpio -i",
                        ]
                        if platform.system() == "Darwin"
                        else ["7z", "x", str(payload_path.resolve()), "-o" + str(payload_extract_dir.resolve())]
                    )
                    subprocess.run(  # noqa: S603
                        command,
                        capture_output=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    stderr_output = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
                    message = f"Failed to expand .pkg file: {e!s}\nstderr:\n{stderr_output}"
                    logger.exception(message)
                    raise RuntimeError(message) from e

                for app_path in payload_extract_dir.glob("**/*"):
                    if app_path.is_dir() and app_path.name.startswith("QuPath") and app_path.name.endswith(".app"):
                        shutil.move(app_path, installation_path)
                        archive_path.unlink(missing_ok=True)  # remove the archive after extraction
                        return destination

                message = "No QuPath application found in the extracted contents"
                logger.error(message)
                raise RuntimeError(message)

        if system == "Windows":
            if archive_path.suffix != ".zip":
                message = f"archive '{archive_path!s}' does not end with `.zip`"
                logger.error(message)
                raise ValueError(message)

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / destination.name
                with zipfile.ZipFile(archive_path, mode="r") as zf:
                    zf.extractall(tmp_path)  # nosec: B202  # noqa: S202
                    for item in tmp_path.iterdir():
                        if item.name.startswith("QuPath") and item.is_file() and item.suffix == ".exe":
                            pth = tmp_path
                            break
                    else:
                        message = "No QuPath directory or .exe found in the extracted contents."
                        logger.error(message)
                        raise RuntimeError(message)
                shutil.move(pth, installation_path)
            archive_path.unlink(missing_ok=True)  # remove the archive after extraction
            return destination

        message = f"unsupported platform.system() == {system!r}"
        logger.error(message)
        raise RuntimeError(message)

    @staticmethod
    def install_qupath(  # noqa: PLR0913, PLR0917
        version: str = QUPATH_VERSION,
        path: Path | None = None,
        reinstall: bool = True,
        platform_system: str | None = None,
        platform_machine: str | None = None,
        download_progress: Callable | None = None,  # type: ignore[type-arg]
        extract_progress: Callable | None = None,  # type: ignore[type-arg]
        progress_queue: queue.Queue[InstallProgress] | None = None,
    ) -> Path:
        """Install QuPath application.

        Args:
            version (str): Version of QuPath to install. Defaults to "0.5.1".
            path (Path | None): Path to install QuPath to.
                If not specified, the home directory of the user will be used.
            reinstall (bool): If True, will reinstall QuPath even if it is already installed.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine (str | None): The machine architecture. If None, it will use platform.machine().
            download_progress (Callable | None): Callback function for download progress.
            extract_progress (Callable | None): Callback function for extraction progress.
            progress_queue (queue.Queue[InstallProgress] | None): Queue for download progress updates, if applicable.

        Raises:
            RuntimeError: If the download fails or if the file cannot be extracted.
            Exception: If there is an error during the download or extraction.

        Returns:
            Path: The path to the executable of the installed QuPath application.
        """
        if path is None:
            path = Service.get_installation_path()

        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                message = f"Failed to create installation directory '{path}': {e!s}"
                logger.exception(message)
                raise RuntimeError(message) from e
        try:
            archive_path = Service._download_qupath(
                version=version,
                path=path,
                platform_system=platform_system,
                platform_machine=platform_machine,
                download_progress=download_progress,
                install_progress_queue=progress_queue,
            )
            message = f"QuPath archive downloaded to '{archive_path!s}'."
            logger.debug(message)

            application_path = Service._extract_qupath(
                archive_path=archive_path,
                installation_path=path,
                overwrite=reinstall,
                platform_system=platform_system,
                platform_machine=platform_machine,
            )
            if not application_path.is_dir():
                message = f"QuPath directory not found as expected at '{application_path!s}'."
                logger.error(message)
                raise RuntimeError(message)  # noqa: TRY301
            message = f"QuPath application extracted to '{application_path!s}'."
            logger.debug(message)

            if extract_progress:
                application_size = 0
                for file_path in application_path.glob("**/*"):
                    if file_path.is_file():
                        application_size += file_path.stat().st_size
                message = f"Total size of QuPath application: '{application_size}' bytes"
                logger.debug(message)
                extract_progress(application_path, application_size=application_size)

            qupath_executable = Service.find_qupath(
                platform_system=platform_system,
            )
            if not qupath_executable:
                message = "QuPath executable not found after installation."
                logger.error(message)
                raise RuntimeError(message)  # noqa: TRY301
            message = f"QuPath executable found at '{qupath_executable!s}'."
            logger.debug(message)

            qupath_executable.chmod(0o755)  # Make sure the executable is runnable
            message = f"Set permissions set to 755 for QuPath executable at '{qupath_executable!s}'."
            logger.debug(message)

            return application_path
        except Exception as e:
            message = f"Failed to install QuPath v{version} to '{path!s}': {e!s}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def launch_qupath(  # noqa: C901, PLR0912
        quiet: bool = True,
        project: Path | None = None,
        image: str | Path | None = None,
        script: str | Path | None = None,
    ) -> int | None:
        """Launch QuPath application.

        Args:
            quiet (bool): If True, will launch QuPath in quiet mode (no GUI).
            project (Path | None): Path to the QuPath project to open. If None, no project will be opened.
            image: str | Path | None: Path to the image file to open in QuPath. If project path given as well,
                this must be the name of the image within project as str.
            script (str | Path | None): Path to the script to run in QuPath. If None, no script will be run.

        Returns:
            bool: True if QuPath was launched successfully, False otherwise.

        """
        application_path = Service.find_qupath()
        if not application_path:
            logger.error("QuPath executable not found.")
            return None

        message = f"QuPath executable found at: {application_path}"
        logger.debug(message)

        if platform.system() in {"Linux", "Darwin", "Windows"}:
            command = [str(application_path)]
            if script:
                command.extend(["script"])
            if quiet and not script:
                command.append("-q")
            if image:
                command.extend(["-i", str(image)])
            if project:
                command.extend(["-p", str(project.resolve() / PROJECT_FILENAME)])
            if script:
                command.extend([str(script)])
        else:
            message = f"Unsupported platform: {platform.system()}"
            logger.error(message)
            raise NotImplementedError(message)

        try:
            logger.debug("Launching QuPath with command: %s", " ".join(command))
            process = subprocess.Popen(  # noqa: S603
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            if not process.stdout:
                logger.error("QuPath process has no stdout.")
                return None

            start_time = time.time()
            while True:
                waited = time.time() - start_time
                if time.time() - start_time > LAUNCH_MAX_WAIT_TIME:
                    message = f"Timed out after {waited:.2f} seconds waiting for QuPath to start"
                    logger.error(message)
                    return None

                # Check if there's any output available
                output = process.stdout.readline() if process.stdout.readable() else ""
                exit_code = process.poll()

                # Exit if process has terminated with no output
                if not output and exit_code is not None:
                    message = f"QuPath process has terminated with exit code '{exit_code}'."
                    logger.debug(message)
                    break

                # Process output if available
                if output:
                    logger.debug(output.strip())
                    if "qupath.lib.gui.QuPathApp - Starting QuPath with parameters" in output:
                        logger.debug("QuPath started successfully.")
                        return process.pid

                # Small sleep to prevent CPU hogging
                time.sleep(0.1)
            return None
        except Exception as exc:
            message = f"Failed to launch QuPath: {exc!s}"
            logger.exception(message)
            return None

    @staticmethod
    def uninstall_qupath(
        version: str | None = None,
        path: Path | None = None,
        platform_system: str | None = None,
        platform_machine: str | None = None,
    ) -> bool:
        """Uninstall QuPath application.

        Args:
            version (str): Specific version of QuPath to uninstall. Defaults to None,
                i.e. all versions will be uninstalled.
            path (Path | None): Path to the directory where QuPath is installed.
                If not specified, the default installation path will be used.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine (str | None): The machine architecture. If None, it will use platform.machine().

        Returns:
            bool: True if QuPath was uninstalled successfully, False if it was not installed at that location.

        Raises:
            ValueError: If the QuPath application directory is a file unexpectedly or does not exist.
        """
        if path is None:
            path = Service.get_installation_path()

        if not version:
            removed = False
            for qupath in path.glob("QuPath*"):
                if qupath.is_dir():
                    removed = True
                    logger.debug("Removing QuPath directory: %s", qupath)
                    shutil.rmtree(qupath, ignore_errors=False)
                if qupath.is_file():
                    removed = True
                    logger.debug("Removing QuPath archive: %s", qupath)
                    shutil.rmtree(qupath, ignore_errors=False)
            return removed

        app_dir = Service.get_app_dir(
            version=version,
            installation_path=path,
            platform_system=platform_system,
            platform_machine=platform_machine,
        )
        if not app_dir.exists():
            message = f"QuPath application directory '{app_dir!s}' does not exist, skipping."
            logger.warning(message)
            return False
        if app_dir.is_file():
            message = f"QuPath application directory '{app_dir!s}' is a file unexpectedly."
            logger.error(message)
            raise ValueError(message)
        shutil.rmtree(app_dir, ignore_errors=False)
        return True

    @staticmethod
    def _check_project_path(project: Path) -> Path:
        """Check if the project path is valid and return the resolved path to the project file.

        Args:
            project (Path): Path to the QuPath project directory.

        Returns:
            Path: The resolved path to the QuPath project file.

        Raises:
            ValueError: If QuPath is not installed or the project path is invalid.
        """
        if not Service.is_qupath_installed():
            message = "QuPath is not installed. Please install it first."
            logger.error(message)
            raise ValueError(message)

        if project.is_file():
            message = f"Project path '{project!s}' is a file, expected a directory."
            logger.error(message)
            raise ValueError(message)

        if project.is_dir():
            project_path = project / PROJECT_FILENAME
            if any(project.iterdir()) and not project_path.is_file():
                message = (
                    f"Project directory '{project!s}' is not empty and does not contain a valid QuPath project file."
                )
                logger.error(message)
                raise ValueError(message)

        if not project.exists():
            project.mkdir(parents=True, exist_ok=True)
            project_path = project.resolve() / PROJECT_FILENAME

        return project_path

    @staticmethod
    def add(  # noqa: C901, PLR0915
        project: Path,
        paths: list[Path],
        progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> int:
        """Add images to a QuPath project.

        Args:
            project (Path): Path to the QuPath project directory. Will be created if not existent.
            paths (list[Path]): One or multiple paths. A path can point to an individual image or folder.
                In case of a folder, all images within will be added for supported image types
            progress_callable (Callable | None): Optional callback function to report progress of adding images.

        Returns:
            int: The number of images added to the project.

        Raises:
            ValueError: If QuPath is not installed or the project path is invalid.
            RuntimeError: If there is an unexpected error adding images to the project.
        """
        if progress_callable:
            progress = AddProgress()
            progress_callable(progress)

        project_path = Service._check_project_path(project)

        from unittest.mock import patch  # noqa: PLC0415

        from paquo.images import QuPathImageType  # noqa: PLC0415
        from paquo.java import LogManager  # noqa: PLC0415
        from paquo.projects import QuPathProject  # noqa: PLC0415

        if LogManager:
            LogManager.setWarn()

        if progress_callable:
            progress.status = AddProgressState.CREATING_PROJECT
            progress_callable(progress)

        # Patch the uri property to use getURIs() instead of getServerURIs(),
        # as getServerURIs is deprecated in 0.5.1 and gone with 0.6.x
        def mock_uri_property(self) -> str:  # type: ignore[no-untyped-def]  # noqa: ANN001
            """Mock uri property that uses getURIs() instead of getServerURIs().

            Args:
                self: The QuPathImageEntry instance.

            Returns:
                str: The URI string from the first available URI.

            Raises:
                RuntimeError: If no server URIs are available.
                NotImplementedError: If multiple URIs are found (not supported).
            """
            uris = self.java_object.getURIs()
            if len(uris) == 0:
                msg = "no server"
                raise RuntimeError(msg)  # pragma: no cover
            if len(uris) > 1:
                msg = "unsupported in paquo as of now"
                raise NotImplementedError(msg)
            return str(uris[0].toString())

        with patch("paquo.images.QuPathProjectImageEntry.uri", new_callable=lambda: property(mock_uri_property)):
            with QuPathProject(project_path, mode="a") as qp:
                logger.debug("Finding images for QuPath project at '%s'", project_path)

            if progress_callable:
                progress.status = AddProgressState.FINDING_IMAGES
                progress_callable(progress)

            supported_extensions = IMAGE_SUFFIXES

            def is_supported_image(file_path: Path) -> bool:
                return file_path.is_file() and file_path.suffix.lower() in supported_extensions

            files_to_process = []
            for path in paths:
                if path.is_dir():
                    files_to_process = [file for file in path.glob("**/*") if is_supported_image(file)]
                elif is_supported_image(path):
                    files_to_process = [path]

            if progress_callable:
                progress.status = AddProgressState.ADDING_IMAGES
                progress.image_count = len(files_to_process)
                progress_callable(progress)

            added_count = 0
            for file_path in files_to_process:
                logger.debug("Adding image: %s", file_path)
                try:
                    qp.add_image(
                        file_path,
                        image_type=QuPathImageType.BRIGHTFIELD_H_E,
                    )
                    added_count += 1
                    if progress_callable:
                        progress.image_index = added_count
                        progress_callable(progress)

                except Exception as e:  # noqa: BLE001
                    message = f"Failed to add image '{file_path!s}' to project '{project!s}': '{e!s}'"
                    logger.warning(message)

            if progress_callable:
                progress.status = AddProgressState.COMPLETED
                progress_callable(progress)

            return added_count

    @staticmethod
    def annotate(  # noqa: C901
        project: Path,
        image: Path,
        annotations: Path,
        progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> int:
        """Annotate an image in a QuPath project.

        Args:
            project (Path): Path to the QuPath project directory. Will be created if not existent.
            image (Path): Path to the image file to annotate. Will be added to the project if not already present.
            annotations (Path): Path to the annotations file in compatible GeoJSON format.
            progress_callable (Callable | None): Optional callback function to report progress of annotating the image.

        Returns:
            int: The number of annotations added to the image.

        Raises:
            ValueError: If QuPath is not installed, the project path is invalid orthe annotation path is invalid.
            RuntimeError: If there is an error annotating the image.
        """
        if progress_callable:
            progress = AnnotateProgress()
            progress_callable(progress)

        Service._check_project_path(project)

        if not image.is_file():
            message = f"Image path '{image!s}' is not a valid file."
            logger.error(message)
            raise ValueError(message)

        if not annotations.is_file():
            message = f"Annotations path '{annotations!s}' is not a valid file."
            logger.error(message)
            raise ValueError(message)

        if progress_callable:
            progress.annotation_path = annotations
            progress.image_path = image
            progress_callable(progress)

        if progress_callable:
            progress.status = AnnotateProgressState.OPENING_PROJECT
            progress_callable(progress)

        if progress_callable:
            progress.status = AnnotateProgressState.FINDING_IMAGE
            progress_callable(progress)

        if progress_callable:
            progress.status = AnnotateProgressState.COUNTING
            progress_callable(progress)

        annotation_count = 0
        with open(annotations, "rb") as f:
            features_parser = ijson.items(f, "features.item")
            for _ in features_parser:
                annotation_count += 1

        if progress_callable:
            progress.annotation_count = annotation_count
            progress.status = AnnotateProgressState.ANNOTATING
            progress_callable(progress)

        # Generate and execute Groovy script to import annotations
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "annotate.groovy"

            # Generate Groovy script content based on the template
            groovy_script_content = f"""import qupath.lib.io.GsonTools
import qupath.lib.objects.PathObjects
import qupath.lib.regions.ImagePlane
import qupath.lib.roi.ROIs
import qupath.lib.geom.Point2
import qupath.lib.objects.classes.PathClass
import java.awt.Color
import java.io.File

// Check we are in a project
def project = getProject()
if (project == null) {{
    println("No project found! Did you launch this script with -p?")
    return
}}

// Load the image data
def imageName = "{image.name}"
println("Looking for image: " + imageName)
def imageEntry = project.getImageList().find {{ entry ->
    entry.getImageName().contains(imageName)
}}
if (imageEntry == null) {{
    println("Image not found in project. Available images:")
    project.getImageList().each {{ entry ->
        println("  - " + entry.getImageName())
    }}
    return
}}
println("Found image: " + imageEntry.getImageName())
def imageData = imageEntry.readImageData()

// Open the geojson
def jsonPath = "{annotations.as_posix()}"
println("Loading annotations from: " + jsonPath)
def jsonFile = new File(jsonPath)
if (!jsonFile.exists()) {{
    println("File not found: " + jsonPath)
    return
}}
def gson = GsonTools.getInstance(true)
def json = jsonFile.text

// Parse as GeoJSON
def type = new com.google.gson.reflect.TypeToken<Map<String, Object>>(){{}}.getType()
def geoJsonData = gson.fromJson(json, type)

// Get current image plane
def plane = ImagePlane.getDefaultPlane()

// Create list for new objects
def newObjects = []

// Process GeoJSON features
def features = geoJsonData.features
features.each {{ feature ->
    def geometry = feature.geometry
    def properties = feature.properties ?: [:]

    if (geometry.type == "Polygon") {{
        // Get exterior ring coordinates and convert to Point2 objects
        def coordinates = geometry.coordinates[0]
        def points = coordinates.collect {{ coord ->
            return new Point2(coord[0] as double, coord[1] as double)
        }}

        // Create polygon ROI
        def roi = ROIs.createPolygonROI(points, plane)

        // Create annotation object instead of detection
        def pathObject = PathObjects.createAnnotationObject(roi)

        // Set classification if available
        if (properties.classification) {{
            def className = properties.classification.name
            def colorArray = properties.classification.color

            // Create PathClass with color
            def pathClass = PathClass.fromString(className)
            if (colorArray && colorArray.size() >= 3) {{
                def color = new Color(colorArray[0] as int, colorArray[1] as int, colorArray[2] as int)
                pathClass = PathClass.fromString(className, color.getRGB())
            }}
            pathObject.setPathClass(pathClass)
        }}

        // Add other properties as metadata
        properties.each {{ key, value ->
            if (key != "classification") {{
                pathObject.getMetadata().put(key.toString(), value.toString())
            }}
        }}

        newObjects.add(pathObject)
    }}
}}

// Add objects to hierarchy
println("Adding annotations ...")
imageData.getHierarchy().addObjects(newObjects)
println("Added " + newObjects.size() + " annotations from GeoJSON")

// Save image
println("Saving image ...")
imageEntry.saveImageData(imageData)
println("Saved image.")

"""

            # Write the Groovy script to temporary file
            script_path.write_text(groovy_script_content, encoding="utf-8")

            message = f"Generated Groovy script at: {script_path}"
            logger.debug(message)

            # Launch QuPath with the generated script
            Service.launch_qupath(project=project, script=script_path)

        if progress_callable:
            progress.status = AnnotateProgressState.COMPLETED
            progress_callable(progress)

        return annotation_count

    @staticmethod
    def inspect(project: Path) -> dict[str, Any]:
        """Inspect QuPath project.

        Args:
            project (Path): Path to the QuPath project directory.

        Returns:
            dict[str,Any]: The QuPath project.

        Raises:
            ValueError: If QuPath is not installed or the project path is invalid.
            RuntimeError: If there is an error adding images to the project.
        """
        if not Service.is_qupath_installed():
            message = "QuPath is not installed. Please install it first."
            logger.error(message)
            raise RuntimeError(message)

        if not project.exists():
            message = f"Project path '{project!s}' does not exist."
            logger.error(message)
            raise ValueError(message)

        if project.is_file():
            message = f"Project path '{project!s}' is a file, expected a directory."
            logger.error(message)
            raise ValueError(message)

        if project.is_dir():
            project_file = project.resolve() / PROJECT_FILENAME
            if not project_file.is_file():
                # If the project file does not exist, we create a new one
                message = f"Not a QuPath project directory at '{project}'"
                logger.error(message)
                raise ValueError(message)

        rtn = dict[str, Any]()

        from paquo.java import LogManager  # noqa: PLC0415
        from paquo.projects import QuPathProject  # noqa: PLC0415

        if LogManager:
            LogManager.setWarn()

        qp = QuPathProject(path=project_file, mode="r")
        rtn["project_path"] = str(qp.path)
        rtn["version"] = qp.version
        rtn["timestamp_creation"] = qp.timestamp_creation
        rtn["timestamp_modification"] = qp.timestamp_modification
        rtn["images"] = []
        if qp.images:
            logger.debug("Found images in project: %s", qp.images)
            # If there are images, we only return the first one
            # to avoid overwhelming the output with too much data.
            for image in qp.images:
                logger.debug("Found image: %s", image)
                rtn["images"].append({
                    "entry_id": image.entry_id,
                    "entry_path": str(image.entry_path),
                    "uri": image.uri,
                    "image_name": image.image_name,
                    "image_type": image.image_type,
                    "description": image.description,
                    "num_channels": image.num_channels,
                    "num_timepoints": image.num_timepoints,
                    "num_zslices": image.num_z_slices,
                    "downsample_levels": image.downsample_levels,
                    "height": image.height,
                    "width": image.width,
                    "hierarchy": str(image.hierarchy),
                    "metadata": str(image.metadata),
                    "properties": str(image.properties),
                })
        return rtn


os.environ["PAQUO_QUPATH_SEARCH_DIRS"] = str(Service.get_installation_path())
