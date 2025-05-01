"""CLI for operations on pyramidal TIFF files."""

from pathlib import Path
from typing import Annotated

import typer

from aignostics.utils import console, get_logger

from ._service import Service

logger = get_logger(__name__)


cli = typer.Typer(name="tiff", help="Operations on pyramidal TIFF files.")


@cli.command()
def inspect(
    path: Annotated[Path, typer.Argument(help="Path to the TIFF file", exists=True)],
) -> None:
    """Inspect a TIFF file and display its metadata."""
    metadata = Service().get_metadata(path)

    # Basics
    console.print("Format:", style="blue", end=" ")
    console.print(metadata["format"], style="green")
    console.print("Path:", style="blue", end=" ")
    console.print(metadata["file"]["path"], style="green")
    console.print("Size (human):", style="blue", end=" ")
    console.print(metadata["file"]["size_human"], style="green")
    console.print("Width:", style="blue", end=" ")
    console.print(metadata["dimensions"]["width"], style="green")
    console.print("Height:", style="blue", end=" ")
    console.print(metadata["dimensions"]["height"], style="green")
    console.print("MPP (x):", style="blue", end=" ")
    console.print(metadata["resolution"]["mpp_x"], style="green")
    console.print("MPP (y):", style="blue", end=" ")
    console.print(metadata["resolution"]["mpp_y"], style="green")

    # Image Properties
    if "properties" in metadata and "image" in metadata["properties"]:
        img = metadata["properties"]["image"]
        created = f"{img['date']} (libvips {img['version']})"
        console.print("Created:", style="blue", end=" ")
        console.print(created, style="green")

        if "properties" in img and "bands" in img["properties"]:
            console.print("Color channels:", style="blue", end=" ")
            console.print(str(img["properties"]["bands"]), style="green")

        if "properties" in img and "aix-original-format" in img["properties"]:
            console.print("aix-original-format:", style="blue", end=" ")
            console.print(str(img["properties"]["aix-original-format"]), style="green")

    # Level Structure
    console.print("\nLevel Structure:", style="bold blue")
    for level in metadata["levels"]["data"]:
        console.print(f"\nLevel {level['index']}", style="blue")

        dimensions = f"{level['dimensions']['width']} x {level['dimensions']['height']} pixels"
        console.print("  Dimensions:", style="blue", end=" ")
        console.print(dimensions, style="green")

        downsample = f"{level['downsample']:.1f}x"
        console.print("  Downsample factor:", style="blue", end=" ")
        console.print(downsample, style="green")

        pixel_size = f"{metadata['resolution']['mpp_x'] * level['downsample']:.3f} µm/pixel"
        console.print("  Pixel size:", style="blue", end=" ")
        console.print(pixel_size, style="green")

        tile_size = f"{level['tile']['width']} x {level['tile']['height']} pixels"
        console.print("  Tile size:", style="blue", end=" ")
        console.print(tile_size, style="green")

        tiles = f"{level['tile']['grid']['x']} x {level['tile']['grid']['y']} ({level['tile']['grid']['total']} total)"
        console.print("  Tiles:", style="blue", end=" ")
        console.print(tiles, style="green")

    # Associated Images
    if metadata.get("associated_images"):
        console.print("\nAssociated Images:", style="bold blue")
        for img in metadata["associated_images"]:
            console.print(f"  - {img}", style="green")
