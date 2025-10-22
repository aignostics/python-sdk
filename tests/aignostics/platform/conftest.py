"""Shared fixtures for platform tests."""

import typing as t
from unittest.mock import MagicMock, patch

import pytest

from aignostics.platform._client import Client
from aignostics.platform._operation_cache import _operation_cache


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
