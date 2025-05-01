# src/orion/tiff/handler.py
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import openslide


class TiffHandler:
    """Handler for TIFF files using OpenSlide."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.slide = openslide.OpenSlide(str(path))

    @classmethod
    def from_file(cls, path: str) -> "TiffHandler":
        return cls(path)

    def _detect_format(self) -> str:
        """Enhanced format detection"""
        props = dict(self.slide.properties)
        # print(props)

        # Check for libvips signature in XML metadata
        if "tiff.ImageDescription" in props:
            try:
                root = ET.fromstring(props["tiff.ImageDescription"])
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

    def _parse_xml_image_description(self, xml_string: str) -> dict[str, Any]:
        """Parse the XML image description."""
        try:
            root = ET.fromstring(xml_string)
            namespace = {"ns": "http://www.vips.ecs.soton.ac.uk//dzsave"}
            image_desc = {
                "date": root.get("date"),
                "version": root.get("version"),
                "properties": {},
            }
            for prop in root.findall(".//ns:property", namespace):
                name = prop.find("ns:name", namespace).text
                value_elem = prop.find("ns:value", namespace)
                value = value_elem.text
                value_type = value_elem.get("type", "")

                if value_type == "gint":
                    value = int(value)
                elif value_type == "gdouble":
                    value = float(value)
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
        """Get detailed information for each level"""
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
        """Get comprehensive slide metadata"""
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
        if "tiff.ImageDescription" in props:
            image_desc = self._parse_xml_image_description(props["tiff.ImageDescription"])
            if image_desc:
                metadata["properties"]["image"] = image_desc
                if "libvips_version" in image_desc:
                    metadata["generator"] = f"libvips {image_desc['libvips_version']}"

        # Include vendor information
        if "openslide.vendor" in props:
            metadata["vendor"] = props["openslide.vendor"]

        # Add associated images if any
        associated_images = list(self.slide.associated_images.keys())
        if associated_images:
            metadata["associated_images"] = associated_images

        return metadata

    def close(self):
        """Close the OpenSlide object"""
        self.slide.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
