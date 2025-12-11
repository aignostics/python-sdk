"""Tests for the platform service module."""

from unittest.mock import MagicMock

import pytest

from aignostics.platform._service import Service, UserInfo


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
