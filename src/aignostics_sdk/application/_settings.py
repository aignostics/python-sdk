"""Settings of the application module."""

from pydantic_settings import SettingsConfigDict

from aignostics_sdk.utils import ENV_PREFIX, OpaqueSettings, __env_file__


class Settings(OpaqueSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{ENV_PREFIX}_APPLICATION_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )
