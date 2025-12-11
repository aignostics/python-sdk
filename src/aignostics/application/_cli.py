"""CLI of application module."""

import json
import sys
import time
import zipfile
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from aignostics.bucket import Service as BucketService
from aignostics.platform import (
    DEFAULT_CPU_PROVISIONING_MODE,
    DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES,
    DEFAULT_GPU_PROVISIONING_MODE,
    DEFAULT_GPU_TYPE,
    DEFAULT_MAX_GPUS_PER_SLIDE,
    DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES,
    NotFoundException,
    RunState,
)
from aignostics.platform import Service as PlatformService
from aignostics.system import Service as SystemService
from aignostics.utils import console, get_user_data_directory, sanitize_path

from ._models import DownloadProgress, DownloadProgressState
from ._service import Service
from ._utils import (
    application_run_status_to_str,
    get_mime_type_for_artifact,
    print_runs_non_verbose,
    print_runs_verbose,
    read_metadata_csv_to_dict,
    retrieve_and_print_run_details,
    validate_mappings,
    write_metadata_dict_to_csv,
)

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"
PROGRESS_TASK_DESCRIPTION = "[progress.description]{task.description}"


ApplicationVersionOption = Annotated[
    str | None,
    typer.Option(
        help="Version of the application. If not provided, the latest version will be used.",
    ),
]

NoteOption = Annotated[
    str | None,
    typer.Option(help="Optional note to include with the run submission via custom metadata."),
]

DueDateOption = Annotated[
    str | None,
    typer.Option(
        help="Optional soft due date to include with the run submission, ISO8601 format. "
        "The scheduler will try to complete the run by this date, taking the subscription tier"
        "and available GPU resources into account."
    ),
]

DeadlineOption = Annotated[
    str | None,
    typer.Option(
        help=(
            "Optional hard deadline to include with the run submission, ISO8601 format. "
            "If processing exceeds this deadline, the run can be aborted."
        ),
    ),
]

OnboardToPortalOption = Annotated[
    bool,
    typer.Option(help="If True, onboard the run to the Aignostics Portal."),
]

ForceOption = Annotated[
    bool,
    typer.Option(help="If True, skip the platform health check before proceeding."),
]

GpuTypeOption = Annotated[
    str,
    typer.Option(help="GPU type to use for processing (L4 or A100)."),
]

GpuProvisioningModeOption = Annotated[
    str,
    typer.Option(help="GPU provisioning mode (SPOT, ON_DEMAND, or FLEX_START)."),
]

FlexStartMaxRunDurationOption = Annotated[
    int,
    typer.Option(
        help="Maximum run duration in minutes when using FLEX_START provisioning mode (1-3600). "
        "Ignored when gpu_provisioning_mode is not FLEX_START.",
        min=1,
        max=3600,
    ),
]

MaxGpusPerSlideOption = Annotated[
    int,
    typer.Option(help="Maximum number of GPUs to allocate per slide (1-8).", min=1, max=8),
]

CpuProvisioningModeOption = Annotated[
    str,
    typer.Option(help="CPU provisioning mode (SPOT or ON_DEMAND)."),
]

NodeAcquisitionTimeoutOption = Annotated[
    int,
    typer.Option(help="Timeout for acquiring compute nodes in minutes (1-3600).", min=1, max=3600),
]


cli = typer.Typer(name="application", help="List and inspect applications on Aignostics Platform.")

run_app = typer.Typer()
cli.add_typer(run_app, name="run", help="List, submit and manage application runs")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Download or delete run results.")


def _abort_if_system_unhealthy() -> None:
    health = SystemService.health_static()
    if not health:
        logger.error(f"Platform is not healthy: {health.reason}. Aborting.")
        console.print(f"[error]Error:[/error] Platform is not healthy: {health.reason}. Aborting.")
        sys.exit(1)


@cli.command("list")
def application_list(  # noqa: C901
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    format: Annotated[  # noqa: A002
        str,
        typer.Option(help="Output format: 'text' (default) or 'json'"),
    ] = "text",
) -> None:
    """List available applications."""
    try:
        apps = Service().applications()
    except Exception as e:
        logger.exception("Could not load applications")
        if format == "json":
            print(json.dumps({"error": "failed", "message": str(e)}), file=sys.stderr)
        else:
            console.print(f"[error]Error:[/error] Could not load applications: {e}")
        sys.exit(1)

    if format == "json":
        # Convert apps to JSON-serializable format
        apps_data = [app.model_dump(mode="json") for app in apps]
        print(json.dumps(apps_data, indent=2, default=str))
        return

    app_count = 0

    if verbose:
        console.print("[bold]Available Applications:[/bold]")
        console.print("=" * 80)

        for app in apps:
            app_count += 1
            console.print(f"[bold]Application ID:[/bold] {app.application_id}")
            console.print(f"[bold]Name:[/bold] {app.name}")
            console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(app.regulatory_classes)}")

            try:
                details = Service().application(app.application_id)
            except Exception as e:
                logger.exception(f"Failed to get application details for application '{app.application_id}'")
                console.print(
                    f"[error]Error:[/error] Failed to get application details for application "
                    f"'{app.application_id}': {e}"
                )
                continue
            console.print("[bold]Available Versions:[/bold]")
            for version in details.versions:
                console.print(f"  - {version.number} ({version.released_at})")

                app_version = Service().application_version(app.application_id, version.number)
                console.print(f"    Changelog: {app_version.changelog}")

                num_inputs = len(app_version.input_artifacts)
                num_outputs = len(app_version.output_artifacts)
                console.print(f"    Artifacts: {num_inputs} input(s), {num_outputs} output(s)")

            console.print("[bold]Description:[/bold]")
            for line in app.description.strip().split("\n"):
                console.print(f"  {line}")

            console.print("-" * 80)
    else:
        console.print("[bold]Available Aignostics Applications:[/bold]")
        for app in apps:
            app_count += 1
            console.print(
                f"- [bold]{app.application_id}[/bold] - latest application version: `{app.latest_version or 'None'}`"
            )

    if app_count == 0:
        logger.debug("No applications available.")
        console.print("No applications available.")


@cli.command("dump-schemata")
def application_dump_schemata(  # noqa: C901
    application_id: Annotated[
        str,
        typer.Argument(help="Id of the application or application_version to dump the output schema for."),
    ],
    application_version: Annotated[
        str | None,
        typer.Option(
            help="Version of the application. If not provided, the latest version will be used.",
        ),
    ] = None,
    destination: Annotated[
        Path,
        typer.Option(
            help="Path pointing to directory where the input and output schemata will be dumped.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
            show_default="<current-working-directory>",
        ),
    ] = Path().cwd(),  # noqa: B008
    zip: Annotated[  # noqa: A002
        bool,
        typer.Option(
            help="If set, the schema files will be zipped into a single file, with the schema files deleted.",
        ),
    ] = False,
) -> None:
    """Output the input schema of the application in JSON format."""
    try:
        app = Service().application(application_id)
        app_version = Service().application_version(application_id, application_version)
    except (NotFoundException, ValueError) as e:
        message = f"Failed to load application version with ID '{id}', check your input: : {e!s}."
        logger.warning(message)
        console.print(f"[warning]Warning:[/warning] {message}")
        sys.exit(2)
    except Exception as e:
        message = f"Failed to load application version with ID '{id}': {e!s}."
        logger.exception(message)
        console.print(f"[warning]Error:[/warning] {message}")
        sys.exit(1)
    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[error]Error:[/error] Failed to create directory '{destination}': {e}")
        sys.exit(1)

    created_files: list[Path] = []

    for input_artifact in app_version.input_artifacts:
        if input_artifact.metadata_schema:
            file_path: Path = sanitize_path(
                Path(
                    destination / f"{app.application_id}_{app_version.version_number}_input_{input_artifact.name}.json"
                )
            )  # type: ignore
            file_path.write_text(data=json.dumps(input_artifact.metadata_schema, indent=2), encoding="utf-8")
            created_files.append(file_path)

    for output_artifact in app_version.output_artifacts:
        if output_artifact.metadata_schema:
            file_path = sanitize_path(
                Path(
                    destination
                    / f"{app.application_id}_{app_version.version_number}_output_{output_artifact.name}.json"
                )
            )  # type: ignore
            file_path.write_text(data=json.dumps(output_artifact.metadata_schema, indent=2), encoding="utf-8")
            created_files.append(file_path)

    md_file_path: Path = sanitize_path(
        Path(destination / f"{app.application_id}_{app_version.version_number}_schemata.md")
    )  # type: ignore
    with md_file_path.open("w", encoding="utf-8") as md_file:
        md_file.write(f"# Schemata for Aignostics Application {app.name}\n")
        md_file.write(f"* ID: {app.application_id}\n")
        md_file.write(f"\n## Description: \n{app.description}\n\n")
        md_file.write("\n## Input Artifacts\n")
        for input_artifact in app_version.input_artifacts:
            md_file.write(
                f"- {input_artifact.name}: "
                f"{app.application_id}_{app_version.version_number}_input_{input_artifact.name}.json\n"
            )
        md_file.write("\n## Output Artifacts\n")
        for output_artifact in app_version.output_artifacts:
            md_file.write(
                f"- {output_artifact.name}: "
                f"{app.application_id}_{app_version.version_number}_output_{output_artifact.name}.json\n"
            )
    created_files.append(md_file_path)

    if zip:
        zip_filename = sanitize_path(
            Path(destination / f"{app.application_id}_{app_version.version_number}_schemata.zip")
        )
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in created_files:
                zipf.write(file_path, arcname=file_path.name)
        console.print(f"Zipped {len(created_files)} files to [bold]{zip_filename}[/bold]")
        for file_path in created_files:
            file_path.unlink()


@cli.command("describe")
def application_describe(  # noqa: C901, PLR0912
    application_id: Annotated[str, typer.Argument(help="Id of the application to describe")],
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    format: Annotated[  # noqa: A002
        str,
        typer.Option(help="Output format: 'text' (default) or 'json'"),
    ] = "text",
) -> None:
    """Describe application."""
    try:
        app = Service().application(application_id)
    except NotFoundException:
        logger.warning(f"Application with ID '{application_id}' not found.")
        if format == "json":
            error_msg = {"error": "not_found", "message": f"Application with ID '{application_id}' not found."}
            print(json.dumps(error_msg), file=sys.stderr)
        else:
            console.print(f"[warning]Warning:[/warning] Application with ID '{application_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to describe application with ID '{application_id}'")
        if format == "json":
            print(json.dumps({"error": "failed", "message": str(e)}), file=sys.stderr)
        else:
            console.print(f"[error]Error:[/error] Failed to describe application: {e}")
        sys.exit(1)

    if format == "json":
        # Output application details as JSON
        print(json.dumps(app.model_dump(mode="json"), indent=2, default=str))
        return

    console.print(f"[bold]Application Details for {app.application_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]Name:[/bold] {app.name}")
    console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(app.regulatory_classes)}")

    console.print("[bold]Description:[/bold]")
    for line in app.description.strip().split("\n"):
        console.print(f"  {line}")

    if app.versions:
        console.print()
        console.print("[bold]Available Versions:[/bold]")
        for version in app.versions:
            console.print(f"  [bold]Version:[/bold] {version.number} ({version.released_at})")
            if not verbose:
                continue
            try:
                app_version = Service().application_version(app.application_id, version.number)
            except Exception as e:
                logger.exception(f"Failed to get application version for '{application_id}', '{version.number}'")
                console.print(
                    f"[error]Error:[/error] Failed to get application version for "
                    f"'{application_id}', '{version.number}': {e}"
                )
                sys.exit(1)

            console.print(f"  [bold]Changelog:[/bold] {app_version.changelog}")
            console.print("  [bold]Input Artifacts:[/bold]")
            for artifact in app_version.input_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {get_mime_type_for_artifact(artifact)}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            console.print("  [bold]Output Artifacts:[/bold]")
            for artifact in app_version.output_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {get_mime_type_for_artifact}")
                console.print(f"      Scope: {artifact.scope}")
                console.print(f"      Schema: {artifact.metadata_schema}")

            console.print()


@run_app.command(name="execute")
def run_execute(  # noqa: PLR0913, PLR0917
    application_id: Annotated[
        str,
        typer.Argument(help="Id of application version to execute."),
    ],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and external ids.",
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
    application_version: ApplicationVersionOption = None,
    mapping: Annotated[
        list[str] | None,
        typer.Option(
            help="Mapping to use for amending metadata CSV file. "
            "Each mapping is of the form '<regexp>:<key>=<value>,<key>=<value>,...'. "
            "The regular expression is matched against the external_id attribute of the entry. "
            "The key/value pairs are applied to the entry if the pattern matches. "
            "You can use the mapping option multiple times to set values for multiple files. "
            'Example: ".*:staining_method=H&E,tissue=LIVER,disease=LIVER_CANCER"',
        ),
    ] = None,
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
            show_default="<current-timestamp-ms>",
        ),
    ] = f"{time.time() * 1000}",
    wait_for_completion: Annotated[
        bool,
        typer.Option(
            help="Wait for run completion and download results incrementally",
        ),
    ] = True,
    note: NoteOption = None,
    due_date: DueDateOption = None,
    deadline: DeadlineOption = None,
    onboard_to_aignostics_portal: OnboardToPortalOption = False,
    gpu_type: GpuTypeOption = DEFAULT_GPU_TYPE,
    gpu_provisioning_mode: GpuProvisioningModeOption = DEFAULT_GPU_PROVISIONING_MODE,
    max_gpus_per_slide: MaxGpusPerSlideOption = DEFAULT_MAX_GPUS_PER_SLIDE,
    flex_start_max_run_duration_minutes: FlexStartMaxRunDurationOption = DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES,
    cpu_provisioning_mode: CpuProvisioningModeOption = DEFAULT_CPU_PROVISIONING_MODE,
    node_acquisition_timeout_minutes: NodeAcquisitionTimeoutOption = DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES,
    force: ForceOption = False,
) -> None:
    """Prepare metadata, upload data to platform, and submit an application run, then incrementally download results.

    (1) Prepares metadata CSV file for the given application version
        by scanning the source directory for whole slide images
        and extracting metadata such as width, height, and mpp.
    (2) Optionally amends the metadata CSV file using the given mappings
        to set additional required attributes.
    (3) Uploads the files referenced in the metadata CSV file
        to the cloud bucket provisioned in the Aignostics platform.
    (4) Submits the run for the given application version
        with the metadata from the CSV file.
    (5) Downloads the results of the run to the destination directory,
        by default waiting for the run to complete
        and downloading results incrementally.
    """
    if not force:
        _abort_if_system_unhealthy()
    run_prepare(
        application_id=application_id,
        metadata_csv=metadata_csv_file,
        source_directory=source_directory,
        application_version=application_version,
        mapping=mapping,
    )
    run_upload(
        application_id=application_id,
        metadata_csv_file=metadata_csv_file,
        application_version=application_version,
        upload_prefix=upload_prefix,
        onboard_to_aignostics_portal=onboard_to_aignostics_portal,
        force=force,
    )
    run_id = run_submit(
        application_id=application_id,
        metadata_csv_file=metadata_csv_file,
        application_version=application_version,
        note=note,
        tags=None,
        due_date=due_date,
        deadline=deadline,
        onboard_to_aignostics_portal=onboard_to_aignostics_portal,
        gpu_type=gpu_type,
        gpu_provisioning_mode=gpu_provisioning_mode,
        max_gpus_per_slide=max_gpus_per_slide,
        flex_start_max_run_duration_minutes=flex_start_max_run_duration_minutes,
        cpu_provisioning_mode=cpu_provisioning_mode,
        node_acquisition_timeout_minutes=node_acquisition_timeout_minutes,
    )
    result_download(
        run_id=run_id,
        destination_directory=metadata_csv_file.parent,
        create_subdirectory_for_run=create_subdirectory_for_run,
        create_subdirectory_per_item=create_subdirectory_per_item,
        wait_for_completion=wait_for_completion,
    )


@run_app.command(name="prepare")
def run_prepare(
    application_id: Annotated[
        str,
        typer.Argument(help="Id of the application to generate the metadata for. "),
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
    application_version: Annotated[
        str | None,
        typer.Option(
            help="Version of the application. If not provided, the latest version will be used.",
        ),
    ] = None,
    mapping: Annotated[
        list[str] | None,
        typer.Option(
            help="Mapping to use for amending metadata CSV file. "
            "Each mapping is of the form '<regexp>:<key>=<value>,<key>=<value>,...'. "
            "The regular expression is matched against the external_id attribute of the entry. "
            "The key/value pairs are applied to the entry if the pattern matches. "
            "You can use the mapping option multiple times to set values for multiple files. "
        ),
    ] = None,
) -> None:
    r"""Prepare metadata CSV file required for submitting a run.

    (1) Scans source_directory for whole slide images.
    (2) Extracts metadata from whole slide images such as width, height, mpp.
    (3) Creates CSV file with columns as required by the given application version.
    (4) Optionally applies mappings to amend the metadata CSV file for columns
        that are not automatically filled by the metadata extraction process.

    Example:
        aignostics application run prepare "he-tme:v0.51.0" metadata.csv /path/to/source_directory
        --mapping ".*\\.tiff:staining_method=H&E,tissue=LUNG,disease=LUNG_CANCER"
    """
    try:
        validate_mappings(mapping)
    except ValueError as e:
        console.print(f"[error]Error:[/error] {e}")
        sys.exit(1)

    write_metadata_dict_to_csv(
        metadata_csv=metadata_csv,
        metadata_dict=Service().generate_metadata_from_source_directory(
            source_directory=source_directory,
            application_id=application_id,
            application_version=application_version,
            mappings=mapping or [],
        ),
    )
    console.print(f"Generated metadata file [bold]{metadata_csv}[/bold]")
    logger.debug("Generated metadata file: '{}'", metadata_csv)


@run_app.command(name="upload")
def run_upload(  # noqa: PLR0913, PLR0917
    application_id: Annotated[
        str,
        typer.Argument(help="Id of the application to upload data for. "),
    ],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and external ids.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    application_version: Annotated[
        str | None,
        typer.Option(
            help="Version of the application. If not provided, the latest version will be used.",
        ),
    ] = None,
    upload_prefix: Annotated[
        str,
        typer.Option(
            help="Prefix for the upload destination. If not given will be set to current milliseconds.",
            show_default="<current-timestamp-ms>",
        ),
    ] = str(time.time() * 1000),
    onboard_to_aignostics_portal: Annotated[
        bool,
        typer.Option(
            help="If set, the run will be onboarded to the Aignostics Portal.",
        ),
    ] = False,
    force: ForceOption = False,
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

    if not force:
        _abort_if_system_unhealthy()

    metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
    if not metadata_dict:
        sys.exit(2)

    total_bytes = 0
    for i, entry in enumerate(metadata_dict):
        source = entry["external_id"]
        source_file_path = Path(source)
        if not source_file_path.is_file():
            logger.warning(f"Source file '{source_file_path}' (row {i}) does not exist")
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
        TextColumn(PROGRESS_TASK_DESCRIPTION),
    ) as progress:
        task = progress.add_task(f"Uploading to {upload_prefix}/...", total=total_bytes)

        def update_progress(bytes_uploaded: int, source: Path, platform_bucket_url: str) -> None:
            progress.update(task, advance=bytes_uploaded, description=f"{source.name}")
            for entry in metadata_dict:
                if entry["external_id"] == str(source):
                    entry["platform_bucket_url"] = platform_bucket_url
                    break
            write_metadata_dict_to_csv(
                metadata_csv=metadata_csv_file,
                metadata_dict=metadata_dict,
            )

        Service().application_run_upload(
            application_id=application_id,
            application_version=application_version,
            metadata=metadata_dict,
            onboard_to_aignostics_portal=onboard_to_aignostics_portal,
            upload_prefix=upload_prefix,
            upload_progress_callable=update_progress,
        )

    logger.debug("Upload completed.")
    console.print("Upload completed.", style="info")


@run_app.command("submit")
def run_submit(  # noqa: PLR0913, PLR0917
    application_id: Annotated[
        str,
        typer.Argument(help="Id of the application to submit run for."),
    ],
    metadata_csv_file: Annotated[
        Path,
        typer.Argument(
            help="Filename of the .csv file containing the metadata and external ids.",
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    application_version: ApplicationVersionOption = None,
    note: NoteOption = None,
    tags: Annotated[
        str | None,
        typer.Option(help="Optional comma-separated list of tags to attach to the run for filtering."),
    ] = None,
    due_date: DueDateOption = None,
    deadline: DeadlineOption = None,
    onboard_to_aignostics_portal: OnboardToPortalOption = False,
    gpu_type: GpuTypeOption = DEFAULT_GPU_TYPE,
    gpu_provisioning_mode: GpuProvisioningModeOption = DEFAULT_GPU_PROVISIONING_MODE,
    max_gpus_per_slide: MaxGpusPerSlideOption = DEFAULT_MAX_GPUS_PER_SLIDE,
    flex_start_max_run_duration_minutes: FlexStartMaxRunDurationOption = DEFAULT_FLEX_START_MAX_RUN_DURATION_MINUTES,
    cpu_provisioning_mode: CpuProvisioningModeOption = DEFAULT_CPU_PROVISIONING_MODE,
    node_acquisition_timeout_minutes: NodeAcquisitionTimeoutOption = DEFAULT_NODE_ACQUISITION_TIMEOUT_MINUTES,
    force: ForceOption = False,
) -> str:
    """Submit run by referencing the metadata CSV file.

    1. Requires the metadata CSV file to be generated and referenced files uploaded first

    Returns:
        The ID of the submitted application run.
    """
    if not force:
        _abort_if_system_unhealthy()

    try:
        app_version = Service().application_version(
            application_id=application_id, application_version=application_version
        )
    except ValueError as e:
        logger.warning(
            "Bad input to create run for application '{}' (version: '{}'): {}", application_id, application_version, e
        )
        console.print(
            f"[warning]Warning:[/warning] Bad input to create run for application "
            f"'{application_id} (version: {application_version})': {e}"
        )
        sys.exit(2)
    except NotFoundException as e:
        logger.warning(
            "Could not find application version '{}' (version: '{}'): {}", application_id, application_version, e
        )
        console.print(
            f"[warning]Warning:[/warning] Could not find application '{application_id} "
            f"(version: {application_version})': {e}"
        )
        sys.exit(2)
    except Exception as e:
        message = (
            f"Failed to load application version '{application_version}' for application '{application_id}': {e!s}."
        )
        logger.exception(message)
        console.print(f"[error]Error:[/error] {message}")
        sys.exit(1)

    try:
        metadata_dict = read_metadata_csv_to_dict(metadata_csv_file=metadata_csv_file)
        if not metadata_dict:
            console.print(f"Could not read metadata file '{metadata_csv_file}'")
            sys.exit(2)
        logger.trace(
            "Submitting run for application '{}' (version: '{}') with metadata: {}",
            application_id,
            app_version.version_number,
            metadata_dict,
        )

        # Submit run with pipeline configuration
        application_run = Service().application_run_submit_from_metadata(
            application_id=application_id,
            metadata=metadata_dict,
            application_version=application_version,
            custom_metadata=None,
            note=note,
            tags={tag.strip() for tag in tags.split(",") if tag.strip()} if tags else None,
            due_date=due_date,
            deadline=deadline,
            onboard_to_aignostics_portal=onboard_to_aignostics_portal,
            gpu_type=gpu_type,
            gpu_provisioning_mode=gpu_provisioning_mode,
            max_gpus_per_slide=max_gpus_per_slide,
            flex_start_max_run_duration_minutes=(
                flex_start_max_run_duration_minutes if gpu_provisioning_mode == "FLEX_START" else None
            ),
            cpu_provisioning_mode=cpu_provisioning_mode,
            node_acquisition_timeout_minutes=node_acquisition_timeout_minutes,
        )
        console.print(
            f"Submitted run with id '{application_run.run_id}' for "
            f"'{application_id} (version: {app_version.version_number})'."
        )
        return application_run.run_id
    except ValueError as e:
        logger.warning(
            "Bad input to create run for application '{}' (version: {}): {}",
            application_id,
            app_version.version_number,
            e,
        )
        console.print(
            f"[warning]Warning:[/warning] Bad input to create run for application "
            f"'{application_id} (version: {app_version.version_number})': {e}"
        )
        sys.exit(2)
    except Exception as e:
        logger.exception(
            "Failed to create run for application '{}' (version: {})", application_id, app_version.version_number
        )
        console.print(
            f"[error]Error:[/error] Failed to create run for application "
            f"'{application_id} (version: {app_version.version_number})': {e}"
        )
        sys.exit(1)


@run_app.command("list")
def run_list(  # noqa: PLR0913, PLR0917
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    limit: Annotated[int | None, typer.Option(help="Maximum number of runs to display")] = None,
    tags: Annotated[
        str | None,
        typer.Option(help="Optional comma-separated list of tags to filter runs. All tags must match."),
    ] = None,
    note_regex: Annotated[
        str | None,
        typer.Option(help="Optional regex pattern to filter runs by note metadata."),
    ] = None,
    query: Annotated[str | None, typer.Option(help="Optional query string to filter runs by note OR tags.")] = None,
    note_case_insensitive: Annotated[bool, typer.Option(help="Make note regex search case-insensitive.")] = True,
    format: Annotated[  # noqa: A002
        str,
        typer.Option(help="Output format: 'text' (default) or 'json'"),
    ] = "text",
) -> None:
    """List runs."""
    try:
        runs = Service().application_runs(
            limit=limit,
            tags={tag.strip() for tag in tags.split(",") if tag.strip()} if tags else None,
            note_regex=note_regex,
            note_query_case_insensitive=note_case_insensitive,
            query=query,
        )
        if len(runs) == 0:
            if format == "json":
                print(json.dumps([]))
            else:
                if tags:
                    message = f"You did not yet create a run matching tags: {tags!r}."
                elif note_regex:
                    message = f"You did not yet create a run matching note pattern: {note_regex!r}."
                else:
                    message = "You did not yet create a run."
                logger.warning(message)
                console.print(message, style="warning")
        else:
            if format == "json":
                # Convert runs to JSON-serializable format
                runs_data = [run.model_dump(mode="json") for run in runs]
                print(json.dumps(runs_data, indent=2, default=str))
            else:
                print_runs_verbose(runs) if verbose else print_runs_non_verbose(runs)
                message = f"Listed '{len(runs)}' run(s)."
                console.print(message, style="info")
            logger.debug(f"Listed '{len(runs)}' run(s).")
    except Exception as e:
        logger.exception("Failed to list runs")
        console.print(f"[error]Error:[/error] Failed to list runs: {e}")


@run_app.command("describe")
def run_describe(
    run_id: Annotated[str, typer.Argument(help="Id of the run to describe")],
    format: Annotated[  # noqa: A002
        str,
        typer.Option(help="Output format: 'text' (default) or 'json'"),
    ] = "text",
) -> None:
    """Describe run."""
    logger.trace("Describing run with ID '{}'", run_id)

    try:
        user_info = PlatformService.get_user_info()
        run = Service().application_run(run_id)
        if format == "json":
            # Get run details and output as JSON
            run_details = run.details(hide_platform_queue_position=not user_info.is_internal_user)
            print(json.dumps(run_details.model_dump(mode="json"), indent=2, default=str))
        else:
            retrieve_and_print_run_details(run, hide_platform_queue_position=not user_info.is_internal_user)
        logger.debug("Described run with ID '{}'", run_id)
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' not found.")
        if format == "json":
            print(json.dumps({"error": "not_found", "message": f"Run with ID '{run_id}' not found."}), file=sys.stderr)
        else:
            console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to retrieve and print run details for ID '{run_id}'")
        if format == "json":
            print(json.dumps({"error": "failed", "message": str(e)}), file=sys.stderr)
        else:
            console.print(f"[error]Error:[/error] Failed to retrieve run details for ID '{run_id}': {e}")
        sys.exit(1)


@run_app.command("dump-metadata")
def run_dump_metadata(
    run_id: Annotated[str, typer.Argument(help="Id of the run to dump custom metadata for")],
    pretty: Annotated[bool, typer.Option(help="Pretty print JSON output with indentation")] = False,
) -> None:
    """Dump custom metadata of a run as JSON to stdout."""
    logger.trace("Dumping custom metadata for run with ID '{}'", run_id)

    try:
        run = Service().application_run(run_id).details()
        custom_metadata = run.custom_metadata if hasattr(run, "custom_metadata") else {}

        # Output JSON to stdout
        if pretty:
            print(json.dumps(custom_metadata, indent=2))
        else:
            print(json.dumps(custom_metadata))

        logger.debug("Dumped custom metadata for run with ID '{}'", run_id)
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' not found.")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to dump custom metadata for run with ID '{run_id}'")
        console.print(f"[error]Error:[/error] Failed to dump custom metadata for run with ID '{run_id}': {e}")
        sys.exit(1)


@run_app.command("dump-item-metadata")
def run_dump_item_metadata(
    run_id: Annotated[str, typer.Argument(help="Id of the run containing the item")],
    external_id: Annotated[str, typer.Argument(help="External ID of the item to dump custom metadata for")],
    pretty: Annotated[bool, typer.Option(help="Pretty print JSON output with indentation")] = False,
) -> None:
    """Dump custom metadata of an item as JSON to stdout."""
    logger.trace("Dumping custom metadata for item '{}' in run with ID '{}'", external_id, run_id)

    try:
        run = Service().application_run(run_id)

        # Find the item with the matching external_id in the results
        item = None
        for result_item in run.results():
            if result_item.external_id == external_id:
                item = result_item
                break

        if item is None:
            logger.warning(f"Item with external ID '{external_id}' not found in run '{run_id}'.")
            print(
                f"Warning: Item with external ID '{external_id}' not found in run '{run_id}'.",
                file=sys.stderr,
            )
            sys.exit(2)

        custom_metadata = item.custom_metadata if hasattr(item, "custom_metadata") else {}

        # Output JSON to stdout
        if pretty:
            print(json.dumps(custom_metadata, indent=2))
        else:
            print(json.dumps(custom_metadata))

        logger.debug("Dumped custom metadata for item '{}' in run with ID '{}'", external_id, run_id)
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' not found.")
        print(f"Warning: Run with ID '{run_id}' not found.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to dump custom metadata for item '{external_id}' in run with ID '{run_id}'")
        print(
            f"Error: Failed to dump custom metadata for item '{external_id}' in run with ID '{run_id}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)


@run_app.command("cancel")
def run_cancel(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to cancel")],
) -> None:
    """Cancel run."""
    logger.trace("Canceling run with ID '{}'", run_id)

    try:
        Service().application_run_cancel(run_id)
        logger.debug("Canceled run with ID '{}'.", run_id)
        console.print(f"Run with ID '{run_id}' has been canceled.")
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' not found.")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except ValueError:
        logger.warning(f"Run ID '{run_id}' invalid")
        console.print(f"[warning]Warning:[/warning] Run ID '{run_id}' invalid.")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to cancel run with ID '{run_id}'")
        console.print(f"[bold red]Error:[/bold red] Failed to cancel run with ID '{run_id}': {e}")
        sys.exit(1)


@run_app.command("cancel-by-filter")
def run_cancel_by_filter(  # noqa: C901, PLR0912, PLR0915
    tags: Annotated[
        str | None,
        typer.Option(help="Optional comma-separated list of tags to filter runs. All tags must match."),
    ] = None,
    application_id: Annotated[
        str | None,
        typer.Option(help="Optional application ID to filter runs."),
    ] = None,
    application_version: Annotated[
        str | None,
        typer.Option(help="Optional application version to filter runs."),
    ] = None,
    limit: Annotated[int | None, typer.Option(help="Maximum number of runs to cancel")] = None,
    dry_run: Annotated[
        bool,
        typer.Option(help="Show which runs would be canceled without actually canceling them."),
    ] = False,
) -> None:
    """Cancel runs matching filter criteria.

    All provided filters must match for a run to be canceled.
    At least one filter parameter (tags, application_id, or application_version) must be provided.
    """
    # Validate at least one filter is provided
    if not tags and not application_id and not application_version:
        error_msg = (
            "[error]Error:[/error] At least one filter parameter "
            "(--tags, --application-id, or --application-version) must be provided."
        )
        console.print(error_msg)
        sys.exit(1)

    logger.trace(
        "Canceling runs with filters: tags={}, application_id={}, application_version={}, limit={}, dry_run={}",
        tags,
        application_id,
        application_version,
        limit,
        dry_run,
    )

    try:
        # Get runs matching the tag filter first
        runs = Service().application_runs(
            limit=limit,
            tags={tag.strip() for tag in tags.split(",") if tag.strip()} if tags else None,
        )

        # Further filter by application_id and application_version if provided
        filtered_runs = []
        for run in runs:
            # Check application_id match
            if application_id and run.application_id != application_id:
                continue
            # Check application_version match
            if application_version and run.version_number != application_version:
                continue
            filtered_runs.append(run)

        if len(filtered_runs) == 0:
            filter_desc = []
            if tags:
                filter_desc.append(f"tags={tags}")
            if application_id:
                filter_desc.append(f"application_id={application_id}")
            if application_version:
                filter_desc.append(f"application_version={application_version}")
            message = f"No runs found matching filters: {', '.join(filter_desc)}"
            logger.warning(message)
            console.print(f"[warning]Warning:[/warning] {message}")
            return

        if dry_run:
            console.print(f"[bold]Would cancel {len(filtered_runs)} run(s):[/bold]")
            for run in filtered_runs:
                console.print(f"  - {run.run_id} ({run.application_id} v{run.version_number}, state: {run.state})")
            return

        # Cancel each matching run
        canceled_count = 0
        failed_count = 0
        for run in filtered_runs:
            try:
                Service().application_run_cancel(run.run_id)
                canceled_count += 1
                logger.debug(f"Canceled run with ID '{run.run_id}'.")
            except NotFoundException:
                logger.warning(f"Run with ID '{run.run_id}' not found (may have been deleted).")
                failed_count += 1
            except ValueError:
                logger.warning(f"Run ID '{run.run_id}' invalid")
                failed_count += 1
            except Exception as e:
                logger.exception(f"Failed to cancel run with ID '{run.run_id}'")
                console.print(f"[error]Error:[/error] Failed to cancel run with ID '{run.run_id}': {e}")
                failed_count += 1

        # Print summary
        console.print(f"Successfully canceled {canceled_count} run(s).")
        if failed_count > 0:
            console.print(f"[warning]Warning:[/warning] Failed to cancel {failed_count} run(s).")

    except Exception as e:
        logger.exception("Failed to cancel runs by filter")
        console.print(f"[error]Error:[/error] Failed to cancel runs by filter: {e}")
        sys.exit(1)


@run_app.command("update-metadata")
def run_update_metadata(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to update")],
    metadata_json: Annotated[
        str, typer.Argument(..., help='Custom metadata as JSON string (e.g., \'{"key": "value"}\')')
    ],
) -> None:
    """Update custom metadata for a run."""
    import json  # noqa: PLC0415

    logger.trace("Updating custom metadata for run with ID '{}'", run_id)

    try:
        # Parse JSON metadata
        try:
            custom_metadata = json.loads(metadata_json)
            if not isinstance(custom_metadata, dict):
                console.print("[error]Error:[/error] Metadata must be a JSON object (dictionary).")
                sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[error]Error:[/error] Invalid JSON: {e}")
            sys.exit(1)

        Service().application_run_update_custom_metadata(run_id, custom_metadata)
        logger.debug("Updated custom metadata for run with ID '{}'.", run_id)
        console.print(f"Successfully updated custom metadata for run with ID '{run_id}'.")
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' not found.")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except ValueError as e:
        logger.warning(f"Run ID '{run_id}' invalid or metadata invalid: {e}")
        console.print(f"[warning]Warning:[/warning] Run ID '{run_id}' invalid or metadata invalid: {e}")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to update custom metadata for run with ID '{run_id}'")
        console.print(f"[bold red]Error:[/bold red] Failed to update custom metadata for run with ID '{run_id}': {e}")
        sys.exit(1)


@run_app.command("update-item-metadata")
def run_update_item_metadata(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run containing the item")],
    external_id: Annotated[str, typer.Argument(..., help="External ID of the item to update")],
    metadata_json: Annotated[
        str, typer.Argument(..., help='Custom metadata as JSON string (e.g., \'{"key": "value"}\')')
    ],
) -> None:
    """Update custom metadata for an item in a run."""
    import json  # noqa: PLC0415

    logger.trace("Updating custom metadata for item '{}' in run with ID '{}'", external_id, run_id)

    try:
        # Parse JSON metadata
        try:
            custom_metadata = json.loads(metadata_json)
            if not isinstance(custom_metadata, dict):
                console.print("[error]Error:[/error] Metadata must be a JSON object (dictionary).")
                sys.exit(1)
        except json.JSONDecodeError as e:
            console.print(f"[error]Error:[/error] Invalid JSON: {e}")
            sys.exit(1)

        Service().application_run_update_item_custom_metadata(run_id, external_id, custom_metadata)
        logger.debug("Updated custom metadata for item '{}' in run with ID '{}'.", external_id, run_id)
        console.print(f"Successfully updated custom metadata for item '{external_id}' in run with ID '{run_id}'.")
    except NotFoundException:
        logger.warning(f"Run with ID '{run_id}' or item '{external_id}' not found.")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' or item '{external_id}' not found.")
        sys.exit(2)
    except ValueError as e:
        logger.warning(
            "Run ID '{}' or item external ID '{}' invalid or metadata invalid: {}",
            run_id,
            external_id,
            e,
        )
        console.print(
            f"[warning]Warning:[/warning] Run ID '{run_id}' or item external ID '{external_id}' "
            f"invalid or metadata invalid: {e}"
        )
        sys.exit(2)
    except Exception as e:
        logger.exception(
            "Failed to update custom metadata for item '{}' in run with ID '{}'",
            external_id,
            run_id,
        )
        console.print(
            f"[bold red]Error:[/bold red] Failed to update custom metadata for item '{external_id}' "
            f"in run with ID '{run_id}': {e}"
        )
        sys.exit(1)


@result_app.command("download")
def result_download(  # noqa: C901, PLR0913, PLR0915, PLR0917
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
            show_default="~/Library/Application Support/aignostics/results",
        ),
    ] = get_user_data_directory("results"),  # noqa: B008
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
    logger.trace(
        "Downloading results for run with ID '{}' to '{}' with options: "
        "create_subdirectory_for_run={}, create_subdirectory_per_item={}, wait_for_completion={}, qupath_project={}",
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
            TextColumn(PROGRESS_TASK_DESCRIPTION),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("{task.fields[extra_description]}"),
        )
        artifact_download_progress_ui = Progress(
            BarColumn(),
            TaskProgressColumn(),
            TextColumn(PROGRESS_TASK_DESCRIPTION),
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

            def update_progress(progress: DownloadProgress) -> None:  # noqa: C901
                """Update progress bar for file downloads."""
                if progress.run:
                    panel.title = (
                        f"Run {progress.run.run_id} of {progress.run.application_id} "
                        f"(version: {progress.run.version_number})"
                    )
                    panel.subtitle = f"Triggered at {progress.run.submitted_at.strftime('%a, %x %X')}"
                    if progress.item_count:
                        panel.subtitle += f" with {progress.item_count} " + (
                            "item" if progress.item_count == 1 else "items"
                        )
                    if progress.run.state is RunState.TERMINATED:
                        status_text = application_run_status_to_str(progress.run.state)
                        panel.subtitle += f", status: {status_text} ({progress.run.termination_reason})."
                    else:
                        panel.subtitle += f", status: {application_run_status_to_str(progress.run.state)}."
                # Determine the status message based on progress state
                if progress.status is DownloadProgressState.DOWNLOADING_INPUT:
                    status_message = (
                        f"Downloading input slide {progress.item_index + 1} of {progress.item_count}"
                        if progress.item_index is not None and progress.item_count
                        else "Downloading input slide ..."
                    )
                elif progress.status is DownloadProgressState.DOWNLOADING and progress.total_artifact_index is not None:
                    status_message = (
                        f"Downloading artifact {progress.total_artifact_index + 1} of {progress.total_artifact_count}"
                    )
                else:
                    status_message = progress.status

                main_download_progress_ui.update(
                    main_task,
                    description=status_message.ljust(50),
                )
                # Handle input slide download progress
                if progress.status is DownloadProgressState.DOWNLOADING_INPUT and progress.input_slide_path:
                    task_key = str(progress.input_slide_path.absolute())
                    if task_key not in download_tasks:
                        download_tasks[task_key] = artifact_download_progress_ui.add_task(
                            f"{progress.input_slide_path.name}".ljust(50),
                            total=progress.input_slide_size,
                            extra_description=f"Input from {progress.input_slide_url or 'gs://'}"
                            if progress.input_slide_url
                            else "Input slide",
                        )

                    artifact_download_progress_ui.update(
                        download_tasks[task_key],
                        total=progress.input_slide_size,
                        advance=progress.input_slide_downloaded_chunk_size,
                    )
                # Handle artifact download progress
                elif progress.artifact_path:
                    task_key = str(progress.artifact_path.absolute())
                    if task_key not in download_tasks:
                        download_tasks[task_key] = artifact_download_progress_ui.add_task(
                            f"{progress.artifact_path.name}".ljust(50),
                            total=progress.artifact_size,
                            extra_description=f"Item {progress.item.external_id if progress.item else 'unknown'}",
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
        logger.debug(message)
        console.print(message, style="info")
    except NotFoundException as e:
        logger.warning(f"Run with ID '{run_id}' not found: {e}")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except ValueError as e:
        logger.warning(f"Bad input to download results of run with ID '{run_id}': {e}")
        console.print(f"[warning]Warning:[/warning] Bad input to download results of run with ID '{run_id}': {e}")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to download results of run with ID '{run_id}'")
        console.print(
            f"[error]Error:[/error] Failed to download results of run with ID '{run_id}': {type(e).__name__}: {e}"
        )
        sys.exit(1)


@result_app.command("delete")
def result_delete(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to delete results for")],
) -> None:
    """Delete results of run."""
    logger.trace("Deleting results for run with ID '{}'", run_id)

    try:
        Service().application_run_delete(run_id)
        logger.debug("Deleted run with ID '{}'.", run_id)
        console.print(f"Results for run with ID '{run_id}' have been deleted.")
    except NotFoundException:
        logger.warning(f"Results for with ID '{run_id}' not found.")
        console.print(f"[warning]Warning:[/warning] Run with ID '{run_id}' not found.")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"Failed to delete run with ID '{run_id}'")
        console.print(f"[bold red]Error:[/bold red] Failed to delete results for with ID '{run_id}': {e}")
        sys.exit(1)
