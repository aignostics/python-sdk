"""CLI for operations on pyramidal DICOM files."""

from pathlib import Path
from typing import Annotated

import typer

from aignostics.utils import console

from ._utils import print_slide_info, print_study_info

cli = typer.Typer(name="dicom", help="Operations on DICOM datasets.")


@cli.command()
def inspect(
    path: Annotated[
        Path,
        typer.Argument(..., help="Path of file or directory to inspect", exists=True),
    ],
    verbose: Annotated[bool, typer.Option(help="Verbose output")] = False,
    summary: Annotated[bool, typer.Option(help="Show only summary information")] = False,
) -> None:  # pylint: disable=W0613
    """Inspect DICOM files at any hierarchy level."""
    from ._handler import DicomHandler  # noqa: PLC0415

    with DicomHandler.from_file(str(path)) as handler:
        metadata = handler.get_metadata(verbose)

        if metadata["type"] == "empty":
            console.print("[bold red]No DICOM files found in the specified path.[/bold red]")
            return

        # Print hierarchy
        for study_uid, study_data in metadata["studies"].items():
            console.print(f"\n[bold]Study:[/bold] {study_uid}")
            print_study_info(study_data)

            if not summary:
                for container_id, slide_data in study_data["slides"].items():
                    console.print(f"\n[bold]Slide (Container ID):[/bold] {container_id}")
                    print_slide_info(slide_data, indent=1, verbose=verbose)


cli_geojson = typer.Typer(no_args_is_help=True)
cli.add_typer(cli_geojson, name="geojson")


@cli_geojson.callback()
def geojson() -> None:  # pylint: disable=W0613
    """Operations on GeoJSON files."""


@cli_geojson.command(name="import")
def dicom_geojson_import(
    dicom_path: Annotated[Path, typer.Argument(help="Path to the DICOM file", exists=True)],
    geojson_path: Annotated[Path, typer.Argument(help="Path to the GeoJSON file", exists=True)],
) -> None:  # pylint: disable=W0613
    """Import GeoJSON annotations into DICOM ANN instance."""
    from ._handler import DicomHandler  # noqa: PLC0415

    console.print("\nImporting GeoJSON annotations into DICOM ANN instance...", style="blue")
    DicomHandler.geojson_import(dicom_path, geojson_path)
