"""CLI of application module."""

import sys
import time
from pathlib import Path
from typing import Annotated

import typer

from aignostics.bucket import Service as BucketService
from aignostics.platform import NotFoundException
from aignostics.system import Service as SystemService
from aignostics.utils import console, get_logger

from ._service import DownloadProgress, DownloadProgressState, Service
from ._utils import (
    application_run_status_to_str,
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
run_app.add_typer(result_app, name="result", help="Download or delete run results.")


@cli.command("list")
def application_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
) -> None:
    """List available applications."""
    try:
        applications = Service().applications()
    except Exception as e:
        logger.exception("Failed to list applications")
        console.print(f"[error]Error:[/error] Failed to list applications: {e}")
        sys.exit(1)

    app_count = 0

    if verbose:
        console.print("[bold]Available Applications:[/bold]")
        console.print("=" * 80)

        for app in applications:
            app_count += 1
            console.print(f"[bold]Application ID:[/bold] {app.application_id}")
            console.print(f"[bold]Name:[/bold] {app.name}")
            console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(app.regulatory_classes)}")

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

                    num_inputs = len(version.input_artifacts)
                    num_outputs = len(version.output_artifacts)
                    console.print(f"    Artifacts: {num_inputs} input(s), {num_outputs} output(s)")

            console.print("[bold]Description:[/bold]")
            for line in app.description.strip().split("\n"):
                console.print(f"  {line}")

            console.print("-" * 80)
    else:
        console.print("[bold]Available Aignostics Applications:[/bold]")
        for app in applications:
            app_count += 1
            latest_version = Service().application_version_latest(app)
            console.print(
                f"- [bold]{app.application_id}[/bold] - latest application version id: "
                f"`{latest_version.application_version_id if latest_version else 'None'}`"
            )

    if app_count == 0:
        logger.info("No applications available.")
        console.print("No applications available.")


@cli.command("describe")
def application_describe(
    application_id: Annotated[str, typer.Argument(help="Id of the application to describe")],
) -> None:
    """Describe application."""
    try:
        application = Service().application(application_id)
    except NotFoundException:
        logger.warning("Application with ID '%s' not found.", application_id)
        console.print(f"[warning]Warning:[/warning] Application with ID '{application_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception("Failed to describe application with ID '%s'", application_id)
        console.print(f"[error]Error:[/error] Failed to describe application: {e}")
        sys.exit(1)

    console.print(f"[bold]Application Details for {application.application_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]Name:[/bold] {application.name}")
    console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(application.regulatory_classes)}")

    console.print("[bold]Description:[/bold]")
    for line in application.description.strip().split("\n"):
        console.print(f"  {line}")

    versions = Service().application_versions(application)
    if versions:
        console.print()
        console.print("[bold]Available Versions:[/bold]")
        for version in versions:
            console.print(f"  [bold]Version ID:[/bold] {version.application_version_id}")
            console.print(f"  [bold]Version:[/bold] {version.version}")
            console.print(f"  [bold]Changelog:[/bold] {version.changelog}")

            console.print("  [bold]Input Artifacts:[/bold]")
            for artifact in version.input_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {artifact.mime_type}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            console.print("  [bold]Output Artifacts:[/bold]")
            for artifact in version.output_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {artifact.mime_type}")
                console.print(f"      Scope: {artifact.scope}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            console.print()


@run_app.command(name="execute")
def run_execute(  # noqa: PLR0913, PLR0917
    application_version_id: Annotated[
        str,
        typer.Argument(
            help="Id of application version to execute. "
            "If application id is given, the latest version of that application is used."
        ),
    ],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and references.",
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
    mapping: Annotated[
        list[str],
        typer.Argument(
            help="Mapping to use for amending metadata CSV file. "
            "Each mapping is of the form '<regexp>:<key>:<value>,<key>:<value>,...'. "
            "The regular expression is matched against the reference attribute of the entry. "
            "The key/value pairs are applied to the entry if the pattern matches. "
            "You can use the mapping option multiple times to set values for multiple files. ",
        ),
    ],
    create_subdirectory_for_run: Annotated[
        bool,
        typer.Option(
            help="Create a subdirectory for the results of the run in the destination directory",
        ),
    ] = True,
    create_subdirectory_per_item: Annotated[
        bool,
        typer.Option(
            help="Create a subdirectory per item in the destination directory",
        ),
    ] = True,
    upload_prefix: Annotated[
        str,
        typer.Option(
            help="Prefix for the upload destination. If not given will be set to current milliseconds.",
        ),
    ] = f"{time.time() * 1000}",
    wait_for_completion: Annotated[
        bool,
        typer.Option(
            help="Wait for run completion and download results incrementally",
        ),
    ] = True,
) -> None:
    """Prepare metadata, upload data to platform, and submit an application run, then incrementally download results.

    (1) Prepares metadata CSV file for the given application version
        by scanning the source directory for whole slide images
        and extracting metadata such as width, height, and mpp.
    (2) Amends the metadata CSV file using the given mappings
        to set all required attributes.
    (3) Uploads the files referenced in the metadata CSV file
        to the cloud bucket provisioned in the Aignostics platform.
    (4) Submits the run for the given application version
        with the metadata from the CSV file.
    (5) Downloads the results of the run to the destination directory,
        by default waiting for the run to complete
        and downloading results incrementally.
    """
    run_prepare(
        application_version_id=application_version_id,
        metadata_csv=metadata_csv_file,
        source_directory=source_directory,
        mapping=mapping,
    )
    run_upload(
        application_version_id=application_version_id,
        metadata_csv_file=metadata_csv_file,
        upload_prefix=upload_prefix,
    )
    application_run_id = run_submit(
        application_version_id=application_version_id,
        metadata_csv_file=metadata_csv_file,
    )
    result_download(
        run_id=application_run_id,
        destination_directory=metadata_csv_file.parent,
        create_subdirectory_for_run=create_subdirectory_for_run,
        create_subdirectory_per_item=create_subdirectory_per_item,
        wait_for_completion=wait_for_completion,
    )


@run_app.command(name="prepare")
def run_prepare(
    application_version_id: Annotated[
        str,
        typer.Argument(
            help="Id of the application version to generate the metadata for. "
            "If application id is given, the latest version of that application is used."
        ),
    ],
    metadata_csv: Annotated[
        Path,
        typer.Argument(
            help="Target filename for the generated metadata CSV file.",
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
    mapping: Annotated[
        list[str] | None,
        typer.Option(
            help="Mapping to use for amending metadata CSV file. "
            "Each mapping is of the form '<regexp>:<key>:<value>,<key>:<value>,...'. "
            "The regular expression is matched against the reference attribute of the entry. "
            "The key/value pairs are applied to the entry if the pattern matches. "
            "You can use the mapping option multiple times to set values for multiple files. "
        ),
    ] = None,
) -> None:
    """Prepare metadata CSV file required for submitting a run.

    (1) Scans source_directory for whole slide images (.tif, .tiff and .dcm.
    (2) Extracts metadata from whole slide images such as width, height, mpp.
    (3) Creates CSV file with columns as required by the given application version.
    (4) Optionally applies mappings to amend the metadata CSV file for columns
        that are not automatically filled by the metadata extraction process.

    Example:
        aignostics application run prepare "he-tme:v0.51.0" metadata.csv /path/to/source_directory
        --mapping "*.tiff:staining_method:H&E,tissue:LUNG,disease:LUNG_CANCER"
    """
    write_metadata_dict_to_csv(
        metadata_csv=metadata_csv,
        metadata_dict=Service().generate_metadata_from_source_directory(
            application_version_id=application_version_id,
            source_directory=source_directory,
            mappings=mapping or [],
        ),
    )
    console.print(f"Generated metadata file [bold]{metadata_csv}[/bold]")
    logger.info("Generated metadata file: '%s'", metadata_csv)


@run_app.command(name="upload")
def run_upload(
    application_version_id: Annotated[
        str,
        typer.Argument(
            help="Id of the application version to upload data for. "
            "If application id is given, the latest version of that application is used."
        ),
    ],
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
) -> None:
    """Upload files referenced in the metadata CSV file to the Aignostics platform.

    1. Reads the metadata CSV file.
    2. Uploads the files referenced in the CSV file to the Aignostics platform.
    3. Incrementally updates the CSV file with upload progress and the signed URLs for the uploaded files.
    """
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

    metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
    if not metadata_dict:
        sys.exit(2)

    total_bytes = 0
    for i, entry in enumerate(metadata_dict):
        source = entry["reference"]
        source_file_path = Path(source)
        if not source_file_path.is_file():
            logger.warning("Source file '%s' (row %d) does not exist", source_file_path, i)
            console.print(f"[warning]Warning:[/warning] Source file '{source_file_path}' (row {i}) does not exist")
            sys.exit(2)

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
                if entry["reference"] == str(source):
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


@run_app.command("submit")
def run_submit(
    application_version_id: Annotated[
        str,
        typer.Argument(
            help="Id of the application version to submit run for. "
            "If application id is given, the latest version of that application is used."
        ),
    ],
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
) -> str:
    """Submit run by referencing the metadata CSV file.

    1. Requires the metadata CSV file to be generated and referenced files uploaded first

    Returns:
        The ID of the submitted application run.
    """
    try:
        metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
        if not metadata_dict:
            console.print("Could mot read metadata file '%s'", metadata_csv_file)
            sys.exit(2)
        logger.debug(
            "Submitting run for application version '%s' with metadata: %s", application_version_id, metadata_dict
        )
        application_run = Service().application_run_submit_from_metadata(
            application_version_id=application_version_id,
            metadata=metadata_dict,
        )
        console.print(f"Submitted run with id '{application_run.application_run_id}' for '{application_version_id}'.")
        return application_run.application_run_id
    except ValueError as e:
        logger.warning("Bad input to create run for application version '%s': %s", application_version_id, e)
        console.print(
            f"[warning]Warning:[/warning] Bad input to create run for application version "
            f"'{application_version_id}': {e}"
        )
        sys.exit(2)
    except Exception as e:
        logger.exception("Failed to create run for application version '%s'", application_version_id)
        console.print(
            f"[error]Error:[/error] Failed to create run for application version '{application_version_id}': {e}"
        )
        sys.exit(1)


@run_app.command("list")
def run_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    limit: Annotated[int | None, typer.Option(help="Maximum number of runs to display")] = None,
) -> None:
    """List runs."""
    try:
        runs = Service().application_runs(limit=limit)
        if len(runs) == 0:
            message = "You did not yet create a run."
            logger.warning(message)
            console.print(message, style="warning")
        else:
            print_runs_verbose(runs) if verbose else print_runs_non_verbose(runs)
            message = f"Listed '{len(runs)}' run(s)."
            console.print(message, style="info")
            logger.info(message, len(runs))
    except Exception as e:
        logger.exception("Failed to list runs")
        console.print(f"[error]Error:[/error] Failed to list runs: {e}")


@run_app.command("describe")
def run_describe(run_id: Annotated[str, typer.Argument(help="Id of the run to describe")]) -> None:
    """Describe run."""
    logger.debug("Describing run with ID '%s'", run_id)

    try:
        retrieve_and_print_run_details(Service().application_run(run_id))
        logger.info("Described run with ID '%s'", run_id)
    except NotFoundException:
        logger.warning("Run with ID '%s' not found.", run_id)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception("Failed to retrieve and print run details for ID '%s'", run_id)
        console.print(f"[error]Error:[/error] Failed to retrieve run details for ID '{run_id}': {e}")
        sys.exit(1)


@run_app.command("cancel")
def run_cancel(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to cancel")],
) -> None:
    """Cancel run."""
    logger.debug("Canceling run with ID '%s'", run_id)

    try:
        Service().application_run_cancel(run_id)
        logger.info("Canceled run with ID '%s'.", run_id)
        console.print(f"Run with ID '{run_id}' has been canceled.")
    except NotFoundException:
        logger.warning("Run with ID '%s' not found.", run_id)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception("Failed to cancel run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to cancel run with ID '{run_id}': {e}")
        sys.exit(1)


@result_app.command("download")
def result_download(  # noqa: PLR0913, PLR0917
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
    ] = SystemService.get_user_data_directory("results"),  # noqa: B008
    create_subdirectory_for_run: Annotated[
        bool,
        typer.Option(
            help="Create a subdirectory for the results of the run in the destination directory",
        ),
    ] = True,
    create_subdirectory_per_item: Annotated[
        bool,
        typer.Option(
            help="Create a subdirectory per item in the destination directory",
        ),
    ] = True,
    wait_for_completion: Annotated[
        bool,
        typer.Option(
            help="Wait for run completion and download results incrementally",
        ),
    ] = True,
    qupath_project: Annotated[
        bool,
        typer.Option(
            help="Create a QuPath project referencing input slides and results. \n"
            "The QuPath project will be created in a subfolder of the destination directory. \n"
            "This option requires the QuPath extension for Launchpad: "
            'start the Launchpad with `uvx --with "aignostics[qupath]" aignostics ...` \n'
            "This options requires installation of the QuPath application: "
            'Run uvx --with "aignostics[qupath]" aignostics qupath install'
        ),
    ] = False,
) -> None:
    """Download results of a run."""
    logger.debug(
        "Downloading results for run with ID '%s' to '%s' with options: "
        "create_subdirectory_for_run=%s, create_subdirectory_per_item=%s, wait_for_completion=%s, qupath_project=%r",
        run_id,
        destination_directory,
        create_subdirectory_for_run,
        create_subdirectory_per_item,
        wait_for_completion,
        qupath_project,
    )
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

    try:
        download_tasks: dict[str, TaskID] = {}

        main_download_progress_ui = Progress(
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("{task.fields[extra_description]}"),
        )
        artifact_download_progress_ui = Progress(
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
        panel = Panel(
            Group(main_download_progress_ui, artifact_download_progress_ui),
            title=f"Run {run_id}",
            subtitle="",
            highlight=True,
        )
        with Live(panel):
            main_task = main_download_progress_ui.add_task(description="", total=None, extra_description="")

            def update_progress(progress: DownloadProgress) -> None:
                """Update progress bar for file downloads."""
                if progress.run:
                    panel.title = f"Run {progress.run.application_run_id} of {progress.run.application_version_id}"
                    panel.subtitle = f"Triggered at {progress.run.triggered_at.strftime('%a, %x %X')}"
                    if progress.item_count:
                        panel.subtitle += f" with {progress.item_count} " + (
                            "item" if progress.item_count == 1 else "items"
                        )
                    panel.subtitle += f", status: {application_run_status_to_str(progress.run.status)}."
                main_download_progress_ui.update(
                    main_task,
                    description=(
                        progress.status
                        if progress.status is not DownloadProgressState.DOWNLOADING or not progress.total_artifact_index
                        else (
                            f"Downloading artifact {progress.total_artifact_index + 1} "
                            f"of {progress.total_artifact_count}"
                        )
                    ).ljust(50),
                )
                if progress.artifact_path:
                    task_key = str(progress.artifact_path.absolute())
                    if task_key not in download_tasks:
                        download_tasks[task_key] = artifact_download_progress_ui.add_task(
                            f"{progress.artifact_path.name}".ljust(50),
                            total=progress.artifact_size,
                            extra_description=f"Item {progress.item.reference if progress.item else 'unknown'}",
                        )

                    artifact_download_progress_ui.update(
                        download_tasks[task_key],
                        total=progress.artifact_size,
                        advance=progress.artifact_downloaded_chunk_size,
                    )

                if (
                    progress.item_count
                    and progress.item_index is not None
                    and progress.artifact_count
                    and progress.artifact_index is not None
                ):
                    main_download_progress_ui.update(
                        main_task,
                        completed=progress.item_index * progress.artifact_count + progress.artifact_index + 1,
                        total=float(progress.total_artifact_count) if progress.total_artifact_count else 0.0,
                    )

            destination_directory = Service().application_run_download(
                run_id=run_id,
                destination_directory=destination_directory,
                create_subdirectory_for_run=create_subdirectory_for_run,
                create_subdirectory_per_item=create_subdirectory_per_item,
                wait_for_completion=wait_for_completion,
                qupath_project=qupath_project,
                download_progress_callable=update_progress,
            )

            main_download_progress_ui.update(main_task, completed=100, total=100)

        message = f"Downloaded results of run '{run_id}' to '{destination_directory}'"
        logger.info(message)
        console.print(message, style="info")
    except NotFoundException as e:
        logger.warning("Run with ID '%s' not found: %s", run_id, e)
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except ValueError as e:
        logger.warning("Bad input to download results of run with ID '%s': %s", run_id, e)
        console.print(f"[warning]Warning:[/warning] Bad input to download results of run with ID '{run_id}': {e}")
        sys.exit(2)
    except Exception as e:
        logger.exception("Failed to download results of run with ID '%s'", run_id)
        console.print(
            f"[error]Error:[/error] Failed to download results of run with ID '{run_id}': {type(e).__name__}: {e}"
        )
        sys.exit(1)


# TODO(Helmut): Implement result delete when available in platform
@result_app.command("delete")
def result_delete() -> None:
    """Delete results of a run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)
    sys.exit(1)
