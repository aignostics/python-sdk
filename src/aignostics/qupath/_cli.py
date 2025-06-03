"""CLI of QuPath module."""

import platform
import sys
from pathlib import Path
from typing import Annotated

import typer

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
    platform_system: Annotated[
        str,
        typer.Option(help="Override the system to assume for the installation. This is useful for testing purposes."),
    ] = platform.system(),
    platform_machine: Annotated[
        str,
        typer.Option(
            help="Override the machine architecture to assume for the installation. "
            "This is useful for testing purposes.",
        ),
    ] = platform.machine(),
) -> None:
    """Install QuPath application."""
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
                platform_system=platform_system,
                platform_machine=platform_machine,
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
def launch(
    project: Annotated[
        Path | None,
        typer.Option(
            help="Path to QuPath project directory.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
    image: Annotated[
        str | None,
        typer.Option(
            help="Path to image. Must be part of QuPath project",
        ),
    ] = None,
    script: Annotated[
        Path | None,
        typer.Option(
            help="Path to QuPath script to run on launch. Must be part of QuPath project.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """Launch QuPath application."""
    try:
        if not Service().is_qupath_installed():
            console.print("QuPath is not installed. Use 'uvx aignostics qupath install' to install it.")
            sys.exit(2)
        pid = Service().launch_qupath(project=project, image=image, script=script)
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
    if not Service().is_qupath_installed():
        console.print("QuPath is not installed. Use 'uvx aignostics qupath install' to install it.", style="warning")
        sys.exit(2)
    try:
        console.print_json(data=Service().info())
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
        str | None,
        typer.Option(
            help="Version of QuPath to install. If not specified, all versions will be uninstalled.",
        ),
    ] = None,
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
    platform_system: Annotated[
        str,
        typer.Option(help="Override the system to assume for the installation. This is useful for testing purposes."),
    ] = platform.system(),
    platform_machine: Annotated[
        str,
        typer.Option(
            help="Override the machine architecture to assume for the installation. "
            "This is useful for testing purposes.",
        ),
    ] = platform.machine(),
) -> None:
    """Uninstall QuPath application."""
    try:
        uninstalled = Service().uninstall_qupath(version, path, platform_system, platform_machine)
        if not uninstalled:
            console.print(f"QuPath not installed at {path!s}.", style="warning")
            sys.exit(2)
        console.print("QuPath uninstalled successfully.", style="success")
    except Exception as e:
        message = f"Failed to uninstall QuPath version {version} at {path!s}: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def add(
    project: Annotated[
        Path,
        typer.Argument(
            help="Path to QuPath project directory. Will be created if it does not exist.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    path: Annotated[
        list[Path],
        typer.Argument(
            help="One or multiple paths. A path can point to an individual image or folder."
            "In case of a folder, all images within will be added for supported image types.",
            exists=True,
            file_okay=True,
            dir_okay=True,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Add image(s) to QuPath project. Creates project if it does not exist."""
    try:
        count = Service().add(
            project=project,
            paths=path,
        )
        console.print(f"Added '{count}' images to project '{project}'.", style="success")
    except Exception as e:
        message = f"Failed to add images to project: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def annotate(
    project: Annotated[
        Path,
        typer.Argument(
            help="Path to QuPath project directory. Will be created if it does not exist.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    image: Annotated[
        Path,
        typer.Argument(
            help="Path to image to annotate. If the image is not part of the project, it will be added.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    annotations: Annotated[
        Path,
        typer.Argument(
            help="Path to polygons file to import. The file must be a compatible GeoJSON file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Add image(s) to QuPath project. Creates project if it does not exist."""
    try:
        annotation_count = Service().annotate(project=project, image=image, annotations=annotations)
        console.print(
            f"Added {annotation_count} annotations to {image} in {project}.",
            style="success",
        )
    except Exception as e:
        message = f"Failed to add images to project: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def inspect(
    project: Annotated[
        Path,
        typer.Argument(
            help="Path to QuPath project directory.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Inspect project."""
    try:
        console.print(f"Inspecting project in folder '{project}'...")
        info = Service().inspect(project=project)
        console.print_json(data=info)
    except Exception as e:
        message = f"Failed to read project: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
