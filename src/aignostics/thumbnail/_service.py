"""Service of the thumbnail module."""

import io
from pathlib import Path
from typing import Any

from PIL.Image import Image

from aignostics.utils import BaseService, Health, get_logger

logger = get_logger(__name__)


class Service(BaseService):
    """Service of the application module."""

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of thumbnail service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
        )

    def get_thumbnail_image(self, path: Path) -> Image:  # noqa: PLR6301
        """Get thumbnail of a image as PIL image.

        Args:
            path (Path): Path to the image.

        Returns:
            Any: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported (.dcm, .tiff, or .tif).
        """
        from aignostics.dicom import Service as DICOMService  # noqa: PLC0415
        from aignostics.tiff import Service as TIFFService  # noqa: PLC0415

        if path.suffix.lower() == ".dcm":
            handler = DICOMService()
            return handler.get_thumbnail(path)
        if path.suffix.lower() == ".tiff" or path.suffix.lower() == ".tif":
            handler = TIFFService()
            return handler.get_thumbnail(path)
        message = f"Unsupported file type: {path.suffix}. Supported types are .dcm, .tiff, and .tif."
        logger.error(message)
        logger.error(message)
        raise ValueError(message)

    def get_thumbnail_bytes(self, path: Path) -> bytes:
        """Get thumbnail of a image as bytes.

        Args:
            path (Path): Path to the image.

        Returns:
            bytes: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported (.dcm, .tiff, or .tif).
        """
        thumbnail_image = self.get_thumbnail_image(path)
        buffer = io.BytesIO()
        thumbnail_image.save(buffer, format="PNG")
        return buffer.getvalue()
