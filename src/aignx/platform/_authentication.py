import os
import time
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse
from urllib.parse import urlparse

import appdirs
import jwt
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# load client ids
load_dotenv()

CLIENT_ID_DEVICE = os.getenv("CLIENT_ID_DEVICE")
CLIENT_ID_INTERACTIVE = os.getenv("CLIENT_ID_INTERACTIVE")
SCOPE = ["offline_access"]  # include a refresh token as well
REDIRECT_URI = "http://localhost:8080"  # is configured in Auth0 - do not change

AUDIENCE = "https://dev-8ouohmmrbuh2h4vu-samia"
AUTHORIZATION_BASE_URL = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize"
TOKEN_URL = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token"
DEVICE_URL = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/device/code"

# constants for token caching
CLIENT_APP_NAME = "python-sdk"
CACHE_DIR = appdirs.user_cache_dir(CLIENT_APP_NAME, "aignostics")
TOKEN_FILE = Path(CACHE_DIR) / ".token"

AUTHORIZATION_BACKOFF_SECONDS = 3


def get_token(store: bool = True):
    if not store:
        return _login()

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            stored_token = f.read()
        # Parse stored string "token:expiry_timestamp"
        parts = stored_token.split(":")
        if len(parts) == 2:
            token, expiry_str = parts
            expiry = datetime.fromtimestamp(int(expiry_str))

            # Check if token is still valid (with some buffer time)
            if datetime.now() + timedelta(minutes=5) < expiry:
                return token

    # If we got here, we need a new token
    refresh_token = os.getenv("AIGNX_REFRESH_TOKEN")
    if refresh_token:
        new_token = _token_from_refresh_token(refresh_token)
    else:
        new_token = _login()

    # we do not need to verify as we just want to obtain the expiry date
    claims = jwt.decode(new_token.encode("ascii"), options={"verify_signature": False})
    timestamp = claims["exp"]

    # Store new token with expiry
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(f"{new_token}:{timestamp}")

    return new_token


def _login() -> str:
    """Allows the user to login, returns the JSON Web Token."""
    flow_type = "browser" if _can_open_browser() else "device"
    if flow_type == "browser":
        token = _perform_authorization_code_with_pkce_flow()
    else:
        token = _perform_device_flow()
    assert token.count(".") == 2
    return token


def _can_open_browser() -> bool:
    launch_browser = False
    try:
        _ = webbrowser.get()
        launch_browser = True
    except webbrowser.Error:
        launch_browser = False

    return launch_browser


class _OAuthHttpServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.authorization_code = ""


class _OAuthHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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

    def log_message(self, format, *args):
        pass


def _perform_authorization_code_with_pkce_flow():
    parsed_redirect = urlparse(REDIRECT_URI)
    with _OAuthHttpServer((parsed_redirect.hostname, parsed_redirect.port), _OAuthHttpHandler) as httpd:
        # initialize flow (generate code_challenge and code_verifier)
        session = OAuth2Session(CLIENT_ID_INTERACTIVE, scope=SCOPE, redirect_uri=REDIRECT_URI, pkce="S256")
        authorization_url, state = session.authorization_url(
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


def _perform_device_flow():
    resp = requests.post(DEVICE_URL, data={"client_id": CLIENT_ID_DEVICE, "scope": SCOPE, "audience": AUDIENCE})
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
        ).json()

        if "error" in resp:
            if resp["error"] in ("authorization_pending", "slow_down"):
                time.sleep(3)
                continue
            raise RuntimeError(resp["error"])
        return resp["access_token"]


def _token_from_refresh_token(refresh_token: str):
    while True:
        resp = requests.post(
            TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID_INTERACTIVE,
                "refresh_token": refresh_token,
            },
        ).json()
        if "error" in resp:
            if resp["error"] in ("authorization_pending", "slow_down"):
                time.sleep(AUTHORIZATION_BACKOFF_SECONDS)
                continue
            raise RuntimeError(resp["error"])
        return resp["access_token"]


if __name__ == "__main__":
    print(get_token())
