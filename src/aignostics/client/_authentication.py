import os
import time
import webbrowser
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse
from urllib.parse import urlparse

import appdirs
import jwt
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

ENV_FILE = os.getenv("ENV_FILE", Path.home() / ".aignostics/env")
load_dotenv(dotenv_path=ENV_FILE)

CLIENT_ID_DEVICE = os.getenv("CLIENT_ID_DEVICE")
CLIENT_ID_INTERACTIVE = os.getenv("CLIENT_ID_INTERACTIVE")
SCOPE = [scope.strip() for scope in os.getenv("SCOPE").split(",")]
REDIRECT_URI = os.getenv("REDIRECT_URI")

AUDIENCE = os.getenv("AUDIENCE")
AUTHORIZATION_BASE_URL = os.getenv("AUTHORIZATION_BASE_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
DEVICE_URL = os.getenv("DEVICE_URL")

JWS_JSON_URL = os.getenv("JWS_JSON_URL")

# constants for token caching
CLIENT_APP_NAME = "python-sdk"
CACHE_DIR = appdirs.user_cache_dir(CLIENT_APP_NAME, "aignostics")
TOKEN_FILE = Path(CACHE_DIR) / ".token"

AUTHORIZATION_BACKOFF_SECONDS = 3
REQUEST_TIMEOUT_SECONDS = 30


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
    jwk_client = jwt.PyJWKClient(JWS_JSON_URL)
    try:
        # Get the public key from the JWK client
        key = jwk_client.get_signing_key_from_jwt(token).key
        # Get the algorithm from the token header
        binary_token = token.encode("ascii")
        header_data = jwt.get_unverified_header(binary_token)
        algorithm = header_data["alg"]
        # Verify and decode the token using the public key
        return jwt.decode(binary_token, key=key, algorithms=[algorithm], audience=AUDIENCE)
    except jwt.exceptions.PyJWKClientError as e:
        msg = "Authentication failed"
        raise RuntimeError(msg) from e
    except jwt.exceptions.DecodeError as e:
        msg = "Authentication failed"
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
    if refresh_token := os.getenv("AIGNX_REFRESH_TOKEN"):
        token = _token_from_refresh_token(refresh_token)
    elif _can_open_browser():
        token = _perform_authorization_code_with_pkce_flow()
    else:
        token = _perform_device_flow()
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

    def __init__(self, *args, **kwargs) -> None:
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

        response = """
        <script type="application/javascript">setTimeout(function() { window.close(); }, 1000);</script>
        {status}
        """

        # see if auth was successful
        if "error" in qs:
            self.server.error = qs["error"][0]
            self.server.error_description = qs["error_description"][0]
            status = b"Authentication error"
        else:
            self.server.error = None
            self.server.authorization_code = qs["code"][0]
            status = b"Authentication successful"

        # display status in browser and close tab after 2 seconds
        response = b"""
        <script type="application/javascript">setTimeout(function() { window.close(); }, 1000);</script>
        """
        self.wfile.write(response + status)

    def log_message(self, _format: str, *args) -> None:
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
    parsed_redirect = urlparse(REDIRECT_URI)
    with _OAuthHttpServer((parsed_redirect.hostname, parsed_redirect.port), _OAuthHttpHandler) as httpd:
        # initialize flow (generate code_challenge and code_verifier)
        session = OAuth2Session(CLIENT_ID_INTERACTIVE, scope=SCOPE, redirect_uri=REDIRECT_URI, pkce="S256")
        authorization_url, _ = session.authorization_url(
            AUTHORIZATION_BASE_URL, access_type="offline", audience=AUDIENCE
        )

        # Call Auth0 with challenge and redirect to localhost with code after successful authN
        webbrowser.open_new(authorization_url)

        # extract authorization_code from redirected request
        httpd.handle_request()

        auth_code = httpd.authorization_code

        # exchange authorization_code against access token at Auth0 (prove identity with code_verifier)
        token_response = session.fetch_token(TOKEN_URL, code=auth_code, include_client_id=True)
        return token_response["access_token"]


def _perform_device_flow() -> str | None:
    """Performs the OAuth 2.0 Device Authorization flow.

    Used when a browser cannot be opened. Provides a URL for the user to visit
    on another device and polls for authorization completion.

    Returns:
        str: The JWT access token.

    Raises:
        RuntimeError: If authentication fails or is denied.
    """
    resp = requests.post(
        DEVICE_URL,
        data={"client_id": CLIENT_ID_DEVICE, "scope": SCOPE, "audience": AUDIENCE},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    device_code = resp.json()["device_code"]
    print(f"Please visit: {resp.json()['verification_uri_complete']}")

    # Polling for access token with received device code
    while True:
        resp = requests.post(
            TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": CLIENT_ID_DEVICE,
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
            TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID_INTERACTIVE,
                "refresh_token": refresh_token,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        ).json()
        if "error" in resp:
            if resp["error"] in {"authorization_pending", "slow_down"}:
                time.sleep(AUTHORIZATION_BACKOFF_SECONDS)
                continue
            raise RuntimeError(resp["error"])
        return resp["access_token"]


if __name__ == "__main__":
    print(get_token(use_cache=False))
