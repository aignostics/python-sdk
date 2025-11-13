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
