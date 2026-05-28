"""Full utils — re-exports slim aignostics_sdk.utils and adds heavy-only utilities."""

from __future__ import annotations

from aignostics_sdk.utils import (
    ENV_PREFIX,
    SUBPROCESS_CREATION_FLAGS,
    UNHIDE_SENSITIVE_INFO,
    BaseService,
    Health,
    HealthStatus,
    LogSettings,
    OpaqueSettings,
    ProcessInfo,
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
    boot,
    console,
    get_process_info,
    get_user_data_directory,
    load_settings,
    open_user_data_directory,
    prepare_cli,
    sanitize_path,
    sanitize_path_component,
    strip_to_none_before_validator,
    user_agent,
)

from ._di import discover_plugin_packages, load_modules, locate_implementations, locate_subclasses
from ._mcp import MCP_SERVER_NAME, MCP_TRANSPORT, mcp_create_server, mcp_discover_servers, mcp_list_tools, mcp_run
from ._nav import BaseNavBuilder, NavGroup, NavItem, gui_get_nav_groups

__all__ = [
    "ENV_PREFIX",
    "MCP_SERVER_NAME",
    "MCP_TRANSPORT",
    "SUBPROCESS_CREATION_FLAGS",
    "UNHIDE_SENSITIVE_INFO",
    "BaseNavBuilder",
    "BaseService",
    "Health",
    "HealthStatus",
    "LogSettings",
    "NavGroup",
    "NavItem",
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
    "discover_plugin_packages",
    "get_process_info",
    "get_user_data_directory",
    "gui_get_nav_groups",
    "load_modules",
    "load_settings",
    "locate_implementations",
    "locate_subclasses",
    "mcp_create_server",
    "mcp_discover_servers",
    "mcp_list_tools",
    "mcp_run",
    "open_user_data_directory",
    "prepare_cli",
    "sanitize_path",
    "sanitize_path_component",
    "strip_to_none_before_validator",
    "user_agent",
]

from importlib.util import find_spec

if find_spec("sentry"):
    from aignostics_sdk.utils import SentrySettings

    __all__ += ["SentrySettings"]

if find_spec("nicegui"):
    from ._gui import BasePageBuilder, GUILocalFilePicker, gui_register_pages, gui_run

    __all__ += ["BasePageBuilder", "GUILocalFilePicker", "gui_register_pages", "gui_run"]

if find_spec("marimo"):
    from aignostics_sdk.utils import create_marimo_app

    __all__ += ["create_marimo_app"]
