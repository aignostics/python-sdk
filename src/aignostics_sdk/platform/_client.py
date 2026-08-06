from __future__ import annotations

import os
from collections.abc import Callable  # noqa: TC003
from typing import TYPE_CHECKING, ClassVar
from urllib.request import getproxies

import semver
from loguru import logger
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from aignostics_sdk.platform._authentication import get_token
from aignostics_sdk.platform._operation_cache import cached_operation
from aignostics_sdk.utils import user_agent

from ._settings import settings
from .resources.access import ShareTokens

if TYPE_CHECKING:
    from aignostics_sdk._codegen.models import ApplicationReadResponse as Application
    from aignostics_sdk._codegen.models import MeReadResponse as Me
    from aignostics_sdk._codegen.models import VersionReadResponse as ApplicationVersion
    from aignostics_sdk.platform._api import (
        _AuthenticatedApi,
    )
    from aignostics_sdk.platform.resources.applications import Applications, Versions
    from aignostics_sdk.platform.resources.runs import Run, Runs

# Safety bound for the external token-provider cache.  In normal usage callers
# reuse a single provider reference, so this limit should never be reached.
_MAX_EXTERNAL_CLIENTS = 16


class Client:
    """Main client for interacting with the Aignostics Platform API.

    - Provides access to platform resources like applications, versions, and runs.
    - Handles authentication and API client configuration.
    - Supports external token providers for machine-to-machine or custom auth flows.
    - Retries on network and server errors for specific operations.
    - Caches operation results for specific operations.
    """

    _api_client_cached: ClassVar[_AuthenticatedApi | None] = None
    _api_client_uncached: ClassVar[_AuthenticatedApi | None] = None
    _api_client_external: ClassVar[dict[Callable[[], str], _AuthenticatedApi]] = {}

    _api: _AuthenticatedApi
    applications: Applications
    versions: Versions
    runs: Runs
    share_tokens: ShareTokens

    def __init__(self, cache_token: bool = True, token_provider: Callable[[], str] | None = None) -> None:
        """Initializes a client instance with authenticated API access.

        Args:
            cache_token: If True, caches the authentication token. Defaults to True.
                Ignored when ``token_provider`` is supplied.
            token_provider: Optional external token provider callable. When provided,
                bypasses internal OAuth authentication entirely. The callable must
                return a raw access token string (without the ``Bearer `` prefix).
                When set, ``cache_token`` has no effect because the external provider
                manages its own token lifecycle.

        Sets up resource accessors for applications, versions, and runs.
        """
        from aignostics_sdk.platform.resources.applications import Applications, Versions  # noqa: PLC0415
        from aignostics_sdk.platform.resources.runs import Runs  # noqa: PLC0415

        try:
            logger.trace(
                "Initializing client with cache_token={}, token_provider={}",
                cache_token,
                type(token_provider).__name__ if token_provider is not None else None,
            )
            self._api = Client.get_api_client(cache_token=cache_token, token_provider=token_provider)
            self.applications: Applications = Applications(self._api)
            self.runs: Runs = Runs(self._api)
            self.share_tokens: ShareTokens = ShareTokens(self._api)
            self.versions: Versions = Versions(self._api)
            logger.trace("Client initialized successfully.")
        except Exception:
            logger.exception("Failed to initialize client.")
            raise

    def me(self, nocache: bool = False) -> Me:
        """Retrieves info about the current user and their organisation.

        Retries on network and server errors.

        Note:
        - We are not using urllib3s retry class as it does not support fine grained definition when to retry,
            exponential backoff with jitter, logging before retry, and is difficult to configure.

        Args:
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Me: User and organization information.

        Raises:
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """
        from aignostics_sdk.platform._api import RETRYABLE_EXCEPTIONS, _log_retry_attempt  # noqa: PLC0415

        @cached_operation(ttl=settings().me_cache_ttl, token_provider=self._api.token_provider)
        def me_with_retry() -> Me:
            return Retrying(  # We are not using Tenacity annotations as settings can change at runtime
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().me_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().me_retry_wait_min, max=settings().me_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.get_me_v1_me_get(
                    _request_timeout=settings().me_timeout, _headers={"User-Agent": user_agent()}
                )
            )  # Retryer will pass down arguments

        return me_with_retry(nocache=nocache)  # type: ignore[call-arg]

    def application(self, application_id: str, nocache: bool = False) -> Application:
        """Find application by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            Application: The application object.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """
        from aignostics_sdk.platform._api import RETRYABLE_EXCEPTIONS, _log_retry_attempt  # noqa: PLC0415

        @cached_operation(ttl=settings().application_cache_ttl, token_provider=self._api.token_provider)
        def application_with_retry(application_id: str) -> Application:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_retry_wait_min, max=settings().application_retry_wait_max
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.read_application_by_id_v1_applications_application_id_get(
                    application_id=application_id,
                    _request_timeout=settings().application_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return application_with_retry(application_id, nocache=nocache)  # type: ignore[call-arg]

    def application_version(
        self, application_id: str, version_number: str | None = None, nocache: bool = False
    ) -> ApplicationVersion:
        """Find application version by id.

        Retries on network and server errors.

        Args:
            application_id (str): The ID of the application.
            version_number (str | None): The version number of the application.
                If None, the latest version will be retrieved.
            nocache (bool): If True, skip reading from cache and fetch fresh data from the API.
                The fresh result will still be cached for subsequent calls. Defaults to False.

        Returns:
            ApplicationVersion: The application version object.

        Raises:
            NotFoundException: If the application with the given ID and version number is not found.
            ValueError: If the version is not valid semver.
            aignx.codegen.exceptions.ApiException: If the API call fails.
        """
        from aignostics_sdk._codegen.exceptions import NotFoundException  # noqa: PLC0415
        from aignostics_sdk.platform._api import RETRYABLE_EXCEPTIONS, _log_retry_attempt  # noqa: PLC0415
        from aignostics_sdk.platform.resources.applications import Versions  # noqa: PLC0415

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
        @cached_operation(ttl=settings().application_version_cache_ttl, token_provider=self._api.token_provider)
        def application_version_with_retry(application_id: str, version: str) -> ApplicationVersion:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().application_version_retry_attempts),
                wait=wait_exponential_jitter(
                    initial=settings().application_version_retry_wait_min,
                    max=settings().application_version_retry_wait_max,
                ),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: self._api.application_version_details_v1_applications_application_id_versions_version_get(
                    application_id=application_id,
                    version=version,
                    _request_timeout=settings().application_version_timeout,
                    _headers={"User-Agent": user_agent()},
                )
            )

        return application_version_with_retry(application_id, version_number, nocache=nocache)  # type: ignore[call-arg]

    def run(self, run_id: str) -> Run:
        """Finds run by id.

        Args:
            run_id (str): The ID of the application run.

        Returns:
            Run: The run object.
        """
        from aignostics_sdk.platform.resources.runs import Run  # noqa: PLC0415

        return Run(self._api, run_id)

    @staticmethod
    def get_api_client(cache_token: bool = True, token_provider: Callable[[], str] | None = None) -> _AuthenticatedApi:
        """Create and configure an authenticated API client.

        API client instances are shared across all Client instances for efficient connection reuse.
        Three pools are maintained: cached-token, uncached-token, and external-provider (keyed by
        the provider callable — callers should reuse a stable ``token_provider`` reference for
        connection reuse).

        Args:
            cache_token: If True, caches the authentication token. Defaults to True.
            token_provider: Optional external token provider. When provided, bypasses
                internal OAuth and uses this callable to obtain bearer tokens.

        Returns:
            _AuthenticatedApi: Configured API client with authentication token.

        Raises:
            RuntimeError: If authentication fails.
        """
        from aignostics_sdk._codegen.api_client import ApiClient  # noqa: PLC0415
        from aignostics_sdk.platform._api import (  # noqa: PLC0415
            _AuthenticatedApi,
            _OAuth2TokenProviderConfiguration,
        )

        # Check singleton caches first
        if token_provider is not None:
            if token_provider in Client._api_client_external:
                return Client._api_client_external[token_provider]
        elif cache_token and Client._api_client_cached is not None:
            return Client._api_client_cached
        elif not cache_token and Client._api_client_uncached is not None:
            return Client._api_client_uncached

        # Resolve the effective token provider
        effective_provider: Callable[[], str] = (
            token_provider if token_provider is not None else (lambda: get_token(use_cache=cache_token))
        )

        # Build the API client
        ca_file = os.getenv("REQUESTS_CA_BUNDLE")  # point to .cer file of proxy if defined
        config = _OAuth2TokenProviderConfiguration(
            host=settings().api_root, ssl_ca_cert=ca_file, token_provider=effective_provider
        )
        config.proxy = getproxies().get("https")  # use system proxy
        client = ApiClient(config)
        client.user_agent = user_agent()
        api_client = _AuthenticatedApi(client, effective_provider)

        # Store in the appropriate singleton cache.
        # For external providers we use a simple bounded dict rather than LRU:
        # switching providers is rare in practice, and a full clear is simpler
        # than tracking access order while still bounding memory.
        if token_provider is not None:
            if len(Client._api_client_external) >= _MAX_EXTERNAL_CLIENTS:
                logger.warning(
                    "External token provider cache exceeded {} entries; clearing to prevent resource leak. "
                    "Pass a stable (module-level or instance) callable — each new lambda is a distinct "
                    "key and will re-trigger this eviction.",
                    _MAX_EXTERNAL_CLIENTS,
                )
                Client._api_client_external.clear()
            Client._api_client_external[token_provider] = api_client
        elif cache_token:
            Client._api_client_cached = api_client
        else:
            Client._api_client_uncached = api_client

        return api_client
