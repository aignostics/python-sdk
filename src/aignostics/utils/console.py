"""Define styling for typer, overriding defaults."""

from rich.console import Console
from rich.theme import Theme

console = Console(
    theme=Theme({
        "logging.level.info": "purple4",
        "debug": "light_cyan3",
        "info": "purple4",
        "warning": "yellow1",
        "error": "red1",
    }),
)
