"""Runs resource module for the Aignostics client.

This module provides classes for creating and managing application runs on the Aignostics platform.
It includes functionality for starting runs, monitoring status, and downloading results.
"""

import builtins
import time
import typing as t
from collections.abc import Callable, Iterator
from http import HTTPStatus
from pathlib import Path
from time import sleep
from typing import Any, cast

import requests
from aignx.codegen.exceptions import ApiException, NotFoundException, ServiceException
from aignx.codegen.models import (
    ArtifactOutput,
    CustomMetadataUpdateRequest,
    ItemCreationRequest,
    ItemOutput,
    ItemResultReadResponse,
    ItemState,
    ItemTerminationReason,
    RunCreationRequest,
    RunCreationResponse,
    RunState,
    SchedulingRequest,
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
from sentry_sdk import metrics
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
)

from aignostics.platform._api import (
    RETRYABLE_EXCEPTIONS,
    _AuthenticatedApi,
    _AuthenticatedResource,
    _log_retry_attempt,
)
from aignostics.platform._authentication import get_token
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

LIST_APPLICATION_RUNS_MAX_PAGE_SIZE = 100
LIST_APPLICATION_RUNS_MIN_PAGE_SIZE = 5


class DownloadTimeoutError(RuntimeError):
    """Exception raised when the download operation exceeds its timeout."""


_REDIRECT_STATUSES = frozenset({
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
    HTTPStatus.TEMPORARY_REDIRECT,
    HTTPStatus.PERMANENT_REDIRECT,
})


class Artifact(_AuthenticatedResource):
    """Represents a single output artifact belonging to a run.

    Provides operations to resolve a fresh presigned download URL via the
    ``GET /api/v1/runs/{run_id}/artifacts/{artifact_id}/file`` endpoint.
    """

    def __init__(self, api: _AuthenticatedApi, run_id: str, artifact_id: str) -> None:
        """Initializes an Artifact instance.

        Args:
            api (_AuthenticatedApi): The configured API client.
            run_id (str): The ID of the parent run.
            artifact_id (str): The ID of the output artifact.
        """
        super().__init__(api)
        self.run_id = run_id
        self.artifact_id = artifact_id

    def get_download_url(self) -> str:
        """Resolve a fresh presigned download URL for this artifact.

        Calls ``GET /api/v1/runs/{run_id}/artifacts/{artifact_id}/file`` with
        ``allow_redirects=False`` and returns the presigned URL from the redirect
        ``Location`` header. The presigned URL is short-lived; resolve immediately
        before downloading.

        The generated client cannot be used directly because urllib3 follows the
        redirect automatically and would fetch the artifact body — losing the URL
        we need for streaming/chunked downloads with checksum verification.

        Returns:
            str: A time-limited presigned URL.

        Raises:
            NotFoundException: 404 — artifact not found for the run.
            ApiException: Other 4xx (e.g. 403 forbidden, 410 gone).
            ServiceException: 5xx, request timeouts, or connection errors
                (after retry attempts have been exhausted).
            RuntimeError: 3xx response with no Location header, or any other
                unexpected status the API contract does not define.
        """
        configuration = self._api.api_client.configuration
        host = configuration.host.rstrip("/")
        endpoint_url = f"{host}/api/v1/runs/{self.run_id}/artifacts/{self.artifact_id}/file"
        proxy = getattr(configuration, "proxy", None)
        ssl_ca_cert = getattr(configuration, "ssl_ca_cert", None)
        verify_ssl = getattr(configuration, "verify_ssl", True)
        ssl_verify: bool | str = ssl_ca_cert or verify_ssl
        # Honor the codegen client's token_provider when set: Client.get_api_client()
        # wires it up with use_cache=cache_token, so a user who instantiates
        # Client(cache_token=False) does not want us to read/write the token cache.
        # Fall back to get_token() only when the configuration was built outside
        # of Client (e.g. unit tests with bare PublicApi).
        token_provider = getattr(configuration, "token_provider", None) or get_token

        return Retrying(
            retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
            stop=stop_after_attempt(settings().run_retry_attempts),
            wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
            before_sleep=_log_retry_attempt,
            reraise=True,
        )(lambda: self._fetch_redirect_url(endpoint_url, ssl_verify, proxy, token_provider))

    def _fetch_redirect_url(
        self,
        endpoint_url: str,
        ssl_verify: bool | str,
        proxy: str | None,
        token_provider: Callable[[], str],
    ) -> str:
        """Issue the GET and return the presigned URL from the 3xx Location header.

        Args:
            endpoint_url: Full /file endpoint URL.
            ssl_verify: True/False or CA bundle path, mirroring the codegen client config.
            proxy: Optional HTTP/HTTPS proxy URL, mirroring the codegen client config.
            token_provider: Callable returning a fresh bearer token. Honors the
                codegen client's ``cache_token`` choice when sourced from
                ``Configuration.token_provider``.

        Returns:
            str: The presigned URL extracted from the Location header.

        Raises:
            NotFoundException: 404.
            ApiException: 4xx other than 404.
            ServiceException: 5xx or transient network errors (caught & wrapped so
                the outer Retrying picks them up).
            RuntimeError: 3xx without a Location header, or unexpected non-3xx status.
        """
        try:
            with requests.get(
                endpoint_url,
                headers={
                    "Authorization": f"Bearer {token_provider()}",
                    "User-Agent": user_agent(),
                },
                allow_redirects=False,
                timeout=settings().run_timeout,
                proxies={"http": proxy, "https": proxy} if proxy else None,
                verify=ssl_verify,
                stream=True,
            ) as response:
                if response.status_code in _REDIRECT_STATUSES:
                    location = response.headers.get("Location")
                    if not location:
                        msg = (
                            f"Redirect response {response.status_code} from /file endpoint "
                            f"missing Location header for artifact {self.artifact_id}"
                        )
                        raise RuntimeError(msg)
                    return location
                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise NotFoundException(
                        status=HTTPStatus.NOT_FOUND.value,
                        reason=f"Artifact {self.artifact_id} not found in run {self.run_id}",
                    )
                if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    raise ServiceException(status=response.status_code, reason=response.reason)
                if response.status_code >= HTTPStatus.BAD_REQUEST:
                    raise ApiException(status=response.status_code, reason=response.reason)
                msg = (
                    f"Unexpected status {response.status_code} from /file endpoint "
                    f"for artifact {self.artifact_id}; expected a redirect"
                )
                raise RuntimeError(msg)
        except requests.Timeout as e:
            raise ServiceException(
                status=HTTPStatus.SERVICE_UNAVAILABLE.value,
                reason="Request timed out",
            ) from e
        except requests.ConnectionError as e:
            raise ServiceException(
                status=HTTPStatus.SERVICE_UNAVAILABLE.value,
                reason="Connection failed",
            ) from e
        except requests.RequestException as e:
            raise ServiceException(
                status=HTTPStatus.SERVICE_UNAVAILABLE.value,
                reason=f"Request failed: {e}",
            ) from e


class Run(_AuthenticatedResource):
    """Represents a single application run.

    Provides operations to check status, retrieve results, and download artifacts.
    """

    def __init__(self, api: _AuthenticatedApi, run_id: str) -> None:
        """Initializes a Run instance.

        Args:
            api (_AuthenticatedApi): The configured API client.
            run_id (str): The ID of the application run.
        """
        super().__init__(api)
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

    def details(self, nocache: bool = False, hide_platform_queue_position: bool = False) -> RunData:
        """Retrieves the current status of the application run.

        Retries on network and server errors. Additionally retries on
        NotFoundException for up to 5 seconds to handle read replica lag.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.
            hide_platform_queue_position (bool): If True, hides the platform queue position
                in the returned run data. Defaults to False.

        Returns:
            RunData: The run data.

        Raises:
            NotFoundException: If the run is not found after retries.
            Exception: If the API request fails.
        """

        @cached_operation(ttl=settings().run_cache_ttl, token_provider=self._api.token_provider)
        def details_with_retry(run_id: str) -> RunData:
            def _fetch() -> RunData:
                return Retrying(
                    retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                    stop=stop_after_attempt(settings().run_retry_attempts),
                    wait=wait_exponential_jitter(
                        initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max
                    ),
                    before_sleep=_log_retry_attempt,
                    reraise=True,
                )(
                    lambda: self._api.get_run_v1_runs_run_id_get(
                        run_id,
                        _request_timeout=settings().run_timeout,
                        _headers={"User-Agent": user_agent()},
                    )
                )

            # NOTE(nahua): Outer retry handles NotFoundException (read replica lag)
            return Retrying(
                retry=retry_if_exception_type(exception_types=(NotFoundException,)),
                stop=stop_after_delay(5),
                wait=wait_exponential_jitter(initial=0.5, max=3),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(_fetch)

        run_data: RunData = details_with_retry(self.run_id, nocache=nocache)  # type: ignore[call-arg]
        if hide_platform_queue_position:
            run_data = run_data.model_copy(deep=True)
            run_data.num_preceding_items_platform = None
        return run_data

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

    def results(  # noqa: PLR0913
        self,
        nocache: bool = False,
        item_ids: list[str] | None = None,
        external_ids: list[str] | None = None,
        *,
        state: ItemState | None = None,
        termination_reason: ItemTerminationReason | None = None,
        custom_metadata: str | None = None,
    ) -> t.Iterator[ItemResultData]:
        """Retrieves the results of all items in the run.

        Retries on network and server errors.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.
            item_ids (list[str] | None): Optional list of item IDs to filter results by.
            external_ids (list[str] | None): Optional list of external IDs to filter results by.
            state (ItemState | None): Optional filter by item state (server-side).
            termination_reason (ItemTerminationReason | None): Optional filter by termination reason
                (server-side, only applies to TERMINATED items).
            custom_metadata (str | None): Optional JSONPath expression to filter items by their
                custom_metadata (server-side).

        Returns:
            Iterator[ItemResultData]: An iterator over item results.

        Raises:
            Exception: If the API request fails.
        """

        # Create a wrapper function that applies retry logic and caching to each API call
        # Caching at this level ensures having a fresh iterator on cache hits
        @cached_operation(ttl=settings().run_cache_ttl, token_provider=self._api.token_provider)
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

        filter_kwargs: dict[str, object] = {}
        if item_ids:
            filter_kwargs["item_id__in"] = item_ids
        if external_ids:
            filter_kwargs["external_id__in"] = external_ids
        if state is not None:
            filter_kwargs["state"] = state
        if termination_reason is not None:
            filter_kwargs["termination_reason"] = termination_reason
        if custom_metadata is not None:
            filter_kwargs["custom_metadata"] = custom_metadata

        return paginate(lambda **kwargs: results_with_retry(self.run_id, nocache=nocache, **filter_kwargs, **kwargs))

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

            # iteratively check for available results
            application_run_state = self.details(nocache=True).state  # no cache to get fresh results
            while application_run_state in {RunState.PROCESSING, RunState.PENDING}:
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
                        self.ensure_artifacts_downloaded(
                            application_run_dir, item, checksum_attribute_key, print_status=print_status
                        )
                sleep(sleep_interval)
                application_run_state = self.details(nocache=True).state
                print(self) if print_status else None
                if application_run_state in {RunState.PROCESSING, RunState.PENDING}:
                    logger.trace("Waiting for termination of run {}, current state: {!r}.", self.run_id, self)
                else:
                    logger.trace("Run {} has terminated, final state {!r}.", self.run_id, self)

            # check if last results have been downloaded yet and report on errors
            for item in self.results(nocache=True):
                if item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL:
                    self.ensure_artifacts_downloaded(
                        application_run_dir, item, checksum_attribute_key, print_status=print_status
                    )
                message = (
                    f"Output of item `{item.external_id}` is `{item.output}`, state `{item.state}`, "
                    f"error `{item.error_message}` ({item.error_code}), "
                    f"termination reason `{item.termination_reason}`."
                )
                logger.trace(message)
                print(message) if print_status else None

        except (ValueError, DownloadTimeoutError):
            # Re-raise ValueError and DownloadTimeoutError as-is
            raise
        except Exception as e:
            # Wrap all other exceptions in RuntimeError
            msg = f"Download operation failed unexpectedly for run {self.run_id}: {e}"
            raise RuntimeError(msg) from e

    def artifact(self, artifact_id: str) -> Artifact:
        """Get an Artifact handle for resolving a presigned download URL.

        Args:
            artifact_id (str): The output artifact ID
                (``OutputArtifactResultReadResponse.output_artifact_id``).

        Returns:
            Artifact: A handle bound to this run and the given artifact.
        """
        return Artifact(self._api, self.run_id, artifact_id)

    def get_artifact_download_url(self, artifact_id: str) -> str:
        """Resolve a fresh presigned download URL for an artifact of this run.

        Convenience wrapper around :meth:`artifact` and
        :meth:`Artifact.get_download_url`.

        Args:
            artifact_id (str): The output artifact ID.

        Returns:
            str: A short-lived presigned URL.

        Raises:
            NotFoundException: 404.
            ApiException: Other 4xx.
            ServiceException: 5xx or transient network errors.
            RuntimeError: Unexpected response from the /file endpoint.
        """
        return self.artifact(artifact_id).get_download_url()

    def ensure_artifacts_downloaded(
        self,
        base_folder: Path,
        item: ItemResultReadResponse,
        checksum_attribute_key: str = "checksum_base64_crc32c",
        print_status: bool = True,
    ) -> None:
        """Ensures all artifacts for an item are downloaded.

        Downloads missing or partially downloaded artifacts and verifies their integrity.
        Resolves a fresh presigned URL for each artifact via the
        ``/api/v1/runs/{run_id}/artifacts/{artifact_id}/file`` endpoint instead
        of the deprecated ``OutputArtifactResultReadResponse.download_url`` field.

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
            if artifact.output != ArtifactOutput.AVAILABLE:
                continue
            # Metadata check must come BEFORE the MIME lookup: an artifact with
            # empty metadata falls back to application/octet-stream, which
            # mime_type_to_file_ending raises ValueError on — pre-empting the
            # intended skip. (Caught by Copilot review on PR #598.)
            if not artifact.metadata:
                logger.error("Skipping artifact %s for item %s, no metadata present", artifact.name, item.external_id)
                print(
                    f"> Skipping artifact {artifact.name} for item {item.external_id}, no metadata present"
                ) if print_status else None
                continue
            item_dir.mkdir(exist_ok=True, parents=True)
            file_ending = mime_type_to_file_ending(get_mime_type_for_artifact(artifact))
            file_path = item_dir / f"{artifact.name}{file_ending}"
            checksum = artifact.metadata[checksum_attribute_key]

            if file_path.exists():
                file_checksum = calculate_file_crc32c(file_path)
                if file_checksum != checksum:
                    logger.trace("Resume download for {} to {}", artifact.name, file_path)
                    print(f"> Resume download for {artifact.name} to {file_path}") if print_status else None
                else:
                    continue
            else:
                logger.trace("Download for {} to {}", artifact.name, file_path)
                print(f"> Download for {artifact.name} to {file_path}") if print_status else None

            downloaded_at_least_one_artifact = True
            download_file(self.get_artifact_download_url(artifact.output_artifact_id), str(file_path), checksum)

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
        error_status = (
            f" with error `{details.error_message}` ({details.error_code})"
            if details.error_message or details.error_code
            else ""
        )
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
        return (
            f"Run `{self.run_id}` ({details.application_id}:{details.version_number}): "
            f"{app_status}{error_status}, {items}"
        )


class Runs(_AuthenticatedResource):
    """Resource class for managing application runs.

    Provides operations to submit, find, and retrieve runs.
    """

    def __init__(self, api: _AuthenticatedApi) -> None:
        """Initializes the Runs resource with the API client.

        Args:
            api (_AuthenticatedApi): The configured API client.
        """
        super().__init__(api)

    def __call__(self, run_id: str) -> Run:
        """Retrieves a Run instance for an existing run.

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
        scheduling: SchedulingRequest | None = None,
    ) -> Run:
        """Submit a new application run.

        Args:
            application_id (str): The ID of the application.
            items (list[ItemCreationRequest]): The run creation request payload.
            application_version (str|None): The version of the application to use.
                If None, the latest version is used.
            custom_metadata (dict[str, Any] | None): Optional metadata to attach to the run.
            scheduling (SchedulingRequest | None): Optional scheduling constraints for the run.
                Supports 'due_date' (requested completion time, ISO 8601) and
                'deadline' (hard deadline, ISO 8601).

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
            scheduling=scheduling,
        )
        current_settings = settings()
        self._validate_input_items(payload)
        res: RunCreationResponse = self._api.create_run_v1_runs_post(
            payload,
            _request_timeout=current_settings.run_submit_timeout,
            _headers={"User-Agent": user_agent()},
        )
        metrics.count(
            "aignostics.platform.run.submitted",
            1,
            attributes={
                "api_root": current_settings.api_root,
                "application_id": application_id,
                "application_version": application_version or "latest",
            },
        )
        metrics.count(
            "aignostics.platform.items.submitted",
            len(items),
            attributes={
                "api_root": current_settings.api_root,
                "application_id": application_id,
                "application_version": application_version or "latest",
            },
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
        for_organization: str | None = None,
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
            for_organization (str | None): If set, returns all runs triggered by users of the specified organization
                that match the filter criteria. If None, only the runs of the user are returned.

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
                for_organization=for_organization,
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
        for_organization: str | None = None,
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
            for_organization (str | None): If set, returns all runs triggered by users of the specified organization
                that match the filter criteria. If None, only the runs of the user are returned.

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

        @cached_operation(ttl=settings().run_cache_ttl, token_provider=self._api.token_provider)
        def list_data_with_retry(**kwargs: object) -> builtins.list[RunData]:
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
                for_organization=for_organization,
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

        Optimized for large item counts: builds SDK metadata once and reuses it for items
        without existing SDK metadata. Items with custom SDK metadata are processed individually.

        Args:
            items (builtins.list[ItemCreationRequest]): The list of item creation requests to amend.
        """
        if not items:
            return

        base_sdk_metadata: dict[str, Any] | None = None

        for item in items:
            item_custom_metadata = item.custom_metadata or {}
            existing_item_sdk_metadata = item_custom_metadata.get("sdk")

            if existing_item_sdk_metadata:
                item_sdk_metadata = build_item_sdk_metadata(existing_item_sdk_metadata)
                validate_item_sdk_metadata(item_sdk_metadata)
                item_custom_metadata["sdk"] = item_sdk_metadata
            else:
                if base_sdk_metadata is None:
                    base_sdk_metadata = build_item_sdk_metadata({})  # Cache base SDK metadata
                    validate_item_sdk_metadata(base_sdk_metadata)
                item_custom_metadata["sdk"] = base_sdk_metadata

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
