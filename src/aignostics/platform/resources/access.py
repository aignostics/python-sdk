"""Access-control resources: organization grants and share tokens.

This module provides classes for managing access to Aignostics platform resources.
There are two complementary mechanisms:

* **Share grants** (``AccessGrant``) — delegate access to an existing platform
  user or organization directly.  Grants are always associated with a specific
  resource (e.g. a run) and a subject (e.g. an organization).

* **Share tokens** (``ShareToken``) — create a short-lived, revocable secret that
  can be handed to anyone.  The recipient exchanges the token for a grant without
  needing a platform account.

Typical workflow::

    from aignostics.platform import Client
    from aignx.codegen.models import SubjectType

    client = Client()

    # --- Share a run with another organization via a grant ---
    run = client.run("run-abc123")
    grant = run.grant_access(
        subject_type=SubjectType.ORGANIZATION_USER,
        subject_id="org-xyz",
    )
    print(f"Granted access: {grant.grant_id}")

    # List all active grants on the run
    for g in run.list_share_grants():
        print(g.grant_id, g.subject_type, g.subject_id)

    # Revoke a specific grant
    grant.revoke()

    # --- Share a run via a one-time token ---
    token = client.share_tokens.create()
    print(f"Share this token secret once: {token.share_token}")

    # Grant the token access to the run
    run.grant_access(
        subject_type=SubjectType.SHARE_TOKEN,
        subject_id=token.share_token_id,
    )

    # List tokens and revoke one
    for t in client.share_tokens.list():
        print(t.share_token_id, t.expires_at)
    token.revoke()
"""
import builtins
from collections.abc import Iterator
from datetime import datetime
from typing import Any, cast

from aignx.codegen.models import (
    GrantReadResponse,
    GrantRelation,
    ShareTokenCreateRequest,
    SubjectType,
)
from pydantic import BaseModel, ConfigDict, PrivateAttr
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from aignostics.platform._api import RETRYABLE_EXCEPTIONS, _AuthenticatedApi, _AuthenticatedResource, _log_retry_attempt
from aignostics.platform._operation_cache import cached_operation, operation_cache_clear
from aignostics.platform._settings import settings
from aignostics.platform.resources.utils import paginate
from aignostics.utils import user_agent


class AccessGrant(BaseModel):
    """An active access grant linking a platform resource to a subject.

    A grant gives a *subject* (an organization, an organization user, or a
    share token) a specific *relation* (e.g. ``VIEWER``) on a *resource*.

    Instances are returned by resource-level helpers such as
    ``resource.grant_access()`` and ``resource.list_share_grants()``, or
    fetched directly via ``AccessGrant.for_grant_id()``.

    Attributes:
        grant_id: Unique identifier for this grant.
        subject_id: Identifier of the entity that was granted access.
        subject_type: Category of the subject (``ORGANIZATION_ADMIN``,
            ``ORGANIZATION_USER``, or ``SHARE_TOKEN``).
        relation: Level of access granted (currently always ``VIEWER``).
        created_at: UTC timestamp when the grant was created.
        revoked: ``True`` if the grant has already been revoked.

    Example::

        grant = AccessGrant.for_grant_id("grant-abc123")
        print(grant.subject_type, grant.relation, grant.revoked)

        # Remove the grant
        grant.revoke()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _api: _AuthenticatedApi = PrivateAttr()
    grant_id: str
    subject_id: str
    subject_type: SubjectType
    relation: GrantRelation
    created_at: datetime
    revoked: bool

    def __init__(self, *, api: _AuthenticatedApi, **data: Any) -> None:  # noqa: ANN401, D107
        super().__init__(**data)
        self._api = api

    def revoke(self) -> None:
        """Revoke this grant, removing the subject's access to the resource.

        After this call the in-memory ``revoked`` attribute is *not* updated;
        call ``AccessGrant.for_grant_id(self.grant_id)`` if you need a fresh
        server-side view.

        Raises:
            Exception: If the API request fails.
        """
        self._api.revoke_grant_v1_access_grants_grant_id_delete(
            grant_id=self.grant_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()

    @classmethod
    def for_grant_id(cls, grant_id: str, cache_token: bool = True) -> "AccessGrant":
        """Retrieve a single grant by its ID.

        Args:
            grant_id: The unique identifier of the grant to fetch.
            cache_token: Whether to use the cached authentication token.
                Defaults to ``True``.

        Returns:
            The ``AccessGrant`` corresponding to *grant_id*.

        Raises:
            NotFoundException: If no grant with the given ID exists.
            Exception: If the API request fails.

        Example::

            grant = AccessGrant.for_grant_id("grant-abc123")
            print(grant.subject_type, grant.revoked)
        """
        from aignostics.platform._client import Client  # noqa: PLC0415

        return Client.get_api_client(
            cache_token=cache_token).get_grant_v1_access_grants_grant_id_get(
            grant_id=grant_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )


class ShareToken(BaseModel):
    """A share token that can be used to grant access to platform resources.

    Share tokens decouple *token creation* from *grant creation*: a token is
    minted first, then attached to one or more resources as a subject of type
    ``SHARE_TOKEN``.  The secret value (``share_token``) is only available
    immediately after creation — it is never stored by the platform and will be
    ``None`` for tokens fetched later via ``ShareToken.for_token_id()``.

    Attributes:
        share_token_id: Stable identifier for this token (safe to persist).
        revoked: ``True`` if the token has been revoked.
        created_at: UTC timestamp when the token was created.
        expires_at: Optional UTC expiry; ``None`` means the token never expires.
        share_token: One-time secret value.  Only present immediately after
            ``ShareTokens.create()``; ``None`` for subsequently fetched tokens.

    Example::

        from aignostics.platform import Client

        client = Client()

        # Create a token and note the secret — it won't be retrievable later
        token = client.share_tokens.create()
        secret = token.share_token          # store or transmit this once
        token_id = token.share_token_id     # stable ID for revocation

        # Fetch the token record later (secret is gone)
        fetched = ShareToken.for_token_id(token_id)
        assert fetched.share_token is None

        # List grants created for this token
        for grant in fetched.list_share_grants():
            print(grant.grant_id, grant.relation)

        # Revoke the token (all associated grants become ineffective)
        fetched.revoke()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _api: _AuthenticatedApi = PrivateAttr()

    share_token_id: str
    revoked: bool
    created_at: datetime
    expires_at: datetime | None = None
    share_token: str | None = None

    def __init__(self, *, api: _AuthenticatedApi, **data: Any) -> None:  # noqa: ANN401, D107
        super().__init__(**data)
        self._api = api

    @classmethod
    def for_token_id(cls, share_token_id: str, cache_token: bool = True) -> "ShareToken":
        """Retrieve a share token record by its stable ID.

        The returned object will have ``share_token = None`` because the secret
        is only returned at creation time.

        Args:
            share_token_id: The stable ID of the token to fetch.
            cache_token: Whether to use the cached authentication token.
                Defaults to ``True``.

        Returns:
            The ``ShareToken`` corresponding to *share_token_id*.

        Raises:
            NotFoundException: If no token with the given ID exists.
            Exception: If the API request fails.

        Example::

            token = ShareToken.for_token_id("tok-abc123")
            print(token.revoked, token.expires_at)
        """
        from aignostics.platform._client import Client  # noqa: PLC0415

        api = Client.get_api_client(cache_token=cache_token)
        token = api.get_share_token_v1_access_share_tokens_share_token_id_get(
            share_token_id=share_token_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )

        return ShareToken(api=api, **token.__dict__)

    def list_share_grants(self, *, page_size: int = 100) -> Iterator[AccessGrant]:
        """List all active grants where this token is the subject.

        Each returned ``AccessGrant`` represents a resource this token has been
        granted access to.  Call ``grant.revoke()`` to remove access to a
        specific resource without invalidating the token itself.

        Args:
            page_size: Number of grants to fetch per page (max 100).

        Returns:
            Iterator of ``AccessGrant`` objects for this token.

        Raises:
            Exception: If the API request fails.

        Example::

            token = client.share_tokens.create()
            for grant in token.list_share_grants():
                print(grant.grant_id, grant.relation)
        """

        def fetch_page(**kwargs: object) -> list[GrantReadResponse]:
            return cast(
                "list[GrantReadResponse]",
                self._api.list_grants_v1_access_grants_get(
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
                api=self._api,
                **g.__dict__
            )
            for g in paginate(fetch_page, page_size=page_size)
        )

    def revoke(self) -> None:
        """Revoke this share token, invalidating all grants associated with it.

        After revocation any resource that was shared via this token becomes
        inaccessible to its holder.  The in-memory ``revoked`` attribute is
        *not* updated in-place; fetch a fresh record via
        ``ShareToken.for_token_id()`` if you need the server-side state.

        Raises:
            Exception: If the API request fails.
        """
        self._api.revoke_share_token_v1_access_share_tokens_share_token_id_delete(
            share_token_id=self.share_token_id,
            _request_timeout=settings().run_timeout,
            _headers={"User-Agent": user_agent()},
        )
        operation_cache_clear()


class ShareTokens(_AuthenticatedResource):
    """Collection resource for managing share tokens.

    Accessible as ``client.share_tokens``.  Use ``create()`` to mint a new
    token and ``list()`` to enumerate existing ones.

    Example::

        from aignostics.platform import Client
        from datetime import datetime, timedelta, timezone

        client = Client()

        # Create a token that expires in 7 days
        token = client.share_tokens.create(
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        print("Secret (store once):", token.share_token)
        print("Token ID:", token.share_token_id)

        # List all active tokens
        for t in client.share_tokens.list():
            print(t.share_token_id, t.expires_at, t.revoked)
    """

    def __init__(self, api: _AuthenticatedApi) -> None:  # noqa: D107
        super().__init__(api)

    def list(self, *, run_id: str | None = None, nocache: bool = False, page_size: int = 100) -> Iterator[ShareToken]:
        """List all share tokens for the authenticated user.

        Results are cached for ``run_cache_ttl`` seconds and retried on
        transient network or server errors.

        Args:
            run_id: Optional run ID to filter tokens by the run they are associated with.
                Defaults to ``None`` (no filter).
            nocache: If ``True``, bypass the local cache and fetch fresh data
                from the API.  The fetched result is still written to the cache.
                Defaults to ``False``.
            page_size: Number of tokens to fetch per page (max 100).
                Defaults to 100.

        Returns:
            Iterator of ``ShareToken`` objects.

        Raises:
            Exception: If the API request fails after all retries.

        Example::

            for token in client.share_tokens.list():
                print(token.share_token_id, token.revoked)

            # Force a fresh fetch after creating a new token
            for token in client.share_tokens.list(nocache=True):
                print(token.share_token_id)
        """

        @cached_operation(ttl=settings().run_cache_ttl, token_provider=self._api.token_provider)
        def list_data_with_retry(**kwargs: object) -> builtins.list[ShareToken]:
            return Retrying(
                retry=retry_if_exception_type(exception_types=RETRYABLE_EXCEPTIONS),
                stop=stop_after_attempt(settings().run_retry_attempts),
                wait=wait_exponential_jitter(initial=settings().run_retry_wait_min, max=settings().run_retry_wait_max),
                before_sleep=_log_retry_attempt,
                reraise=True,
            )(
                lambda: [
                    ShareToken(api=self._api, **t.__dict__)
                    for t in self._api.list_share_tokens_v1_access_share_tokens_get(
                        run_id=run_id,
                        revoked=False,
                        _request_timeout=settings().run_timeout,
                        _headers={"User-Agent": user_agent()},
                        **kwargs,  # pyright: ignore[reportArgumentType]
                    )
                ]
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
    ) -> ShareToken:
        """Create a new share token.

        The returned ``ShareToken`` contains the one-time secret in
        ``share_token``.  This is the **only** time the secret is returned by
        the API — subsequent fetches via ``ShareToken.for_token_id()`` will
        have ``share_token = None``.

        Args:
            expires_at: Optional UTC datetime at which the token expires.
                Pass ``None`` (default) for a token that never expires.

        Returns:
            A newly created ``ShareToken`` with ``share_token`` populated.

        Raises:
            Exception: If the API request fails.

        Example::

            from datetime import datetime, timedelta, timezone

            # Token valid for 24 hours
            token = client.share_tokens.create(
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            )
            secret = token.share_token   # transmit to the intended recipient
        """
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
