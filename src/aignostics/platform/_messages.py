"""Messages for the Aignostics client."""

AUTHENTICATION_FAILED = "Authentication failed. Please check your credentials."
AUTHENTICATION_FAILED_ACCESS_TOKEN_FROM_REFRESH_TOKEN = (
    "Authentication failed on exchange of refresh token with access token: "  # noqa: S105
)
AUTHENTICATION_FAILED_TOKEN_VERIFICATION = "Authentication failed on token verification: "  # noqa: S105
NOT_YET_IMPLEMENTED = "Not yet implemented."
UNKNOWN_ENDPOINT_URL = "AIGNOSTICS_API_ROOT set to unknown endpoint URL. Please check your environment settings."
INVALID_REDIRECT_URI = "Invalid redirect URI. Please check the redirect URI in your application settings."
