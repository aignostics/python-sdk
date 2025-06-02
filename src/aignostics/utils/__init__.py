"""Utilities module."""

from ._cli import prepare_cli
from ._console import console
from ._constants import (
    __author_email__,
    __author_name__,
    __base__url__,
    __documentation__url__,
    __env__,
    __env_file__,
    __is_development_mode__,
    __is_running_in_container__,
    __is_running_in_read_only_environment__,
    __project_name__,
    __project_path__,
    __repository_url__,
    __version__,
)
from ._di import load_modules, locate_implementations, locate_subclasses
from ._fs import sanitize_path, sanitize_path_component
from ._health import Health
from ._log import LogSettings, get_logger
from ._logfire import LogfireSettings
from ._process import ProcessInfo, get_process_info
from ._sentry import SentrySettings
from ._service import BaseService
from ._settings import UNHIDE_SENSITIVE_INFO, OpaqueSettings, load_settings, strip_to_none_before_validator
from .boot import boot

__all__ = [
    "UNHIDE_SENSITIVE_INFO",
    "BaseService",
    "Health",
    "LogSettings",
    "LogSettings",
    "LogfireSettings",
    "OpaqueSettings",
    "ProcessInfo",
    "SentrySettings",
    "__author_email__",
    "__author_name__",
    "__base__url__",
    "__documentation__url__",
    "__env__",
    "__env_file__",
    "__is_development_mode__",
    "__is_running_in_container__",
    "__is_running_in_read_only_environment__",
    "__project_name__",
    "__project_path__",
    "__repository_url__",
    "__version__",
    "boot",
    "console",
    "get_logger",
    "get_process_info",
    "load_modules",
    "load_settings",
    "locate_implementations",
    "locate_subclasses",
    "prepare_cli",
    "sanitize_path",
    "sanitize_path_component",
    "strip_to_none_before_validator",
]

from importlib.util import find_spec

if find_spec("nicegui"):
    from ._gui import BasePageBuilder, GUILocalFilePicker, gui_register_pages, gui_run

    __all__ += ["BasePageBuilder", "GUILocalFilePicker", "gui_register_pages", "gui_run"]

if find_spec("marimo"):
    from ._notebook import create_marimo_app

    __all__ += [
        "create_marimo_app",
    ]
