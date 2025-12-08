"""Shared fixtures for platform tests."""

import typing as t
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from aignx.codegen.models import RunItemStatistics, RunOutput, RunReadResponse, RunState, RunTerminationReason

from aignostics.platform._client import Client
from aignostics.platform._operation_cache import _operation_cache


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


def make_run_read_response(
    run_id: str = "test-run-id",
    application_id: str = "he-tme",
    version_number: str = "1.0.0",
    state: RunState = RunState.PENDING,
    output: RunOutput = RunOutput.NONE,
    termination_reason: RunTerminationReason | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    statistics: RunItemStatistics | None = None,
    custom_metadata: dict | None = None,
    custom_metadata_checksum: str | None = None,
    submitted_at: datetime | None = None,
    submitted_by: str = "user@example.com",
    terminated_at: datetime | None = None,
    num_preceding_items_org: int | None = None,
    num_preceding_items_platform: int | None = None,
) -> RunReadResponse:
    """Create a RunReadResponse instance with sensible defaults.

    Args:
        run_id: The run ID.
        application_id: The application ID.
        version_number: The version number.
        state: The run state.
        output: The output status.
        termination_reason: The termination reason.
        error_code: Error code if any.
        error_message: Error message if any.
        statistics: The item statistics (defaults to single pending item).
        custom_metadata: Custom metadata dictionary.
        custom_metadata_checksum: Checksum of custom metadata.
        submitted_at: When the run was submitted.
        submitted_by: Who submitted the run.
        terminated_at: When the run terminated.
        num_preceding_items_org: Queue position within organization.
        num_preceding_items_platform: Queue position across platform.

    Returns:
        RunReadResponse: A run read response with the specified values.
    """
    if statistics is None:
        statistics = make_run_item_statistics()
    if submitted_at is None:
        submitted_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

    return RunReadResponse(
        run_id=run_id,
        application_id=application_id,
        version_number=version_number,
        state=state,
        output=output,
        termination_reason=termination_reason,
        error_code=error_code,
        error_message=error_message,
        statistics=statistics,
        custom_metadata=custom_metadata,
        custom_metadata_checksum=custom_metadata_checksum,
        submitted_at=submitted_at,
        submitted_by=submitted_by,
        terminated_at=terminated_at,
        num_preceding_items_org=num_preceding_items_org,
        num_preceding_items_platform=num_preceding_items_platform,
    )


@pytest.fixture
def mock_settings() -> MagicMock:
    """Provide a mock of settings for testing.

    Yields:
        MagicMock: A mock of the settings.
    """
    with patch("aignostics.platform._client.settings") as mock_settings:
        settings = MagicMock()
        settings.me_retry_attempts = 3
        settings.me_retry_wait_min = 0.1
        settings.me_retry_wait_max = 5.0
        settings.me_timeout = 10.0
        settings.me_cache_ttl = 60  # 60 seconds for testing
        settings.application_retry_attempts = 3
        settings.application_retry_wait_min = 0.1
        settings.application_retry_wait_max = 5.0
        settings.application_timeout = 10.0
        settings.application_cache_ttl = 300  # 5 minutes
        settings.application_version_retry_attempts = 3
        settings.application_version_retry_wait_min = 0.1
        settings.application_version_retry_wait_max = 5.0
        settings.application_version_timeout = 10.0
        settings.application_version_cache_ttl = 300  # 5 minutes
        settings.run_retry_attempts = 3
        settings.run_retry_wait_min = 0.1
        settings.run_retry_wait_max = 5.0
        settings.run_timeout = 10.0
        settings.run_cache_ttl = 15  # 15 seconds
        settings.api_root = "https://test.api.com"
        mock_settings.return_value = settings
        yield mock_settings


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Provide a mock API client.

    Returns:
        MagicMock: A mock of the PublicApi client.
    """
    return MagicMock()


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear the operation cache before each test.

    This ensures tests don't interfere with each other through shared cache state.
    """
    _operation_cache.clear()


@pytest.fixture
def client_with_mock_api(mock_api_client: MagicMock) -> t.Generator[Client, None, None]:
    """Provide a Client instance with a mocked API client.

    Args:
        mock_api_client: The mocked API client.

    Yields:
        Client: A client instance with mocked API.
    """
    mock_token_claims = {
        "sub": "test-user",
        "org_id": "test-org",
        "exp": 9999999999,
        "iss": "test-issuer",
    }
    with (
        patch("aignostics.platform._client.get_token", return_value="test-token-123"),
        patch("aignostics.platform._authentication.verify_and_decode_token", return_value=mock_token_claims),
        patch("aignostics.platform._client.Client.get_api_client", return_value=mock_api_client),
    ):
        client = Client(cache_token=False)
        client._api = mock_api_client
        yield client


@pytest.fixture
def clear_jwk_cache() -> t.Generator[None, None, None]:
    """Clear the JWK client cache before and after each test.

    This fixture ensures the cache is always cleaned up, even if assertions fail.
    Use this fixture by adding it as a parameter to tests that interact with JWT verification.

    Yields:
        None: This fixture doesn't yield a value.
    """
    from aignostics.platform._authentication import _get_jwk_client

    _get_jwk_client.cache_clear()
    yield
    _get_jwk_client.cache_clear()
