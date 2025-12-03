"""Client specific and other constants such as defaults."""

API_ROOT_PRODUCTION = "https://platform.aignostics.com"
CLIENT_ID_INTERACTIVE_PRODUCTION = "YtJ7F9lAtxx16SZGQlYPe6wcjlXB78MM"  # not a secret, but a public client ID
AUDIENCE_PRODUCTION = "https://aignostics-platform-samia"
AUTHORIZATION_BASE_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/authorize"
TOKEN_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_PRODUCTION = "http://localhost:8989/"
DEVICE_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/.well-known/jwks.json"

API_ROOT_STAGING = "https://platform-staging.aignostics.com"
CLIENT_ID_INTERACTIVE_STAGING = "fQkbvYzQPPVwLxc3uque5JsyFW00rJ7b"  # not a secret, but a public client ID
AUDIENCE_STAGING = "https://aignostics-platform-staging-samia"
AUTHORIZATION_BASE_URL_STAGING = "https://aignostics-platform-staging.eu.auth0.com/authorize"
TOKEN_URL_STAGING = "https://aignostics-platform-staging.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_STAGING = "http://localhost:8989/"
DEVICE_URL_STAGING = "https://aignostics-platform-staging.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_STAGING = "https://aignostics-platform-staging.eu.auth0.com/.well-known/jwks.json"

API_ROOT_DEV = "https://platform-dev.aignostics.ai"
CLIENT_ID_INTERACTIVE_DEV = "gqduveFvx7LX90drQPGzr4JGUYdh24gA"  # not a secret, but a public client ID
AUDIENCE_DEV = "https://dev-8ouohmmrbuh2h4vu-samia"
AUTHORIZATION_BASE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize"
TOKEN_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_DEV = "http://localhost:8989/"
DEVICE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/.well-known/jwks.json"

# Pipeline orchestration defaults
DEFAULT_GPU_TYPE = "L4"
DEFAULT_MAX_GPUS_PER_SLIDE = 1
DEFAULT_GPU_PROVISIONING_MODE = "SPOT"
DEFAULT_CPU_PROVISIONING_MODE = "SPOT"
DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES = 30
DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES = 12 * 60  # 12 hours in minutes
