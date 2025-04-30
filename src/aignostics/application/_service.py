"""Service of the application module."""

from collections.abc import Iterator
from math import log
from pathlib import Path
from typing import Any

from aignostics.platform import Application, ApplicationRun, Client
from aignostics.utils import BaseService, Health, get_logger

from ._settings import Settings
from ._utils import find_latest_application_version as util_find_latest_application_version

log = get_logger(__name__)


# Services derived from BaseService and exported by modules via their __init__.py are automatically registered
# with the system module, enabling for dynamic discovery of health, info and further functionality.
class Service(BaseService):
    """Service of the application module."""

    _settings: Settings

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    @staticmethod
    def _get_platform_client() -> Client:
        """Get the platform client.

        Returns:
            Client: The platform client.

        Raises:
            Exception: If the client cannot be created.
        """
        try:
            log.debug("Creating authenticated client.")
            client = Client()
            log.debug("Authenticated client created.")
            return client
        except Exception:
            log.exception("Failed to create authenticated client.")
            raise

    def info(self) -> dict[str, Any]:  # noqa: PLR6301
        """Determine info of this service.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def applications(self) -> Iterator[Application]:
        """Get a list of all applications.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return platform_client.applications.list()
        except Exception:
            log.exception("Failed to list applications.")
            raise

    def application(self, application_id: str) -> Application | None:
        """Get a specific application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application | None: The application or None if not found.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            applications = platform_client.applications.list()
            for application in applications:
                if application.application_id == application_id:
                    return application
            return None
        except Exception:
            log.exception("Failed to get application.")
            raise

    def find_latest_application_version(self, application: Application) -> str | None:
        """Find the latest version of the given application.

        Args:
            application (Application): The application to check for the latest version.

        Returns:
            list[str]: A list of all application runs.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the latest version cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return util_find_latest_application_version(application, platform_client)
        except Exception:
            log.exception("Failed to retrieve latest application for application id '%s'.", application.application_id)
            raise

    def application_runs(self) -> Iterator[ApplicationRun]:
        """Get a list of all application runs.

        Returns:
            list[str]: A list of all application runs.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application run list cannot be retrieved.
        """
        platform_client = self._get_platform_client()
        try:
            return platform_client.runs.list()
        except Exception:
            log.exception("Failed to list application runs.")
            raise

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
