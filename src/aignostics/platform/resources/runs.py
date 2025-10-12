"""Runs resource module for the Aignostics client.

This module provides classes for creating and managing application runs on the Aignostics platform.
It includes functionality for starting runs, monitoring status, and downloading results.
"""
import json
import typing as t
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Any

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import (
    ItemCreationRequest,
    ItemResultReadResponse,
    RunCreationRequest,
    RunCreationResponse,
)
from aignx.codegen.models import ItemOutput
from aignx.codegen.models import (
    ItemResultReadResponse as ItemResultData,
)
from aignx.codegen.models import ItemState
from aignx.codegen.models import ItemTerminationReason
from aignx.codegen.models import (
    RunReadResponse as ApplicationRunData,
)
from aignx.codegen.models import RunState
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from aignostics.platform._utils import (
    calculate_file_crc32c,
    download_file,
    get_mime_type_for_artifact,
    mime_type_to_file_ending,
)
from aignostics.platform.resources.applications import Versions
from aignostics.platform.resources.utils import paginate
from aignostics.utils import user_agent
from aignx.codegen.models import RunTerminationReason

LIST_APPLICATION_RUNS_MAX_PAGE_SIZE = 100
LIST_APPLICATION_RUNS_MIN_PAGE_SIZE = 5

# todo(andreas): As soon as we switch to the new status types of the API,
# this class is obsolete
class ItemStatus(str, Enum):
    PENDING = 'PENDING'
    CANCELED_USER = 'CANCELED_USER'
    CANCELED_SYSTEM = 'CANCELED_SYSTEM'
    USER_ERROR = 'USER_ERROR'
    SYSTEM_ERROR = 'SYSTEM_ERROR'
    SUCCEEDED = 'SUCCEEDED'

    @classmethod
    def from_json(cls, json_str: str) -> t.Self:
        """Create an instance of ItemStatus from a JSON string"""
        return cls(json.loads(json_str))


class ApplicationRun:
    """Represents a single application run.

    Provides operations to check status, retrieve results, and download artifacts.
    """

    def __init__(self, api: PublicApi, run_id: str) -> None:
        """Initializes an ApplicationRun instance.

        Args:
            api (PublicApi): The configured API client.
            run_id (str): The ID of the application run.
        """
        self._api = api
        self.run_id = run_id

    @classmethod
    def for_run_id(cls, run_id: str) -> "ApplicationRun":
        """Creates an ApplicationRun instance for an existing run.

        Args:
            run_id (str): The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        from aignostics.platform._client import Client  # noqa: PLC0415

        return cls(Client.get_api_client(cache_token=False), run_id)

    def details(self) -> ApplicationRunData:
        """Retrieves the current status of the application run.

        Returns:
            ApplicationRunData: The run data.

        Raises:
            Exception: If the API request fails.
        """
        return self._api.get_run_v1_runs_run_id_get(self.run_id)

    def item_status(self) -> dict[str, ItemStatus]:
        """Retrieves the status of all items in the run.

        Returns:
            dict[str, ItemStatus]: A dictionary mapping item external IDs to their status.

        Raises:
            Exception: If the API request fails.
        """
        #     PENDING = 'PENDING'
        #     CANCELED_USER = 'CANCELED_USER'
        #     CANCELED_SYSTEM = 'CANCELED_SYSTEM'
        #     USER_ERROR = 'USER_ERROR'
        #     SYSTEM_ERROR = 'SYSTEM_ERROR'
        #     SUCCEEDED = 'SUCCEEDED'
        item_status = {}
        for item in self.results():
            match item.state:
                case ItemState.PENDING | ItemState.PROCESSING:
                    item_status[item.external_id] = ItemStatus.PENDING
                case ItemState.TERMINATED:
                    match item.termination_reason:
                        case ItemTerminationReason.SUCCEEDED:
                            item_status[item.external_id] = ItemStatus.SUCCEEDED
                        case ItemTerminationReason.SYSTEM_ERROR:
                            item_status[item.external_id] = ItemStatus.SYSTEM_ERROR
                        case ItemTerminationReason.USER_ERROR:
                            item_status[item.external_id] = ItemStatus.USER_ERROR
                        case ItemTerminationReason.SKIPPED:
                            run_termination_reason = self.details().termination_reason
                            if run_termination_reason == RunTerminationReason.CANCELED_BY_SYSTEM:
                                item_status[item.external_id] = ItemStatus.CANCELED_SYSTEM
                            if run_termination_reason == RunTerminationReason.CANCELED_BY_USER:
                                item_status[item.external_id] = ItemStatus.CANCELED_USER
        return item_status

    # TODO(Andreas): Low Prio / existed prior to API migraiton: Please check if this still fails with
    #  Internal Server Error if run was already canceled, should rather fail with 400 bad request in that state.
    def cancel(self) -> None:
        """Cancels the application run.

        Raises:
            Exception: If the API request fails.
        """
        self._api.cancel_run_v1_runs_run_id_cancel_post(self.run_id)

    def delete(self) -> None:
        """Delete the application run.

        Raises:
            Exception: If the API request fails.
        """
        self._api.delete_run_items_v1_runs_run_id_artifacts_delete(self.run_id)

    def results(self) -> t.Iterator[ItemResultData]:
        """Retrieves the results of all items in the run.

        Returns:
            list[ItemResultData]: A list of item results.

        Raises:
            Exception: If the API request fails.
        """
        return paginate(
            self._api.list_run_items_v1_runs_run_id_items_get,
            run_id=self.run_id,
        )

    def download_to_folder(
        self, download_base: Path | str, checksum_attribute_key: str = "checksum_base64_crc32c"
    ) -> None:
        """Downloads all result artifacts to a folder.

        Monitors run progress and downloads results as they become available.

        Args:
            download_base (Path | str): Base directory to download results to.
            checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.

        Raises:
            ValueError: If the provided path is not a directory.
            Exception: If downloads or API requests fail.
        """
        # create application run base folder
        download_base = Path(download_base)
        if not download_base.is_dir():
            msg = f"{download_base} is not a directory"
            raise ValueError(msg)
        application_run_dir = Path(download_base) / self.run_id

        # incrementally check for available results
        application_run_state = self.details().state
        while application_run_state in {RunState.PROCESSING, RunState.PENDING}:
            for item in self.results():
                if item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL:
                    self.ensure_artifacts_downloaded(application_run_dir, item, checksum_attribute_key)
            sleep(5)
            application_run_state = self.details().state
            print(self)

        # check if last results have been downloaded yet and report on errors
        for item in self.results():
            match item.output:
                case ItemOutput.FULL:
                    self.ensure_artifacts_downloaded(application_run_dir, item, checksum_attribute_key)
                case ItemOutput.NONE:
                    print(f"{item.external_id} failed with {item.state.value}: {item.error_message}")

    @staticmethod
    def ensure_artifacts_downloaded(
        base_folder: Path, item: ItemResultReadResponse, checksum_attribute_key: str = "checksum_base64_crc32c"
    ) -> None:
        """Ensures all artifacts for an item are downloaded.

        Downloads missing or partially downloaded artifacts and verifies their integrity.

        Args:
            base_folder (Path): Base directory to download artifacts to.
            item (ItemResultReadResponse): The item result containing the artifacts to download.
            checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.

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
                checksum = artifact.metadata[checksum_attribute_key]

                if file_path.exists():
                    file_checksum = calculate_file_crc32c(file_path)
                    if file_checksum != checksum:
                        print(f"> Resume download for {artifact.name} to {file_path}")
                    else:
                        continue
                else:
                    downloaded_at_least_one_artifact = True
                    print(f"> Download for {artifact.name} to {file_path}")

                # if file is not there at all or only partially downloaded yet
                download_file(artifact.download_url, str(file_path), checksum)

        if downloaded_at_least_one_artifact:
            print(f"Downloaded results for item: {item.external_id} to {item_dir}")
        else:
            print(f"Results for item: {item.external_id} already present in {item_dir}")

    def __str__(self) -> str:
        """Returns a string representation of the application run.

        The string includes run ID, status, and item statistics.

        Returns:
            str: String representation of the application run.
        """
        details = self.details()
        app_status = details.state.value
        items = (
            f"{details.statistics.item_count} items - "
            f"({details.statistics.item_pending_count}/{details.statistics.item_succeeded_count}/"
            f"{details.statistics.item_system_error_count + details.statistics.item_user_error_count}) "
            f"[pending/succeeded/error]"
        )
        return f"Application run `{self.run_id}`: {app_status}, {items}"


class Runs:
    """Resource class for managing application runs.

    Provides operations to create, find, and retrieve runs.
    """

    def __init__(self, api: PublicApi) -> None:
        """Initializes the Runs resource with the API client.

        Args:
            api (PublicApi): The configured API client.
        """
        self._api = api

    def __call__(self, run_id: str) -> ApplicationRun:
        """Retrieves an ApplicationRun instance for an existing run.

        Args:
            run_id (str): The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        return ApplicationRun(self._api, run_id)

    def create(
        self,
        application_id: str,
        items: list[ItemCreationRequest],
        application_version: str | None = None,
        custom_metadata: dict[str, Any] | None = None,
    ) -> ApplicationRun:
        """Creates a new application run.

        Args:
            application_id (str): The ID of the application.
            items (list[ItemCreationRequest]): The run creation request payload.
            application_version (str|None): The version of the application to use.
                If None, the latest version is used.
            custom_metadata (dict[str, Any] | None): Optional metadata to attach to the run.

        Returns:
            ApplicationRun: The created application run.

        Raises:
            ValueError: If the payload is invalid.
            Exception: If the API request fails.
        """
        custom_metadata = custom_metadata or {}
        custom_metadata.setdefault("sdk", {})
        custom_metadata["sdk"]["user_agent"] = user_agent()
        payload = RunCreationRequest(
            application_id=application_id,
            version_number=application_version,
            custom_metadata=custom_metadata,
            items=items,
        )
        self._validate_input_items(payload)
        res: RunCreationResponse = self._api.create_run_v1_runs_post(payload)
        return ApplicationRun(self._api, str(res.run_id))

    def list(
        self, application_id: str | None = None, application_version: str | None = None
    ) -> Generator[ApplicationRun, Any, None]:
        """Find application runs, optionally filtered by application id and/or version.

        Args:
            application_id (str | None): Optional application ID to filter by.
            application_version (str | None): Optional application version to filter by.

        Returns:
            Generator[ApplicationRun, Any, None]: A generator yielding application runs.

        Raises:
            Exception: If the API request fails.
        """
        res = paginate(
            self._api.list_runs_v1_runs_get,
            application_id=application_id,
            application_version=application_version,
        )
        return (ApplicationRun(self._api, response.run_id) for response in res)

    def list_data(
        self,
        application_id: str | None = None,
        application_version: str | None = None,
        custom_metadata: str | None = None,
        sort: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    ) -> t.Iterator[ApplicationRunData]:
        """Fetch application runs, optionally filtered by application version.

        Args:
            application_id (str | None): Optional application ID to filter by.
            application_version (str | None): Optional application version ID to filter by.
            custom_metadata (str | None): Optional metadata filter in JSONPath format.
            sort (str | None): Optional field to sort by. Prefix with '-' for descending order.
            page_size (int): Number of items per page, defaults to max

        Returns:
            Iterator[ApplicationRunData]: Iterator yielding application run data.

        Raises:
            ValueError: If page_size is greater than 100.
            Exception: If the API request fails.
        """
        if page_size > LIST_APPLICATION_RUNS_MAX_PAGE_SIZE:
            message = (
                f"page_size is must be less than or equal to {LIST_APPLICATION_RUNS_MAX_PAGE_SIZE}, but got {page_size}"
            )
            raise ValueError(message)
        return paginate(
            self._api.list_runs_v1_runs_get,
            page_size=page_size,
            application_id=application_id,
            application_version=application_version,
            custom_metadata=custom_metadata,
            sort=[sort] if sort else None,
        )

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
        app_version = Versions(self._api).details(
            application_id=payload.application_id, application_version=payload.version_number
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
