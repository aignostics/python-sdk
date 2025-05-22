"""Service of the application module."""

import base64
import re
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, TypedDict

import google_crc32c
import requests

from aignostics.bucket import Service as BucketService
from aignostics.platform import (
    Application,
    ApplicationRun,
    ApplicationRunData,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
    NotFoundException,
)
from aignostics.utils import BaseService, Health, get_logger
from aignostics.wsi import Service as WSIService

from ._settings import Settings

logger = get_logger(__name__)


class UploadProgressItem(TypedDict, total=False):
    """Type definition for upload progress queue items."""

    reference: str
    platform_bucket_url: str
    file_upload_progress: float


class Service(BaseService):
    """Service of the application module."""

    _settings: Settings
    _client: Client | None = None

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
        )

    def _get_platform_client(self) -> Client:
        """Get the platform client.

        Returns:
            Client: The platform client.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._client is None:
            logger.debug("Creating platform client.")
            self._client = Client()
        else:
            logger.debug("Reusing platform client.")
        return self._client

    def applications(self) -> list[Application]:
        """Get a list of all applications.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        return [
            app
            for app in list(self._get_platform_client().applications.list())
            if app.application_id not in {"h-e-tme", "two-task-dummy"}
        ]

    def application(self, application_id: str) -> Application:
        """Get a specific application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application: The application or None if not found.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            Exception: If the application cannot be retrieved.
        """
        return self._get_platform_client().application(application_id)

    def application_version(self, application_version_id: str) -> ApplicationVersion:
        """Get a specific application version.

        Args:
            application_version_id (str): The ID of the application version

        Returns:
            ApplicationVersion: The application version

        Raises:
            ValueError: If the application version ID is invalid.
            NotFoundException: If the application with the given ID is not found.
            Exception: If the application cannot be retrieved.
        """
        # Validate format: application_id:vX.Y.Z (where X.Y.Z is a semver)
        # This checks for proper format like "he-tme:v0.50.0" where "he-tme" is the application id
        # and "v0.50.0" is the version with proper semver format
        if not re.match(r"^[^:]+:v\d+\.\d+\.\d+$", application_version_id):
            message = f"Invalid application version id format: {application_version_id}. "
            "Expected format: application_id:vX.Y.Z"
            raise ValueError(message)

        application_id = application_version_id.split(":")[0]

        application = self.application(application_id)
        for version in self.application_versions(application):
            if version.application_version_id == application_version_id:
                return version
        message = f"Application version with ID {application_version_id} not found in application {application_id}"
        raise NotFoundException(message)

    def application_versions(self, application: Application) -> list[ApplicationVersion]:
        """Get a list of all versions of the given application.

        Args:
            application (Application): The application to check for versions.

        Returns:
            list[ApplicationVersion]: A list of all application versions.

        Raises:
            Exception: If version list cannot be retrieved
        """
        return self._get_platform_client().applications.versions.list_sorted(application=application)

    def application_version_latest(self, application: Application) -> ApplicationVersion | None:
        """Get a latest application version.

        Args:
            application (Application): The application to check for versions.

        Returns:
            ApplicationVersion | None: A list of all application versions.

        Raises:
            Exception: If version list cannot be retrieved
        """
        versions = self.application_versions(application)
        return versions[0] if versions else None

    @staticmethod
    def generate_metadata_from_source_directory(
        application_version_id: str,
        source_directory: Path,
    ) -> list[dict[str, Any]]:
        """Generate metadata from the source directory.

        - Recursively files ending with .tiff, .tif and .dcm in the source directory
        - Creates a dict with the following columns
            - reference (str): The reference of the file, being equivalent to the file name without suffix
            - source (str): The full path of the file
            - checksum_crc32c (str): The checksum of the file constructed using the CRC32C algorithm
            - base_mpp (float): The microns per pixel, inspecting the base layer
            - width: The width of the image, inspecting the base layer
            - height: The height of the image in pixes, inspecting the base layer
            - staining: The staining of the sample, fixed to "H&E"
            - sample_tissue: The tissue of the sample, None or an entry from the enum of
                ["adrenal gland", "bladder", "bone", "brain", "breast", "colon", "liver", "lung", "lymph node"]
            - sample_disease: The disease of the sample, None or an entry from the enum of
                ["lung", "liver", "breast", "bladder", "colorectal"]

        Args:
            application_version_id (str): The ID of the application version.
            source_directory (Path): The source directory to generate metadata from.
            with_header (bool): If True, include a header in the metadata.

        Returns:
            dict[str, Any]: The generated metadata.

        Raises:
            Exception: If the metadata cannot be generated.

        Raises:
            ValueError: If the source directory does not exist or is not a directory.
        """
        logger.debug("Generating metadata from source directory: %s", source_directory)

        # TODO(Helmut): Use it
        application_version = Service().application_version(application_version_id)  # noqa: F841

        if not source_directory.is_dir():
            logger.error("Source directory does not exist or is not a directory: %s", source_directory)
            message = f"Source directory does not exist or is not a directory: {source_directory}"
            raise ValueError(message)

        metadata = []
        file_extensions = [".tiff", ".tif", ".dcm"]

        try:
            for extension in file_extensions:
                for file_path in source_directory.glob(f"**/*{extension}"):
                    # Generate CRC32C checksum with google_crc32c and encode as base64
                    hash_sum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
                    with file_path.open("rb") as f:
                        while chunk := f.read(1024):
                            hash_sum.update(chunk)  # type: ignore[no-untyped-call]
                    checksum = str(base64.b64encode(hash_sum.digest()), "UTF-8")  # type: ignore[no-untyped-call]
                    if file_path.suffix in {".dcm", ".tiff", ".tif"}:
                        image_metadata = WSIService().get_metadata(file_path)
                        width = image_metadata["dimensions"]["width"]
                        height = image_metadata["dimensions"]["height"]
                        mpp = image_metadata["resolution"]["mpp_x"]
                        file_size_human = image_metadata["file"]["size_human"]
                    else:
                        mpp = None
                        width = None
                        height = None
                        file_size_human = None
                    entry = {
                        "reference": file_path.stem,
                        "source": str(file_path),
                        "checksum_crc32c": checksum,
                        "mpp": mpp,
                        "width": width,
                        "height": height,
                        "staining": "H&E",
                        "tissue_type": None,
                        "disease": None,
                        "file_size_human": file_size_human,
                        "file_upload_progress": 0.0,
                        "platform_bucket_url": None,
                    }
                    metadata.append(entry)

            logger.debug("Generated metadata for %d files", len(metadata))
            return metadata

        except Exception:
            logger.exception("Failed to generate metadata from source directory: %s", source_directory)
            raise

    @staticmethod
    def application_run_upload(
        application_version_id: str,
        metadata: list[dict[str, Any]],
        upload_prefix: str,
        upload_progress_queue: Any | None = None,  # noqa: ANN401
        upload_progress_callable: Callable[[int, Path, str], None] | None = None,
    ) -> bool:
        """Upload files with a progress queue.

        Args:
            application_version_id (str): The ID of the application version.
            metadata (list[dict[str, Any]]): The metadata to upload.
            upload_prefix (str): The prefix for the upload.
            upload_progress_queue (Queue | None): The queue to send progress updates to.
            upload_progress_callable (Callable[[int, Path, str], None] | None): The task to update for progress updates.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        import psutil  # noqa: PLC0415

        logger.debug("Uploading files with upload ID '%s'", upload_prefix)
        for row in metadata:
            reference = row["reference"]
            source_file_path = Path(row["source"])
            if not source_file_path.is_file():
                logger.warning("Source file '%s' does not exist.", row["source"])
                return False
            object_key = (
                f"{psutil.Process().username()}/{upload_prefix}/{application_version_id}/{source_file_path.name}"
            )
            platform_bucket_url = (
                f"{BucketService().get_bucket_protocol()}://{BucketService().get_bucket_name()}/{object_key}"
            )
            signed_upload_url = BucketService().create_signed_upload_url(object_key)
            logger.debug("Generated signed upload URL '%s' for object '%s'", signed_upload_url, platform_bucket_url)
            if upload_progress_queue:
                upload_progress_queue.put_nowait({
                    "reference": reference,
                    "platform_bucket_url": platform_bucket_url,
                })
            file_size = source_file_path.stat().st_size
            logger.debug(
                "Uploading file '%s' with size %d bytes to '%s' via '%s'",
                source_file_path,
                file_size,
                platform_bucket_url,
                signed_upload_url,
            )
            with (
                open(source_file_path, "rb") as f,
            ):

                def read_in_chunks(  # noqa: PLR0913, PLR0917
                    reference: str,
                    file_size: int,
                    upload_progress_queue: Any | None = None,  # noqa: ANN401
                    upload_progress_callable: Callable[[int, Path, str], None] | None = None,
                    file_path: Path = source_file_path,
                    platform_bucket_url: str = platform_bucket_url,
                ) -> Generator[bytes, None, None]:
                    while True:
                        chunk = f.read(1048576)
                        if not chunk:
                            break
                        if upload_progress_queue:
                            upload_progress_queue.put_nowait({
                                "reference": reference,
                                "file_upload_progress": min(100.0, f.tell() / file_size),
                            })
                        if upload_progress_callable:
                            upload_progress_callable(len(chunk), file_path, platform_bucket_url)
                        yield chunk

                response = requests.put(
                    signed_upload_url,
                    data=read_in_chunks(reference, file_size, upload_progress_queue, upload_progress_callable),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60,
                )
                response.raise_for_status()
        logger.info("Upload completed successfully.")
        return True

    @staticmethod
    def application_runs_static(limit: int | None = None) -> list[dict[str, Any]]:
        return [
            {
                "application_run_id": run.application_run_id,
                "application_version_id": run.application_version_id,
                "triggered_at": run.triggered_at,
                "status": run.status,
            }
            for run in Service().application_runs(limit=limit)
        ]

    def application_runs(self, limit: int | None = None) -> list[ApplicationRunData]:
        """Get a list of all application runs.

        Args:
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.

        Returns:
            list[ApplicationRunData]: A list of all application runs.

        Raises:
            Exception: If the application run list cannot be retrieved.
        """
        runs = list(self._get_platform_client().runs.list_data(sort="triggered_at"))[::-1]
        return runs[: min(len(runs), limit) if limit is not None else len(runs)]

    def application_run(self, run_id: str) -> ApplicationRun:
        """Find a run by its ID.

        Args:
            run_id: The ID of the run to find

        Returns:
            ApplicationRun: The run that can be fetched using the .details() call.

        Raises:
            Exception: If initializing the client fails.
        """
        return self._get_platform_client().run(run_id)

    def application_run_submit_from_metadata(
        self, application_version_id: str, metadata: list[dict[str, Any]]
    ) -> ApplicationRun:
        """Submit a run for the given application.

        Args:
            application_version_id: The ID of the application version to run.
            metadata: The metadata for the run.

        Returns:
            ApplicationRun: The submitted run.

        Raises:
            ValueError: If platform bucket URL is missing or has unsupported protocol.
            Exception: If submitting the run failed unexpectedly.
        """
        logger.debug("Submitting application run with metadata: %s", metadata)
        items = []
        for row in metadata:
            platform_bucket_url = row["platform_bucket_url"]
            if platform_bucket_url and platform_bucket_url.startswith("gs://"):
                url_parts = platform_bucket_url[5:].split("/", 1)
                bucket_name = url_parts[0]
                object_key = url_parts[1]
                download_url = BucketService().create_signed_download_url(object_key, bucket_name)
            else:
                message = f"Invalid platform bucket URL: '{platform_bucket_url}'."
                logger.warning(message)
                raise ValueError(message)
            items.append(
                InputItem(
                    reference=row["reference"],
                    input_artifacts=[
                        InputArtifact(
                            name="user_slide",
                            download_url=download_url,
                            metadata={
                                "checksum_crc32c": row["checksum_crc32c"],
                                "base_mpp": float(row["mpp"]),
                                "width": int(row["width"]),
                                "height": int(row["height"]),
                                "cancer": {
                                    "type": row["disease"],
                                    "tissue": row["tissue_type"],
                                },
                            },
                        )
                    ],
                )
            )
        logger.debug("Items for application run submission: %s", items)
        try:
            run = self.application_run_submit(application_version_id, items)
            logger.info(
                "Submitted application run with items: %s, application run id %s", items, run.application_run_id
            )
            return run
        except Exception:
            logger.exception("Failed to submit application run.")
            raise

    def application_run_submit(self, application_version_id: str, items: list[InputItem]) -> ApplicationRun:
        """Submit a run for the given application.

        Args:
            application_version_id: The ID of the application version to run.
            items: The input items for the run.

        Returns:
            ApplicationRun: The submitted run.

        Raises:
            Exception: If submitting the run failed unexpectedly.
        """
        return self._get_platform_client().runs.create(application_version=application_version_id, items=items)

    def application_run_cancel(self, run_id: str) -> None:
        """Cancel a run by its ID.

        Args:
            run_id: The ID of the run to cancel

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If canceling the run failed unexpectedly.
        """
        self.application_run(run_id).cancel()
