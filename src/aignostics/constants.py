"""Static configuration of Aignostics Python SDK."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from aignostics.utils import __version__

if TYPE_CHECKING:
    from sentry_sdk.integrations import Integration

# Configuration required by oe-python-template
API_VERSIONS: dict[str, str] = {"v1": __version__}
NOTEBOOK_DEFAULT = Path(__file__).parent / "notebook" / "_notebook.py"

SENTRY_INTEGRATIONS: "list[Integration] | None" = None
try:
    from sentry_sdk.integrations.loguru import LoggingLevels, LoguruIntegration
    from sentry_sdk.integrations.typer import TyperIntegration

    SENTRY_INTEGRATIONS = [
        TyperIntegration(),
        LoguruIntegration(
            level=LoggingLevels.INFO.value,  # Capture INFO and above as breadcrumbs
            event_level=LoggingLevels.ERROR.value,  # Send ERROR logs as events
            sentry_logs_level=LoggingLevels.TRACE.value,  # Capture TRAVCE and above as logs
        ),
    ]
except ImportError:
    pass  # se

# Project specific configuration
os.environ["MATPLOTLIB"] = "false"
os.environ["NICEGUI_STORAGE_PATH"] = str(Path.home().resolve() / ".aignostics" / ".nicegui")

HETA_APPLICATION_ID = "he-tme"
TEST_APP_APPLICATION_ID = "test-app"
WSI_SUPPORTED_FILE_EXTENSIONS = {".dcm", ".tiff", ".tif", ".svs"}
WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP = {".tiff"}

WINDOW_TITLE = "Aignostics Launchpad"

# Deprecation of the Aignostics Python SDK
PLATFORM_API_DOCS_URL = "https://platform.aignostics.com/api/v1/docs"
CONSOLE_URL = "https://platform.aignostics.com"
DEPRECATION_NOTICE = (
    "The Aignostics Python SDK is deprecated and gets only bug fixes and security fixes until April 30, 2027. "
    "After that date, the repository and the PyPI project are archived. "
    f"Use the Aignostics Platform REST API ({PLATFORM_API_DOCS_URL}) or the Console ({CONSOLE_URL})."
)
# Organizations with internal/advanced access (e.g., platform-wide queue visibility, GPU config)
INTERNAL_ORGS = {"aignostics", "pre-alpha-org", "lmu", "charite"}
