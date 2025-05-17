"""CLI (Command Line Interface) of Aignostics Python SDK."""

import os
import time
from collections.abc import Generator
from pathlib import Path
from typing import Annotated

import requests
import typer
from tqdm.rich import tqdm

from aignostics.platform import Client, generate_signed_url
from aignostics.utils import console, get_logger

from ._utils import (
    construct_input_items,
    create_signed_upload_url,
    print_runs_non_verbose,
    print_runs_verbose,
    retrieve_and_print_run_details,
)

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)

cli = typer.Typer(name="application", help="Run applications on Aignostics platform.")

bucket_app = typer.Typer()
cli.add_typer(bucket_app, name="bucket", help="Transfer bucket provide by platform")

datasset_app = typer.Typer()
cli.add_typer(datasset_app, name="dataset", help="Datasets for use as input for applications")

metadata_app = typer.Typer()
cli.add_typer(metadata_app, name="metadata", help="Metadata required as input for applications")

run_app = typer.Typer()
cli.add_typer(run_app, name="run", help="Runs of applications")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Results of applications runs")


@cli.command("download")
def download(
    source_url: Annotated[str, typer.Option(help="URL to download")],
    destination_directory: Annotated[str, typer.Option(help="Destination directory to download to")],
) -> None:
    """Download from bucket to folder via a signed URL."""
    source_url_signed = generate_signed_url(source_url)
    console.print("Generated signed URL:")
    console.print(source_url_signed)
    destination_directory_path = Path(destination_directory)
    if not destination_directory_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] Destination directory '{destination_directory}' does not exist.")
        return
    # Extract filename from the URL
    filename = source_url_signed.split("/")[-1].split("?")[0]

    output_path = Path(destination_directory) / filename

    # Download the file
    response = requests.get(source_url_signed, stream=True, timeout=60)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Get total file size for progress bar
    total_size = int(response.headers.get("content-length", 0))

    with (
        open(output_path, "wb") as f,
        tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024, desc=filename, miniters=1) as progress_bar,
    ):
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    print(f"File successfully downloaded to {output_path}")


@cli.command("upload")
def upload(
    source_file: Annotated[str, typer.Option(help="Source file to upload")],
) -> None:
    """Upload a filew to a transfer bucket via a signed URL, authenticating with hmac."""
    source_file_path = Path(source_file)
    if not source_file_path.is_file():
        logger.warning("Source file '%s' does not exist.", source_file)
        console.print(f"[bold red]Error:[/bold red] Source file '{source_file}' does not exist.")
        return

    # Generate signed URL
    bucket_name = str(os.environ.get("AIGNOSTICS_BUCKET_NAME"))
    timestamp_millis = int(time.time() * 1000)
    object_key = f"helmut/heta/{timestamp_millis}_{source_file_path.name}"
    url = create_signed_upload_url(bucket_name, object_key)

    logger.debug("Generated signed upload URL: %s", url)

    file_size = source_file_path.stat().st_size
    with (
        open(source_file_path, "rb") as f,
        tqdm(
            total=file_size, unit="B", unit_scale=True, unit_divisor=1024, desc=source_file_path.name, miniters=1
        ) as progress_bar,
    ):

        def read_in_chunks() -> Generator[bytes, None, None]:
            while True:
                chunk = f.read(8192)  # 8KB chunks
                if not chunk:
                    break
                progress_bar.update(len(chunk))
                yield chunk

        response = requests.put(
            url, data=read_in_chunks(), headers={"Content-Type": "application/octet-stream"}, timeout=60
        )

        response.raise_for_status()

    console.print(
        f"[bold green]Success:[/bold green] File '{source_file_path.name}' uploaded successfully to 'gs://{bucket_name}/{object_key}'."
    )


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
        applications = Client().applications.find()
    except Exception as e:
        logger.exception("Failed to list applications")
        console.print(f"[bold red]Error:[/bold red] Failed to list applications: {e}")
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
                versions = list(Client().applications.versions.find(app))
            except Exception as e:
                logger.exception("Failed to list versions for application '%s'", app.application_id)
                console.print(
                    f"[bold red]Error:[/bold red] Failed to list versions for application '{app.application_id}': {e}"
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
            latest_version = Client().versions.find_latest_version_id(app)
            console.print(f"- [bold]{app.application_id}[/bold] - latest application version id: `{latest_version}`")

    if app_count == 0:
        logger.warning("No applications available.")
        console.print("No applications available.")

    return True


@cli.command("describe")
def application_describe(
    application_id: Annotated[str, typer.Option(help="Id of the application to describe")],
) -> bool:
    """Describe application.

    Args:
        application_id (str): The ID of the application to describe

    Returns:
        bool: Success status of the operation
    """
    try:
        application = Client().application(application_id)
    except Exception as e:
        logger.exception("Failed to find application with ID '%s'", application_id)
        console.print(f"[bold red]Error:[/bold red] Failed to find application: {e}")
        return False

    if not application:
        logger.warning("Application with ID '%s' not found.", application_id)
        console.print(f"[bold red]Warning:[/bold red] Application with ID '{application_id}' not found.")
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
    versions = list(Client().applications.versions.find(application))
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


@metadata_app.command("generate")
def metadata_generate() -> None:
    """Generate metadata."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)


@run_app.command("submit")
def run_submit(
    application_version_id: Annotated[str, typer.Option(help="Id of the application version to submit run for")],
    source: Annotated[
        str,
        typer.Option(
            help="Source of the run. If not starting with 's3://' or 'gs://', "
            "it is assumed to be a local file path pointing to a .csv file"
        ),
    ],
) -> bool:
    """Create run.

    Args:
        application_version_id (str): The ID of the application version to submit a run for
        source (str): The source of the run. If not starting with 's3://' or 'gs://',
            it is assumed to be a local file path pointing to a .csv file

    Returns:
        bool: Success status of the operation
    """
    source_csv = Path(source)
    if not source_csv.is_file():
        logger.warning("Source file '%s' does not exist.", source)
        console.print(f"[bold red]Error:[/bold red] Source file '{source}' does not exist.")
        return False
    payload = construct_input_items(source_csv)

    try:
        application_run = Client().runs.create(application_version=application_version_id, items=payload)
    except Exception as e:
        logger.exception("Failed to create run for application version '%s'", application_version_id)
        console.print(
            f"[bold red]Error:[/bold red] Failed to create run for application version '{application_version_id}': {e}"
        )
        return False

    console.print(f"submitted run with id '{application_run}'")
    return True


@run_app.command("list")
def run_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
) -> bool:
    """List runs.

    Args:
        verbose (bool): If True, show detailed information about each run

    Returns:
        bool: Success status of the operation
    """
    try:
        runs_data = list(Client().runs.find_data())
    except Exception as e:
        logger.exception("Failed to list runs")
        console.print(f"[bold red]Error:[/bold red] Failed to list runs: {e}")
        return False

    run_count = print_runs_verbose(runs_data, Client()) if verbose else print_runs_non_verbose(runs_data)

    if run_count == 0:
        logger.warning("No application runs found.")
        console.print("No application runs found.")

    return True


@run_app.command("describe")
def run_describe(run_id: Annotated[str, typer.Option(help="Id of the run to describe")]) -> bool:
    """Describe run.

    Args:
        run_id (str): The ID of the run to describe

    Returns:
        bool: Success status of the operation
    """
    logger.debug("Describing run with ID '%s'", run_id)

    try:
        retrieve_and_print_run_details(Client().run(run_id))
    except Exception as e:
        logger.exception("Failed to retrieve and print run details for ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to retrieve run details for ID '{run_id}': {e}")
        return False
    logger.info("Described run with ID '%s'", run_id)
    return True


@run_app.command("cancel")
def run_cancel(
    run_id: Annotated[str, typer.Option(..., help="Id of the run to cancel")],
) -> bool:
    """Cancel run.

    Args:
        run_id(str): The ID of the run to cancel

    Returns:
        bool: True if the run was canceled successfully, False otherwise
    """
    logger.debug("Canceling run with ID '%s'", run_id)

    try:
        Client().run(run_id).cancel()
    except Exception as e:
        logger.exception("Failed to cancel run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to cancel run with ID '{run_id}': {e}")
        return False
    logger.info("Canceled run with ID '%s'.", run_id)
    console.print(f"Run with ID '{run_id}' has been canceled.")
    return True


@result_app.command("describe")
def result_describe() -> None:
    """Describe the result of an application run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)


@result_app.command("download")
def result_download(
    run_id: Annotated[str, typer.Option(..., help="Id of the run to download results for")],
    destination: Annotated[str, typer.Option(help="Destination directory to download results to")],
) -> bool:
    """Download the result of an application run.

    Args:
        run_id (str): The ID of the run to download results for
        destination (str): The destination directory to download results to

    Returns:
        bool: True if the download was successful, False otherwise
    """
    logger.debug("Downloading results for run with ID '%s' to '%s'", run_id, destination)

    destination_dir = Path(destination)
    try:
        destination_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Created destination directory '%s'", destination_dir)
    except OSError as e:
        logger.exception("Failed to create destination directory '%s'", destination)
        console.log(f"[bold red]Error:[/bold red] Failed to create destination directory '{destination}': {e}")
        return False

    run = Client().run(run_id)

    if run:
        logger.debug("Found run with ID '%s'", run_id)
        try:
            run.download_to_folder(destination_dir)
        except Exception as e:
            logger.exception("Failed to download results for run with ID '%s'", run_id)
            console.print(f"[bold red]Error:[/bold red] Failed to download results for run with ID '{run_id}': {e}")
            return False
        logger.info("Downloaded results for run with ID '%s' to '%s'", run_id, destination_dir)
        console.print("downloaded result")
        return True

    logger.warning("Run with ID '%s' not found.", run_id)
    console.print(f"[bold yellow]Warning:[/bold yellow] Run with ID '{run_id}' not found.")
    return False


@result_app.command("delete")
def result_delete() -> None:
    """Delete the result of an application run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)
