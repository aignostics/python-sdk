"""Constants used throughout Aignostics Python SDK's codebase ."""

import importlib.metadata
import pathlib

__project_name__ = __name__.split(".")[0]
__project_path__ = str(pathlib.Path(__file__).parent.parent.parent)
__version__ = importlib.metadata.version(__project_name__)

API_ROOT_PRODUCTION = "https://platform.aignostics.com"
# TODO (Andreas): hhva: please fill in
AUDIENCE_PRODUCTION = "https://todo"
AUTHORIZATION_BASE_URL_PRODUCTION = "https://todo"
TOKEN_URL_PRODUCTION = "https://todo"  # noqa: S105
REDIRECT_URI_PRODUCTION = "https://todo"
DEVICE_URL_PRODUCTION = "https://todo"
JWS_JSON_URL_PRODUCTION = "https://todo"

API_ROOT_STAGING = "https://platform-staging.aignostics.com"
# TODO (Andreas): hhva: please fill in
AUDIENCE_STAGING = "https://todo"
AUTHORIZATION_BASE_URL_STAGING = "https://todo"
TOKEN_URL_STAGING = "https://todo"  # noqa: S105
REDIRECT_URI_STAGING = "https://todo"
DEVICE_URL_STAGING = "https://todo"
JWS_JSON_URL_STAGING = "https://todo"

API_ROOT_DEV = "https://platform-dev.aignostics.com"
AUDIENCE_DEV = "https://dev-8ouohmmrbuh2h4vu-samia"
AUTHORIZATION_BASE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize"
TOKEN_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_DEV = "http://localhost:8080/"
DEVICE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/.well-known/jwks.json"
