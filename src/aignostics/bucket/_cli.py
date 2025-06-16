"""CLI of bucket module."""

import datetime
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import humanize
import requests
import typer

from aignostics.utils import console, get_logger

from ._service import Service

if TYPE_CHECKING:
    from rich.progress import Progress

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)


cli = typer.Typer(
    name="bucket",
    help="Operations on cloud bucket on Aignostics Platform.",
)


def _find_matching_objects(source_pattern: str) -> list[dict[str, str]]:
    """Find objects in bucket matching the given pattern.
    
    Args:
        source_pattern: Regular expression pattern to match object keys against.
        
    Returns:
        List of dictionaries containing object key and signed download URL.
    """
    all_objects = Service().find()
    logger.debug("Found %d objects in bucket, matching against '%s'...", len(all_objects), source_pattern)

    matched = []
    for obj in all_objects:
        object_key = obj if isinstance(obj, str) else obj.get("key", "")
        if re.match(source_pattern, object_key):
            matched.append({
                "key": object_key,
                "signed_download_url": Service().create_signed_download_url(object_key),
            })
    return matched


def _download_single_file(
    obj: dict[str, str],
    destination: Path,
    file_progress: "Progress",
) -> Path | None:
    """Download a single file and return the output path on success, None on failure.
    
    Args:
        obj: Dictionary containing object key and signed download URL.
        destination: Destination directory for the downloaded file.
        file_progress: Rich Progress instance for tracking individual file progress.
        
    Returns:
        Path to the downloaded file on success, None on failure.
    """
    object_key = obj["key"]
    source_url_signed = obj["signed_download_url"]
    filename = object_key.split("/")[-1]
    output_path = destination / filename

    try:
        response = requests.get(source_url_signed, stream=True, timeout=60)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        # Create a task for individual file progress
        file_task = file_progress.add_task(
            f"Downloading {filename}", total=total_size, extra_description=f"from {object_key}"
        )

        # Write the file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    file_progress.update(file_task, advance=len(chunk))

        # Remove the completed file task
        file_progress.remove_task(file_task)
        return output_path

    except requests.RequestException:
        logger.exception("Failed to download %s", object_key)
        return None


def _create_progress_ui() -> tuple["Progress", "Progress", type, type, type]:
    """Create the progress UI components.

    Returns:
        Tuple of (main_progress, file_progress, panel_class, group_class, live_class) components.
    """
    from rich.console import Group  # noqa: PLC0415
    from rich.live import Live  # noqa: PLC0415
    from rich.panel import Panel  # noqa: PLC0415
    from rich.progress import (  # noqa: PLC0415
        BarColumn,
        FileSizeColumn,
        Progress,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        TotalFileSizeColumn,
        TransferSpeedColumn,
    )

    # Create main progress bar for overall download progress
    main_progress = Progress(
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TextColumn("{task.fields[extra_description]}"),
    )

    # Create individual file progress bar
    file_progress = Progress(
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("{task.fields[extra_description]}"),
    )

    return main_progress, file_progress, Panel, Group, Live


def _download_with_progress(matched: list[dict[str, str]], destination: Path, source_pattern: str) -> None:
    """Download files with progress tracking."""
    main_progress, file_progress, panel_class, group_class, live_class = _create_progress_ui()

    # Create main task for overall progress
    main_task = main_progress.add_task(
        f"Downloading {len(matched)} files",
        total=len(matched),
        extra_description=f"matching '{source_pattern}'"
    )

    # Create progress group
    progress_group = group_class(
        panel_class(main_progress, title="Overall Progress"),
        panel_class(file_progress, title="Current File"),
    )

    downloaded_count = 0
    failed_count = 0

    with live_class(progress_group, console=console, refresh_per_second=10):
        for obj in matched:
            result = _download_single_file(obj, destination, file_progress)

            if result:
                downloaded_count += 1
                console.print(f"[green]✓[/green] Downloaded: {result.name}")
            else:
                failed_count += 1
                console.print(f"[red]✗[/red] Failed: {obj['key']}")

            # Update main progress
            main_progress.update(main_task, advance=1)

    # Final summary
    if downloaded_count > 0:
        console.print(f"[green]Successfully downloaded {downloaded_count} files to {destination}[/green]")

    if failed_count > 0:
        console.print(f"[red]Failed to download {failed_count} files[/red]")


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

    username = psutil.Process().username()
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
def download(
    source: Annotated[
        str,
        typer.Argument(
            help="Interpreted as a regular expression keys of objects in bucket are matched against."
            "All matching objects are downloaded",
        ),
    ],
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
    ] = Path.cwd(),  # noqa: B008
) -> None:
    """Download objects from bucket in Aignsotics platform to local directory."""
    logger.debug("Creating directory '%s' if it does not exist...", destination)
    destination.mkdir(parents=True, exist_ok=True)

    matched = _find_matching_objects(source)

    if not matched:
        console.print(f"[yellow]No objects found matching pattern '{source}'[/yellow]")
        return

    logger.debug("Found %d objects matching '%s' in bucket, downloading to '%s'...", len(matched), source, destination)

    _download_with_progress(matched, destination, source)


@cli.command()
def ls(
    detail: Annotated[bool, typer.Option(help="Show details")] = False,
) -> None:
    """List objects in bucket on Aignostics Platform."""
    console.print_json(json=json.dumps(Service().ls(detail=detail), default=str))


@cli.command()
def find(
    detail: Annotated[bool, typer.Option(help="Show details")] = False,
) -> None:
    """Find objects in bucket on Aignostics Platform."""
    console.print_json(json=json.dumps(Service().find(detail=detail), default=str))


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
