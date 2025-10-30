"""Static configuration of Aignostics Python SDK."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentry_sdk.integrations import Integration

# Configuration required by oe-python-template
API_VERSIONS: dict[str, str] = {"v1": "1.0.0"}
LOGFIRE_MODULES_TO_INSTRUMENT: list[str] = ["aignostics.qupath"]

SENTRY_INTEGRATIONS: list[Integration] | None = None
try:
    from sentry_sdk.integrations.typer import TyperIntegration

    SENTRY_INTEGRATIONS = [TyperIntegration()]
except ImportError:
    pass  # sentry_sdk not installed

NOTEBOOK_DEFAULT = Path(__file__).parent / "notebook" / "_notebook.py"

# Project specific configuration
os.environ["MATPLOTLIB"] = "false"
os.environ["NICEGUI_STORAGE_PATH"] = str(Path.home().resolve() / ".aignostics" / ".nicegui")

HETA_APPLICATION_ID = "he-tme"
TEST_APP_APPLICATION_ID = "test-app"
WSI_SUPPORTED_FILE_EXTENSIONS = {".dcm", ".tiff", ".tif", ".svs"}
WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP = {".tiff"}
