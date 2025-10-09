import hashlib
import logging
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar
from urllib.request import getproxies

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import AuthSettings, Configuration
from aignx.codegen.exceptions import NotFoundException, ServiceException
from aignx.codegen.models import ApplicationReadResponse as Application
from aignx.codegen.models import MeReadResponse as Me
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
from aignostics.platform.resources.applications import Applications, Versions
from aignostics.platform.resources.runs import ApplicationRun, Runs
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

    _operation_cache: ClassVar[dict[str, tuple[Any, float]]] = {}
    _api_client_cached: ClassVar[PublicApi | None] = None
    _api_client_uncached: ClassVar[PublicApi | None] = None

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

    @staticmethod
    def _cache_key(token: str, method_name: str, *args: object, **kwargs: object) -> str:
        """Generates a cache key based on the token, method name, and parameters.

        Args:
            token (str): The authentication token.
            method_name (str): The name of the method being cached.
            *args: Positional arguments to the method.
            **kwargs: Keyword arguments to the method.

        Returns:
            str: A unique cache key.
        """
        token_hash = hashlib.sha256((token or "").encode()).hexdigest()[:16]
        params = f"{args}:{sorted(kwargs.items())}"
        return f"{token_hash}:{method_name}:{params}"

    @staticmethod
    def cached_operation(ttl: int) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Caches the result of a method call for a specified time-to-live (TTL).

        Args:
            ttl (int): Time-to-live for the cache in seconds.

        Returns:
            Callable: A decorator that caches the method result.
        """

        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            @wraps(func)
            def wrapper(self: "Client", *args: object, **kwargs: object) -> object:
                token = get_token(True)
                cache_key = Client._cache_key(token, func.__name__, *args, **kwargs)

                if cache_key in Client._operation_cache:
                    value, expiry = Client._operation_cache[cache_key]
                    if time.time() < expiry:
                        return value
                    del Client._operation_cache[cache_key]

                result = func(self, *args, **kwargs)
                Client._operation_cache[cache_key] = (result, time.time() + ttl)
                return result

            return wrapper

        return decorator

    @cached_operation(ttl=60)
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
        return Retrying(  # We are not using Tenacity annotations as settings can change at runtime
            retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
            stop=stop_after_attempt(settings().me_retry_attempts_max),
            wait=wait_exponential_jitter(initial=settings().me_retry_wait_min, max=settings().me_retry_wait_max),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )(
            lambda: self._api.get_me_v1_me_get(
                _request_timeout=settings().me_timeout, _headers={"User-Agent": user_agent()}
            )
        )  # Retryer will pass down arguments

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
