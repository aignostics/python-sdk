"""Static configuration of Aignostics Python SDK."""

import os
from pathlib import Path

# Configuration required by oe-python-template
API_VERSIONS: dict[str, str] = {"v1": "1.0.0"}
MODULES_TO_INSTRUMENT: list[str] = ["aignostics.platform", "aignostics.application"]
NOTEBOOK_FOLDER = Path(__file__).parent.parent.parent / "examples"
NOTEBOOK_APP = Path(__file__).parent.parent.parent / "examples" / "notebook.py"

# Project specific configuration
os.environ["MATPLOTLIB"] = "false"
os.environ["NICEGUI_STORAGE_PATH"] = str(Path.home().resolve() / ".aignostics" / ".nicegui")
