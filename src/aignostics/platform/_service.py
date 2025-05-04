"""Service of the platform module."""

from typing import Any

from aignostics.platform import Client
from aignostics.utils import BaseService, Health, get_logger

from ._settings import Settings

logger = get_logger(__name__)


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

    def _determine_api_health(self) -> Health:
        """Determine healthiness and reachability of Aignostics Platform API.

        - Checks if health endpoint is reachable and returns 200 OK

        Returns:
            Health: The healthiness of the Aignostics Platform API.
        """
        try:
            client = Client()
            api_client = client.get_api_client(cache_token=False).api_client
            response = api_client.call_api(
                url=self._settings.api_root + "/api/v1/health",
                method="GET",
            )
            if response.status != 200:
                return Health(status=Health.Code.DOWN, reason=f"Aignostics Platform API returned '{response.status}'")
        except Exception as e:
            logger.exception("Issue with Aignostics Platform API")
            return Health(status=Health.Code.DOWN, reason=f"Issue with Aignostics Platform API: '{e}'")
        return Health(status=Health.Code.UP)

    def health(self) -> Health:
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
            components={
                "api": self._determine_api_health(),
            },
        )
