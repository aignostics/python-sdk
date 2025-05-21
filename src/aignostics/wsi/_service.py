"""Service of the wsi module."""

import io
from pathlib import Path
from typing import Any

import requests
from openslide import OpenSlideError, OpenSlideUnsupportedFormatError
from PIL import Image as PILImage
from PIL import UnidentifiedImageError
from PIL.Image import Image

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

    def _get_openslide_metadata(self, path: Path) -> dict[str, Any]:  # noqa: PLR6301
        """Get metadata of a wsi file via OpenSlide.

        Args:
            path (Path): Path to the wsi file.

        Returns:
            dict[str, Any]: Metadata of the wsi file.
        """
        from ._openslide_handler import OpenSlideHandler  # noqa: PLC0415

        handler = OpenSlideHandler.from_file(path)
        return handler.get_metadata()

    def _get_openslide_thumbnail(self, path: Path) -> Image:  # noqa: PLR6301
        """Get thumbnail of a wsi file via OpenSlide.

        Args:
            path (Path): Path to the wsi file.

        Returns:
            Image: Thumbnail of the wsi file.

        Raises:
            OpenSlideError: If there is an error processing the wsi file with OpenSlide.
        """
        from ._openslide_handler import OpenSlideHandler  # noqa: PLC0415

        try:
            handler = OpenSlideHandler.from_file(path)
            return handler.get_thumbnail()
        except OpenSlideUnsupportedFormatError:
            # If OpenSlide fails, try using PIL directly
            img_file = PILImage.open(path)
            # Create a thumbnail with max size 256x256 while maintaining aspect ratio
            img_file.thumbnail((256, 256))
            # Convert to RGB mode if needed (for PNG compatibility)
            return img_file.convert("RGB") if img_file.mode not in {"RGB", "RGBA"} else img_file.copy()
        except OpenSlideError as e:
            if str(e) == "No pyramid levels found":
                # If regular OpenSlide fails, try using PIL directly
                img_file = PILImage.open(path)
                # Create a thumbnail with max size 256x256 while maintaining aspect ratio
                img_file.thumbnail((256, 256))
                # Convert to RGB mode if needed (for PNG compatibility)
                return img_file.convert("RGB") if img_file.mode not in {"RGB", "RGBA"} else img_file.copy()
            raise

    def get_thumbnail(self, path: Path) -> Image:
        """Get thumbnail as PIL image.

        Args:
            path (Path): Path to the image.

        Returns:
            Image.Image: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported (.dcm, .tiff, or .tif).
        """
        if path.exists() is False:
            message = f"File does not exist: {path}"
            logger.warning(message)
            raise ValueError(message)
        if path.suffix.lower() in {".dcm", ".tiff", ".tif"}:
            return self._get_openslide_thumbnail(path)
        message = f"Unsupported file type: {path.suffix}. Supported types are .dcm, .tiff, and .tif."
        logger.warning(message)
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

    def get_metadata(self, path: Path) -> dict[str, Any]:
        """Get metadata from a TIFF file.

        Args:
            path (Path): Path to the TIFF file.

        Returns:
            dict[str, Any]: Metadata of the TIFF file.
        """
        return self._get_openslide_metadata(path)

    def get_tiff_as_jpg(self, url: str) -> bytes:  # noqa: PLR6301
        """Get a TIFF image from a URL and convert it to JPG format.

        Args:
            url (str): URL to the TIFF image.

        Returns:
            bytes: The TIFF image converted to JPG format as bytes.

        Raises:
            ValueError: If URL format is invalid or if there's an error opening the tiff.
            RuntimeError: If there's an unexpected internal error.
        """
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
