"""Constants for the Aignostics Python SDK."""

from pathlib import Path

MODULES_TO_INSTRUMENT = ["aignostics.client", "aignostics.application"]

API_VERSIONS = {
    "v1": "1.0.0",
}

NOTEBOOK_FOLDER = Path(__file__).parent.parent.parent / "examples"
NOTEBOOK_APP = Path(__file__).parent.parent.parent / "examples" / "notebook.py"
