"""CLI (Command Line Interface) of Aignostics Python SDK."""

import sys
from importlib.metadata import entry_points as _entry_points
from importlib.util import find_spec
from pathlib import Path

import typer
from loguru import logger

from aignostics.constants import NOTEBOOK_DEFAULT, WINDOW_TITLE
from aignostics_sdk.utils import (
    __is_running_in_container__,
    __python_version__,
    __version__,
    console,
    prepare_cli,
)

cli = typer.Typer(
    help="Command Line Interface (CLI) of Aignostics Python SDK providing access to Aignostics Platform.",
)

# Mount slim commands from aignostics-sdk (and any other registered plugins) via entry points
for _ep in _entry_points(group="aignostics.cli"):
    cli.add_typer(_ep.load())

if find_spec("nicegui") and find_spec("webview") and not __is_running_in_container__:

    @cli.command()
    def launchpad() -> None:
        """Open Aignostics Launchpad, the graphical user interface of the Aignostics Platform."""
        from aignostics.utils import gui_run  # noqa: PLC0415

        gui_run(native=True, with_api=False, title=WINDOW_TITLE, icon="🔬")


if find_spec("marimo"):
    from typing import Annotated

    from aignostics_sdk.utils import create_marimo_app

    @cli.command()
    def notebook(
        host: Annotated[str, typer.Option(help="Host to bind the server to")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="Port to bind the server to")] = 8001,
        notebook: Annotated[
            Path,
            typer.Argument(
                help="Path to the notebook file to run. If not provided, a default notebook will be used.",
                exists=True,
                file_okay=True,
                dir_okay=False,
                readable=True,
                show_default="<sdk-install-dir>/notebook/_notebook.py",
            ),
        ] = NOTEBOOK_DEFAULT,
        override_if_exists: Annotated[
            bool,
            typer.Option(
                help="Override the notebook in the user data directory if it already exists.",
            ),
        ] = False,
    ) -> None:
        """Run Python notebook server based on Marimo."""
        import uvicorn  # noqa: PLC0415

        console.print(f"Starting Python notebook server at http://{host}:{port}")
        uvicorn.run(create_marimo_app(notebook=notebook, override_if_exists=override_if_exists), host=host, port=port)


# MCP (Model Context Protocol) server CLI
mcp_cli = typer.Typer(name="mcp", help="MCP (Model Context Protocol) server for AI agent integration.")


@mcp_cli.command("run")
def mcp_run() -> None:
    """Run the MCP server.

    Starts an MCP server using `stdio` transport that exposes SDK functionality
    to AI agents. The server automatically discovers and mounts tools from
    the SDK and any installed plugins.

    Examples:
        uv run aignostics mcp run
    """
    from aignostics.utils import mcp_run  # noqa: PLC0415

    mcp_run()


@mcp_cli.command("list-tools")
def mcp_list_tools() -> None:
    """List all available MCP tools.

    Shows all tools available in the MCP server, including tools from
    the SDK and any installed plugins. Each tool is displayed with its
    name and description.

    Examples:
        uv run aignostics mcp list-tools
    """
    import operator  # noqa: PLC0415

    from rich.table import Table  # noqa: PLC0415

    from aignostics.utils import mcp_list_tools  # noqa: PLC0415

    tools = mcp_list_tools()

    if not tools:
        console.print("[dim]No tools discovered[/dim]")
        return

    table = Table(title="Available MCP Tools")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for tool in sorted(tools, key=operator.itemgetter("name")):
        table.add_row(tool["name"], tool["description"])

    console.print(table)


cli.add_typer(mcp_cli)

prepare_cli(
    cli, f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻 // Python v{__python_version__}"
)


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except Exception as e:
        message = f"An error occurred while running the CLI: {e!s}"
        logger.critical(message)
        console.print(message, style="error")
        sys.exit(1)
