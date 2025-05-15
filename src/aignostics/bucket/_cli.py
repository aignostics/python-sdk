"""CLI of bucket module."""

from typing import Annotated

import typer

from aignostics.utils import console, get_logger

from ._service import Service

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)


cli = typer.Typer(
    name="bucket",
    help="Operations on cloud bucket on Aignostics Platform.",
)


@cli.command()
def ls(
    detail: Annotated[bool, typer.Option(help="Show details")] = False,
) -> None:
    """List objects in bucket on Aignostics Platform."""
    console.print(Service().ls(detail=detail))


@cli.command()
def find(
    detail: Annotated[bool, typer.Option(help="Show details")] = False,
) -> None:
    """Find objects in bucket on Aignostics Platform."""
    console.print(Service().find(detail=detail))


@cli.command()
def delete(
    key: Annotated[str, typer.Argument(help="key of object in object")],
) -> None:
    """Find objects in bucket on Aignostics Platform."""
    deleted = Service().delete_objects([key])
    if deleted:
        console.print(f"Deleted object with key '{key}'")
    else:
        console.print(f"Object with key '{key}' not found")


@cli.command()
def purge() -> None:
    """Purge all objects in bucket on Aignostics Platform."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)
