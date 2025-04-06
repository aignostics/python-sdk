"""CLI (Command Line Interface) of Aignostics Python SDK."""

from typing import Annotated

import typer
import yaml
from rich.console import Console

import aignostics.client

from . import APIVersion, InfoOutputFormat, OpenAPIOutputFormat, Platform, __version__
from .client import authentication_settings as auth_settings
from .utils import prepare_cli

_console = Console()
_platform = Platform()
cli = typer.Typer(help="Command Line Interface of the aignostics platform")

platform_app = typer.Typer()
cli.add_typer(platform_app, name="platform", help="Platform diagnostics and utilities")

bucket_app = typer.Typer()
platform_app.add_typer(bucket_app, name="bucket", help="Transfer bucket provide by platform")

application_app = typer.Typer()
cli.add_typer(application_app, name="application", help="aignostics applications")

datasset_app = typer.Typer()
application_app.add_typer(datasset_app, name="dataset", help="Datasets for use as input for applications")

metadata_app = typer.Typer()
application_app.add_typer(metadata_app, name="metadata", help="Metadata required as input for applications")

run_app = typer.Typer()
application_app.add_typer(run_app, name="run", help="Runs of applications")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Results of applications runs")


@platform_app.command("install")
def install() -> None:
    """Complete and validate installation of the CLI."""
    _platform.install()


@platform_app.command("health")
def health() -> None:
    """Indicate if aignostics platform is healthy."""
    _console.print(_platform.healthy())


@platform_app.command("info")
def info(
    output_format: Annotated[
        InfoOutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = InfoOutputFormat.YAML,
    env: Annotated[bool, typer.Option(help="Include environment variables in output")] = False,
    filter_secrets: Annotated[bool, typer.Option(help="Filter out secret values from environment variables")] = True,
) -> None:
    """Print info about service configuration."""
    info = _platform.info(env=env, filter_secrets=filter_secrets)
    match output_format:
        case InfoOutputFormat.JSON:
            _console.print_json(data=info)
        case InfoOutputFormat.YAML:
            _console.print(yaml.dump(info, default_flow_style=False), end="")


@platform_app.command("authentication-settings")
def authentication_settings() -> None:
    """Print info about service configuration."""
    print(auth_settings().model_dump())


@platform_app.command("openapi")
def openapi(
    api_version: Annotated[APIVersion, typer.Option(help="API Version", case_sensitive=False)] = APIVersion.V1,
    output_format: Annotated[
        OpenAPIOutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OpenAPIOutputFormat.YAML,
) -> None:
    """Dump the OpenAPI specification of to stdout."""
    match api_version:
        case APIVersion.V1:
            schema = Platform.openapi_schema()
    match output_format:
        case OpenAPIOutputFormat.JSON:
            _console.print_json(data=schema)
        case OpenAPIOutputFormat.YAML:
            _console.print(yaml.dump(schema, default_flow_style=False), end="")


@bucket_app.command("ls")
def bucket_ls() -> None:
    """List contents of tranfer bucket."""
    _console.print("bucket ls")


@bucket_app.command("purge")
def bucket_purge() -> None:
    """Purge content of transfer bucket."""
    _console.print("bucket purged.")


@application_app.command("list")
def application_list() -> None:
    """List available applications."""
    papi_client = aignostics.client.Client()
    applications = papi_client.applications.list()
    _console.print(applications)


@application_app.command("describe")
def application_describe() -> None:
    """Describe application."""
    papi_client = aignostics.client.Client()
    applications = papi_client.applications.list()
    _console.print(applications)


@datasset_app.command("download")
def dataset_download() -> None:
    """Download dataset."""
    _console.print("dataset download")


@metadata_app.command("generate")
def metadata_generate() -> None:
    """Generate metadata."""
    _console.print("generate metadata")


@run_app.command("submit")
def run_submit() -> None:
    """Create run."""
    _console.print("submit run")


@run_app.command("list")
def run_list() -> None:
    """List runs."""
    papi_client = aignostics.client.Client()
    runs = papi_client.runs.list()
    _console.print(runs)


@run_app.command("describe")
def run_describe() -> None:
    """Describe run."""
    _console.print("The run")


@run_app.command("cancel")
def run_cancel() -> None:
    """Cancel run."""
    _console.print("canceled run")


@result_app.command("describe")
def result_describe() -> None:
    """Describe the result of an application run."""
    _console.print("describe result")


@result_app.command("download")
def result_download() -> None:
    """Download the result of an application run."""
    _console.print("download result")


@result_app.command("delete")
def result_delete() -> None:
    """Delete the result of an application run."""
    _console.print("delete resuilt")


prepare_cli(cli, f"🔬 Aignostics Python SDK v{__version__} - built with love in Berlin 🐻")

if __name__ == "__main__":
    cli()
