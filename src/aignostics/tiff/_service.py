# src/orion/tiff/handler.py
from typing import Any

from fastapi import Path

from aignostics.utils import BaseService, Health


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the application module."""

    def health(self) -> Health:
        """Determine health of hello service.

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

    def get_metadata(self, path: Path) -> dict[str, Any]:
        """Get metadata from a TIFF file.

        Args:
            path (Path): Path to the TIFF file.

        Returns:
            dict[str, Any]: Metadata of the TIFF file.
        """
        from ._handler import TiffHandler

        handler = TiffHandler.from_file(path)
        return handler.get_metadata()
