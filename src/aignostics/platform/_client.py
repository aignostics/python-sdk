import logging
import os
from collections.abc import Callable
from typing import ClassVar
from urllib.request import getproxies

import semver
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import AuthSettings, Configuration
from aignx.codegen.exceptions import NotFoundException, ServiceException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import MeReadResponse as Me
from aignx.codegen.models import VersionReadResponse as ApplicationVersion
from tenacity import (
    Retrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from urllib3.exceptions import IncompleteRead, PoolError, ProtocolError, ProxyError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

from aignostics.platform._authentication import get_token
from aignostics.platform._operation_cache import cached_operation
from aignostics.platform.resources.applications import Applications, Versions
from aignostics.platform.resources.runs import Run, Runs
from aignostics.utils import get_logger, user_agent

from ._settings import settings

logger = get_logger(__name__)

RETRYABLE_EXCEPTIONS = (
    ServiceException,
    Urllib3TimeoutError,
    PoolError,
    IncompleteRead,
    ProtocolError,
    ProxyError,
)


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

    - Provides access to platform resources like applications, versions, and runs.
    - Handles authentication and API client configuration.
    - Retries on network and server errors for specific operations.
    - Caches operation results for specific operations.
    """

    _api_client_cached: ClassVar[PublicApi | None] = None
    _api_client_uncached: ClassVar[PublicApi | None] = None

    applications: Applications
    versions: Versions
    runs: Runs

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
            self.versions: Versions = Versions(self._api)
            logger.debug("Client initialized successfully.")
        except Exception:
            logger.exception("Failed to initialize client.")
            raise

    def me(self) -> Me:
        """Retrieves info about the current user and their organisation.

        Retries on network and server errors.

        Note:
        - We are not using urllib3s retry class as it does not support fine grained definition when to retry,
            exponential backoff with jitter, logging before retry, and is difficult to configure.

        Returns:
            Me: User and organization information.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """

        @cached_operation(ttl=settings().me_cache_ttl, use_token=True)
        def me_with_retry() -> Me:
            return Retrying(  # We are not using Tenacity annotations as settings can change at runtime
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().me_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().me_retry_wait_min, max=settings().me_retry_wait_max),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.get_me_v1_me_get(
                    _request_timeout=settings().me_timeout, _headers={"User-Agent": user_agent()}
                )
            )  # Retryer will pass down arguments

        return me_with_retry()

    def application(self, application_id: str) -> Application:
        """Find application by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            aignx.codegen.exceptions.ApiException: If the API call fails.

        Returns:
            Application: The application object.
        """

        @cached_operation(ttl=settings().application_cache_ttl, use_token=True)
        def application_with_retry(application_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=application_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return application_with_retry(application_id)

    def application_version(self, application_id: str, version_number: str | None = None) -> ApplicationVersion:
        """Find application version by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            version_number (str | None): The version number of the application.
                If None, the latest version will be retrieved.

        Raises:
            NotFoundException: If the application with the given ID and version number is not found.
            ValueError: If the version is not valid semver.
            aignx.codegen.exceptions.ApiException: If the API call fails.

        Returns:
            ApplicationVersion: The application version object.
        """
        # Handle version resolution and validation first (not retried)
        if version_number is None:
            # Get the latest version - this call already has its own retry logic in Versions
            version_tuple = Versions(self._api).latest(application=application_id)
            if version_tuple is None:
                message = f"No versions found for application '{application_id}'."
                raise NotFoundException(message)
            version_number = version_tuple.number

        # Validate semver format
        if version_number and not semver.Version.is_valid(version_number):
            message = f"Invalid version format: '{version_number}' not compliant with semantic versioning."
            raise ValueError(message)

        # Make the API call with retry logic and caching
        @cached_operation(ttl=settings().application_version_cache_ttl, use_token=True)
        def application_version_with_retry(application_id: str, version: str) -> ApplicationVersion:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )(
                lambda: self._api.application_version_details_v1_applications_application_id_versions_version_get(
                    application_id=application_id,
                    version=version,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return application_version_with_retry(application_id, version_number)

    def run(self, run_id: str) -> Run:
        """Finds run by id.

        Args:
            run_id (str): The ID of the application run.

        Returns:
            Run: The run object.
        """
        return Run(self._api, run_id)

    @staticmethod
    def get_api_client(cache_token: bool = True) -> PublicApi:
        """Create and configure an authenticated API client.

        API client instances are shared across all Client instances for efficient connection reuse.
        Two separate instances are maintained: one for cached tokens and one for uncached tokens.

        Args:
            cache_token (bool): If True, caches the authentication token.
                Defaults to True.

        Returns:
            PublicApi: Configured API client with authentication token.

        Raises:
            RuntimeError: If authentication fails.
        """
        # Return cached instance if available
        if cache_token and Client._api_client_cached is not None:
            return Client._api_client_cached
        if not cache_token and Client._api_client_uncached is not None:
            return Client._api_client_uncached

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
        # TODO(Helmut): move to request calling
        client.user_agent = user_agent()
        api_client = PublicApi(client)

        # Cache the instance
        if cache_token:
            Client._api_client_cached = api_client
        else:
            Client._api_client_uncached = api_client

        return api_client
