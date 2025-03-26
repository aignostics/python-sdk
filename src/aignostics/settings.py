"""Settings of Aignostics Python SDK."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import __project_name__


class Language(StrEnum):
    """Supported languages."""

    GERMAN = "de_DE"
    US_ENGLISH = "en_US"


class Settings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    language: Annotated[
        Language,
        Field(
            Language.US_ENGLISH,
            description="Language to use for output - defaults to US english.",
        ),
    ]
