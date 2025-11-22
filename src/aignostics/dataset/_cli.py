"""CLI of dataset module."""

import sys
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from aignostics.utils import console, get_user_data_directory

PATH_LENGTH_MAX = 260
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
    from aignostics.third_party.idc_index import IDCClient  # noqa: PLC0415

    try:
        client = IDCClient.client()
        console.print(list(client.indices_overview.keys()))
    except Exception as e:
        message = f"Error fetching indices overview: {e!s}"
        logger.exception(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)


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
    from aignostics.third_party.idc_index import IDCClient  # noqa: PLC0415

    try:
        client = IDCClient.client()
        client.fetch_index(index)
        console.print(list(getattr(client, index).columns))
    except Exception as e:
        message = f"Error fetching columns for index '{index}': {e!s}"
        logger.exception(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)


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

    from aignostics.third_party.idc_index import IDCClient  # noqa: PLC0415

    try:
        client = IDCClient.client()
        for idx in [idx.strip() for idx in indices.split(",") if idx.strip()]:
            logger.debug("Fetching index: '{}'", idx)
            client.fetch_index(idx)

        pd.set_option("display.max_colwidth", None)
        console.print(client.sql_query(sql_query=query))  # type: ignore[no-untyped-call]
    except Exception as e:
        message = f"Error executing query '{query}': {e!s}"
        logger.exception(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)


@idc_app.command(name="download")
def idc_download(
    source: Annotated[
        str,
        typer.Argument(
            help="Identifier or comma-separated set of identifiers."
            " IDs matched against collection_id, PatientId, StudyInstanceUID, SeriesInstanceUID or SOPInstanceUID."
            " Example: 1.3.6.1.4.1.5962.99.1.1069745200.1645485340.1637452317744.2.0"
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
    ] = get_user_data_directory("datasets/idc"),  # noqa: B008
    target_layout: Annotated[
        str, typer.Option(help="layout of the target directory. See default for available elements for use")
    ] = TARGET_LAYOUT_DEFAULT,
    dry_run: Annotated[bool, typer.Option(help="dry run")] = False,
) -> None:
    """Download from manifest file, identifier, or comma-separate set of identifiers."""
    from ._service import Service  # noqa: PLC0415

    try:
        matches_found = Service.download_idc(
            source=source,
            target=target,
            target_layout=target_layout,
            dry_run=dry_run,
        )
        console.print(f"[green]Successfully downloaded {matches_found} identifier type(s) to {target}[/green]")
    except ValueError as e:
        logger.warning(f"Bad input to download from IDC for IDs '{source}': {e}")
        console.print(f"[warning]Warning:[/warning] {e}")
        sys.exit(2)
    except Exception as e:
        message = f"Error downloading data for IDs '{source}': {e!s}"
        logger.exception(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)


@aignostics_app.command("download")
def aignostics_download(
    source_url: Annotated[
        str,
        typer.Argument(
            help="URL to download."
            " Example: gs://aignx-storage-service-dev/sample_data_formatted/9375e3ed-28d2-4cf3-9fb9-8df9d11a6627.tiff"
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
    ] = get_user_data_directory("datasets/aignostics"),  # noqa: B008
) -> None:
    """Download from bucket to folder via a bucket URL."""
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

    from ._service import Service  # noqa: PLC0415

    try:
        # Get filename for progress display
        filename = source_url.split("/")[-1]

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
            task = progress.add_task(f"Downloading {filename}", total=0)

            def update_progress(bytes_downloaded: int, total_size: int, _filename: str) -> None:
                progress.update(task, advance=bytes_downloaded, total=total_size)

            output_path = Service.download_aignostics(
                source_url=source_url,
                destination_directory=destination_directory,
                download_progress_callable=update_progress,
            )

        console.print(f"[green]Successfully downloaded to {output_path}[/green]")
    except ValueError as e:
        logger.warning(f"Bad input to download from '{source_url}': {e}")
        console.print(f"[warning]Warning:[/warning] Bad input: {e}")
        sys.exit(2)
    except Exception as e:
        message = f"Error downloading data from '{source_url}': {e!s}"
        logger.exception(message)
        console.print(f"[red]{message}[/red]")
        sys.exit(1)
