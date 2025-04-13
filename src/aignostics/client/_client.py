from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import Configuration

from aignostics.client._authentication import get_token
from aignostics.client.resources.applications import Applications
from aignostics.client.resources.runs import Runs

from ._constants import API_ROOT_DEV, API_ROOT_PRODUCTION, API_ROOT_STAGING
from ._settings import settings


class Client:
    """Main client for interacting with the Aignostics Platform API.

    Provides access to platform resources like applications, versions, and runs.
    Handles authentication and API client configuration.
    """

    def __init__(self, cache_token: bool = True) -> None:
        """Initializes a client instance with authenticated API access.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Sets up resource accessors for applications, versions, and runs.
        """
        self._api = Client.get_api_client(cache_token=cache_token)
        self.applications: Applications = Applications(self._api)
        self.runs: Runs = Runs(self._api)

    @staticmethod
    def get_api_client(cache_token: bool = True) -> PublicApi:
        """Creates and configures an authenticated API client.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Returns:
            ExternalsApi: Configured API client with authentication token.

        Raises:
            RuntimeError: If authentication fails.
        """
        token = get_token(use_cache=cache_token)
        client = ApiClient(
            Configuration(
                host=settings().api_root,
            ),
            header_name="Authorization",
            header_value=f"Bearer {token}",
        )
        return PublicApi(client)

    @staticmethod
    def get_info() -> dict[str, dict]:  # type: ignore[type-arg]
        """Retrieves process information.

        Returns:
            dict[str, dict]: Process information including platform API roots.
        """
        return {
            "platform": {
                "production": {
                    "API_ROOT": API_ROOT_PRODUCTION,
                },
                "staging": {
                    "API_ROOT": API_ROOT_STAGING,
                },
                "dev": {
                    "API_ROOT": API_ROOT_DEV,
                },
            }
        }
