"""This module provides the low-level client interface for interacting with the API of the Aignostics Platform.

The primary class in this module is the `Client` class, serving as the entry point
for authenticated API operations. Login and token management are handled
automatically.

Further operations are encapsulated in the `Service` class, which provides methods
for manual login, logout and getting information about the authenticated user.

Higher level abstractions are provided in the application module.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from ._cli import cli_sdk, cli_user
from ._client import Client
from ._constants import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    API_ROOT_TEST,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUDIENCE_TEST,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
    AUTHORIZATION_BASE_URL_TEST,
    CLIENT_ID_INTERACTIVE_DEV,
    CLIENT_ID_INTERACTIVE_PRODUCTION,
    CLIENT_ID_INTERACTIVE_STAGING,
    CLIENT_ID_INTERACTIVE_TEST,
    DEFAULT_CPU_PROVISIONING_MODE,
    DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES,
    DEFAULT_GPU_PROVISIONING_MODE,
    DEFAULT_GPU_TYPE,
    DEFAULT_MAX_GPUS_PER_SLIDE,
    DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES,
    DEVICE_URL_DEV,
    DEVICE_URL_PRODUCTION,
    DEVICE_URL_STAGING,
    DEVICE_URL_TEST,
    JWS_JSON_URL_DEV,
    JWS_JSON_URL_PRODUCTION,
    JWS_JSON_URL_STAGING,
    JWS_JSON_URL_TEST,
    REDIRECT_URI_DEV,
    REDIRECT_URI_PRODUCTION,
    REDIRECT_URI_STAGING,
    REDIRECT_URI_TEST,
    STATUS_PAGE_URL_DEV,
    STATUS_PAGE_URL_PRODUCTION,
    STATUS_PAGE_URL_STAGING,
    STATUS_PAGE_URL_TEST,
    TOKEN_URL_DEV,
    TOKEN_URL_PRODUCTION,
    TOKEN_URL_STAGING,
    TOKEN_URL_TEST,
)
from ._messages import AUTHENTICATION_FAILED, NOT_YET_IMPLEMENTED, UNKNOWN_ENDPOINT_URL
from ._sdk_metadata import (
    PipelineConfig,
    RunSdkMetadata,
    SchedulingMetadata,
)
from ._settings import Settings, settings
from ._utils import (
    calculate_file_crc32c,
    download_file,
    generate_signed_url,
    get_mime_type_for_artifact,
    mime_type_to_file_ending,
)

if TYPE_CHECKING:
    from aignostics_sdk._codegen.exceptions import ApiException, ForbiddenException, NotFoundException
    from aignostics_sdk._codegen.models import ApplicationReadResponse as Application
    from aignostics_sdk._codegen.models import ApplicationReadShortResponse as ApplicationSummary
    from aignostics_sdk._codegen.models import (
        ArtifactOutput,
        ItemOutput,
        ItemState,
        ItemTerminationReason,
        RunItemStatistics,
        RunOutput,
        RunState,
        RunTerminationReason,
    )
    from aignostics_sdk._codegen.models import InputArtifact as InputArtifactData
    from aignostics_sdk._codegen.models import InputArtifactCreationRequest as InputArtifact
    from aignostics_sdk._codegen.models import ItemCreationRequest as InputItem
    from aignostics_sdk._codegen.models import ItemResultReadResponse as ItemResult
    from aignostics_sdk._codegen.models import MeReadResponse as Me
    from aignostics_sdk._codegen.models import OrganizationReadResponse as Organization
    from aignostics_sdk._codegen.models import OutputArtifact as OutputArtifactData
    from aignostics_sdk._codegen.models import OutputArtifactResultReadResponse as OutputArtifactElement
    from aignostics_sdk._codegen.models import RunReadResponse as RunData
    from aignostics_sdk._codegen.models import UserReadResponse as User
    from aignostics_sdk._codegen.models import VersionReadResponse as ApplicationVersion

    from ._exceptions import ConcurrencyConflictError
    from ._service import Service, TokenInfo, UserInfo
    from .resources.applications import ApplicationVersionDocument, Documents
    from .resources.runs import LIST_APPLICATION_RUNS_MAX_PAGE_SIZE, LIST_APPLICATION_RUNS_MIN_PAGE_SIZE, Artifact, Run

# Lazy export map: public_name -> (module_path, original_name_in_module)
_LAZY: dict[str, tuple[str, str]] = {
    # service types (loaded lazily because _service.py imports codegen at module level)
    "Service": ("aignostics_sdk.platform._service", "Service"),
    "TokenInfo": ("aignostics_sdk.platform._service", "TokenInfo"),
    "UserInfo": ("aignostics_sdk.platform._service", "UserInfo"),
    # exceptions
    "ConcurrencyConflictError": ("aignostics_sdk.platform._exceptions", "ConcurrencyConflictError"),
    "ApiException": ("aignostics_sdk._codegen.exceptions", "ApiException"),
    "ForbiddenException": ("aignostics_sdk._codegen.exceptions", "ForbiddenException"),
    "NotFoundException": ("aignostics_sdk._codegen.exceptions", "NotFoundException"),
    # codegen models
    "Application": ("aignostics_sdk._codegen.models", "ApplicationReadResponse"),
    "ApplicationSummary": ("aignostics_sdk._codegen.models", "ApplicationReadShortResponse"),
    "ApplicationVersion": ("aignostics_sdk._codegen.models", "VersionReadResponse"),
    "ArtifactOutput": ("aignostics_sdk._codegen.models", "ArtifactOutput"),
    "InputArtifact": ("aignostics_sdk._codegen.models", "InputArtifactCreationRequest"),
    "InputArtifactData": ("aignostics_sdk._codegen.models", "InputArtifact"),
    "InputItem": ("aignostics_sdk._codegen.models", "ItemCreationRequest"),
    "ItemOutput": ("aignostics_sdk._codegen.models", "ItemOutput"),
    "ItemResult": ("aignostics_sdk._codegen.models", "ItemResultReadResponse"),
    "ItemState": ("aignostics_sdk._codegen.models", "ItemState"),
    "ItemTerminationReason": ("aignostics_sdk._codegen.models", "ItemTerminationReason"),
    "Me": ("aignostics_sdk._codegen.models", "MeReadResponse"),
    "Organization": ("aignostics_sdk._codegen.models", "OrganizationReadResponse"),
    "OutputArtifactData": ("aignostics_sdk._codegen.models", "OutputArtifact"),
    "OutputArtifactElement": ("aignostics_sdk._codegen.models", "OutputArtifactResultReadResponse"),
    "RunData": ("aignostics_sdk._codegen.models", "RunReadResponse"),
    "RunItemStatistics": ("aignostics_sdk._codegen.models", "RunItemStatistics"),
    "RunOutput": ("aignostics_sdk._codegen.models", "RunOutput"),
    "RunState": ("aignostics_sdk._codegen.models", "RunState"),
    "RunTerminationReason": ("aignostics_sdk._codegen.models", "RunTerminationReason"),
    "User": ("aignostics_sdk._codegen.models", "UserReadResponse"),
    # resource types
    "Artifact": ("aignostics_sdk.platform.resources.runs", "Artifact"),
    "Run": ("aignostics_sdk.platform.resources.runs", "Run"),
    "LIST_APPLICATION_RUNS_MAX_PAGE_SIZE": (
        "aignostics_sdk.platform.resources.runs",
        "LIST_APPLICATION_RUNS_MAX_PAGE_SIZE",
    ),
    "LIST_APPLICATION_RUNS_MIN_PAGE_SIZE": (
        "aignostics_sdk.platform.resources.runs",
        "LIST_APPLICATION_RUNS_MIN_PAGE_SIZE",
    ),
    "ApplicationVersionDocument": ("aignostics_sdk.platform.resources.applications", "ApplicationVersionDocument"),
    "Documents": ("aignostics_sdk.platform.resources.applications", "Documents"),
}


def __getattr__(name: str) -> object:
    if name in _LAZY:
        module_path, attr_name = _LAZY[name]
        mod = importlib.import_module(module_path)
        obj = getattr(mod, attr_name)
        globals()[name] = obj  # cache so __getattr__ is not called again
        return obj
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = [
    "API_ROOT_DEV",
    "API_ROOT_PRODUCTION",
    "API_ROOT_STAGING",
    "API_ROOT_TEST",
    "AUDIENCE_DEV",
    "AUDIENCE_PRODUCTION",
    "AUDIENCE_STAGING",
    "AUDIENCE_TEST",
    "AUTHENTICATION_FAILED",
    "AUTHORIZATION_BASE_URL_DEV",
    "AUTHORIZATION_BASE_URL_PRODUCTION",
    "AUTHORIZATION_BASE_URL_STAGING",
    "AUTHORIZATION_BASE_URL_TEST",
    "CLIENT_ID_INTERACTIVE_DEV",
    "CLIENT_ID_INTERACTIVE_PRODUCTION",
    "CLIENT_ID_INTERACTIVE_STAGING",
    "CLIENT_ID_INTERACTIVE_TEST",
    "DEFAULT_CPU_PROVISIONING_MODE",
    "DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES",
    "DEFAULT_GPU_PROVISIONING_MODE",
    "DEFAULT_GPU_TYPE",
    "DEFAULT_MAX_GPUS_PER_SLIDE",
    "DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES",
    "DEVICE_URL_DEV",
    "DEVICE_URL_PRODUCTION",
    "DEVICE_URL_STAGING",
    "DEVICE_URL_TEST",
    "JWS_JSON_URL_DEV",
    "JWS_JSON_URL_PRODUCTION",
    "JWS_JSON_URL_STAGING",
    "JWS_JSON_URL_TEST",
    "LIST_APPLICATION_RUNS_MAX_PAGE_SIZE",
    "LIST_APPLICATION_RUNS_MIN_PAGE_SIZE",
    "NOT_YET_IMPLEMENTED",
    "REDIRECT_URI_DEV",
    "REDIRECT_URI_PRODUCTION",
    "REDIRECT_URI_STAGING",
    "REDIRECT_URI_TEST",
    "STATUS_PAGE_URL_DEV",
    "STATUS_PAGE_URL_PRODUCTION",
    "STATUS_PAGE_URL_STAGING",
    "STATUS_PAGE_URL_TEST",
    "TOKEN_URL_DEV",
    "TOKEN_URL_PRODUCTION",
    "TOKEN_URL_STAGING",
    "TOKEN_URL_TEST",
    "UNKNOWN_ENDPOINT_URL",
    "ApiException",
    "Application",
    "ApplicationSummary",
    "ApplicationVersion",
    "ApplicationVersionDocument",
    "Artifact",
    "ArtifactOutput",
    "Client",
    "ConcurrencyConflictError",
    "Documents",
    "ForbiddenException",
    "InputArtifact",
    "InputArtifactData",
    "InputItem",
    "ItemOutput",
    "ItemResult",
    "ItemState",
    "ItemTerminationReason",
    "Me",
    "NotFoundException",
    "Organization",
    "OutputArtifactData",
    "OutputArtifactElement",
    "PipelineConfig",
    "Run",
    "RunData",
    "RunItemStatistics",
    "RunOutput",
    "RunSdkMetadata",
    "RunState",
    "RunTerminationReason",
    "SchedulingMetadata",
    "Service",
    "Settings",
    "TokenInfo",
    "User",
    "UserInfo",
    "calculate_file_crc32c",
    "cli_sdk",
    "cli_user",
    "download_file",
    "generate_signed_url",
    "get_mime_type_for_artifact",
    "mime_type_to_file_ending",
    "settings",
]
