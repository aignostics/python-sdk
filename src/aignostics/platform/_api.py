"""Authenticated API wrapper and configuration.

This module defines the thin API subclass and configuration that lift
``token_provider`` to a first-class attribute.  Kept separate from ``_client``
so that resource modules can import these types directly without circular
dependencies.

Shared retry helpers (``RETRYABLE_EXCEPTIONS``, ``_log_retry_attempt``) live
here so every platform sub-module can import from a single source of truth.
"""

from collections.abc import Callable

from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.api_client import ApiClient
from aignx.codegen.configuration import AuthSettings, Configuration
from aignx.codegen.exceptions import ServiceException
from loguru import logger
from tenacity import RetryCallState
from urllib3.exceptions import IncompleteRead, PoolError, ProtocolError, ProxyError
from urllib3.exceptions import TimeoutError as Urllib3TimeoutError

RETRYABLE_EXCEPTIONS = (
    ServiceException,
    Urllib3TimeoutError,
    PoolError,
    IncompleteRead,
    ProtocolError,
    ProxyError,
)


def _log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log a retry attempt with function name, sleep duration, and exception."""
    fn = retry_state.fn
    fn_module = fn.__module__ if fn and hasattr(fn, "__module__") else "<unknown>"
    fn_name = fn.__name__ if fn and hasattr(fn, "__name__") else "<unknown>"
    logger.warning(
        "Retrying {}.{} in {} seconds as attempt {} ended with: {}",
        fn_module,
        fn_name,
        retry_state.next_action.sleep if retry_state.next_action else 0,
        retry_state.attempt_number,
        retry_state.outcome.exception() if retry_state.outcome else "<no outcome>",
    )


class _OAuth2TokenProviderConfiguration(Configuration):
    """Overwrites the original Configuration to call a function to obtain a bearer token.

    The base class does not support callbacks. This is necessary for integrations where
    access tokens may expire or need to be refreshed or rotated automatically.
    """

    def __init__(
        self, host: str, ssl_ca_cert: str | None = None, token_provider: Callable[[], str] | None = None
    ) -> None:
        super().__init__(host=host, ssl_ca_cert=ssl_ca_cert)
        self.token_provider = token_provider

    def auth_settings(self) -> AuthSettings:
        token = self.token_provider() if self.token_provider else None
        if not token:
            if self.token_provider is not None:
                logger.warning(
                    "token_provider returned an empty or None token; "
                    "request will proceed without an Authorization header"
                )
            return {}
        return {
            "OAuth2AuthorizationCodeBearer": {
                "type": "oauth2",
                "in": "header",
                "key": "Authorization",
                "value": f"Bearer {token}",
            }
        }


class _AuthenticatedApi(PublicApi):
    """Thin wrapper around the generated :class:`PublicApi`.

    Lifts ``token_provider`` from the deeply-nested ``Configuration`` to a
    top-level attribute, making it accessible without traversing codegen internals.
    """

    token_provider: Callable[[], str] | None

    def __init__(self, api_client: ApiClient, token_provider: Callable[[], str] | None = None) -> None:
        super().__init__(api_client)
        self.token_provider = token_provider


class _AuthenticatedResource:
    """Base for platform resource classes that require an authenticated API client.

    Validates at construction time that the provided API object is a genuine
    :class:`_AuthenticatedApi` instance, ensuring ``token_provider`` is available
    for per-user cache key isolation in ``@cached_operation``.
    """

    _api: _AuthenticatedApi

    def __init__(self, api: _AuthenticatedApi) -> None:
        """Initialize with an authenticated API client.

        Args:
            api: The configured API client providing ``token_provider``.

        Raises:
            TypeError: If *api* is not an :class:`_AuthenticatedApi` instance.
        """
        if not isinstance(api, _AuthenticatedApi):  # runtime guard for untyped callers
            msg = (  # type: ignore[unreachable]
                f"{type(self).__name__} requires _AuthenticatedApi, "
                f"got {type(api).__name__!r}. "
                "Use Client to obtain a correctly configured instance."
            )
            raise TypeError(msg)
        self._api = api
