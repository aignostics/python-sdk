"""Client specific constants."""

API_ROOT_PRODUCTION = "https://platform.aignostics.com"
CLIENT_ID_INTERACTIVE_PRODUCTION = "YtJ7F9lAtxx16SZGQlYPe6wcjlXB78MM"  # not a secret, but a public client ID
AUDIENCE_PRODUCTION = "https://aignostics-platform-samia"
AUTHORIZATION_BASE_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/authorize"
TOKEN_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_PRODUCTION = "http://localhost:8989/"
DEVICE_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_PRODUCTION = "https://aignostics-platform.eu.auth0.com/.well-known/jwks.json"

API_ROOT_STAGING = "https://platform-staging.aignostics.com"
# TODO (Andreas): hhva: please fill in
TODO_URL = "https://todo"
CLIENT_ID_INTERACTIVE_STAGING = "TODO"
AUDIENCE_STAGING = TODO_URL
AUTHORIZATION_BASE_URL_STAGING = TODO_URL
TOKEN_URL_STAGING = TODO_URL
REDIRECT_URI_STAGING = TODO_URL
DEVICE_URL_STAGING = TODO_URL
JWS_JSON_URL_STAGING = TODO_URL

API_ROOT_DEV = "https://platform-dev.aignostics.com"
CLIENT_ID_INTERACTIVE_DEV = "gqduveFvx7LX90drQPGzr4JGUYdh24gA"
AUDIENCE_DEV = "https://dev-8ouohmmrbuh2h4vu-samia"
AUTHORIZATION_BASE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize"
TOKEN_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/token"  # noqa: S105
REDIRECT_URI_DEV = "http://localhost:8989/"
DEVICE_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/oauth/device/code"
JWS_JSON_URL_DEV = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/.well-known/jwks.json"
