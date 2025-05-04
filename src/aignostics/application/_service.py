"""Service of the application module."""

import binascii
import os
from collections.abc import Generator, Iterator
from multiprocessing import Queue
from pathlib import Path
from typing import Any

import requests

from aignostics.dicom import Service as DicomService
from aignostics.platform import (
    Application,
    ApplicationRun,
    ApplicationRunStatus,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
)
from aignostics.tiff import Service as TiffService
from aignostics.utils import BaseService, Health, get_logger

from ._settings import Settings
from ._utils import application_versions_sorted_by_semver, create_signed_download_url, create_signed_upload_url
from ._utils import find_latest_application_version_id as util_find_latest_application_version_id

logger = get_logger(__name__)


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the application module."""

    _settings: Settings

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

    def get_data_directory(self) -> Path:
        """Get the data directory.

        Returns:
            Path: The data directory.
        """
        return Path(self._settings.data_directory)

    @staticmethod
    def _get_platform_client() -> Client:
        """Get the platform client.

        Returns:
            Client: The platform client.

        Raises:
            Exception: If the client cannot be created.
        """
        try:
            logger.debug("Creating authenticated client.")
            client = Client()
            logger.debug("Authenticated client created.")
            return client
        except Exception:
            logger.exception("Failed to create authenticated client.")
            raise

    def applications(self) -> Iterator[Application]:
        """Get a list of all applications.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return platform_client.applications.list()
        except Exception:
            logger.exception("Failed to list applications.")
            raise

    def application(self, application_id: str) -> Application | None:
        """Get a specific application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application | None: The application or None if not found.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            applications = platform_client.applications.list()
            for application in applications:
                if application.application_id == application_id:
                    return application
            return None
        except Exception:
            logger.exception("Failed to get application.")
            raise

    def application_versions(self, application: Application) -> list[ApplicationVersion]:
        """Get a list of all versions of the given application.

        Args:
            application (Application): The application to check for versions.

        Returns:
            list[ApplicationVersion]: A list of all application versions.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application version list cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return application_versions_sorted_by_semver(application, platform_client)
        except Exception:
            logger.exception(
                "Failed to retrieve application versions for  application id '%s'.", application.application_id
            )
            raise

    def find_latest_application_version_id(self, application: Application) -> str:
        """Find the latest version of the given application.

        Args:
            application (Application): The application to check for the latest version.

        Returns:
            list[str]: A list of all application runs.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the latest version cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return str(util_find_latest_application_version_id(application, platform_client))
        except Exception:
            logger.exception(
                "Failed to retrieve latest application for application id '%s'.", application.application_id
            )
            raise

    @staticmethod
    def generate_metadata_from_source_directory(source_directory: Path) -> list[dict[str, Any]]:
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
            source_directory (Path): The source directory to generate metadata from.

        Returns:
            dict[str, Any]: The generated metadata.

        Raises:
            Exception: If the metadata cannot be generated.

        Raises:
            ValueError: If the source directory does not exist or is not a directory.
        """
        logger.debug("Generating metadata from source directory: %s", source_directory)

        if not source_directory.is_dir():
            logger.error("Source directory does not exist or is not a directory: %s", source_directory)
            message = f"Source directory does not exist or is not a directory: {source_directory}"
            raise ValueError(message)

        metadata = []
        file_extensions = [".tiff", ".tif", ".dcm"]

        try:
            for extension in file_extensions:
                for file_path in source_directory.glob(f"**/*{extension}"):
                    with file_path.open("rb") as f:
                        file_content = f.read()
                        checksum = format(binascii.crc32(file_content) & 0xFFFFFFFF, "08x")
                    if file_path.suffix in {".tiff", ".tif"}:
                        image_metadata = TiffService().get_metadata(file_path)
                        width = image_metadata["dimensions"]["width"]
                        height = image_metadata["dimensions"]["height"]
                        mpp = image_metadata["resolution"]["mpp_x"]
                        file_size_human = image_metadata["file"]["size_human"]
                    elif file_path.suffix == ".dcm":
                        image_metadata = DicomService().get_metadata(file_path)
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
    def upload_with_queue(
        upload_id: str,
        application_version_id: str,
        metadata: list[dict[str, Any]],
        upload_progress_queue: Queue,
    ) -> bool:
        """Upload files with a progress queue.

        Args:
            upload_id (str): The ID of the upload.
            application_version_id (str): The ID of the application version.
            metadata (list[dict[str, Any]]): The metadata to upload.
            upload_progress_queue (Queue[Any]): The queue to use for progress updates.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        logger.debug("Uploading files with upload ID '%s'", upload_id)
        for row in metadata:
            reference = row["reference"]
            source_file_path = Path(row["source"])
            if not source_file_path.is_file():
                logger.warning("Source file '%s' does not exist.", row["source"])
                return False

            # Generate signed URL
            bucket_protocol = str(os.environ.get("AIGNOSTICS_BUCKET_PROTOCOL"))
            bucket_name = str(os.environ.get("AIGNOSTICS_BUCKET_NAME"))
            object_key = f"helmut/{upload_id}/{application_version_id}/{source_file_path.name}"
            platform_bucket_url = f"{bucket_protocol}://{bucket_name}/{object_key}"
            signed_upload_url = create_signed_upload_url(bucket_name, object_key)
            logger.debug("Generated signed upload URL '%s' for object '%s'", signed_upload_url, platform_bucket_url)
            upload_progress_queue.put_nowait({
                "reference": reference,
                "platform_bucket_url": platform_bucket_url,
            })
            # Upload file and posting progress to message queue
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

                def read_in_chunks(
                    reference: str, file_size: int, upload_progress_queue: Queue
                ) -> Generator[bytes, None, None]:
                    while True:
                        chunk = f.read(1048576)
                        if not chunk:
                            break
                        upload_progress_queue.put_nowait({
                            "reference": reference,
                            "file_upload_progress": min(100.0, f.tell() / file_size),
                        })
                        yield chunk

                response = requests.put(
                    signed_upload_url,
                    data=read_in_chunks(reference, file_size, upload_progress_queue),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60,
                )

                response.raise_for_status()

        logger.info("Upload completed successfully.")
        return True

    def application_runs_with_status(self) -> list[tuple[ApplicationRun, ApplicationRunStatus]]:
        """Get a list of all application runs.

        Returns:
            list[str]: A list of all application runs.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application run list cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            runs = platform_client.runs.list()
            runs_with_status = []
            for run in runs:
                try:
                    run_status = run.status()
                    if run_status:
                        runs_with_status.append((run, run_status))
                except Exception:
                    logger.exception("Failed to get status for run with ID '%s'", run.application_run_id)
                    continue

            # Sort runs by triggered_at in descending order (newest first)
            return sorted(runs_with_status, key=lambda x: x[1].triggered_at, reverse=True)
        except Exception:
            logger.exception("Failed to list application runs.")
            raise

    def application_run(self, run_id: str) -> tuple[ApplicationRun, ApplicationRunStatus] | None:
        """Find a run by its ID.

        Args:
            run_id: The ID of the run to find

        Returns:
            tuple[ApplicationRun, ApplicationRunStatus] | None: The run and its status or None if not found.
        """
        platform_client = self._get_platform_client()

        try:
            runs = platform_client.runs.list()
            for run in runs:
                run_status = run.status()
                if run_status.application_run_id == run_id:
                    return (run, run_status)
        except Exception:
            logger.exception("Failed to get application run '%s'.", run_id)
            raise

        return None

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
            Exception: If the client cannot be created.

        Raises:
            Exception: If submitting the run failed unexpectedly.
        """
        logger.debug("Submitting application run with metadata: %s", metadata)
        items = []
        for row in metadata:
            if "platform_bucket_url" in row:
                platform_bucket_url = row["platform_bucket_url"]
                if platform_bucket_url and platform_bucket_url.startswith("gs://"):
                    url_parts = platform_bucket_url[5:].split("/", 1)
                    if len(url_parts) == 2:
                        bucket_name = url_parts[0]
                        object_key = url_parts[1]
                        download_url = create_signed_download_url(bucket_name, object_key)
                    else:
                        logger.error("Invalid GCS URL format: %s", row[0])
                        continue
                else:
                    logger.error("Unsupported platform bucket URL protocol: %s", platform_bucket_url)
                    continue
                items.append(
                    InputItem(
                        reference=row["reference"],
                        input_artifacts=[
                            InputArtifact(
                                name="user_slide",
                                download_url=download_url,
                                metadata={
                                    "checksum_crc32c": row["checksum_crc32c"],
                                    "base_mpp": row["mpp"],
                                    "width": row["width"],
                                    "height": row["height"],
                                    "cancer": {
                                        "type": row["disease"],
                                        "tissue": row["tissue_type"],
                                    },
                                },
                            )
                        ],
                    )
                )
            else:
                logger.error("Missing platform bucket URL in metadata: %s", row)
                continue
        logger.debug("Items for application run submission: %s", items)
        platform_client = self._get_platform_client()
        try:
            return platform_client.runs.create(application_version=application_version_id, items=items)
            logger.info("Submitted application run with items: %s", items)
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
            Exception: If the client cannot be created.

        Raises:
            Exception: If submitting the run failed unexpectedly.
        """
        platform_client = self._get_platform_client()
        try:
            return platform_client.runs.create(application_version=application_version_id, items=items)
        except Exception:
            logger.exception("Failed to submit application run.")
            raise

    def application_run_cancel(self, run_id: str) -> bool:
        """Cancel a run by its ID.

        Args:
            run_id: The ID of the run to cancel

        Returns:
            bool: True if the run was cancelled, False otherwise.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If canceling the run failed unexpectedly.
        """
        (run, status) = self.application_run(run_id)
        try:
            if run and status:
                run.cancel()
        except ApplicationRunStatus.NotCancellable:
            logger.warning("Run '%s' is not cancellable.", run_id)
            return False
        except Exception:
            logger.exception("Failed to cancel application run '%s'.", run_id)
            raise
        return True
