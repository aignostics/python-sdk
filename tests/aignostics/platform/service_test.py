"""Tests for the platform service module."""

from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aignostics.platform._service import Service, UserInfo
from aignostics.utils import Health

_PATCH_AUTH_GETTER = "aignostics.platform._service.get_token"


@pytest.mark.unit
async def test_determine_api_authenticated_health_success() -> None:
    """Health.UP returned when httpx responds 200 with auth token."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "UP"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with (
        patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls,
        patch(_PATCH_AUTH_GETTER, return_value="test-token"),
    ):
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.UP


@pytest.mark.unit
async def test_determine_api_authenticated_health_non_200() -> None:
    """Health.DOWN returned when httpx responds with non-200."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.SERVICE_UNAVAILABLE

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with (
        patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls,
        patch(_PATCH_AUTH_GETTER, return_value="test-token"),
    ):
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_authenticated_health_handles_exception() -> None:
    """Health.DOWN with reason when get_token raises."""
    with patch(_PATCH_AUTH_GETTER, side_effect=RuntimeError("no auth")):
        result = await Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_public_health_non_200() -> None:
    """Health.DOWN returned when httpx responds with non-200."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.SERVICE_UNAVAILABLE

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_public_health_handles_exception() -> None:
    """Health.DOWN returned when httpx raises."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = ConnectionError("unreachable")

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_public_health_up_response() -> None:
    """HTTP 200 + {"status": "UP"} body → Health.UP (explicit JSON body check)."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "UP"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.UP


@pytest.mark.unit
async def test_determine_api_public_health_degraded_response() -> None:
    """HTTP 200 + {"status": "DEGRADED"} body → Health.DEGRADED with reason set."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "DEGRADED"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.DEGRADED
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_public_health_degraded_response_with_reason() -> None:
    """HTTP 200 + {"status": "DEGRADED", "reason": "DB slow"} → reason == "DB slow"."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "DEGRADED", "reason": "DB slow"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.DEGRADED
    assert result.reason == "DB slow"


@pytest.mark.unit
async def test_determine_api_public_health_unknown_status_is_down() -> None:
    """HTTP 200 + {"status": "UNKNOWN"} body → Health.DOWN."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "UNKNOWN"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_public_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
async def test_determine_api_authenticated_health_degraded_response() -> None:
    """HTTP 200 + {"status": "DEGRADED"} body → Health.DEGRADED with reason set."""
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mock_response.json.return_value = {"status": "DEGRADED"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with (
        patch("aignostics.platform._service.httpx.AsyncClient") as mock_cls,
        patch(_PATCH_AUTH_GETTER, return_value="test-token"),
    ):
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        result = await Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.DEGRADED
    assert result.reason is not None


@pytest.mark.unit
async def test_health_returns_both_components() -> None:
    """health() aggregates api_public and api_authenticated component keys."""
    public_health = Health(status=Health.Code.UP)
    auth_health = Health(status=Health.Code.UP)

    service = Service()
    with (
        patch.object(service, "_determine_api_public_health", new=AsyncMock(return_value=public_health)),
        patch.object(service, "_determine_api_authenticated_health", new=AsyncMock(return_value=auth_health)),
    ):
        result = await service.health()

    assert result.components is not None
    assert "api_public" in result.components
    assert "api_authenticated" in result.components
    assert result.components["api_public"] is public_health
    assert result.components["api_authenticated"] is auth_health


@pytest.mark.unit
@pytest.mark.parametrize(
    ("organization_name", "is_internal"),
    [
        ("Aignostics", True),
        ("Not Aignostics", False),
    ],
)
def test_user_info_identifies_internal_users(organization_name: str, is_internal: bool) -> None:
    """Test that UserInfo.is_internal_user returns True for internal orgs."""
    mock_org = MagicMock()
    mock_org.name = organization_name
    user_info = UserInfo.model_construct(  # use model_construct to bypass validation
        organization=mock_org,
    )
    assert user_info.is_internal_user is is_internal
