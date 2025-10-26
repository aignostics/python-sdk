"""Static configuration of Aignostics Python SDK."""

import os
from pathlib import Path

# Configuration required by oe-python-template
API_VERSIONS: dict[str, str] = {"v1": "1.0.0"}
MODULES_TO_INSTRUMENT: list[str] = ["aignostics.qupath"]
NOTEBOOK_DEFAULT = Path(__file__).parent / "notebook" / "_notebook.py"

# Project specific configuration
os.environ["MATPLOTLIB"] = "false"
os.environ["NICEGUI_STORAGE_PATH"] = str(Path.home().resolve() / ".aignostics" / ".nicegui")

HETA_APPLICATION_ID = "he-tme"
TEST_APP_APPLICATION_ID = "test-app"
WSI_SUPPORTED_FILE_EXTENSIONS = {".dcm", ".tiff", ".tif", ".svs"}
WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP = {".tiff"}
