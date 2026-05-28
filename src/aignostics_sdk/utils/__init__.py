"""Utilities module."""

from ._cli import prepare_cli
from ._console import console
from ._constants import (
    ENV_PREFIX,
    __author_email__,
    __author_name__,
    __base__url__,
    __build_number__,
    __documentation__url__,
    __env__,
    __env_file__,
    __is_development_mode__,
    __is_library_mode__,
    __is_running_in_container__,
    __is_running_in_read_only_environment__,
    __is_test_mode__,
    __project_name__,
    __project_path__,
    __python_version__,
    __repository_url__,
    __version__,
    __version_full__,
)
from ._fs import get_user_data_directory, open_user_data_directory, sanitize_path, sanitize_path_component
from ._health import Health, HealthStatus
from ._log import LogSettings
from ._process import SUBPROCESS_CREATION_FLAGS, ProcessInfo, get_process_info
from ._service import BaseService
from ._settings import UNHIDE_SENSITIVE_INFO, OpaqueSettings, load_settings, strip_to_none_before_validator
from ._user_agent import user_agent
from .boot import boot

__all__ = [
    "ENV_PREFIX",
    "SUBPROCESS_CREATION_FLAGS",
    "UNHIDE_SENSITIVE_INFO",
    "BaseService",
    "Health",
    "HealthStatus",
    "LogSettings",
    "OpaqueSettings",
    "ProcessInfo",
    "__author_email__",
    "__author_name__",
    "__base__url__",
    "__build_number__",
    "__documentation__url__",
    "__env__",
    "__env_file__",
    "__is_development_mode__",
    "__is_library_mode__",
    "__is_running_in_container__",
    "__is_running_in_read_only_environment__",
    "__is_test_mode__",
    "__project_name__",
    "__project_path__",
    "__python_version__",
    "__repository_url__",
    "__version__",
    "__version_full__",
    "boot",
    "console",
    "get_process_info",
    "get_user_data_directory",
    "load_settings",
    "open_user_data_directory",
    "prepare_cli",
    "sanitize_path",
    "sanitize_path_component",
    "strip_to_none_before_validator",
    "user_agent",
]

from importlib.util import find_spec

if find_spec("sentry"):
    from ._sentry import SentrySettings

    __all__ += ["SentrySettings"]

if find_spec("marimo"):
    from ._notebook import create_marimo_app

    __all__ += [
        "create_marimo_app",
    ]
