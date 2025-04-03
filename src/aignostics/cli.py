"""CLI (Command Line Interface) of Aignostics Python SDK."""

from typing import Annotated

import typer
import yaml
from rich.console import Console

import aignostics.client

from . import APIVersion, InfoOutputFormat, OpenAPIOutputFormat, Service, __version__
from .utils import prepare_cli

cli = typer.Typer(name="Command Line Interface of Aignostics Python SDK")
applications_app = typer.Typer()
cli.add_typer(applications_app, name="applications", help="Manage AI applications")
runs_app = typer.Typer()
cli.add_typer(runs_app, name="runs", help="Manage AI runs")
diagnostics_app = typer.Typer()
cli.add_typer(diagnostics_app, name="system", help="System diagnostics")

_service = Service()
_console = Console()


@applications_app.command("list")
def applications_list() -> None:
    """List AI applications."""
    papi_client = aignostics.client.Client()
    applications = papi_client.applications.list()
    _console.print(applications)


@runs_app.command("list")
def runs_list() -> None:
    """List runs."""
    papi_client = aignostics.client.Client()
    runs = papi_client.runs.list()
    _console.print(runs)


@diagnostics_app.command("health")
def health() -> None:
    """Indicate if service is healthy."""
    _console.print(_service.healthy())


@diagnostics_app.command("info")
def info(
    output_format: Annotated[
        InfoOutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = InfoOutputFormat.YAML,
    env: Annotated[bool, typer.Option(help="Include environment variables in output")] = False,
    filter_secrets: Annotated[bool, typer.Option(help="Filter out secret values from environment variables")] = True,
) -> None:
    """Print info about service configuration."""
    info = _service.info(env=env, filter_secrets=filter_secrets)
    match output_format:
        case InfoOutputFormat.JSON:
            _console.print_json(data=info)
        case InfoOutputFormat.YAML:
            _console.print(yaml.dump(info, default_flow_style=False), end="")


@diagnostics_app.command("openapi")
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


prepare_cli(cli, f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻")

if __name__ == "__main__":
    cli()
