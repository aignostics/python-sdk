"""CLI (Command Line Interface) of Aignostics Python SDK."""

import sys
from importlib.util import find_spec

import typer

from .constants import MODULES_TO_INSTRUMENT
from .utils import __is_running_in_container__, __version__, boot, console, get_logger, prepare_cli

boot(MODULES_TO_INSTRUMENT)
logger = get_logger(__name__)

cli = typer.Typer(help="Command Line Interface of Aignostics Python SDK")
prepare_cli(cli, f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻")


if find_spec("nicegui") and find_spec("webview") and not __is_running_in_container__:

    @cli.command()
    def gui() -> None:
        """Start graphical user interface (GUI) in native window."""
        from .utils import gui_run  # noqa: PLC0415

        gui_run(native=True, with_api=False, title="Aignostics Python SDK", icon="🔬")


if find_spec("marimo"):
    from typing import Annotated

    import uvicorn

    from .utils import create_marimo_app

    @cli.command()
    def notebook(
        host: Annotated[str, typer.Option(help="Host to bind the server to")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="Port to bind the server to")] = 8001,
    ) -> None:
        """Start notebook in web browser."""
        console.print(f"Starting marimo notebook server at http://{host}:{port}")
        uvicorn.run(
            create_marimo_app(),
            host=host,
            port=port,
        )


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except Exception as e:  # noqa: BLE001
        logger.critical("Fatal error occurred: %s", e)
        console.print(f"Fatal error occurred: {e}", style="error")
        sys.exit(1)
