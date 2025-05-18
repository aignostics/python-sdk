"""Service module for handling TIFF files."""

from pathlib import Path
from typing import Any

from openslide import OpenSlideError, OpenSlideUnsupportedFormatError
from PIL import Image as PILImage
from PIL.Image import Image

from aignostics.utils import BaseService, Health


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the TIFF module."""

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
        """Get metadata from a TIFF file.

        Args:
            path (Path): Path to the TIFF file.

        Returns:
            dict[str, Any]: Metadata of the TIFF file.
        """
        from ._handler import TiffHandler  # noqa: PLC0415

        handler = TiffHandler.from_file(path)
        return handler.get_metadata()

    def get_thumbnail(self, path: Path) -> Image:  # noqa: PLR6301
        """Get thumbnail of a TIFF file.

        Args:
            path (Path): Path to the TIFF file.

        Returns:
            Image: Thumbnail of the TIFF file.

        Raises:
            OpenSlideError: If there is an error processing the TIFF file with OpenSlide.
        """
        from ._handler import TiffHandler  # noqa: PLC0415

        try:
            handler = TiffHandler.from_file(path)
            return handler.get_thumbnail()
        except OpenSlideUnsupportedFormatError:
            # If OpenSlide fails, try using PIL directly
            img = PILImage.open(path)
            # Create a thumbnail with max size 256x256 while maintaining aspect ratio
            img.thumbnail((256, 256))
            # Convert to RGB mode if needed (for PNG compatibility)
            if img.mode not in {"RGB", "RGBA"}:
                img = img.convert("RGB")
            # Return the thumbnail image
            return img
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
