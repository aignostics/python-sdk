"""Service module for handling DICOM files."""

from pathlib import Path
from typing import Any

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
        """
        from aignostics.tiff import Service as TiffService  # noqa: PLC0415

        return TiffService().get_thumbnail(path)
