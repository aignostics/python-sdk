"""Unit tests for Run sharing methods."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from aignx.codegen.models import (
    GrantCreateRequest,
    GrantReadResponse,
    GrantRelation,
    MeReadResponse,
    ResourceType,
    ShareTokenCreateRequest,
    ShareTokenCreateResponse,
    ShareTokenReadResponse,
    SubjectType,
)

from aignostics.platform._api import _AuthenticatedApi
from aignostics.platform.resources.access import OrganizationGrant, RunGrant, ShareToken
from aignostics.platform.resources.runs import Run

_RUN_ID = "550e8400-e29b-41d4-a716-446655440000"
_ORG_ID = "org-001"
_GRANT_ID = "grant-001"
_TOKEN_ID = "token-001"  # noqa: S105
_TOKEN_VALUE = "secret-share-token"  # noqa: S105


@pytest.fixture
def mock_api() -> Mock:
    """Return a mock _AuthenticatedApi."""
    api = Mock(spec=_AuthenticatedApi)
    api.token_provider = lambda: "test-token"
    return api


@pytest.fixture
def run(mock_api: Mock) -> Run:
    """Return a Run bound to the mock API."""
    return Run(mock_api, _RUN_ID)


def _make_grant(
    grant_id: str = _GRANT_ID,
    subject_type: SubjectType = SubjectType.ORGANIZATION_USER,
    subject_id: str = _ORG_ID,
    revoked: bool = False,
) -> GrantReadResponse:
    """Build a minimal GrantReadResponse for testing."""
    return GrantReadResponse(
        grant_id=grant_id,
        resource_type=ResourceType.RUN,
        resource_id=_RUN_ID,
        subject_type=subject_type,
        subject_id=subject_id,
        relation=GrantRelation.VIEWER,
        created_by="user-1",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        revoked=revoked,
    )


def _make_share_token_response(token_id: str = _TOKEN_ID) -> ShareTokenReadResponse:
    """Build a minimal ShareTokenReadResponse for testing."""
    return ShareTokenReadResponse(
        share_token_id=token_id,
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        expires_at=None,
        revoked=False,
    )


def _make_me(org_id: str = _ORG_ID) -> MeReadResponse:
    """Build a minimal MeReadResponse mock for testing."""
    me = Mock(spec=MeReadResponse)
    me.organization = Mock()
    me.organization.id = org_id
    return me


class TestOrganizationGrants:
    """Tests for Run.organization_grants()."""

    @pytest.mark.unit
    @staticmethod
    def test_returns_org_grants(run: Run, mock_api: Mock) -> None:
        """organization_grants() returns OrganizationGrant objects for org_user/org_admin."""
        org_grant = _make_grant(subject_type=SubjectType.ORGANIZATION_USER)
        token_grant = _make_grant(grant_id="g2", subject_type=SubjectType.SHARE_TOKEN, subject_id=_TOKEN_ID)
        mock_api.list_grants_v1_access_grants_get.return_value = [org_grant, token_grant]

        result = list(run.organization_grants())

        assert len(result) == 1
        assert isinstance(result[0], OrganizationGrant)
        assert result[0].grant_id == _GRANT_ID
        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        mock_api.list_grants_v1_access_grants_get.assert_called_once_with(
            resource_type=ResourceType.RUN,
            resource_id=_RUN_ID,
            revoked=False,
            page=1,
            page_size=100,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_includes_org_admin_grants(run: Run, mock_api: Mock) -> None:
        """organization_grants() includes organization_admin subject type."""
        admin_grant = _make_grant(subject_type=SubjectType.ORGANIZATION_ADMIN)
        mock_api.list_grants_v1_access_grants_get.return_value = [admin_grant]

        result = list(run.organization_grants())

        assert len(result) == 1
        assert isinstance(result[0], OrganizationGrant)

    @pytest.mark.unit
    @staticmethod
    def test_returns_empty_list_when_none(run: Run, mock_api: Mock) -> None:
        """organization_grants() returns an empty iterator when the API returns no grants."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        result = list(run.organization_grants())

        assert result == []


class TestShareTokens:
    """Tests for Run.share_tokens()."""

    @pytest.mark.unit
    @staticmethod
    def test_returns_share_tokens(run: Run, mock_api: Mock) -> None:
        """share_tokens() returns ShareToken objects from the API."""
        token = _make_share_token_response()
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = [token]

        result = list(run.share_tokens())

        assert len(result) == 1
        assert isinstance(result[0], ShareToken)
        assert result[0].share_token_id == _TOKEN_ID
        assert result[0].token is None
        call_kw = mock_api.list_share_tokens_v1_access_share_tokens_get.call_args.kwargs
        mock_api.list_share_tokens_v1_access_share_tokens_get.assert_called_once_with(
            run_id=_RUN_ID,
            revoked=False,
            page=1,
            page_size=100,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_returns_empty_list_when_none(run: Run, mock_api: Mock) -> None:
        """share_tokens() returns an empty iterator when the API returns no tokens."""
        mock_api.list_share_tokens_v1_access_share_tokens_get.return_value = []

        result = list(run.share_tokens())

        assert result == []


class TestShareWithOrganization:
    """Tests for Run.share_with_organization()."""

    @pytest.mark.unit
    @staticmethod
    def test_creates_org_user_grant(run: Run, mock_api: Mock) -> None:
        """share_with_organization() resolves org ID via me() and returns OrganizationGrant."""
        mock_api.get_me_v1_me_get.return_value = _make_me()
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant()

        with patch("aignostics.platform.resources.runs.operation_cache_clear") as mock_clear:
            result = run.share_with_organization()

        assert isinstance(result, OrganizationGrant)
        assert result.grant_id == _GRANT_ID
        assert result.subject_id == _ORG_ID
        assert result.relation == GrantRelation.VIEWER
        mock_api.get_me_v1_me_get.assert_called_once()
        mock_api.create_grant_v1_access_grants_post.assert_called_once()
        req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs["grant_create_request"]
        assert req.resource_type == ResourceType.RUN
        assert req.resource_id == _RUN_ID
        assert req.subject_type == SubjectType.ORGANIZATION_USER
        assert req.subject_id == _ORG_ID
        assert req.relation == GrantRelation.VIEWER
        mock_clear.assert_called_once()

    @pytest.mark.unit
    @staticmethod
    def test_uses_org_id_from_me(run: Run, mock_api: Mock) -> None:
        """share_with_organization() uses the org ID from me() as subject_id."""
        mock_api.get_me_v1_me_get.return_value = _make_me(org_id="other-org")
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant(subject_id="other-org")

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            run.share_with_organization()

        req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs["grant_create_request"]
        assert req.subject_id == "other-org"

    @pytest.mark.unit
    @staticmethod
    def test_uses_explicit_org_id_without_calling_me(run: Run, mock_api: Mock) -> None:
        """share_with_organization(organization_id=...) skips the /me call."""
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant(subject_id="explicit-org")

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            result = run.share_with_organization(organization_id="explicit-org")

        mock_api.get_me_v1_me_get.assert_not_called()
        assert isinstance(result, OrganizationGrant)
        req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs["grant_create_request"]
        assert req.subject_id == "explicit-org"


class TestOrganizationGrantRevoke:
    """Tests for OrganizationGrant.revoke()."""

    @pytest.mark.unit
    @staticmethod
    def test_revoke_calls_api_and_clears_cache(mock_api: Mock) -> None:
        """revoke() calls the revoke endpoint and clears the operation cache."""
        data = _make_grant()
        grant = OrganizationGrant(
            mock_api,
            str(data.grant_id),
            subject_id=str(data.subject_id),
            subject_type=data.subject_type,
            relation=data.relation,
            created_at=data.created_at,
            revoked=bool(data.revoked),
        )

        with patch("aignostics.platform.resources.access.operation_cache_clear") as mock_clear:
            grant.revoke()

        call_kw = mock_api.revoke_grant_v1_access_grants_grant_id_delete.call_args.kwargs
        mock_api.revoke_grant_v1_access_grants_grant_id_delete.assert_called_once_with(
            grant_id=_GRANT_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )
        mock_clear.assert_called_once()


class TestCreateShareToken:
    """Tests for Run.create_share_token()."""

    @pytest.mark.unit
    @staticmethod
    def test_creates_token_and_grant(run: Run, mock_api: Mock) -> None:
        """create_share_token() creates the token, binds it via a grant, and returns ShareToken."""
        token_response = ShareTokenCreateResponse(
            share_token_id=_TOKEN_ID,
            share_token=_TOKEN_VALUE,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            expires_at=None,
            revoked=False,
        )
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = token_response
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant(
            subject_type=SubjectType.SHARE_TOKEN, subject_id=_TOKEN_ID
        )

        with patch("aignostics.platform.resources.runs.operation_cache_clear") as mock_clear:
            result = run.create_share_token()

        assert isinstance(result, ShareToken)
        assert result.share_token_id == _TOKEN_ID
        assert result.token == _TOKEN_VALUE
        assert result.created_at == datetime(2024, 1, 1, tzinfo=UTC)
        assert result.expires_at is None
        mock_api.create_share_token_v1_access_share_tokens_post.assert_called_once()
        grant_req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs[
            "grant_create_request"
        ]
        assert grant_req.resource_type == ResourceType.RUN
        assert grant_req.resource_id == _RUN_ID
        assert grant_req.subject_type == SubjectType.SHARE_TOKEN
        assert grant_req.subject_id == _TOKEN_ID
        assert grant_req.relation == GrantRelation.VIEWER
        mock_clear.assert_called_once()

    @pytest.mark.unit
    @staticmethod
    def test_passes_expires_at(run: Run, mock_api: Mock) -> None:
        """create_share_token() forwards expires_at to the share-token creation request."""
        expires = datetime(2025, 12, 31, tzinfo=UTC)
        token_response = ShareTokenCreateResponse(
            share_token_id=_TOKEN_ID,
            share_token=_TOKEN_VALUE,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            expires_at=expires,
            revoked=False,
        )
        mock_api.create_share_token_v1_access_share_tokens_post.return_value = token_response
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant(
            subject_type=SubjectType.SHARE_TOKEN, subject_id=_TOKEN_ID
        )

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            result = run.create_share_token(expires_at=expires)

        token_req: ShareTokenCreateRequest = mock_api.create_share_token_v1_access_share_tokens_post.call_args.kwargs[
            "share_token_create_request"
        ]
        assert token_req.expires_at == expires
        assert result.expires_at == expires


class TestShareTokenGrants:
    """Tests for ShareToken.grants()."""

    @pytest.mark.unit
    @staticmethod
    def test_returns_run_grants(mock_api: Mock) -> None:
        """grants() returns RunGrant objects for each grant associated with the token."""
        grant = GrantReadResponse(
            grant_id=_GRANT_ID,
            resource_type=ResourceType.RUN,
            resource_id=_RUN_ID,
            subject_type=SubjectType.SHARE_TOKEN,
            subject_id=_TOKEN_ID,
            relation=GrantRelation.VIEWER,
            created_by="user-1",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            revoked=False,
        )
        mock_api.list_grants_v1_access_grants_get.return_value = [grant]
        token = ShareToken(mock_api, _TOKEN_ID)

        result = list(token.grants())

        assert len(result) == 1
        assert isinstance(result[0], RunGrant)
        assert result[0].grant_id == _GRANT_ID
        assert result[0].run_id == _RUN_ID
        assert result[0].relation == GrantRelation.VIEWER
        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        mock_api.list_grants_v1_access_grants_get.assert_called_once_with(
            subject_type=SubjectType.SHARE_TOKEN,
            subject_id=_TOKEN_ID,
            revoked=False,
            page=1,
            page_size=100,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )

    @pytest.mark.unit
    @staticmethod
    def test_returns_empty_list_when_none(mock_api: Mock) -> None:
        """grants() returns an empty iterator when the API returns no grants."""
        mock_api.list_grants_v1_access_grants_get.return_value = []
        token = ShareToken(mock_api, _TOKEN_ID)

        assert list(token.grants()) == []

    @pytest.mark.unit
    @staticmethod
    def test_run_grant_revoke(mock_api: Mock) -> None:
        """RunGrant.revoke() calls the revoke endpoint and clears the cache."""
        grant = RunGrant(
            mock_api,
            _GRANT_ID,
            run_id=_RUN_ID,
            relation=GrantRelation.VIEWER,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            revoked=False,
        )

        with patch("aignostics.platform.resources.access.operation_cache_clear") as mock_clear:
            grant.revoke()

        call_kw = mock_api.revoke_grant_v1_access_grants_grant_id_delete.call_args.kwargs
        mock_api.revoke_grant_v1_access_grants_grant_id_delete.assert_called_once_with(
            grant_id=_GRANT_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )
        mock_clear.assert_called_once()


class TestShareTokenRevoke:
    """Tests for ShareToken.revoke() and Run.share_token() factory."""

    @pytest.mark.unit
    @staticmethod
    def test_revoke_calls_api_and_clears_cache(mock_api: Mock) -> None:
        """ShareToken.revoke() calls the revoke endpoint and clears the cache."""
        token = ShareToken(mock_api, _TOKEN_ID)

        with patch("aignostics.platform.resources.access.operation_cache_clear") as mock_clear:
            token.revoke()

        call_kw = mock_api.revoke_share_token_v1_access_share_tokens_share_token_id_delete.call_args.kwargs
        mock_api.revoke_share_token_v1_access_share_tokens_share_token_id_delete.assert_called_once_with(
            share_token_id=_TOKEN_ID,
            _request_timeout=call_kw["_request_timeout"],
            _headers={"User-Agent": call_kw["_headers"]["User-Agent"]},
        )
        mock_clear.assert_called_once()

    @pytest.mark.unit
    @staticmethod
    def test_run_share_token_factory(run: Run, mock_api: Mock) -> None:
        """Run.share_token(id) returns a ShareToken handle without making an API call."""
        token = run.share_token(_TOKEN_ID)

        assert isinstance(token, ShareToken)
        assert token.share_token_id == _TOKEN_ID
        mock_api.assert_not_called()
