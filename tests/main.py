"""Start script for pytest."""

from aignostics.utils import (
    get_logger,
    gui_run,
)

logger = get_logger(__name__)

gui_run(native=False, with_api=False, title="Aignostics Launchpad", icon="🔬")
