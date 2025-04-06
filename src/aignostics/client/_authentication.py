import os
import time
import typing as t
import webbrowser
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse
from urllib.parse import urlparse

import appdirs
import jwt
import requests
from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests_oauthlib import OAuth2Session

from .messages import AUTHENTICATION_FAILED

# Constants
CLIENT_APP_NAME = "python-sdk"

CACHE_DIR = appdirs.user_cache_dir(CLIENT_APP_NAME, "aignostics")
TOKEN_FILE = Path(CACHE_DIR) / ".token"
ENV_FILE = os.getenv("AIGNOSTICS_ENV_FILE", Path.home() / ".aignostics/env")

AUTHORIZATION_BACKOFF_SECONDS = 3
REQUEST_TIMEOUT_SECONDS = 30


# Settings
class AuthenticationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AIGNOSTICS_", env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    client_id_device: SecretStr
    client_id_interactive: SecretStr
    scope: str
    redirect_uri: str
    audience: str
    authorization_base_url: str
    token_url: str
    device_url: str
    jws_json_url: str
    refresh_token: SecretStr | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scope_elements(self) -> list[str]:
        if not self.scope:
            return []
        return [element.strip() for element in self.scope.split(",")]


__cached_authentication_settings: AuthenticationSettings | None = None


def authentication_settings() -> AuthenticationSettings:
    """Lazy load authentication settings from the environment or a file.

    * Given we use Pydantic Settings, validation is done automatically.
    * We only load and validate if we actually need the settings,
        thereby not killing the client on other actions.
    * If the settings have already been loaded, return the cached instance.

    Returns:
        AuthenticationSettings: The loaded authentication settings.
    """
    global __cached_authentication_settings  # noqa: PLW0603
    if __cached_authentication_settings is None:
        __cached_authentication_settings = AuthenticationSettings()  # pyright: ignore[reportCallIssue]
    return __cached_authentication_settings


print(authentication_settings().scope_elements)


def get_token(use_cache: bool = True) -> str:
    """Retrieves an authentication token, either from cache or via login.

    Args:
        use_cache: Boolean indicating whether to store & use the token from disk cache.
            Defaults to True.

    Returns:
        str: The JWT access token.

    Raises:
        RuntimeError: If token retrieval fails.
    """
    if use_cache and TOKEN_FILE.exists():
        stored_token = Path(TOKEN_FILE).read_text(encoding="utf-8")
        # Parse stored string "token:expiry_timestamp"
        parts = stored_token.split(":")
        token, expiry_str = parts
        expiry = datetime.fromtimestamp(int(expiry_str), tz=UTC)

        # Check if token is still valid (with some buffer time)
        if datetime.now(tz=UTC) + timedelta(minutes=5) < expiry:
            return token

    # If we end up here, we:
    # 1. Do not want to use the cached token
    # 2. The cached token is expired
    # 3. No token was cached yet
    new_token = _authenticate()
    claims = verify_and_decode_token(new_token)

    # Store new token with expiry
    if use_cache:
        timestamp = claims["exp"]
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        Path(TOKEN_FILE).write_text(f"{new_token}:{timestamp}", encoding="utf-8")

    return new_token


def verify_and_decode_token(token: str) -> dict[str, str]:
    """
    Verifies and decodes the JWT token using the public key from JWS JSON URL.

    Args:
        token: The JWT token to verify and decode.

    Returns:
        dict: The decoded token claims.

    Raises:
        RuntimeError: If token verification or decoding fails.
    """
    jwk_client = jwt.PyJWKClient(authentication_settings().jws_json_url)
    try:
        # Get the public key from the JWK client
        key = jwk_client.get_signing_key_from_jwt(token).key
        # Get the algorithm from the token header
        binary_token = token.encode("ascii")
        header_data = jwt.get_unverified_header(binary_token)
        algorithm = header_data["alg"]
        # Verify and decode the token using the public key
        return t.cast(
            # TODO(Andreas): hhva: Are we missing error handilng in case jwt.decode fails given invalid token?
            "dict[str, str]",
            jwt.decode(binary_token, key=key, algorithms=[algorithm], audience=authentication_settings().audience),
        )
    except jwt.exceptions.PyJWKClientError as e:
        msg = AUTHENTICATION_FAILED
        raise RuntimeError(msg) from e
    except jwt.exceptions.DecodeError as e:
        msg = AUTHENTICATION_FAILED
        raise RuntimeError(msg) from e


def _authenticate() -> str:
    """Allows the user to login and obtain an access token.

    Determines the appropriate authentication flow based on whether
    a browser can be opened, then executes that flow.

    Returns:
        str: The JWT access token.

    Raises:
        RuntimeError: If authentication fails.
        AssertionError: If the returned token doesn't have the expected format.
    """
    if refresh_token := authentication_settings().refresh_token:
        token = _token_from_refresh_token(refresh_token.get_secret_value())
    elif _can_open_browser():
        token = _perform_authorization_code_with_pkce_flow()
    else:
        token = _perform_device_flow()
    if not token:
        raise RuntimeError(AUTHENTICATION_FAILED)
    return token


def _can_open_browser() -> bool:
    """Checks if a browser can be opened for authentication.

    Returns:
        bool: True if a browser can be opened, False otherwise.
    """
    launch_browser = False
    try:
        _ = webbrowser.get()
        launch_browser = True
    except webbrowser.Error:
        launch_browser = False

    return launch_browser


class _OAuthHttpServer(HTTPServer):
    """HTTP server for OAuth authorization code flow.

    Extends HTTPServer to store the authorization code received during OAuth flow.
    """

    # TODO(Andreas): hhva: HTTPServer.init expects particular args, guess you want to have them there
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initializes the server with storage for the authorization code.

        Args:
            *args: Variable length argument list passed to parent.
            **kwargs: Arbitrary keyword arguments passed to parent.
        """
        HTTPServer.__init__(self, *args, **kwargs)
        self.authorization_code = ""


class _OAuthHttpHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth authorization code flow.

    Processes the OAuth callback redirect and extracts the authorization code.
    """

    def do_GET(self) -> None:  # noqa: N802
        """Handles GET requests containing OAuth response parameters.

        Extracts authorization code or error from the URL and updates the server state.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        parsed = parse.urlparse(self.path)
        qs = parse.parse_qs(parsed.query)

        response = b"""
        <script type="application/javascript">setTimeout(function() { window.close(); }, 1000);</script>
        {status}
        """

        # see if auth was successful
        # TODO(Andreas): The base server does not have .error or .error_description. Was this tested?
        if "error" in qs:
            self.server.error = qs["error"][0]  # type: ignore[attr-defined]
            self.server.error_description = qs["error_description"][0]  # type: ignore[attr-defined]
            status = b"Authentication error"
        else:
            self.server.error = None  # type: ignore[attr-defined]
            self.server.authorization_code = qs["code"][0]  # type: ignore[attr-defined]
            status = b"Authentication successful"

        # display status in browser and close tab after 2 seconds
        response = b"""
        <script type="application/javascript">setTimeout(function() { window.close(); }, 1000);</script>
        """
        self.wfile.write(response + status)

    # TODO(Andreas): Implement and fix typing
    def log_message(self, _format: str, *args) -> None:  # type: ignore[no-untyped-def]
        """Suppresses log messages from the HTTP server.

        Args:
            _format: The log message format string.
            *args: The arguments to be applied to the format string.
        """


def _perform_authorization_code_with_pkce_flow() -> str:
    """Performs the OAuth 2.0 Authorization Code flow with PKCE.

    Opens a browser for user authentication and uses a local redirect
    to receive the authorization code.

    Returns:
        str: The JWT access token.

    Raises:
        RuntimeError: If authentication fails.
    """
    parsed_redirect = urlparse(authentication_settings().redirect_uri)
    with _OAuthHttpServer((parsed_redirect.hostname, parsed_redirect.port), _OAuthHttpHandler) as httpd:
        # initialize flow (generate code_challenge and code_verifier)
        session = OAuth2Session(
            authentication_settings().client_id_interactive.get_secret_value(),
            scope=authentication_settings().scope_elements,
            redirect_uri=authentication_settings().redirect_uri,
            pkce="S256",
        )
        authorization_url, _ = session.authorization_url(
            authentication_settings().authorization_base_url,
            access_type="offline",
            audience=authentication_settings().audience,
        )

        # Call Auth0 with challenge and redirect to localhost with code after successful authN
        webbrowser.open_new(authorization_url)

        # extract authorization_code from redirected request
        httpd.handle_request()

        auth_code = httpd.authorization_code

        # exchange authorization_code against access token at Auth0 (prove identity with code_verifier)
        token_response = session.fetch_token(
            authentication_settings().token_url, code=auth_code, include_client_id=True
        )
        # TODO(Andreas): hhva: Validate response
        return t.cast("str", token_response["access_token"])


def _perform_device_flow() -> str | None:
    """Performs the OAuth 2.0 Device Authorization flow.

    Used when a browser cannot be opened. Provides a URL for the user to visit
    on another device and polls for authorization completion.

    Returns:
        str: The JWT access token.

    Raises:
        RuntimeError: If authentication fails or is denied.
    """
    # TODO(Andreas): hhva: Validate response. How about using Pydantic here?
    resp: dict[str, str] = requests.post(
        authentication_settings().device_url,
        data={
            "client_id": authentication_settings().client_id_device.get_secret_value(),
            "scope": authentication_settings().scope_elements,
            "audience": authentication_settings().audience,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    ).json()
    device_code = resp["device_code"]
    print(f"Please visit: {resp['verification_uri_complete']}")

    # Polling for access token with received device code
    while True:
        # TODO(Andreas): hhva: Validate response. How about using Pydantic here?
        resp = requests.post(
            authentication_settings().token_url,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": authentication_settings().client_id_device.get_secret_value(),
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        ).json()

        if "error" in resp:
            if resp["error"] in {"authorization_pending", "slow_down"}:
                time.sleep(3)
                continue
            raise RuntimeError(resp["error"])
        return resp["access_token"]


def _token_from_refresh_token(refresh_token: str) -> str | None:
    """Obtains a new access token using a refresh token.

    Args:
        refresh_token: The refresh token to use for obtaining a new access token.

    Returns:
        str: The new JWT access token.

    Raises:
        RuntimeError: If token refresh fails.
    """
    while True:
        resp = requests.post(
            authentication_settings().token_url,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "refresh_token",
                "client_id": authentication_settings().client_id_interactive.get_secret_value,
                "refresh_token": refresh_token,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        ).json()
        if "error" in resp:
            if resp["error"] in {"authorization_pending", "slow_down"}:
                time.sleep(AUTHORIZATION_BACKOFF_SECONDS)
                continue
            raise RuntimeError(resp["error"])
        return t.cast("str", resp["access_token"])


if __name__ == "__main__":
    print(get_token(use_cache=False))
