"""CLI of bucket module."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path  # noqa: TC003
from typing import Annotated

import humanize
import typer

from aignostics.utils import console, get_logger, get_user_data_directory

from ._service import DownloadProgress, Service

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

    total_bytes = 0
    files_count = 0

    if source.is_file():
        total_bytes = source.stat().st_size
        files_count = 1
    else:
        for file_path in source.glob("**/*"):
            if file_path.is_file():
                total_bytes += file_path.stat().st_size
                files_count += 1

    console.print(f"Found {files_count} files with total size of {humanize.naturalsize(total_bytes)}")

    username = psutil.Process().username().replace("\\", "_")
    timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d_%H%M%S")
    base_prefix = destination_prefix.format(username=username, timestamp=timestamp)
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
        task = progress.add_task(f"Uploading to {base_prefix}/...", total=total_bytes)

        def update_progress(bytes_uploaded: int, file: Path) -> None:
            relpath = file.relative_to(source)
            progress.update(task, advance=bytes_uploaded, description=f"{relpath}")

        results = Service().upload(source, base_prefix, update_progress)

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
def find(
    what: Annotated[
        list[str] | None,
        typer.Argument(help="Patterns or keys to match object keys against - all if not specified."),
    ] = None,
    what_is_key: Annotated[
        bool,
        typer.Option(
            help="Specify if 'what' is a single object key. If not specified, 'what' is treated as a regex pattern.",
        ),
    ] = False,
    detail: Annotated[bool, typer.Option(help="Show details")] = False,
    signed_urls: Annotated[bool, typer.Option("--signed-urls", help="Include signed download URLs")] = False,
) -> None:
    """Find objects in bucket on Aignostics Platform."""
    try:
        result = Service().find(what, what_is_key, detail, signed_urls)
        console.print_json(json=json.dumps(result, default=str))
    except ValueError as e:
        msg = f"Failed to find objects matching {what or 'all'}: {e!s}"
        logger.exception(msg)
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@cli.command()
def download(
    what: Annotated[
        list[str] | None,
        typer.Argument(help="Patterns or keys to match object keys against - all if not specified."),
    ] = None,
    what_is_key: Annotated[
        bool,
        typer.Option(
            help="Specify if 'what' is a single object key. If not specified, 'what' is treated as a regex pattern.",
        ),
    ] = False,
    destination: Annotated[
        Path,
        typer.Option(
            help="Destination directory to download the matching objects to.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ] = get_user_data_directory("bucket_downloads"),  # noqa: B008
) -> None:
    """Download objects from bucket in Aignostics platform to local directory."""
    service = Service()

    try:
        matched_objects = service.find(what, what_is_key)
        if not matched_objects:
            console.print(f"[warning]No objects found matching {what or 'all'}[/warning]")
            return
    except ValueError as e:
        msg = f"Failed to find objects matching {what or 'all'} on download to {destination}: {e!s}"
        logger.exception(msg)
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    from rich.console import Group  # noqa: PLC0415
    from rich.live import Live  # noqa: PLC0415
    from rich.panel import Panel  # noqa: PLC0415
    from rich.progress import (  # noqa: PLC0415
        BarColumn,
        FileSizeColumn,
        Progress,
        TaskID,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        TotalFileSizeColumn,
        TransferSpeedColumn,
    )

    main_progress = Progress(
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TextColumn("[progress.description]{task.description}"),
    )

    file_progress = Progress(
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("[progress.description]{task.description}"),
    )

    progress_group = Panel(
        Group(main_progress, file_progress),
        title=f"Download objects matching {what or 'all'}",
        subtitle=f"Destination '{destination}'",
    )

    current_file_task: TaskID | None = None
    main_task = main_progress.add_task("", total=len(matched_objects))

    def progress_callback(progress: DownloadProgress) -> None:
        nonlocal current_file_task
        main_progress.update(
            main_task,
            completed=progress.overall_processed,
            description=f"Object {progress.overall_current} of {progress.overall_total}",
        )

        if progress.current_file_key:
            file_description = f"{progress.current_file_key}"
            if current_file_task is None:
                current_file_task = file_progress.add_task(file_description, total=progress.current_file_size)
            file_progress.update(
                current_file_task,
                completed=progress.current_file_downloaded,
                total=progress.current_file_size,
                description=file_description,
            )
        elif current_file_task is not None:
            file_progress.remove_task(current_file_task)
            current_file_task = None

    try:
        with Live(progress_group, console=console, refresh_per_second=10, transient=True):
            result = service.download(what, destination, what_is_key, progress_callback)
    except ValueError as e:
        msg = f"Failed to download objects matching {what or 'all'} to {destination}: {e!s}"
        logger.exception(msg)
        console.print(f"[red]Error:[/red] {e!s}")
        sys.exit(2)

    for downloaded_path in result.downloaded:
        console.print(f"[green]✓[/green] Downloaded: {downloaded_path.name}")

    for failed_key in result.failed:
        console.print(f"[red]✗[/red] Failed: {failed_key}")

    console.print(
        f"[bold]Summary:[/bold] [success]{result.downloaded_count}[/success] downloaded, "
        f"[error]{result.failed_count}[/error] failed, [info]{result.total_count}[/info] total"
    )


@cli.command()
def delete(
    what: Annotated[
        list[str],
        typer.Argument(help="Patterns or keys to match object keys against."),
    ],
    what_is_key: Annotated[
        bool,
        typer.Option(
            help="Specify if 'what' is a single object key. If not specified, 'what' is treated as a regex pattern.",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If set, only determines number of items that would be deleted, without actually deleting.",
        ),
    ] = True,
) -> None:
    """Delete objects in bucket on Aignostics Platform."""
    try:
        deleted_count = Service().delete(what, what_is_key, dry_run)
        if deleted_count > 0:
            action = "Would delete" if dry_run else "Deleted"
            console.print(f"[green]✓[/green] {action} {deleted_count} object(s) matching {what}")
        else:
            console.print(f"[yellow]⚠[/yellow] No objects found matching pattern {what}")
    except ValueError as e:
        msg = f"Failed to delete objects matching {what}: {e!s}"
        logger.exception(msg)
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@cli.command()
def purge(
    dry_run: Annotated[
        bool,
        typer.Option(help="If set, only determines number of items that would be deleted, without actually deleting."),
    ] = True,
) -> None:
    """Purge all objects in bucket on Aignostics Platform."""
    try:
        deleted_count = Service().delete(what=None, what_is_key=False, dry_run=dry_run)
        if deleted_count > 0:
            action = "Would purge bucket by deleting" if dry_run else "Purged bucket by deleting"
            console.print(f"[green]✓[/green] {action} {deleted_count} object(s)")
        else:
            console.print("[yellow]⚠[/yellow] No objects found to purge.")
    except ValueError as e:
        msg = f"Failed to purge bucket: {e!s}"
        logger.exception(msg)
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)
