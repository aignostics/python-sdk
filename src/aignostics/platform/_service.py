"""Service of the platform module."""

from http import HTTPStatus
from typing import Any

import urllib3

from aignostics.platform import Client
from aignostics.utils import BaseService, Health, __version__, get_logger

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

    def _determine_api_public_health(self) -> Health:
        """Determine healthiness and reachability of Aignostics Platform API.

        - Checks if health endpoint is reachable and returns 200 OK
        - Uses urllib3 for a direct connection check without authentication

        Returns:
            Health: The healthiness of the Aignostics Platform API via basic unauthenticated request.
        """
        try:
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=10.0))
            response = http.request(
                method="GET",
                url=f"{self._settings.api_root}/api/v1/health",
                headers={"User-Agent": f"aignostics-python-sdk/{__version__}"},
            )

            if response.status != HTTPStatus.OK:
                logger.error("Aignostics Platform API (public) returned '%s'", response.status)
                return Health(
                    status=Health.Code.DOWN, reason=f"Aignostics Platform API returned status '{response.status}'"
                )
        except Exception as e:
            logger.exception("Issue with Aignostics Platform API")
            return Health(status=Health.Code.DOWN, reason=f"Issue with Aignostics Platform API: '{e}'")

        return Health(status=Health.Code.UP)

    def _determine_api_authenticated_health(self) -> Health:
        """Determine healthiness and reachability of Aignostics Platform API via authenticated API client.

        - Checks if health endpoint is reachable and returns 200 OK

        Returns:
            Health: The healthiness of the Aignostics Platform API when trying to reach via authenticated API client.
        """
        try:
            client = Client()
            api_client = client.get_api_client(cache_token=True).api_client
            response = api_client.call_api(
                url=self._settings.api_root + "/api/v1/health",
                method="GET",
            )
            if response.status != HTTPStatus.OK:
                logger.error("Aignostics Platform API (authenticated) returned '%s'", response.status)
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
                "api_public": self._determine_api_public_health(),
                "api_authenticated": self._determine_api_authenticated_health(),
            },
        )
