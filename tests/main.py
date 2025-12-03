"""Start script for pytest."""

from aignostics.utils import (
    gui_run,
)

gui_run(native=False, with_api=False, title="Aignostics Launchpad", icon="🔬")
