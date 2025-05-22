"""Settings of the bucket module."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from ..utils import OpaqueSettings, __env_file__, __project_name__  # noqa: TID252


class BucketProtocol(StrEnum):
    GS = "gs"
    S3 = "s3"


class Settings(OpaqueSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_BUCKET_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )

    protocol: Annotated[
        BucketProtocol,
        Field(
            description=("Protocol to access the cloud bucket, default is gs"),
            default="gs",
        ),
    ]

    name: Annotated[
        str,
        Field(description=("Name of the cloud bucket")),
    ]

    region_name: Annotated[
        str,
        Field(description=("Region of the cloud bucket"), default="EUROPE-WEST3"),
    ]

    hmac_access_key_id: Annotated[
        SecretStr,
        Field(description=("HMAC access key ID of the cloud bucket")),
    ]

    hmac_secret_access_key: Annotated[
        SecretStr,
        Field(description=("HMAC secret access key of the cloud bucket")),
    ]
