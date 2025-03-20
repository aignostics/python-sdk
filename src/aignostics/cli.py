"""CLI (Command Line Interface) of Aignostics Python SDK."""

import os
from enum import StrEnum
from typing import Annotated

import typer
import uvicorn
import yaml
from rich.console import Console

from aignostics import Service, __version__
from aignostics.api import api_v1, api_v2

console = Console()

cli = typer.Typer(name="Command Line Interface of Aignostics Python SDK")


@cli.command()
def echo(
    text: Annotated[
        str, typer.Argument(help="The text to echo")
    ] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    json: Annotated[
        bool,
        typer.Option(
            help=("Print as JSON"),
        ),
    ] = False,
) -> None:
    """Echo the text."""
    if json:
        console.print_json(data={"text": text})
    else:
        console.print(text)


@cli.command()
def hello_world() -> None:
    """Print hello world message and what's in the environment variable THE_VAR."""
    console.print(Service.get_hello_world())


@cli.command()
def serve(
    host: Annotated[str, typer.Option(help="Host to bind the server to")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port to bind the server to")] = 8000,
    watch: Annotated[bool, typer.Option(help="Enable auto-reload")] = True,
) -> None:
    """Start the API server."""
    console.print(f"Starting API server at http://{host}:{port}")
    os.environ["UVICORN_HOST"] = host
    os.environ["UVICORN_PORT"] = str(port)
    uvicorn.run(
        "aignostics.api:api",
        host=host,
        port=port,
        reload=watch,
    )


class APIVersion(StrEnum):
    """
    Enum representing the API versions.

    This enum defines the supported API verions:
    - V1: Output doc for v1 API
    - V2: Output doc for v2 API

    Usage:
        version = APIVersion.V1
        print(f"Using {version} version")

    """

    V1 = "v1"
    V2 = "v2"


class OutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - YAML: Output data in YAML format
    - JSON: Output data in JSON format

    Usage:
        format = OutputFormat.YAML
        print(f"Using {format} format")
    """

    YAML = "yaml"
    JSON = "json"


@cli.command()
def openapi(
    api_version: Annotated[APIVersion, typer.Option(help="API Version", case_sensitive=False)] = APIVersion.V1,
    output_format: Annotated[
        OutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OutputFormat.YAML,
) -> None:
    """Dump the OpenAPI specification to stdout (YAML by default)."""
    match api_version:
        case APIVersion.V1:
            schema = api_v1.openapi()
        case APIVersion.V2:
            schema = api_v2.openapi()
    match output_format:
        case OutputFormat.JSON:
            console.print_json(data=schema)
        case OutputFormat.YAML:
            console.print(yaml.dump(schema, default_flow_style=False), end="")


def _apply_cli_settings(cli: typer.Typer, epilog: str) -> None:
    """Add epilog to all typers in the tree and configure default behavior."""
    cli.info.epilog = epilog
    cli.info.no_args_is_help = True
    for command in cli.registered_commands:
        command.epilog = cli.info.epilog


_apply_cli_settings(
    cli,
    f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻",
)


if __name__ == "__main__":
    cli()
