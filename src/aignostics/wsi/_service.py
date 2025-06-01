"""Service of the wsi module."""

import io
from pathlib import Path
from typing import Any

import requests

from aignostics.utils import BaseService, Health, get_logger

logger = get_logger(__name__)

TIMEOUT = 60  # 1 minutes

FILE_TYPES_SUPPORTED = {".dcm", ".tiff", ".tif", ".svs"}


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

    @staticmethod
    def get_thumbnail(path: Path) -> "PIL.Image.Image":  # type: ignore # noqa: F821
        """Get thumbnail as PIL image.

        Args:
            path (Path): Path to the image.

        Returns:
            PIL.Image.Image: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported (.dcm, .tiff, or .tif).
            RuntimeError: If there is an error generating the thumbnail.
        """
        from ._openslide_handler import OpenSlideHandler  # noqa: PLC0415

        if path.exists() is False:
            message = f"File does not exist: {path}"
            logger.warning(message)
            raise ValueError(message)
        if path.suffix.lower() not in FILE_TYPES_SUPPORTED:
            message = f"Unsupported file type: {path.suffix}. Supported types are .dcm, .tiff, and .tif."
            logger.warning(message)
            raise ValueError(message)
        try:
            return OpenSlideHandler.from_file(path).get_thumbnail()
        except Exception as e:
            message = f"Error processing file {path}: {e!s}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def get_thumbnail_bytes(path: Path) -> bytes:
        """Get thumbnail of a image as bytes.

        Args:
            path (Path): Path to the image.

        Returns:
            bytes: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported.
            RuntimeError: If there is an error processing the file.
        """
        thumbnail_image = Service.get_thumbnail(path)
        buffer = io.BytesIO()
        thumbnail_image.save(buffer, format="PNG")
        return buffer.getvalue()

    @staticmethod
    def get_metadata(path: Path) -> dict[str, Any]:
        """Get metadata from a TIFF file.

        Args:
            path (Path): Path to the TIFF file.

        Returns:
            dict[str, Any]: Metadata of the TIFF file.

        Raises:
            ValueError: If the file type is not supported.
            RuntimeError: If there is an error processing the file.
        """
        from ._openslide_handler import OpenSlideHandler  # noqa: PLC0415

        if path.exists() is False:
            message = f"File does not exist: {path}"
            logger.warning(message)
            raise ValueError(message)
        if path.suffix.lower() not in FILE_TYPES_SUPPORTED:
            message = f"Unsupported file type: {path.suffix}. Supported types are .dcm, .tiff, and .tif."
            logger.warning(message)
            raise ValueError(message)
        try:
            return OpenSlideHandler.from_file(path).get_metadata()
        except Exception as e:
            error_msg = f"Error processing file {path}: {e!s}"
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e

    @staticmethod
    def get_tiff_as_jpg(url: str) -> bytes:
        """Get a TIFF image from a URL and convert it to JPG format.

        Args:
            url (str): URL to the TIFF image.

        Returns:
            bytes: The TIFF image converted to JPG format as bytes.

        Raises:
            ValueError: If URL format is invalid or if there's an error opening the tiff.
            RuntimeError: If there's an unexpected internal error.
        """
        from PIL import Image as PILImage  # noqa: PLC0415
        from PIL import UnidentifiedImageError  # noqa: PLC0415

        if not url.startswith(("http://localhost", "https://")):
            error_msg = "URL must start with 'http://localhost' or 'https://'."
            logger.warning(error_msg)
            raise ValueError(error_msg)
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            tiff_data = response.content
            tiff_buffer = io.BytesIO(tiff_data)
            with PILImage.open(tiff_buffer) as img:
                rgb_img = img.convert("RGB") if img.mode != "RGB" else img
                jpg_buffer = io.BytesIO()
                rgb_img.save(jpg_buffer, format="JPEG", quality=90)
                return jpg_buffer.getvalue()
        except requests.HTTPError as e:
            error_msg = f"HTTP error while fetching TIFF from URL: {e!s}."
            logger.warning(error_msg)
            raise ValueError(error_msg) from e
        except requests.exceptions.InvalidURL as e:
            error_msg = f"URL error prevented fetching TIFF: {e!s}."
            logger.warning(error_msg)
            raise ValueError(error_msg) from e
        except requests.URLRequired as e:
            error_msg = f"URL error prevented fetching TIFF: {e!s}."
            logger.warning(error_msg)
            raise ValueError(error_msg) from e
        except UnidentifiedImageError as e:
            error_msg = f"Unidentified image error while trying to process as TIFF: {e!s}."
            logger.warning(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error converting TIFF to JPEG: {e!s}."
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e
