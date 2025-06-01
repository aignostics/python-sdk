"""CLI of dataset module."""

import webbrowser
from pathlib import Path
from typing import Annotated

import requests
import typer

from aignostics.platform import generate_signed_url as platform_generate_signed_url
from aignostics.system import Service as SystemService
from aignostics.utils import console, get_logger

logger = get_logger(__name__)

PATH_LENFTH_MAX = 260
TARGET_LAYOUT_DEFAULT = "%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID/"

cli = typer.Typer(
    name="dataset",
    help="Download datasets from National Institute of Cancer (NIC) and Aignostics.",
)

idc_app = typer.Typer()
cli.add_typer(
    idc_app,
    name="idc",
    help="Download public datasets from Image Data Commons (IDC) Portal of National Institute of Cancer (NIC).",
)

aignostics_app = typer.Typer()
cli.add_typer(aignostics_app, name="aignostics", help="Download proprietary sample datasets from Aignostics.")


@idc_app.command()
def browse() -> None:
    """Open browser to explore IDC portal."""
    webbrowser.open("https://portal.imaging.datacommons.cancer.gov/explore/")


@idc_app.command()
def indices() -> None:
    """List available columns in given of the IDC Portal."""
    from ._idc_index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    console.print(list(client.indices_overview.keys()))


@idc_app.command()
def columns(
    index: Annotated[
        str,
        typer.Option(
            help="List available columns in given of the IDC Portal."
            " See List available columns in given of the IDC Portal for available indices"
        ),
    ] = "sm_instance_index",
) -> None:
    """List available columns in given of the IDC Portal."""
    from ._idc_index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    client.fetch_index(index)
    console.print(list(getattr(client, index).columns))


@idc_app.command()
def query(
    query: Annotated[
        str,
        typer.Argument(
            help="SQL Query to execute."
            "See https://idc-index.readthedocs.io/en/latest/column_descriptions.html "
            "for indices and their attributes"
        ),
    ] = """SELECT
    SOPInstanceUID, SeriesInstanceUID, ImageType[3], instance_size, TotalPixelMatrixColumns, TotalPixelMatrixRows
FROM
    sm_instance_index
WHERE
    TotalPixelMatrixColumns > 25000
    AND TotalPixelMatrixRows > 25000
    AND ImageType[3] = 'VOLUME'
""",
    indices: Annotated[
        str,
        typer.Option(
            help="Comma separated list of additional indices to sync before running the query."
            " The main index is always present. By default sm_instance_index is synched in addition."
            " See https://idc-index.readthedocs.io/en/latest/column_descriptions.html for available indices."
        ),
    ] = "sm_instance_index",
) -> None:
    """Query IDC index. For example queries see https://github.com/ImagingDataCommons/IDC-Tutorials/blob/master/notebooks/labs/idc_rsna2023.ipynb."""
    import pandas as pd  # noqa: PLC0415

    from ._idc_index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    for idx in [idx.strip() for idx in indices.split(",") if idx.strip()]:
        logger.info("Fetching index: '%s'", idx)
        client.fetch_index(idx)

    pd.set_option("display.max_colwidth", None)
    console.print(client.sql_query(sql_query=query))  # type: ignore[no-untyped-call]


@idc_app.command(name="download")
def idc_download(
    source: Annotated[
        str,
        typer.Argument(
            help="Identifier or comma-separated set of identifiers."
            " IDs matched against collection_id, PatientId, StudyInstanceUID, SeriesInstanceUID or SOPInstanceUID."
        ),
    ],
    target: Annotated[
        Path,
        typer.Argument(
            help="target directory for download",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ] = SystemService.get_user_data_directory("datasets/idc"),  # noqa: B008
    target_layout: Annotated[
        str, typer.Option(help="layout of the target directory. See default for available elements for use")
    ] = TARGET_LAYOUT_DEFAULT,
    dry_run: Annotated[bool, typer.Option(help="dry run")] = False,
) -> None:
    """Download from manifest file, identifier, or comma-separate set of identifiers.

    Raises:
        typer.Exit: If the target directory does not exist.
    """
    from ._idc_index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    logger.info("Downloading instance index from IDC version: %s", client.get_idc_version())  # type: ignore[no-untyped-call]

    target_directory = Path(target)
    if not target_directory.is_dir():
        logger.error("Target directory does not exist: %s", target_directory)
        raise typer.Exit(code=1)

    item_ids = [item for item in source.split(",") if item]

    if not item_ids:
        logger.error("No valid IDs provided.")

    index_df = client.index
    client.fetch_index("sm_instance_index")
    logger.info("Downloaded instance index")
    sm_instance_index_df = client.sm_instance_index

    def check_and_download(column_name: str, item_ids: list[str], target_directory: Path, kwarg_name: str) -> bool:
        if column_name != "SOPInstanceUID":
            matches = index_df[column_name].isin(item_ids)
            matched_ids = index_df[column_name][matches].unique().tolist()
        else:
            matches = sm_instance_index_df[column_name].isin(item_ids)  # type: ignore
            matched_ids = sm_instance_index_df[column_name][matches].unique().tolist()  # type: ignore
        if not matched_ids:
            return False
        unmatched_ids = list(set(item_ids) - set(matched_ids))
        if unmatched_ids:
            logger.debug("Partial match for %s: matched %s, unmatched %s", column_name, matched_ids, unmatched_ids)
        logger.info("Identified matching %s: %s", column_name, matched_ids)
        client.download_from_selection(**{  # type: ignore[no-untyped-call]
            kwarg_name: matched_ids,
            "downloadDir": target_directory,
            "dirTemplate": target_layout,
            "quiet": False,
            "show_progress_bar": True,
            "use_s5cmd_sync": True,
            "dry_run": dry_run,
        })
        return True

    matches_found = 0
    matches_found += check_and_download("collection_id", item_ids, target_directory, "collection_id")
    matches_found += check_and_download("PatientID", item_ids, target_directory, "patientId")
    matches_found += check_and_download("StudyInstanceUID", item_ids, target_directory, "studyInstanceUID")
    matches_found += check_and_download("SeriesInstanceUID", item_ids, target_directory, "seriesInstanceUID")
    matches_found += check_and_download("SOPInstanceUID", item_ids, target_directory, "sopInstanceUID")
    if not matches_found:
        logger.error(
            "None of the values passed matched any of the identifiers: "
            "collection_id, PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID."
        )


@aignostics_app.command("download")
def aignostics_download(
    source_url: Annotated[
        str,
        typer.Argument(
            help="URL to download, e.g. gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
        ),
    ],
    destination_directory: Annotated[
        Path,
        typer.Argument(
            help="Destination directory to download to",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ] = SystemService.get_user_data_directory("datasets/aignostics"),  # noqa: B008
) -> None:
    """Download from bucket to folder via a signed URL."""
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

    # Get filename from URL
    filename = source_url.split("/")[-1]

    # Generate a signed URL
    source_url_signed = platform_generate_signed_url(source_url)

    output_path = Path(destination_directory) / filename

    console.print(f"Downloading from {source_url} to {output_path}")

    # Make sure the destination directory exists
    Path(destination_directory).mkdir(parents=True, exist_ok=True)

    # Start the request to get content length
    response = requests.get(source_url_signed, stream=True, timeout=60)
    total_size = int(response.headers.get("content-length", 0))

    with Progress(
        TextColumn("[progress.description]Downloading"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        # Create a task for overall progress
        task = progress.add_task(f"Downloading {filename}", total=total_size)

        # Write the file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

    console.print(f"[green]Successfully downloaded to {output_path}[/green]")
