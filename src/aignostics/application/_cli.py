"""CLI of application module."""

from pathlib import Path
from typing import Annotated

import typer

from aignostics.platform import Client, NotFoundException
from aignostics.utils import console, get_logger

from ._utils import (
    construct_input_items,
    print_runs_non_verbose,
    print_runs_verbose,
    retrieve_and_print_run_details,
)

MESSAGE_NOT_YET_IMPLEMENTED = "NOT YET IMPLEMENTED"

logger = get_logger(__name__)

cli = typer.Typer(name="application", help="Run applications on Aignostics Platform.")

metadata_app = typer.Typer()
cli.add_typer(metadata_app, name="metadata", help="Metadata required as input for applications")

run_app = typer.Typer()
cli.add_typer(run_app, name="run", help="Runs of applications")

result_app = typer.Typer()
run_app.add_typer(result_app, name="result", help="Results of applications runs")


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
        applications = Client().applications.list()
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
                versions = list(Client().applications.versions.list(app))
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
            latest_version = Client().applications.versions.latest(app)
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
        application = Client().application(application_id)
    except Exception as e:
        logger.exception("Failed to find application with ID '%s'", application_id)
        console.print(f"[error]Error:[/error] Failed to find application: {e}")
        return False

    if not application:
        logger.warning("Application with ID '%s' not found.", application_id)
        console.print(f"[warning]Warning:[/warning] Application with ID '{application_id}' not found.")
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
    versions = list(Client().applications.versions.list(application))
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


# TODO(Helmut): Implement metadata generation as used in the GUI
@metadata_app.command("generate")
def metadata_generate() -> None:
    """Generate metadata."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)


@run_app.command("submit")
def run_submit(
    application_version_id: Annotated[str, typer.Argument(help="Id of the application version to submit run for")],
    source: Annotated[
        str,
        typer.Argument(
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
        console.print(f"[error]Error:[/error] Source file '{source}' does not exist.")
        return False
    payload = construct_input_items(source_csv)

    try:
        application_run = Client().runs.create(application_version=application_version_id, items=payload)
    except Exception as e:
        logger.exception("Failed to create run for application version '%s'", application_version_id)
        console.print(
            f"[error]Error:[/error] Failed to create run for application version '{application_version_id}': {e}"
        )
        return False

    console.print(f"submitted run with id '{application_run}'")
    return True


@run_app.command("list")
def run_list(
    verbose: Annotated[bool, typer.Option(help="Show application details")] = False,
    limit: Annotated[int | None, typer.Option(help="Maximum number of runs to display")] = None,
) -> int:
    """List runs, sorted by triggered_at, descending.

    Args:
        verbose (bool): If True, show detailed information about each run.
        limit (int | None): Maximum number of runs to display. If None, display all runs.

    Returns:
        int: Number of runs found, or -1 if an error occurred
    """
    try:
        runs = list(Client().runs.list_data(sort="triggered_at"))[::-1]
    except Exception as e:
        logger.exception("Failed to list runs")
        console.print(f"[error]Error:[/error] Failed to list runs: {e}")
        return -1

    if len(runs) == 0:
        message = "You did not yet create a run."
        logger.warning(message)
        console.print(message, style="warning")
        return 0

    limit = min(len(runs), limit) if limit is not None else len(runs)
    console.print(f"Found {len(runs)} application runs, displaying {limit} ...", style="debug")
    print_runs_verbose(runs[:limit], Client()) if verbose else print_runs_non_verbose(runs[:limit])
    message = f"Found {len(runs)} application runs, displayed {limit}."
    logger.info(message)
    console.print(message, style="info")
    return len(runs)


@run_app.command("describe")
def run_describe(run_id: Annotated[str, typer.Argument(help="Id of the run to describe")]) -> bool:
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
        console.print(f"[error]Error:[/error] Failed to retrieve run details for ID '{run_id}': {e}")
        return False
    logger.info("Described run with ID '%s'", run_id)
    return True


@run_app.command("cancel")
def run_cancel(
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to cancel")],
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
    run_id: Annotated[str, typer.Argument(..., help="Id of the run to download results for")],
    destination: Annotated[str, typer.Argument(help="Destination directory to download results to")],
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
    try:
        run.download_to_folder(destination_dir)
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
    message = f"Downloaded results for run with ID '{run_id}' to '{destination_dir}'"
    logger.info(message)
    console.print(message, style="info")
    return True


# TODO(Helmut): Implement result delete when available in client
@result_app.command("delete")
def result_delete() -> None:
    """Delete the result of an application run."""
    console.print(MESSAGE_NOT_YET_IMPLEMENTED)
