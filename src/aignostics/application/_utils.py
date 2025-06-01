"""Utility functions for application module.

1. Printing of application resources
2. Reading/writing metadata CSV files
3. Mime type handling.
"""

import csv
import mimetypes
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from aignostics.platform import (
    ApplicationRun,
    ApplicationRunData,
    ApplicationRunStatus,
    InputArtifactData,
    OutputArtifactData,
    OutputArtifactElement,
)
from aignostics.utils import console, get_logger

logger = get_logger(__name__)

RUN_FAILED_MESSAGE = "Failed to get status for run with ID '%s'"


class OutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - TEXT: Output data as formatted text
    - JSON: Output data in JSON format
    """

    TEXT = "text"
    JSON = "json"


def retrieve_and_print_run_details(run: ApplicationRun) -> None:
    """Retrieve and print detailed information about a run.

    Args:
        run (ApplicationRun): The ApplicationRun object

    """
    run_data = run.details()
    console.print(f"[bold]Run Details for {run.application_run_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]App Version:[/bold] {run_data.application_version_id}")
    console.print(f"[bold]Status:[/bold] {run_data.status.value}")
    console.print(f"[bold]Triggered at:[/bold] {run_data.triggered_at}")
    console.print(f"[bold]Organization:[/bold] {run_data.organization_id}")
    console.print(f"[bold]Triggered by:[/bold] {run_data.triggered_by}")

    # Get and display detailed item status
    console.print()
    console.print("[bold]Items:[/bold]")

    _retrieve_and_print_run_items(run)
    _print_run_status_summary(run)


def _retrieve_and_print_run_items(run: ApplicationRun) -> None:
    """Retrieve and print information about items in a run.

    Args:
        run (ApplicationRun): The ApplicationRun object
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
            console.print(f"  [error]Error:[/error] {item.error}")

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
        run (ApplicationRun): The ApplicationRun object
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


def _retrieve_and_print_item_status_counts(run: ApplicationRun) -> bool:
    """Retrieve and print item status counts for a run.

    Args:
        run (ApplicationRun): The run object

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        item_statuses = run.item_status()
    except Exception as e:
        logger.exception("Failed to get item status for run with ID '%s'", run.application_run_id)
        console.print(
            f"[error]Error:[/error] Failed to get item statuses for run with ID '{run.application_run_id}': {e}"
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


def print_runs_verbose(runs: list[ApplicationRunData]) -> None:
    """Print detailed information about runs, sorted by triggered_at in descending order.

    Args:
        runs (list[ApplicationRunData]): List of run data
        service (Service): The Service instance to use

    """
    from ._service import Service  # noqa: PLC0415

    console.print("[bold]Application Runs:[/bold]")
    console.print("=" * 80)

    for run in runs:
        console.print(f"[bold]Run ID:[/bold] {run.application_run_id}")
        console.print(f"[bold]App Version:[/bold] {run.application_version_id}")
        console.print(f"[bold]Status:[/bold] {run.status.value}")
        console.print(f"[bold]Triggered at:[/bold] {run.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        console.print(f"[bold]Organization:[/bold] {run.organization_id}")

        try:
            _retrieve_and_print_item_status_counts(Service().application_run(run.application_run_id))
        except Exception as e:
            logger.exception("Failed to retrieve item status counts for run with ID '%s'", run.application_run_id)
            console.print(
                f"[error]Error:[/error] Failed to retrieve item status counts for run with ID "
                f"'{run.application_run_id}': {e}"
            )
            continue
        console.print("-" * 80)


def print_runs_non_verbose(runs: list[ApplicationRunData]) -> None:
    """Print simplified information about runs, sorted by triggered_at in descending order.

    Args:
        runs (list[ApplicationRunData]): List of runs

    """
    console.print("[bold]Application Run IDs:[/bold]")

    for run_status in runs:
        console.print(
            f"- [bold]{run_status.application_run_id}[/bold] of "
            f"[bold]{run_status.application_version_id}[/bold] "
            f"(triggered: {run_status.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"status: {run_status.status.value})"
        )


def write_metadata_dict_to_csv(
    metadata_csv: Path,
    metadata_dict: list[dict[str, Any]],
) -> Path:
    """Write metadata dict to a CSV file.

    Convert dict to CSV including header assuming all entries in dict have the same keys

    Args:
        metadata_csv (Path): Path to the CSV file
        metadata_dict (list[dict[str,Any]]): List of dictionaries containing metadata

    Returns:
        Path: Path to the CSV file
    """
    with metadata_csv.open("w", newline="", encoding="utf-8") as f:
        field_names = list(metadata_dict[0].keys())
        writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(field_names)
        for entry in metadata_dict:
            writer.writerow([entry.get(field, "") for field in field_names])
    return metadata_csv


def read_metadata_csv_to_dict(
    metadata_csv_file: Path,
) -> list[dict[str, Any]] | None:
    """Read metadata CSV file and convert it to a list of dictionaries.

    Args:
        metadata_csv_file (Path): Path to the CSV file

    Returns:
        list[dict[str, str]] | None: List of dictionaries containing metadata or None if an error occurs
    """
    try:
        with metadata_csv_file.open("r", encoding="utf-8") as f:
            return list(csv.DictReader(f, delimiter=";", quotechar='"'))
    except (csv.Error, UnicodeDecodeError, KeyError) as e:
        logger.warning("Failed to parse metadata CSV file '%s': %s", metadata_csv_file, e)
        console.print(f"[warning]Warning:[/warning] Failed to parse metadata CSV file '{metadata_csv_file}': {e}")
        return None


def application_run_status_to_str(
    status: ApplicationRunStatus,
) -> str:
    """Convert application status to a human-readable string.

    Args:
        status (ApplicationRunStatus): The application status

    Raises:
        RuntimeError: If the status is invalid or unknown

    Returns:
        str: Human-readable string representation of the status
    """
    status_mapping = {
        ApplicationRunStatus.CANCELED_SYSTEM: "canceled by platform",
        ApplicationRunStatus.CANCELED_USER: "canceled by user",
        ApplicationRunStatus.COMPLETED: "completed",
        ApplicationRunStatus.COMPLETED_WITH_ERROR: "completed with error",
        ApplicationRunStatus.RECEIVED: "received by platform",
        ApplicationRunStatus.REJECTED: "rejected by platform",
        ApplicationRunStatus.RUNNING: "running on platform",
        ApplicationRunStatus.SCHEDULED: "scheduled for processing",
    }

    if status in status_mapping:
        return status_mapping[status]

    message = f"Unknown application status: {status.value}"
    logger.error(message)
    raise RuntimeError(message)


def get_mime_type_for_artifact(artifact: OutputArtifactData | InputArtifactData | OutputArtifactElement) -> str:
    """Get the MIME type for a given artifact.

    Args:
        artifact (OutputArtifact | InputArtifact | OutputArtifactElement): The artifact to get the MIME type for.

    Returns:
        str: The MIME type of the artifact.
    """
    if isinstance(artifact, InputArtifactData):
        return str(artifact.mime_type)
    if isinstance(artifact, OutputArtifactData):
        return str(artifact.mime_type)
    metadata = artifact.metadata or {}
    return str(metadata.get("media_type", metadata.get("mime_type", "application/octet-stream")))


def get_file_extension_for_artifact(artifact: OutputArtifactData) -> str:
    """Get the file extension for a given artifact.

    Returns .bin if no known extension is found for mime type.

    Args:
        artifact (OutputArtifact): The artifact to get the extension for.

    Returns:
        str: The file extension of the artifact.
    """
    mimetypes.init()
    mimetypes.add_type("application/vnd.apache.parquet", ".parquet")
    mimetypes.add_type("application/geo+json", ".json")

    file_extension = mimetypes.guess_extension(get_mime_type_for_artifact(artifact))
    if file_extension == ".geojson":
        file_extension = ".json"
    if not file_extension:
        file_extension = ".bin"
    logger.debug("Guessed file extension: '%s' for artifact '%s'", file_extension, artifact.name)
    return file_extension
