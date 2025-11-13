"""Utility functions for application module.

1. Printing of application resources
2. Reading/writing metadata CSV files
3. Mime type handling.
4. Date/time validation.
"""

import csv
import mimetypes
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import humanize
from loguru import logger

from aignostics.constants import (
    HETA_APPLICATION_ID,
    TEST_APP_APPLICATION_ID,
    WSI_SUPPORTED_FILE_EXTENSIONS,
    WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP,
)
from aignostics.platform import (
    InputArtifactData,
    OutputArtifactData,
    OutputArtifactElement,
    Run,
    RunData,
    RunItemStatistics,
    RunState,
)
from aignostics.utils import console

RUN_FAILED_MESSAGE = "Failed to get status for run with ID '%s'"


def validate_due_date(due_date: str | None) -> None:
    """Validate that due_date is in ISO 8601 format and in the future.

    Args:
        due_date (str | None): The datetime string to validate.

    Raises:
        ValueError: If
            the format is invalid
            or the due_date is not in the future.
    """
    if due_date is None:
        return

    # Try parsing with fromisoformat (handles most ISO 8601 formats)
    try:
        # Handle 'Z' suffix by replacing with '+00:00'
        normalized = due_date.replace("Z", "+00:00")
        parsed_dt = datetime.fromisoformat(normalized)
    except (ValueError, TypeError) as e:
        message = (
            f"Invalid ISO 8601 format for due_date. "
            f"Expected format like '2025-10-19T19:53:00+00:00' or '2025-10-19T19:53:00Z', "
            f"but got: '{due_date}' (error: {e})"
        )
        raise ValueError(message) from e

    # Ensure the datetime is timezone-aware (reject naive datetimes)
    if parsed_dt.tzinfo is None:
        message = (
            f"Invalid ISO 8601 format for due_date. "
            f"Expected format with timezone like '2025-10-19T19:53:00+00:00' or '2025-10-19T19:53:00Z', "
            f"but got: '{due_date}' (missing timezone information)"
        )
        raise ValueError(message)

    # Check that the datetime is in the future
    now = datetime.now(UTC)
    if parsed_dt <= now:
        message = (
            f"due_date must be in the future. "
            f"Got '{due_date}' ({parsed_dt.isoformat()}), "
            f"but current UTC time is {now.isoformat()}"
        )
        raise ValueError(message)


class OutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - TEXT: Output data as formatted text
    - JSON: Output data in JSON format
    """

    TEXT = "text"
    JSON = "json"


def _format_status_string(state: RunState, termination_reason: str | None = None) -> str:
    """Format status string with optional termination reason.

    Args:
        state (RunState): The run state
        termination_reason (str | None): Optional termination reason

    Returns:
        str: Formatted status string
    """
    if state is RunState.TERMINATED and termination_reason:
        return f"{state.value} ({termination_reason})"
    return f"{state.value}"


def _format_duration_string(submitted_at: datetime | None, terminated_at: datetime | None) -> str:
    """Format duration string for a run.

    Args:
        submitted_at: Submission timestamp
        terminated_at: Termination timestamp

    Returns:
        str: Formatted duration string
    """
    if terminated_at and submitted_at:
        duration = terminated_at - submitted_at
        return humanize.precisedelta(duration)
    return "still processing"


def _format_run_statistics(statistics: RunItemStatistics) -> str:
    """Format run statistics as a multi-line string.

    Args:
        statistics: Run statistics object

    Returns:
        str: Formatted statistics string
    """
    return (
        f"  - {statistics.item_count} items\n"
        f"  - {statistics.item_pending_count} pending\n"
        f"  - {statistics.item_processing_count} processing\n"
        f"  - {statistics.item_skipped_count} skipped\n"
        f"  - {statistics.item_succeeded_count} succeeded\n"
        f"  - {statistics.item_user_error_count} user errors\n"
        f"  - {statistics.item_system_error_count} system errors"
    )


def _format_run_details(run: RunData) -> str:
    """Format detailed run information as a single string.

    Args:
        run (RunData): Run data to format

    Returns:
        str: Formatted run details
    """
    status_str = _format_status_string(run.state, run.termination_reason)
    duration_str = _format_duration_string(run.submitted_at, run.terminated_at)

    output = (
        f"[bold]Run ID:[/bold] {run.run_id}\n"
        f"[bold]Application (Version):[/bold] {run.application_id} ({run.version_number})\n"
        f"[bold]Status (Termination Reason):[/bold] {status_str}\n"
        f"[bold]Output:[/bold] {run.output.value}\n"
    )

    if run.error_message or run.error_code:
        output += f"[bold]Error Message (Code):[/bold] {run.error_message or 'N/A'} ({run.error_code or 'N/A'})\n"

    output += (
        f"[bold]Statistics:[/bold]\n"
        f"{_format_run_statistics(run.statistics)}\n"
        f"[bold]Submitted (by):[/bold] {run.submitted_at} ({run.submitted_by})\n"
        f"[bold]Terminated (duration):[/bold] {run.terminated_at} ({duration_str})\n"
        f"[bold]Custom Metadata:[/bold] {run.custom_metadata or 'None'}"
    )

    return output


def retrieve_and_print_run_details(run_handle: Run) -> None:
    """Retrieve and print detailed information about a run.

    Args:
        run_handle (Run): The Run handle

    """
    run = run_handle.details()

    output = f"[bold]Run Details for {run.run_id}[/bold]\n{'=' * 80}\n{_format_run_details(run)}\n\n[bold]Items:[/bold]"

    console.print(output)
    _retrieve_and_print_run_items(run_handle)


def _retrieve_and_print_run_items(run_handle: Run) -> None:
    """Retrieve and print information about items in a run.

    Args:
        run_handle (Run): The Run handle
    """
    results = run_handle.results()
    if not results:
        console.print("  No item results available.")
        return

    for item in results:
        item_output = (
            f"  [bold]Item ID:[/bold] {item.item_id}\n"
            f"  [bold]Item External ID:[/bold] `{item.external_id}`\n"
            f"  [bold]Status (Termination Reason):[/bold] {item.state.value} ({item.termination_reason})\n"
            f"  [bold]Error Message (Code):[/bold] {item.error_message} ({item.error_code})\n"
            f"  [bold]Custom Metadata:[/bold] {item.custom_metadata or 'None'}"
        )

        if item.output_artifacts:
            artifacts_output = "\n  [bold]Output Artifacts:[/bold]"
            for artifact in item.output_artifacts:
                artifacts_output += (
                    f"\n    - Name: {artifact.name}"
                    f"\n      MIME Type: {get_mime_type_for_artifact(artifact)}"
                    f"\n      Artifact ID: {artifact.output_artifact_id}"
                    f"\n      Download URL: {artifact.download_url}"
                )
            item_output += artifacts_output

        console.print(f"{item_output}\n")


def print_runs_verbose(runs: list[RunData]) -> None:
    """Print detailed information about runs, sorted by submitted_at in descending order.

    Args:
        runs (list[RunData]): List of run data

    """
    output = f"[bold]Application Runs:[/bold]\n{'=' * 80}"

    for run in runs:
        output += f"\n{_format_run_details(run)}\n{'-' * 80}"

    console.print(output)


def print_runs_non_verbose(runs: list[RunData]) -> None:
    """Print simplified information about runs, sorted by submitted_at in descending order.

    Args:
        runs (list[RunData]): List of runs

    """
    output = "[bold]Application Run IDs:[/bold]"

    for run in runs:
        status_str = _format_status_string(run.state, run.termination_reason)

        if run.error_message or run.error_code:
            status_str += f" | error: {run.error_message or 'N/A'} ({run.error_code or 'N/A'})"

        output += (
            f"\n- [bold]{run.run_id}[/bold] of "
            f"[bold]{run.application_id} ({run.version_number})[/bold] "
            f"(submitted: {run.submitted_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"status: {status_str}, "
            f"output: {run.output.value})"
        )

    console.print(output)


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
        logger.warning("Failed to parse metadata CSV file '{}': {}", metadata_csv_file, e)
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
    logger.trace("Guessed file extension: '{}' for artifact '{}'", file_extension, artifact.name)
    return file_extension


def get_supported_extensions_for_application(application_id: str) -> set[str]:
    """Get the list of supported file extensions for a given application.

    Args:
        application_id (str): The application ID

    Returns:
        set[str]: List of supported file extensions

    Raises:
        RuntimeError: If the application ID is not supported
    """
    if application_id == HETA_APPLICATION_ID:
        return WSI_SUPPORTED_FILE_EXTENSIONS
    if application_id == TEST_APP_APPLICATION_ID:
        return WSI_SUPPORTED_FILE_EXTENSIONS_TEST_APP

    message = f"Unsupported application {application_id}"
    logger.critical(message)
    raise RuntimeError(message)
