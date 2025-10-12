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
    ArtifactOutput,
    ArtifactState,
    ItemStatus,
)

from aignostics import platform
from aignostics.platform.resources.runs import ApplicationRun, ApplicationRunStatus, ItemStatus
from aignx.codegen.models import ArtifactOutput
from aignx.codegen.models import ArtifactState
from aignx.codegen.models import ItemOutput
from aignx.codegen.models import ItemState
from aignx.codegen.models import RunOutput
from aignx.codegen.models import RunState
from tests.contants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_TIMEOUT_SECONDS,
    HETA_APPLICATION_VERSION,
    TEST_APPLICATION_ID,
    TEST_APPLICATION_TIMEOUT_SECONDS,
    TEST_APPLICATION_VERSION,
)


def _get_single_spot_payload_for_heta_v1_0_0() -> list[platform.InputItem]:
    """Generates a payload using a single spot."""
    return [
        platform.InputItem(
            external_id="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        "gs://platform-api-application-test-data/heta/slides/8fafc17d-a5cc-4e9d-a982-030b1486ca88.tiff",
                        HETA_APPLICATION_TIMEOUT_SECONDS,
                    ),
                    metadata={
                        "checksum_base64_crc32c": "5onqtA==",
                        "resolution_mpp": 0.26268186053789266,
                        "width_px": 7447,
                        "height_px": 7196,
                        "media_type": "image/tiff",
                        "staining_method": "H&E",
                        "specimen": {
                            "tissue": "LUNG",
                            "disease": "LUNG_CANCER",
                        },
                    },
                )
            ],
        ),
    ]


def _get_three_spots_payload_for_test_v0_0_1() -> list[platform.InputItem]:
    """Generates a payload using three spots."""
    return [
        platform.InputItem(
            external_id="1",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff",
                        TEST_APPLICATION_TIMEOUT_SECONDS,
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
            external_id="2",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/8c7b079e-8b8a-4036-bfde-5818352b503a.tiff",
                        TEST_APPLICATION_TIMEOUT_SECONDS,
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
            external_id="3",
            input_artifacts=[
                platform.InputArtifact(
                    name="user_slide",
                    download_url=platform.generate_signed_url(
                        "gs://aignx-storage-service-dev/sample_data_formatted/1f4f366f-a2c5-4407-9f5e-23400b22d50e.tiff",
                        TEST_APPLICATION_TIMEOUT_SECONDS,
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


def _run_application_test(
    application_id: str,
    application_version: str,
    payload: list[platform.InputItem],
    checksum_attribute_key: str,
) -> None:
    """Helper function to run an application test.

    This function creates an application run, downloads results, and validates outputs.

    Args:
        timeout (int): Timeout for the test in seconds.
        application_id (str): The application ID to use for the test.
        application_version (str): The application version to use for the test.
        payload (list[platform.InputItem]): The input items for the application run.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    client = platform.Client(cache_token=False)
    application_run = client.runs.create(
        application_id=application_id, application_version=application_version, items=payload
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        application_run.download_to_folder(temp_dir, checksum_attribute_key)
        # validate the output
        _validate_output(application_run, Path(temp_dir), checksum_attribute_key)


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.scheduled
@pytest.mark.timeout(timeout=TEST_APPLICATION_TIMEOUT_SECONDS)
def test_application_runs_test_version() -> None:
    """Test application runs with the test application.

    This test creates an application run using the test application and three spots.
    It then downloads the results to a temporary directory and performs various checks to ensure
    the application run completed successfully and the results are valid.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _run_application_test(
        application_id=TEST_APPLICATION_ID,
        application_version=TEST_APPLICATION_VERSION,
        payload=_get_three_spots_payload_for_test_v0_0_1(),
        checksum_attribute_key="checksum_crc32c",
    )


@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_TIMEOUT_SECONDS)
def test_application_runs_heta_version() -> None:
    """Test application runs with the HETA application.

    This test creates an application run using the HETA application and a single spot.
    It then downloads the results to a temporary directory and performs various checks to ensure
    the application run completed successfully and the results are valid.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _run_application_test(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        payload=_get_single_spot_payload_for_heta_v1_0_0(),
        checksum_attribute_key="checksum_base64_crc32c",
    )


def _validate_output(
    application_run: ApplicationRun,
    output_base_folder: Path,
    checksum_attribute_key: str = "checksum_base64_crc32c",
) -> None:
    """Validate the output of an application run.

    This function checks if the application run has completed successfully and verifies the output artifact checksum

    Args:
        application_run (ApplicationRun): The application run to validate.
        output_base_folder (Path): The base folder where the output is stored.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
    """
    run_details = application_run.details()
    assert run_details.status == RunState.TERMINATED and run_details.output == RunOutput.FULL, (
        f"Run {application_run.run_id}: Did not finish in state `FULL` for its output, but '{run_details.output}'."
    )

    run_result_folder = output_base_folder / application_run.run_id
    assert run_result_folder.exists(), f"Application run {application_run.run_id}: result folder does not exist"

    run_results = application_run.results()

    for item in run_results:
        # validate state
        assert item.state == ItemState.TERMINATED and item.output == ItemOutput.FULL, (
            f"Application run {application_run.run_id}: "
            f"output for item {item.external_id} is {item.output}, expected `FULL`"
        )
        # validate results
        item_dir = run_result_folder / item.external_id
        assert item_dir.exists(), (
            f"Application run {application_run.run_id}: result folder for item {item.external_id} does not exist"
        )
        for artifact in item.output_artifacts:
            assert artifact.state == ArtifactState.TERMINATED and artifact.output == ArtifactOutput.AVAILABLE, (
                f"Application run {application_run.run_id}: artifact {artifact} should have output state `AVAILABLE`"
            )
            assert artifact.download_url is not None, (
                f"Application run {application_run.run_id}: artifact {artifact} should provide a download url"
            )
            file_ending = platform.mime_type_to_file_ending(platform.get_mime_type_for_artifact(artifact))
            file_path = item_dir / f"{artifact.name}{file_ending}"
            assert file_path.exists(), (
                f"Application run {application_run.run_id}: artifact {artifact} was not downloaded"
            )
            checksum = artifact.metadata[checksum_attribute_key]
            file_checksum = platform.calculate_file_crc32c(file_path)
            assert file_checksum == checksum, (
                f"Application run {application_run.run_id}: "
                f"metadata checksum != file checksum {checksum} <> {file_checksum}"
            )
