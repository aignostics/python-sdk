"""Access-control resources: organization grants and share tokens."""
import builtins
from collections.abc import Iterator
from datetime import datetime
from typing import Protocol, cast

from aignx.codegen.models import (
    GrantReadResponse,
    GrantRelation,
    ShareTokenCreateRequest,
    SubjectType,
)
from pydantic import BaseModel, ConfigDict
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from aignostics.platform._api import RETRYABLE_EXCEPTIONS, _AuthenticatedApi, _AuthenticatedResource, _log_retry_attempt
from aignostics.platform._operation_cache import cached_operation, operation_cache_clear
from aignostics.platform._settings import settings
from aignostics.platform.resources.utils import paginate
from aignostics.utils import user_agent


class ShareSubject(Protocol):
    """An active share subject (duck-type interface for grant targets)."""

    subject_type: SubjectType
    subject_id: str


class AccessGrant(BaseModel):
    """An active share grant.

    Obtained from ``Run.share_grants()``
    Call ``revoke()`` to remove access.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api: _AuthenticatedApi
    grant_id: str
    subject_id: str
    subject_type: SubjectType
    relation: GrantRelation
    created_at: datetime
    revoked: bool

    def revoke(self) -> None:
        """Revoke this grant.

        Raises:
            Exception: If the API request fails.
        """
        self.api.revoke_grant_v1_access_grants_grant_id_delete(
            grant_id=self.grant_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()

        @classmethod
        def for_grant_id(cls, grant_id: str, cache_token: bool = True) -> "AccessGrant":
            from aignostics.platform._client import Client  # noqa: PLC0415

            return Client.get_api_client(
                cache_token=cache_token).get_grant_v1_access_grants_grant_id_get(
                grant_id=grant_id,
                _request_timeout=settings().run_timeout,
                _headers={"User-Agent": user_agent()},
            )


class ShareToken(BaseModel):
    """A share token granting access to a run.

    When returned from ``Run.create_share_token()``, the one-time ``token``
    value is populated.  For tokens obtained from ``Run.share_tokens()``,
    ``token`` is ``None`` because the secret is never stored after creation.
    Call ``revoke()`` to invalidate the token.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api: _AuthenticatedApi
    share_token_id: str
    revoked: bool
    created_at: datetime
    expires_at: datetime | None = None
    share_token: str | None = None

    @classmethod
    def for_token_id(cls, share_token_id: str, cache_token: bool = True) -> "ShareToken":
        from aignostics.platform._client import Client  # noqa: PLC0415

        return Client.get_api_client(cache_token=cache_token).get_share_token_v1_access_share_tokens_share_token_id_get(
            share_token_id=share_token_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )

    def grants(self, *, page_size: int = 100) -> Iterator[AccessGrant]:
        """List the run grants associated with this share token.

        Each returned grant represents a run this token can access.
        Call ``grant.revoke()`` to remove access to a specific run.

        Args:
            page_size: Number of grants to fetch per page (max 100).

        Returns:
            Iterator[RunGrant]: Grants giving this token access to runs.

        Raises:
            Exception: If the API request fails.
        """

        def fetch_page(**kwargs: object) -> list[GrantReadResponse]:
            return cast(
                "list[GrantReadResponse]",
                self.api.list_grants_v1_access_grants_get(
                    subject_type=SubjectType.SHARE_TOKEN,
                    subject_id=self.share_token_id,
                    revoked=False,
                    _request_timeout=settings().run_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                ),
            )

        return (
            AccessGrant(
                api=self.api,
                **g.__dict__
            )
            for g in paginate(fetch_page, page_size=page_size)
        )

    def revoke(self) -> None:
        """Revoke this share token.

        Raises:
            Exception: If the API request fails.
        """
        self.api.revoke_share_token_v1_access_share_tokens_share_token_id_delete(
            share_token_id=self.share_token_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()


class ShareTokens(_AuthenticatedResource):

    def __init__(self, api: _AuthenticatedApi) -> None:
        super().__init__(api)

    def list(self, *, nocache=False, page_size: int = 100) -> Iterator[ShareToken]:

        @cached_operation(ttl=settings().run_cache_ttl, token_provider=self._api.token_provider)
        def list_data_with_retry(**kwargs: object) -> builtins.list[ShareToken]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().run_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: [ShareToken(api=self._api, **t.__dict__) for t in self._api.list_share_tokens_v1_access_share_tokens_get(
                    _request_timeout=settings().run_timeout,
                    _headers={"User-Agent": user_agent()},
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )]
            )

        return paginate(
            lambda **kwargs: list_data_with_retry(
                nocache=nocache,
                **kwargs,
            ),
            page_size=page_size,
        )

    def create(
        self,
        expires_at: datetime | None = None,
    ):
        """Create a new share token."""
        share_token = self._api.create_share_token_v1_access_share_tokens_post(
            share_token_create_request=ShareTokenCreateRequest(
                expires_at=expires_at
            ),
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )

        return ShareToken(
            api=self._api,
            **share_token.__dict__
        )
