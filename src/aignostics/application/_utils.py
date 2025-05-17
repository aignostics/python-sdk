"""Utility functions to ease using the platform client."""

import csv
import os
from enum import StrEnum
from pathlib import Path
from typing import Literal, cast

from boto3.session import Session
from botocore.client import BaseClient, Config

from aignostics.platform import (
    ApplicationRun,
    ApplicationRunData,
    Client,
    InputArtifact,
    InputItem,
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

    Usage:
        format = OutputFormat.YAML
        print(f"Using {format} format")
    https://nicegui.io/documentation/html
    """

    TEXT = "text"
    JSON = "json"


def _get_s3_client(endpoint_url: str = "https://storage.googleapis.com") -> BaseClient:
    """Get a client instance for S3.

    Args:
        endpoint_url (str): The endpoint URL for the S3 service.

    Returns:
        BaseClient: A Boto3 S3 client instance.
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
    url = _get_s3_client().generate_presigned_url(
        ClientMethod="put_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=3600
    )
    return cast("str", url)


def create_signed_download_url(bucket_name: str, object_key: str) -> str:
    """Generates a signed URL to download a Google Cloud Storage object.

    Args:
        bucket_name (str): The name of the bucket to generate a signed URL for.
        object_key (str): The key of the object to generate a signed URL for.

    Returns:
        str: A signed URL that can be used to download from the bucket and key.
    """
    url = _get_s3_client().generate_presigned_url(
        ClientMethod="get_object", Params={"Bucket": bucket_name, "Key": object_key}, ExpiresIn=3600
    )
    return cast("str", url)


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
            if pos == 0:
                pos += 1
                continue
            # Parse the GCS URL (gs://bucketname/path)
            if row[0].startswith("gs://"):
                # Remove 'gs://' prefix and split into bucket name and object key
                url_parts = row[0][5:].split("/", 1)
                if len(url_parts) == 2:  # noqa: PLR2004
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


def retrieve_and_print_run_details(run: ApplicationRun) -> None:
    """Retrieve and print detailed information about a run.

    Args:
        run(ApplicationRun): The ApplicationRun object

    """
    run_data = run.find()
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


def print_runs_verbose(runs: list[ApplicationRunData], client: Client) -> int:
    """Print detailed information about runs, sorted by triggered_at in descending order.

    Args:
        runs (list[ApplicationRunData]): List of run data
        client (Client): The Client instance to use

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Runs:[/bold]")
    console.print("=" * 80)

    run_count = 0

    # Sort runs by triggered_at in descending order (newest first)
    sorted_runs = sorted(runs, key=lambda x: x.triggered_at, reverse=True)

    # Display the sorted runs
    for run in sorted_runs:
        console.print(f"[bold]Run ID:[/bold] {run.application_run_id}")
        console.print(f"[bold]App Version:[/bold] {run.application_version_id}")
        console.print(f"[bold]Status:[/bold] {run.status.value}")
        console.print(f"[bold]Triggered at:[/bold] {run.triggered_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        console.print(f"[bold]Organization:[/bold] {run.organization_id}")

        try:
            _retrieve_and_print_item_status_counts(client.run(run.application_run_id))
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


def print_runs_non_verbose(runs: list[ApplicationRunData]) -> int:
    """Print simplified information about runs, sorted by triggered_at in descending order.

    Args:
        runs: List of runs

    Returns:
        int: Number of runs processed
    """
    console.print("[bold]Application Run IDs:[/bold]")
    run_count = 0

    # Sort runs by triggered_at in descending order (newest first)
    sorted_runs = sorted(runs, key=lambda x: x.triggered_at, reverse=True)

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
