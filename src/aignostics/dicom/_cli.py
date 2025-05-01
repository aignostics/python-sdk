"""
This module provides a command-line interface (CLI) for performing various operations on DICOM files using the Typer library.
It includes commands for inspecting, validating, and converting DICOM files, as well as importing GeoJSON annotations into DICOM ANN instances.
Additionally, it supports DICOMWeb operations such as searching, deleting, and storing studies, series, and instances.
The CLI is organized into multiple subcommands, each with specific options and arguments to customize the behavior of the operations.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from aignostics.utils import console, path_autocomplete
from ._utils import print_study_info, print_slide_info

cli = typer.Typer(name="dicom", help="Operations on DICOM datasets.")


@cli.command()
def inspect(
    path: Annotated[
        Path, typer.Argument(..., help="Path of file or directory to inspect", exists=True, autocompletion=path_autocomplete(file_okay=True, dir_okay=True, readable=True)),
    ],
    verbose: Annotated[
        bool, typer.Option(help="Verbose output")
    ] = False,
    summary: Annotated[
        bool, typer.Option(help="Show only summary information")
    ] = False,
):  # pylint: disable=W0613
    """Inspect DICOM files at any hierarchy level"""
    from ._handler import DicomHandler
    with DicomHandler.from_file(str(path)) as handler:
        metadata = handler.get_metadata(verbose)

        if metadata["type"] == "empty":
            console.print(
                "[bold red]No DICOM files found in the specified path.[/bold red]"
            )
            return

        # Print hierarchy
        for study_uid, study_data in metadata["studies"].items():
            console.print(f"\n[bold]Study:[/bold] {study_uid}")
            print_study_info(study_data)

            if not summary:
                for container_id, slide_data in study_data["slides"].items():
                    console.print(
                        f"\n[bold]Slide (Container ID):[/bold] {container_id}"
                    )
                    print_slide_info(slide_data, indent=1, verbose=verbose)


@cli.command(name="validate")
def dicom_validate(
    ctx: typer.Context,
    verbose: bool = False,
    dicom_path: Path = typer.Argument(..., exists=True),
    standard_path: Path = typer.Option(
        Path.home() / "dicom-validator",
        "--standard-path",
        "-src",
        help="Base path with the DICOM specs in docbook and json format",
    ),
    revision: str = typer.Option(
        "current",
        "--revision",
        "-r",
        help='Standard revision (e.g. "2014c"), year of revision, "current" or "local" (latest locally installed)',
    ),
    force_read: bool = typer.Option(
        False, "--force-read", help="Force-read DICOM files without DICOM header"
    ),
    recreate_json: bool = typer.Option(
        False,
        "--recreate-json",
        help="Force recreating the JSON information from the DICOM specs",
    ),
    suppress_vr_warnings: bool = typer.Option(
        False,
        "--suppress-vr-warnings",
        "-svr",
        help="Suppress warnings for values not matching value representation (VR)",
    ),
):  # pylint: disable=W0613
    """Validate DICOM files."""
    from ._handler import DicomHandler
    error_nr = DicomHandler.validate(
        dicom_path=dicom_path,
        standard_path=standard_path,
        revision=revision,
        force_read=force_read,
        suppress_vr_warnings=suppress_vr_warnings,
        recreate_json=recreate_json,
        verbose=verbose,
    )
    if error_nr > 0:
        typer.Exit(1)


cli_geojson = typer.Typer(no_args_is_help=True)
cli.add_typer(cli_geojson, name="geojson")


@cli_geojson.callback()
def geojson(ctx: typer.Context, verbose: bool = False):  # pylint: disable=W0613
    """Operations on GeoJSON files"""


@cli_geojson.command(name="import")
def dicom_geojson_import(
    ctx: typer.Context,
    verbose: bool = False,
    dicom_path: Path = typer.Argument(..., exists=True),
    geojson_path: Path = typer.Argument(..., exists=True),
):  # pylint: disable=W0613
    """Import GeoJSON annotations into DICOM ANN instance"""
    from ._handler import DicomHandler
    console.print(
        "\nImporting GeoJSON annotations into DICOM ANN instance...", style="blue"
    )
    DicomHandler.geojson_import(dicom_path, geojson_path)


cli_wsi = typer.Typer(no_args_is_help=True)
cli.add_typer(cli_wsi, name="wsi")


@cli_wsi.callback()
def wsi(ctx: typer.Context, verbose: bool = False):  # pylint: disable=W0613
    """Operations on WSI files"""


@cli_wsi.command(name="convert")
def dicom_wsi_convert(
    ctx: typer.Context,
    verbose: bool = False,
    wsi_path: Path = typer.Argument(..., exists=True),
    dicom_path: Path = typer.Argument(..., exists=True),
    id_base: int = typer.Option(1, "--id-base", "-i", help="Base for ID generation"),
):  # pylint: disable=W0613
    """Convert a WSI to DICOM SM instances"""
    from ._handler import DicomHandler
    console.print("\nConverting WSI to DICOM SM instances...", style="blue")
    DicomHandler.wsi_convert(wsi_path, dicom_path, id_base)

