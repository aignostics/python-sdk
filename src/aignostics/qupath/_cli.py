"""CLI of QuPath module."""

import platform
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

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
        pid = Service.execute_qupath(project=project, image=image, script=script)
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
def processes(
    json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output the running QuPath processes as JSON.",
            is_flag=True,
        ),
    ],
) -> None:
    """List running QuPath processes.

    Notice: This will not list processes that are not started from the installation directory.
    """
    try:
        processes = Service.get_qupath_processes()
        if not processes:
            console.print("No running QuPath processes found.", style="warning")
            sys.exit(0)
        if json:
            process_info = [
                {
                    "pid": process.pid,
                    "exe": process.exe() or "N/A",
                    "cwd": process.cwd() or "N/A",
                    "args": " ".join(process.cmdline()[1:]) if len(process.cmdline()) > 1 else "N/A",
                }
                for process in processes
            ]
            console.print_json(data=process_info)
            return
        process_table = Table(title="Running QuPath Processes")
        process_table.add_column("Process ID", justify="right", style="cyan")
        process_table.add_column("Executable", style="green")
        process_table.add_column("Working Directory", style="yellow")
        process_table.add_column("Arguments", style="blue")
        for process in processes:
            process_table.add_row(
                str(process.pid),
                process.exe() or "N/A",
                process.cwd() or "N/A",
                " ".join(process.cmdline()[1:]) if len(process.cmdline()) > 1 else "N/A",
            )
        console.print(process_table)
    except Exception as e:
        message = f"Failed to determine running QuPath processes: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command()
def terminate() -> None:
    """Terminate running QuPath processes.

    Notice: This will not terminate processes that are not started from the installation directory.
    """
    try:
        terminated_count = Service.terminate_qupath_processes()
        if terminated_count == 0:
            console.print("No running QuPath processes found to terminate.", style="warning")
            sys.exit(2)
        else:
            console.print(f"Terminated {terminated_count} running QuPath processes.", style="success")
    except Exception as e:
        message = f"Failed to determine running QuPath processes: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


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
        info = Service().inspect(project=project)
        console.print_json(data=info.model_dump())
    except Exception as e:
        message = f"Failed to read project: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)


@cli.command(name="run-script")
def run_script(
    script: Annotated[
        Path,
        typer.Argument(
            help="Path to the Groovy script file to execute.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    project: Annotated[
        Path | None,
        typer.Option(
            "--project",
            "-p",
            help="Path to the QuPath project directory.",
            exists=False,
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
            "--image",
            "-i",
            help="Name of the image in the project or path to image file.",
        ),
    ] = None,
    args: Annotated[
        list[str] | None,
        typer.Option(
            "--args",
            "-a",
            help="Arguments to pass to the script. Can be specified multiple times.",
        ),
    ] = None,
) -> None:
    """Run a QuPath Groovy script with optional arguments."""
    try:
        if not Service().is_qupath_installed():
            console.print("QuPath is not installed. Use 'uvx aignostics qupath install' to install it.")
            sys.exit(2)

        # Validate script file exists
        if not script.is_file():
            console.print(f"Script file not found: {script}", style="error")
            sys.exit(1)

        pid = Service.execute_qupath(
            quiet=True,
            project=project,
            image=image,
            script=script,
            script_args=args,
        )

        if not pid:
            console.print("QuPath script could not be executed.", style="error")
            sys.exit(1)

        message = f"QuPath script executed successfully with process id '{pid}'."
        console.print(message, style="success")

        if args:
            console.print(f"Script arguments: {' '.join(args)}", style="info")

    except Exception as e:
        message = f"Failed to run QuPath script: {e!s}."
        logger.exception(message)
        console.print(message, style="error")
        sys.exit(1)
