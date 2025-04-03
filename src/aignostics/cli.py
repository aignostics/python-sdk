"""CLI (Command Line Interface) of Aignostics Python SDK."""

from typing import Annotated

import typer
import yaml
from rich.console import Console

import aignx.platform

from . import APIVersion, OpenAPIOutputFormat, Service, __version__

cli = typer.Typer(name="Command Line Interface of Aignostics Python SDK")
_service = Service()
_console = Console()


@cli.command()
def health() -> None:
    """Indicate if service is healthy."""
    _console.print(_service.healthy())


@cli.command()
def info() -> None:
    """Print info about service configuration."""
    _console.print(_service.info())


@cli.command()
def papi_applications_list() -> None:
    """Check PAPI health."""
    papi_client = aignx.platform.Client()
    applications = papi_client.applications.list()
    _console.print(applications)


@cli.command()
def openapi(
    api_version: Annotated[APIVersion, typer.Option(help="API Version", case_sensitive=False)] = APIVersion.V1,
    output_format: Annotated[
        OpenAPIOutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OpenAPIOutputFormat.YAML,
) -> None:
    """Dump the OpenAPI specification to stdout (YAML by default)."""
    match api_version:
        case APIVersion.V1:
            schema = Service.openapi_schema()
    match output_format:
        case OpenAPIOutputFormat.JSON:
            _console.print_json(data=schema)
        case OpenAPIOutputFormat.YAML:
            _console.print(yaml.dump(schema, default_flow_style=False), end="")


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
