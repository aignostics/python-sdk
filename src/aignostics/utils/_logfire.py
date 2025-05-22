"""Logfire integration for logging and instrumentation."""

from typing import Annotated

import logfire
from pydantic import BeforeValidator, Field, PlainSerializer, SecretStr
from pydantic_settings import SettingsConfigDict

from ._constants import __env__, __env_file__, __project_name__, __repository_url__, __version__
from ._settings import OpaqueSettings, load_settings, strip_to_none_before_validator


class LogfireSettings(OpaqueSettings):
    """Configuration settings for Logfire integration."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_LOGFIRE_",
        env_file=__env_file__,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: Annotated[
        SecretStr | None,
        BeforeValidator(strip_to_none_before_validator),
        PlainSerializer(func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"),
        Field(description="Logfire token. Leave empty to disable logfire.", examples=["YOUR_TOKEN"], default=None),
    ]
    instrument_system_metrics: Annotated[
        bool,
        Field(description="Enable system metrics instrumentation", default=False),
    ]


def logfire_initialize(modules: list["str"]) -> bool:
    """Initialize Logfire integration.

    Args:
        modules(list["str"]): List of modules to be instrumented.

    Returns:
        bool: True if initialized successfully False otherwise
    """
    settings = load_settings(LogfireSettings)

    if settings.token is None:
        return False

    logfire.configure(
        send_to_logfire="if-token-present",
        token=settings.token.get_secret_value(),
        environment=__env__,
        service_name=__project_name__,
        console=False,
        code_source=logfire.CodeSource(
            repository=__repository_url__,
            revision=__version__,
            root_path="",
        ),
    )

    if settings.instrument_system_metrics:
        logfire.instrument_system_metrics(base="full")

    logfire.instrument_pydantic()

    logfire.install_auto_tracing(modules=modules, min_duration=0.0)

    return True
