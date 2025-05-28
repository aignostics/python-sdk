"""CLI of QuPath module."""

from pathlib import Path
from typing import Annotated

import typer
from rich.progress import (
    BarColumn,
    FileSizeColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn,
)

from aignostics.utils import console, get_logger

from ._service import Service

logger = get_logger(__name__)


cli = typer.Typer(
    name="qupath",
    help="Interact with QuPath application.",
)


@cli.command()
def install(
    version: Annotated[
        str,
        typer.Option(
            help="Version of QuPath to install. Do not change this unless you know what you are doing.",
        ),
    ] = "0.5.1",
    path: Annotated[
        Path,
        typer.Option(
            help="Path to install QuPath to. If not specified, the default installation path will be used."
            "Do not change this unless you know what you are doing.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ] = Service.get_installation_path(),  # noqa: B008
) -> None:
    """Install Paquo."""
    console.print(f"Installing QuPath version {version} to {path}...")
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("[progress.description]{task.fields[extra_description]}"),
    ) as progress:
        download_task = progress.add_task("Downloading", total=None, extra_description="")
        extract_task = progress.add_task("Extracting", total=None, extra_description="")

        def download_progress(filepath: Path, filesize: int, chunksize: int) -> None:
            progress.update(
                download_task,
                total=filesize,
                advance=chunksize,
                extra_description=filepath.name,
            )

        def extract_progress(application_path: Path, application_size: int) -> None:
            progress.update(
                extract_task,
                total=application_size,
                completed=1.0,
                extra_description=application_path.name,
            )

        application_path = Service().install_qupath(
            version=version, path=path, download_progress=download_progress, extract_progress=None
        )

        console.print(f"QuPath v {version} installed successfully at: {application_path}")


@cli.command()
def defaults() -> None:
    """Show default settings of Paquo based QuPath integration."""
    console.print(Service().get_paquo_defaults())


@cli.command()
def settings() -> None:
    """Show settings configured for Paquo based QuPath integration."""
    console.print(Service().get_paquo_settings())


@cli.command()
def launch() -> None:
    """Launch QuPath application."""
    Service().launch_qupath()
