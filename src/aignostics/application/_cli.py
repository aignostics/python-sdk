"""CLI (Command Line Interface) of Aignostics Python SDK."""

from pathlib import Path
from typing import Annotated

import typer

from aignostics.platform import Client
from aignostics.utils import console, get_logger

from ._utils import (
    construct_input_items,
    find_latest_version,
    find_run_by_id,
    get_client,
    print_runs_non_verbose,
    print_runs_verbose,
    retrieve_and_print_run_details,
)

log = get_logger(__name__)

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


@cli.command("list")
def application_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
) -> None:
    """List available applications."""
    client = Client()
    applications = client.applications.list()

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
            versions = list(client.applications.versions.list(app))
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
            latest_version = find_latest_version(app, client)
            console.print(f"- [bold]{app.application_id}[/bold] - latest application version id: `{latest_version}`")

    if app_count == 0:
        console.print("No applications available.")


@cli.command("describe")
def application_describe(
    application_id: Annotated[str, typer.Option(help="Id of the application to describe")],
) -> None:
    """Describe application."""
    client = Client()
    found = False

    for app in client.applications.list():
        if app.application_id == application_id:
            found = True
            console.print(f"[bold]Application Details for {app.application_id}[/bold]")
            console.print("=" * 80)
            console.print(f"[bold]Name:[/bold] {app.name}")
            console.print(f"[bold]Regulatory Classes:[/bold] {', '.join(app.regulatory_classes)}")

            # Display description with proper wrapping
            console.print("[bold]Description:[/bold]")
            for line in app.description.strip().split("\n"):
                console.print(f"  {line}")

            # Display available versions
            versions = list(client.applications.versions.list(app))
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
            break

    if not found:
        console.print(f"[bold red]Error:[/bold red] Application with ID '{application_id}' not found.")


@bucket_app.command("ls")
def bucket_ls() -> None:
    """List contents of tranfer bucket."""
    console.print("bucket ls")


@bucket_app.command("purge")
def bucket_purge() -> None:
    """Purge content of transfer bucket."""
    console.print("bucket purged.")


@datasset_app.command("download")
def dataset_download() -> None:
    """Download dataset."""
    console.print("dataset download")


@metadata_app.command("generate")
def metadata_generate() -> None:
    """Generate metadata."""
    console.print("generate metadata")


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
    client = get_client()
    if not client:
        return False

    source_csv = Path(source)
    if not source_csv.is_file():
        log.warning("Source file '%s' does not exist.", source)
        console.print(f"[bold red]Error:[/bold red] Source file '{source}' does not exist.")
        return False
    payload = construct_input_items(source_csv)
    application_run = client.runs.create(application_version=application_version_id, items=payload)
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
    client = get_client()
    if not client:
        return False

    try:
        # List all runs and convert generator to list
        runs = list(client.runs.list())
    except Exception as e:
        log.exception("Failed to list runs")
        console.print(f"[bold red]Error:[/bold red] Failed to list runs: {e}")
        return False

    # Use different display functions based on verbose flag
    run_count = print_runs_verbose(runs) if verbose else print_runs_non_verbose(runs)

    if run_count == 0:
        console.print("No application runs found.")

    return True


@run_app.command("describe")
def run_describe(run_id: Annotated[str, typer.Option(help="Id of the run to desfribe")]) -> bool:
    """Describe run.

    Args:
        run_id (str): The ID of the run to describe

    Returns:
        bool: Success status of the operation
    """
    log.debug("Describing run with ID '%s'", run_id)

    client = get_client()
    if not client:
        return False

    try:
        run = find_run_by_id(run_id, client)
    except Exception as e:
        log.exception("Failed to find run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to find run with ID '{run_id}': {e}")
        return False

    if run:
        log.debug("Found run with ID '%s'", run_id)
        try:
            retrieve_and_print_run_details(run, run_id)
        except Exception as e:
            log.exception("Failed to retrieve and print run details for ID '%s'", run_id)
            console.print(f"[bold red]Error:[/bold red] Failed to retrieve run details for ID '{run_id}': {e}")
            return False
        log.info("Described run with ID '%s'", run_id)
        return True

    log.warning("Run with ID '%s' not found.", run_id)
    console.print(f"[bold yellow]Warning:[/bold yellow] Run with ID '{run_id}' not found.")
    return False


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
    log.debug("Canceling run with ID '%s'", run_id)

    client = get_client()
    if not client:
        return False

    try:
        run = find_run_by_id(run_id, client)
    except Exception as e:
        log.exception("Failed to find run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to find run with ID '{run_id}': {e}")
        return False

    if run:
        try:
            run.cancel()
        except Exception as e:
            log.exception("Failed to cancel run with ID '%s'", run_id)
            console.print(f"[bold red]Error:[/bold red] Failed to cancel run with ID '{run_id}': {e}")
            return False
        log.info("Canceled run with ID '%s'.", run)
        console.print(f"Run with ID '{run_id}' has been canceled.")
        return True

    log.warning("Run with ID '%s' not found.", run_id)
    console.print(f"[bold yellow]Warning:[/bold yellow] Run with ID '{run_id}' not found.")
    return False


@result_app.command("describe")
def result_describe() -> None:
    """Describe the result of an application run."""
    console.print("NOT YET IMPLEMENTED")


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
    log.debug("Downloading results for run with ID '%s' to '%s'", run_id, destination)

    destination_dir = Path(destination)
    try:
        destination_dir.mkdir(parents=True, exist_ok=True)
        log.debug("Created destination directory '%s'", destination_dir)
    except OSError as e:
        log.exception("Failed to create destination directory '%s'", destination)
        console.log(f"[bold red]Error:[/bold red] Failed to create destination directory '{destination}': {e}")
        return False

    client = get_client()
    if not client:
        return False

    try:
        run = find_run_by_id(run_id, client)
    except Exception as e:
        log.exception("Failed to find run with ID '%s'", run_id)
        console.print(f"[bold red]Error:[/bold red] Failed to find run with ID '{run_id}': {e}")
        return False

    if run:
        log.debug("Found run with ID '%s'", run_id)
        try:
            run.download_to_folder(destination_dir)
        except Exception as e:
            log.exception("Failed to download results for run with ID '%s'", run_id)
            console.print(f"[bold red]Error:[/bold red] Failed to download results for run with ID '{run_id}': {e}")
            return False
        log.info("Downloaded results for run with ID '%s' to '%s'", run_id, destination_dir)
        console.print("downloaded result")
        return True

    log.warning("Run with ID '%s' not found.", run_id)
    console.print(f"[bold yellow]Warning:[/bold yellow] Run with ID '{run_id}' not found.")
    return False


@result_app.command("delete")
def result_delete() -> None:
    """Delete the result of an application run."""
    console.print("NOT YET IMPLEMENTED")
