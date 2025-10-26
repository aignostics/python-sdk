"""Scheduled end-to-end (e2e) tests for the Aignostics client.

This module contains e2e tests that run real application workflows
against the Aignostics platform. These tests verify e2e functionality
including creating runs, downloading results, and validating outputs.

"""

import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from aignx.codegen.models import (
    ArtifactOutput,
    ArtifactState,
    ItemOutput,
    ItemState,
    RunOutput,
    RunState,
)

from aignostics import platform
from aignostics.platform.resources.runs import Run
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    HETA_SINGLE_SPOT_GS_URL,
    TEST_APPLICATION_ID,
    TEST_APPLICATION_VERSION,
    TEST_THREE_SPOTS_GS_URLS,
)

TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS = 60 * 45  # 45 minutes
TEST_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS = 60 * 10  # 10 minutes

TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS = 60 * 60 * 24  # 24 hours
TEST_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS = 60 * 60 * 24  # 24 hours

HETA_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS = 60 * 60 * 1  # 1 hour
HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS = 60 * 60 * 3  # 3 hours

HETA_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS = 60 * 60 * 24  # 24 hours
HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS = 60 * 60 * 24  # 24 hours


def _get_single_spot_payload_for_heta(expires_seconds: int) -> list[platform.InputItem]:
    """Generates a payload using a single spot."""
    return [
        platform.InputItem(
            external_id=HETA_SINGLE_SPOT_GS_URL,
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=HETA_SINGLE_SPOT_GS_URL,
                        expires_seconds=expires_seconds,
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


def _get_three_spots_payload_for_test(expires_seconds: int) -> list[platform.InputItem]:
    """Generates a payload using three spots."""
    return [
        platform.InputItem(
            external_id=TEST_THREE_SPOTS_GS_URLS[0],
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=TEST_THREE_SPOTS_GS_URLS[0],
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": "9l3NNQ==",
                        "width_px": 3728,
                        "height_px": 3640,
                        "resolution_mpp": 0.46499982,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
        platform.InputItem(
            external_id=TEST_THREE_SPOTS_GS_URLS[1],
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=TEST_THREE_SPOTS_GS_URLS[1],
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": "w+ud3g==",
                        "width_px": 3616,
                        "height_px": 3400,
                        "resolution_mpp": 0.46499982,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
        platform.InputItem(
            external_id=TEST_THREE_SPOTS_GS_URLS[2],
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=TEST_THREE_SPOTS_GS_URLS[2],
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": "Zmx0wA==",
                        "width_px": 4016,
                        "height_px": 3952,
                        "resolution_mpp": 0.46499982,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
    ]


def _submit_and_validate(  # noqa: PLR0913, PLR0917
    application_id: str,
    application_version: str,
    payload: list[platform.InputItem],
    due_date_seconds: int,
    deadline_seconds: int,
    tags: set[str] | None = None,
) -> Run:
    """Submit application run and validate its details.

    Args:
        application_id (str): The application ID to use for the test.
        application_version (str): The application version to use for the test.
        payload (list[platform.InputItem]): The input items for the application run.
        due_date_seconds (int): The due date in seconds from now for the application run.
        deadline_seconds (int): The deadline in seconds from now for the application run.
        tags (set[str] | None): A set of tags to attach to the application run.

    Raises:
        AssertionError: If any of the validation checks fail.
        ValueError: If more than one tag is provided.
    """
    client = platform.Client()
    run = client.runs.submit(
        application_id=application_id,
        application_version=application_version,
        items=payload,
        custom_metadata={
            "sdk": {
                "tags": tags or set(),
                "scheduling": {
                    "due_date": (datetime.now(tz=UTC) + timedelta(seconds=due_date_seconds)).isoformat(),
                    "deadline": (datetime.now(tz=UTC) + timedelta(seconds=deadline_seconds)).isoformat(),
                },
            }
        },
    )
    details = run.details()
    assert details.run_id == run.run_id, "Run ID mismatch after submission"
    assert details.application_id == application_id, "Application ID mismatch after submission"
    assert details.application_version == application_version, "Application version mismatch after submission"
    assert details.state in {RunState.PENDING, RunState.PROCESSING}, (
        f"Unexpected run state `{details.state}` after submission"
    )

    if tags and len(tags) > 1:
        message = "Only single tag filtering is supported in this test code."
        raise ValueError(message)
    runs = client.runs.list(
        application_id=application_id,
        application_version=application_version,
        custom_metadata=f'$.sdk.tags[*] ? (@ == "{tags[0]}")' if tags else None,
    )

    # Find the submitted run in the list
    matched_runs = [r for r in runs if r.run_id == run.run_id]
    assert len(matched_runs) == 1, f"Submitted run `{run.run_id}` not found in run listing"

    return run


def _submit_and_wait(  # noqa: PLR0913, PLR0917
    application_id: str,
    application_version: str,
    payload: list[platform.InputItem],
    due_date_seconds: int,
    deadline_seconds: int,
    tags: set[str] | None = None,
    checksum_attribute_key: str = "checksum_base64_crc32c",
) -> None:
    """Helper function to run an application test.

    This function creates an application run, waits for results to become available,
        downloads results, and validates outputs.

    Args:
        application_id (str): The application ID to use for the test.
        application_version (str): The application version to use for the test.
        payload (list[platform.InputItem]): The input items for the application run.
        due_date_seconds (int): The due date in seconds from now for the application run.
        deadline_seconds (int): The deadline in seconds from now for the application run.
        tags (set[str] | None): A set of tags to attach to the application run.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    run = _submit_and_validate(
        application_id=application_id,
        application_version=application_version,
        payload=payload,
        due_date_seconds=due_date_seconds,
        deadline_seconds=deadline_seconds,
        tags=tags,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        run.download_to_folder(temp_dir, checksum_attribute_key, timeout_seconds=deadline_seconds)
        _validate_output(run, Path(temp_dir), checksum_attribute_key)


def _find_and_validate(
    application_id: str,
    application_version: str,
    payload: list[platform.InputItem],
    due_date_seconds: int,
    deadline_seconds: int,
) -> Run:
    """Find application run submitted earlier and validate its details.

    Args:
        application_id (str): The application ID to use for the test.
        application_version (str): The application version to use for the test.
        payload (list[platform.InputItem]): The input items for the application run.
        due_date_seconds (int): The due date in seconds from now for the application run.
        deadline_seconds (int): The deadline in seconds from now for the application run.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    client = platform.Client()
    assert client is not None, "Failed to create platform client"
    # TODO(Helmut): Build logic to find the run based on metadata once supported


@pytest.mark.skip(
    reason="v0.0.4 on production balking on whole_slide_image input while identical version accepting on staging"
)
@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.timeout(timeout=TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5)
def test_platform_test_app_submit_and_wait() -> None:
    """Test application runs with the test application.

    This test creates an application run using the test application and three spots.
    It then waits for results to become available, downloads the results to a temporary directory
    and performs various checks to ensure the application run completed successfully and the results are valid.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _submit_and_wait(
        application_id=TEST_APPLICATION_ID,
        application_version=TEST_APPLICATION_VERSION,
        payload=_get_three_spots_payload_for_test(),
        deadline_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
        tags=["test_platform_test_app_submit_and_wait"],
    )


@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5)
def test_platform_heta_app_submit_and_wait() -> None:
    """Test application runs with the HETA application.

    This test creates an application run using the HETA application and a single spot.
    It then waits for the results to become available, downloads the results to a
    temporary directory and performs various checks to ensure the application run completed successfully
    and the results are valid.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _submit_and_wait(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        payload=_get_single_spot_payload_for_heta(
            expires_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5
        ),
        deadline_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS,
        due_date_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS,
        tags=["test_platform_heta_app_submit_and_wait"],
    )


@pytest.mark.skip(reason="Waits for change in scheduler")
@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.timeout(timeout=TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5)
def test_platform_test_app_submit() -> None:
    """Test application submission with the test application.

    This test submits an application run with the test application and validates the submission.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _submit_and_validate(
        application_id=TEST_APPLICATION_ID,
        application_version=TEST_APPLICATION_VERSION,
        payload=_get_three_spots_payload_for_test(
            expires_seconds=TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5
        ),
        deadline_seconds=TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS,
        due_date_seconds=TEST_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS,
        tags=["test_platform_heta_app_submit_and_wait"],
    )


@pytest.mark.skip(reason="Waits for change in scheduler")
@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 5)
def test_platform_test_app_find() -> None:
    """Test application runs with the test application.

    This test finds an application run with the test application submitted earlier and
    validates it completed successfully and in time.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _find_and_validate(
        application_id=TEST_APPLICATION_ID,
        application_version=TEST_APPLICATION_VERSION,
        payload=_get_three_spots_payload_for_test(
            expires_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 5
        ),
        deadline_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
    )


@pytest.mark.skip(reason="Waits for change in scheduler")
@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5)
def test_platform_heta_app_submit() -> None:
    """Test application runs with the HETA application.

    This test submits an application run with the HETA application and validates the submission.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _submit_and_validate(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        payload=_get_single_spot_payload_for_heta(
            expires_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 5
        ),
        deadline_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
        tags=["test_platform_heta_app_submit_and_find"],
    )


@pytest.mark.skip(reason="Waits for change in scheduler")
@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS + 60 * 5)
def test_platform_heta_app_find() -> None:
    """Test application runs with the HETA application.

    This test finds an application run with the HETA application submitted earlier and
    validates it completed successfully and in time.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _find_and_validate(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
        payload=_get_single_spot_payload_for_heta(
            expires_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 5
        ),
        deadline_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
    )


def _validate_output(
    application_run: Run,
    output_base_folder: Path,
    checksum_attribute_key: str = "checksum_base64_crc32c",
) -> None:
    """Validate the output of an application run.

    This function checks if the application run has completed successfully and verifies the output artifact checksum

    Args:
        application_run (Run): The application run to validate.
        output_base_folder (Path): The base folder where the output is stored.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
    """
    # validate run state
    run_details = application_run.details()
    assert run_details.state == RunState.TERMINATED, (
        f"Run `{application_run.run_id}`: "
        f"Did not finish in state `TERMINATED`, but `{run_details.state}`.\n"
        f"Termination reason `{run_details.termination_reason}`, "
        f"error code `{run_details.error_code}`, message `{run_details.error_message}`."
    )
    assert run_details.output == RunOutput.FULL, (
        f"Run `{application_run.run_id}`: "
        f"Did not finish in state `FULL` for its output, but `{run_details.output}`.\n"
        f"Termination reason `{run_details.termination_reason}`, "
        f"error code `{run_details.error_code}`, message `{run_details.error_message}`."
    )

    run_result_folder = output_base_folder / application_run.run_id
    assert run_result_folder.exists(), f"Application run {application_run.run_id}: result folder does not exist"

    # validate item state
    run_results = application_run.results()
    for item in run_results:
        assert item.state == ItemState.TERMINATED, (
            f"Application run `{application_run.run_id}`: "
            f"state for item `{item.external_id}` is `{item.state}`, expected `TERMINATED`.\n"
            f"Termination reason `{item.termination_reason}`, "
            f"error code `{item.error_code}`, message `{item.error_message}`."
        )
        assert item.output == ItemOutput.FULL, (
            f"Application run `{application_run.run_id}`: "
            f"output for item `{item.external_id}` is `{item.output}`, expected `FULL`.\n"
            f"Termination reason`{item.termination_reason}`, "
            f"error code `{item.error_code}`, message `{item.error_message}`."
        )

        # validate output artifact state
        item_dir = run_result_folder / item.external_id
        assert item_dir.exists(), (
            f"Application run `{application_run.run_id}`: result folder for item `{item.external_id}` does not exist"
        )
        for artifact in item.output_artifacts:
            assert artifact.state == ArtifactState.TERMINATED, (
                f"Application run `{application_run.run_id}`: artifact `{artifact}` should have state `TERMINATED`"
            )
            assert artifact.output == ArtifactOutput.AVAILABLE, (
                f"Application run `{application_run.run_id}`: "
                f"artifact `{artifact}` should have output state `AVAILABLE`."
            )
            assert artifact.download_url is not None, (
                f"Application run `{application_run.run_id}`: artifact `{artifact}` should provide a download url."
            )
            file_ending = platform.mime_type_to_file_ending(platform.get_mime_type_for_artifact(artifact))
            file_path = item_dir / f"{artifact.name}{file_ending}"
            assert file_path.exists(), (
                f"Application run `{application_run.run_id}`: artifact `{artifact}` was not downloaded/"
            )
            checksum = artifact.metadata[checksum_attribute_key]
            file_checksum = platform.calculate_file_crc32c(file_path)
            assert file_checksum == checksum, (
                f"Application run `{application_run.run_id}`: "
                f"metadata checksum != file checksum `{checksum}` <> `{file_checksum}` for artifact `{artifact}`."
            )
