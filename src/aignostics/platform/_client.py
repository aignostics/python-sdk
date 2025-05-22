import os
from urllib.request import getproxies

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import Configuration
from aignx.codegen.exceptions import NotFoundException
from aignx.codegen.models import ApplicationReadResponse as Application

from aignostics.platform._authentication import get_token
from aignostics.platform.resources.applications import Applications, Versions
from aignostics.platform.resources.runs import ApplicationRun, Runs
from aignostics.utils import get_logger

from ._settings import settings

logger = get_logger(__name__)


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
        config = Configuration(
            host=settings().api_root,
            ssl_ca_cert=os.getenv("REQUESTS_CA_BUNDLE"),  # point to .cer file of proxy if defined
        )
        config.proxy = getproxies().get("https")  # use system proxy
        client = ApiClient(
            config,
            header_name="Authorization",
            header_value=f"Bearer {token}",
        )
        return PublicApi(client)
