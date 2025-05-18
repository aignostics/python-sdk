"""Service of the wsi module."""

import io
from pathlib import Path
from typing import Any

import requests
from PIL import Image

from aignostics.utils import BaseService, Health, get_logger

logger = get_logger(__name__)

TIMEOUT = 60  # 1 minutes


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

    def get_thumbnail(self, path: Path) -> Image.Image:  # noqa: PLR6301
        """Get thumbnail as PIL image.

        Args:
            path (Path): Path to the image.

        Returns:
            Image.Image: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported (.dcm, .tiff, or .tif).
        """
        from aignostics.dicom import Service as DICOMService  # noqa: PLC0415
        from aignostics.tiff import Service as TIFFService  # noqa: PLC0415

        if path.suffix.lower() == ".dcm":
            return DICOMService().get_thumbnail(path)
        if path.suffix.lower() in {".tiff", ".tif"}:
            return TIFFService().get_thumbnail(path)
        message = f"Unsupported file type: {path.suffix}. Supported types are .dcm, .tiff, and .tif."
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
        thumbnail_image = self.get_thumbnail(path)
        buffer = io.BytesIO()
        thumbnail_image.save(buffer, format="PNG")
        return buffer.getvalue()

    def get_tiff_as_jpg(self, url: str) -> bytes:  # noqa: PLR6301
        """Get a TIFF image from a URL and convert it to JPG format.

        Args:
            url (str): URL to the TIFF image.

        Returns:
            bytes: The TIFF image converted to JPG format as bytes.

        Raises:
            ValueError: If URL format is invalid or if there's an error converting TIFF to JPG.
            requests.HTTPError: If there's an HTTP error while fetching the TIFF from the URL.
            requests.URLRequired: If there's a URL error while fetching the TIFF from the URL.
        """
        if not url.startswith(("http:", "https:")):
            error_msg = "URL must start with 'http:' or 'https:'"
            logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            tiff_data = response.content
            tiff_buffer = io.BytesIO(tiff_data)
            with Image.open(tiff_buffer) as img:
                rgb_img = img.convert("RGB") if img.mode != "RGB" else img
                jpg_buffer = io.BytesIO()
                rgb_img.save(jpg_buffer, format="JPEG", quality=90)
                return jpg_buffer.getvalue()
        except requests.HTTPError:
            error_msg = "HTTP error while fetching TIFF from URL"
            logger.exception(error_msg)
            raise
        except requests.URLRequired:
            error_msg = "URL error while fetching TIFF from URL"
            logger.exception(error_msg)
            raise
        except Exception as e:
            error_msg = "Error converting TIFF to JPG"
            logger.exception(error_msg)
            raise ValueError(error_msg) from e
