"""Scheduled integration tests for the Aignostics client.

This module contains integration tests that run real application workflows
against the Aignostics platform. These tests verify end-to-end functionality
including creating runs, downloading results, and validating outputs.
"""

import tempfile
from pathlib import Path

import pytest
from aignx.codegen.models import (
    ApplicationRunStatus,
    ApplicationVersion,
    InputArtifactCreationRequest,
    ItemCreationRequest,
    ItemStatus,
    RunCreationRequest,
)

import aignostics.client
from aignostics.client._utils import calculate_file_crc32c, generate_signed_url, mime_type_to_file_ending


def three_spots_payload() -> list[ItemCreationRequest]:
    """Generates a payload for the two task dummy application using three spots."""
    return [
        ItemCreationRequest(
            reference="1",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "N+LWCg==",
                        "base_mpp": 0.46499982,
                        "width": 3728,
                        "height": 3640,
                    },
                )
            ],
        ),
        ItemCreationRequest(
            reference="2",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "w+ud3g==",
                        "base_mpp": 0.46499982,
                        "width": 3616,
                        "height": 3400,
                    },
                )
            ],
        ),
        ItemCreationRequest(
            reference="3",
            input_artifacts=[
                InputArtifactCreationRequest(
                    name="user_slide",
                    download_url=generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "Zmx0wA==",
                        "base_mpp": 0.46499982,
                        "width": 4016,
                        "height": 3952,
                    },
                )
            ],
        ),
    ]


@pytest.mark.timeout(240)
@pytest.mark.scheduled
def test_two_task_dummy_app() -> None:
    """Test the two-task dummy application.

    This test creates an application run using a predefined application version and input samples.
    It then downloads the results to a temporary directory and performs various checks to ensure
    the application run completed successfully and the results are valid.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    application_version = "60e7b441-307a-4b41-8a97-5b02e7bc73a4"
    platform = aignostics.client.Client(cache_token=False)
    application_run = platform.runs.create(
        RunCreationRequest(application_version=ApplicationVersion(application_version), items=three_spots_payload())
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        application_run.download_to_folder(temp_dir)

        assert application_run.status().status == ApplicationRunStatus.COMPLETED, (
            "Application run did not finish in completed status"
        )

        run_result_folder = temp_path / application_run.application_run_id
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
                file_checksum = calculate_file_crc32c(file_path)
                assert file_checksum == checksum, f"Metadata checksum != file checksum {checksum} <> {file_checksum}"
