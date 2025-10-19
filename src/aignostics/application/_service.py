"""Service of the application module."""

import base64
import re
import time
from collections.abc import Callable, Generator
from datetime import UTC, datetime
from enum import StrEnum
from http import HTTPStatus
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import google_crc32c
import requests
from aignx.codegen.models import ItemOutput, ItemState
from pydantic import BaseModel, computed_field

from aignostics.bucket import Service as BucketService
from aignostics.constants import WSI_SUPPORTED_FILE_EXTENSIONS
from aignostics.platform import (
    LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    ApiException,
    Application,
    ApplicationSummary,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
    ItemResult,
    NotFoundException,
    OutputArtifactElement,
    Run,
    RunData,
    RunOutput,
    RunState,
)
from aignostics.platform import (
    Service as PlatformService,
)
from aignostics.utils import BaseService, Health, get_logger, sanitize_path_component
from aignostics.wsi import Service as WSIService

from ._settings import Settings
from ._utils import get_file_extension_for_artifact, get_mime_type_for_artifact

has_qupath_extra = find_spec("ijson")
if has_qupath_extra:
    from aignostics.qupath import AddProgress as QuPathAddProgress
    from aignostics.qupath import AnnotateProgress as QuPathAnnotateProgress
    from aignostics.qupath import Service as QuPathService


logger = get_logger(__name__)

APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS = 5
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


class DownloadProgressState(StrEnum):
    """Enum for download progress states."""

    INITIALIZING = "Initializing ..."
    QUPATH_ADD_INPUT = "Adding input slides to QuPath project ..."
    CHECKING = "Checking run status ..."
    WAITING = "Waiting for item completing ..."
    DOWNLOADING = "Downloading artifact ..."
    QUPATH_ADD_RESULTS = "Adding result images to QuPath project ..."
    QUPATH_ANNOTATE_INPUT_WITH_RESULTS = "Annotating input slides in QuPath project with results ..."
    COMPLETED = "Completed."


class DownloadProgress(BaseModel):
    status: DownloadProgressState = DownloadProgressState.INITIALIZING
    run: RunData | None = None
    item: ItemResult | None = None
    item_count: int | None = None
    item_index: int | None = None
    item_external_id: str | None = None
    artifact: OutputArtifactElement | None = None
    artifact_count: int | None = None
    artifact_index: int | None = None
    artifact_path: Path | None = None
    artifact_download_url: str | None = None
    artifact_size: int | None = None
    artifact_downloaded_chunk_size: int = 0
    artifact_downloaded_size: int = 0
    if has_qupath_extra:
        qupath_add_input_progress: QuPathAddProgress | None = None
        qupath_add_results_progress: QuPathAddProgress | None = None
        qupath_annotate_input_with_results_progress: QuPathAnnotateProgress | None = None

    @computed_field  # type: ignore
    @property
    def total_artifact_count(self) -> int | None:
        if self.item_count and self.artifact_count:
            return self.item_count * self.artifact_count
        return None

    @computed_field  # type: ignore
    @property
    def total_artifact_index(self) -> int | None:
        if self.item_count and self.artifact_count and self.item_index is not None and self.artifact_index is not None:
            return self.item_index * self.artifact_count + self.artifact_index
        return None

    @computed_field  # type: ignore
    @property
    def item_progress_normalized(self) -> float:  # noqa: PLR0911
        """Compute normalized item progress in range 0..1.

        Returns:
            float: The normalized item progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING:
            if (not self.total_artifact_count) or self.total_artifact_index is None:
                return 0.0
            return min(1, float(self.total_artifact_index + 1) / float(self.total_artifact_count))
        if has_qupath_extra:
            if self.status == DownloadProgressState.QUPATH_ADD_INPUT and self.qupath_add_input_progress:
                return self.qupath_add_input_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ADD_RESULTS and self.qupath_add_results_progress:
                return self.qupath_add_results_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS:
                if (not self.item_count) or (not self.item_index):
                    return 0.0
                return min(1, float(self.item_index + 1) / float(self.item_count))
        return 0.0

    @computed_field  # type: ignore
    @property
    def artifact_progress_normalized(self) -> float:
        """Compute normalized artifact progress in range 0..1.

        Returns:
            float: The normalized artifact progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING:
            if not self.artifact_size:
                return 0.0
            return min(1, float(self.artifact_downloaded_size) / float(self.artifact_size))
        if (
            has_qupath_extra
            and self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
            and self.qupath_annotate_input_with_results_progress
        ):
            return self.qupath_annotate_input_with_results_progress.progress_normalized
        return 0.0


class Service(BaseService):
    """Service of the application module."""

    _settings: Settings
    _client: Client | None = None
    _platform_service: PlatformService | None = None

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: ARG002, PLR6301
        """Determine info of this service.

        Args:
            mask_secrets (bool): If True, mask sensitive information in the output.

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

    def _get_platform_service(self) -> PlatformService:
        """Get the platform service.

        Returns:
            PlatformService: The platform service.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._platform_service is None:
            logger.debug("Creating platform service.")
            self._platform_service = PlatformService()
        else:
            logger.debug("Reusing platform service.")
        return self._platform_service

    @staticmethod
    def _validate_due_date(due_date: str | None) -> None:
        """Validate that due_date is in ISO 8601 format and in the future.

        Args:
            due_date (str | None): The datetime string to validate.

        Raises:
            ValueError: If
                the format is invalid
                or the due_date is not in the future.
        """
        if due_date is None:
            return

        # Try parsing with fromisoformat (handles most ISO 8601 formats)
        try:
            # Handle 'Z' suffix by replacing with '+00:00'
            normalized = due_date.replace("Z", "+00:00")
            parsed_dt = datetime.fromisoformat(normalized)
        except (ValueError, TypeError) as e:
            message = (
                f"Invalid ISO 8601 format for due_date. "
                f"Expected format like '2025-10-19T19:53:00+00:00' or '2025-10-19T19:53:00Z', "
                f"but got: '{due_date}' (error: {e})"
            )
            raise ValueError(message) from e

        # Ensure the datetime is timezone-aware (reject naive datetimes)
        if parsed_dt.tzinfo is None:
            message = (
                f"Invalid ISO 8601 format for due_date. "
                f"Expected format with timezone like '2025-10-19T19:53:00+00:00' or '2025-10-19T19:53:00Z', "
                f"but got: '{due_date}' (missing timezone information)"
            )
            raise ValueError(message)

        # Check that the datetime is in the future
        now = datetime.now(UTC)
        if parsed_dt <= now:
            message = (
                f"due_date must be in the future. "
                f"Got '{due_date}' ({parsed_dt.isoformat()}), "
                f"but current UTC time is {now.isoformat()}"
            )
            raise ValueError(message)

    @staticmethod
    def applications_static() -> list[ApplicationSummary]:
        """Get a list of all applications, static variant.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        return Service().applications()

    def applications(self) -> list[ApplicationSummary]:
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
        """Get application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application: The application.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            RuntimeError: If the application cannot be retrieved unexpectedly.
        """
        try:
            return self._get_platform_client().application(application_id)
        except NotFoundException as e:
            message = f"Application with ID '{application_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to retrieve application with ID '{application_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_version(self, application_id: str, application_version: str | None = None) -> ApplicationVersion:
        """Get a specific application version.

        Args:
            application_id (str): The ID of the application
            application_version (str|None): The version of the application (semver).
                If not given latest version is used.

        Returns:
            ApplicationVersion: The application version

        Raises:
            ValueError: If
                the application version number is invalid.
            NotFoundException: If the application version with the given ID and number is not found.
            RuntimeError: If the application cannot be retrieved unexpectedly.
        """
        try:
            return self._get_platform_client().application_version(application_id, application_version)
        except ValueError:
            raise
        except NotFoundException as e:
            message = f"Application with ID '{application_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to retrieve application with ID '{application_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_versions_static(application_id: str) -> list[ApplicationVersion]:
        """Get a list of all versions for a specific application, static variant.

        Args:
            application_id (str): The ID of the application.

        Returns:
            list[ApplicationVersion]: A list of all versions for the application.

        Raises:
            Exception: If the application versions cannot be retrieved.
        """
        return Service().application_versions(application_id)

    def application_versions(self, application_id: str) -> list[ApplicationVersion]:
        """Get a list of all versions for a specific application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            list[ApplicationVersion]: A list of all versions for the application.

        Raises:
            RuntimeError: If the versions cannot be retrieved unexpectedly.
            NotFoundException: If the application with the given ID is not found.
        """
        # TODO(Andreas): Have to make calls for all application versions to construct
        # Changelog dialog on run describe page.
        # Can be optimized to one call if API would support it.
        # Let's discuss if we should re-add the endpoint that existed.
        try:
            client = self._get_platform_client()
            return [
                client.application_version(application_id, version.number)
                for version in client.versions.list(application_id)
            ]
        except NotFoundException as e:
            message = f"Application with ID '{application_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to retrieve versions for application with ID '{application_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def _process_key_value_pair(entry: dict[str, Any], key_value: str, external_id: str) -> None:
        """Process a single key-value pair from a mapping.

        Args:
            entry (dict[str, Any]): The entry dictionary to update
            key_value (str): String in the format "key=value"
            external_id (str): The external_id value for logging
        """
        key, value = key_value.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return

        if key not in entry:
            logger.warning("key '%s' not found in entry, ignoring mapping for '%s'", key, external_id)
            return

        logger.debug("Updating key '%s' with value '%s' for external_id '%s'.", key, value, external_id)
        entry[key.strip()] = value.strip()

    @staticmethod
    def _apply_mappings_to_entry(entry: dict[str, Any], mappings: list[str]) -> None:
        """Apply key/value mappings to an entry.

        If the external_id attribute of the entry matches the regex pattern in the mapping,
            the key/value pairs are applied.

        Args:
            entry (dict[str, Any]): The entry dictionary to update with mapped values
            mappings (list[str]): List of strings with format 'regex:key=value,...'
                where regex ismatched against the external_id attribute in the entry
        """
        external_id = entry["external_id"]
        for mapping in mappings:
            parts = mapping.split(":", 1)
            if len(parts) != 2:  # noqa: PLR2004
                continue

            pattern = parts[0].strip()
            if not re.search(pattern, external_id):
                continue

            key_value_pairs = parts[1].split(",")
            for key_value in key_value_pairs:
                Service._process_key_value_pair(entry, key_value, external_id)

    @staticmethod
    def generate_metadata_from_source_directory(  # noqa: PLR0913, PLR0917
        source_directory: Path,
        application_id: str,
        application_version: str | None = None,
        with_gui_metadata: bool = False,
        mappings: list[str] | None = None,
        with_extra_metadata: bool = False,
    ) -> list[dict[str, Any]]:
        """Generate metadata from the source directory.

        Steps:
        1. Recursively files ending with supported extensions in the source directory
        2. Creates a dict with the following columns
            - external_id (str): The external_id of the file, by default equivalent to the absolute file name
            - source (str): The absolute filename
            - checksum_base64_crc32c (str): The CRC32C checksum of the file constructed, base64 encoded
            - resolution_mpp (float): The microns per pixel, inspecting the base layer
            - height_px: The height of the image in pixels, inspecting the base layer
            - width_px: The width of the image in pixels, inspecting the base layer
            - Further attributes depending on the application and it's version
        3. Applies the optional mappings to fill in additional metadata fields in the dict.

        Args:
            source_directory (Path): The source directory to generate metadata from.
            application_id (str): The ID of the application.
            application_version (str|None): The version of the application (semver).
                If not given latest version is used.
            with_gui_metadata (bool): If True, include additional metadata for GUI.
            mappings (list[str]): Mappings of the form '<regexp>:<key>:<value>,<key>:<value>,...'.
                The regular expression is matched against the external_id attribute of the entry.
                The key/value pairs are applied to the entry if the pattern matches.
            with_extra_metadata (bool): If True, include extra metadata from the WSIService.

        Returns:
            dict[str, Any]: The generated metadata.

        Raises:
            Exception: If the metadata cannot be generated.

        Raises:
            NotFoundError: If the application version with the given ID is not found.
            ValueError: If
                the source directory does not exist
                or is not a directory.
            RuntimeError: If the metadata generation fails unexpectedly.
        """
        logger.debug("Generating metadata from source directory: %s", source_directory)

        # TODO(Helmut): Use it
        _ = Service().application_version(application_id, application_version)

        metadata = []

        try:
            for extension in list(WSI_SUPPORTED_FILE_EXTENSIONS):
                for file_path in source_directory.glob(f"**/*{extension}"):
                    # Generate CRC32C checksum with google_crc32c and encode as base64
                    hash_sum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
                    with file_path.open("rb") as f:
                        while chunk := f.read(1024):
                            hash_sum.update(chunk)  # type: ignore[no-untyped-call]
                    checksum = str(base64.b64encode(hash_sum.digest()), "UTF-8")  # type: ignore[no-untyped-call]
                    try:
                        image_metadata = WSIService().get_metadata(file_path)
                        width = image_metadata["dimensions"]["width"]
                        height = image_metadata["dimensions"]["height"]
                        mpp = image_metadata["resolution"]["mpp_x"]
                        file_size_human = image_metadata["file"]["size_human"]
                        path = file_path.absolute()
                        entry = {
                            "external_id": str(path),
                            "path_name": str(path.name),
                            "source": str(file_path),
                            "checksum_base64_crc32c": checksum,
                            "resolution_mpp": mpp,
                            "width_px": width,
                            "height_px": height,
                            "staining_method": None,
                            "tissue": None,
                            "disease": None,
                            "file_size_human": file_size_human,
                            "file_upload_progress": 0.0,
                            "platform_bucket_url": None,
                        }
                        if with_extra_metadata:
                            entry["extra"] = image_metadata.get("extra", {})

                        if not with_gui_metadata:
                            entry.pop("path_name", None)
                            entry.pop("source", None)
                            entry.pop("file_size_human", None)
                            entry.pop("file_upload_progress", None)

                        if mappings:
                            Service._apply_mappings_to_entry(entry, mappings)

                        metadata.append(entry)
                    except Exception as e:  # noqa: BLE001
                        message = f"Failed to process file '{file_path}': {e}"
                        logger.warning(message)
                        continue

            logger.debug("Generated metadata for %d files", len(metadata))
            return metadata

        except Exception as e:
            message = f"Failed to generate metadata from source directory '{source_directory}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_upload(  # noqa: PLR0913, PLR0917
        application_id: str,
        metadata: list[dict[str, Any]],
        application_version: str | None = None,
        onboard_to_aignostics_portal: bool = False,
        upload_prefix: str = str(time.time() * 1000),
        upload_progress_queue: Any | None = None,  # noqa: ANN401
        upload_progress_callable: Callable[[int, Path, str], None] | None = None,
    ) -> bool:
        """Upload files with a progress queue.

        Args:
            application_id (str): The ID of the application.
            metadata (list[dict[str, Any]]): The metadata to upload.
            application_version (str|None): The version ID of the application.
                If not given latest version is used.
            onboard_to_aignostics_portal (bool): True if the run should be onboarded to the Aignostics Portal.
            upload_prefix (str): The prefix for the upload, defaults to current milliseconds.
            upload_progress_queue (Queue | None): The queue to send progress updates to.
            upload_progress_callable (Callable[[int, Path, str], None] | None): The task to update for progress updates.

        Returns:
            bool: True if the upload was successful, False otherwise.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            RuntimeError: If fetching the application version fails unexpectedly.
            requests.HTTPError: If the upload fails with an HTTP error.
        """
        import psutil  # noqa: PLC0415

        logger.debug("Uploading files with upload ID '%s'", upload_prefix)
        app_version = Service().application_version(application_id, application_version=application_version)
        for row in metadata:
            external_id = row["external_id"]
            source_file_path = Path(row["external_id"])
            if not source_file_path.is_file():
                logger.warning("Source file '%s' does not exist.", row["external_id"])
                return False
            username = psutil.Process().username().replace("\\", "_")
            object_key = (
                f"{username}/{upload_prefix}/{application_id}/{app_version.version_number}/{source_file_path.name}"
            )
            if onboard_to_aignostics_portal:
                object_key = f"onboard/{object_key}"
            platform_bucket_url = (
                f"{BucketService().get_bucket_protocol()}://{BucketService().get_bucket_name()}/{object_key}"
            )
            signed_upload_url = BucketService().create_signed_upload_url(object_key)
            logger.debug("Generated signed upload URL '%s' for object '%s'", signed_upload_url, platform_bucket_url)
            if upload_progress_queue:
                upload_progress_queue.put_nowait({
                    "external_id": external_id,
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
                    external_id: str,
                    file_size: int,
                    upload_progress_queue: Any | None = None,  # noqa: ANN401
                    upload_progress_callable: Callable[[int, Path, str], None] | None = None,
                    file_path: Path = source_file_path,
                    platform_bucket_url: str = platform_bucket_url,
                ) -> Generator[bytes, None, None]:
                    while True:
                        chunk = f.read(APPLICATION_RUN_UPLOAD_CHUNK_SIZE)
                        if not chunk:
                            break
                        if upload_progress_queue:
                            upload_progress_queue.put_nowait({
                                "external_id": external_id,
                                "file_upload_progress": min(100.0, f.tell() / file_size),
                            })
                        if upload_progress_callable:
                            upload_progress_callable(len(chunk), file_path, platform_bucket_url)
                        yield chunk

                response = requests.put(
                    signed_upload_url,
                    data=read_in_chunks(external_id, file_size, upload_progress_queue, upload_progress_callable),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60,
                )
                response.raise_for_status()
        logger.info("Upload completed successfully.")
        return True

    # TODO(Helmut): Refactor to find runs with succeeded items
    @staticmethod
    def application_runs_static(
        limit: int | None = None,
        has_output: bool = False,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
    ) -> list[dict[str, Any]]:
        """Get a list of all application runs, static variant.

        Args:
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.
            has_output (bool): If True, only runs with partial or full output are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.

        Returns:
            list[RunData]: A list of all application runs.

        Raises:
            RuntimeError: If the application run list cannot be retrieved.
        """
        return [
            {
                "run_id": run.run_id,
                "application_id": run.application_id,
                "version_number": run.version_number,
                "submitted_at": run.submitted_at,
                "state": run.state,
                "termination_reason": run.termination_reason,
                "item_count": run.statistics.item_count,
                "item_succeeded_count": run.statistics.item_succeeded_count,
            }
            for run in Service().application_runs(
                limit=limit,
                has_output=has_output,
                note_regex=note_regex,
                note_query_case_insensitive=note_query_case_insensitive,
            )
        ]

    def application_runs(
        self,
        limit: int | None = None,
        has_output: bool = False,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
    ) -> list[RunData]:
        """Get a list of all application runs.

        Args:
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.
            has_output (bool): If True, only runs with partial or full output are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.

        Returns:
            list[RunData]: A list of all application runs.

        Raises:
            RuntimeError: If the application run list cannot be retrieved.
        """
        if limit is not None and limit <= 0:
            return []
        runs = []
        page_size = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
        try:
            if note_regex:
                flag_case_insensitive = ' flag "i"' if note_query_case_insensitive else ""
                custom_metadata = f'$.sdk.note ? (@ like_regex "{note_regex}"{flag_case_insensitive})'
            else:
                custom_metadata = None

            run_iterator = self._get_platform_client().runs.list_data(
                sort="-submitted_at", page_size=page_size, custom_metadata=custom_metadata
            )
            for run in run_iterator:
                if has_output and run.output == RunOutput.NONE:
                    continue
                runs.append(run)
                if limit is not None and len(runs) >= limit:
                    break
            return runs
        except Exception as e:
            message = f"Failed to retrieve application runs: {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run(self, run_id: str) -> Run:
        """Select a run by its ID.

        Args:
            run_id (str): The ID of the run to find

        Returns:
            Run: The run that can be fetched using the .details() call.

        Raises:
            RuntimeError: If initializing the client fails or the run cannot be retrieved.
        """
        try:
            return self._get_platform_client().run(run_id)
        except Exception as e:
            message = f"Failed to retrieve application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_submit_from_metadata(  # noqa: PLR0913, PLR0917
        self,
        application_id: str,
        metadata: list[dict[str, Any]],
        application_version: str | None = None,
        custom_metadata: dict[str, Any] | None = None,
        note: str | None = None,
        due_date: str | None = None,
        deadline: str | None = None,
        onboard_to_aignostics_portal: bool = False,
        validate_only: bool = False,
    ) -> Run:
        """Submit a run for the given application.

        Args:
            application_id (str): The ID of the application to run.
            metadata (list[dict[str, Any]]): The metadata for the run.
            custom_metadata (dict[str, Any] | None): Optional custom metadata to attach to the run.
            note (str | None): An optional note for the run.
            due_date (str | None): An optional requested completion time for the run, ISO8601 format.
                The scheduler will try to complete the run before this time, taking
                the subscription tier and available GPU resources into account.
            deadline (str | None): An optional hard deadline for the run, ISO8601 format.
                If processing exceeds this deadline, the run can be aborted.
            application_version (str | None): The version of the application.
                If not given latest version is used.
            onboard_to_aignostics_portal (bool): True if the run should be onboarded to the Aignostics Portal.
            validate_only (bool): If True, cancel the run post validation, before analysis.

        Returns:
            Run: The submitted run.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            ValueError: If
                platform bucket URL is missing
                or has unsupported protocol,
                or if the application version ID is invalid,
                or if due_date is not ISO 8601
                or if due_date not in the future.
            RuntimeError: If submitting the run failed unexpectedly.
        """
        self._validate_due_date(due_date)
        logger.debug("Submitting application run with metadata: %s", metadata)
        app_version = self.application_version(application_id, application_version=application_version)
        if len(app_version.input_artifacts) != 1:
            message = (
                f"Application version '{app_version.version_number}' has "
                f"{len(app_version.input_artifacts)} input artifacts, "
                "but only 1 is supported."
            )
            logger.warning(message)
            raise RuntimeError(message)
        input_artifact_name = app_version.input_artifacts[0].name

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
                    external_id=row["external_id"],
                    input_artifacts=[
                        InputArtifact(
                            name=input_artifact_name,
                            download_url=download_url,
                            metadata={
                                "checksum_base64_crc32c": row["checksum_base64_crc32c"],
                                "height_px": int(row["height_px"]),
                                "width_px": int(row["width_px"]),
                                "media_type": (
                                    "image/tiff"
                                    if row["external_id"].lower().endswith((".tif", ".tiff"))
                                    else "application/dicom"
                                    if row["external_id"].lower().endswith(".dcm")
                                    else "application/octet-stream"
                                ),
                                "resolution_mpp": float(row["resolution_mpp"]),
                                "specimen": {
                                    "disease": row["disease"],
                                    "tissue": row["tissue"],
                                },
                                "staining_method": row["staining_method"],
                            },
                        )
                    ],
                )
            )
        logger.debug("Items for application run submission: %s", items)

        try:
            run = self.application_run_submit(
                application_id=application_id,
                items=items,
                application_version=app_version.version_number,
                custom_metadata=custom_metadata,
                note=note,
                due_date=due_date,
                deadline=deadline,
                onboard_to_aignostics_portal=onboard_to_aignostics_portal,
                validate_only=validate_only,
            )
            logger.info(
                "Submitted application run with items: %s, application run id %s, custom metadata: %s",
                items,
                run.run_id,
                custom_metadata,
            )
            return run
        except ValueError as e:
            message = (
                f"Failed to submit application run for application '{application_id}' "
                f"(version: {app_version.version_number}): {e}"
            )
            logger.warning(message)
            raise ValueError(message) from e
        except Exception as e:
            message = (
                f"Failed to submit application run for application '{application_id}' "
                f"(version: {app_version.version_number}): {e}"
            )
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_submit(  # noqa: PLR0913, PLR0917
        self,
        application_id: str,
        items: list[InputItem],
        application_version: str | None = None,
        custom_metadata: dict[str, Any] | None = None,
        note: str | None = None,
        due_date: str | None = None,
        deadline: str | None = None,
        onboard_to_aignostics_portal: bool = False,
        validate_only: bool = False,
    ) -> Run:
        """Submit a run for the given application.

        Args:
            application_id (str): The ID of the application to run.
            items (list[InputItem]): The input items for the run.
            application_version (str | None): The version of the application to run.
            custom_metadata (dict[str, Any] | None): Optional custom metadata to attach to the run.
            note (str | None): An optional note for the run.
            due_date (str | None): An optional requested completion time for the run, ISO8601 format.
                The scheduler will try to complete the run before this time, taking
                the subscription tier and available GPU resources into account.
            deadline (str | None): An optional hard deadline for the run, ISO8601 format.
                If processing exceeds this deadline, the run can be aborted.
            onboard_to_aignostics_portal (bool): True if the run should be onboarded to the Aignostics Portal.
            validate_only (bool): If True, cancel the run post validation, before analysis.

        Returns:
            Run: The submitted run.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            ValueError: If
                the application version ID is invalid
                or items invalid
                or due_date not ISO 8601
                or due_date not in the future.
            RuntimeError: If submitting the run failed unexpectedly.
        """
        self._validate_due_date(due_date)
        try:
            if custom_metadata is None:
                custom_metadata = {}
            custom_metadata["sdk"] = {
                "note": note,
                "workflow": {
                    "onboard_to_aignostics_portal": onboard_to_aignostics_portal,
                    "validate_only": validate_only,
                },
                "scheduling": {
                    "due_date": due_date,
                    "deadline": deadline,
                },
            }
            custom_metadata["sdk"]["note"] = note
            return self._get_platform_client().runs.submit(
                application_id=application_id,
                items=items,
                application_version=application_version,
                custom_metadata=custom_metadata,
            )
        except ValueError as e:
            message = f"Failed to submit application run for '{application_id}' (version: {application_version}): {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except Exception as e:
            message = f"Failed to submit application run for '{application_id}' (version: {application_version}): {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_cancel(self, run_id: str) -> None:
        """Cancel a run by its ID.

        Args:
            run_id (str): The ID of the run to cancel

        Raises:
            Exception: If the client cannot be created.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If
                the run ID is invalid
                or the run cannot be canceled given its current state.
            RuntimeError: If canceling the run fails unexpectedly.
        """
        try:
            self.application_run(run_id).cancel()
        except ValueError as e:
            message = f"Failed to cancel application run with ID '{run_id}': ValueError {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except ApiException as e:
            if e.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                message = f"Run ID '{run_id}' invalid: {e!s}."
                logger.warning(message)
                raise ValueError(message) from e
            message = f"Failed to retrieve application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e
        except Exception as e:
            message = f"Failed to cancel application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_delete(self, run_id: str) -> None:
        """Delete a run by its ID.

        Args:
            run_id (str): The ID of the run to delete

        Raises:
            Exception: If the client cannot be created.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If
                the run ID is invalid
                or the run cannot be deleted given its current state.
            RuntimeError: If deleting the run fails unexpectedly.
        """
        try:
            logger.debug("Deleting application run with ID '%s'", run_id)
            self.application_run(run_id).delete()
            logger.debug("Deleted application run with ID '%s'", run_id)
        except ValueError as e:
            message = f"Failed to delete application run with ID '{run_id}': ValueError {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to delete application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_download_static(  # noqa: PLR0913, PLR0917
        run_id: str,
        destination_directory: Path,
        create_subdirectory_for_run: bool = True,
        create_subdirectory_per_item: bool = True,
        wait_for_completion: bool = True,
        qupath_project: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
    ) -> Path:
        """Download application run results with progress tracking, static variant.

        Args:
            run_id (str): The ID of the application run to download.
            destination_directory (Path): Directory to save downloaded files.
            create_subdirectory_for_run (bool): Whether to create a subdirectory for the run.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item,
                if not set, all items will be downloaded to the same directory but prefixed
                with the item external ID and underscore.
            wait_for_completion (bool): Whether to wait for run completion. Defaults to True.
            qupath_project (bool): If True, create QuPath project referencing input slides and results.
                This requires QuPath to be installed. The QuPath project will be created in a subfolder
                of the destination directory.
            download_progress_queue (Queue | None): Queue for GUI progress updates.

        Returns:
            Path: The directory containing downloaded results.

        Raises:
            ValueError: If
                the run ID is invalid
                or destination directory cannot be created.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails unexpectedly.
            requests.HTTPError: If the download fails with an HTTP error.
        """
        return Service().application_run_download(
            run_id,
            destination_directory,
            create_subdirectory_for_run,
            create_subdirectory_per_item,
            wait_for_completion,
            qupath_project,
            download_progress_queue,
        )

    def application_run_download(  # noqa: C901, PLR0912, PLR0913, PLR0914, PLR0915, PLR0917
        self,
        run_id: str,
        destination_directory: Path,
        create_subdirectory_for_run: bool = True,
        create_subdirectory_per_item: bool = True,
        wait_for_completion: bool = True,
        qupath_project: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> Path:
        """Download application run results with progress tracking.

        Args:
            run_id (str): The ID of the application run to download.
            destination_directory (Path): Directory to save downloaded files.
            create_subdirectory_for_run (bool): Whether to create a subdirectory for the run.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item,
                if not set, all items will be downloaded to the same directory but prefixed
                with the item external id and underscore.
            wait_for_completion (bool): Whether to wait for run completion. Defaults to True.
            qupath_project (bool): If True, create QuPath project referencing input slides and results.
                This requires QuPath to be installed. The QuPath project will be created in a subfolder
                of the destination directory.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Returns:
            Path: The directory containing downloaded results.

        Raises:
            ValueError: If
                the run ID is invalid
                or destination directory cannot be created.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails unexpectedly.
            requests.HTTPError: If the download fails with an HTTP error.
        """
        if qupath_project and not has_qupath_extra:
            message = "QuPath project creation requested, but 'qupath' extra is not installed."
            message += 'Start launchpad with `uvx --with "aignostics[qupath]" ....'
            logger.warning(message)
            raise ValueError(message)
        progress = DownloadProgress()
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        application_run = self.application_run(run_id)
        final_destination_directory = destination_directory
        try:
            details = application_run.details()
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except ApiException as e:
            if e.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                message = f"Run ID '{run_id}' invalid: {e!s}."
                logger.warning(message)
                raise ValueError(message) from e
            message = f"Failed to retrieve details for application run '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

        if create_subdirectory_for_run:
            final_destination_directory = destination_directory / details.run_id
        try:
            final_destination_directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            message = f"Failed to create destination directory '{final_destination_directory}': {e}"
            logger.warning(message)
            raise ValueError(message) from e

        if qupath_project:

            def update_qupath_add_input_progress(qupath_add_input_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_INPUT
                progress.qupath_add_input_progress = qupath_add_input_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            logger.debug("Adding input slides to QuPath project ...")
            image_paths = []
            for item in application_run.results():
                image_path = Path(item.external_id)
                if image_path.is_file():
                    image_paths.append(image_path.resolve())
            added = QuPathService.add(
                final_destination_directory / "qupath", image_paths, update_qupath_add_input_progress
            )
            message = f"Added '{added}' input slides to QuPath project."
            logger.info(message)

        logger.debug("Downloading results for run '%s' to '%s'", run_id, final_destination_directory)

        progress.status = DownloadProgressState.CHECKING
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        downloaded_items: set[str] = set()  # Track downloaded items to avoid re-downloading
        while True:
            run_details = application_run.details()  # (Re)load current run details
            progress.run = run_details
            Service._update_progress(progress, download_progress_callable, download_progress_queue)

            self._download_available_items(
                progress,
                application_run,
                final_destination_directory,
                downloaded_items,
                create_subdirectory_per_item,
                download_progress_queue,
                download_progress_callable,
            )

            # TODO(Helmut): More info
            if run_details.state == RunState.TERMINATED:
                logger.debug(
                    "Run '%s' reached final status '%s' with message '%s' (%s).",
                    run_id,
                    run_details.state,
                    run_details.error_message,
                    run_details.error_code,
                )
                break

            if not wait_for_completion:
                logger.debug(
                    "Run '%s' is in progress with status '%s' and message '%s' (%s), "
                    "but not requested to wait for completion.",
                    run_id,
                    run_details.state,
                    run_details.error_message,
                    run_details.error_code,
                )
                break

            logger.debug(
                "Run '%s' is in progress with status '%s', waiting for completion ...", run_id, run_details.state
            )
            progress.status = DownloadProgressState.WAITING
            Service._update_progress(progress, download_progress_callable, download_progress_queue)
            time.sleep(APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS)

        if qupath_project:
            logger.debug("Adding result images to QuPath project ...")

            def update_qupath_add_results_progress(qupath_add_results_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_RESULTS
                progress.qupath_add_results_progress = qupath_add_results_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            added = QuPathService.add(
                final_destination_directory / "qupath",
                [final_destination_directory],
                update_qupath_add_results_progress,
            )
            message = f"Added {added} result images to QuPath project."
            logger.info(message)
            logger.debug("Annotating input slides with polygons from results ...")

            def update_qupath_annotate_input_with_results_progress(
                qupath_annotate_input_with_results_progress: QuPathAnnotateProgress,
            ) -> None:
                progress.status = DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
                progress.qupath_annotate_input_with_results_progress = qupath_annotate_input_with_results_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            total_annotations = 0
            results = list(application_run.results())
            progress.item_count = len(results)
            for item_index, item in enumerate(application_run.results()):
                progress.item_index = item_index
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

                image_path = Path(item.external_id)
                if not image_path.is_file():
                    continue
                for artifact in item.output_artifacts:
                    if (
                        get_mime_type_for_artifact(artifact) == "application/geo+json"
                        and artifact.name == "cell_classification:geojson_polygons"
                    ):
                        artifact_name = artifact.name
                        if create_subdirectory_per_item:
                            path = Path(item.external_id)
                            stem_name = path.stem
                            artifact_path = (
                                final_destination_directory
                                / stem_name
                                / f"{sanitize_path_component(artifact_name)}.json"
                            )
                        else:
                            artifact_path = (
                                final_destination_directory / f"{sanitize_path_component(artifact_name)}.json"
                            )
                        message = f"Annotating input slide '{image_path}' with artifact '{artifact_path}' ..."
                        logger.debug(message)
                        added = QuPathService.annotate(
                            final_destination_directory / "qupath",
                            image_path,
                            artifact_path,
                            update_qupath_annotate_input_with_results_progress,
                        )
                        message = f"Added {added} annotations to input slide '{image_path}' from '{artifact_path}'."
                        logger.info(message)
                        total_annotations += added
            message = f"Added {added} annotations to input slides."
            logger.info(message)

        progress.status = DownloadProgressState.COMPLETED
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        return final_destination_directory

    @staticmethod
    def _update_progress(
        progress: DownloadProgress,
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
        download_progress_queue: Any | None = None,  # noqa: ANN401
    ) -> None:
        if download_progress_callable:
            download_progress_callable(progress)
        if download_progress_queue:
            download_progress_queue.put_nowait(progress)

    def _download_available_items(  # noqa: PLR0913, PLR0917
        self,
        progress: DownloadProgress,
        application_run: Run,
        destination_directory: Path,
        downloaded_items: set[str],
        create_subdirectory_per_item: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download items that are available and not yet downloaded.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            application_run (Run): The application run object.
            destination_directory (Path): Directory to save files.
            downloaded_items (set): Set of already downloaded item external ids.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.
        """
        items = list(application_run.results())
        progress.item_count = len(items)
        for item_index, item in enumerate(items):
            if item.external_id in downloaded_items:
                continue

            if item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL:
                progress.status = DownloadProgressState.DOWNLOADING
                progress.item_index = item_index
                progress.item = item
                progress.item_external_id = item.external_id

                progress.artifact_count = len(item.output_artifacts)
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

                if create_subdirectory_per_item:
                    path = Path(item.external_id)
                    stem_name = path.stem
                    try:
                        # Handle case where path might be relative to destination
                        rel_path = path.relative_to(destination_directory)
                        stem_name = rel_path.stem
                    except ValueError:
                        # Not a subfolder - just use the stem
                        pass
                    item_directory = destination_directory / stem_name
                else:
                    item_directory = destination_directory
                item_directory.mkdir(exist_ok=True)

                for artifact_index, artifact in enumerate(item.output_artifacts):
                    progress.artifact_index = artifact_index
                    progress.artifact = artifact
                    Service._update_progress(progress, download_progress_callable, download_progress_queue)

                    self._download_item_artifact(
                        progress,
                        artifact,
                        item_directory,
                        item.external_id if not create_subdirectory_per_item else "",
                        download_progress_queue,
                        download_progress_callable,
                    )

                downloaded_items.add(item.external_id)

    def _download_item_artifact(  # noqa: PLR0913, PLR0917
        self,
        progress: DownloadProgress,
        artifact: Any,  # noqa: ANN401
        destination_directory: Path,
        prefix: str = "",
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download a an artifact of a result item with progress tracking.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            artifact (Any): The artifact to download.
            destination_directory (Path): Directory to save the file.
            prefix (str): Prefix for the file name, if needed.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Raises:
            ValueError: If
                no checksum metadata is found for the artifact.
            requests.HTTPError: If the download fails.
        """
        metadata = artifact.metadata or {}
        metadata_checksum = metadata.get("checksum_base64_crc32c", "") or metadata.get("checksum_crc32c", "")
        if not metadata_checksum:
            message = f"No checksum metadata found for artifact {artifact.name}"
            logger.error(message)
            raise ValueError(message)

        artifact_path = (
            destination_directory
            / f"{prefix}{sanitize_path_component(artifact.name)}{get_file_extension_for_artifact(artifact)}"
        )

        if artifact_path.exists():
            checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
            with open(artifact_path, "rb") as f:
                while chunk := f.read(APPLICATION_RUN_FILE_READ_CHUNK_SIZE):
                    checksum.update(chunk)  # type: ignore[no-untyped-call]
            existing_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
            if existing_checksum == metadata_checksum:
                logger.debug("File %s already exists with correct checksum", artifact_path)
                return

        self._download_file_with_progress(
            progress,
            artifact.download_url,
            artifact_path,
            metadata_checksum,
            download_progress_queue,
            download_progress_callable,
        )

    @staticmethod
    def _download_file_with_progress(  # noqa: PLR0913, PLR0917
        progress: DownloadProgress,
        signed_url: str,
        artifact_path: Path,
        metadata_checksum: str,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download a file with progress tracking support.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            signed_url (str): The signed URL to download from.
            artifact_path (Path): Path to save the file.
            metadata_checksum (str): Expected CRC32C checksum in base64.
            download_progress_queue (Any | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Raises:
            ValueError: If
                checksum verification fails.
            requests.HTTPError: If download fails.
        """
        logger.debug(
            "Downloading artifact '%s' to '%s' with expected checksum '%s' for item with external id '%s'",
            progress.artifact.name if progress.artifact else "unknown",
            artifact_path,
            metadata_checksum,
            progress.item_external_id or "unknown",
        )
        progress.artifact_download_url = signed_url
        progress.artifact_path = artifact_path
        progress.artifact_downloaded_size = 0
        progress.artifact_downloaded_chunk_size = 0
        progress.artifact_size = None
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]

        with requests.get(signed_url, stream=True, timeout=60) as stream:
            stream.raise_for_status()
            progress.artifact_size = int(stream.headers.get("content-length", 0))
            Service._update_progress(progress, download_progress_callable, download_progress_queue)
            with open(artifact_path, mode="wb") as file:
                for chunk in stream.iter_content(chunk_size=APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
                        checksum.update(chunk)  # type: ignore[no-untyped-call]
                        progress.artifact_downloaded_chunk_size = len(chunk)
                        progress.artifact_downloaded_size += progress.artifact_downloaded_chunk_size
                        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        downloaded_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
        if downloaded_checksum != metadata_checksum:
            artifact_path.unlink()  # Remove corrupted file
            msg = f"Checksum mismatch for {artifact_path}: {downloaded_checksum} != {metadata_checksum}"
            logger.error(msg)
            raise ValueError(msg)
