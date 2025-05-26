"""Scheduled integration tests for the Aignostics client.

This module contains integration tests that run real application workflows
against the Aignostics platform. These tests verify end-to-end functionality
including creating runs, downloading results, and validating outputs.
"""

import tempfile
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from aignx.codegen.models import ApplicationRunStatus, ItemStatus

from aignostics import platform
from aignostics.platform.resources.runs import ApplicationRun

TEST_APPLICATION_VERSION_ID = "two-task-dummy:v0.35.0"
HETA_APPLICATION_VERSION_ID = "he-tme:v0.51.0"


def single_spot_payload_heta_0_51_0() -> list[platform.InputItem]:
    """Generates a payload using a single spot."""
    return [
        platform.InputItem(
            reference="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://platform-api-application-test-data/heta/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff"
                    ),
                    metadata={
                        "checksum_base64_crc32c": "5onqtA==",
                        "resolution_mpp": 0.26268186053789266,
                        "width_px": 7447,
                        "height_px": 7196,
                        "media_type": "image/tiff",
                        "staining_method": "H&E",
                        "tissue": "LUNG",
                        "disease": "LUNG_CANCER",
                    },
                )
            ],
        ),
    ]


def three_spots_payload_for_dummy_0_35_0() -> list[platform.InputItem]:
    """Generates a payload using three spots."""
    return [
        platform.InputItem(
            reference="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
                    ),
                    metadata={
                        "checksum_crc32c": "9l3NNQ==",
                        "base_mpp": 0.46499982,
                        "width": 3728,
                        "height": 3640,
                    },
                )
            ],
        ),
        platform.InputItem(
            reference="2",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
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
        platform.InputItem(
            reference="3",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
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


@pytest.mark.scheduled
@pytest.mark.long_running
@pytest.mark.parametrize(
    ("timeout", "application_version_id", "payload"),
    [
        (240, TEST_APPLICATION_VERSION_ID, three_spots_payload_for_dummy_0_35_0()),
        (3600, HETA_APPLICATION_VERSION_ID, single_spot_payload_heta_0_51_0()),
    ],
)
def test_application_runs(
    timeout: int, application_version_id: str, payload: list[platform.InputItem], request: FixtureRequest
) -> None:
    """Test application runs.

    This test creates an application run using a predefined application version and input samples.
    It then downloads the results to a temporary directory and performs various checks to ensure
    the application run completed successfully and the results are valid.

    Args:
        timeout (int): Timeout for the test in seconds.
        application_version_id (str): The application version ID to use for the test.
        payload (list[ItemCreationRequest]): The payload to use for the application run.
        request (FixtureRequest): The pytest request object.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    request.node.add_marker(pytest.mark.timeout(timeout))

    client = platform.Client(cache_token=False)
    application_run = client.runs.create(application_version_id, items=payload)

    with tempfile.TemporaryDirectory() as temp_dir:
        application_run.download_to_folder(temp_dir)
        # validate the output
        _validate_output(application_run, Path(temp_dir))


def _validate_output(application_run: ApplicationRun, output_base_folder: Path) -> None:
    """Validate the output of an application run.

    This function checks if the application run has completed successfully and verifies the output artifact checksum

    Args:
        application_run (ApplicationRun): The application run to validate.
        output_base_folder (Path): The base folder where the output is stored.
    """
    assert application_run.details().status == ApplicationRunStatus.COMPLETED, (
        "Application run did not finish in completed status"
    )

    run_result_folder = output_base_folder / application_run.application_run_id
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
            file_ending = platform.mime_type_to_file_ending(artifact.mime_type)
            file_path = item_dir / f"{artifact.name}{file_ending}"
            assert file_path.exists(), f"Artifact {artifact} was not downloaded"
            checksum = artifact.metadata["checksum_base64_crc32c"]
            file_checksum = platform.calculate_file_crc32c(file_path)
            assert file_checksum == checksum, f"Metadata checksum != file checksum {checksum} <> {file_checksum}"
