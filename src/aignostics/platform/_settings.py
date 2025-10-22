"""Settings of the Python SDK."""

import logging
import os
from pathlib import Path
from typing import Annotated, TypeVar
from urllib.parse import urlparse

import platformdirs
from pydantic import (
    BeforeValidator,
    Field,
    FieldSerializationInfo,
    PlainSerializer,
    SecretStr,
    computed_field,
    field_serializer,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from aignostics.utils import OpaqueSettings, __project_name__, load_settings

from ._constants import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
    CLIENT_ID_INTERACTIVE_DEV,
    CLIENT_ID_INTERACTIVE_PRODUCTION,
    CLIENT_ID_INTERACTIVE_STAGING,
    DEVICE_URL_DEV,
    DEVICE_URL_PRODUCTION,
    DEVICE_URL_STAGING,
    JWS_JSON_URL_DEV,
    JWS_JSON_URL_PRODUCTION,
    JWS_JSON_URL_STAGING,
    REDIRECT_URI_DEV,
    REDIRECT_URI_PRODUCTION,
    REDIRECT_URI_STAGING,
    TOKEN_URL_DEV,
    TOKEN_URL_PRODUCTION,
    TOKEN_URL_STAGING,
)
from ._messages import UNKNOWN_ENDPOINT_URL

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseSettings)

TIMEOUT_MIN_DEFAULT = 0.1  # seconds
TIMEOUT_MAX_DEFAULT = 300.0  # seconds
TIMEOUT_DEFAULT = 30.0  # seconds

RETRY_ATTEMPTS_MIN_DEFAULT = 0
RETRY_ATTEMPTS_MAX_DEFAULT = 10
RETRY_ATTEMPTS_DEFAULT = 4

RETRY_WAIT_MIN_MIN_DEFAULT = 0.0  # seconds
RETRY_WAIT_MIN_MAX_DEFAULT = 600.0  # seconds
RETRY_WAIT_MIN_DEFAULT = 0.1  # seconds

RETRY_WAIT_MAX_MIN_DEFAULT = 0.0  # seconds
RETRY_WAIT_MAX_MAX_DEFAULT = 600.0  # seconds
RETRY_WAIT_MAX_DEFAULT = 60.0  # seconds

CACHE_TTL_MIN_DEFAULT = 0  # seconds
CACHE_TTL_MAX_DEFAULT = 60 * 60 * 24 * 7  # 1 week
CACHE_TTL_DEFAULT = 60 * 5  # 5 minutes
AUTH_JWK_SET_CACHE_TTL_DEFAULT = 60 * 60 * 24  # 1 day
RUN_CACHE_TTL_DEFAULT = 15  # 15 seconds


def _validate_url(value: str) -> str:
    """Validate that a string is a valid URL.

    Args:
        value: The string to validate.

    Returns:
        The validated URL string.

    Raises:
        ValueError: If the string is not a valid URL.
    """
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        msg = f"Invalid URL format: {value}"
        raise ValueError(msg)

    if parsed.scheme not in {"http", "https"}:
        msg = f"URL must use http or https scheme, got {parsed.scheme}"
        raise ValueError(msg)

    return value


class Settings(OpaqueSettings):
    """Configuration settings for the Aignostics SDK.

    This class handles configuration settings loaded from environment variables,
    configuration files, or default values. It manages authentication endpoints,
    client credentials, token storage, and other SDK behaviors.

    Attributes:
        api_root (str): Base URL of the Aignostics API.
        audience (str): OAuth audience claim.
        authorization_base_url (str): Authorization endpoint for OAuth flows.
        cache_dir (str): Directory for caching tokens and other data.
        client_id_interactive (str): Client ID for interactive authorization flow.
        client_id_device (SecretStr | None): Client ID for device authorization flow.
        device_url (str): Device authorization endpoint for device flow.
        jws_json_url (str): URL for JWS key set.
        redirect_uri (str): Redirect URI for OAuth authorization code flow.
        refresh_token (SecretStr | None): OAuth refresh token if available.
        health_timeout (float): Timeout for health checks in seconds.
        auth_jwk_set_cache_ttl (int): Time-to-live for JWK set cache in seconds.
        auth_timeout (float): Authentication request timeout in seconds.
        auth_retry_attempts (int): Number of retry attempts for authentication requests.
        auth_retry_wait_min (float): Minimum wait time between authentication request retries in seconds.
        auth_retry_wait_max (float): Maximum wait time between authentication request retries in seconds.
        me_timeout (float): Timeout for "me" requests in seconds.
        me_retry_attempts (int): Number of retry attempts for "me" requests.
        me_retry_wait_min (float): Minimum wait time between "me" request retries in seconds.
        me_retry_wait_max (float): Maximum wait time between "me" request retries in seconds.
        me_cache_ttl (int): Time-to-live for "me" cache in seconds.
        application_timeout (float): Timeout for application requests in seconds.
        application_retry_attempts (int): Number of retry attempts for application requests.
        application_retry_wait_min (float): Minimum wait time between application request retries in seconds.
        application_retry_wait_max (float): Maximum wait time between application request retries in seconds.
        application_cache_ttl (int): Time-to-live for application cache in seconds.
        application_version_timeout (float): Timeout for application version requests in seconds.
        application_version_retry_attempts (int): Number of retry attempts for application version requests.
        application_version_retry_wait_min (float): Minimum wait time between application version request
            retries in seconds.
        application_version_retry_wait_max (float): Maximum wait time between application version request
            retries in seconds.
        application_version_cache_ttl (int): Time-to-live for application version cache in seconds.
        run_timeout (float): Timeout for run requests in seconds.
        run_retry_attempts (int): Number of retry attempts for run requests.
        run_retry_wait_min (float): Minimum wait time between run request retries in seconds.
        run_retry_wait_max (float): Maximum wait time between run request retries in seconds.
        run_cache_ttl (int): Time-to-live for run cache in seconds.
        run_cancel_timeout (float): Timeout for run cancel requests in seconds.
        run_delete_timeout (float): Timeout for run delete requests in seconds.
        run_submit_timeout (float): Timeout for run submit requests in seconds.
        scope (str): OAuth scopes required by the SDK.
        scope_elements (list[str]): OAuth scopes split into individual elements.
        token_file (Path): Path to the token storage file.
        token_url (str): Token endpoint for OAuth flows.
    """

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_",
        env_file=(
            os.getenv(f"{__project_name__.upper()}_ENV_FILE", Path.home() / f".{__project_name__}/.env"),
            Path(".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_id_device: Annotated[
        SecretStr | None,
        PlainSerializer(
            func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"
        ),  # allow to unhide sensitive info from CLI or if user presents valid token via API
        Field(description="OAuth Client ID Interactive"),
    ] = None

    api_root: Annotated[
        str,
        BeforeValidator(_validate_url),
        Field(description="URL of the API root", default=API_ROOT_PRODUCTION),
    ]

    scope: Annotated[str, Field(description="OAuth scopes", min_length=3)] = "offline_access"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scope_elements(self) -> list[str]:
        """Get the OAuth scope elements as a list.

        Splits the scope string by comma and strips whitespace from each element.

        Returns:
            list[str]: List of individual scope elements.
        """
        return [element.strip() for element in self.scope.split(",")]

    audience: Annotated[str, Field(description="OAuth audience claim", min_length=10, max_length=100)]
    authorization_base_url: Annotated[str, Field(description="OAuth authorization endpoint URL", min_length=1)]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def issuer(self) -> str:
        """Get the issuer URL based on the authorization base root.

        Extracts the scheme and domain from the authorization base URL to create
        a failsafe issuer URL in the format scheme://domain/

        Returns:
            str: Issuer URL in the format scheme://domain/
        """
        try:
            parsed = urlparse(self.authorization_base_url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}/"
            # Fallback to original logic if URL parsing fails
            logger.warning(
                "Failed to parse authorization_base_url '%s', falling back to rsplit method",
                self.authorization_base_url,
            )
            return self.authorization_base_url.rsplit("/", 1)[0] + "/"
        except (ValueError, AttributeError):
            # Ultimate fallback if everything fails
            logger.exception(
                "Error parsing authorization_base_url '%s', falling back to rsplit method",
                self.authorization_base_url,
            )
            return self.authorization_base_url.rsplit("/", 1)[0] + "/"

    token_url: Annotated[str, BeforeValidator(_validate_url), Field(description="OAuth token endpoint URL")]
    redirect_uri: Annotated[
        str, BeforeValidator(_validate_url), Field(description="OAuth redirect URI for authorization code flow")
    ]
    device_url: Annotated[
        str, BeforeValidator(_validate_url), Field(description="OAuth device authorization endpoint URL")
    ]
    jws_json_url: Annotated[
        str, BeforeValidator(_validate_url), Field(description="JWS key set URL for token verification")
    ]
    client_id_interactive: Annotated[str, Field(description="OAuth client ID for interactive flows")]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def tenant_domain(self) -> str:
        """Get the tenant domain from the authorization base URL.

        Returns:
            str: The domain part of the authorization base URL.

        Raises:
            ValueError: If the authorization base URL is invalid or does not contain a netloc.
        """
        parsed = urlparse(self.authorization_base_url)
        if parsed.netloc:
            return parsed.netloc
        message = f"Invalid authorization_base_url: {self.authorization_base_url}"
        logger.error(message)
        raise ValueError(message)

    refresh_token: Annotated[
        SecretStr | None,
        PlainSerializer(
            func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"
        ),  # allow to unhide sensitive info from CLI or if user presents valid token via API
        Field(description="Refresh token for OAuth authentication", min_length=10, max_length=1000, default=None),
    ] = None

    cache_dir: str = platformdirs.user_cache_dir(__project_name__)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def token_file(self) -> Path:
        """Get the path to the token file.

        Returns:
            Path: The path to the file where the authentication token is stored.
        """
        return Path(self.cache_dir) / ".token"

    @field_serializer("token_file")
    def serialize_token_file(self, token_file: Path, _info: FieldSerializationInfo) -> str:  # noqa: PLR6301
        return str(token_file.resolve())

    health_timeout: Annotated[
        float,
        Field(
            description="Timeout for health checks",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT

    auth_jwk_set_cache_ttl: Annotated[
        int,
        Field(
            description="Time-to-live for JWK set cache (in seconds)",
            ge=CACHE_TTL_MIN_DEFAULT,
            le=CACHE_TTL_MAX_DEFAULT,
        ),
    ] = AUTH_JWK_SET_CACHE_TTL_DEFAULT

    auth_timeout: Annotated[
        float,
        Field(
            description="Timeout for authentication requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT
    auth_retry_attempts: Annotated[
        int,
        Field(
            description="Number of retry attempts for authentication requests",
            ge=RETRY_ATTEMPTS_MIN_DEFAULT,
            le=RETRY_ATTEMPTS_MAX_DEFAULT,
        ),
    ] = RETRY_ATTEMPTS_DEFAULT
    auth_retry_wait_min: Annotated[
        float,
        Field(
            description="Minimum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MIN_MIN_DEFAULT,
            le=RETRY_WAIT_MIN_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MIN_DEFAULT
    auth_retry_wait_max: Annotated[
        float,
        Field(
            description="Maximum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MAX_MIN_DEFAULT,
            le=RETRY_WAIT_MAX_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MAX_DEFAULT

    me_timeout: Annotated[
        float,
        Field(
            description="Timeout for me requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT
    me_retry_attempts: Annotated[
        int,
        Field(
            description="Number of retry attempts for me requests",
            ge=RETRY_ATTEMPTS_MIN_DEFAULT,
            le=RETRY_ATTEMPTS_MAX_DEFAULT,
        ),
    ] = RETRY_ATTEMPTS_DEFAULT
    me_retry_wait_min: Annotated[
        float,
        Field(
            description="Minimum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MIN_MIN_DEFAULT,
            le=RETRY_WAIT_MIN_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MIN_DEFAULT
    me_retry_wait_max: Annotated[
        float,
        Field(
            description="Maximum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MAX_MIN_DEFAULT,
            le=RETRY_WAIT_MAX_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MAX_DEFAULT
    me_cache_ttl: Annotated[
        int,
        Field(
            description="Time-to-live for me cache (in seconds)",
            ge=CACHE_TTL_MIN_DEFAULT,
            le=CACHE_TTL_MAX_DEFAULT,
        ),
    ] = CACHE_TTL_DEFAULT

    application_timeout: Annotated[
        float,
        Field(
            description="Timeout for application requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT
    application_retry_attempts: Annotated[
        int,
        Field(
            description="Number of retry attempts for application requests",
            ge=RETRY_ATTEMPTS_MIN_DEFAULT,
            le=RETRY_ATTEMPTS_MAX_DEFAULT,
        ),
    ] = RETRY_ATTEMPTS_DEFAULT
    application_retry_wait_min: Annotated[
        float,
        Field(
            description="Minimum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MIN_MIN_DEFAULT,
            le=RETRY_WAIT_MIN_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MIN_DEFAULT
    application_retry_wait_max: Annotated[
        float,
        Field(
            description="Maximum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MAX_MIN_DEFAULT,
            le=RETRY_WAIT_MAX_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MAX_DEFAULT
    application_cache_ttl: Annotated[
        int,
        Field(
            description="Time-to-live for application cache (in seconds)",
            ge=CACHE_TTL_MIN_DEFAULT,
            le=CACHE_TTL_MAX_DEFAULT,
        ),
    ] = CACHE_TTL_DEFAULT

    application_version_timeout: Annotated[
        float,
        Field(
            description="Timeout for application version requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT
    application_version_retry_attempts: Annotated[
        int,
        Field(
            description="Number of retry attempts for application version requests",
            ge=RETRY_ATTEMPTS_MIN_DEFAULT,
            le=RETRY_ATTEMPTS_MAX_DEFAULT,
        ),
    ] = RETRY_ATTEMPTS_DEFAULT
    application_version_retry_wait_min: Annotated[
        float,
        Field(
            description="Minimum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MIN_MIN_DEFAULT,
            le=RETRY_WAIT_MIN_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MIN_DEFAULT
    application_version_retry_wait_max: Annotated[
        float,
        Field(
            description="Maximum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MAX_MIN_DEFAULT,
            le=RETRY_WAIT_MAX_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MAX_DEFAULT
    application_version_cache_ttl: Annotated[
        int,
        Field(
            description="Time-to-live for application version cache (in seconds)",
            ge=CACHE_TTL_MIN_DEFAULT,
            le=CACHE_TTL_MAX_DEFAULT,
        ),
    ] = CACHE_TTL_DEFAULT

    run_timeout: Annotated[
        float,
        Field(
            description="Timeout for run requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT
    run_retry_attempts: Annotated[
        int,
        Field(
            description="Number of retry attempts for run requests",
            ge=RETRY_ATTEMPTS_MIN_DEFAULT,
            le=RETRY_ATTEMPTS_MAX_DEFAULT,
        ),
    ] = RETRY_ATTEMPTS_DEFAULT
    run_retry_wait_min: Annotated[
        float,
        Field(
            description="Minimum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MIN_MIN_DEFAULT,
            le=RETRY_WAIT_MIN_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MIN_DEFAULT
    run_retry_wait_max: Annotated[
        float,
        Field(
            description="Maximum wait time between retry attempts (in seconds)",
            ge=RETRY_WAIT_MAX_MIN_DEFAULT,
            le=RETRY_WAIT_MAX_MAX_DEFAULT,
        ),
    ] = RETRY_WAIT_MAX_DEFAULT
    run_cache_ttl: Annotated[
        int,
        Field(
            description="Time-to-live for run cache (in seconds)",
            ge=CACHE_TTL_MIN_DEFAULT,
            le=CACHE_TTL_MAX_DEFAULT,
        ),
    ] = RUN_CACHE_TTL_DEFAULT

    run_cancel_timeout: Annotated[
        float,
        Field(
            description="Timeout for run cancel requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT

    run_delete_timeout: Annotated[
        float,
        Field(
            description="Timeout for run delete requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT

    run_submit_timeout: Annotated[
        float,
        Field(
            description="Timeout for run submit requests",
            ge=TIMEOUT_MIN_DEFAULT,
            le=TIMEOUT_MAX_DEFAULT,
        ),
    ] = TIMEOUT_DEFAULT

    @model_validator(mode="before")
    def pre_init(cls, values: dict) -> dict:  # type: ignore[type-arg] # noqa: N805
        """Initialize auth-related fields based on the API root.

        This validator sets the appropriate authentication URLs and parameters
        based on the target environment (production, staging, or development).
        If auth-related fields are already provided, they will not be overridden.

        Args:
            values: The input data dictionary to validate.

        Returns:
            The updated values dictionary with all environment-specific fields populated.

        Raises:
            ValueError: If the API root URL is not recognized and auth fields are missing.
        """
        # See https://github.com/pydantic/pydantic/issues/9789
        api_root = values.get("api_root", API_ROOT_PRODUCTION)

        # Check if all required auth fields are already provided
        auth_fields = [
            "audience",
            "authorization_base_url",
            "token_url",
            "redirect_uri",
            "device_url",
            "jws_json_url",
            "client_id_interactive",
        ]
        all_auth_fields_provided = all(field in values for field in auth_fields)

        # If all auth fields are provided, don't override them
        if all_auth_fields_provided:
            return values

        match api_root:
            case x if x == API_ROOT_PRODUCTION:
                values["audience"] = AUDIENCE_PRODUCTION
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_PRODUCTION
                values["token_url"] = TOKEN_URL_PRODUCTION
                values["redirect_uri"] = REDIRECT_URI_PRODUCTION
                values["device_url"] = DEVICE_URL_PRODUCTION
                values["jws_json_url"] = JWS_JSON_URL_PRODUCTION
                values["client_id_interactive"] = CLIENT_ID_INTERACTIVE_PRODUCTION
            case x if x == API_ROOT_STAGING:
                values["audience"] = AUDIENCE_STAGING
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_STAGING
                values["token_url"] = TOKEN_URL_STAGING
                values["redirect_uri"] = REDIRECT_URI_STAGING
                values["device_url"] = DEVICE_URL_STAGING
                values["jws_json_url"] = JWS_JSON_URL_STAGING
                values["client_id_interactive"] = CLIENT_ID_INTERACTIVE_STAGING
            case x if x == API_ROOT_DEV:
                values["audience"] = AUDIENCE_DEV
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_DEV
                values["token_url"] = TOKEN_URL_DEV
                values["redirect_uri"] = REDIRECT_URI_DEV
                values["device_url"] = DEVICE_URL_DEV
                values["jws_json_url"] = JWS_JSON_URL_DEV
                values["client_id_interactive"] = CLIENT_ID_INTERACTIVE_DEV
            case _:
                raise ValueError(UNKNOWN_ENDPOINT_URL)

        return values

    @model_validator(mode="after")
    def validate_retry_wait_times(self) -> "Settings":
        """Validate that retry wait min is less or equal than retry wait max for all operations.

        Returns:
            Settings: The validated settings instance.

        Raises:
            ValueError: If any operation's retry_wait_min is greater than retry_wait_max.
        """
        if self.auth_retry_wait_min > self.auth_retry_wait_max:
            msg = (
                f"auth_retry_wait_min ({self.auth_retry_wait_min}) must be less or equal than "
                f"auth_retry_wait_max ({self.auth_retry_wait_max})"
            )
            raise ValueError(msg)
        if self.me_retry_wait_min > self.me_retry_wait_max:
            msg = (
                f"me_retry_wait_min ({self.me_retry_wait_min}) must be less or equal than "
                f"me_retry_wait_max ({self.me_retry_wait_max})"
            )
            raise ValueError(msg)
        if self.application_retry_wait_min > self.application_retry_wait_max:
            msg = (
                f"application_retry_wait_min ({self.application_retry_wait_min}) must be less or equal than "
                f"application_retry_wait_max ({self.application_retry_wait_max})"
            )
            raise ValueError(msg)
        if self.application_version_retry_wait_min > self.application_version_retry_wait_max:
            msg = (
                f"application_version_retry_wait_min ({self.application_version_retry_wait_min}) "
                f"must be less or equal than application_version_retry_wait_max "
                f"({self.application_version_retry_wait_max})"
            )
            raise ValueError(msg)
        if self.run_retry_wait_min > self.run_retry_wait_max:
            msg = (
                f"run_retry_wait_min ({self.run_retry_wait_min}) must be less or equal than "
                f"run_retry_wait_max ({self.run_retry_wait_max})"
            )
            raise ValueError(msg)
        return self


__cached_settings: Settings | None = None


def settings() -> Settings:
    """Lazy load authentication settings from the environment or a file.

    * Given we use Pydantic Settings, validation is done automatically.
    * We only load and validate if we actually need the settings,
        thereby not killing the client on other actions.
    * If the settings have already been loaded, return the cached instance.

    Returns:
        AuthenticationSettings: The loaded authentication settings.
    """
    global __cached_settings  # noqa: PLW0603
    if __cached_settings is None:
        __cached_settings = load_settings(Settings)  # pyright: ignore[reportCallIssue]
    return __cached_settings
