from aignostics.client._authentication import get_token
from aignostics.client.resources.applications import Applications, Versions
from aignostics.client.resources.runs import Runs
from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import Configuration

API_ROOT = "https://platform-dev.aignostics.com"
# API_ROOT = "https://platform-staging.aignostics.ai"


class Client:
    """Main client for interacting with the Aignostics Platform API.

    Provides access to platform resources like applications, versions, and runs.
    Handles authentication and API client configuration.
    """
    def __init__(self, cache_token: bool = True):
        """Initializes a client instance with authenticated API access.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Sets up resource accessors for applications, versions, and runs.
        """
        self._api = Client._get_api_client(cache_token=cache_token)
        self.applications: Applications = Applications(self._api)
        self.versions: Versions = Versions(self._api)
        self.runs: Runs = Runs(self._api)

    @staticmethod
    def _get_api_client(cache_token: bool = True) -> ExternalsApi:
        """Creates and configures an authenticated API client.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Returns:
            ExternalsApi: Configured API client with authentication token.

        Raises:
            RuntimeError: If authentication fails.
        """
        token = get_token(store=cache_token)
        client = ApiClient(
            Configuration(
                host=API_ROOT,
                # debug=True,
                # the following can be used if the auth is set in the schema
                # api_key={"Authorization": T},
                # api_key_prefix={"Authorization": "Bearer"},
            ),
            header_name="Authorization",
            header_value=f"Bearer {token}"
        )
        return ExternalsApi(client)
