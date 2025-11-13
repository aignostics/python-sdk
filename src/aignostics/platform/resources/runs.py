"""Runs resource module for the Aignostics client.

This module provides classes for creating and managing application runs on the Aignostics platform.
It includes functionality for starting runs, monitoring status, and downloading results.
"""

import builtins
import time
import typing as t
from collections.abc import Iterator
from pathlib import Path
from time import sleep
from typing import Any, cast

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.exceptions import ServiceException
from aignx.codegen.models import (
    CustomMetadataUpdateRequest,
    ItemCreationRequest,
    ItemOutput,
    ItemResultReadResponse,
    ItemState,
    RunCreationRequest,
    RunCreationResponse,
    RunState,
)
from aignx.codegen.models import (
    ItemResultReadResponse as ItemResultData,
)
from aignx.codegen.models import (
    RunReadResponse as RunData,
)
from aignx.codegen.models import (
    VersionReadResponse as ApplicationVersion,
)
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from loguru import logger
from tenacity import (
    RetryCallState,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from urllib3.exceptions import IncompleteRead, PoolError, ProtocolError, ProxyError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

from aignostics.platform._operation_cache import cached_operation, operation_cache_clear
from aignostics.platform._sdk_metadata import (
    build_item_sdk_metadata,
    build_run_sdk_metadata,
    validate_item_sdk_metadata,
    validate_run_sdk_metadata,
)
from aignostics.platform._settings import settings
from aignostics.platform._utils import (
    calculate_file_crc32c,
    convert_to_json_serializable,
    download_file,
    get_mime_type_for_artifact,
    mime_type_to_file_ending,
)
from aignostics.platform.resources.applications import Versions
from aignostics.platform.resources.utils import paginate
from aignostics.utils import user_agent

RETRYABLE_EXCEPTIONS = (
    ServiceException,  # TODO(Helmut): Do we want this down the road?
    Urllib3TimeoutError,
    PoolError,
    IncompleteRead,
    ProtocolError,
    ProxyError,
)


def _log_retry_attempt(retry_state: RetryCallState) -> None:
    """Custom callback for logging retry attempts with loguru.

    Args:
        retry_state: The retry state from tenacity.
    """
    fn = retry_state.fn
    fn_module = fn.__module__ if fn and hasattr(fn, "__module__") else "<unknown>"
    fn_name = fn.__name__ if fn and hasattr(fn, "__name__") else "<unknown>"
    logger.warning(
        "Retrying {}.{} in {} seconds as attempt {} ended with: {}",
        fn_module,
        fn_name,
        retry_state.next_action.sleep if retry_state.next_action else 0,
        retry_state.attempt_number,
        retry_state.outcome.exception() if retry_state.outcome else "<no outcome>",
    )


LIST_APPLICATION_RUNS_MAX_PAGE_SIZE = 100
LIST_APPLICATION_RUNS_MIN_PAGE_SIZE = 5


class DownloadTimeoutError(RuntimeError):
    """Exception raised when the download operation exceeds its timeout."""


class Run:
    """Represents a single application run.

    Provides operations to check status, retrieve results, and download artifacts.
    """

    def __init__(self, api: PublicApi, run_id: str) -> None:
        """Initializes an Run instance.

        Args:
            api (PublicApi): The configured API client.
            run_id (str): The ID of the application run.
        """
        self._api = api
        self.run_id = run_id

    @classmethod
    def for_run_id(cls, run_id: str, cache_token: bool = True) -> "Run":
        """Creates an Run instance for an existing run.

        Args:
            run_id (str): The ID of the application run.
            cache_token (bool): Whether to cache the API token.

        Returns:
            Run: The initialized Run instance.
        """
        from aignostics.platform._client import Client  # noqa: PLC0415

        return cls(Client.get_api_client(cache_token=cache_token), run_id)

    def details(self, nocache: bool = False) -> RunData:
        """Retrieves the current status of the application run.

        Retries on network and server errors.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            RunData: The run data.

        Raises:
            Exception: If the API request fails.
        """

        @cached_operation(ttl=settings().run_cache_ttl, use_token=True)
        def details_with_retry(run_id: str) -> RunData:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().run_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.get_run_v1_runs_run_id_get(
                    run_id,
                    _request_timeout=settings().run_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return details_with_retry(self.run_id, nocache=nocache)  # type: ignore[call-arg]

    # TODO(Andreas): Low Prio / existed prior to API migration: Please check if this still fails with
    #  Internal Server Error if run was already canceled, should rather fail with 400 bad request in that state.
    def cancel(self) -> None:
        """Cancels the application run.

        Raises:
            Exception: If the API request fails.
        """
        self._api.cancel_run_v1_runs_run_id_cancel_post(
            self.run_id,
            _request_timeout=settings().run_cancel_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()  # Clear all caches since we added a new run

    def delete(self) -> None:
        """Delete the application run.

        Raises:
            Exception: If the API request fails.
        """
        self._api.delete_run_items_v1_runs_run_id_artifacts_delete(
            self.run_id,
            _request_timeout=settings().run_delete_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()  # Clear all caches since we added a new run

    def results(self, nocache: bool = False) -> t.Iterator[ItemResultData]:
        """Retrieves the results of all items in the run.

        Retries on network and server errors.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            list[ItemResultData]: A list of item results.

        Raises:
            Exception: If the API request fails.
        """

        # Create a wrapper function that applies retry logic and caching to each API call
        # Caching at this level ensures having a fresh iterator on cache hits
        @cached_operation(ttl=settings().run_cache_ttl, use_token=True)
        def results_with_retry(run_id: str, **kwargs: object) -> list[ItemResultData]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().run_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.list_run_items_v1_runs_run_id_items_get(
                    run_id=run_id,
                    _request_timeout=settings().run_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )
            )

        return paginate(lambda **kwargs: results_with_retry(self.run_id, nocache=nocache, **kwargs))

    def download_to_folder(  # noqa: C901
        self,
        download_base: Path | str,
        checksum_attribute_key: str = "checksum_base64_crc32c",
        sleep_interval: int = 5,
        timeout_seconds: int | None = None,
        print_status: bool = True,
    ) -> None:
        """Downloads all result artifacts to a folder.

        Monitors run progress and downloads results as they become available.

        Args:
            download_base (Path | str): Base directory to download results to.
            checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
            sleep_interval (int): Time in seconds to wait between checks for new results.
            timeout_seconds (int | None): Optional timeout in seconds for the entire download operation.
            print_status (bool): If True, prints status updates to the console, otherwise just logs.

        Raises:
            ValueError: If the provided path is not a directory.
            DownloadTimeoutError: If the timeout is exceeded while waiting for the run to terminate.
            RuntimeError: If downloads or API requests fail.
        """
        try:
            # create application run base folder
            download_base = Path(download_base)
            if not download_base.is_dir():
                msg = f"{download_base} is not a directory"
                raise ValueError(msg)  # noqa: TRY301
            application_run_dir = Path(download_base) / self.run_id

            # track timeout if specified
            start_time = time.time() if timeout_seconds is not None else None

            # incrementally check for available results
            application_run_state = self.details(nocache=True).state  # no cache to get fresh results
            while application_run_state in {RunState.PROCESSING, RunState.PENDING}:
                # check timeout
                if start_time is not None and timeout_seconds is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout_seconds:
                        msg = (
                            f"Timeout of {timeout_seconds} seconds exceeded while waiting for run {self.run_id} "
                            f"to terminate. Run state: {application_run_state.value}"
                        )
                        raise DownloadTimeoutError(msg)  # noqa: TRY301
                for item in self.results(nocache=True):
                    if item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL:
                        self.ensure_artifacts_downloaded(application_run_dir, item, checksum_attribute_key)
                sleep(sleep_interval)
                application_run_state = self.details(nocache=True).state
                logger.trace("Continuing to wait for run {}, current state: {!r}", self.run_id, self)
                print(self) if print_status else None

            # check if last results have been downloaded yet and report on errors
            for item in self.results(nocache=True):
                match item.output:
                    case ItemOutput.FULL:
                        self.ensure_artifacts_downloaded(application_run_dir, item, checksum_attribute_key)
                    case ItemOutput.NONE:
                        message = (
                            f"{item.external_id} failed with `{item.state.value}`.\n"
                            f"Termination reason `{item.termination_reason}`, "
                            f"error_code:`{item.error_code}`, message `{item.error_message}`."
                        )
                        logger.error(message)
                        print(message) if print_status else None
        except (ValueError, DownloadTimeoutError):
            # Re-raise ValueError and DownloadTimeoutError as-is
            raise
        except Exception as e:
            # Wrap all other exceptions in RuntimeError
            msg = f"Download operation failed for run {self.run_id}: {e}"
            raise RuntimeError(msg) from e

    @staticmethod
    def ensure_artifacts_downloaded(
        base_folder: Path,
        item: ItemResultReadResponse,
        checksum_attribute_key: str = "checksum_base64_crc32c",
        print_status: bool = True,
    ) -> None:
        """Ensures all artifacts for an item are downloaded.

        Downloads missing or partially downloaded artifacts and verifies their integrity.

        Args:
            base_folder (Path): Base directory to download artifacts to.
            item (ItemResultReadResponse): The item result containing the artifacts to download.
            checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
            print_status (bool): If True, prints status updates to the console, otherwise just logs.

        Raises:
            ValueError: If checksums don't match.
            Exception: If downloads fail.
        """
        item_dir = base_folder / item.external_id

        downloaded_at_least_one_artifact = False
        for artifact in item.output_artifacts:
            if artifact.download_url:
                item_dir.mkdir(exist_ok=True, parents=True)
                file_ending = mime_type_to_file_ending(get_mime_type_for_artifact(artifact))
                file_path = item_dir / f"{artifact.name}{file_ending}"
                if not artifact.metadata:
                    logger.error(
                        "Skipping artifact %s for item %s, no metadata present", artifact.name, item.external_id
                    )
                    print(
                        f"> Skipping artifact {artifact.name} for item {item.external_id}, no metadata present"
                    ) if print_status else None
                    continue
                checksum = artifact.metadata[checksum_attribute_key]

                if file_path.exists():
                    file_checksum = calculate_file_crc32c(file_path)
                    if file_checksum != checksum:
                        logger.trace("Resume download for {} to {}", artifact.name, file_path)
                        print(f"> Resume download for {artifact.name} to {file_path}") if print_status else None
                    else:
                        continue
                else:
                    downloaded_at_least_one_artifact = True
                    logger.trace("Download for {} to {}", artifact.name, file_path)
                    print(f"> Download for {artifact.name} to {file_path}") if print_status else None

                # if file is not there at all or only partially downloaded yet
                download_file(artifact.download_url, str(file_path), checksum)

        if downloaded_at_least_one_artifact:
            logger.trace("Downloaded results for item: {} to {}", item.external_id, item_dir)
            print(f"Downloaded results for item: {item.external_id} to {item_dir}") if print_status else None
        else:
            logger.trace("Results for item: {} already present in {}", item.external_id, item_dir)
            print(f"Results for item: {item.external_id} already present in {item_dir}") if print_status else None

    def update_custom_metadata(
        self,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Update custom metadata for this application run.

        Args:
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the run.

        Raises:
            Exception: If the API request fails.
        """
        custom_metadata = custom_metadata or {}
        custom_metadata.setdefault("sdk", {})
        existing_sdk_metadata = custom_metadata.get("sdk", {})
        sdk_metadata = build_run_sdk_metadata(existing_sdk_metadata)
        custom_metadata["sdk"].update(sdk_metadata)
        validate_run_sdk_metadata(custom_metadata["sdk"])

        self._api.put_run_custom_metadata_v1_runs_run_id_custom_metadata_put(
            self.run_id,
            custom_metadata_update_request=CustomMetadataUpdateRequest(
                custom_metadata=cast("dict[str, Any]", convert_to_json_serializable(custom_metadata))
            ),
            _request_timeout=settings().run_submit_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()  # Clear all caches since we updated a run

    # TODO(Andreas): Always returns 404, likely connected with external_id encoding,
    # see test test_cli_run_dump_and_update_item_custom_metadata
    def update_item_custom_metadata(
        self,
        external_id: str,
        custom_metadata: dict[str, Any],
    ) -> None:
        """Update custom metadata for an item in this application run.

        Args:
            external_id (str): The external ID of the item.
            custom_metadata (dict[str, Any]): The new custom metadata to attach to the item.

        Raises:
            Exception: If the API request fails.
        """
        custom_metadata = custom_metadata or {}
        custom_metadata.setdefault("sdk", {})
        existing_sdk_metadata = custom_metadata.get("sdk", {})
        sdk_metadata = build_item_sdk_metadata(existing_sdk_metadata)
        custom_metadata["sdk"].update(sdk_metadata)
        validate_item_sdk_metadata(custom_metadata["sdk"])

        self._api.put_item_custom_metadata_by_run_v1_runs_run_id_items_external_id_custom_metadata_put(
            self.run_id,
            external_id,
            custom_metadata_update_request=CustomMetadataUpdateRequest(
                custom_metadata=cast("dict[str, Any]", convert_to_json_serializable(custom_metadata))
            ),
            _request_timeout=settings().run_submit_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()  # Clear all caches since we updated a run

    def __str__(self) -> str:
        """Returns a string representation of the application run.

        The string includes run ID, status, and item statistics.

        Returns:
            str: String representation of the application run.
        """
        details = cast("RunData", self.details())
        app_status = details.state.value
        items = (
            f"{details.statistics.item_count} items: "
            f"{details.statistics.item_pending_count}/"
            f"{details.statistics.item_processing_count}/"
            f"{details.statistics.item_user_error_count}/"
            f"{details.statistics.item_system_error_count}/"
            f"{details.statistics.item_skipped_count}/"
            f"{details.statistics.item_succeeded_count}"
            " [pending/processing/user-error/system-error/skipped/succeeded]"
        )
        return f"Run `{self.run_id}`: {app_status}, {items}"


class Runs:
    """Resource class for managing application runs.

    Provides operations to submit, find, and retrieve runs.
    """

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Runs resource with the API client.

        Args:
            api (PublicApi): The configured API client.
        """
        self._api = api

    def __call__(self, run_id: str) -> Run:
        """Retrieves an Run instance for an existing run.

        Args:
            run_id (str): The ID of the application run.

        Returns:
            Run: The initialized Run instance.
        """
        return Run(self._api, run_id)

    def submit(
        self,
        application_id: str,
        items: list[ItemCreationRequest],
        application_version: str | None = None,
        custom_metadata: dict[str, Any] | None = None,
    ) -> Run:
        """Submit a new application run.

        Args:
            application_id (str): The ID of the application.
            items (list[ItemCreationRequest]): The run creation request payload.
            application_version (str|None): The version of the application to use.
                If None, the latest version is used.
            custom_metadata (dict[str, Any] | None): Optional metadata to attach to the run.

        Returns:
            Run: The submitted application run.

        Raises:
            ValueError: If the payload is invalid.
            Exception: If the API request fails.
        """
        custom_metadata = custom_metadata or {}
        custom_metadata.setdefault("sdk", {})
        existing_sdk_metadata = custom_metadata.get("sdk", {})
        sdk_metadata = build_run_sdk_metadata(existing_sdk_metadata)
        custom_metadata["sdk"].update(sdk_metadata)
        validate_run_sdk_metadata(custom_metadata["sdk"])
        self._amend_input_items_with_sdk_metadata(items)
        payload = RunCreationRequest(
            application_id=application_id,
            version_number=application_version,
            custom_metadata=cast("dict[str, Any]", convert_to_json_serializable(custom_metadata)),
            items=items,
        )
        self._validate_input_items(payload)
        res: RunCreationResponse = self._api.create_run_v1_runs_post(
            payload,
            _request_timeout=settings().run_submit_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()  # Clear all caches since we added a new run
        return Run(self._api, str(res.run_id))

    def list(  # noqa: PLR0913, PLR0917
        self,
        application_id: str | None = None,
        application_version: str | None = None,
        external_id: str | None = None,
        custom_metadata: str | None = None,
        sort: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
        nocache: bool = False,
    ) -> Iterator[Run]:
        """Find application runs, optionally filtered by application id and/or version.

        Retries on network and server errors.

        Args:
            application_id (str | None): Optional application ID to filter by.
            application_version (str | None): Optional application version to filter by.
            external_id (str | None): The external ID to filter runs. If None, no filtering is applied.
            custom_metadata (str | None): Optional metadata filter in JSONPath format.
            sort (str | None): Optional field to sort by. Prefix with '-' for descending order.
            page_size (int): Number of items per page, defaults to max
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Iterator[Run]: An iterator yielding application run handles.

        Raises:
            ValueError: If page_size is greater than 100.
            Exception: If the API request fails.
        """
        return (
            Run(self._api, response.run_id)
            for response in self.list_data(
                application_id=application_id,
                application_version=application_version,
                external_id=external_id,
                custom_metadata=custom_metadata,
                sort=sort,
                page_size=page_size,
                nocache=nocache,
            )
        )

    def list_data(  # noqa: PLR0913, PLR0917
        self,
        application_id: str | None = None,
        application_version: str | None = None,
        external_id: str | None = None,
        custom_metadata: str | None = None,
        sort: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
        nocache: bool = False,
    ) -> t.Iterator[RunData]:
        """Fetch application runs, optionally filtered by application version.

        Retries on network and server errors.

        Args:
            application_id (str | None): Optional application ID to filter by.
            application_version (str | None): Optional application version ID to filter by.
            external_id (str | None): The external ID to filter runs. If None, no filtering is applied.
            custom_metadata (str | None): Optional metadata filter in JSONPath format.
            sort (str | None): Optional field to sort by. Prefix with '-' for descending order.
            page_size (int): Number of items per page, defaults to max
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Iterator[RunData]: Iterator yielding application run data.

        Raises:
            ValueError: If page_size is greater than 100.
            Exception: If the API request fails.
        """
        if page_size > LIST_APPLICATION_RUNS_MAX_PAGE_SIZE:
            message = (
                f"page_size is must be less than or equal to {LIST_APPLICATION_RUNS_MAX_PAGE_SIZE}, but got {page_size}"
            )
            raise ValueError(message)

        @cached_operation(ttl=settings().run_cache_ttl, use_token=True)
        def list_data_with_retry(**kwargs: object) -> list[RunData]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().run_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.list_runs_v1_runs_get(
                    _request_timeout=settings().run_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )
            )

        return paginate(
            lambda **kwargs: list_data_with_retry(
                application_id=application_id,
                application_version=application_version,
                external_id=external_id,
                custom_metadata=custom_metadata,
                sort=[sort] if sort else None,
                nocache=nocache,
                **kwargs,
            ),
            page_size=page_size,
        )

    @staticmethod
    def _amend_input_items_with_sdk_metadata(items: builtins.list[ItemCreationRequest]) -> None:
        """Amends input items with SDK metadata.

        Args:
            items (builtins.list[ItemCreationRequest]): The list of item creation requests to amend.
        """
        for item in items:
            item_custom_metadata = item.custom_metadata or {}
            item_custom_metadata.setdefault("sdk", {})
            existing_item_sdk_metadata = item_custom_metadata.get("sdk")
            item_sdk_metadata = build_item_sdk_metadata(existing_item_sdk_metadata)
            item_custom_metadata["sdk"].update(item_sdk_metadata)
            validate_item_sdk_metadata(item_custom_metadata["sdk"])
            item.custom_metadata = cast("dict[str, Any]", convert_to_json_serializable(item_custom_metadata))

    def _validate_input_items(self, payload: RunCreationRequest) -> None:
        """Validates the input items in a run creation request.

        Checks that external ids are unique, all required artifacts are provided,
        and artifact metadata matches the expected schema.

        Args:
            payload (RunCreationRequest): The run creation request payload.

        Raises:
            ValueError: If validation fails.
            Exception: If the API request fails.
        """
        # validate metadata based on schema of application version
        app_version = cast(
            "ApplicationVersion",
            Versions(self._api).details(
                application_id=payload.application_id, application_version=payload.version_number
            ),
        )
        schema_idx = {
            input_artifact.name: input_artifact.metadata_schema for input_artifact in app_version.input_artifacts
        }
        external_ids = set()
        for item in payload.items:
            # verify external IDs are unique
            if item.external_id in external_ids:
                msg = f"Duplicate external ID `{item.external_id}` in items."
                raise ValueError(msg)
            external_ids.add(item.external_id)

            schema_check = set(schema_idx.keys())
            for artifact in item.input_artifacts:
                # check if artifact is in schema
                if artifact.name not in schema_idx:
                    msg = f"Invalid artifact `{artifact.name}`, application version requires: {schema_idx.keys()}"
                    raise ValueError(msg)
                try:
                    # validate metadata
                    validate(artifact.metadata, schema=schema_idx[artifact.name])
                    schema_check.remove(artifact.name)
                except ValidationError as e:
                    msg = f"Invalid metadata for artifact `{artifact.name}`: {e.message}"
                    raise ValueError(msg) from e
            # all artifacts set?
            if len(schema_check) > 0:
                msg = f"Missing artifact(s): {schema_check}"
                raise ValueError(msg)
