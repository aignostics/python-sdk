import json
from pathlib import Path
from time import sleep

from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.models import (
    ApplicationRunStatus,
    ItemResultReadResponse,
    ItemStatus,
    RunCreationRequest,
    RunCreationResponse,
    RunReadResponse,
)
from jsf import JSF
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from aignostics.client.resources.applications import Versions
from aignostics.client.utils import _calculate_file_crc32c, _download_file, mime_type_to_file_ending


class ApplicationRun:
    """Represents a single application run.

    Provides operations to check status, retrieve results, and download artifacts.
    """

    def __init__(self, api: ExternalsApi, application_run_id: str):
        """Initializes an ApplicationRun instance.

        Args:
            api: The configured API client.
            application_run_id: The ID of the application run.
        """
        self._api = api
        self.application_run_id = application_run_id

    @classmethod
    def for_application_run_id(cls, application_run_id: str) -> "ApplicationRun":
        """Creates an ApplicationRun instance for an existing run.

        Args:
            application_run_id: The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        from aignostics.client import Client

        return cls(Client._get_api_client(), application_run_id)

    def status(self) -> RunReadResponse:
        """Retrieves the current status of the application run.

        Returns:
            RunReadResponse: The run status details.

        Raises:
            Exception: If the API request fails.
        """
        res = self._api.get_run_v1_runs_application_run_id_get(self.application_run_id, include=None)
        return res

    def item_status(self) -> dict[str, ItemStatus]:
        """Retrieves the status of all items in the run.

        Returns:
            dict[str, ItemStatus]: A dictionary mapping item references to their status.

        Raises:
            Exception: If the API request fails.
        """
        results = self.results()
        item_status = {}
        for item in results:
            item_status[item.reference] = item.status
        return item_status

    def cancel(self):
        """Cancels the application run.

        Raises:
            Exception: If the API request fails.
        """
        res = self._api.cancel_run_v1_runs_application_run_id_cancel_post(self.application_run_id)

    def results(self) -> list[ItemResultReadResponse]:
        """Retrieves the results of all items in the run.

        Returns:
            list[ItemResultReadResponse]: A list of item results.

        Raises:
            Exception: If the API request fails.
        """
        # TODO(andreas): paging, sorting
        res = self._api.list_run_results_v1_runs_application_run_id_results_get(self.application_run_id)
        return res

    def download_to_folder(self, download_base: Path | str):
        """Downloads all result artifacts to a folder.

        Monitors run progress and downloads results as they become available.

        Args:
            download_base: Base directory to download results to.

        Raises:
            ValueError: If the provided path is not a directory.
            Exception: If downloads or API requests fail.
        """
        # create application run base folder
        download_base = Path(download_base)
        if not download_base.is_dir():
            raise ValueError(f"{download_base} is not a directory")
        application_run_dir = Path(download_base) / self.application_run_id

        # incrementally check for available results
        application_run_status = self.status().status
        while application_run_status == ApplicationRunStatus.RUNNING:
            for item in self.results():
                if item.status == ItemStatus.SUCCEEDED:
                    self.ensure_artifacts_downloaded(application_run_dir, item)
            sleep(5)
            application_run_status = self.status().status
            print(self)

        # check if last results have been downloaded yet and report on errors
        for item in self.results():
            match item.status:
                case ItemStatus.SUCCEEDED:
                    self.ensure_artifacts_downloaded(application_run_dir, item)
                case ItemStatus.ERROR_SYSTEM | ItemStatus.ERROR_USER:
                    print(f"{item.reference} failed with {item.status.value}: {item.error}")

    @staticmethod
    def ensure_artifacts_downloaded(base_folder: Path, item: ItemResultReadResponse):
        """Ensures all artifacts for an item are downloaded.

        Downloads missing or partially downloaded artifacts and verifies their integrity.

        Args:
            base_folder: Base directory to download artifacts to.
            item: The item result containing the artifacts to download.

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
                    file_checksum = _calculate_file_crc32c(file_path)
                    if file_checksum != checksum:
                        print(f"> Resume download for {artifact.name} to {file_path}")
                    else:
                        continue
                else:
                    downloaded_at_least_one_artifact = True
                    print(f"> Download for {artifact.name} to {file_path}")

                # if file is not there at all or only partially downloaded yet
                _download_file(artifact.download_url, file_path, checksum)

        if downloaded_at_least_one_artifact:
            print(f"Downloaded results for item: {item.reference} to {item_dir}")
        else:
            print(f"Results for item: {item.reference} already present in {item_dir}")

    def __str__(self):
        """Returns a string representation of the application run.

        The string includes run ID, status, and item statistics.

        Returns:
            str: String representation of the application run.
        """
        app_status = self.status().status.value
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

    Provides operations to create, list, and retrieve runs.
    """

    def __init__(self, api: ExternalsApi):
        """Initializes the Runs resource with the API client.

        Args:
            api: The configured API client.
        """
        self._api = api

    def __call__(self, application_run_id: str) -> ApplicationRun:
        """Retrieves an ApplicationRun instance for an existing run.

        Args:
            application_run_id: The ID of the application run.

        Returns:
            ApplicationRun: The initialized ApplicationRun instance.
        """
        return ApplicationRun(self._api, application_run_id)

    def create(self, payload: RunCreationRequest) -> ApplicationRun:
        """Creates a new application run.

        Args:
            payload: The run creation request payload.

        Returns:
            ApplicationRun: The created application run.

        Raises:
            ValueError: If the payload is invalid.
            Exception: If the API request fails.
        """
        self._validate_input_items(payload)
        res: RunCreationResponse = self._api.create_application_run_v1_runs_post(payload)
        return ApplicationRun(self._api, res.application_run_id)

    def generate_example_payload(self, application_version_id: str):
        """Generates an example payload for creating a run.

        Args:
            application_version_id: The ID of the application version.

        Raises:
            Exception: If the API request fails.
        """
        app_version = Versions(self._api).details(for_application_version_id=application_version_id)
        schema_idx = {
            input_artifact.name: input_artifact.metadata_schema for input_artifact in app_version.input_artifacts
        }
        schema = RunCreationRequest.model_json_schema()
        faker = JSF(schema)
        example = faker.generate()
        print(json.dumps(example, indent=2))
        # schema = ItemCreationRequest.model_json_schema()
        # example = jsonschema_default.create_from(schema)
        # print(json.dumps(example, indent=2))
        #
        # schema = InputArtifactCreationRequest.model_json_schema()
        # example = jsonschema_default.create_from(schema)
        # print(json.dumps(example, indent=2))
        #
        # for artifact, schema in schema_idx.items():
        #     s = jsonschema_default.create_from(schema)
        #     print(f"{artifact}:\n{json.dumps(s)}")
        # validate(artifact.metadata, schema=schema_idx[artifact.name])

    def list(self, for_application_version: str = None) -> list[ApplicationRun]:
        """Lists application runs, optionally filtered by application version.

        Args:
            for_application_version: Optional application version ID to filter by.

        Returns:
            list[ApplicationRun]: A list of application runs.

        Raises:
            Exception: If the API request fails.
        """
        # TODO(andreas): pagination
        if not for_application_version:
            res = self._api.list_application_runs_v1_runs_get()
        else:
            res = self._api.list_application_runs_v1_runs_get_with_http_info(for_application_version)
        return [ApplicationRun(self._api, response.application_run_id) for response in res]

    def _validate_input_items(self, payload: RunCreationRequest):
        """Validates the input items in a run creation request.

        Checks that references are unique, all required artifacts are provided,
        and artifact metadata matches the expected schema.

        Args:
            payload: The run creation request payload.

        Raises:
            ValueError: If validation fails.
            Exception: If the API request fails.
        """
        # validate metadata based on schema of application version
        app_version = Versions(self._api).details(
            for_application_version_id=payload.application_version.actual_instance
        )
        schema_idx = {
            input_artifact.name: input_artifact.metadata_schema for input_artifact in app_version.input_artifacts
        }
        references = set()
        for item in payload.items:
            # verify references are unique
            if item.reference in references:
                raise ValueError(f"Duplicate reference `{item.reference}` in items.")
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
                    raise ValueError(f"Invalid metadata for artifact `{artifact.name}`: {e.message}")
            # all artifacts set?
            if len(schema_check) > 0:
                raise ValueError(f"Missing artifact(s): {schema_check}")
