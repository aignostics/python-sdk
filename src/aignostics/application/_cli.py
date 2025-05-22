"""CLI of application module."""

import time
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

from aignostics.bucket import Service as BucketService
from aignostics.platform import NotFoundException
from aignostics.utils import console, get_logger

from ._service import Service
from ._utils import (
    print_runs_non_verbose,
    print_runs_verbose,
    read_metadata_csv_to_dict,
    retrieve_and_print_run_details,
    write_metadata_dict_to_csv,
)

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)

cli = typer.Typer(name="application", help="List and inspect applications on Aignostics Platform.")

run_app = typer.Typer()
cli.add_typer(run_app, name="run", help="List, submit and manage application runs")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Inspect and download application run results")


@cli.command("list")
def application_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
) -> bool:
    """List available applications.

    Args:
        verbose (bool): If True, show detailed information about each application

    Returns:
        bool: Success status of the operation
    """
    try:
        applications = Service().applications()
    except Exception as e:
        logger.exception("Failed to list applications")
        console.print(f"[error]Error:[/error] Failed to list applications: {e}")
        return False

    app_count = 0

    if verbose:
        console.print("[bold]Available Applications:[/bold]")
        console.print("=" * 80)

        for app in applications:
            app_count += 1
            console.print(f"[bold]Application ID:[/bold] {app.application_id}")
            console.print(f"[bold]Name:[/bold] {app.name}")
            console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(app.regulatory_classes)}")

            # Display available versions
            try:
                versions = Service().application_versions(app)
            except Exception as e:
                logger.exception("Failed to list versions for application '%s'", app.application_id)
                console.print(
                    f"[error]Error:[/error] Failed to list versions for application '{app.application_id}': {e}"
                )
                continue
            if versions:
                console.print("[bold]Available Versions:[/bold]")
                for version in versions:
                    console.print(f"  - {version.version} ({version.application_version_id})")
                    console.print(f"    Changelog: {version.changelog}")

                    # Count input and output artifacts
                    num_inputs = len(version.input_artifacts)
                    num_outputs = len(version.output_artifacts)
                    console.print(f"    Artifacts: {num_inputs} input(s), {num_outputs} output(s)")

            # Display description with proper wrapping
            console.print("[bold]Description:[/bold]")
            for line in app.description.strip().split("\n"):
                console.print(f"  {line}")

            console.print("-" * 80)
    else:
        console.print("[bold]Available Aignostics Applications:[/bold]")
        for app in applications:
            app_count += 1
            # Get latest version info for this application
            latest_version = Service().application_version_latest(app)
            console.print(
                f"- [bold]{app.application_id}[/bold] - latest application version id: "
                f"`{latest_version.application_version_id if latest_version else 'None'}`"
            )

    if app_count == 0:
        logger.warning("No applications available.")
        console.print("No applications available.")

    return True


@cli.command("describe")
def application_describe(
    application_id: Annotated[str, typer.Argument(help="Id of the application to describe")],
) -> bool:
    """Describe application.

    Args:
        application_id (str): The ID of the application to describe

    Returns:
        bool: Success status of the operation
    """
    try:
        application = Service().application(application_id)
    except NotFoundException:
        logger.warning("Application with ID '%s' not found.", application_id)
        console.print(f"[warning]Warning:[/warning] Application with ID '{application_id}' not found.")
        return False
    except Exception as e:
        logger.exception("Failed to describe application with ID '%s'", application_id)
        console.print(f"[error]Error:[/error] Failed to describe application: {e}")
        return False

    console.print(f"[bold]Application Details for {application.application_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]Name:[/bold] {application.name}")
    console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(application.regulatory_classes)}")

    # Display description with proper wrapping
    console.print("[bold]Description:[/bold]")
    for line in application.description.strip().split("\n"):
        console.print(f"  {line}")

    # Display available versions
    versions = Service().application_versions(application)
    if versions:
        console.print()
        console.print("[bold]Available Versions:[/bold]")
        for version in versions:
            console.print(f"  [bold]Version ID:[/bold] {version.application_version_id}")
            console.print(f"  [bold]Version:[/bold] {version.version}")
            console.print(f"  [bold]Changelog:[/bold] {version.changelog}")

            # Display input artifacts
            console.print("  [bold]Input Artifacts:[/bold]")
            for artifact in version.input_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {artifact.mime_type}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            # Display output artifacts
            console.print("  [bold]Output Artifacts:[/bold]")
            for artifact in version.output_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {artifact.mime_type}")
                console.print(f"      Scope: {artifact.scope}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            console.print()

    return True


@run_app.command(name="prepare")
def run_prepare(
    application_version_id: Annotated[str, typer.Argument(help="Id of the application to generate the metadata for")],
    metadata_csv: Annotated[
        Path,
        typer.Argument(
            help="Target filename for the generated metadata file. .csv will be appended automatically.",
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    source_directory: Annotated[
        Path,
        typer.Argument(
            help="Source directory to scan for whole slide images",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Prepare metadata CSV file required for submitting a run.

    1. Scans source_directory for whole slide images (.tif, .tiff and .dcm)
    2. Extracts metadata from whole slide images such as width, height, mpp
    3. Creates CSV file with metadata as required for the given application version

    Args:
        application_version_id (str): The ID of the application version to generate metadata for
        metadata_csv (str): The target filename for the generated metadata file.
        source_directory (str): The source directory to scan for whole slide images
    """
    write_metadata_dict_to_csv(
        metadata_csv=metadata_csv,
        metadata_dict=Service().generate_metadata_from_source_directory(
            application_version_id=application_version_id,
            source_directory=source_directory,
        ),
    )
    console.print(f"Generated metadata file [bold]{metadata_csv}[/bold]")
    logger.info("Generated metadata file: '%s'", metadata_csv)


@run_app.command(name="upload")
def run_upload(
    application_version_id: Annotated[str, typer.Argument(help="Id of the application to generate the metadata for")],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and references.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    upload_prefix: Annotated[
        str,
        typer.Option(
            help="Prefix for the upload destination. If not given will be set to current milliseconds.",
        ),
    ] = f"{time.time() * 1000}",
) -> bool:
    """Upload files referenced in the metadata CSV file to the Aignostics platform.

    1. Reads the metadata CSV file
    2. Uploads the files referenced in the CSV file to the Aignostics platform
    3. Incrementally updates the CSV file with upload progress and the signed URLs for the uploaded files

    Args:
        application_version_id (str): The ID of the application version to generate the metadata for
        metadata_csv_file (str): The metadata file containing the references to whole slide images.
        upload_prefix (str): The prefix for the upload destination. If not given, will be set to current milliseconds.

    Returns:
        bool: Success status of the operation
    """
    metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
    if not metadata_dict:
        return False

    total_bytes = 0
    for i, entry in enumerate(metadata_dict):
        source = entry["source"]
        source_file_path = Path(source)
        if not source_file_path.is_file():
            logger.warning("Source file '%s' (row %d) does not exist", source_file_path, i)
            console.print(f"[warning]Warning:[/warning] Source file '{source_file_path}' (row {i}) does not exist")
            return False
        total_bytes += source_file_path.stat().st_size

    with Progress(
        TextColumn(
            f"[progress.description]Uploading from {metadata_csv_file} to "
            f"{BucketService().get_bucket_protocol()}:/{BucketService().get_bucket_name()}/{upload_prefix}"
        ),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task(f"Uploading to {upload_prefix}/...", total=total_bytes)

        def update_progress(bytes_uploaded: int, source: Path, platform_bucket_url: str) -> None:
            progress.update(task, advance=bytes_uploaded, description=f"{source.name}")
            for entry in metadata_dict:
                if entry["source"] == str(source):
                    entry["file_upload_progress"] = float(entry["file_upload_progress"]) + bytes_uploaded
                    entry["platform_bucket_url"] = platform_bucket_url
                    break
            write_metadata_dict_to_csv(
                metadata_csv=metadata_csv_file,
                metadata_dict=metadata_dict,
            )

        Service().application_run_upload(
            application_version_id=application_version_id,
            metadata=metadata_dict,
            upload_prefix=upload_prefix,
            upload_progress_callable=update_progress,
        )

    logger.info("Upload completed.")
    console.print("Upload completed.", style="info")
    return True


@run_app.command("submit")
def run_submit(
    application_version_id: Annotated[str, typer.Argument(help="Id of the application version to submit run for")],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and references.",
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> bool:
    """Submit run by referencing the metadata CSV file.

    1. Requires the metadata CSV file to be generated and referenced files uploaded first

    Args:
        application_version_id (str): The ID of the application version to submit a run for
        metadata_csv_file (str): The metadata file containing the references to whole slide images
            and their metadata to submit.

    Returns:
        bool: Success status of the operation
    """
    try:
        metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
        if not metadata_dict:
            return False
        logger.debug(
            "Submitting run for application version '%s' with metadata: %s", application_version_id, metadata_dict
        )
        application_run = Service().application_run_submit_from_metadata(
            application_version_id=application_version_id,
            metadata=metadata_dict,
        )
        console.print(f"submitted run with id '{application_run}'")
        return True
    except ValueError as e:
        logger.warning("Bad input to create run for application version '%s': %s", application_version_id, e)
        console.print(
            f"[warning]Warning:[/warning] Bad input to create run for application version "
            f"'{application_version_id}': {e}"
        )
        return False
    except Exception as e:
        logger.exception("Failed to create run for application version '%s'", application_version_id)
        console.print(
            f"[error]Error:[/error] Failed to create run for application version '{application_version_id}': {e}"
        )
        return False


@run_app.command("list")
def run_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    limit: Annotated[int | None, typer.Option(help="Maximum number of runs to display")] = None,
) -> int:
    """List application runs, sorted by triggered_at, descending.

    Args:
        verbose (bool): If True, show detailed information about each run.
        limit (int | None): Maximum number of runs to display. If None, display all runs.

    Returns:
        int: Number of runs found, or -1 if an error occurred
    """
    try:
        runs = Service().application_runs(limit=limit)
        if len(runs) == 0:
            message = "You did not yet create a run."
            logger.warning(message)
            console.print(message, style="warning")
            return 0

        limit = min(len(runs), limit) if limit is not None else len(runs)
        console.print(f"Found {len(runs)} application runs, displaying {limit} ...", style="debug")
        print_runs_verbose(runs) if verbose else print_runs_non_verbose(runs)
        message = f"Found {len(runs)} application runs, displayed {limit}."
        logger.info(message)
        console.print(message, style="info")
        return len(runs)
    except Exception as e:
        logger.exception("Failed to list runs")
        console.print(f"[error]Error:[/error] Failed to list runs: {e}")
        return -1


@run_app.command("describe")
def run_describe(run_id: Annotated[str, typer.Argument(help="Id of the run to describe")]) -> bool:
    """Describe application run.

    Args:
        run_id (str): The ID of the run to describe

    Returns:
        bool: Success status of the operation
    """
    logger.debug("Describing run with ID '%s'", run_id)

    try:
        retrieve_and_print_run_details(Service().application_run(run_id))
        logger.info("Described run with ID '%s'", run_id)
        return True
    except NotFoundException:
        logger.warning("Run with ID '%s' not found.", run_id)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        return False
    except Exception as e:
        logger.exception("Failed to retrieve and print run details for ID '%s'", run_id)
        console.print(f"[error]Error:[/error] Failed to retrieve run details for ID '{run_id}': {e}")
        return False


@run_app.command("cancel")
def run_cancel(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to cancel")],
) -> bool:
    """Cancel application run.

    Args:
        run_id(str): The ID of the run to cancel

    Returns:
        bool: True if the run was canceled successfully, False otherwise
    """
    logger.debug("Canceling run with ID '%s'", run_id)

    try:
        Service().application_run_cancel(run_id)
        logger.info("Canceled run with ID '%s'.", run_id)
        console.print(f"Run with ID '{run_id}' has been canceled.")
        return True
    except NotFoundException:
        logger.warning("Run with ID '%s' not found.", run_id)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        return False
    except Exception as e:
        logger.exception("Failed to cancel run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to cancel run with ID '{run_id}': {e}")
        return False


@result_app.command("describe")
def result_describe() -> None:
    """Describe the result of an application run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)


@result_app.command("download")
def download(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to download results for")],
    destination_directory: Annotated[
        Path,
        typer.Argument(
            help="Destination directory to download results to",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> bool:
    """Download the results of an application run.

    Args:
        run_id (str): The ID of the run to download results for
        destination_directory (str): The destination directory to download results to

    Returns:
        bool: True if the download was successful, False otherwise
    """
    logger.debug("Downloading results for run with ID '%s' to '%s'", run_id, destination_directory)

    try:
        destination_directory.mkdir(parents=True, exist_ok=True)
        logger.debug("Created destination directory '%s'", destination_directory)
    except OSError as e:
        logger.exception("Failed to create destination directory '%s'", destination_directory)
        console.log(
            f"[bold red]Error:[/bold red] Failed to create destination directory '{destination_directory}': {e}"
        )
        return False

    try:
        run = Service().application_run(run_id)
        run.download_to_folder(destination_directory)
        message = f"Downloaded results for run with ID '{run_id}' to '{destination_directory}'"
        logger.info(message)
        console.print(message, style="info")
        return True
    except NotFoundException as e:
        logger.warning("Run with ID '%s' not found: %s", run_id, e)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        return False
    except Exception as e:
        logger.exception("Failed to download results for run with ID '%s'", run_id)
        console.print(
            f"[error]Error:[/error] Failed to download results for run with ID '{run_id}': {type(e).__name__}: {e}"
        )
        return False


# TODO(Helmut): Implement result delete when available in platform
@result_app.command("delete")
def result_delete() -> None:
    """Delete the results of an application run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)
