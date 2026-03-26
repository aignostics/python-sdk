"""Tests for the token provider configuration and its integration with the client."""

from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest

from aignostics.platform._api import _AuthenticatedApi, _AuthenticatedResource, _OAuth2TokenProviderConfiguration
from aignostics.platform._client import Client

# Module-level constants for repeated string literals (extracted to satisfy
# SonarQube python:S1192 — "Define a constant instead of duplicating this literal").
# These are unittest.mock.patch() targets (Python module paths), not credentials.
# The noqa on _GET_TOKEN_PATCH is needed because ruff's hardcoded-password
# detector (S105) treats any constant whose name contains "TOKEN" as a credential —
# a false positive for a patch-target string. The bare `# noqa: S105` form keeps
# the suppression syntactically valid for SonarQube python:S7632.
_DUMMY_HOST = "https://dummy"
_GET_TOKEN_PATCH = "aignostics.platform._client.get_token"  # noqa: S105
_APICLIENT_PATCH = "aignostics.platform._client.ApiClient"


@pytest.fixture(autouse=True)
def _clear_api_client_cache() -> None:
    """Clear the API client cache before each test to ensure test isolation."""
    Client._api_client_cached = None
    Client._api_client_uncached = None
    Client._api_client_external.clear()


def _make_provider(token: str) -> Callable[[], str]:
    """Create a token provider that returns the given token string."""

    def provider() -> str:
        return token

    return provider


@pytest.mark.unit
def test_oauth2_token_provider_configuration_uses_token_provider() -> None:
    """Test that token_provider is used when provided."""
    token_provider = Mock(return_value="dynamic-token")
    config = _OAuth2TokenProviderConfiguration(host=_DUMMY_HOST, token_provider=token_provider)
    auth = config.auth_settings()
    assert auth["OAuth2AuthorizationCodeBearer"]["value"] == "Bearer dynamic-token"
    token_provider.assert_called_once()


@pytest.mark.unit
def test_oauth2_token_provider_configuration_no_token() -> None:
    """Test that auth_settings returns empty dict if no token_provider is set."""
    config = _OAuth2TokenProviderConfiguration(host=_DUMMY_HOST)
    auth = config.auth_settings()
    assert auth == {}


@pytest.mark.unit
def test_client_passes_token_provider() -> None:
    """Test that the client passes the token provider to the configuration."""
    with (
        patch(_GET_TOKEN_PATCH, return_value="client-token"),
        patch(_APICLIENT_PATCH) as api_client_mock,
    ):
        Client(cache_token=False)
        config_used = api_client_mock.call_args[0][0]
        assert isinstance(config_used, _OAuth2TokenProviderConfiguration)
        assert config_used.token_provider() == "client-token"


@pytest.mark.unit
def test_client_me_calls_api() -> None:
    """Test that the client.me() method calls the API and returns the result."""
    with (
        patch(_GET_TOKEN_PATCH, return_value="client-token"),
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None) as _,
    ):
        client = Client()
        # Manually set up the mock api on the client
        api_instance = Mock()
        api_instance.get_me_v1_me_get.return_value = "me-info"
        api_instance.token_provider = lambda: "client-token"
        client._api = api_instance
        result = client.me()
        assert result == "me-info"
        api_instance.get_me_v1_me_get.assert_called_once()


# --- External token provider tests ---


@pytest.mark.unit
def test_client_with_external_token_provider() -> None:
    """Test that Client accepts an external token provider and initializes successfully."""
    my_provider = _make_provider("my-m2m-token")

    with (
        patch(_APICLIENT_PATCH) as api_client_mock,
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        Client(token_provider=my_provider)

        # Verify the config received the external provider
        config_used = api_client_mock.call_args[0][0]
        assert isinstance(config_used, _OAuth2TokenProviderConfiguration)
        assert config_used.token_provider is my_provider


@pytest.mark.unit
def test_external_provider_bypasses_oauth() -> None:
    """Test that get_token is NOT called when an external token provider is used."""
    my_provider = _make_provider("external-token")

    with (
        patch(_GET_TOKEN_PATCH) as mock_get_token,
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        Client(token_provider=my_provider)
        mock_get_token.assert_not_called()


@pytest.mark.unit
def test_external_provider_token_in_auth_header() -> None:
    """Test that the external provider's token appears in the Authorization header."""
    my_provider = _make_provider("bearer-value-123")

    with (
        patch(_APICLIENT_PATCH) as api_client_mock,
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        Client(token_provider=my_provider)
        config_used = api_client_mock.call_args[0][0]
        auth = config_used.auth_settings()
        assert auth["OAuth2AuthorizationCodeBearer"]["value"] == "Bearer bearer-value-123"


@pytest.mark.unit
def test_external_provider_singleton_isolation() -> None:
    """Test that different providers get different API client instances."""
    provider_a = _make_provider("token-a")
    provider_b = _make_provider("token-b")

    with (
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        client_a = Client(token_provider=provider_a)
        client_b = Client(token_provider=provider_b)

        assert client_a._api is not client_b._api


@pytest.mark.unit
def test_external_provider_same_provider_reused() -> None:
    """Test that the same provider callable reuses the cached API client."""
    my_provider = _make_provider("reuse-token")

    with (
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        client1 = Client(token_provider=my_provider)
        client2 = Client(token_provider=my_provider)

        assert client1._api is client2._api


@pytest.mark.unit
def test_cache_token_false_with_external_provider_is_allowed() -> None:
    """Test that cache_token=False is silently ignored when token_provider is set."""
    with (
        patch(_GET_TOKEN_PATCH) as mock_get_token,
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        # Should not raise; cache_token is irrelevant when using an external provider
        Client(token_provider=_make_provider("token"), cache_token=False)
        mock_get_token.assert_not_called()


@pytest.mark.unit
def test_cache_token_default_with_external_provider_ok() -> None:
    """Test that default cache_token=True works with an external token provider."""
    with (
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
    ):
        # Should not raise
        Client(token_provider=_make_provider("token"))


@pytest.mark.unit
def test_falsy_token_provider_logs_warning() -> None:
    """Test that a warning is logged when token_provider returns an empty string."""
    empty_provider = _make_provider("")
    config = _OAuth2TokenProviderConfiguration(host=_DUMMY_HOST, token_provider=empty_provider)

    with patch("aignostics.platform._api.logger") as mock_logger:
        result = config.auth_settings()

    assert result == {}
    mock_logger.warning.assert_called_once()
    warning_msg = mock_logger.warning.call_args[0][0]
    assert "empty or None token" in warning_msg


@pytest.mark.unit
def test_none_token_provider_no_warning() -> None:
    """Test that no warning is logged when token_provider is not set (None)."""
    config = _OAuth2TokenProviderConfiguration(host=_DUMMY_HOST)

    with patch("aignostics.platform._api.logger") as mock_logger:
        result = config.auth_settings()

    assert result == {}
    mock_logger.warning.assert_not_called()


@pytest.mark.unit
def test_external_provider_cache_bounded() -> None:
    """Test that _api_client_external is bounded to _MAX_EXTERNAL_CLIENTS entries."""
    from aignostics.platform._client import _MAX_EXTERNAL_CLIENTS

    with (
        patch(_APICLIENT_PATCH),
        patch.object(_AuthenticatedApi, "__init__", lambda self, *a, **kw: None),
        patch("aignostics.platform._client.logger") as mock_logger,
    ):
        # Create more clients than the limit, each with a distinct provider
        for i in range(_MAX_EXTERNAL_CLIENTS + 5):
            Client(token_provider=_make_provider(f"token-{i}"))

        # Cache must not exceed the limit (cleared + 1 new entry after overflow)
        assert len(Client._api_client_external) <= _MAX_EXTERNAL_CLIENTS

        # A warning should have been logged when the cache was cleared
        mock_logger.warning.assert_called()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "resource leak" in warning_msg


# --- Integration tests ---


@pytest.mark.integration
def test_external_provider_wires_through_to_resources() -> None:
    """Integration: Client(token_provider=...) wires through real constructors.

    Verifies that an external token provider flows through Client → _AuthenticatedApi →
    resource classes (Applications, Runs) without any AttributeError.  Only the
    ApiClient constructor is mocked to avoid real HTTP calls.
    """
    my_provider = _make_provider("integration-test-token")

    with patch(_APICLIENT_PATCH) as mock_api_client_cls:
        # Create client with external provider — real _AuthenticatedApi and
        # resource constructors (_AuthenticatedResource.__init__) run.
        client = Client(token_provider=my_provider)

        # Verify the provider is wired through the real _AuthenticatedApi
        assert isinstance(client._api, _AuthenticatedApi)
        assert client._api.token_provider is my_provider

        # Verify resources received the same _AuthenticatedApi instance
        assert client.applications._api is client._api
        assert client.runs._api is client._api
        assert client.versions._api is client._api

        # Verify the Configuration passed to ApiClient produces the correct auth header
        config = mock_api_client_cls.call_args[0][0]
        assert isinstance(config, _OAuth2TokenProviderConfiguration)
        auth = config.auth_settings()
        assert auth["OAuth2AuthorizationCodeBearer"]["value"] == "Bearer integration-test-token"


# --- Runtime guard tests ---


@pytest.mark.unit
def test_authenticated_resource_rejects_non_authenticated_api() -> None:
    """`_AuthenticatedResource.__init__` raises TypeError for non-`_AuthenticatedApi` inputs.

    The runtime guard exists to catch callers that bypass `Client` and construct
    resource classes directly with a plain codegen `PublicApi` (or any other object
    lacking `token_provider`). Without this guard, the `AttributeError` would only
    surface much later at the first cached call site, with a confusing message.
    """

    class NotAnAuthenticatedApi:
        """Stand-in for a plain `PublicApi` or arbitrary object."""

    with pytest.raises(TypeError, match="requires _AuthenticatedApi"):
        _AuthenticatedResource(NotAnAuthenticatedApi())  # type: ignore[arg-type]


@pytest.mark.unit
def test_authenticated_resource_accepts_authenticated_api() -> None:
    """`_AuthenticatedResource.__init__` stores the api and exposes it as `_api`."""
    api = Mock(spec=_AuthenticatedApi)
    resource = _AuthenticatedResource(api)
    assert resource._api is api
