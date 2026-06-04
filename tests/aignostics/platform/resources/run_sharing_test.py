"""Unit tests for Run sharing methods: list_share_grants and grant_access."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from aignx.codegen.models import (
    GrantCreateRequest,
    GrantReadResponse,
    GrantRelation,
    ResourceType,
    SubjectType,
)

from aignostics.platform._api import _AuthenticatedApi
from aignostics.platform.resources.access import AccessGrant
from aignostics.platform.resources.runs import Run

_RUN_ID = "550e8400-e29b-41d4-a716-446655440000"
_ORG_ID = "org-001"
_GRANT_ID = "grant-001"
_CREATED_AT = datetime(2024, 1, 1, tzinfo=UTC)


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


def _make_grant_response(
    grant_id: str = _GRANT_ID,
    subject_type: SubjectType = SubjectType.ORGANIZATION_USER,
    subject_id: str = _ORG_ID,
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


class TestRunListShareGrants:
    """Tests for Run.list_share_grants()."""

    @pytest.mark.unit
    @staticmethod
    def test_returns_access_grants(run: Run, mock_api: Mock) -> None:
        """list_share_grants() yields AccessGrant objects from the API response."""
        mock_api.list_grants_v1_access_grants_get.return_value = [_make_grant_response()]

        result = list(run.list_share_grants())

        assert len(result) == 1
        assert isinstance(result[0], AccessGrant)
        assert result[0].grant_id == _GRANT_ID
        assert result[0].relation == GrantRelation.VIEWER

    @pytest.mark.unit
    @staticmethod
    def test_calls_api_with_run_resource_params(run: Run, mock_api: Mock) -> None:
        """list_share_grants() passes resource_type=RUN and the run's ID to the API."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        list(run.list_share_grants())

        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        assert call_kw["resource_type"] == ResourceType.RUN
        assert call_kw["resource_id"] == _RUN_ID
        assert call_kw["revoked"] is False

    @pytest.mark.unit
    @staticmethod
    def test_default_filters_are_none(run: Run, mock_api: Mock) -> None:
        """list_share_grants() passes subject_type=None and subject_id=None by default."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        list(run.list_share_grants())

        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        assert call_kw["subject_type"] is None
        assert call_kw["subject_id"] is None

    @pytest.mark.unit
    @staticmethod
    def test_passes_subject_type_filter(run: Run, mock_api: Mock) -> None:
        """list_share_grants(subject_type=...) forwards the filter to the API."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        list(run.list_share_grants(subject_type=SubjectType.SHARE_TOKEN))

        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        assert call_kw["subject_type"] == SubjectType.SHARE_TOKEN

    @pytest.mark.unit
    @staticmethod
    def test_passes_subject_id_filter(run: Run, mock_api: Mock) -> None:
        """list_share_grants(subject_id=...) forwards the filter to the API."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        list(run.list_share_grants(subject_id="token-abc"))

        call_kw = mock_api.list_grants_v1_access_grants_get.call_args.kwargs
        assert call_kw["subject_id"] == "token-abc"

    @pytest.mark.unit
    @staticmethod
    def test_returns_empty_iterator_when_no_grants(run: Run, mock_api: Mock) -> None:
        """list_share_grants() returns an empty iterator when the API returns no grants."""
        mock_api.list_grants_v1_access_grants_get.return_value = []

        assert list(run.list_share_grants()) == []

    @pytest.mark.unit
    @staticmethod
    def test_returns_multiple_grants(run: Run, mock_api: Mock) -> None:
        """list_share_grants() returns all grants from the API response."""
        responses = [_make_grant_response(grant_id=f"grant-{i}") for i in range(3)]
        mock_api.list_grants_v1_access_grants_get.return_value = responses

        result = list(run.list_share_grants())

        assert len(result) == 3
        assert all(isinstance(g, AccessGrant) for g in result)

    @pytest.mark.unit
    @staticmethod
    def test_raises_for_page_size_exceeding_max(run: Run) -> None:
        """list_share_grants() raises ValueError when page_size > 100."""
        with pytest.raises(ValueError, match="page_size"):
            list(run.list_share_grants(page_size=101))

    @pytest.mark.unit
    @staticmethod
    def test_nocache_bypasses_cache(run: Run, mock_api: Mock) -> None:
        """list_share_grants(nocache=True) bypasses the cache and calls the API again."""
        first = [_make_grant_response(grant_id="grant-first")]
        second = [_make_grant_response(grant_id="grant-second")]
        mock_api.list_grants_v1_access_grants_get.side_effect = [first, second]

        result1 = list(run.list_share_grants())
        result2 = list(run.list_share_grants(nocache=True))

        assert result1[0].grant_id == "grant-first"
        assert result2[0].grant_id == "grant-second"
        assert mock_api.list_grants_v1_access_grants_get.call_count == 2

    @pytest.mark.unit
    @staticmethod
    def test_default_uses_cache_on_second_call(run: Run, mock_api: Mock) -> None:
        """list_share_grants() without nocache returns cached result on the second call."""
        mock_api.list_grants_v1_access_grants_get.return_value = [_make_grant_response()]

        list(run.list_share_grants())
        list(run.list_share_grants())

        mock_api.list_grants_v1_access_grants_get.assert_called_once()


class TestRunGrantAccess:
    """Tests for Run.grant_access()."""

    @pytest.mark.unit
    @staticmethod
    def test_creates_grant_with_correct_request(run: Run, mock_api: Mock) -> None:
        """grant_access() calls create_grant with the correct GrantCreateRequest fields."""
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant_response()

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            run.grant_access(subject_type=SubjectType.ORGANIZATION_USER, subject_id=_ORG_ID)

        req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs["grant_create_request"]
        assert req.resource_type == ResourceType.RUN
        assert req.resource_id == _RUN_ID
        assert req.subject_type == SubjectType.ORGANIZATION_USER
        assert req.subject_id == _ORG_ID
        assert req.relation == GrantRelation.VIEWER

    @pytest.mark.unit
    @staticmethod
    def test_returns_access_grant(run: Run, mock_api: Mock) -> None:
        """grant_access() returns an AccessGrant built from the API response."""
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant_response()

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            result = run.grant_access(subject_type=SubjectType.ORGANIZATION_USER, subject_id=_ORG_ID)

        assert isinstance(result, AccessGrant)
        assert result.grant_id == _GRANT_ID
        assert result.subject_id == _ORG_ID
        assert result.relation == GrantRelation.VIEWER

    @pytest.mark.unit
    @staticmethod
    def test_clears_operation_cache(run: Run, mock_api: Mock) -> None:
        """grant_access() clears the operation cache after creating the grant."""
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant_response()

        with patch("aignostics.platform.resources.runs.operation_cache_clear") as mock_clear:
            run.grant_access(subject_type=SubjectType.ORGANIZATION_USER, subject_id=_ORG_ID)

        mock_clear.assert_called_once()

    @pytest.mark.unit
    @staticmethod
    def test_works_with_share_token_subject_type(run: Run, mock_api: Mock) -> None:
        """grant_access() accepts SubjectType.SHARE_TOKEN and forwards it correctly."""
        token_id = "token-abc"  # noqa: S105
        mock_api.create_grant_v1_access_grants_post.return_value = _make_grant_response(
            subject_type=SubjectType.SHARE_TOKEN, subject_id=token_id
        )

        with patch("aignostics.platform.resources.runs.operation_cache_clear"):
            result = run.grant_access(subject_type=SubjectType.SHARE_TOKEN, subject_id=token_id)

        req: GrantCreateRequest = mock_api.create_grant_v1_access_grants_post.call_args.kwargs["grant_create_request"]
        assert req.subject_type == SubjectType.SHARE_TOKEN
        assert req.subject_id == token_id
        assert isinstance(result, AccessGrant)
