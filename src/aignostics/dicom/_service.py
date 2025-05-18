"""Service module for handling DICOM files."""

from pathlib import Path
from typing import Any

from openslide import OpenSlideError
from PIL import Image as PILImage
from PIL.Image import Image

from aignostics.utils import BaseService, Health


class Service(BaseService):
    """Service of the application module."""

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={},
        )

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def get_metadata(self, path: Path) -> dict[str, Any]:  # noqa: PLR6301
        """Get metadata from a DICOM dataset.

        Args:
            path (Path): Path to the DICOM dataset.

        Returns:
            dict[str, Any]: Metadata of the DICOM dataset.
        """
        from aignostics.tiff import Service as TiffService  # noqa: PLC0415

        # TODO(Helmut): Uncomment when DICOM is implemented
        #        handler = DicomHandler.from_file(path)  # noqa: ERA001
        #        return handler.get_metadata()  # noqa: ERA001
        return TiffService().get_metadata(path)

    def get_thumbnail(self, path: Path) -> Image:  # noqa: PLR6301
        """Get thumbnail of a DICOM image.

        Args:
            path (Path): Path to the DICOM image.

        Returns:
            Any: Thumbnail of the image.

        Raises:
            OpenSlideError: If there's an error opening the slide, except when "No pyramid levels found".
        """
        from aignostics.tiff import Service as TiffService  # noqa: PLC0415

        try:
            return TiffService().get_thumbnail(path)
        except OpenSlideError as e:
            if str(e) == "No pyramid levels found":
                # If regular OpenSlide fails, try using PIL directly
                img = PILImage.open(path)
                # Create a thumbnail with max size 256x256 while maintaining aspect ratio
                img.thumbnail((256, 256))
                # Convert to RGB mode if needed (for PNG compatibility)
                if img.mode not in {"RGB", "RGBA"}:
                    img = img.convert("RGB")
                # Return the thumbnail image
                return img
            raise
