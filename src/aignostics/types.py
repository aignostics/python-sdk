"""Types of Aignostics Python SDK."""

import typing as t
from enum import StrEnum

JsonType: t.TypeAlias = list["JsonValue"] | t.Mapping[str, "JsonValue"]
JsonValue: t.TypeAlias = str | int | float | JsonType | None


class APIVersion(StrEnum):
    """
    Enum representing the API versions.

    This enum defines the supported API verions:
    - V1: Output doc for v1 API

    Usage:
        version = APIVersion.V1
        print(f"Using {version} version")

    """

    V1 = "v1"


class OpenAPIOutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - YAML: Output data in YAML format
    - JSON: Output data in JSON format

    Usage:
        format = OpenAPIOutputFormat.YAML
        print(f"Using {format} format")
    """

    YAML = "yaml"
    JSON = "json"


class InfoOutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - YAML: Output data in YAML format
    - JSON: Output data in JSON format

    Usage:
        format = InfoOutputFormat.YAML
        print(f"Using {format} format")
    """

    YAML = "yaml"
    JSON = "json"
