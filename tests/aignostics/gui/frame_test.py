"""Tests for GUI frame module."""

import pytest

from aignostics.gui._frame import get_status_page_url
from aignostics.platform import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    API_ROOT_TEST,
)


@pytest.mark.unit
def test_get_status_page_url_production(record_property) -> None:
    """Test that production environment returns correct status page URL.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-GUI-FRAME")
    url = get_status_page_url(API_ROOT_PRODUCTION)
    assert url == "https://status.platform.aignostics.com"


@pytest.mark.unit
def test_get_status_page_url_staging(record_property) -> None:
    """Test that staging environment returns correct status page URL.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-GUI-FRAME")
    url = get_status_page_url(API_ROOT_STAGING)
    assert url == "https://status.platform-staging.aignostics.com"


@pytest.mark.unit
def test_get_status_page_url_dev(record_property) -> None:
    """Test that dev environment returns None (no status page).

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-GUI-FRAME")
    url = get_status_page_url(API_ROOT_DEV)
    assert url is None


@pytest.mark.unit
def test_get_status_page_url_test(record_property) -> None:
    """Test that test environment returns None (no status page).

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-GUI-FRAME")
    url = get_status_page_url(API_ROOT_TEST)
    assert url is None


@pytest.mark.unit
def test_get_status_page_url_unknown(record_property) -> None:
    """Test that unknown environment returns None (no status page).

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-GUI-FRAME")
    url = get_status_page_url("https://custom.example.com")
    assert url is None
