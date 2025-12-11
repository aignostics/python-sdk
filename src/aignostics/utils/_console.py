"""Themed rich console."""

import os

from rich.console import Console
from rich.theme import Theme


def _get_console() -> Console:
    """Get a themed rich console.

    The console width can be set via the AIGNOSTICS_CONSOLE_WIDTH environment variable.

    Returns:
        Console: The themed rich console.
    """
    return Console(
        theme=Theme({
            "logging.level.info": "purple4",
            "debug": "light_cyan3",
            "success": "green",
            "info": "purple4",
            "warning": "yellow1",
            "error": "red1",
        }),
        width=int(os.environ.get("AIGNOSTICS_CONSOLE_WIDTH", "0")) or None,
        legacy_windows=False,  # Modern Windows (10+) doesn't need width adjustment
    )


console = _get_console()
