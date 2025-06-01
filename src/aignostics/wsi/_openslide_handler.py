"""Handler for wsi files using OpenSlide."""

import xml.etree.ElementTree as ET  # noqa: S405
from pathlib import Path
from typing import Any

import openslide
from openslide import ImageSlide, OpenSlide, open_slide
from PIL.Image import Image

TIFF_IMAGE_DESCRIPTION = "tiff.ImageDescription"


class OpenSlideHandler:
    """Handler for WSI files using OpenSlide."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.slide: OpenSlide | ImageSlide = open_slide(str(path))

    @classmethod
    def from_file(cls, path: str | Path) -> "OpenSlideHandler":
        """Create an OpenSlideHandler from a file path.

        Args:
            path (str | Path): The path to the WSI file.

        Returns:
            OpenSlideHandler: An instance of OpenSlideHandler initialized with the given path.

        Raises:
            OpenSlideError: If the file cannot be opened as a WSI.
        """
        return cls(str(path))

    def _detect_format(self) -> str | None:
        """Enhanced format detection.

        Returns:
            str: The detected format of the TIFF file.
        """
        props = dict(self.slide.properties)

        # Check for libvips signature in XML metadata
        if TIFF_IMAGE_DESCRIPTION in props:
            try:
                root = ET.fromstring(props[TIFF_IMAGE_DESCRIPTION])  # noqa: S314
                if root.get("xmlns") == "http://www.vips.ecs.soton.ac.uk//dzsave":
                    return "pyramidal-tiff (libvips)"
            except ET.ParseError:
                pass

        # Additional format checks could go here
        # For example, check for BigTIFF indicators
        # BigTIFF uses 64-bit offsets instead of 32-bit
        # This would require reading the TIFF header directly
        base_format = self.slide.detect_format(self.path)
        if base_format == "generic-tiff":
            if self.slide.level_count > 1:
                return "pyramidal-tiff"
            return "tiff"

        return base_format

    def get_thumbnail(self) -> Image:
        """Get thumbnail of the slide.

        Returns:
            Image: Thumbnail image of the slide.

        Raises:
            OpenSlideError: If the slide cannot be opened or if thumbnail generation fails.
        """
        return self.slide.get_thumbnail((256, 256))

    def _parse_xml_image_description(self, xml_string: str) -> dict[str, Any]:  # noqa: C901, PLR6301
        """Parse the XML image description.

        Args:
            xml_string: XML string containing image description.

        Returns:
            dict[str, Any]: Parsed image description as a dictionary with metadata properties.
        """
        try:
            root = ET.fromstring(xml_string)  # noqa: S314
            namespace = {"ns": "http://www.vips.ecs.soton.ac.uk//dzsave"}
            image_desc: dict[str, Any] = {
                "date": root.get("date"),
                "version": root.get("version"),
                "properties": {},
            }
            for prop in root.findall(".//ns:property", namespace):
                name_elem = prop.find("ns:name", namespace)
                if name_elem is None:
                    continue
                name = name_elem.text
                if name is None:
                    continue
                value_elem = prop.find("ns:value", namespace)
                if value_elem is None:
                    continue
                value = value_elem.text
                if value is None:
                    continue
                value_type = value_elem.get("type", "")

                if value_type == "gint":
                    value = int(value)  # type: ignore[assignment]
                elif value_type == "gdouble":
                    value = float(value)  # type: ignore[assignment]
                elif value_type == "VipsRefString":
                    # Handle special libvips string properties
                    if name == "aix-libVips-version":
                        image_desc["libvips_version"] = value
                    elif name == "aix-original-format":
                        image_desc["original_format"] = value

                image_desc["properties"][name] = value

            return image_desc
        except ET.ParseError:
            return {}

    def _get_level_info(self) -> list[dict[str, Any]]:
        """Get detailed information for each level.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing detailed information for each level
                of the pyramidal image.
        """
        levels = []
        props = dict(self.slide.properties)
        base_mpp_x = float(props.get(openslide.PROPERTY_NAME_MPP_X, 0))
        base_mpp_y = float(props.get(openslide.PROPERTY_NAME_MPP_Y, 0))

        for level in range(self.slide.level_count):
            width, height = self.slide.level_dimensions[level]
            downsample = self.slide.level_downsamples[level]

            tile_width = int(props.get(f"openslide.level[{level}].tile-width", 256))
            tile_height = int(props.get(f"openslide.level[{level}].tile-height", 256))

            # Calculate number of tiles
            tiles_x = (width + tile_width - 1) // tile_width
            tiles_y = (height + tile_height - 1) // tile_height

            level_info = {
                "index": level,
                "dimensions": {
                    "width": width,
                    "height": height,
                    "total_pixels": width * height,
                    "aspect_ratio": width / height if height else 0,
                },
                "downsample": downsample,
                "resolution": {
                    "mpp_x": base_mpp_x * downsample if base_mpp_x else 0,
                    "mpp_y": base_mpp_y * downsample if base_mpp_y else 0,
                },
                "tile": {
                    "width": tile_width,
                    "height": tile_height,
                    "grid": {"x": tiles_x, "y": tiles_y, "total": tiles_x * tiles_y},
                },
            }
            levels.append(level_info)

        return levels

    def get_metadata(self) -> dict[str, Any]:
        """Get comprehensive slide metadata.

        Returns:
            dict[str, Any]: A dictionary containing detailed metadata about the image,
                including format, file information, dimensions, resolution, levels, and other properties.
        """
        props = dict(self.slide.properties)
        file_size = self.path.stat().st_size
        base_width, base_height = self.slide.dimensions

        metadata = {
            "format": self._detect_format(),
            "file": {
                "path": str(self.path),
                "size": file_size,
                "size_human": f"{file_size / (1024 * 1024 * 1024):.2f} GB",
            },
            "dimensions": {"width": base_width, "height": base_height},
            "resolution": {
                "mpp_x": float(props.get(openslide.PROPERTY_NAME_MPP_X, 0)),
                "mpp_y": float(props.get(openslide.PROPERTY_NAME_MPP_Y, 0)),
                "unit": props.get("tiff.ResolutionUnit", "unknown"),
                "x_resolution": float(props.get("tiff.XResolution", 0)),
                "y_resolution": float(props.get("tiff.YResolution", 0)),
            },
            "bounds": {
                "x": int(props.get(openslide.PROPERTY_NAME_BOUNDS_X, 0)),
                "y": int(props.get(openslide.PROPERTY_NAME_BOUNDS_X, 0)),
                "width": int(props.get(openslide.PROPERTY_NAME_BOUNDS_X, base_width)),
                "height": int(props.get(openslide.PROPERTY_NAME_BOUNDS_X, base_height)),
            },
            "tile": {
                "width": int(props.get("openslide.level[0].tile-width", 256)),
                "height": int(props.get("openslide.level[0].tile-height", 256)),
            },
            "levels": {"count": self.slide.level_count, "data": self._get_level_info()},
            "properties": {},
        }

        # Parse image description if available
        if TIFF_IMAGE_DESCRIPTION in props:
            image_desc = self._parse_xml_image_description(props[TIFF_IMAGE_DESCRIPTION])
            if image_desc:
                # Initialize "properties.image" as a dict if needed
                if "properties" not in metadata:
                    metadata["properties"] = {}
                metadata["properties"]["image"] = image_desc  # type: ignore[index, assignment]
                if "libvips_version" in image_desc:
                    metadata["generator"] = f"libvips {image_desc['libvips_version']}"

        # Include vendor information
        if "openslide.vendor" in props:
            metadata["vendor"] = props["openslide.vendor"]

        # Add associated images if any
        associated_images = list(self.slide.associated_images.keys())
        if associated_images:
            metadata["associated_images"] = associated_images  # type: ignore[assignment]

        return metadata

    def close(self) -> None:
        """Close the OpenSlide object."""
        self.slide.close()

    def __enter__(self) -> "OpenSlideHandler":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the context manager.

        Args:
            exc_type: The exception type if an exception was raised.
            exc_val: The exception value if an exception was raised.
            exc_tb: The traceback if an exception was raised.
        """
        self.close()
