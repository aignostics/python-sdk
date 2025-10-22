"""Utility functions for application module.

1. Printing of application resources
2. Reading/writing metadata CSV files
3. Mime type handling.
"""

import csv
import mimetypes
from enum import StrEnum
from pathlib import Path
from typing import Any

import humanize

from aignostics.platform import (
    InputArtifactData,
    OutputArtifactData,
    OutputArtifactElement,
    Run,
    RunData,
    RunState,
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


def retrieve_and_print_run_details(run: Run) -> None:
    """Retrieve and print detailed information about a run.

    Args:
        run (Run): The Run object

    """
    run_data = run.details()
    console.print(f"[bold]Run Details for {run.run_id}[/bold]")
    console.print("=" * 80)
    console.print(f"[bold]Application (Version):[/bold] {run_data.application_id} ({run_data.version_number})   ")
    if run_data.state is RunState.TERMINATED and run_data.termination_reason:
        status_str = f"{run_data.state.value} ({run_data.termination_reason})"
    else:
        status_str = f"{run_data.state.value}"
    console.print(f"[bold]Status:[/bold] {status_str}")
    console.print(
        f"  - {run_data.statistics.item_count} items\n"
        f"  - {run_data.statistics.item_pending_count} pending\n"
        f"  - {run_data.statistics.item_processing_count} processing\n"
        f"  - {run_data.statistics.item_skipped_count} skipped\n"
        f"  - {run_data.statistics.item_succeeded_count} succeeded\n"
        f"  - {run_data.statistics.item_user_error_count} user errors\n"
        f"  - {run_data.statistics.item_system_error_count} system errors\n"
    )
    console.print(f"[bold]Error:[/bold] {run_data.error_message or 'N/A'} ({run_data.error_code or 'N/A'})")
    if run_data.terminated_at and run_data.submitted_at:
        duration = run_data.terminated_at - run_data.submitted_at
        duration_str = humanize.precisedelta(duration)
        console.print(f"[bold]Duration:[/bold] {duration_str}")
    else:
        duration_str = "still processing"
    console.print(f"[bold]Submitted:[/bold] {run_data.submitted_at} ({run_data.submitted_by})")
    console.print(f"[bold]Terminated:[/bold] {run_data.terminated_at} ({duration_str})")

    console.print(f"[bold]Custom Metadata:[/bold] {run_data.custom_metadata or 'None'}")

    # Get and display detailed item status
    console.print()
    console.print("[bold]Items:[/bold]")

    _retrieve_and_print_run_items(run)
    _print_run_statistics(run)


def _retrieve_and_print_run_items(run: Run) -> None:
    """Retrieve and print information about items in a run.

    Args:
        run (Run): The Run object
    """
    # Get results with detailed information
    results = run.results()
    if not results:
        console.print("  No item results available.")
        return

    for item in results:
        console.print(f"  [bold]Item ID:[/bold] {item.item_id}")
        console.print(f"  [bold]Item External ID:[/bold] {item.external_id}")
        console.print(f"  [bold]Status (Termination Reason):[/bold] {item.state.value} ({item.termination_reason})")
        console.print(f"  [bold]Error Message (Code):[/bold] {item.error_message} ({item.error_code})")

        # TODO(Andreas): error_code is missing on item model; should be printed here as well.
        # Please add in the openapi.json and regenerate the SDK, and add line here.
        # Can be set to generic code initially so we have a stable API at last.
        if item.error_message:
            console.print(f"  [error]Error:[/error] {item.error_message}")

        if item.output_artifacts:
            console.print("  [bold]Output Artifacts:[/bold]")
            for artifact in item.output_artifacts:
                console.print(f"    - Name: {artifact.name}")
                console.print(f"      MIME Type: {get_mime_type_for_artifact(artifact)}")
                console.print(f"      Artifact ID: {artifact.output_artifact_id}")
                console.print(f"      Download URL: {artifact.download_url}")

        console.print()


def _print_run_statistics(run: Run) -> None:
    """Print statistics of items in a run.

    Args:
        run (Run): The Run object
    """
    console.print("[bold]Item Statistics:[/bold]")
    console.print(run.details().statistics)


def print_runs_verbose(runs: list[RunData]) -> None:
    """Print detailed information about runs, sorted by submitted_at in descending order.

    Args:
        runs (list[RunData]): List of run data

    """
    from ._service import Service  # noqa: PLC0415

    console.print("[bold]Application Runs:[/bold]")
    console.print("=" * 80)

    for run in runs:
        console.print(f"[bold]Run ID:[/bold] {run.run_id}")
        console.print(f"[bold]Application:[/bold] {run.application_id} ({run.version_number})")
        console.print(f"[bold]Status:[/bold] {run.state.value}")
        console.print(
            f"[bold]Submitted:[/bold] "
            f"{run.submitted_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')} "
            f"({run.submitted_by})"
        )

        try:
            _print_run_statistics(Service().application_run(run.run_id))
        except Exception as e:
            logger.exception("Failed to retrieve  statistics for run with ID '%s'", run.run_id)
            console.print(f"[error]Error:[/error] Failed to retrieve statistics for run with ID '{run.run_id}': {e}")
            continue
        console.print("-" * 80)


def print_runs_non_verbose(runs: list[RunData]) -> None:
    """Print simplified information about runs, sorted by submitted_at in descending order.

    Args:
        runs (list[RunData]): List of runs

    """
    console.print("[bold]Application Run IDs:[/bold]")

    for run_status in runs:
        console.print(
            f"- [bold]{run_status.run_id}[/bold] of "
            f"[bold]{run_status.application_id} ({run_status.version_number})[/bold] "
            f"(submitted: {run_status.submitted_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"status: {run_status.state.value})"
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
    status: RunState,
) -> str:
    """Convert application status to a human-readable string.

    Args:
        status (RunState): The application status

    Raises:
        RuntimeError: If the status is invalid or unknown

    Returns:
        str: Human-readable string representation of the status
    """
    status_mapping = {
        RunState.PENDING: "pending",
        RunState.PROCESSING: "processing",
        RunState.TERMINATED: "terminated",
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
