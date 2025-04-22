"""Settings of the application module."""

from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from ..utils import OpaqueSettings, __env_file__, __project_name__  # noqa: TID252


class Settings(OpaqueSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_APPLICATION_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )

    data_directory: Annotated[
        str,
        Field(
            description=("Data directory"),
            default=str(Path.cwd() / "data"),
        ),
    ]
