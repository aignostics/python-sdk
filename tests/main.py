"""Start script for pytest."""

from aignostics.constants import WINDOW_TITLE

from aignostics_sdk.utils import (
    gui_run,
)

gui_run(native=False, with_api=False, title=WINDOW_TITLE, icon="🔬")
