"""This module provides the low-level client interface for interacting with the API of the Aignostics Platform.

The primary class in this module is the `Client` class, serving as the entry point
for authenticated API operations. Login and token management are handled
automatically.

Further operations are encapsulated in the `Service` class, which provides methods
for manual login, logout and getting information about the authenticated user.

Higher level abstractions are provided in the application module.
"""

from aignx.codegen.exceptions import ApiException, NotFoundException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import ApplicationRunStatus, ItemStatus
from aignx.codegen.models import ApplicationVersionReadResponse as ApplicationVersion
from aignx.codegen.models import InputArtifactCreationRequest as InputArtifact
from aignx.codegen.models import InputArtifactReadResponse as InputArtifactData
from aignx.codegen.models import ItemCreationRequest as InputItem
from aignx.codegen.models import ItemResultReadResponse as ItemResult
from aignx.codegen.models import OutputArtifactReadResponse as OutputArtifactData
from aignx.codegen.models import OutputArtifactResultReadResponse as OutputArtifactElement
from aignx.codegen.models import RunReadResponse as ApplicationRunData

from ._cli import cli
from ._client import Client
from ._constants import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
    DEVICE_URL_DEV,
    DEVICE_URL_PRODUCTION,
    DEVICE_URL_STAGING,
    JWS_JSON_URL_DEV,
    JWS_JSON_URL_PRODUCTION,
    JWS_JSON_URL_STAGING,
    REDIRECT_URI_DEV,
    REDIRECT_URI_PRODUCTION,
    REDIRECT_URI_STAGING,
    TOKEN_URL_DEV,
    TOKEN_URL_PRODUCTION,
    TOKEN_URL_STAGING,
)
from ._messages import AUTHENTICATION_FAILED, NOT_YET_IMPLEMENTED, UNKNOWN_ENDPOINT_URL
from ._service import Service, TokenInfo, UserInfo
from ._settings import Settings, settings
from ._utils import (
    calculate_file_crc32c,
    download_file,
    generate_signed_url,
    get_mime_type_for_artifact,
    mime_type_to_file_ending,
)
from .resources.runs import LIST_APPLICATION_RUNS_MAX_PAGE_SIZE, LIST_APPLICATION_RUNS_MIN_PAGE_SIZE, ApplicationRun

__all__ = [
    "API_ROOT_DEV",
    "API_ROOT_PRODUCTION",
    "API_ROOT_STAGING",
    "AUDIENCE_DEV",
    "AUDIENCE_PRODUCTION",
    "AUDIENCE_STAGING",
    "AUTHENTICATION_FAILED",
    "AUTHORIZATION_BASE_URL_DEV",
    "AUTHORIZATION_BASE_URL_PRODUCTION",
    "AUTHORIZATION_BASE_URL_STAGING",
    "DEVICE_URL_DEV",
    "DEVICE_URL_PRODUCTION",
    "DEVICE_URL_STAGING",
    "JWS_JSON_URL_DEV",
    "JWS_JSON_URL_PRODUCTION",
    "JWS_JSON_URL_STAGING",
    "LIST_APPLICATION_RUNS_MAX_PAGE_SIZE",
    "LIST_APPLICATION_RUNS_MIN_PAGE_SIZE",
    "NOT_YET_IMPLEMENTED",
    "NOT_YET_IMPLEMENTED",
    "REDIRECT_URI_DEV",
    "REDIRECT_URI_PRODUCTION",
    "REDIRECT_URI_STAGING",
    "TOKEN_URL_DEV",
    "TOKEN_URL_PRODUCTION",
    "TOKEN_URL_STAGING",
    "UNKNOWN_ENDPOINT_URL",
    "ApiException",
    "Application",
    "ApplicationRun",
    "ApplicationRunData",
    "ApplicationRunStatus",
    "ApplicationRunStatus",
    "ApplicationVersion",
    "Client",
    "InputArtifact",
    "InputArtifactData",
    "InputItem",
    "ItemResult",
    "ItemStatus",
    "NotFoundException",
    "OutputArtifactData",
    "OutputArtifactElement",
    "Service",
    "Settings",
    "TokenInfo",
    "UserInfo",
    "calculate_file_crc32c",
    "cli",
    "download_file",
    "generate_signed_url",
    "get_mime_type_for_artifact",
    "mime_type_to_file_ending",
    "settings",
]
