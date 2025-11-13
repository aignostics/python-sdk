"""Service of the application module."""

import base64
import re
import time
from collections.abc import Callable, Generator
from http import HTTPStatus
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import google_crc32c
import requests
from loguru import logger

from aignostics.bucket import Service as BucketService
from aignostics.constants import (
    TEST_APP_APPLICATION_ID,
)
from aignostics.platform import (
    LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    ApiException,
    Application,
    ApplicationSummary,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
    NotFoundException,
    Run,
    RunData,
    RunOutput,
    RunState,
)
from aignostics.platform import (
    Service as PlatformService,
)
from aignostics.utils import BaseService, Health, sanitize_path_component
from aignostics.wsi import Service as WSIService

from ._download import (
    download_available_items,
    download_url_to_file_with_progress,
    extract_filename_from_url,
    update_progress,
)
from ._models import DownloadProgress, DownloadProgressState
from ._settings import Settings
from ._utils import (
    get_mime_type_for_artifact,
    get_supported_extensions_for_application,
    validate_due_date,
)

has_qupath_extra = find_spec("ijson")
if has_qupath_extra:
    from aignostics.qupath import AddProgress as QuPathAddProgress
    from aignostics.qupath import AnnotateProgress as QuPathAnnotateProgress
    from aignostics.qupath import Service as QuPathService


APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS = 5
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


class Service(BaseService):  # noqa: PLR0904
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
            logger.trace("Creating platform client.")
            self._client = Client()
        else:
            logger.trace("Reusing platform client.")
        return self._client

    def _get_platform_service(self) -> PlatformService:
        """Get the platform service.

        Returns:
            PlatformService: The platform service.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._platform_service is None:
            logger.trace("Creating platform service.")
            self._platform_service = PlatformService()
        else:
            logger.trace("Reusing platform service.")
        return self._platform_service

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
            logger.warning("key '{}' not found in entry, ignoring mapping for '{}'", key, external_id)
            return

        logger.trace("Updating key '{}' with value '{}' for external_id '{}'.", key, value, external_id)
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
        logger.trace("Generating metadata from source directory: {}", source_directory)

        # TODO(Helmut): Use it
        _ = Service().application_version(application_id, application_version)

        metadata = []

        try:
            extensions = get_supported_extensions_for_application(application_id)
            for extension in extensions:
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
                    except Exception as e:
                        message = f"Failed to process file '{file_path}': {e}"
                        logger.warning(message)
                        continue

            logger.trace("Generated metadata for {} files", len(metadata))
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

        logger.trace("Uploading files with upload ID '{}'", upload_prefix)
        app_version = Service().application_version(application_id, application_version=application_version)
        for row in metadata:
            external_id = row["external_id"]
            source_file_path = Path(row["external_id"])
            if not source_file_path.is_file():
                logger.warning("Source file '{}' does not exist.", row["external_id"])
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
            logger.trace("Generated signed upload URL '{}' for object '{}'", signed_upload_url, platform_bucket_url)
            if upload_progress_queue:
                upload_progress_queue.put_nowait({
                    "external_id": external_id,
                    "platform_bucket_url": platform_bucket_url,
                })
            file_size = source_file_path.stat().st_size
            logger.trace(
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
        logger.debug("Upload completed successfully.")
        return True

    @staticmethod
    def application_runs_static(  # noqa: PLR0913, PLR0917
        application_id: str | None = None,
        application_version: str | None = None,
        external_id: str | None = None,
        has_output: bool = False,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
        tags: set[str] | None = None,
        query: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get a list of all application runs, static variant.

        Args:
            application_id (str | None): The ID of the application to filter runs. If None, no filtering is applied.
            application_version (str | None): The version of the application to filter runs.
                If None, no filtering is applied.
            external_id (str | None): The external ID to filter runs. If None, no filtering is applied.
            has_output (bool): If True, only runs with partial or full output are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
                Cannot be used together with query parameter.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.
            tags (set[str] | None): Optional set of tags to filter runs. All tags must match.
                Cannot be used together with query parameter.
            query (str | None): Optional string to filter runs by note OR tags (case insensitive partial match).
                If None, no filtering is applied. Cannot be used together with custom_metadata, note_regex, or tags.
                Performs a union search: matches runs where the query appears in the note OR matches any tag.
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.

        Returns:
            list[RunData]: A list of all application runs.

        Raises:
            ValueError: If query is used together with custom_metadata, note_regex, or tags.
            RuntimeError: If the application run list cannot be retrieved.
        """
        return [
            {
                "run_id": run.run_id,
                "application_id": run.application_id,
                "version_number": run.version_number,
                "submitted_at": run.submitted_at,
                "terminated_at": run.terminated_at,
                "state": run.state,
                "termination_reason": run.termination_reason,
                "item_count": run.statistics.item_count,
                "item_succeeded_count": run.statistics.item_succeeded_count,
                "tags": run.custom_metadata.get("sdk", {}).get("tags", []) if run.custom_metadata else [],
            }
            for run in Service().application_runs(
                application_id=application_id,
                application_version=application_version,
                external_id=external_id,
                has_output=has_output,
                note_regex=note_regex,
                note_query_case_insensitive=note_query_case_insensitive,
                tags=tags,
                query=query,
                limit=limit,
            )
        ]

    def application_runs(  # noqa: C901, PLR0912, PLR0913, PLR0914, PLR0915, PLR0917
        self,
        application_id: str | None = None,
        application_version: str | None = None,
        external_id: str | None = None,
        has_output: bool = False,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
        tags: set[str] | None = None,
        query: str | None = None,
        limit: int | None = None,
    ) -> list[RunData]:
        """Get a list of all application runs.

        Args:
            application_id (str | None): The ID of the application to filter runs. If None, no filtering is applied.
            application_version (str | None): The version of the application to filter runs.
                If None, no filtering is applied.
            external_id (str | None): The external ID to filter runs. If None, no filtering is applied.
            has_output (bool): If True, only runs with partial or full output are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
                Cannot be used together with query parameter.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.
            tags (set[str] | None): Optional set of tags to filter runs. All tags must match.
                If None, no filtering is applied. Cannot be used together with query parameter.
            query (str | None): Optional string to filter runs by note OR tags (case insensitive partial match).
                If None, no filtering is applied. Cannot be used together with custom_metadata, note_regex, or tags.
                Performs a union search: matches runs where the query appears in the note OR matches any tag.
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.

        Returns:
            list[RunData]: A list of all application runs.

        Raises:
            ValueError: If query is used together with custom_metadata, note_regex, or tags.
            RuntimeError: If the application run list cannot be retrieved.
        """
        # Validate that query is not used with other metadata filters
        if query is not None:
            if note_regex is not None:
                message = "Cannot use 'query' parameter together with 'note_regex' parameter."
                logger.warning(message)
                raise ValueError(message)
            if tags is not None:
                message = "Cannot use 'query' parameter together with 'tags' parameter."
                logger.warning(message)
                raise ValueError(message)

        if limit is not None and limit <= 0:
            return []
        runs = []
        page_size = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
        try:
            # Handle query parameter with union semantics (note OR tags)
            if query:
                # Search for runs matching query in notes
                note_runs_dict: dict[str, RunData] = {}
                flag_case_insensitive = ' flag "i"'
                escaped_query = query.replace("\\", "\\\\").replace('"', '\\"')
                custom_metadata_note = f'$.sdk.note ? (@ like_regex "{escaped_query}"{flag_case_insensitive})'

                note_run_iterator = self._get_platform_client().runs.list_data(
                    application_id=application_id,
                    application_version=application_version,
                    external_id=external_id,
                    custom_metadata=custom_metadata_note,
                    sort="-submitted_at",
                    page_size=page_size,
                )
                for run in note_run_iterator:
                    if has_output and run.output == RunOutput.NONE:
                        continue
                    note_runs_dict[run.run_id] = run
                    if limit is not None and len(note_runs_dict) >= limit:
                        break

                # Search for runs matching query in tags
                tag_runs_dict: dict[str, RunData] = {}
                custom_metadata_tags = f'$.sdk.tags ? (@ like_regex "{escaped_query}"{flag_case_insensitive})'

                tag_run_iterator = self._get_platform_client().runs.list_data(
                    application_id=application_id,
                    application_version=application_version,
                    external_id=external_id,
                    custom_metadata=custom_metadata_tags,
                    sort="-submitted_at",
                    page_size=page_size,
                )
                for run in tag_run_iterator:
                    if has_output and run.output == RunOutput.NONE:
                        continue
                    # Add to dict if not already present from note search
                    if run.run_id not in note_runs_dict:
                        tag_runs_dict[run.run_id] = run
                    if limit is not None and len(note_runs_dict) + len(tag_runs_dict) >= limit:
                        break

                # Union of results from both searches
                runs = list(note_runs_dict.values()) + list(tag_runs_dict.values())

                # Apply limit after union
                if limit is not None and len(runs) > limit:
                    runs = runs[:limit]

                return runs

            custom_metadata = None
            client_side_note_filter = None

            # Handle note_regex filter
            if note_regex:
                flag_case_insensitive = ' flag "i"' if note_query_case_insensitive else ""
                # If we also have tags, we'll need to do note filtering client-side
                if tags:
                    # Store for client-side filtering
                    client_side_note_filter = (note_regex, note_query_case_insensitive)
                else:
                    # No tags, so we can filter note on backend
                    custom_metadata = f'$.sdk.note ? (@ like_regex "{note_regex}"{flag_case_insensitive})'

            # Handle tags filter
            if tags:
                # JSONPath filter to match all of the provided tags in the sdk.tags array
                # PostgreSQL limitation: Cannot use && between separate path expressions as backend crashes with 500
                # Workaround: Filter on backend for ANY tag match, then filter client-side for ALL
                # Use regex alternation to match any of the tags
                escaped_tags = [tag.replace('"', '\\"').replace("\\", "\\\\") for tag in tags]
                # Create regex pattern: ^(tag1|tag2|tag3)$
                regex_pattern = "^(" + "|".join(escaped_tags) + ")$"
                custom_metadata = f'$.sdk.tags ? (@ like_regex "{regex_pattern}")'

            run_iterator = self._get_platform_client().runs.list_data(
                application_id=application_id,
                application_version=application_version,
                external_id=external_id,
                custom_metadata=custom_metadata,
                sort="-submitted_at",
                page_size=page_size,
            )
            for run in run_iterator:
                if has_output and run.output == RunOutput.NONE:
                    continue
                # Client-side filtering when combining multiple criteria
                # 1. If multiple tags specified, ensure ALL are present
                if tags and len(tags) > 1:
                    # Backend filter with regex alternation matches ANY tag
                    # Now verify ALL tags are present in run metadata
                    run_tags = set()
                    if run.custom_metadata and "sdk" in run.custom_metadata:
                        sdk_metadata = run.custom_metadata.get("sdk", {})
                        if "tags" in sdk_metadata:
                            run_tags = set(sdk_metadata.get("tags", []))

                    # Check if all required tags are present
                    if not tags.issubset(run_tags):
                        continue  # Skip this run, not all tags match

                # 2. If note filter is applied client-side (when combined with tags)
                if client_side_note_filter:
                    note_pattern, case_insensitive = client_side_note_filter
                    run_note = None
                    if run.custom_metadata and "sdk" in run.custom_metadata:
                        sdk_metadata = run.custom_metadata.get("sdk", {})
                        run_note = sdk_metadata.get("note")

                    # Check if note matches the regex pattern
                    if run_note:
                        flags = re.IGNORECASE if case_insensitive else 0
                        if not re.search(note_pattern, run_note, flags):
                            continue  # Skip this run, note doesn't match
                    else:
                        continue  # Skip this run, no note present

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
        tags: set[str] | None = None,
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
            tags (set[str] | None): Optional set of tags to attach to the run for filtering.
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
        validate_due_date(due_date)
        logger.trace("Submitting application run with metadata: {}", metadata)
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

            item_metadata = {
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
            }

            # Only add specimen and staining_method metadata if not test-app
            # TODO(Helmut): Remove condition when test-app reached input parity with heta
            if application_id != TEST_APP_APPLICATION_ID:
                item_metadata["specimen"] = {
                    "disease": row["disease"],
                    "tissue": row["tissue"],
                }
                item_metadata["staining_method"] = row["staining_method"]

            items.append(
                InputItem(
                    external_id=row["external_id"],
                    input_artifacts=[
                        InputArtifact(
                            name=input_artifact_name,
                            download_url=download_url,
                            metadata=item_metadata,
                        )
                    ],
                    custom_metadata={
                        "sdk": {
                            "platform_bucket": {
                                "bucket_name": bucket_name,
                                "object_key": object_key,
                                "signed_download_url": download_url,
                            }
                        }
                    },
                )
            )
        logger.trace("Items for application run submission: {}", items)

        try:
            run = self.application_run_submit(
                application_id=application_id,
                items=items,
                application_version=app_version.version_number,
                custom_metadata=custom_metadata,
                note=note,
                tags=tags,
                due_date=due_date,
                deadline=deadline,
                onboard_to_aignostics_portal=onboard_to_aignostics_portal,
                validate_only=validate_only,
            )
            logger.debug(
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
        tags: set[str] | None = None,
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
            tags (set[str] | None): Optional set of tags to attach to the run for filtering.
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
        validate_due_date(due_date)
        try:
            if custom_metadata is None:
                custom_metadata = {}

            sdk_metadata: dict[str, Any] = {}
            if note:
                sdk_metadata["note"] = note
            if tags:
                sdk_metadata["tags"] = tags
            if onboard_to_aignostics_portal or validate_only:
                sdk_metadata["workflow"] = {
                    "onboard_to_aignostics_portal": onboard_to_aignostics_portal,
                    "validate_only": validate_only,
                }
            if due_date or deadline:
                sdk_metadata["scheduling"] = {}
                if due_date:
                    sdk_metadata["scheduling"]["due_date"] = due_date
                if deadline:
                    sdk_metadata["scheduling"]["deadline"] = deadline

            custom_metadata["sdk"] = sdk_metadata

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

    def application_run_update_custom_metadata(
        self,
        run_id: str,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Update custom metadata for an existing application run.

        Args:
            run_id (str): The ID of the run to update
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the run.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If the run ID is invalid.
            RuntimeError: If updating the run metadata fails unexpectedly.
        """
        try:
            logger.trace("Updating custom metadata for run with ID '{}'", run_id)
            self._get_platform_client().run(run_id).update_custom_metadata(custom_metadata)
            logger.trace("Updated custom metadata for run with ID '{}'", run_id)
        except ValueError as e:
            message = f"Failed to update custom metadata for run with ID '{run_id}': ValueError {e}"
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
            message = f"Failed to update custom metadata for run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e
        except Exception as e:
            message = f"Failed to update custom metadata for run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_update_custom_metadata_static(
        run_id: str,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Static wrapper for updating custom metadata for an application run.

        Args:
            run_id (str): The ID of the run to update
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the run.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If the run ID is invalid.
            RuntimeError: If updating the run metadata fails unexpectedly.
        """
        Service().application_run_update_custom_metadata(run_id, custom_metadata)

    def application_run_update_item_custom_metadata(
        self,
        run_id: str,
        external_id: str,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Update custom metadata for an existing item in an application run.

        Args:
            run_id (str): The ID of the run containing the item
            external_id (str): The external ID of the item to update
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the item.

        Raises:
            NotFoundException: If the application run or item with the given IDs is not found.
            ValueError: If the run ID or item external ID is invalid.
            RuntimeError: If updating the item metadata fails unexpectedly.
        """
        try:
            logger.trace(
                "Updating custom metadata for item '%s' in run with ID '%s'",
                external_id,
                run_id,
            )
            self._get_platform_client().run(run_id).update_item_custom_metadata(
                external_id,
                custom_metadata,
            )
            logger.trace(
                "Updated custom metadata for item '%s' in run with ID '%s'",
                external_id,
                run_id,
            )
        except ValueError as e:
            message = (
                f"Failed to update custom metadata for item '{external_id}' in run with ID '{run_id}': ValueError {e}"
            )
            logger.warning(message)
            raise ValueError(message) from e
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' or item '{external_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except ApiException as e:
            if e.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                message = f"Run ID '{run_id}' or item external ID '{external_id}' invalid: {e!s}."
                logger.warning(message)
                raise ValueError(message) from e
            message = f"Failed to update custom metadata for item '{external_id}' in run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e
        except Exception as e:
            message = f"Failed to update custom metadata for item '{external_id}' in run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_update_item_custom_metadata_static(
        run_id: str,
        external_id: str,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Static wrapper for updating custom metadata for an item in an application run.

        Args:
            run_id (str): The ID of the run containing the item
            external_id (str): The external ID of the item to update
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the item.

        Raises:
            NotFoundException: If the application run or item with the given IDs is not found.
            ValueError: If the run ID or item external ID is invalid.
            RuntimeError: If updating the item metadata fails unexpectedly.
        """
        Service().application_run_update_item_custom_metadata(run_id, external_id, custom_metadata)

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
            logger.trace("Deleting application run with ID '{}'", run_id)
            self.application_run(run_id).delete()
            logger.trace("Deleted application run with ID '{}'", run_id)
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
                or destination directory cannot be created
                or QuPath extra is not installed when qupath_project=True.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails.
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
                or destination directory cannot be created
                or QuPath extra is not installed when qupath_project=True.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails.
        """
        if qupath_project and not has_qupath_extra:
            message = "QuPath project creation requested, but 'qupath' extra is not installed."
            message += 'Start launchpad with `uvx --with "aignostics[qupath]" ....'
            logger.warning(message)
            raise ValueError(message)
        progress = DownloadProgress()
        update_progress(progress, download_progress_callable, download_progress_queue)

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

        results = list(application_run.results())
        for item_index, item in enumerate(results):
            if item.external_id.startswith(("gs://", "http://", "https://")):
                # Download URL to local input directory and update external_id
                try:
                    filename = extract_filename_from_url(item.external_id)
                    local_path = final_destination_directory / "input" / filename
                    if not local_path.exists():
                        progress.item_index = item_index
                        progress.item = item
                        download_url_to_file_with_progress(
                            progress,
                            item.external_id,
                            local_path,
                            download_progress_queue,
                            download_progress_callable,
                        )
                    item.external_id = str(local_path)  # Update external_id so subsequent code uses the local path
                except Exception as e:
                    logger.warning(
                        "Failed to download input slide from '%s' to '%s': %s", item.external_id, local_path, e
                    )

        if qupath_project:

            def update_qupath_add_input_progress(qupath_add_input_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_INPUT
                progress.qupath_add_input_progress = qupath_add_input_progress
                update_progress(progress, download_progress_callable, download_progress_queue)

            logger.trace("Adding input slides to QuPath project ...")
            image_paths = []
            for item in results:
                local_path = Path(item.external_id)
                if not local_path.is_file():
                    logger.warning("Input slide '{}' not found, skipping QuPath addition.", local_path)
                    continue
                image_paths.append(local_path.resolve())
            added = QuPathService.add(
                final_destination_directory / "qupath", image_paths, update_qupath_add_input_progress
            )
            message = f"Added '{added}' input slides to QuPath project."
            logger.debug(message)

        logger.trace("Downloading results for run '{}' to '{}'", run_id, final_destination_directory)

        progress.status = DownloadProgressState.CHECKING
        update_progress(progress, download_progress_callable, download_progress_queue)

        downloaded_items: set[str] = set()  # Track downloaded items to avoid re-downloading
        while True:
            run_details = application_run.details()  # (Re)load current run details
            progress.run = run_details
            update_progress(progress, download_progress_callable, download_progress_queue)

            download_available_items(
                progress,
                application_run,
                final_destination_directory,
                downloaded_items,
                create_subdirectory_per_item,
                download_progress_queue,
                download_progress_callable,
            )

            if run_details.state == RunState.TERMINATED:
                logger.trace(
                    "Run '%s' reached final status '%s' with message '%s' (%s).",
                    run_id,
                    run_details.state,
                    run_details.error_message,
                    run_details.error_code,
                )
                break

            if not wait_for_completion:
                logger.trace(
                    "Run '%s' is in progress with status '%s' and message '%s' (%s), "
                    "but not requested to wait for completion.",
                    run_id,
                    run_details.state,
                    run_details.error_message,
                    run_details.error_code,
                )
                break

            logger.trace(
                "Run '%s' is in progress with status '%s', waiting for completion ...", run_id, run_details.state
            )
            progress.status = DownloadProgressState.WAITING
            update_progress(progress, download_progress_callable, download_progress_queue)
            time.sleep(APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS)

        if qupath_project:
            logger.trace("Adding result images to QuPath project ...")

            def update_qupath_add_results_progress(qupath_add_results_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_RESULTS
                progress.qupath_add_results_progress = qupath_add_results_progress
                update_progress(progress, download_progress_callable, download_progress_queue)

            added = QuPathService.add(
                final_destination_directory / "qupath",
                [final_destination_directory],
                update_qupath_add_results_progress,
            )
            message = f"Added {added} result images to QuPath project."
            logger.debug(message)
            logger.trace("Annotating input slides with polygons from results ...")

            def update_qupath_annotate_input_with_results_progress(
                qupath_annotate_input_with_results_progress: QuPathAnnotateProgress,
            ) -> None:
                progress.status = DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
                progress.qupath_annotate_input_with_results_progress = qupath_annotate_input_with_results_progress
                update_progress(progress, download_progress_callable, download_progress_queue)

            total_annotations = 0
            progress.item_count = len(results)
            for item_index, item in enumerate(results):
                progress.item_index = item_index
                update_progress(progress, download_progress_callable, download_progress_queue)

                image_path = Path(item.external_id)
                if not image_path.is_file():
                    logger.warning("Input slide '{}' not found, skipping QuPath annotation.", image_path)
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
                        logger.trace(message)
                        added = QuPathService.annotate(
                            final_destination_directory / "qupath",
                            image_path,
                            artifact_path,
                            update_qupath_annotate_input_with_results_progress,
                        )
                        message = f"Added {added} annotations to input slide '{image_path}' from '{artifact_path}'."
                        logger.debug(message)
                        total_annotations += added
            message = f"Added {added} annotations to input slides."
            logger.debug(message)

        progress.status = DownloadProgressState.COMPLETED
        update_progress(progress, download_progress_callable, download_progress_queue)

        return final_destination_directory
