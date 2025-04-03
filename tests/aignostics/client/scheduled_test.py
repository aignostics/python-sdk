import tempfile
from pathlib import Path

import pytest

import aignostics.client
from aignostics.client.samples import input_samples
from aignostics.client.utils import _calculate_file_crc32c, mime_type_to_file_ending
from aignx.codegen.models import ApplicationRunStatus, ApplicationVersion, ItemStatus, RunCreationRequest


@pytest.mark.timeout(240)
@pytest.mark.scheduled
def test_two_task_dummy_app():
    application_version = "60e7b441-307a-4b41-8a97-5b02e7bc73a4"
    print(f"Create application run for application version: {application_version}")
    platform = aignostics.client.Client(cache_token=False)
    application_run = platform.runs.create(
        RunCreationRequest(
            application_version=ApplicationVersion(application_version),
            items=input_samples.three_spots_payload()
        )
    )

    with tempfile.TemporaryDirectory() as dir:
        dir = Path(dir)
        application_run.download_to_folder(dir)

        assert application_run.status().status == ApplicationRunStatus.COMPLETED, "Application run did not finish in completed status"

        run_result_folder = dir / application_run.application_run_id
        assert run_result_folder.exists(), "Application run result folder does not exist"

        run_results = application_run.results()

        for item in run_results:
            # validate status
            assert item.status == ItemStatus.SUCCEEDED
            # validate results
            item_dir = run_result_folder / item.reference
            assert item_dir.exists(), f"Result folder for item {item.reference} does not exist"

            for artifact in item.output_artifacts:
                assert artifact.download_url is not None, f"{artifact} should provide an download url"
                # check if file exists
                file_ending = mime_type_to_file_ending(artifact.mime_type)
                file_path = item_dir / f"{artifact.name}{file_ending}"
                assert file_path.exists(), f"Artifact {artifact} was not downloaded"
                # validate checksum
                checksum = artifact.metadata["checksum_crc32c"]
                file_checksum = _calculate_file_crc32c(file_path)
                assert file_checksum == checksum, f"Metadata checksum != file checksum {checksum} <> {file_checksum}"
