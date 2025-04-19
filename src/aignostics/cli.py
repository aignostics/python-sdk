"""CLI (Command Line Interface) of Aignostics Python SDK."""

import sys
from importlib.util import find_spec
from typing import Annotated

import typer

from .constants import MODULES_TO_INSTRUMENT
from .utils import __version__, boot, console, get_logger, prepare_cli

boot(MODULES_TO_INSTRUMENT)
logger = get_logger(__name__)

cli = typer.Typer(help="Command Line Interface of ")
prepare_cli(cli, f"🧠 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻")


if find_spec("nicegui"):
    from aignostics.gui import run

    @cli.command(name="gui", help="Start GUI")
    def gui(
        in_browser: Annotated[bool, typer.Option(help="Run the GUI in a web browser")] = False,
    ) -> None:
        """Start GUI."""
        run(in_browser=in_browser, watch=False)


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except Exception as e:  # noqa: BLE001
        logger.critical("Fatal error occurred: %s", e)
        console.print(f"Fatal error occurred: {e}", style="error")
        sys.exit(1)
