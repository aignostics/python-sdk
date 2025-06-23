"""Settings of the Python SDK."""

import logging
import os
from pathlib import Path
from typing import Annotated, TypeVar
from urllib.parse import urlparse

import appdirs
from pydantic import (
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
    API_ROOT_PRODUCTION,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
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


class Settings(OpaqueSettings):
    """Configuration settings for the Aignostics SDK.

    This class handles configuration settings loaded from environment variables,
    configuration files, or default values. It manages authentication endpoints,
    client credentials, token storage, and other SDK behaviors.

    Attributes:
        api_root (str): Base URL of the Aignostics API.
        audience (str): OAuth audience claim.
        authorization_backoff_seconds (int): Backoff time for authorization retries in seconds.
        authorization_base_url (str): Authorization endpoint for OAuth flows.
        cache_dir (str): Directory for caching tokens and other data.
        client_id_device (SecretStr): Client ID for device authorization flow.
        client_id_interactive (SecretStr): Client ID for interactive authorization flow.
        device_url (str): Device authorization endpoint for device flow.
        jws_json_url (str): URL for JWS key set.
        redirect_uri (str): Redirect URI for OAuth authorization code flow.
        refresh_token (SecretStr | None): OAuth refresh token if available.
        request_timeout_seconds (int): Timeout for API requests in seconds.
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
        SecretStr,
        PlainSerializer(
            func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"
        ),  # allow to unhide sensitive info from CLI or if user presents valid token via API
        Field(description="OAuth Client ID Interactive"),
    ]
    client_id_interactive: Annotated[
        SecretStr,
        PlainSerializer(
            func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"
        ),  # allow to unhide sensitive info from CLI or if user presents valid token via API
        Field(description="OAuth Client ID Interactive"),
    ]
    api_root: Annotated[
        str,
        Field(description="URL of the API root", default=API_ROOT_PRODUCTION),
    ]

    scope: str = "offline_access, profile, email, openid"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scope_elements(self) -> list[str]:
        """Get the OAuth scope elements as a list.

        Splits the scope string by comma and strips whitespace from each element.

        Returns:
            list[str]: List of individual scope elements.
        """
        if not self.scope:
            return []
        return [element.strip() for element in self.scope.split(",")]

    audience: str
    authorization_base_url: str

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

    token_url: str
    redirect_uri: str
    device_url: str
    jws_json_url: str

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

    cache_dir: str = appdirs.user_cache_dir(__project_name__)

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

    request_timeout_seconds: int = 30
    authorization_backoff_seconds: int = 3

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
        auth_fields = ["audience", "authorization_base_url", "token_url", "redirect_uri", "device_url", "jws_json_url"]
        all_auth_fields_provided = all(field in values for field in auth_fields)

        # If all auth fields are provided, don't override them
        if all_auth_fields_provided:
            return values

        match api_root:
            case "https://platform.aignostics.com":
                values["audience"] = AUDIENCE_PRODUCTION
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_PRODUCTION
                values["token_url"] = TOKEN_URL_PRODUCTION
                values["redirect_uri"] = REDIRECT_URI_PRODUCTION
                values["device_url"] = DEVICE_URL_PRODUCTION
                values["jws_json_url"] = JWS_JSON_URL_PRODUCTION
            case "https://platform-staging.aignostics.com":
                values["audience"] = AUDIENCE_STAGING
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_STAGING
                values["token_url"] = TOKEN_URL_STAGING
                values["redirect_uri"] = REDIRECT_URI_STAGING
                values["device_url"] = DEVICE_URL_STAGING
                values["jws_json_url"] = JWS_JSON_URL_STAGING
            case "https://platform-dev.aignostics.com":
                values["audience"] = AUDIENCE_DEV
                values["authorization_base_url"] = AUTHORIZATION_BASE_URL_DEV
                values["token_url"] = TOKEN_URL_DEV
                values["redirect_uri"] = REDIRECT_URI_DEV
                values["device_url"] = DEVICE_URL_DEV
                values["jws_json_url"] = JWS_JSON_URL_DEV
            case _:
                raise ValueError(UNKNOWN_ENDPOINT_URL)

        return values


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
