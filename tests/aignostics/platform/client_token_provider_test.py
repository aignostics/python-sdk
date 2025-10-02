"""Tests for the token provider configuration and its integration with the client."""

from unittest.mock import Mock, patch

from aignostics.platform._client import Client, _OAuth2TokenProviderConfiguration


def test_oauth2_token_provider_configuration_uses_token_provider() -> None:
    """Test that token_provider is used when provided."""
    token_provider = Mock(return_value="dynamic-token")
    config = _OAuth2TokenProviderConfiguration(host="https://dummy", token_provider=token_provider)
    auth = config.auth_settings()
    assert auth["OAuth2AuthorizationCodeBearer"]["value"] == "Bearer dynamic-token"
    token_provider.assert_called_once()


def test_oauth2_token_provider_configuration_no_token() -> None:
    """Test that auth_settings returns empty dict if no token_provider is set."""
    config = _OAuth2TokenProviderConfiguration(host="https://dummy")
    auth = config.auth_settings()
    assert auth == {}


def test_client_passes_token_provider() -> None:
    """Test that the client passes the token provider to the configuration."""
    with (
        patch("aignostics.platform._client.get_token", return_value="client-token"),
        patch("aignostics.platform._client.ApiClient") as api_client_mock,
        patch("aignostics.platform._client.PublicApi") as public_api_mock,
    ):
        Client(cache_token=False)
        config_used = api_client_mock.call_args[0][0]
        assert isinstance(config_used, _OAuth2TokenProviderConfiguration)
        assert config_used.token_provider() == "client-token"
        public_api_mock.assert_called()


def test_client_me_calls_api() -> None:
    """Test that the client.me() method calls the API and returns the result."""
    with (
        patch("aignostics.platform._client.get_token", return_value="client-token"),
        patch("aignostics.platform._client.ApiClient"),
        patch("aignostics.platform._client.PublicApi") as public_api_mock,
    ):
        api_instance = Mock()
        api_instance.get_me_v1_me_get.return_value = "me-info"
        public_api_mock.return_value = api_instance
        client = Client()
        result = client.me()
        assert result == "me-info"
        api_instance.get_me_v1_me_get.assert_called_once()
