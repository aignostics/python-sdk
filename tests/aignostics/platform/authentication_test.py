"""Tests for the authentication module of the Aignostics Python SDK."""

import socket
import time
import webbrowser
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import jwt
import pytest
from pydantic import SecretStr
from requests_oauthlib import OAuth2Session

from aignostics.platform._authentication import (
    _authenticate,
    _can_open_browser,
    _ensure_local_port_is_available,
    _perform_authorization_code_with_pkce_flow,
    _perform_device_flow,
    get_token,
    remove_cached_token,
    verify_and_decode_token,
)
from aignostics.platform._messages import AUTHENTICATION_FAILED, INVALID_REDIRECT_URI


@pytest.fixture
def mock_settings() -> MagicMock:
    """Provide a mock of authentication settings for testing.

    Yields:
        MagicMock: A mock of the authentication settings.
    """
    with patch("aignostics.platform._authentication.settings") as mock_settings:
        settings = MagicMock()
        # Using tmp_path in a controlled test environment is acceptable for testing
        settings.token_file = Path("mock_token_path")  # Avoid hardcoded /tmp path
        settings.client_id_interactive = SecretStr("test-interactive-platform-id")
        settings.client_id_device = SecretStr("test-device-platform-id")
        settings.scope_elements = "openid profile"
        settings.redirect_uri = "http://localhost:8989/callback"
        settings.authorization_base_url = "https://test.auth/authorize"
        settings.token_url = "https://test.auth/token"  # noqa: S105 - Test credential
        settings.device_url = "https://test.auth/device"
        settings.audience = "test-audience"
        settings.jws_json_url = "https://test.auth/.well-known/jwks.json"
        settings.request_timeout_seconds = 10
        settings.refresh_token = None
        mock_settings.return_value = settings
        yield mock_settings


@pytest.fixture
def mock_token_file(tmp_path) -> Path:
    """Create a temporary token file for testing."""
    return tmp_path / "token"  # Return directly, no need for assignment


@pytest.fixture
def valid_token() -> str:
    """Return a dummy valid token for testing."""
    return "valid.jwt.token"


@pytest.fixture
def expired_token() -> str:
    """Return a dummy expired token for testing."""
    # Token that is expired
    expired_time = int((datetime.now(tz=UTC) - timedelta(hours=1)).timestamp())
    return f"expired.jwt.token:{expired_time}"


@pytest.fixture
def valid_token_with_expiry() -> str:
    """Return a dummy valid token with future expiry for testing."""
    # Token that is still valid with future expiry
    future_time = int((datetime.now(tz=UTC) + timedelta(hours=1)).timestamp())
    return f"valid.jwt.token:{future_time}"


# Always force _can_open_browser to return False in tests to prevent browser opening
@pytest.fixture(autouse=True)
def mock_can_open_browser() -> None:
    """Mock browser capability to always return False to prevent actual browser opening.

    Yields:
        None: This fixture doesn't yield a value.
    """
    with patch("aignostics.platform._authentication._can_open_browser", return_value=False):
        yield


# Prevent real webbrowser from opening in any test
@pytest.fixture(autouse=True)
def mock_webbrowser() -> MagicMock:
    """Mock webbrowser.open_new to prevent actual browser from opening during tests.

    Yields:
        MagicMock: The mocked webbrowser.open_new function.
    """
    with patch("webbrowser.open_new") as mock_open:
        yield mock_open


class TestGetToken:
    """Test cases for the get_token function."""

    @staticmethod
    def test_get_token_from_cache_valid(mock_settings, valid_token_with_expiry) -> None:
        """Test retrieving a valid token from cache."""
        # Create a mock for Path that can be properly asserted on
        mock_write_text = MagicMock()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "read_text", return_value=valid_token_with_expiry),
            patch.object(Path, "write_text", mock_write_text),
        ):
            token = get_token(use_cache=True)
            assert token == "valid.jwt.token"  # noqa: S105 - Test credential
            # Ensure we didn't need to authenticate
            mock_write_text.assert_not_called()

    @staticmethod
    def test_get_token_from_cache_expired(mock_settings, expired_token) -> None:
        """Test retrieving an expired token from cache, which should trigger re-authentication."""
        # Create a mock for Path that can be properly asserted on
        mock_write_text = MagicMock()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "read_text", return_value=expired_token),
            patch("aignostics.platform._authentication._authenticate", return_value="new.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                return_value={"exp": int(time.time()) + 3600},
            ),
            patch.object(Path, "write_text", mock_write_text),
        ):
            token = get_token(use_cache=True)
            assert token == "new.token"  # noqa: S105 - Test credential
            # Ensure we wrote the new token
            assert mock_write_text.call_count == 1

    @staticmethod
    def test_get_token_no_cache(mock_settings) -> None:
        """Test retrieving a token without using cache."""
        # Create a mock for Path that can be properly asserted on
        mock_write_text = MagicMock()

        with (
            patch("aignostics.platform._authentication._authenticate", return_value="new.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                return_value={"exp": int(time.time()) + 3600},
            ),
            patch.object(Path, "write_text", mock_write_text),
        ):
            token = get_token(use_cache=False)
            assert token == "new.token"  # noqa: S105 - Test credential
            # Ensure we didn't write to cache
            mock_write_text.assert_not_called()

    @staticmethod
    def test_authenticate_uses_refresh_token_when_available(mock_settings) -> None:
        """Test that _authenticate uses refresh token flow when refresh token is available."""
        # Set up refresh token in settings
        mock_settings.return_value.refresh_token = SecretStr("test-refresh-token")

        with patch(
            "aignostics.platform._authentication._token_from_refresh_token", return_value="refreshed.token"
        ) as mock_refresh:
            token = _authenticate(use_device_flow=False)
            assert token == "refreshed.token"  # noqa: S105 - Test credential
            mock_refresh.assert_called_once_with(mock_settings.return_value.refresh_token)

    @staticmethod
    def test_authenticate_uses_browser_flow_when_available(mock_settings) -> None:
        """Test that _authenticate uses browser flow when browser is available."""
        mock_settings.return_value.refresh_token = None

        with (
            patch("aignostics.platform._authentication._can_open_browser", return_value=True),
            patch(
                "aignostics.platform._authentication._perform_authorization_code_with_pkce_flow",
                return_value="browser.token",
            ) as mock_browser,
        ):
            token = _authenticate(use_device_flow=False)
            assert token == "browser.token"  # noqa: S105 - Test credential
            mock_browser.assert_called_once()

    @staticmethod
    def test_authenticate_falls_back_to_device_flow(mock_settings) -> None:
        """Test that _authenticate falls back to device flow when browser and refresh token are unavailable."""
        mock_settings.return_value.refresh_token = None

        with (
            patch("aignostics.platform._authentication._can_open_browser", return_value=False),
            patch(
                "aignostics.platform._authentication._perform_device_flow", return_value="device.token"
            ) as mock_device,
        ):
            token = _authenticate(use_device_flow=True)
            assert token == "device.token"  # noqa: S105 - Test credential
            mock_device.assert_called_once()

    @staticmethod
    def test_authenticate_raises_error_on_failure(mock_settings) -> None:
        """Test that _authenticate raises an error when all authentication methods fail."""
        mock_settings.return_value.refresh_token = None

        with (
            patch("aignostics.platform._authentication._can_open_browser", return_value=False),
            patch("aignostics.platform._authentication._perform_device_flow", return_value=None),
            pytest.raises(RuntimeError, match=AUTHENTICATION_FAILED),
        ):
            _authenticate(use_device_flow=True)


class TestVerifyAndDecodeToken:
    """Test cases for the verify_and_decode_token function."""

    @staticmethod
    def test_verify_and_decode_valid_token() -> None:
        """Test that a valid token is properly verified and decoded."""
        mock_jwt_client = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = "test-key"
        mock_jwt_client.get_signing_key_from_jwt.return_value = mock_signing_key

        with (
            patch("jwt.PyJWKClient", return_value=mock_jwt_client),
            patch("jwt.get_unverified_header", return_value={"alg": "RS256"}),
            patch("jwt.decode", return_value={"sub": "user-id", "exp": int(time.time()) + 3600}),
        ):
            result = verify_and_decode_token("valid.token")
            assert "sub" in result
            assert "exp" in result

    @staticmethod
    def test_verify_and_decode_invalid_token() -> None:
        """Test that an invalid token raises an appropriate error."""
        with (
            patch("jwt.PyJWKClient"),
            patch("jwt.get_unverified_header"),
            patch("jwt.decode", side_effect=jwt.exceptions.PyJWTError("Invalid token")),
            pytest.raises(RuntimeError, match=AUTHENTICATION_FAILED),
        ):
            verify_and_decode_token("invalid.token")


class TestBrowserCapabilityCheck:
    """Test cases for the browser capability check functionality."""

    @staticmethod
    def test_can_open_browser_true() -> None:
        """Test that _can_open_browser returns True when a browser is available."""
        # We need to override the autouse fixture here
        with (
            patch("webbrowser.get", return_value=MagicMock()),
            patch("aignostics.platform._authentication._can_open_browser", wraps=_can_open_browser),
        ):
            assert _can_open_browser() is True

    @staticmethod
    def test_can_open_browser_false() -> None:
        """Test that _can_open_browser returns False when no browser is available."""
        with patch("webbrowser.get", side_effect=webbrowser.Error):
            assert _can_open_browser() is False


class TestAuthorizationCodeFlow:
    """Test cases for the authorization code flow with PKCE."""

    @staticmethod
    def test_perform_authorization_code_flow_success(mock_settings) -> None:
        """Test successful authorization code flow with PKCE."""
        # Mock OAuth session
        mock_session = MagicMock(spec=OAuth2Session)
        mock_session.authorization_url.return_value = ("https://test.auth/authorize?code_challenge=abc", None)
        mock_session.fetch_token.return_value = {"access_token": "pkce.token"}

        # Mock HTTP server
        mock_server = MagicMock()

        # Setup mocks for the redirect URI parsing
        mock_redirect_parsed = MagicMock()
        mock_redirect_parsed.hostname = "localhost"
        mock_redirect_parsed.port = 8000

        # Create a custom HTTPServer mock implementation that simulates a callback
        class MockHTTPServer:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def __enter__(self) -> MagicMock:
                return mock_server

            def __exit__(self, *args) -> None:
                pass

        # Create a mock for the auth result
        mock_auth_result = MagicMock()
        mock_auth_result.token = "pkce.token"  # noqa: S105 - Test credential
        mock_auth_result.error = None

        with (
            patch("aignostics.platform._authentication.OAuth2Session", return_value=mock_session),
            patch("aignostics.platform._authentication.HTTPServer", MockHTTPServer),
            patch("urllib.parse.urlparse", return_value=mock_redirect_parsed),
            patch("aignostics.platform._authentication.AuthenticationResult", return_value=mock_auth_result),
        ):
            # Simulate a successful server response by making handle_request set the token
            def handle_request_side_effect():
                # This simulates what the HTTP handler would do on success
                mock_auth_result.token = "pkce.token"  # noqa: S105 - Test credential

            mock_server.handle_request.side_effect = handle_request_side_effect

            # Call the function under test
            token = _perform_authorization_code_with_pkce_flow()

            # Assertions
            assert token == "pkce.token"  # noqa: S105 - Test credential
            mock_server.handle_request.assert_called_once()
            mock_session.authorization_url.assert_called_once()

    @staticmethod
    def test_perform_authorization_code_flow_invalid_redirect(mock_settings) -> None:
        """Test authorization code flow fails with invalid redirect URI."""
        # Mock OAuth session to prevent it from being created
        mock_session = MagicMock(spec=OAuth2Session)
        mock_session.authorization_url.return_value = ("https://test.auth/authorize?code_challenge=abc", None)

        with patch("aignostics.platform._authentication.OAuth2Session", return_value=mock_session):
            # Create a mock redirect URI with invalid hostname/port
            mock_redirect_parsed = MagicMock()
            mock_redirect_parsed.hostname = None  # Invalid hostname
            mock_redirect_parsed.port = None  # Invalid port

            with (
                patch("urllib.parse.urlparse", return_value=mock_redirect_parsed),
                pytest.raises(RuntimeError, match=INVALID_REDIRECT_URI),
            ):
                _perform_authorization_code_with_pkce_flow()

    @staticmethod
    def test_perform_authorization_code_flow_failure(mock_settings) -> None:
        """Test authorization code flow when authentication fails."""
        # Mock OAuth session
        mock_session = MagicMock(spec=OAuth2Session)
        mock_session.authorization_url.return_value = ("https://test.auth/authorize?code_challenge=abc", None)

        # Mock HTTP server
        mock_server = MagicMock()

        # Setup mocks for the redirect URI parsing
        mock_redirect_parsed = MagicMock()
        mock_redirect_parsed.hostname = "localhost"
        mock_redirect_parsed.port = 8000

        # Create a custom HTTPServer mock implementation
        class MockHTTPServer:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def __enter__(self) -> MagicMock:
                return mock_server

            def __exit__(self, *args) -> None:
                pass

        # Create a mock for the auth result
        mock_auth_result = MagicMock()
        mock_auth_result.token = None
        mock_auth_result.error = "Authentication failed"

        with (
            patch("aignostics.platform._authentication.OAuth2Session", return_value=mock_session),
            patch("aignostics.platform._authentication.HTTPServer", MockHTTPServer),
            patch("urllib.parse.urlparse", return_value=mock_redirect_parsed),
            patch("aignostics.platform._authentication.AuthenticationResult", return_value=mock_auth_result),
        ):
            # Simulate a failed server response
            def handle_request_side_effect():
                # This simulates what the HTTP handler would do on failure
                mock_auth_result.error = "Authentication failed"
                mock_auth_result.token = None

            mock_server.handle_request.side_effect = handle_request_side_effect

            # Expect RuntimeError with AUTHENTICATION_FAILED message
            with pytest.raises(RuntimeError, match=AUTHENTICATION_FAILED):
                _perform_authorization_code_with_pkce_flow()


class TestDeviceFlow:
    """Test cases for the device flow authentication."""

    @staticmethod
    def test_perform_device_flow_success(mock_settings) -> None:
        """Test successful device flow authentication."""
        device_response = {
            "device_code": "device-code-123",
            "verification_uri_complete": "https://test.auth/device/activate",
            "user_code": "USER123",
            "interval": 5,
        }

        token_response = {"access_token": "device.token"}

        # Create mock responses
        mock_device_response = MagicMock()
        mock_device_response.json.return_value = device_response
        mock_device_response.raise_for_status = MagicMock()

        mock_token_response = MagicMock()
        mock_token_response.json.return_value = token_response

        with (
            patch("requests.post") as mock_post,
            patch("time.sleep") as mock_sleep,
            patch("builtins.print") as mock_print,
        ):
            # Configure mock_post to return different responses for different calls
            mock_post.side_effect = [mock_device_response, mock_token_response]

            # Call the function
            token = _perform_device_flow()

            # Assertions
            assert token == "device.token"  # noqa: S105 - Test credential
            assert mock_post.call_count == 2
            mock_print.assert_called_once()  # Verify we printed instructions
            mock_sleep.assert_not_called()  # We didn't have to poll in our test


class TestPortAvailability:
    """Test cases for checking port availability."""

    @staticmethod
    def test_port_available() -> None:
        """Test that _ensure_local_port_is_available returns True when the port is available."""
        with patch("socket.socket.bind", return_value=None) as mock_bind:
            assert _ensure_local_port_is_available(8000) is True
            mock_bind.assert_called_once()

    @staticmethod
    def test_port_unavailable() -> None:
        """Test that _ensure_local_port_is_available returns False when the port is unavailable."""
        with patch("socket.socket.bind", side_effect=socket.error) as mock_bind:
            assert _ensure_local_port_is_available(8000) is False
            mock_bind.assert_called()

    @staticmethod
    def test_port_retries() -> None:
        """Test that _ensure_local_port_is_available retries the specified number of times."""
        with patch("socket.socket.bind", side_effect=socket.error) as mock_bind, patch("time.sleep") as mock_sleep:
            assert _ensure_local_port_is_available(8000, max_retries=3) is False
            assert mock_bind.call_count == 4  # Initial attempt + 3 retries
            assert mock_sleep.call_count == 3


class TestRemoveCachedToken:
    """Test cases for the remove_cached_token function."""

    @staticmethod
    def test_remove_cached_token_exists(mock_settings) -> None:
        """Test removing a cached token when the token file exists."""
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "unlink") as mock_unlink,
        ):
            result = remove_cached_token()

            assert result is True
            mock_unlink.assert_called_once_with(missing_ok=True)

    @staticmethod
    def test_remove_cached_token_not_exists(mock_settings) -> None:
        """Test removing a cached token when the token file does not exist."""
        with patch.object(Path, "exists", return_value=False):
            result = remove_cached_token()

            assert result is False

    @staticmethod
    def test_remove_cached_token_unlink_error(mock_settings) -> None:
        """Test that remove_cached_token handles unlink errors gracefully."""
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "unlink", side_effect=OSError("Permission denied")) as mock_unlink,
            pytest.raises(OSError, match="Permission denied"),
        ):
            remove_cached_token()
            mock_unlink.assert_called_once_with(missing_ok=True)


class TestSentryIntegration:
    """Test cases for Sentry integration in the authentication module."""

    @staticmethod
    def test_get_token_calls_sentry_set_user(mock_settings) -> None:
        """Test that get_token calls sentry_sdk.set_user with correct user information extracted from token claims."""
        # Mock token claims with the required fields
        mock_claims = {
            "sub": "user123",
            "org_id": "org456",
            "aud": "test-audience",
            "test-audience/role": "admin",
            "exp": int(time.time()) + 3600,
        }

        # Create a mock for sentry_sdk
        mock_sentry_sdk = MagicMock()

        with (
            patch("aignostics.platform._authentication.sentry_sdk", mock_sentry_sdk),
            patch("aignostics.platform._authentication._authenticate", return_value="test.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                return_value=mock_claims,
            ),
            patch.object(Path, "exists", return_value=False),  # Force authentication
            patch.object(Path, "write_text"),
        ):
            token = get_token(use_cache=True)

            # Verify the token was returned
            assert token == "test.token"  # noqa: S105 - Test credential

            # Verify sentry_sdk.set_user was called with correct user information
            mock_sentry_sdk.set_user.assert_called_once_with({
                "id": "user123",
                "org_id": "org456",
                "role": "admin",
            })

    @staticmethod
    def test_get_token_sentry_unavailable(mock_settings) -> None:
        """Test that get_token works correctly when sentry_sdk is not available."""
        # Mock token claims
        mock_claims = {
            "sub": "user123",
            "org_id": "org456",
            "aud": "test-audience",
            "test-audience/role": "admin",
            "exp": int(time.time()) + 3600,
        }

        with (
            patch("aignostics.platform._authentication.sentry_sdk", None),  # Simulate sentry_sdk not available
            patch("aignostics.platform._authentication._authenticate", return_value="test.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                return_value=mock_claims,
            ),
            patch.object(Path, "exists", return_value=False),  # Force authentication
            patch.object(Path, "write_text"),
        ):
            token = get_token(use_cache=True)

            # Verify the token was returned successfully even without Sentry
            assert token == "test.token"  # noqa: S105 - Test credential

    @staticmethod
    def test_get_token_sentry_missing_sub_claim(mock_settings) -> None:
        """Test that get_token handles missing 'sub' claim gracefully when informing Sentry."""
        # Mock token claims without 'sub' field
        mock_claims = {
            "org_id": "org456",
            "aud": "test-audience",
            "test-audience/role": "admin",
            "exp": int(time.time()) + 3600,
        }

        # Create a mock for sentry_sdk
        mock_sentry_sdk = MagicMock()

        with (
            patch("aignostics.platform._authentication.sentry_sdk", mock_sentry_sdk),
            patch("aignostics.platform._authentication._authenticate", return_value="test.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                return_value=mock_claims,
            ),
            patch.object(Path, "exists", return_value=False),  # Force authentication
            patch.object(Path, "write_text"),
        ):
            token = get_token(use_cache=True)

            # Verify the token was returned successfully
            assert token == "test.token"  # noqa: S105 - Test credential

            # Verify sentry_sdk.set_user was not called due to missing 'sub' claim
            mock_sentry_sdk.set_user.assert_not_called()

    @staticmethod
    def test_get_token_sentry_handles_token_verification_error(mock_settings) -> None:
        """Test that get_token fails when token verification fails, and Sentry is not informed."""
        # Create a mock for sentry_sdk
        mock_sentry_sdk = MagicMock()

        with (
            patch("aignostics.platform._authentication.sentry_sdk", mock_sentry_sdk),
            patch("aignostics.platform._authentication._authenticate", return_value="test.token"),
            patch(
                "aignostics.platform._authentication.verify_and_decode_token",
                side_effect=RuntimeError("Token verification failed"),
            ),
            patch.object(Path, "exists", return_value=False),  # Force authentication
            patch.object(Path, "write_text"),
            pytest.raises(RuntimeError, match="Token verification failed"),
        ):
            get_token(use_cache=True)

            # Verify sentry_sdk.set_user was not called because authentication failed
            mock_sentry_sdk.set_user.assert_not_called()
