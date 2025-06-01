"""Runs resource module for the Aignostics client.

This module provides classes for creating and managing application runs on the Aignostics platform.
It includes functionality for starting runs, monitoring status, and downloading results.
"""

import typing as t
from collections.abc import Generator
from pathlib import Path
from time import sleep
from typing import Any

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import (
    ApplicationRunStatus,
    ItemCreationRequest,
    ItemResultReadResponse,
    ItemStatus,
    RunCreationRequest,
    RunCreationResponse,
)
from aignx.codegen.models import (
    ItemResultReadResponse as ItemResultData,
)
from aignx.codegen.models import (
    RunReadResponse as ApplicationRunData,
)
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from aignostics.platform._utils import calculate_file_crc32c, download_file, mime_type_to_file_ending
from aignostics.platform.resources.applications import Versions
from aignostics.platform.resources.utils import paginate

LIST_APPLICATION_RUNS_MAX_PAGE_SIZE = 100
LIST_APPLICATION_RUNS_MIN_PAGE_SIZE = 5


class ApplicationRun:
    """Represents a single application run.

    Provides operations to check status, retrieve results, and download artifacts.
    """

    def __init__(self, api: PublicApi, application_run_id: str) -> None:
        """Initializes an ApplicationRun instance.

        Args:
            api (PublicApi): The configured API client.
            application_run_id (str): The ID of the application run.
        """
        self._api = api
        self.application_run_id = application_run_id

    @classmethod
    def for_application_run_id(cls, application_run_id: str) -> "ApplicationRun":
        """Creates an ApplicationRun instance for an existing run.

        Args:
            application_run_id (str): The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        from aignostics.platform._client import Client  # noqa: PLC0415

        return cls(Client.get_api_client(cache_token=False), application_run_id)

    # TODO(Andreas): Deprecated, please remove when you updated your integration code
    def status(self) -> ApplicationRunData:
        """Retrieves the current status of the application run.

        Returns:
            ApplicationRunData: The run data.

        Raises:
            Exception: If the API request fails.
        """
        return self.details()

    def details(self) -> ApplicationRunData:
        """Retrieves the current status of the application run.

        Returns:
            ApplicationRunData: The run data.

        Raises:
            Exception: If the API request fails.
        """
        return self._api.get_run_v1_runs_application_run_id_get(self.application_run_id, include=None)

    def item_status(self) -> dict[str, ItemStatus]:
        """Retrieves the status of all items in the run.

        Returns:
            dict[str, ItemStatus]: A dictionary mapping item references to their status.

        Raises:
            Exception: If the API request fails.
        """
        return {item.reference: item.status for item in self.results()}

    # TODO(Andreas): Fails with Internal Server Error if run canceled; don't throw generic exceptions
    def cancel(self) -> None:
        """Cancels the application run.

        Raises:
            Exception: If the API request fails.
        """
        self._api.cancel_application_run_v1_runs_application_run_id_cancel_post(self.application_run_id)

    def results(self) -> t.Iterator[ItemResultData]:
        """Retrieves the results of all items in the run.

        Returns:
            list[ItemResultData]: A list of item results.

        Raises:
            Exception: If the API request fails.
        """
        return paginate(
            self._api.list_run_results_v1_runs_application_run_id_results_get,
            application_run_id=self.application_run_id,
        )

    def download_to_folder(self, download_base: Path | str) -> None:
        """Downloads all result artifacts to a folder.

        Monitors run progress and downloads results as they become available.

        Args:
            download_base (Path | str): Base directory to download results to.

        Raises:
            ValueError: If the provided path is not a directory.
            Exception: If downloads or API requests fail.
        """
        # create application run base folder
        download_base = Path(download_base)
        if not download_base.is_dir():
            msg = f"{download_base} is not a directory"
            raise ValueError(msg)
        application_run_dir = Path(download_base) / self.application_run_id

        # incrementally check for available results
        application_run_status = self.details().status
        while application_run_status == ApplicationRunStatus.RUNNING:
            for item in self.results():
                if item.status == ItemStatus.SUCCEEDED:
                    self.ensure_artifacts_downloaded(application_run_dir, item)
            sleep(5)
            application_run_status = self.details().status
            print(self)

        # check if last results have been downloaded yet and report on errors
        for item in self.results():
            match item.status:
                case ItemStatus.SUCCEEDED:
                    self.ensure_artifacts_downloaded(application_run_dir, item)
                case ItemStatus.ERROR_SYSTEM | ItemStatus.ERROR_USER:
                    print(f"{item.reference} failed with {item.status.value}: {item.error}")

    @staticmethod
    def ensure_artifacts_downloaded(base_folder: Path, item: ItemResultReadResponse) -> None:
        """Ensures all artifacts for an item are downloaded.

        Downloads missing or partially downloaded artifacts and verifies their integrity.

        Args:
            base_folder (Path): Base directory to download artifacts to.
            item (ItemResultReadResponse): The item result containing the artifacts to download.

        Raises:
            ValueError: If checksums don't match.
            Exception: If downloads fail.
        """
        item_dir = base_folder / item.reference

        downloaded_at_least_one_artifact = False
        for artifact in item.output_artifacts:
            if artifact.download_url:
                item_dir.mkdir(exist_ok=True, parents=True)
                file_ending = mime_type_to_file_ending(artifact.mime_type)
                file_path = item_dir / f"{artifact.name}{file_ending}"
                checksum = artifact.metadata["checksum_crc32c"]

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
            print(f"Downloaded results for item: {item.reference} to {item_dir}")
        else:
            print(f"Results for item: {item.reference} already present in {item_dir}")

    def __str__(self) -> str:
        """Returns a string representation of the application run.

        The string includes run ID, status, and item statistics.

        Returns:
            str: String representation of the application run.
        """
        app_status = self.details().status.value
        item_status = self.item_status()
        pending, succeeded, error = 0, 0, 0
        for item in item_status.values():
            match item:
                case ItemStatus.PENDING:
                    pending += 1
                case ItemStatus.SUCCEEDED:
                    succeeded += 1
                case ItemStatus.ERROR_USER | ItemStatus.ERROR_SYSTEM:
                    error += 1

        items = f"{len(item_status)} items - ({pending}/{succeeded}/{error}) [pending/succeeded/error]"
        return f"Application run `{self.application_run_id}`: {app_status}, {items}"


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

    def __call__(self, application_run_id: str) -> ApplicationRun:
        """Retrieves an ApplicationRun instance for an existing run.

        Args:
            application_run_id (str): The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        return ApplicationRun(self._api, application_run_id)

    def create(self, application_version: str, items: list[ItemCreationRequest]) -> ApplicationRun:
        """Creates a new application run.

        Args:
            application_version (ApplicationVersion | str): The ID of the application version.
            items (list[ItemCreationRequest]): The run creation request payload.

        Returns:
            ApplicationRun: The created application run.

        Raises:
            ValueError: If the payload is invalid.
            Exception: If the API request fails.
        """
        payload = RunCreationRequest(
            application_version_id=application_version,
            items=items,
        )
        self._validate_input_items(payload)
        res: RunCreationResponse = self._api.create_application_run_v1_runs_post(payload)
        return ApplicationRun(self._api, str(res.application_run_id))

    def list(self, for_application_version: str | None = None) -> Generator[ApplicationRun, Any, None]:
        """Find application runs, optionally filtered by application version.

        Args:
            for_application_version (str | None): Optional application version ID to filter by.

        Returns:
            Generator[ApplicationRun, Any, None]: A generator yielding application runs.

        Raises:
            Exception: If the API request fails.
        """
        if not for_application_version:
            res = paginate(self._api.list_application_runs_v1_runs_get)
        else:
            res = paginate(self._api.list_application_runs_v1_runs_get, application_version_id=for_application_version)
        return (ApplicationRun(self._api, response.application_run_id) for response in res)

    # TODO(Andreas): Think about merging by having list(...) above return active records that as well hold data
    def list_data(
        self,
        for_application_version: str | None = None,
        sort: str | None = None,
        page_size: int = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    ) -> t.Iterator[ApplicationRunData]:
        """Fetch application runs, optionally filtered by application version.

        Args:
            for_application_version (str | None): Optional application version ID to filter by.
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
        if not for_application_version:
            res = paginate(
                self._api.list_application_runs_v1_runs_get,
                page_size=page_size,
                sort=[sort] if sort else None,
            )
        else:
            res = paginate(
                self._api.list_application_runs_v1_runs_get,
                page_size=page_size,
                application_version_id=for_application_version,
                sort=[sort] if sort else None,
            )
        return res

    def _validate_input_items(self, payload: RunCreationRequest) -> None:
        """Validates the input items in a run creation request.

        Checks that references are unique, all required artifacts are provided,
        and artifact metadata matches the expected schema.

        Args:
            payload (RunCreationRequest): The run creation request payload.

        Raises:
            ValueError: If validation fails.
            Exception: If the API request fails.
        """
        # validate metadata based on schema of application version
        app_version = Versions(self._api).details(application_version=payload.application_version_id)
        schema_idx = {
            input_artifact.name: input_artifact.metadata_schema for input_artifact in app_version.input_artifacts
        }
        references = set()
        for item in payload.items:
            # verify references are unique
            if item.reference in references:
                msg = f"Duplicate reference `{item.reference}` in items."
                raise ValueError(msg)
            references.add(item.reference)

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
