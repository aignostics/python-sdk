"""CLI of QuPath module."""

import sys
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

from ._service import QUPATH_VERSION, Service

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
    ] = QUPATH_VERSION,
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
    reinstall: Annotated[
        bool,
        typer.Option(
            help="Reinstall QuPath even if it is already installed. This will overwrite the existing installation.",
        ),
    ] = True,
) -> None:
    """Install Paquo."""
    try:
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
                    completed=application_size,
                    extra_description=application_path,
                )

            application_path = Service().install_qupath(
                version=version,
                path=path,
                reinstall=reinstall,
                download_progress=download_progress,
                extract_progress=extract_progress,
            )

        console.print(f"QuPath v{version} installed successfully at '{application_path!s}'", style="success")
    except Exception as e:
        message = f"Failed to install QuPath version {version} at {path!s}: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def launch() -> None:
    """Launch QuPath application."""
    try:
        if not Service().is_qupath_installed():
            console.print("QuPath is not installed. Use 'uvx aignostics qupath install' to install it.")
            sys.exit(2)
        pid = Service().launch_qupath()
        if not pid:
            console.print("QuPath could not be launched.", style="error")
            sys.exit(1)

        message = f"QuPath launched successfully with process id '{pid}'."
        console.print(message, style="success")
    except Exception as e:
        message = f"Failed to launch QuPath: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def info() -> None:
    """Get info about QuPath installation."""
    try:
        info = Service().get_qupath_info()
        if not info:
            console.print(
                "QuPath is not installed. Use 'uvx aignostics qupath install' to install it.", style="warning"
            )
            sys.exit(2)
        console.print_json(data=info)
    except Exception as e:
        message = f"Failed to get QuPath info: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def settings() -> None:
    """Show settings configured for Paquo based QuPath integration."""
    console.print_json(data=Service().get_paquo_settings())


@cli.command()
def defaults() -> None:
    """Show default settings of Paquo based QuPath integration."""
    console.print_json(data=Service().get_paquo_defaults())


@cli.command()
def uninstall(
    version: Annotated[
        str,
        typer.Option(
            help="Version of QuPath to install. Do not change this unless you know what you are doing.",
        ),
    ] = QUPATH_VERSION,
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
    """Uninstall QuPath application."""
    try:
        uninstalled = Service().uninstall_qupath(version, path)
        if not uninstalled:
            console.print(f"QuPath not installed at {path!s}.", style="warning")
            sys.exit(2)
        console.print("QuPath uninstalled successfully.", style="success")
    except Exception as e:
        message = f"Failed to uninstall QuPath version {version} at {path!s}: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
