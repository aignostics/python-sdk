"""Utility functions to ease using the platform client."""

import csv
import os
from enum import StrEnum
from operator import itemgetter
from pathlib import Path
from typing import Literal

from boto3.session import Session
from botocore.client import Config

from aignostics.platform import (
    Application,
    ApplicationRun,
    ApplicationRunStatus,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
)
from aignostics.utils import console, get_logger

logger = get_logger(__name__)


class OutputFormat(StrEnum):
    """
    Enum representing the supported output formats.

    This enum defines the possible formats for output data:
    - TEXT: Output data as formatted text
    - JSON: Output data in JSON format

    Usage:
        format = OutputFormat.YAML
        print(f"Using {format} format")
    https://nicegui.io/documentation/html
    """

    TEXT = "text"
    JSON = "json"


def get_platform_client() -> Client | None:
    """Get a client instance.

    Returns:
        Client | None: A Client instance if successful, None otherwise.
    """
    try:
        logger.debug("Creating authenticated client.")
        client = Client()
        logger.debug("Authenticated client created.")
        return client
    except Exception as e:
        logger.exception("Failed to create authenticated client.")
        console.print(f"[bold red]Error:[/bold red] Failed to connect to Aignostics Platform: {e}")
    return None


def _get_s3_client(endpoint_url: str = "https://storage.googleapis.com"):  # noqa: ANN202
    """Get a client instance for S3.

    Returns:
        botocore.client.S3: A Boto3 S3 client instance.
    """
    # https://www.kmp.tw/post/accessgcsusepythonboto3/
    hmac_access_key_id = os.environ.get("AIGNOSTICS_BUCKET_HMAC_ACCESS_KEY_ID")
    hmac_secret_access_key = os.environ.get("AIGNOSTICS_BUCKET_HMAC_SECRET_ACCESS_KEY")

    region_name = "EUROPE-WEST3"

    session = Session(
        aws_access_key_id=hmac_access_key_id, aws_secret_access_key=hmac_secret_access_key, region_name=region_name
    )
    return session.client("s3", endpoint_url=endpoint_url, config=Config(signature_version="s3v4"))


def create_signed_upload_url(bucket_name: str, object_key: str) -> str:
    """Generates a signed URL to upload a Google Cloud Storage object.

    Args:
        bucket_name (str): The name of the bucket to generate a signed URL for.
        object_key (str): The key of the object to generate a signed URL for.

    Returns:
        str: A signed URL that can be used to upload to the bucket and key.
    """
    return _get_s3_client().generate_presigned_url(
        ClientMethod="put_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=3600
    )


def create_signed_download_url(bucket_name: str, object_key: str) -> str:
    """Generates a signed URL to download a Google Cloud Storage object.

    Args:
        bucket_name (str): The name of the bucket to generate a signed URL for.
        object_key (str): The key of the object to generate a signed URL for.

    Returns:
        str: A signed URL that can be used to download from the bucket and key.
    """
    return _get_s3_client().generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=3600
    )


def construct_input_items(source_csv: Path) -> list[InputItem]:
    """Construct payload from CSV file.

    Args:
        source_csv (Path): Path to the CSV file

    Returns:
        list: List of payload items
    """
    payload = []
    logger.debug("Constructing payload from CSV file: %s", source_csv)
    with open(str(source_csv), newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";", quotechar='"')
        pos = 0
        for row in reader:
            # TODO(Helmut): Introspect to generate the below
            if pos == 0:
                pos += 1
                continue
            # Parse the GCS URL (gs://bucketname/path)
            if row[0].startswith("gs://"):
                # Remove 'gs://' prefix and split into bucket name and object key
                url_parts = row[0][5:].split("/", 1)
                if len(url_parts) == 2:
                    bucket_name = url_parts[0]
                    object_key = url_parts[1]
                    download_url = create_signed_download_url(bucket_name, object_key)
                    logger.debug("Constructed signed download URL: %s", download_url)
                else:
                    logger.warning("Invalid GCS URL format: %s", row[0])
                    continue
            else:
                logger.warning("URL '%s' is not a valid GCS URL (should start with 'gs://')", row[0])
                continue

            payload.append(
                InputItem(
                    reference=str(pos),
                    input_artifacts=[
                        InputArtifact(
                            name="user_slide",
                            download_url=download_url,
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
            pos += 1
    return payload


def application_versions_sorted_by_semver(app: Application, client: Client) -> list[ApplicationVersion]:
    """Get application versions sorted by semver, latest first.

    Args:
        app(Application): The application to find versions for
        client(Client): The Client instance to use

    Returns:
        list: List of version objects sorted by semantic versioning (latest first),
            or empty list if no versions are found
    """
    # Get versions for this application
    versions = list(client.applications.versions.list(app))

    # If no versions available
    if not versions:
        return []

    # Extract semantic versions from the version property
    versions_with_semver = []
    for v in versions:
        try:
            # Split into major, minor, patch components for proper comparison
            version_parts = [int(x) for x in v.version.split(".")]
            versions_with_semver.append((v, version_parts))
        except (ValueError, AttributeError):
            # If we can't parse the version or version attribute doesn't exist, skip it
            continue

    # Sort by semantic version (major, minor, patch)
    if versions_with_semver:
        versions_with_semver.sort(key=itemgetter(1), reverse=True)
        # Return just the version objects, not the tuples
        return [item[0] for item in versions_with_semver]

    # If we couldn't parse any versions, return all versions as is
    return versions


def find_latest_application_version_id(app: Application, client: Client) -> str | None:
    """Find the latest version of an application.

    Args:
        app(Application): The application to find the latest version for
        client(Client): The Client instance to use

    Returns:
        str: The application_version_id of the latest version, or "No versions" if no versions are found
    """
    # Get sorted versions using the existing utility function
    sorted_versions = application_versions_sorted_by_semver(app, client)

    # If no versions available
    if not sorted_versions:
        return None

    # The first item is the latest version
    return str(sorted_versions[0].application_version_id)


def find_application_by_id(application_id: str, client: Client) -> Application | None:
    """Find an application by its ID.

    Args:
        application_id(str): The ID of the application to find
        client(Client): The Client instance to use

    Returns:
        Application | None: The Application object if found, None otherwise
    """
    applications = client.applications.list()
    for application in applications:
        if application.application_id == application_id:
            return application
    return None


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
        logger.exception("Failed to get status for run with ID '%s'", run.application_run_id)
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
        logger.exception("Failed to get item statuses for run with ID '%s'", run.application_run_id)
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
    """Print detailed information about runs, sorted by triggered_at in descending order.

    Args:
        runs: List of runs

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Runs:[/bold]")
    console.print("=" * 80)

    run_count = 0

    # First collect all valid run status objects with their data
    runs_with_status = []
    for run in runs:
        try:
            _, run_status = _retrieve_and_print_run_status(run, 0)  # Use 0 as we'll count later
            if run_status:
                runs_with_status.append((run, run_status))
            else:
                run_count += 1  # Count failed runs
        except Exception as e:
            logger.exception("Failed to get status for run with ID '%s'", run.application_run_id)
            console.print(
                f"[bold red]Error:[/bold red] Failed to get status for run with ID '{run.application_run_id}': {e}"
            )
            run_count += 1
            continue

    # Sort runs by triggered_at in descending order (newest first)
    sorted_runs = sorted(runs_with_status, key=lambda x: x[1].triggered_at, reverse=True)

    # Display the sorted runs
    for run, run_status in sorted_runs:
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
            logger.exception("Failed to retrieve item status counts for run with ID '%s'", run.application_run_id)
            console.print(
                f"[bold red]Error:[/bold red] Failed to retrieve item status counts for run with ID "
                f"'{run.application_run_id}': {e}"
            )
            continue
        console.print("-" * 80)
        run_count += 1

    return run_count


def print_runs_non_verbose(runs: list[ApplicationRun]) -> int:
    """Print simplified information about runs, sorted by triggered_at in descending order.

    Args:
        runs: List of runs

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Run IDs:[/bold]")
    run_count = 0

    # First collect all valid run status objects with their data
    runs_with_status = []
    for run in runs:
        try:
            _, run_status = _retrieve_and_print_run_status(run, 0)  # Use 0 as we'll count later
            if run_status:
                runs_with_status.append(run_status)
            else:
                run_count += 1  # Count failed runs
        except Exception as e:
            logger.exception("Failed to get status for run with ID '%s'", run.application_run_id)
            console.print(
                f"[bold red]Error:[/bold red] Failed to get status for run with ID '{run.application_run_id}': {e}"
            )
            run_count += 1
            continue

    # Sort runs by triggered_at in descending order (newest first)
    sorted_runs = sorted(runs_with_status, key=lambda x: x.triggered_at, reverse=True)

    # Display the sorted runs
    for run_status in sorted_runs:
        console.print(
            f"- [bold]{run_status.application_run_id}[/bold] of "
            f"[bold]{run_status.application_version_id}[/bold] "
            f"(triggered: {run_status.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}, "
            f"status: {run_status.status.value})"
        )
        run_count += 1

    return run_count
