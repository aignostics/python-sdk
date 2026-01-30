"""CLI (Command Line Interface) of Aignostics Python SDK."""

import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from aignostics.constants import NOTEBOOK_DEFAULT, WINDOW_TITLE
from aignostics.utils import (
    __is_running_in_container__,
    __python_version__,
    __version__,
    console,
    prepare_cli,
)

cli = typer.Typer(
    help="Command Line Interface (CLI) of Aignostics Python SDK providing access to Aignostics Platform.",
)

if find_spec("nicegui") and find_spec("webview") and not __is_running_in_container__:

    @cli.command()
    def launchpad() -> None:
        """Open Aignostics Launchpad, the graphical user interface of the Aignostics Platform."""
        from aignostics.utils import gui_run  # noqa: PLC0415

        gui_run(native=True, with_api=False, title=WINDOW_TITLE, icon="🔬")


if find_spec("marimo"):
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


@mcp_cli.command("install")
def mcp_install() -> None:
    """Configure Claude Desktop to use the Aignostics MCP server.

    This command automatically adds the Aignostics MCP server configuration
    to your Claude Desktop config file on macOS. After running this command,
    restart Claude Desktop to load the MCP server.

    The configuration uses uvx, so no local installation is required.

    Examples:
        aignostics mcp install

    Raises:
        Exit: If not on macOS, if uvx is not found, or if user cancels.
    """
    import json  # noqa: PLC0415
    import platform  # noqa: PLC0415
    import shutil  # noqa: PLC0415

    if platform.system() != "Darwin":
        console.print("[red]Error:[/red] This command is only supported on macOS.", style="error")
        raise typer.Exit(1)

    # Claude Desktop config path on macOS
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    # Find uvx binary
    uvx_path = shutil.which("uvx")
    if not uvx_path:
        console.print("[red]Error:[/red] Could not find 'uvx' binary. Please install uv first.", style="error")
        raise typer.Exit(1)

    # Build the server configuration using uvx
    server_config = {
        "command": uvx_path,
        "args": ["aignostics", "mcp", "run"],
    }

    # Load existing config or create new one
    if config_path.exists():
        with config_path.open() as f:
            config = json.load(f)
        console.print(f"[dim]Found existing config at {config_path}[/dim]")
    else:
        config = {}
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        console.print(f"[dim]Creating new config at {config_path}[/dim]")

    # Initialize mcpServers if not present
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Check if aignostics is already configured
    if "aignostics" in config["mcpServers"]:
        existing = config["mcpServers"]["aignostics"]
        console.print("[yellow]Warning:[/yellow] Aignostics MCP server is already configured:")
        console.print(f"  command: {existing.get('command')}")
        console.print(f"  args: {existing.get('args')}")
        if not typer.confirm("Do you want to overwrite the existing configuration?"):
            console.print("[dim]Configuration unchanged.[/dim]")
            raise typer.Exit(0)

    # Add or update the aignostics server config
    config["mcpServers"]["aignostics"] = server_config

    # Write the config back
    with config_path.open("w") as f:
        json.dump(config, f, indent=2)

    console.print("\n[green]✓[/green] Claude Desktop configured successfully!")
    console.print(f"\n[bold]Configuration written to:[/bold] {config_path}")
    console.print("\n[bold]Server configuration:[/bold]")
    console.print(f"  command: {server_config['command']}")
    console.print(f"  args: {server_config['args']}")
    console.print("\n[yellow]→[/yellow] Please restart Claude Desktop to load the MCP server.")


@mcp_cli.command("run")
def mcp_run() -> None:
    """Run the MCP server with all tools including MCP Apps.

    Starts an MCP server using stdio transport that exposes SDK functionality
    to AI agents. The server discovers and mounts all available MCP servers,
    including those with MCP Apps for interactive visualizations.

    Examples:
        uv run aignostics mcp run
    """
    from aignostics.utils import mcp_run_server  # noqa: PLC0415

    mcp_run_server()


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
