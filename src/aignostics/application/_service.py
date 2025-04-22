"""Service of the application module."""

from pathlib import Path
from typing import Any

from aignostics.utils import BaseService, Health

from ._settings import Settings


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the application module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def _determine_data_storage_health(self) -> Health:
        """Determine healthiness of data storage.

        - Checks if configured data directory is a directory

        Returns:
            Health: The healthiness of data storage.
        """
        data_directory = Path(self._settings.data_directory)
        if data_directory.is_dir():
            return Health(status=Health.Code.UP)
        return Health(status=Health.Code.DOWN, reason=f"Data directory {data_directory} is not accessible")

    def health(self) -> Health:
        """Determine health of hello service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={
                "data_storage": self._determine_data_storage_health(),
            },
        )

    def get_data_directory(self) -> Path:
        """Get the data directory.

        Returns:
            Path: The data directory.
        """
        return Path(self._settings.data_directory)
