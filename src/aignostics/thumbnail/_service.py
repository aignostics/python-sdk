"""Service of the thumbnail module."""

import io
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image

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

    def get_thumbnail_image(self, path: Path) -> Image.Image:  # noqa: PLR6301
        """Get thumbnail of a image as PIL image.

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

    def get_tiff_as_jpg(self, url: str) -> bytes:  # noqa: PLR6301
        """Get a TIFF image from a URL and convert it to JPG format.

        Args:
            url (str): URL to the TIFF image.

        Returns:
            bytes: The TIFF image converted to JPG format as bytes.

        Raises:
            ValueError: If the URL does not point to a TIFF image or if the conversion fails.
            HTTPError: If the request to the URL fails.
        """
        # Validate URL
        if not url.startswith(("http:", "https:")):
            error_msg = "URL must start with 'http:' or 'https:'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Open the URL and read the content into a bytes object
            with urllib.request.urlopen(url) as response:
                tiff_data = response.read()

            # Create a BytesIO object from the image data
            tiff_buffer = io.BytesIO(tiff_data)

            # Open the image using PIL
            with Image.open(tiff_buffer) as img:
                # Convert to RGB if needed (in case it's a RGBA or other format)
                rgb_img = img.convert("RGB") if img.mode != "RGB" else img.copy()

                # Save the image as JPG to a BytesIO buffer
                jpg_buffer = io.BytesIO()
                rgb_img.save(jpg_buffer, format="JPEG", quality=90)

                # Get the bytes from the buffer
                return jpg_buffer.getvalue()

        except urllib.error.HTTPError as e:
            error_msg = f"HTTP error while fetching TIFF from URL: {e}"
            logger.exception(error_msg)
            raise
        except urllib.error.URLError as e:
            error_msg = f"URL error while fetching TIFF from URL: {e}"
            logger.exception(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Error converting TIFF to JPG: {e}"
            logger.exception(error_msg)
            raise ValueError(error_msg) from e
