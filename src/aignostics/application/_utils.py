"""Utility functions to ease using the platform client."""

import csv
from enum import StrEnum
from operator import itemgetter
from pathlib import Path
from typing import Literal

from aignostics.platform import (
    Application,
    ApplicationRun,
    ApplicationRunStatus,
    Client,
    InputArtifact,
    InputItem,
    generate_signed_url,
)
from aignostics.utils import console, get_logger

log = get_logger(__name__)


class OutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - TEXT: Output data as formatted text
    - JSON: Output data in JSON format

    Usage:
        format = OutputFormat.YAML
        print(f"Using {format} format")
    """

    TEXT = "text"
    JSON = "json"


def get_client() -> Client | None:
    """Get a client instance.

    Returns:
        Client | None: A Client instance if successful, None otherwise.
    """
    try:
        log.debug("Creating authenticated client.")
        client = Client()
        log.debug("Authenticated client created.")
        return client
    except Exception as e:
        log.exception("Failed to create authenticated client.")
        console.print(f"[bold red]Error:[/bold red] Failed to connect to Aignostics Platform: {e}")
    return None


def construct_input_items(source_csv: Path) -> list[InputItem]:
    """Construct payload from CSV file.

    Args:
        source_csv (Path): Path to the CSV file

    Returns:
        list: List of payload items
    """
    payload = []
    log.debug("Constructing payload from CSV file: %s", source_csv)
    with open(str(source_csv), newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";", quotechar='"')
        pos = 0
        for row in reader:
            # TODO(Helmut): Introspect to generate the below
            if pos == 0:
                pos += 1
                continue
            payload.append(
                InputItem(
                    reference=str(pos),
                    input_artifacts=[
                        InputArtifact(
                            name="user_slide",
                            download_url=generate_signed_url(row[0]),
                            metadata={
                                "checksum_crc32c": row[1],
                                "base_mpp": float(row[2]),
                                "width": int(row[3]),
                                "height": int(row[4]),
                                "cancer": {
                                    "type": row[5],
                                    "tissue": row[6],
                                },
                            },
                        )
                    ],
                )
            )
    return payload


def find_latest_version(app: Application, client: Client) -> str:
    """Find the latest version of an application.

    Args:
        app(Application): The application to find the latest version for
        client(Client): The Client instance to use

    Returns:
        str: The application_version_id of the latest version, or "No versions" if no versions are found
    """
    # Get versions for this application
    versions = list(client.applications.versions.list(app))

    # If no versions available
    if not versions:
        return "No versions"

    # Extract semantic versions from application_version_id (format: name:vX.Y.Z)
    versions_with_semver = []
    for v in versions:
        parts = v.application_version_id.split(":")
        if len(parts) > 1 and parts[1].startswith("v"):
            semver = parts[1][1:]  # Remove 'v' prefix
            try:
                # Split into major, minor, patch components for proper comparison
                version_parts = [int(x) for x in semver.split(".")]
                versions_with_semver.append((v, version_parts))
            except ValueError:
                # If we can't parse the version, skip it
                continue

    # Sort by semantic version (major, minor, patch)
    if versions_with_semver:
        versions_with_semver.sort(key=itemgetter(1), reverse=True)
        return str(versions_with_semver[0][0].application_version_id)

    # If we couldn't parse any versions, return the first one
    return str(versions[0].application_version_id)


def find_run_by_id(run_id: str, client: Client) -> ApplicationRun | None:
    """Find a run by its ID.

    Args:
        run_id: The ID of the run to find
        client: The Client instance to use

    Returns:
        The ApplicationRun object if found, None otherwise
    """
    runs = client.runs.list()

    for run in runs:
        run_status = run.status()
        if run_status.application_run_id == run_id:
            return run

    return None


def retrieve_and_print_run_details(run: ApplicationRun, run_id: str) -> None:
    """Retrieve and print detailed information about a run.

    Args:
        run(ApplicationRun): The ApplicationRun object
        run_id(str): The ID of the run

    """
    run_status = run.status()
    console.print(f"[bold]Run Details for {run_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]App Version:[/bold] {run_status.application_version_id}")
    console.print(f"[bold]Status:[/bold] {run_status.status.value}")
    console.print(f"[bold]Triggered at:[/bold] {run_status.triggered_at}")
    console.print(f"[bold]Organization:[/bold] {run_status.organization_id}")
    console.print(f"[bold]Triggered by:[/bold] {run_status.triggered_by}")

    # Get and display detailed item status
    console.print()
    console.print("[bold]Items:[/bold]")

    _retrieve_and_print_run_items(run)
    _print_run_status_summary(run)


def _retrieve_and_print_run_items(run: ApplicationRun) -> None:
    """Retrieve and print information about items in a run.

    Args:
        run(ApplicationRun): The ApplicationRun object
    """
    # Get results with detailed information
    results = run.results()
    if not results:
        console.print("  No item results available.")
        return

    for item in results:
        console.print(f"  [bold]Item Reference:[/bold] {item.reference}")
        console.print(f"  [bold]Item ID:[/bold] {item.item_id}")
        console.print(f"  [bold]Status:[/bold] {item.status.value}")

        if item.error:
            console.print(f"  [bold red]Error:[/bold red] {item.error}")

        if item.output_artifacts:
            console.print("  [bold]Output Artifacts:[/bold]")
            for artifact in item.output_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {artifact.mime_type}")
                console.print(f"      Artifact ID: {artifact.output_artifact_id}")

        console.print()


def _print_run_status_summary(run: ApplicationRun) -> None:
    """Print summary of item statuses in a run.

    Args:
        run(ApplicationRun): The ApplicationRun object
    """
    # Get and display item status counts
    item_statuses = run.item_status()
    if not item_statuses:
        return

    status_counts: dict[
        Literal["pending", "canceled_user", "canceled_system", "error_user", "error_system", "succeeded"], int
    ] = {}
    for status in item_statuses.values():
        status_counts[status.value] = status_counts.get(status.value, 0) + 1

    console.print("[bold]Item Status Summary:[/bold]")
    for status, count in status_counts.items():
        console.print(f"  {status}: {count}")


def _retrieve_and_print_run_status(run: ApplicationRun, run_count: int) -> tuple[int, ApplicationRunStatus | None]:
    """Retrieve and print basic run status information.

    Args:
        run: The run object
        run_count: Counter for runs

    Returns:
        tuple[int, ApplicationRunStatus | None]: A tuple containing the updated run count and the run status
    """
    try:
        run_status = run.status()
    except Exception as e:
        log.exception("Failed to get status for run with ID '%s'", run.application_run_id)
        console.print(
            f"[bold red]Error:[/bold red] Failed to get status for run with ID '{run.application_run_id}': {e}"
        )
        return run_count, None

    return run_count + 1, run_status


def _retrieve_and_print_item_status_counts(run: ApplicationRun) -> bool:
    """Retrieve and print item status counts for a run.

    Args:
        run(ApplicationRun): The run object

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        item_statuses = run.item_status()
    except Exception as e:
        log.exception("Failed to get item statuses for run with ID '%s'", run.application_run_id)
        console.print(
            f"[bold red]Error:[/bold red] Failed to get item statuses for run with ID '{run.application_run_id}': {e}"
        )
        return False

    status_counts: dict[
        Literal["pending", "canceled_user", "canceled_system", "error_user", "error_system", "succeeded"], int
    ] = {}
    for status in item_statuses.values():
        status_counts[status.value] = status_counts.get(status.value, 0) + 1

    if status_counts:
        console.print("[bold]Item Status Counts:[/bold]")
        for status, count in status_counts.items():
            console.print(f"  {status}: {count}")

    return True


def print_runs_verbose(runs: list[ApplicationRun]) -> int:
    """Print detailed information about runs.

    Args:
        runs: List of runs

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Runs:[/bold]")
    console.print("=" * 80)

    run_count = 0
    for run in runs:
        run_count, run_status = _retrieve_and_print_run_status(run, run_count)
        if not run_status:
            continue

        console.print(f"[bold]Run ID:[/bold] {run_status.application_run_id}")
        console.print(f"[bold]App Version:[/bold] {run_status.application_version_id}")
        console.print(f"[bold]Status:[/bold] {run_status.status.value}")
        console.print(
            f"[bold]Triggered at:[/bold] {run_status.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        console.print(f"[bold]Organization:[/bold] {run_status.organization_id}")

        try:
            _retrieve_and_print_item_status_counts(run)
        except Exception as e:
            log.exception("Failed to retrieve item status counts for run with ID '%s'", run.application_run_id)
            console.print(
                f"[bold red]Error:[/bold red] Failed to retrieve item status counts for run with ID "
                f"'{run.application_run_id}': {e}"
            )
            continue
        console.print("-" * 80)

    return run_count


def print_runs_non_verbose(runs: list[ApplicationRun]) -> int:
    """Print simplified information about runs.

    Args:
        runs: List of runs

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Run IDs:[/bold]")
    run_count = 0

    for run in runs:
        try:
            run_count, run_status = _retrieve_and_print_run_status(run, run_count)
        except Exception as e:
            log.exception("Failed to get status for run with ID '%s'", run.application_run_id)
            console.print(
                f"[bold red]Error:[/bold red] Failed to get status for run with ID '{run.application_run_id}': {e}"
            )
            continue

        if not run_status:
            continue

        console.print(
            f"- [bold]{run_status.application_run_id}[/bold] of "
            f"[bold]{run_status.application_version_id}[/bold] "
            f"(triggered: {run_status.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"status: {run_status.status.value})"
        )

    return run_count
