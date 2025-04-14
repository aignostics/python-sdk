"""Utilities around Pydantic settings."""

import json
import logging
import sys
from pathlib import Path
from typing import TypeVar

from pydantic import FieldSerializationInfo, SecretStr, ValidationError
from pydantic_settings import BaseSettings
from rich.panel import Panel
from rich.text import Text

from ._console import console

T = TypeVar("T", bound=BaseSettings)

logger = logging.getLogger(__name__)

UNHIDE_SENSITIVE_INFO = "unhide_sensitive_info"


def strip_to_none_before_validator(v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    return v


class OpaqueSettings(BaseSettings):
    @staticmethod
    def serialize_sensitive_info(input_value: SecretStr, info: FieldSerializationInfo) -> str | None:
        if not input_value:
            return None
        if info.context.get(UNHIDE_SENSITIVE_INFO, False):  # type: ignore
            return input_value.get_secret_value()
        return str(input_value)


def load_settings(settings_class: type[T]) -> T:
    """
    Load settings with error handling and nice formatting.

    Args:
        settings_class: The Pydantic settings class to instantiate

    Returns:
        (T): Instance of the settings class

    Raises:
        SystemExit: If settings validation fails
    """
    try:
        return settings_class()
    except ValidationError as e:
        errors = json.loads(e.json())
        text = Text()
        text.append(
            "Validation error(s): \n\n",
            style="debug",
        )

        prefix = settings_class.model_config.get("env_prefix", "")
        for error in errors:
            env_var = f"{prefix}{error['loc'][0]}".upper()
            logger.fatal(f"Configuration invalid! {env_var}: {error['msg']}")
            text.append(f"• {env_var}", style="yellow bold")
            text.append(f": {error['msg']}\n")

        text.append(
            "\nCheck settings defined in the process environment and in file ",
            style="info",
        )
        env_file = str(settings_class.model_config.get("env_file", ".env") or ".env")
        text.append(
            str(Path(__file__).parent.parent.parent.parent / env_file),
            style="bold blue underline",
        )

        console.print(
            Panel(
                text,
                title="Configuration invalid!",
                border_style="error",
            ),
        )
        sys.exit(78)
