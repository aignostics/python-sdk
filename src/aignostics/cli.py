"""CLI (Command Line Interface) of Aignostics Python SDK."""

import sys
from importlib.util import find_spec
from itertools import pairwise
from pathlib import Path
from typing import Any

import typer
from loguru import logger
from typer.core import TyperGroup

from aignostics.constants import DEPRECATION_NOTICE, NOTEBOOK_DEFAULT, WINDOW_TITLE
from aignostics.utils import (
    __is_running_in_container__,
    __python_version__,
    __version__,
    console,
    prepare_cli,
)

_JSON_OUTPUT_REQUESTED = "aignostics.json_output_requested"


def _requests_json_output(args: list[str]) -> bool:
    """Check if the command arguments request JSON output.

    Args:
        args (list[str]): Command line arguments.

    Returns:
        bool: True if the arguments contain ``--format json`` or ``--format=json``.
    """
    return "--format=json" in args or any(arg == "--format" and value == "json" for arg, value in pairwise(args))


class _RootGroup(TyperGroup):
    """Root command group that records if the command arguments request JSON output.

    Click empties ``ctx.args`` before it calls the root callback. So the group records the
    decision in ``ctx.meta`` while it parses the arguments.
    """

    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:  # noqa: ANN401
        """Record if the arguments request JSON output, then parse them.

        Args:
            ctx (Any): Click context of the root command group.
            args (list[str]): Command line arguments.

        Returns:
            list[str]: The remaining arguments.
        """
        ctx.meta[_JSON_OUTPUT_REQUESTED] = _requests_json_output(args)
        return super().parse_args(ctx, args)


cli = typer.Typer(
    cls=_RootGroup,
    help=f"{DEPRECATION_NOTICE}\n\n"
    "Command Line Interface (CLI) of Aignostics Python SDK providing access to Aignostics Platform.",
)


def _print_deprecation_notice(ctx: typer.Context) -> None:
    """Print the deprecation notice to stderr, so that stdout of each command does not change.

    Commands that write JSON (``--format json``) get no notice, because they can write a JSON error object
    to stderr that consumers parse.

    Args:
        ctx (typer.Context): Typer context of the root command.
    """
    if ctx.meta.get(_JSON_OUTPUT_REQUESTED, False):
        return
    typer.secho(DEPRECATION_NOTICE, err=True, fg=typer.colors.YELLOW)


if find_spec("nicegui") and find_spec("webview") and not __is_running_in_container__:

    @cli.command()
    def launchpad() -> None:
        """Open Aignostics Launchpad, the graphical user interface of the Aignostics Platform."""
        from aignostics.utils import gui_run  # noqa: PLC0415

        gui_run(native=True, with_api=False, title=WINDOW_TITLE, icon="🔬")


if find_spec("marimo"):
    from typing import Annotated

    from aignostics.utils import create_marimo_app

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
    cli,
    f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻 // Python v{__python_version__}",
    root_callback=_print_deprecation_notice,
)


if __name__ == "__main__":  # pragma: no cover
    try:
        cli()
    except Exception as e:
        message = f"An error occurred while running the CLI: {e!s}"
        logger.critical(message)
        console.print(message, style="error")
        sys.exit(1)
