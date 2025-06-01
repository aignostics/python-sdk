"""CLI of bucket module."""

import datetime
from pathlib import Path
from typing import Annotated

import humanize
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
def upload(
    source: Annotated[
        Path,
        typer.Argument(
            help="Source file or directory to upload",
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=False,
            readable=True,
            resolve_path=False,
        ),
    ],
    destination_prefix: Annotated[
        str,
        typer.Option(
            help="Destination layout. Supports {username}, {timestamp}. "
            'E.g. you might want to use "{username}/myproject/"'
        ),
    ] = "{username}",
) -> None:
    """Upload file or directory to bucket in Aignostics platform."""
    import psutil  # noqa: PLC0415
    from rich.progress import (  # noqa: PLC0415
        BarColumn,
        FileSizeColumn,
        Progress,
        TaskProgressColumn,
        TextColumn,
        TimeRemainingColumn,
        TotalFileSizeColumn,
        TransferSpeedColumn,
    )

    console.print(f"Uploading {source} to bucket...")

    # Create a counter for total bytes
    total_bytes = 0
    files_count = 0

    # First, calculate total size and count files
    if source.is_file():
        total_bytes = source.stat().st_size
        files_count = 1
    else:
        for file_path in source.glob("**/*"):
            if file_path.is_file():
                total_bytes += file_path.stat().st_size
                files_count += 1

    console.print(f"Found {files_count} files with total size of {humanize.naturalsize(total_bytes)}")

    # Generate base prefix with placeholders replaced
    username = psutil.Process().username()
    timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d_%H%M%S")

    # Replace placeholders in the destination_prefix
    base_prefix = destination_prefix.format(username=username, timestamp=timestamp)

    # Remove leading/trailing slashes for consistency
    base_prefix = base_prefix.strip("/")

    with Progress(
        TextColumn(
            f"[progress.description]Uploading from {source.name} to "
            f"{Service().get_bucket_protocol()}:/{Service().get_bucket_name()}/{base_prefix}"
        ),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        # Create a task for overall progress
        task = progress.add_task(f"Uploading to {base_prefix}/...", total=total_bytes)

        # Callback function to update progress
        def update_progress(bytes_uploaded: int, file: Path) -> None:
            relpath = file.relative_to(source)
            progress.update(task, advance=bytes_uploaded, description=f"{relpath}")

        # Upload with progress reporting
        results = Service().upload(source, base_prefix, update_progress)

    # Print results summary
    if results["success"]:
        console.print(f"[green]Successfully uploaded {len(results['success'])} files:[/green]")
        for key in results["success"]:
            console.print(f"  [green]- {key}[/green]")

    if results["failed"]:
        console.print(f"[red]Failed to upload {len(results['failed'])} files:[/red]")
        for key in results["failed"]:
            console.print(f"  [red]- {key}[/red]")

    if not results["failed"]:
        console.print("[green]All files uploaded successfully![/green]")


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
