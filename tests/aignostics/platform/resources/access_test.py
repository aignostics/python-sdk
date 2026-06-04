"""Unit tests for access control resources: AccessGrant, ShareToken, ShareTokens."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from aignx.codegen.models import (
    GrantReadResponse,
    GrantRelation,
    ResourceType,
    ShareTokenCreateRequest,
    ShareTokenCreateResponse,
    ShareTokenReadResponse,
    SubjectType,
)

from aignostics.platform._api import _AuthenticatedApi
from aignostics.platform.resources.access import (
    AccessGrant,
    ShareToken,
    ShareTokens,
)

_GRANT_ID = "grant-001"
_TOKEN_ID = "token-001"  # noqa: S105
_TOKEN_SECRET = "secret-token-value"  # noqa: S105
_ORG_ID = "org-001"
_SUBJECT_ID = "subject-001"
_RUN_ID = "run-001"
_CREATED_AT = datetime(2024, 1, 1, tzinfo=UTC)


@pytest.fixture
def mock_api() -> Mock:
    """Return a mock _AuthenticatedApi."""
    api = Mock(spec=_AuthenticatedApi)
    api.token_provider = lambda: "test-token"
    return api


@pytest.fixture
def share_tokens_resource(mock_api: Mock) -> ShareTokens:
    """Return a ShareTokens resource bound to the mock API."""
    return ShareTokens(mock_api)


def _make_grant_read_response(
    grant_id: str = _GRANT_ID,
    subject_type: SubjectType = SubjectType.SHARE_TOKEN,
    subject_id: str = _TOKEN_ID,
    revoked: bool = False,
) -> GrantReadResponse:
    return GrantReadResponse(
        grant_id=grant_id,
        resource_type=ResourceType.RUN,
        resource_id=_RUN_ID,
        subject_type=subject_type,
        subject_id=subject_id,
        relation=GrantRelation.VIEWER,
        created_by="user-1",
        created_at=_CREATED_AT,
        revoked=revoked,
    )


def _make_share_token_read_response(token_id: str = _TOKEN_ID) -> ShareTokenReadResponse:
    return ShareTokenReadResponse(
        share_token_id=token_id,
        created_at=_CREATED_AT,
        expires_at=None,
        revoked=False,
    )


def _make_share_token_create_response(
    token_id: str = _TOKEN_ID,
    expires_at: datetime | None = None,
) -> ShareTokenCreateResponse:
    return ShareTokenCreateResponse(
        share_token_id=token_id,
        share_token=_TOKEN_SECRET,
        created_at=_CREATED_AT,
        expires_at=expires_at,
        revoked=False,
    )


class TestAccessGrantRevoke:
    """Tests for AccessGrant.revoke()."""

    @pytest.mark.unit
    @staticmethod
    def test_revoke_calls_api_with_grant_id(mock_api: Mock) -> None:
        """revoke() calls the revoke endpoint with the correct grant_id."""
        grant = AccessGrant(
            api=mock_api,
            grant_id=_GRANT_ID,
            subject_id=_SUBJECT_ID,
            subject_type=SubjectType.ORGANIZATION_USER,
            relation=GrantRelation.VIEWER,
            created_at=_CREATED_AT,
            revoked=False,
        )

        with patch("aignostics.platform.resources.access.operation_cache_clear"):
            grant.revoke()

        call_kw = mock_api.revoke_grant_v1_access_grants_grant_id_delete.call_args.kwargs
        mock_api.revoke_grant_v1_access_grants_grant_id_delete.assert_called_once_with(
            grant_id=_GRANT_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_revoke_clears_operation_cache(mock_api: Mock) -> None:
        """revoke() clears the operation cache after the API call."""
        grant = AccessGrant(
            api=mock_api,
            grant_id=_GRANT_ID,
            subject_id=_SUBJECT_ID,
            subject_type=SubjectType.ORGANIZATION_USER,
            relation=GrantRelation.VIEWER,
            created_at=_CREATED_AT,
            revoked=False,
        )

        with patch("aignostics.platform.resources.access.operation_cache_clear") as mock_clear:
            grant.revoke()

        mock_clear.assert_called_once()


class TestShareTokenForTokenId:
    """Tests for ShareToken.for_token_id() classmethod."""

    @pytest.mark.unit
    @staticmethod
    def test_calls_api_with_token_id(mock_api: Mock) -> None:
        """for_token_id() calls the get_share_token endpoint with the given ID."""
        mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.return_value = (
            _make_share_token_read_response()
        )

        with patch("aignostics.platform._client.Client") as mock_client_cls:
            mock_client_cls.get_api_client.return_value = mock_api
            ShareToken.for_token_id(_TOKEN_ID)

        call_kw = mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.call_args.kwargs
        mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.assert_called_once_with(
            share_token_id=_TOKEN_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_uses_cached_api_client_by_default(mock_api: Mock) -> None:
        """for_token_id() calls get_api_client with cache_token=True by default."""
        mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.return_value = (
            _make_share_token_read_response()
        )

        with patch("aignostics.platform._client.Client") as mock_client_cls:
            mock_client_cls.get_api_client.return_value = mock_api
            ShareToken.for_token_id(_TOKEN_ID)

        mock_client_cls.get_api_client.assert_called_once_with(cache_token=True)

    @pytest.mark.unit
    @staticmethod
    def test_cache_token_false_forwarded(mock_api: Mock) -> None:
        """for_token_id(cache_token=False) passes cache_token=False to get_api_client."""
        mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.return_value = (
            _make_share_token_read_response()
        )

        with patch("aignostics.platform._client.Client") as mock_client_cls:
            mock_client_cls.get_api_client.return_value = mock_api
            ShareToken.for_token_id(_TOKEN_ID, cache_token=False)

        mock_client_cls.get_api_client.assert_called_once_with(cache_token=False)

    @pytest.mark.unit
    @staticmethod
    def test_returns_share_token_with_correct_fields(mock_api: Mock) -> None:
        """for_token_id() returns a ShareToken constructed from the API response."""
        mock_api.get_share_token_v1_access_share_tokens_share_token_id_get.return_value = (
            _make_share_token_read_response()
        )

        with patch("aignostics.platform._client.Client") as mock_client_cls:
            mock_client_cls.get_api_client.return_value = mock_api
            result = ShareToken.for_token_id(_TOKEN_ID)

        assert isinstance(result, ShareToken)
        assert result.share_token_id == _TOKEN_ID
        assert result.created_at == _CREATED_AT
        assert result.revoked is False
        assert result.share_token is None  # Secret absent in read responses


class TestShareTokenRevoke:
    """Tests for ShareToken.revoke()."""

    @pytest.mark.unit
    @staticmethod
    def test_revoke_calls_api_with_token_id(mock_api: Mock) -> None:
        """revoke() calls the revoke endpoint with the correct share_token_id."""
        token = ShareToken(api=mock_api, share_token_id=_TOKEN_ID, revoked=False, created_at=_CREATED_AT)

        with patch("aignostics.platform.resources.access.operation_cache_clear"):
            token.revoke()

        call_kw = mock_api.revoke_share_token_v1_access_share_tokens_share_token_id_delete.call_args.kwargs
        mock_api.revoke_share_token_v1_access_share_tokens_share_token_id_delete.assert_called_once_with(
            share_token_id=_TOKEN_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_revoke_clears_operation_cache(mock_api: Mock) -> None:
        """revoke() clears the operation cache after the API call."""
        token = ShareToken(api=mock_api, share_token_id=_TOKEN_ID, revoked=False, created_at=_CREATED_AT)

        with patch("aignostics.platform.resources.access.operation_cache_clear") as mock_clear:
            token.revoke()

        mock_clear.assert_called_once()


class TestShareTokensList:
    """Tests for ShareTokens.list()."""

    @pytest.mark.unit
    @staticmethod
    def test_returns_share_tokens(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """list() returns ShareToken objects from the API response."""
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = [_make_share_token_read_response()]

        result = list(share_tokens_resource.list())

        assert len(result) == 1
        assert isinstance(result[0], ShareToken)
        assert result[0].share_token_id == _TOKEN_ID
        assert result[0].share_token is None  # Secrets are absent in read responses

    @pytest.mark.unit
    @staticmethod
    def test_returns_empty_list_when_none(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """list() returns an empty iterator when the API returns no tokens."""
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = []

        assert list(share_tokens_resource.list()) == []

    @pytest.mark.unit
    @staticmethod
    def test_multiple_tokens_returned(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """list() returns all tokens from the API response."""
        responses = [_make_share_token_read_response(f"token-{i}") for i in range(3)]
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = responses

        result = list(share_tokens_resource.list())

        assert len(result) == 3
        assert all(isinstance(t, ShareToken) for t in result)
        assert {t.share_token_id for t in result} == {"token-0", "token-1", "token-2"}

    @pytest.mark.unit
    @staticmethod
    def test_nocache_bypasses_cache_and_fetches_fresh_data(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """list(nocache=True) bypasses the cache and calls the API again."""
        first = _make_share_token_read_response("token-first")
        second = _make_share_token_read_response("token-second")
        mock_api.list_share_tokens_v1_access_share_tokens_get.side_effect = [[first], [second]]

        result1 = list(share_tokens_resource.list())
        result2 = list(share_tokens_resource.list(nocache=True))

        assert result1[0].share_token_id == "token-first"  # noqa: S105
        assert result2[0].share_token_id == "token-second"  # noqa: S105
        assert mock_api.list_share_tokens_v1_access_share_tokens_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_default_list_uses_cache_on_second_call(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """list() without nocache returns cached result on the second call."""
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = [_make_share_token_read_response()]

        list(share_tokens_resource.list())
        list(share_tokens_resource.list())

        mock_api.list_share_tokens_v1_access_share_tokens_get.assert_called_once()


class TestShareTokensCreate:
    """Tests for ShareTokens.create()."""

    @pytest.mark.unit
    @staticmethod
    def test_create_returns_share_token_with_secret(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """create() returns a ShareToken that includes the one-time token secret."""
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = _make_share_token_create_response()

        result = share_tokens_resource.create()

        assert isinstance(result, ShareToken)
        assert result.share_token_id == _TOKEN_ID
        assert result.share_token == _TOKEN_SECRET

    @pytest.mark.unit
    @staticmethod
    def test_create_without_expires_at_passes_none(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """create() passes expires_at=None to the API when not specified."""
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = _make_share_token_create_response()

        share_tokens_resource.create()

        call_kw = mock_api.create_share_token_v1_access_share_tokens_post.call_args.kwargs
        req: ShareTokenCreateRequest = call_kw["share_token_create_request"]
        assert req.expires_at is None

    @pytest.mark.unit
    @staticmethod
    def test_create_with_expires_at_forwards_value(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """create(expires_at=...) forwards the expiry to the API and returns it on the token."""
        expires = datetime(2025, 12, 31, tzinfo=UTC)
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = _make_share_token_create_response(
            expires_at=expires
        )

        result = share_tokens_resource.create(expires_at=expires)

        call_kw = mock_api.create_share_token_v1_access_share_tokens_post.call_args.kwargs
        req: ShareTokenCreateRequest = call_kw["share_token_create_request"]
        assert req.expires_at == expires
        assert result.expires_at == expires

    @pytest.mark.unit
    @staticmethod
    def test_create_returns_token_with_correct_metadata(share_tokens_resource: ShareTokens, mock_api: Mock) -> None:
        """create() maps all fields from the API response onto the returned ShareToken."""
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = _make_share_token_create_response()

        result = share_tokens_resource.create()

        assert result.created_at == _CREATED_AT
        assert result.revoked is False
        assert result.expires_at is None
