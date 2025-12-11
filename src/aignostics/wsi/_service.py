"""Service of the wsi module."""

import io
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import requests
from loguru import logger

from aignostics import WSI_SUPPORTED_FILE_EXTENSIONS
from aignostics.utils import BaseService, Health

from ._openslide_handler import DEFAULT_MAX_SAFE_DIMENSION
from ._utils import select_dicom_files

TIMEOUT = 60  # 1 minutes


class Service(BaseService):
    """Service of the application module."""

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: ARG002, PLR6301
        """Determine info of this service.

        Args:
            mask_secrets (bool): Whether to mask sensitive information in the output.

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
    def get_thumbnail(path: Path, max_safe_dimension: int = DEFAULT_MAX_SAFE_DIMENSION) -> "PIL.Image.Image":  # type: ignore # noqa: F821
        """Get thumbnail as PIL image.

        Args:
            path (Path): Path to the image.
            max_safe_dimension (int): Maximum dimension (width or height) of smallest pyramid level
                before considering the pyramid incomplete.

        Returns:
            PIL.Image.Image: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported.
            RuntimeError: If there is an error generating the thumbnail.
        """
        from ._openslide_handler import OpenSlideHandler  # noqa: PLC0415

        if path.exists() is False:
            message = f"File does not exist: {path}"
            logger.warning(message)
            raise ValueError(message)
        if path.suffix.lower() not in WSI_SUPPORTED_FILE_EXTENSIONS:
            message = f"Unsupported file type: {path.suffix}. Supported types are {WSI_SUPPORTED_FILE_EXTENSIONS!s}"
            logger.warning(message)
            raise ValueError(message)
        try:
            return OpenSlideHandler.from_file(path).get_thumbnail(max_safe_dimension=max_safe_dimension)
        except Exception as e:
            message = f"Error processing file {path}: {e!s}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def get_thumbnail_bytes(path: Path, max_safe_dimension: int = DEFAULT_MAX_SAFE_DIMENSION) -> bytes:
        """Get thumbnail of a image as bytes.

        Args:
            path (Path): Path to the image.
            max_safe_dimension (int): Maximum dimension (width or height) of smallest pyramid level
                before considering the pyramid incomplete.

        Returns:
            bytes: Thumbnail of the image.

        Raises:
            ValueError: If the file type is not supported.
            RuntimeError: If there is an error processing the file.
        """
        thumbnail_image = Service.get_thumbnail(path, max_safe_dimension=max_safe_dimension)
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
        if path.suffix.lower() not in WSI_SUPPORTED_FILE_EXTENSIONS:
            message = f"Unsupported file type: {path.suffix}. Supported types are {WSI_SUPPORTED_FILE_EXTENSIONS}."
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

    @staticmethod
    def get_wsi_files_to_process(path: Path, extension: str) -> Iterable[Path]:
        """Get WSI files to process for the specified extension.

        For DICOM files (.dcm), applies filtering to only include WSI files and select
        only the highest resolution file from multi-file pyramids. For other formats,
        returns all files matching the extension.

        Args:
            path: Root directory to search for WSI files.
            extension: File extension to filter (e.g., ".dcm", ".tiff", ".svs").
                Must include the leading dot.

        Returns:
            Iterable of Path objects for files to process.
        """
        files_to_process: Iterable[Path]
        if extension == ".dcm":  # noqa: SIM108
            # Special handling for DICOM files - filter out auxiliary and redundant files
            files_to_process = select_dicom_files(path)
        else:
            # For non-DICOM formats, process all files with this extension
            files_to_process = path.glob(f"**/*{extension}")
        return files_to_process
