"""Settings of the system module."""

from typing import Annotated

from pydantic import Field, PlainSerializer, SecretStr
from pydantic_settings import SettingsConfigDict

from ..utils import OpaqueSettings, __env_file__, __project_name__  # noqa: TID252


class Settings(OpaqueSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_SYSTEM_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )

    token: Annotated[
        SecretStr | None,
        PlainSerializer(func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"),
        Field(
            description=(
                "Secret token to present when performing sensitive operations such as "
                "retrieving info via webservice API"
            ),
            default=None,
        ),
    ]
