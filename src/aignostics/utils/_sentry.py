"""Sentry integration for application monitoring."""

import re
import urllib.parse
from typing import Annotated

import sentry_sdk
from pydantic import AfterValidator, BeforeValidator, Field, PlainSerializer, SecretStr
from pydantic_settings import SettingsConfigDict
from sentry_sdk.integrations.typer import TyperIntegration

from ._constants import __env__, __env_file__, __project_name__, __version__
from ._settings import OpaqueSettings, load_settings, strip_to_none_before_validator

_ERR_MSG_MISSING_SCHEME = "Sentry DSN is missing URL scheme (protocol)"
_ERR_MSG_MISSING_NETLOC = "Sentry DSN is missing network location (domain)"
_ERR_MSG_NON_HTTPS = "Sentry DSN must use HTTPS protocol for security"
_ERR_MSG_INVALID_DOMAIN = "Sentry DSN must use a valid Sentry domain (ingest.us.sentry.io or ingest.de.sentry.io)"
_ERR_MSG_INVALID_FORMAT = "Invalid Sentry DSN format"
_VALID_SENTRY_DOMAIN_PATTERN = r"^[a-f0-9]+@o\d+\.ingest\.(us|de)\.sentry\.io$"


def _validate_url_scheme(parsed_url: urllib.parse.ParseResult) -> None:
    """Validate that the URL has a scheme.

    Args:
        parsed_url: The parsed URL to validate

    Raises:
        ValueError: If URL is missing scheme
    """
    if not parsed_url.scheme:
        raise ValueError(_ERR_MSG_MISSING_SCHEME)


def _validate_url_netloc(parsed_url: urllib.parse.ParseResult) -> None:
    """Validate that the URL has a network location.

    Args:
        parsed_url: The parsed URL to validate

    Raises:
        ValueError: If URL is missing network location
    """
    if not parsed_url.netloc:
        raise ValueError(_ERR_MSG_MISSING_NETLOC)


def _validate_https_scheme(parsed_url: urllib.parse.ParseResult) -> None:
    """Validate that the URL uses HTTPS scheme.

    Args:
        parsed_url: The parsed URL to validate

    Raises:
        ValueError: If URL doesn't use HTTPS scheme
    """
    if parsed_url.scheme != "https":
        raise ValueError(_ERR_MSG_NON_HTTPS)


def _validate_sentry_domain(netloc_with_auth: str) -> None:
    """Validate that the URL uses a valid Sentry domain.

    Args:
        netloc_with_auth: The network location with auth part

    Raises:
        ValueError: If URL doesn't use a valid Sentry domain
    """
    if "@" not in netloc_with_auth:
        raise ValueError(_ERR_MSG_INVALID_DOMAIN)

    user_pass, domain = netloc_with_auth.split("@", 1)
    full_auth = f"{user_pass}@{domain}"
    if not re.match(_VALID_SENTRY_DOMAIN_PATTERN, full_auth):
        raise ValueError(_ERR_MSG_INVALID_DOMAIN)


def _validate_https_dsn(value: SecretStr | None) -> SecretStr | None:
    """Validate that the Sentry DSN is a valid HTTPS URL.

    Args:
        value: The DSN value to validate

    Returns:
        SecretStr | None: The validated DSN value

    Raises:
        ValueError: If DSN isn't a valid HTTPS URL with specific error details
    """
    if value is None:
        return value

    dsn = value.get_secret_value()
    try:
        parsed_url = urllib.parse.urlparse(dsn)

        # Call validation functions outside of the try block
        _validate_url_scheme(parsed_url)
        _validate_url_netloc(parsed_url)
        _validate_https_scheme(parsed_url)
        _validate_sentry_domain(parsed_url.netloc)

    except ValueError as exc:
        raise exc from None
    except Exception as exc:
        error_message = _ERR_MSG_INVALID_FORMAT
        raise ValueError(error_message) from exc

    return value


class SentrySettings(OpaqueSettings):
    """Configuration settings for Sentry integration."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_SENTRY_",
        env_file=__env_file__,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: Annotated[
        bool,
        Field(
            description="Enable remote error and profile collection via Sentry",
            default=False,
        ),
    ]

    dsn: Annotated[
        SecretStr | None,
        BeforeValidator(strip_to_none_before_validator),
        AfterValidator(_validate_https_dsn),
        PlainSerializer(func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"),
        Field(description="Sentry DSN", examples=["https://SECRET@SECRET.ingest.de.sentry.io/SECRET"], default=None),
    ]

    debug: Annotated[
        bool,
        Field(description="Debug (https://docs.sentry.io/platforms/python/configuration/options/)", default=False),
    ]

    send_default_pii: Annotated[
        bool,
        Field(
            description="Send default personal identifiable information (https://docs.sentry.io/platforms/python/configuration/options/)",
            default=False,
        ),
    ]

    max_breadcrumbs: Annotated[
        int,
        Field(
            description="Max breadcrumbs (https://docs.sentry.io/platforms/python/configuration/options/#max_breadcrumbs)",
            ge=0,
            default=50,
        ),
    ]
    sample_rate: Annotated[
        float,
        Field(
            ge=0.0,
            description="Sample Rate (https://docs.sentry.io/platforms/python/configuration/sampling/#sampling-error-events)",
            default=1.0,
        ),
    ]
    traces_sample_rate: Annotated[
        float,
        Field(
            ge=0.0,
            description="Traces Sample Rate (https://docs.sentry.io/platforms/python/configuration/sampling/#configuring-the-transaction-sample-rate)",
            default=1.0,
        ),
    ]
    profiles_sample_rate: Annotated[
        float,
        Field(
            ge=0.0,
            description="Traces Sample Rate (https://docs.sentry.io/platforms/python/tracing/#configure)",
            default=1.0,
        ),
    ]


def sentry_initialize() -> bool:
    """Initialize Sentry integration.

    Returns:
        bool: True if initialized successfully, False otherwise
    """
    settings = load_settings(SentrySettings)

    if not settings.enabled or settings.dsn is None:
        return False

    sentry_sdk.init(
        release=f"{__project_name__}@{__version__}",  # https://docs.sentry.io/platforms/python/configuration/releases/,
        environment=__env__,
        dsn=settings.dsn.get_secret_value().strip(),
        max_breadcrumbs=settings.max_breadcrumbs,
        debug=settings.debug,
        send_default_pii=settings.send_default_pii,
        sample_rate=settings.sample_rate,
        traces_sample_rate=settings.traces_sample_rate,
        profiles_sample_rate=settings.profiles_sample_rate,
        integrations=[TyperIntegration()],
    )

    return True
