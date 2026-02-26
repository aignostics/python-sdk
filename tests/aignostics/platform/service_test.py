"""Tests for the platform service module."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from aignostics.platform._service import Service, UserInfo
from aignostics.utils import Health

_PATCH_AUTH_GETTER = "aignostics.platform._service.get_token"


@pytest.mark.unit
def test_http_pool_is_shared() -> None:
    """Test that Service._get_http_pool returns the same instance across multiple calls.

    This ensures that all service instances share the same urllib3.PoolManager
    for efficient connection reuse.
    """
    # Get pool instance
    pool1 = Service._get_http_pool()

    # Get pool instance again (should return same instance)
    pool2 = Service._get_http_pool()

    # Verify both calls return the same instance
    assert pool1 is pool2, "Service._get_http_pool should return the same PoolManager instance"


@pytest.mark.unit
def test_http_pool_singleton() -> None:
    """Test that Service._http_pool maintains a singleton pattern.

    Multiple service instances should share the same connection pool.
    """
    # Create two service instances
    service1 = Service()
    service2 = Service()

    # Get pool from each service's perspective
    pool_from_service1 = service1._get_http_pool()
    pool_from_service2 = service2._get_http_pool()

    # Verify they share the same pool
    assert pool_from_service1 is pool_from_service2, "Service instances should share the same HTTP pool"


@pytest.mark.unit
def test_determine_api_authenticated_health_success() -> None:
    """Health.UP returned when the dedicated pool responds 200 with auth token."""
    mock_response = MagicMock()
    mock_response.status = HTTPStatus.OK

    mock_pool = MagicMock()
    mock_pool.request.return_value = mock_response

    with (
        patch.object(Service, "_get_http_pool", return_value=mock_pool),
        patch(_PATCH_AUTH_GETTER, return_value="test-token"),
    ):
        result = Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.UP


@pytest.mark.unit
def test_determine_api_authenticated_health_non_200() -> None:
    """Health.DOWN returned when the dedicated pool responds with non-200."""
    mock_response = MagicMock()
    mock_response.status = HTTPStatus.SERVICE_UNAVAILABLE

    mock_pool = MagicMock()
    mock_pool.request.return_value = mock_response

    with (
        patch.object(Service, "_get_http_pool", return_value=mock_pool),
        patch(_PATCH_AUTH_GETTER, return_value="test-token"),
    ):
        result = Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
def test_determine_api_authenticated_health_handles_exception() -> None:
    """Health.DOWN with reason when get_token raises."""
    with patch(_PATCH_AUTH_GETTER, side_effect=RuntimeError("no auth")):
        result = Service()._determine_api_authenticated_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
def test_determine_api_public_health_success() -> None:
    """Health.UP returned when the public pool responds 200."""
    mock_response = MagicMock()
    mock_response.status = HTTPStatus.OK

    mock_pool = MagicMock()
    mock_pool.request.return_value = mock_response

    with patch.object(Service, "_get_http_pool", return_value=mock_pool):
        result = Service()._determine_api_public_health()

    assert result.status == Health.Code.UP


@pytest.mark.unit
def test_determine_api_public_health_non_200() -> None:
    """Health.DOWN returned when the public pool responds with non-200."""
    mock_response = MagicMock()
    mock_response.status = HTTPStatus.SERVICE_UNAVAILABLE

    mock_pool = MagicMock()
    mock_pool.request.return_value = mock_response

    with patch.object(Service, "_get_http_pool", return_value=mock_pool):
        result = Service()._determine_api_public_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
def test_determine_api_public_health_handles_exception() -> None:
    """Health.DOWN returned when the public pool raises."""
    mock_pool = MagicMock()
    mock_pool.request.side_effect = ConnectionError("unreachable")

    with patch.object(Service, "_get_http_pool", return_value=mock_pool):
        result = Service()._determine_api_public_health()

    assert result.status == Health.Code.DOWN
    assert result.reason is not None


@pytest.mark.unit
def test_health_returns_both_components() -> None:
    """health() aggregates api_public and api_authenticated component keys."""
    public_health = Health(status=Health.Code.UP)
    auth_health = Health(status=Health.Code.UP)

    service = Service()
    with (
        patch.object(service, "_determine_api_public_health", return_value=public_health),
        patch.object(service, "_determine_api_authenticated_health", return_value=auth_health),
    ):
        result = service.health()

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
