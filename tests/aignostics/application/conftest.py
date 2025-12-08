"""Shared fixtures for application module tests."""

from datetime import UTC, datetime

import pytest

from aignostics.platform import (
    RunData,
    RunItemStatistics,
    RunOutput,
    RunState,
    RunTerminationReason,
)


def make_run_item_statistics(
    item_count: int = 1,
    item_pending_count: int = 0,
    item_processing_count: int = 0,
    item_skipped_count: int = 0,
    item_succeeded_count: int = 1,
    item_user_error_count: int = 0,
    item_system_error_count: int = 0,
) -> RunItemStatistics:
    """Create a RunItemStatistics instance with sensible defaults.

    Args:
        item_count: Total number of items.
        item_pending_count: Number of pending items.
        item_processing_count: Number of processing items.
        item_skipped_count: Number of skipped items.
        item_succeeded_count: Number of succeeded items.
        item_user_error_count: Number of user error items.
        item_system_error_count: Number of system error items.

    Returns:
        RunItemStatistics: A statistics instance with the specified values.
    """
    return RunItemStatistics(
        item_count=item_count,
        item_pending_count=item_pending_count,
        item_processing_count=item_processing_count,
        item_skipped_count=item_skipped_count,
        item_succeeded_count=item_succeeded_count,
        item_user_error_count=item_user_error_count,
        item_system_error_count=item_system_error_count,
    )


def make_run_data(
    run_id: str = "run-123",
    application_id: str = "he-tme",
    version_number: str = "1.0.0",
    state: RunState = RunState.PENDING,
    termination_reason: RunTerminationReason | None = None,
    output: RunOutput = RunOutput.NONE,
    statistics: RunItemStatistics | None = None,
    submitted_at: datetime | None = None,
    submitted_by: str = "user@example.com",
    terminated_at: datetime | None = None,
    custom_metadata: dict | None = None,
    error_message: str | None = None,
    error_code: str | None = None,
    num_preceding_items_org: int | None = None,
    num_preceding_items_platform: int | None = None,
) -> RunData:
    """Create a RunData instance with sensible defaults.

    Args:
        run_id: The run ID.
        application_id: The application ID.
        version_number: The version number.
        state: The run state.
        termination_reason: The termination reason.
        output: The output status.
        statistics: The item statistics (defaults to single pending item).
        submitted_at: When the run was submitted.
        submitted_by: Who submitted the run.
        terminated_at: When the run terminated.
        custom_metadata: Custom metadata dictionary.
        error_message: Error message if any.
        error_code: Error code if any.
        num_preceding_items_org: Queue position within organization.
        num_preceding_items_platform: Queue position across platform.

    Returns:
        RunData: A run data instance with the specified values.
    """
    if statistics is None:
        statistics = make_run_item_statistics()
    if submitted_at is None:
        submitted_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

    return RunData(
        run_id=run_id,
        application_id=application_id,
        version_number=version_number,
        state=state,
        termination_reason=termination_reason,
        output=output,
        statistics=statistics,
        submitted_at=submitted_at,
        submitted_by=submitted_by,
        terminated_at=terminated_at,
        custom_metadata=custom_metadata,
        error_message=error_message,
        error_code=error_code,
        num_preceding_items_org=num_preceding_items_org,
        num_preceding_items_platform=num_preceding_items_platform,
    )


@pytest.fixture
def default_run_data() -> RunData:
    """Provide a default RunData instance for testing.

    Returns:
        RunData: A run data instance with default values.
    """
    return make_run_data()


@pytest.fixture
def terminated_run_data() -> RunData:
    """Provide a terminated RunData instance for testing.

    Returns:
        RunData: A terminated run data instance.
    """
    return make_run_data(
        state=RunState.TERMINATED,
        termination_reason=RunTerminationReason.ALL_ITEMS_PROCESSED,
        output=RunOutput.FULL,
        statistics=make_run_item_statistics(item_count=5, item_succeeded_count=5, item_pending_count=0),
        terminated_at=datetime(2025, 1, 1, 13, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def pending_run_data() -> RunData:
    """Provide a pending RunData instance for testing.

    Returns:
        RunData: A pending run data instance.
    """
    return make_run_data(
        state=RunState.PENDING,
        statistics=make_run_item_statistics(item_count=1, item_pending_count=1, item_succeeded_count=0),
    )
