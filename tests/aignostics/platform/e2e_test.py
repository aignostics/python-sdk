"""Scheduled end-to-end (e2e) tests for the Aignostics client.

This module contains e2e tests that run real application workflows
against the Aignostics platform. These tests verify e2e functionality
including creating runs, downloading results, and validating outputs.

"""

import os
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
    SchedulingRequest,
)
from aignx.codegen.models.run_read_response import RunReadResponse
from loguru import logger
from sentry_sdk import metrics

from aignostics import platform
from aignostics.platform import Run, RunSdkMetadata
from tests.constants_test import (
    HETA_APPLICATION_ID,
    HETA_APPLICATION_VERSION,
    PIPELINE_CPU_PROVISIONING_MODE,
    PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES,
    PIPELINE_GPU_PROVISIONING_MODE,
    PIPELINE_GPU_TYPE,
    PIPELINE_MAX_GPUS_PER_SLIDE,
    PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES,
    SPECIAL_APPLICATION_ID,
    SPECIAL_APPLICATION_VERSION,
    SPOT_0_CRC32C,
    SPOT_0_GS_URL,
    SPOT_0_HEIGHT,
    SPOT_0_RESOLUTION_MPP,
    SPOT_0_WIDTH,
    SPOT_1_CRC32C,
    SPOT_1_GS_URL,
    SPOT_1_HEIGHT,
    SPOT_1_RESOLUTION_MPP,
    SPOT_1_WIDTH,
    SPOT_2_CRC32C,
    SPOT_2_GS_URL,
    SPOT_2_HEIGHT,
    SPOT_2_RESOLUTION_MPP,
    SPOT_2_WIDTH,
    SPOT_3_CRC32C,
    SPOT_3_GS_URL,
    SPOT_3_HEIGHT,
    SPOT_3_RESOLUTION_MPP,
    SPOT_3_WIDTH,
    TEST_APPLICATION_ID,
    TEST_APPLICATION_VERSION,
)

TEST_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS = 60 * 45  # 45 minutes
TEST_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS = 60 * 10  # 10 minutes
TEST_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS = (
    60 * 60
)  # 1 hour - timeout should never happen if cancel on deadline exceeded works

TEST_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS = 60 * 30  # 30 minutes
TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS = 60 * 60 * 1  # 1 hour
TEST_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS = 60 * 10  # 10 minutes
TEST_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS = 60 * 5  # 5 minutes

HETA_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS = 60 * 60 * 1  # 1 hour
HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS = 60 * 60 * 4  # 4 hours
HETA_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS = (
    60 * 60 * 5
)  # 5 hours - timeout should never happen if cancel on deadline exceeded works

HETA_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS = 60 * 60 * 20  # 20 hours
HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS = 60 * 60 * 24  # 24 hours
HETA_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS = 60 * 10  # 10 minutes
HETA_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS = 60 * 5  # 5 minutes

# Plan to have 100.000 slides processed in total, with 100 slides per application run,
# one application run starting every 5 minutes, with a throughput of 1 slide per minute,
# given no GPU.
SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT = 100
SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT_ON_00 = 2000  # Minute 0..9
SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT_ON_20 = 2000  # Minute 20..29
SPECIAL_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS = 60 * 60 * 20  # 20 hours
SPECIAL_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS = 60 * 60 * 24  # 24 hours
SPECIAL_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS_ON_40 = 60 * 60 * 2  # 2 hours
SPECIAL_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS_ON_40 = 60 * 60 * 3  # 3 hours
SPECIAL_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS = 60 * 30  # 30 minutes
SPECIAL_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS = 60 * 60  # 60 minutes


def _get_single_spot_payload_for_heta(expires_seconds: int) -> list[platform.InputItem]:
    """Generates a payload using a single spot."""
    return [
        platform.InputItem(
            external_id=SPOT_0_GS_URL,
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=SPOT_0_GS_URL,
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": SPOT_0_CRC32C,
                        "resolution_mpp": SPOT_0_RESOLUTION_MPP,
                        "width_px": SPOT_0_WIDTH,
                        "height_px": SPOT_0_HEIGHT,
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
            external_id=SPOT_1_GS_URL,
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=SPOT_1_GS_URL,
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": SPOT_1_CRC32C,
                        "width_px": SPOT_1_WIDTH,
                        "height_px": SPOT_1_HEIGHT,
                        "resolution_mpp": SPOT_1_RESOLUTION_MPP,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
        platform.InputItem(
            external_id=SPOT_2_GS_URL,
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=SPOT_2_GS_URL,
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": SPOT_2_CRC32C,
                        "width_px": SPOT_2_WIDTH,
                        "height_px": SPOT_2_HEIGHT,
                        "resolution_mpp": SPOT_2_RESOLUTION_MPP,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
        platform.InputItem(
            external_id=SPOT_3_GS_URL,
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=platform.generate_signed_url(
                        url=SPOT_3_GS_URL,
                        expires_seconds=expires_seconds,
                    ),
                    metadata={
                        "checksum_base64_crc32c": SPOT_3_CRC32C,
                        "width_px": SPOT_3_WIDTH,
                        "height_px": SPOT_3_HEIGHT,
                        "resolution_mpp": SPOT_3_RESOLUTION_MPP,
                        "media_type": "image/tiff",
                    },
                )
            ],
        ),
    ]


def _get_spots_payload_for_special(expires_seconds: int, count: int) -> list[platform.InputItem]:
    """Generates a payload using count many spots.

    Optimized for large counts (e.g., 100k items):
    - Generates signed URL once (all items use same source file)
    - Pre-builds metadata dicts once (identical across all items)

    Args:
        expires_seconds: Expiration time for signed URLs in seconds.
        count: Number of items to generate.

    Returns:
        List of InputItem objects for the special application.
    """
    if count <= 0:
        return []

    signed_url = platform.generate_signed_url(
        url=SPOT_1_GS_URL,
        expires_seconds=expires_seconds,
    )
    wsi_metadata = {
        "checksum_base64_crc32c": SPOT_1_CRC32C,
        "width_px": SPOT_1_WIDTH,
        "height_px": SPOT_1_HEIGHT,
        "resolution_mpp": SPOT_1_RESOLUTION_MPP,
        "media_type": "image/tiff",
        "staining_method": "H&E",
        "specimen": {
            "tissue": "LUNG",
            "disease": "LUNG_CANCER",
        },
    }
    normalization_metadata = {
        "checksum_base64_crc32c": SPOT_1_CRC32C,
        "width_px": SPOT_1_WIDTH,
        "height_px": SPOT_1_HEIGHT,
        "resolution_mpp": SPOT_1_RESOLUTION_MPP,
        "media_type": "image/tiff",
    }
    return [
        platform.InputItem(
            external_id=f"{SPOT_1_GS_URL}&spot_index={index}",
            input_artifacts=[
                platform.InputArtifact(
                    name="whole_slide_image",
                    download_url=signed_url,
                    metadata=wsi_metadata,
                ),
                platform.InputArtifact(
                    name="normalization:wsi",
                    download_url=signed_url,
                    metadata=normalization_metadata,
                ),
            ],
        )
        for index in range(count)
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
    tags = tags or set()
    now = datetime.now(tz=UTC)
    due_date = now + timedelta(seconds=due_date_seconds)
    deadline = now + timedelta(seconds=deadline_seconds)
    find_and_validate_at = deadline + timedelta(hours=1)
    tags.add(
        f"find_and_validate:{find_and_validate_at.month}_{find_and_validate_at.day}_{find_and_validate_at.hour}"
    )  # Add a tag indicating when this run has to be found and validated for completion

    logger.trace(f"Submitting application run for {application_id} version {application_version}")
    client = platform.Client()
    scheduling = SchedulingRequest(due_date=due_date, deadline=deadline)
    custom_metadata = {
        "sdk": {
            "tags": tags or set(),
            "pipeline": {
                "gpu": {
                    "gpu_type": PIPELINE_GPU_TYPE,
                    "provisioning_mode": PIPELINE_GPU_PROVISIONING_MODE,
                    "max_gpus_per_slide": PIPELINE_MAX_GPUS_PER_SLIDE,
                },
                "cpu": {
                    "provisioning_mode": PIPELINE_CPU_PROVISIONING_MODE,
                },
                "node_acquisition_timeout_minutes": PIPELINE_NODE_ACQUISITION_TIMEOUT_MINUTES,
            },
        }
    }
    # TODO(oliverm): remove this conditional when applications handle null flex_start_max_run_duration_minutes
    if PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES:
        custom_metadata["sdk"]["pipeline"]["gpu"]["flex_start_max_run_duration_minutes"] = (
            PIPELINE_GPU_FLEX_START_MAX_RUN_DURATION_MINUTES
        )
    run = client.runs.submit(
        application_id=application_id,
        application_version=application_version,
        items=payload,
        custom_metadata=custom_metadata,
        scheduling=scheduling,
    )

    # Let's validate we can find the run by id
    details = run.details()
    assert details.run_id == run.run_id, "Run ID mismatch after submission"
    assert details.application_id == application_id, "Application ID mismatch after submission"
    assert details.version_number == application_version, "Application version mismatch after submission"
    assert details.state in {RunState.PENDING, RunState.PROCESSING}, (
        f"Unexpected run state `{details.state}` after submission"
    )

    # ... and by tags, as otherwise the 2nd leg of the test won't be able to find it
    for tag in tags:
        runs = client.runs.list(
            application_id=application_id,
            application_version=application_version,
            custom_metadata=f'$.sdk.tags[*] ? (@ == "{tag}")',
        )
        matched_runs = [r for r in runs if r.run_id == run.run_id]
        assert len(matched_runs) == 1, (
            f"Submitted run `{run.run_id}` not found in run listing by filtering for tag `{tag}`"
        )

    return run


def _submit_and_wait(  # noqa: PLR0913, PLR0917
    application_id: str,
    application_version: str,
    payload: list[platform.InputItem],
    record_property,
    due_date_seconds: int,
    deadline_seconds: int,
    timeout_seconds: int,
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
        timeout_seconds (int): The timeout in seconds to wait for the application run to complete.
        tags (set[str] | None): A set of tags to attach to the application run.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.
        record_property: Function to record test properties.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")
    run = _submit_and_validate(
        application_id=application_id,
        application_version=application_version,
        payload=payload,
        due_date_seconds=due_date_seconds,
        deadline_seconds=deadline_seconds,
        tags=tags,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        run.download_to_folder(temp_dir, checksum_attribute_key, timeout_seconds=timeout_seconds)
        _validate_output(run, Path(temp_dir), checksum_attribute_key)


def _resolve_run_deadline(details: RunReadResponse, sdk_metadata: RunSdkMetadata) -> datetime:
    """Extract the run deadline from the API scheduling field, falling back to custom_metadata.

    Raises:
        ValueError: If no deadline is found in either the API scheduling field or sdk_metadata.scheduling.
    """
    if getattr(details, "scheduling", None) is not None and getattr(details.scheduling, "deadline", None) is not None:
        deadline = details.scheduling.deadline
        return deadline if isinstance(deadline, datetime) else datetime.fromisoformat(str(deadline))
    if getattr(sdk_metadata, "scheduling", None) is None or getattr(sdk_metadata.scheduling, "deadline", None) is None:
        msg = "No deadline found in API scheduling field or sdk_metadata.scheduling"
        raise ValueError(msg)
    return datetime.fromisoformat(str(sdk_metadata.scheduling.deadline))


def _find_and_validate(
    application_id: str,
    application_version: str,
    checksum_attribute_key: str = "checksum_base64_crc32c",
) -> Run:
    """Find application run submitted earlier and validate its details.

    Args:
        application_id (str): The application ID to use for the test.
        application_version (str): The application version to use for the test.
        checksum_attribute_key (str): The key used to validate the checksum of the output artifacts.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    client = platform.Client()
    assert client is not None, "Failed to create platform client"
    now = datetime.now(tz=UTC)
    check_this_hour_tag = f"find_and_validate:{now.month}_{now.day}_{now.hour}"
    runs = list(
        client.runs.list(
            application_id=application_id,
            application_version=application_version,
            custom_metadata=f'$.sdk.tags[*] ? (@ == "{check_this_hour_tag}")',
        )
    )
    logger.debug(f"Found {len(runs)} runs with tag {check_this_hour_tag}")
    for run in runs:
        details = run.details(nocache=True)
        assert details.application_id == application_id, (
            f"Listed run `{run.run_id}` has unexpected application id `{details.application_id}`"
        )
        assert details.version_number == application_version, (
            f"Listed run `{run.run_id}` has unexpected application version `{details.version_number}`"
        )
        run_handle = Run.for_run_id(run.run_id)
        logger.trace(run_handle)
        print(run_handle)
        for item in run_handle.results(nocache=True):
            message = (
                f"Output of item `{item.external_id}` is `{item.output}`, state `{item.state}`, "
                f"error `{item.error_message}` ({item.error_code}), "
                f"termination reason `{item.termination_reason}`."
            )
            logger.trace(message)
            print(message)
        sdk_metadata = RunSdkMetadata.model_validate(details.custom_metadata.get("sdk", {}))
        logger.trace(sdk_metadata.model_dump_json(indent=2))
        print(sdk_metadata.model_dump_json(indent=2))
        run_deadline = _resolve_run_deadline(details, sdk_metadata)
        allowed_duration = run_deadline - datetime.fromisoformat(sdk_metadata.submission.date)
        allowed_hours = round(allowed_duration.total_seconds() / (60 * 60))
        deadline_met = details.state is RunState.TERMINATED
        metrics_run_attributes = {
            "platform_environment": os.environ.get("AIGNOSTICS_PLATFORM_ENVIRONMENT", "production"),
            "application_id": application_id,
            "application_version": application_version,
            "allowed_hours": allowed_hours,
            "submitted_at": sdk_metadata.submission.date,
            "deadline": run_deadline.isoformat(),
            "state": details.state.value,
            "error_message": details.error_message,
            "error_code": details.error_code,
        }
        logger.trace(f"metrics_run_attributes: {metrics_run_attributes}")
        print(f"metrics_run_attributes: {metrics_run_attributes}")
        if deadline_met:
            metrics.count(
                name="aignostics.platform.tests.run.deadline.met",
                value=1,
                attributes=metrics_run_attributes,
            )
            if details.terminated_at:
                completed_duration_seconds = (
                    details.terminated_at - datetime.fromisoformat(sdk_metadata.submission.date)
                ).total_seconds()
                message = f"Run completed in {completed_duration_seconds} seconds"
                logger.trace(message)
                print(message)
                metrics.distribution(
                    name="aignostics.platform.tests.run.completed.duration",
                    value=completed_duration_seconds,
                    unit="seconds",
                    attributes=metrics_run_attributes,
                )
        else:
            metrics.count(
                name="aignostics.platform.tests.runs.deadline.breached",
                value=1,
                attributes=metrics_run_attributes,
            )
        assert deadline_met, (
            f"{run_handle}, submitted at {sdk_metadata.submission.date}, breached {allowed_hours} hour deadline."
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            run.download_to_folder(temp_dir, checksum_attribute_key, timeout_seconds=0)
            _validate_output(run, Path(temp_dir), checksum_attribute_key)


@pytest.mark.e2e
@pytest.mark.very_long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=TEST_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS + 60 * 5)
def test_platform_test_app_submit_and_wait(record_property) -> None:
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
        payload=_get_three_spots_payload_for_test(
            expires_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 5
        ),
        record_property=record_property,
        deadline_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=TEST_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
        timeout_seconds=TEST_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS,
        tags={"test_platform_test_app_submit_and_wait", "scheduled"},
    )


@pytest.mark.skip(reason="Switching to submit and find approach")
@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS + 60 * 5)
def test_platform_heta_app_submit_and_wait(record_property) -> None:
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
        record_property=record_property,
        deadline_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_DEADLINE_SECONDS,
        due_date_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_DUE_DATE_SECONDS,
        timeout_seconds=HETA_APPLICATION_SUBMIT_AND_WAIT_TIMEOUT_SECONDS,
        tags={"test_platform_heta_app_submit_and_wait", "scheduled"},
    )


@pytest.mark.skip(reason="Using submit and wait approach")
@pytest.mark.e2e
@pytest.mark.timeout(timeout=TEST_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS)
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
        tags={"test_platform_heta_app_submit_and_wait", "scheduled"},
    )


@pytest.mark.e2e
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=TEST_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS)
def test_platform_test_app_find_and_validate() -> None:
    """Test application runs with the test application.

    This test finds an application run with the test application submitted earlier and
    validates it completed successfully and in time.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _find_and_validate(
        application_id=TEST_APPLICATION_ID,
        application_version=TEST_APPLICATION_VERSION,
    )


@pytest.mark.e2e
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS)
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
            expires_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS + 60 * 60 * 10  # 10 hours buffer
        ),
        deadline_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS,
        due_date_seconds=HETA_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS,
        tags={"test_platform_heta_app_submit_and_find", "scheduled"},
    )


@pytest.mark.e2e
@pytest.mark.stress_only
@pytest.mark.long_running
@pytest.mark.timeout(timeout=SPECIAL_APPLICATION_SUBMIT_AND_FIND_SUBMIT_TIMEOUT_SECONDS)
def test_platform_special_app_submit() -> None:
    """Test application runs with the special application.

    This test submits an application run with the special application and validates the submission.

    The test behavior varies based on the current minute when triggered by cron (*/10):
    - Minutes 0-9 (every 6th run): Uses 1000 items instead of 100
    - Minutes 40-49 (every 4th run): Uses 2h due date / 3h deadline instead of 20h due date / 24h deadline

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    # Determine run configuration based on current minute
    # Cron runs every 10 minutes (*/10, in _scheduled-test-stress.yml),
    # so we check which 10-minute window we're in
    current_minute = datetime.now(tz=UTC).minute
    is_on_00 = 0 <= current_minute <= 9
    is_on_20 = 20 <= current_minute <= 29
    is_on_40 = 40 <= current_minute <= 49

    if is_on_00:
        slide_count = SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT_ON_00
    elif is_on_20:
        slide_count = SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT_ON_20
    else:
        slide_count = SPECIAL_APPLICATION_SLIDE_PER_RUN_COUNT

    deadline_seconds = (
        SPECIAL_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS_ON_40
        if is_on_40
        else SPECIAL_APPLICATION_SUBMIT_AND_FIND_DEADLINE_SECONDS
    )
    due_date_seconds = (
        SPECIAL_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS_ON_40
        if is_on_40
        else SPECIAL_APPLICATION_SUBMIT_AND_FIND_DUE_DATE_SECONDS
    )

    logger.info(
        f"Special app submit config: minute={current_minute}, is_on_00={is_on_00}, is_on_40={is_on_40}, "
        f"slide_count={slide_count}, deadline_seconds={deadline_seconds}, due_date_seconds={due_date_seconds}"
    )

    logger.trace(
        f"Generating special application payload with {slide_count} spots for "
        f"{SPECIAL_APPLICATION_ID} version {SPECIAL_APPLICATION_VERSION}"
    )
    payload = _get_spots_payload_for_special(
        expires_seconds=deadline_seconds + 60 * 5,
        count=slide_count,
    )
    logger.debug(f"Generated special application payload: {payload}")
    _submit_and_validate(
        application_id=SPECIAL_APPLICATION_ID,
        application_version=SPECIAL_APPLICATION_VERSION,
        payload=payload,
        deadline_seconds=deadline_seconds,
        due_date_seconds=due_date_seconds,
        tags={"test_platform_special_app_submit", "special", "stress", "stress_only"},
    )
    logger.debug("Special application payload submitted successfully")


@pytest.mark.e2e
@pytest.mark.stress_only
@pytest.mark.long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=SPECIAL_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS)
def test_platform_special_app_find_and_validate() -> None:
    """Test application runs with the special application.

    This test finds an application run with the special application submitted earlier and
    validates it completed successfully and in time.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _find_and_validate(
        application_id=SPECIAL_APPLICATION_ID,
        application_version=SPECIAL_APPLICATION_VERSION,
    )


@pytest.mark.e2e
@pytest.mark.long_running
@pytest.mark.scheduled_only
@pytest.mark.timeout(timeout=HETA_APPLICATION_FIND_AND_VALIDATE_TIMEOUT_SECONDS)
def test_platform_heta_app_find_and_validate() -> None:
    """Test application runs with the HETA application.

    This test finds an application run with the HETA application submitted earlier and
    validates it completed successfully and in time.

    Raises:
        AssertionError: If any of the validation checks fail.
    """
    _find_and_validate(
        application_id=HETA_APPLICATION_ID,
        application_version=HETA_APPLICATION_VERSION,
    )


_CANARY_MAX_RUNS_TO_INSPECT = 20


def _find_available_output_artifact_id(run: Run) -> str | None:
    """Return the first AVAILABLE output_artifact_id from a successful run, else None.

    Single-run scan helper for the /file endpoint canary. Walks the run's
    items and per-item artifacts and returns the first artifact whose output
    is ``AVAILABLE`` and whose ``output_artifact_id`` is non-empty. Returns
    ``None`` when the run produced no usable artifact (e.g. all items
    terminated with ``NONE`` output). The caller is expected to have already
    filtered for runs that are ``TERMINATED`` with ``FULL`` output.
    """
    for item in run.results(nocache=True):
        if item.state is not ItemState.TERMINATED or item.output is not ItemOutput.FULL:
            continue
        for art in item.output_artifacts:
            if art.output is ArtifactOutput.AVAILABLE and art.output_artifact_id:
                return art.output_artifact_id
    return None


def _find_available_artifact_in_recent_heta_run() -> tuple[Run, str] | None:
    """Find one AVAILABLE output artifact from a recent successful HETA run.

    Helper for the /file endpoint canary below. Iterates the most recent HETA
    runs tagged ``scheduled`` lazily — only inspects up to
    ``_CANARY_MAX_RUNS_TO_INSPECT`` runs and stops at the first hit. Returns
    ``None`` when no such artifact is reachable in the inspected window — the
    canary skips in that case rather than fails.

    The cap exists because, as staging accumulates scheduled runs, materializing
    the full list and querying details/results for every one risks the canary's
    60s timeout. Runs from ``client.runs.list`` are already returned newest-first
    so capping is biased toward recent data.

    Returns:
        tuple[Run, str] | None: A bound (Run, output_artifact_id) pair, or None.
    """
    import itertools

    client = platform.Client()
    # client.runs.list yields Run handles directly; iterate lazily and cap to N
    # so the canary stays well under its 60s timeout even on a busy staging env.
    candidate_runs = itertools.islice(
        client.runs.list(
            application_id=HETA_APPLICATION_ID,
            application_version=HETA_APPLICATION_VERSION,
            custom_metadata='$.sdk.tags[*] ? (@ == "scheduled")',
        ),
        _CANARY_MAX_RUNS_TO_INSPECT,
    )
    for run in candidate_runs:
        details = run.details(nocache=True)
        if details.state is not RunState.TERMINATED or details.output is not RunOutput.FULL:
            continue
        artifact_id = _find_available_output_artifact_id(run)
        if artifact_id is not None:
            return run, artifact_id
    return None


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_platform_artifact_file_endpoint_resolves_to_working_url(record_property) -> None:
    """Smoke-test the SAMIA /file endpoint at PR time, not 6h later.

    The full ``_validate_output`` flow that exercises the new endpoint is
    ``scheduled_only``, so it never runs on PRs. That leaves a window in which
    a SAMIA-side regression to ``/api/v1/runs/{run_id}/artifacts/{artifact_id}/file``
    (think PAPI-4868: the auth bug that forced reverting #507) ships green
    through PR CI and is only caught by the next scheduled run, up to 6h later.

    This canary closes that window: at PR time it picks any recent successful
    HETA run, resolves a presigned URL through ``Run.get_artifact_download_url``
    against real SAMIA, and ``HEAD``-checks the URL to confirm the storage backend
    serves it. The whole roundtrip is well under 60s, so the test stays out of
    ``long_running`` and runs on every PR that doesn't carry ``skip:test:e2e``.

    Failure modes covered end-to-end:

    - ``/file`` endpoint 5xx / 4xx (auth, missing run, etc.) → typed exception
    - ``/file`` returns 3xx with an empty Location header → ``RuntimeError``
    - ``/file`` returns a Location URL that storage rejects → ``HEAD`` fails
    - ``/file`` returns a Location URL pointing at the wrong scope → ``HEAD`` 403

    Skips when no recent successful HETA run exists (e.g. the first time the
    scheduled suite has been run in a fresh staging environment) — the test
    is a canary, not a fixture provider, so a missing prerequisite is not a
    failure.

    Raises:
        AssertionError: If the resolved URL is empty or the HEAD request fails.
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SERVICE")

    # Local import: requests is already an SDK dep; importing at use-site avoids
    # adding to the module-level imports of an otherwise import-heavy test file.
    import requests

    found = _find_available_artifact_in_recent_heta_run()
    if found is None:
        pytest.skip(
            f"No AVAILABLE output artifact in any recent HETA run "
            f"(version {HETA_APPLICATION_VERSION}) tagged 'scheduled'; "
            "this canary needs one from the scheduled suite to exercise the /file endpoint."
        )
    selected_run, artifact_id = found

    presigned_url = selected_run.get_artifact_download_url(artifact_id)
    assert presigned_url, (
        f"SAMIA /file endpoint returned an empty/falsy URL for run={selected_run.run_id} artifact={artifact_id}"
    )

    head_response = requests.head(presigned_url, allow_redirects=True, timeout=30)
    assert head_response.ok, (
        f"Presigned URL from /file endpoint did not serve content: "
        f"{head_response.status_code} {head_response.reason} "
        f"(run={selected_run.run_id} artifact={artifact_id})"
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
    run_details = application_run.details(nocache=True)
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
            artifact_download_url = application_run.get_artifact_download_url(artifact.output_artifact_id)
            assert artifact_download_url, (
                f"Application run `{application_run.run_id}`: artifact `{artifact}` "
                f"should resolve to a presigned download URL via the /file endpoint."
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
