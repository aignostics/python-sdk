"""Dummy CLI for integration testing of plugin CLI command registration."""

import typer

cli = typer.Typer(name="dummy-plugin", help="Dummy plugin CLI for integration testing.")


@cli.command("hello")
def hello() -> None:
    """Print a greeting."""
    typer.echo("Hello from dummy plugin!")
