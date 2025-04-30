"""Graphical User Interface (GUI) of Aignostics Python SDK."""

from aignostics.utils import gui_run

# For development run via `uv run watch_gui.py`
gui_run(native=False, show=True, watch=True, dark_mode=False)
