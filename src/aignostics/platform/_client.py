import os
from collections.abc import Callable
from urllib.request import getproxies

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import AuthSettings, Configuration
from aignx.codegen.exceptions import NotFoundException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import MeReadResponse as Me

from aignostics.platform._authentication import get_token
from aignostics.platform.resources.applications import Applications, Versions
from aignostics.platform.resources.runs import ApplicationRun, Runs
from aignostics.utils import get_logger, user_agent

from ._settings import settings

logger = get_logger(__name__)


class _OAuth2TokenProviderConfiguration(Configuration):
    """
    Overwrites the original Configuration to call a function to obtain a refresh token.

    The base class does not support callbacks. This is necessary for integrations where
    tokens may expire or need to be refreshed automatically.
    """

    def __init__(
        self, host: str, ssl_ca_cert: str | None = None, token_provider: Callable[[], str] | None = None
    ) -> None:
        super().__init__(host=host, ssl_ca_cert=ssl_ca_cert)
        self.token_provider = token_provider

    def auth_settings(self) -> AuthSettings:
        token = self.token_provider() if self.token_provider else None
        if not token:
            return {}
        return {
            "OAuth2AuthorizationCodeBearer": {
                "type": "oauth2",
                "in": "header",
                "key": "Authorization",
                "value": f"Bearer {token}",
            }
        }


class Client:
    """Main client for interacting with the Aignostics Platform API.

    Provides access to platform resources like applications, versions, and runs.
    Handles authentication and API client configuration.
    """

    applications: Applications
    runs: Runs
    versions: Versions

    def __init__(self, cache_token: bool = True) -> None:
        """Initializes a client instance with authenticated API access.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Sets up resource accessors for applications, versions, and runs.
        """
        try:
            logger.debug("Initializing client with cache_token=%s", cache_token)
            self._api = Client.get_api_client(cache_token=cache_token)
            self.applications: Applications = Applications(self._api)
            self.runs: Runs = Runs(self._api)
            logger.debug("Client initialized successfully.")
        except Exception:
            logger.exception("Failed to initialize client.")
            raise

    def me(self) -> Me:
        """Retrieves info about the current user and their organisation.

        Returns:
            Me: User and organization information.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """
        return self._api.get_me_v1_me_get()

    def run(self, application_run_id: str) -> ApplicationRun:
        """Finds a specific run by id.

        Args:
            application_run_id (str): The ID of the application run.

        Returns:
            Run: The run object.
        """
        return ApplicationRun(self._api, application_run_id)

    # TODO(Andreas): Provide a /v1/applications/{application_id} endpoint and use that
    def application(self, application_id: str) -> Application:
        """Finds a specific application by id.

        Args:
            application_id (str): The ID of the application.

        Raises:
            NotFoundException: If the application with the given ID is not found.

        Returns:
            Application: The application object.
        """
        applications = self.applications.list()
        for application in applications:
            if application.application_id == application_id:
                return application
        logger.warning("Application with ID '%s' not found.", application_id)
        raise NotFoundException

    @staticmethod
    def get_api_client(cache_token: bool = True) -> PublicApi:
        """Create and configure an authenticated API client.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Returns:
            PublicApi: Configured API client with authentication token.

        Raises:
            RuntimeError: If authentication fails.
        """

        def token_provider() -> str:
            return get_token(use_cache=cache_token)

        ca_file = os.getenv("REQUESTS_CA_BUNDLE")  # point to .cer file of proxy if defined
        config = _OAuth2TokenProviderConfiguration(
            host=settings().api_root, ssl_ca_cert=ca_file, token_provider=token_provider
        )
        config.proxy = getproxies().get("https")  # use system proxy
        client = ApiClient(
            config,
        )
        client.user_agent = user_agent()
        return PublicApi(client)
