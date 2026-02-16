"""Tests for GUI frame module."""

import pytest

from aignostics.platform import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    API_ROOT_TEST,
    STATUS_PAGE_URL_DEV,
    STATUS_PAGE_URL_PRODUCTION,
    STATUS_PAGE_URL_STAGING,
    STATUS_PAGE_URL_TEST,
    Settings,
)


@pytest.mark.unit
def test_status_page_url_production(record_property) -> None:
    """Test that production environment has correct status page URL in settings.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SETTINGS")
    settings = Settings(api_root=API_ROOT_PRODUCTION)
    assert settings.status_page_url == STATUS_PAGE_URL_PRODUCTION
    assert settings.status_page_url == "https://status.platform.aignostics.com"


@pytest.mark.unit
def test_status_page_url_staging(record_property) -> None:
    """Test that staging environment has correct status page URL in settings.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SETTINGS")
    settings = Settings(api_root=API_ROOT_STAGING)
    assert settings.status_page_url == STATUS_PAGE_URL_STAGING
    assert settings.status_page_url == "https://status.platform-staging.aignostics.com"


@pytest.mark.unit
def test_status_page_url_dev(record_property) -> None:
    """Test that dev environment has no status page URL in settings.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SETTINGS")
    settings = Settings(api_root=API_ROOT_DEV)
    assert settings.status_page_url == STATUS_PAGE_URL_DEV
    assert settings.status_page_url is None


@pytest.mark.unit
def test_status_page_url_test(record_property) -> None:
    """Test that test environment has no status page URL in settings.

    Args:
        record_property: pytest record_property fixture
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SETTINGS")
    settings = Settings(api_root=API_ROOT_TEST)
    assert settings.status_page_url == STATUS_PAGE_URL_TEST
    assert settings.status_page_url is None


@pytest.mark.unit
def test_status_page_url_configurable(record_property, monkeypatch) -> None:
    """Test that status page URL can be explicitly configured via settings.

    Args:
        record_property: pytest record_property fixture
        monkeypatch: pytest monkeypatch fixture
    """
    record_property("tested-item-id", "SPEC-PLATFORM-SETTINGS")
    # Test that we can override the status page URL
    custom_url = "https://custom-status.example.com"
    monkeypatch.setenv("AIGNOSTICS_STATUS_PAGE_URL", custom_url)
    settings = Settings(api_root=API_ROOT_PRODUCTION)
    assert settings.status_page_url == custom_url

