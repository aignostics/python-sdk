"""System CLI commands."""

import json
import sys
from enum import StrEnum
from importlib.util import find_spec
from typing import Annotated

import typer
import yaml

from ..constants import API_VERSIONS  # noqa: TID252
from ..utils import console, get_logger  # noqa: TID252
from ._service import Service

logger = get_logger(__name__)

cli = typer.Typer(name="system", help="Determine health, info and further utillities.")

_service = Service()

HTTP_PROXY_DEFAULT_HOST = "proxy.charite.de"
HTTP_PROXY_DEFAULT_PORT = 8080
HTTP_PROXY_DEFAULT_SCHEME = "http"


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
def health(
    output_format: Annotated[
        OutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OutputFormat.JSON,
) -> None:
    """Determine and print system health.

    Args:
        output_format (OutputFormat): Output format (JSON or YAML).
    """
    match output_format:
        case OutputFormat.JSON:
            console.print_json(data=_service.health().model_dump())
        case OutputFormat.YAML:
            console.print(
                yaml.dump(data=json.loads(_service.health().model_dump_json()), width=80, default_flow_style=False),
                end="",
            )


@cli.command()
def info(
    include_environ: Annotated[bool, typer.Option(help="Include environment variables")] = False,
    filter_secrets: Annotated[bool, typer.Option(help="Filter secrets")] = True,
    output_format: Annotated[
        OutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OutputFormat.JSON,
) -> None:
    """Determine and print system info.

    Args:
        include_environ (bool): Include environment variables.
        filter_secrets (bool): Filter secrets from the output.
        output_format (OutputFormat): Output format (JSON or YAML).
    """
    info = _service.info(include_environ=include_environ, filter_secrets=filter_secrets)
    match output_format:
        case OutputFormat.JSON:
            console.print_json(data=info)
        case OutputFormat.YAML:
            console.print(yaml.dump(info, width=80, default_flow_style=False), end="")


if find_spec("nicegui"):
    from ..utils import gui_run  # noqa: TID252

    @cli.command()
    def serve(
        host: Annotated[str, typer.Option(help="Host to bind the server to")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="Port to bind the server to")] = 8000,
        open_browser: Annotated[bool, typer.Option(help="Open app in browser after starting the server")] = False,
    ) -> None:
        """Start the web server, hosting the graphical web application and/or webservice API.

        Args:
            host (str): Host to bind the server to.
            port (int): Port to bind the server to.
            watch (bool): Enable auto-reload on changes of source code.
            open_browser (bool): Open app in browser after starting the server.
        """
        console.print(f"Starting web application server at http://{host}:{port}")
        gui_run(native=False, host=host, port=port, with_api=False, show=open_browser)


@cli.command()
def openapi(
    api_version: Annotated[
        str, typer.Option(help=f"API Version. Available: {', '.join(API_VERSIONS.keys())}", case_sensitive=False)
    ] = next(iter(API_VERSIONS.keys())),
    output_format: Annotated[
        OutputFormat, typer.Option(help="Output format", case_sensitive=False)
    ] = OutputFormat.JSON,
) -> None:
    """Dump the OpenAPI specification.

    Args:
        api_version (str): API version to dump.
        output_format (OutputFormat): Output format (JSON or YAML).

    Raises:
        typer.Exit: If an invalid API version is provided.
    """
    match api_version:
        case "v1":
            schema = Service.openapi_schema()
        case _:
            available_versions = ", ".join(API_VERSIONS.keys())
            console.print(
                f"[bold red]Error:[/] Invalid API version '{api_version}'. Available versions: {available_versions}"
            )
            raise typer.Exit(code=1)
    match output_format:
        case OutputFormat.JSON:
            console.print_json(data=schema)
        case OutputFormat.YAML:
            console.print(yaml.dump(schema, default_flow_style=False), end="")


@cli.command()
def install() -> None:
    """Complete installation."""
    console.print("Installation complete!")


@cli.command("whoami")
def whoami() -> None:
    """Print user info."""
    console.print("TK (whoami)")


config_app = typer.Typer()
cli.add_typer(config_app, name="config", help="Configure application settings.")


@config_app.command()
def get(key: Annotated[str, typer.Argument(help="Configuration key to get value for")]) -> None:
    """Set a configuration key to a value."""
    console.print(Service.dotenv_get(key.upper()))


@config_app.command()
def set(  # noqa: A001
    key: Annotated[str, typer.Argument(help="Configuration key to set")],
    value: Annotated[str, typer.Argument(help="Value to set for the configuration key")],
) -> None:
    """Set a configuration key to a value."""
    key = key.upper()
    try:
        Service.dotenv_set(key, value)
    except ValueError as e:
        console.print(f"Invalid configuration: {e!s}", style="error")
        sys.exit(2)
    console.print(f"Configuration '{key}' set to '{value}'.", style="success")


@config_app.command()
def unset(
    key: Annotated[str, typer.Argument(help="Configuration key to unset")],
) -> None:
    """Set a configuration key to a value."""
    key = key.upper()
    Service.dotenv_unset(key)
    console.print(f"Configuration '{key}' unset.", style="success")


@config_app.command()
def remote_diagnostics_enable() -> None:
    """Enable remote diagnostics via Sentry and Logfire. Data stored in EU data centers."""
    try:
        Service.remote_diagnostics_enable()
        console.print("Remote diagnostics enabled.", style="success")
    except ValueError as e:
        console.print(f"Invalid diagnostics configuration: {e!s}", style="error")
        sys.exit(2)


@config_app.command()
def remote_diagnostics_disable() -> None:
    """Disable remote diagnostics."""
    try:
        Service.remote_diagnostics_disable()
        console.print("Remote diagnostics disabled.", style="success")
    except ValueError as e:
        console.print(f"Invalid diagnostics configuration: {e!s}", style="error")
        sys.exit(2)


@config_app.command()
def http_proxy_enable(
    host: Annotated[str, typer.Option(help="Host")] = HTTP_PROXY_DEFAULT_HOST,
    port: Annotated[int, typer.Option(help="Port")] = HTTP_PROXY_DEFAULT_PORT,
    scheme: Annotated[str, typer.Option(help="Scheme")] = HTTP_PROXY_DEFAULT_SCHEME,
    ssl_cert_file: Annotated[str | None, typer.Option(help="SSL certificate file")] = None,
    no_ssl_verify: Annotated[bool, typer.Option(help="Disable SSL verification")] = False,
) -> None:
    """Enable HTTP proxy."""
    try:
        Service().http_proxy_enable(
            host=host, port=port, scheme=scheme, ssl_cert_file=ssl_cert_file, no_ssl_verify=no_ssl_verify
        )
        console.print("HTTP proxy enabled.", style="success")
    except ValueError as e:
        console.print(f"Invalid HTTP proxy configuration: {e!s}", style="error")
        sys.exit(2)


@config_app.command()
def http_proxy_disable() -> None:
    """Disable HTTP proxy."""
    try:
        Service.http_proxy_disable()
        console.print("HTTP proxy disabled.", style="success")
    except ValueError as e:
        console.print(f"Invalid HTTP proxy configuration: {e!s}", style="error")
        sys.exit(2)
