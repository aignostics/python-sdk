"""Service of the QuPath module."""

import contextlib
import json
import platform
import queue
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import zipfile
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlsplit

import appdirs
import ijson
import psutil
import requests
from packaging.version import Version
from psutil import Process, wait_procs
from pydantic import BaseModel, computed_field

from aignostics.utils import UNHIDE_SENSITIVE_INFO, BaseService, Health, __project_name__, get_logger

from ._settings import Settings

logger = get_logger(__name__)

QUPATH_VERSION = "0.6.0-rc5"
DOWNLOAD_CHUNK_SIZE = 10 * 1024 * 1024
QUPATH_LAUNCH_MAX_WAIT_TIME = 30  # seconds, maximum wait time for QuPath to start
QUPATH_SCRIPT_MAX_EXECUTION_TIME = 60 * 60 * 2  # seconds, maximum wait time for QuPath to run a script

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


class QuPathImageHierarchy(BaseModel):
    """Hierarchy information for a QuPath image."""

    total: int
    detections: int
    annotations: int
    has_root_object: bool


class QuPathImage(BaseModel):
    """Information about a single image in a QuPath project."""

    id: str
    name: str
    description: str

    unique_name: str
    original_image_name: str
    uris: list[str]

    @computed_field  # type: ignore
    @property
    def path(self) -> str | None:
        """Get the path to the image data.

        Iterates over URIs and uses the first file URI found to extract the filename.

        Returns:
            Path: The path to the image data.
        """
        for uri in self.uris:
            parsed_uri = urlparse(uri)
            if parsed_uri.scheme == "file":
                return str(Path(parsed_uri.path).resolve())
        return None

    height: int
    width: int
    downsample_levels: list[float]

    num_channels: int
    num_timepoints: int
    num_zslices: int

    hierarchy: QuPathImageHierarchy

    entry_path: str
    thumbnail_path: str
    server_path: str
    data_path: str
    server_type: str
    server_builder: str


class QuPathProject(BaseModel):
    """Information about a QuPath project."""

    uri: str
    version: str
    images: list[QuPathImage]


class Service(BaseService):
    """Service of the bucket module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Determine info of this service.

        Args:
            mask_secrets (bool): Whether to mask sensitive information in the output.

        Returns:
            dict[str,Any]: The info of this service.
        """
        settings = self._settings.model_dump(context={UNHIDE_SENSITIVE_INFO: not mask_secrets})
        executable = Service.find_qupath_executable()
        version = Service.get_version()
        return {
            "app": {
                "path": str(executable) if executable else None,
                "version": dict(version) if version else None,
                "expected_version": Service.get_expected_version(),
            },
            "settings": settings,
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
    def _get_app_dir_from_qupath_dir(qupath_dir: Path, platform_system: str | None) -> Path:
        """Get the QuPath application directory based on the platform system.

        Args:
            qupath_dir (Path): The QuPath installation directory.
            platform_system (str | None): The system platform (e.g., "Linux", "Darwin", "Windows").
                Will be auto-determined if not given

        Returns:
            str: The path to the QuPath application directory.

        Raises:
            FileNotFoundError: If the QuPath application directory is not a directory.
        """
        platform_system = platform_system or platform.system()
        platform_paths = {"Linux": "lib/app", "Darwin": "Contents/app", "Windows": "app"}
        app_dir = qupath_dir / platform_paths[platform_system]

        if not app_dir.is_dir():
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
        exectuable = Service.find_qupath_executable(platform_system=platform_system)

        if not exectuable:
            return None

        try:
            result = subprocess.run(  # noqa: S603
                [str(exectuable), "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=QUPATH_LAUNCH_MAX_WAIT_TIME,
            )

            output = result.stdout.strip()
            logger.debug("QuPath version output: %s", output)

            version_match = re.search(r"Version:\s+([0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?)", output)

            # If standard pattern fails, try to match "QuPath vX.X.X" pattern, for Win32
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
    def _find_qupath_app_dir(platform_system: str | None) -> Path | None:
        """Find QuPath application directory.

        Args:
            platform_system (str | None): The system platform.

        Returns:
            Path | None: Path to QuPath app directory if found, None otherwise.
        """
        for d in Service.get_installation_path().iterdir():
            if d.is_dir() and re.match(r"(?i)qupath.*", d.name):
                try:
                    return Service._get_app_dir_from_qupath_dir(d, platform_system)
                except FileNotFoundError:
                    continue
        return None

    @staticmethod
    def _find_qupath_exe_from_app_dir(app_dir: Path, system: str) -> Path | None:
        """Get QuPath executable from app directory based on platform.

        Args:
            app_dir (Path): Path to QuPath app directory.
            system (str): The system platform.

        Returns:
            Path | None: Path to QuPath executable if found, None otherwise.
        """
        try:
            if system == "Linux":
                return next(app_dir.parent.parent.joinpath("bin").glob("QuPath*"))
            if system == "Darwin":
                return next(app_dir.parent.joinpath("MacOS").glob("QuPath*"))
            if system == "Windows":
                app_exes = list(app_dir.parent.glob("QuPath*.exe"))
                if len(app_exes) != 2:  # noqa: PLR2004
                    logger.warning(
                        "Expected to find exactly 2 QuPath executables, got %s. "
                        "Please ensure you have the correct QuPath installation.",
                        app_exes,
                    )
                    return None
                return next(qp for qp in app_exes if "console" in qp.stem)
        except StopIteration:
            return None
        return None

    @staticmethod
    def find_qupath_executable(platform_system: str | None = None) -> Path | None:
        """Find path to QuPath executable.

        Args:
            platform_system (str | None): The system platform. If None, it will use platform.system().

        Returns:
            Path | None: Path to the QuPath executable if found, otherwise None.
        """
        system = platform_system or platform.system()
        app_dir = Service._find_qupath_app_dir(platform_system)

        if app_dir is None:
            return None

        app_exe = Service._find_qupath_exe_from_app_dir(app_dir, system)

        if not app_exe or not app_exe.is_file():
            if app_exe:
                logger.warning("Expected to find file at %s.", app_exe)
            return None

        return app_exe

    @staticmethod
    def is_qupath_installed() -> bool:
        """Check if QuPath is installed.

        Returns:
            bool: True if QuPath is installed, False otherwise.
        """
        return Service.find_qupath_executable() is not None

    @staticmethod
    def get_installation_path() -> Path:
        """Get the installation directory of QuPath.

        Returns:
            Path: The directory QuPath will be installed into.
        """
        return Path(appdirs.user_data_dir(__project_name__)).resolve()

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
                    try:
                        shutil.move(destination, nirvana)
                    except PermissionError as e:
                        message = (
                            f"Failed to move existing QuPath directory '{destination!s}' "
                            f"to nirvana in '{nirvana!s}': {e!s}"
                        )
                        logger.exception(message)
                        raise RuntimeError(message) from e
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

            destination.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive_path, mode="r") as zf:
                zf.extractall(destination)  # nosec: B202  # noqa: S202
                # Verify that QuPath executable exists in the extracted content
                qupath_exe_found = False
                for item in destination.rglob("*"):
                    if item.name.startswith("QuPath") and item.is_file() and item.suffix == ".exe":
                        qupath_exe_found = True
                        break
                if not qupath_exe_found:
                    message = "No QuPath .exe found in the extracted contents."
                    logger.error(message)
                    raise RuntimeError(message)
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

            executable = Service.find_qupath_executable(
                platform_system=platform_system,
            )
            if not executable:
                message = "QuPath executable not found after installation."
                logger.error(message)
                raise RuntimeError(message)  # noqa: TRY301
            message = f"QuPath executable found at '{executable!s}'."
            logger.debug(message)

            executable.chmod(0o755)  # Make sure the executable is runnable
            message = f"Set permissions set to 755 for QuPath executable at '{executable!s}'."
            logger.debug(message)

            return application_path
        except Exception as e:
            message = f"Failed to install QuPath v{version} to '{path!s}': {e!s}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def execute_qupath(  # noqa: C901, PLR0912, PLR0915, PLR0911
        quiet: bool = True,
        project: Path | None = None,
        image: str | Path | None = None,
        script: str | Path | None = None,
        script_args: list[str] | None = None,
    ) -> int | None:
        """Execute QuPath application.

        Args:
            quiet (bool): If True, will launch QuPath in quiet mode (no GUI).
            project (Path | None): Path to the QuPath project to open. If None, no project will be opened.
            image: str | Path | None: Path to the image file to open in QuPath. If project path given as well,
                this must be the name of the image within project as str.
            script (str | Path | None): Path to the script to run in QuPath. If None, no script will be run.
            script_args (list[str] | None): Arguments to pass to the script. Only used when script is provided.

        Returns:
            int | None: Pid if QuPath was launched successfully, None otherwise.

        """
        executable = Service.find_qupath_executable()
        if not executable:
            logger.error("QuPath executable not found.")
            return None

        message = f"QuPath executable found at: {executable}"
        logger.debug(message)

        if platform.system() in {"Linux", "Darwin", "Windows"}:
            command = [str(executable)]
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
                if script_args:
                    for arg in script_args:
                        command.extend(["-a", arg])
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
                if script:
                    if waited > QUPATH_SCRIPT_MAX_EXECUTION_TIME:
                        message = f"Timed out after {waited:.2f} seconds waiting for QuPath script to complete"
                        logger.error(message)
                        return None
                elif waited > QUPATH_LAUNCH_MAX_WAIT_TIME:
                    message = f"Timed out after {waited:.2f} seconds waiting for QuPath to launch"
                    logger.error(message)
                    return None

                output = process.stdout.readline() if process.stdout.readable() else ""
                exit_code = process.poll()

                if not output and exit_code is not None:
                    if script:
                        if exit_code == 0:
                            logger.debug("QuPath script completed successfully.")
                            return process.pid
                        message = f"QuPath script failed with exit code '{exit_code}'."
                        logger.error(message)
                        return None
                    message = f"QuPath process has terminated with exit code '{exit_code}'."
                    logger.error(message)
                    break

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
    def get_qupath_processes() -> list[Process]:
        """Get PIDs of QuPath processes started from our managed installation.

        Returns:
            list[Process]: List of processes handles of running QuPath instances.
                Processes not started from installation part are ignored.
        """
        installation_path = Service.get_installation_path()
        processes = []
        for proc in psutil.process_iter(attrs={"pid", "exe"}):
            try:
                exe_path = proc.exe()
                if exe_path and str(installation_path) in exe_path:
                    processes.append(Process(proc.pid))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    @staticmethod
    def terminate_qupath_processes(wait_before_kill: int = 3) -> int:
        """Terminate QuPath processes.

        Args:
            wait_before_kill (int): Time in seconds to wait before forcefully killing processes.

        Returns:
            int: Number of processes terminated.

        """
        procs = Service.get_qupath_processes()
        for p in procs:
            try:
                p.terminate()
            except psutil.NoSuchProcess:
                logger.debug("Process %s already terminated.", p.pid)
                continue
        _, alive = wait_procs(procs, timeout=wait_before_kill)
        for p in alive:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                logger.debug("Process %s already terminated.", p.pid)
                continue
        return len(procs)

    @staticmethod
    def uninstall_qupath(
        version: str | None = None,
        path: Path | None = None,
        platform_system: str | None = None,
        platform_machine: str | None = None,
    ) -> bool:
        """Uninstall QuPath application.

        Notice:
            Terminates managed QuPath processes before uninstalling.

        Args:
            version (str): Specific version of QuPath to uninstall. Defaults to None,
                i.e. all versions will be uninstalled.
            path (Path | None): Path to the directory where QuPath is installed.
                If not specified, the default installation path will be used.
            platform_system (str | None): The system platform. If None, it will use platform.system().
            platform_machine (str | None): The machine architecture. If None, it will use platform.machine().

        Returns:
            bool: True if QuPath was uninstalled successfully.

        Raises:
            ValueError: If the QuPath application directory is a file unexpectedly.
        """
        if path is None:
            path = Service.get_installation_path()

        Service.terminate_qupath_processes()

        if not version:
            removed = False
            for qupath in path.glob("QuPath*"):
                if qupath.is_dir():
                    logger.debug("Removing QuPath directory '%s'", qupath)
                else:
                    logger.debug("Removing QuPath archive '%s'", qupath)
                try:
                    shutil.rmtree(qupath, ignore_errors=False)
                    removed = True
                except Exception as e:  # noqa: BLE001
                    message = f"Failed to remove '{qupath!s}': {e!s}"
                    logger.warning(message)
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
        try:
            logger.debug("Removing '%s'", app_dir)
            shutil.rmtree(app_dir, ignore_errors=False)
            return True
        except Exception as e:  # noqa: BLE001
            message = f"Failed to remove '{app_dir!s}': {e!s}"
            logger.warning(message)
        return False

    @staticmethod
    def _find_groovy_script(script_name: str) -> Path:
        """Find the Groovy script file in the scripts directory.

        Args:
            script_name (str): Name of the Groovy script file to find.

        Returns:
            Path: The path to the Groovy script file.

        Raises:
            ValueError: If the script file does not exist.
        """
        script_path = Path(__file__).parent / "scripts" / f"{script_name}.groovy"
        if not script_path.is_file():
            message = f"Groovy script '{script_name}' not found at: {script_path}"
            logger.error(message)
            raise ValueError(message)
        return script_path

    @staticmethod
    def add(
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
        message = f"Adding images to QuPath project at '{project!s}' from paths: {paths!r}"
        logger.debug(message)

        if progress_callable:
            progress = AddProgress()
            progress_callable(progress)

        if progress_callable:
            progress.status = AddProgressState.ADDING_IMAGES
            progress_callable(progress)

        # We communicate via file I/O with the Groovy script running within QuPath
        with (
            tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as paths_file,
            tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as output_file,
        ):
            try:
                json.dump([str(path.resolve()) for path in paths], paths_file.file)
                paths_file.flush()

                pid = Service.execute_qupath(
                    script=Service._find_groovy_script("add"),
                    script_args=[str(project), str(paths_file.name), str(output_file.name)],
                )

                if not pid:
                    message = "Failed to execute QuPath script for adding images."
                    logger.error(message)
                    raise RuntimeError(message)  # noqa: TRY301

                with Path(output_file.name).open("r", encoding="utf-8") as f:
                    result_data = json.load(f)
                added_count = int(result_data.get("added_count", 0))
                errors = result_data.get("errors", [])
                for error in errors:
                    logger.warning("QuPath add script error: %s", error)

                if progress_callable:
                    progress.status = AddProgressState.COMPLETED
                    progress_callable(progress)

                return added_count
            except Exception as e:
                message = f"Failed to add images to QuPath project: {e!s}"
                logger.exception(message)
                raise RuntimeError(message) from e

    @staticmethod
    def annotate(
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
            ValueError: If QuPath is not installed, the project path is invalid or the annotation path is invalid.
            RuntimeError: If there is an error annotating the image.
        """
        if progress_callable:
            progress = AnnotateProgress()
            progress_callable(progress)

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

        pid = Service.execute_qupath(
            project=project,
            script=Service._find_groovy_script("annotate"),
            script_args=[image.name, str(annotations.as_posix())],
        )
        if not pid:
            message = "Failed to execute QuPath script for annotations."
            logger.error(message)
            raise RuntimeError(message)

        if progress_callable:
            progress.status = AnnotateProgressState.COMPLETED
            progress_callable(progress)

        return annotation_count

    @staticmethod
    def inspect(project: Path) -> QuPathProject:
        """Inspect QuPath project using a Groovy script.

        Args:
            project (Path): Path to the QuPath project directory.

        Returns:
            QuPathProject: The QuPath project information.

        Raises:
            ValueError: If QuPath is not installed or the project path is invalid.
            RuntimeError: If there is an error inspecting the project.
        """
        # We communicate via file I/O with the Groovy script running within QuPath
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", encoding="utf-8") as temp_file:
            output_file = Path(temp_file.name).resolve()

            pid = Service.execute_qupath(
                quiet=True,
                project=project,
                script=Service._find_groovy_script("inspect"),
                script_args=[str(output_file)],
            )

            if not pid:
                message = "Failed to execute QuPath inspect script"
                logger.error(message)
                raise RuntimeError(message)

            if not output_file.is_file():
                message = f"QuPath script output file '{output_file!s}' does not exist."
                logger.error(message)
                raise RuntimeError(message)

            return QuPathProject.model_validate_json(output_file.read_text(encoding="utf-8"))
