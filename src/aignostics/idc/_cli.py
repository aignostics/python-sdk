"""CLI of Image Data Commons Group (IDC) module."""

import webbrowser
from pathlib import Path
from typing import Annotated

import typer

from aignostics.utils import console, get_logger

logger = get_logger(__name__)

PATH_LENFTH_MAX = 260
TARGET_LAYOUT_DEFAULT = "%collection_id/%PatientID/%StudyInstanceUID/%Modality_%SeriesInstanceUID/"

cli = typer.Typer(
    name="idc",
    help="Download datasets from Image Data Commons (IDC) Portal of National Institute of Cancer (NIC).",
)


@cli.command()
def browse() -> None:
    """Open browser to explore IDC portal."""
    webbrowser.open("https://portal.imaging.datacommons.cancer.gov/explore/")


@cli.command()
def indices() -> None:
    """List available columns in given of the IDC Portal."""
    from idc_index.index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    console.print(list(client.indices_overview.keys()))


@cli.command()
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
    from idc_index.index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    client.fetch_index(index)
    console.print(list(getattr(client, index).columns))


@cli.command()
def query(
    query: Annotated[
        str,
        typer.Argument(
            help="SQL Query to execute."
            "See https://idc-index.readthedocs.io/en/latest/column_descriptions.html for indices and their attributes"
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
    from idc_index.index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    for idx in [idx.strip() for idx in indices.split(",") if idx.strip()]:
        logger.info("Fetching index: '%s'", idx)
        client.fetch_index(idx)

    pd.set_option("display.max_colwidth", None)
    console.print(client.sql_query(sql_query=query))  # type: ignore[no-untyped-call]


@cli.command()
def download(
    source: Annotated[
        str,
        typer.Argument(
            help="Identifier or comma-separated set of identifiers."
            " IDs matched against collection_id, PatientId, StudyInstanceUID, SeriesInstanceUID or SOPInstanceUID."
        ),
    ],
    target: Annotated[str, typer.Argument(help="target directory for download")] = str(Path.cwd()),
    target_layout: Annotated[
        str, typer.Option(help="layout of the target directory. See default for available elements for use")
    ] = TARGET_LAYOUT_DEFAULT,
    dry_run: Annotated[bool, typer.Option(help="dry run")] = False,
) -> None:
    """Download from manifest file, identifier, or comma-separate set of identifiers.

    Raises:
        typer.Exit: If the target directory does not exist.
    """
    from idc_index.index import IDCClient  # noqa: PLC0415

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
    sm_instance_index_df = client.sm_instance_index  # type: ignore[attr-defined]

    def check_and_download(column_name: str, item_ids: list[str], target_directory: Path, kwarg_name: str) -> bool:
        if column_name != "SOPInstanceUID":
            matches = index_df[column_name].isin(item_ids)
            matched_ids = index_df[column_name][matches].unique().tolist()
        else:
            matches = sm_instance_index_df[column_name].isin(item_ids)
            matched_ids = sm_instance_index_df[column_name][matches].unique().tolist()
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
