"""Tests for the applications resource module.

This module contains unit tests for the Applications and Versions classes,
verifying their functionality for listing applications and application versions.
"""

from unittest.mock import Mock, call

import pytest
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import ApplicationVersionReadResponse
from aignx.codegen.models.application_read_response import ApplicationReadResponse

from aignostics.platform.resources.applications import Applications, Versions
from aignostics.platform.resources.utils import PAGE_SIZE

API_ERROR = "API error"


@pytest.fixture
def mock_api() -> Mock:
    """Create a mock ExternalsApi object for testing.

    Returns:
        Mock: A mock instance of ExternalsApi.
    """
    return Mock(spec=PublicApi)


@pytest.fixture
def applications(mock_api) -> Applications:
    """Create an Applications instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Applications: An Applications instance using the mock API.
    """
    return Applications(mock_api)


def test_applications_list_with_pagination(applications, mock_api) -> None:
    """Test that Applications.list() correctly handles pagination.

    This test verifies that the list method properly aggregates results
    from multiple paginated API responses.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    # Create two pages of results
    page1 = [Mock(spec=ApplicationReadResponse) for _ in range(PAGE_SIZE)]
    page2 = [Mock(spec=ApplicationReadResponse) for _ in range(5)]  # Partial page
    mock_api.list_applications_v1_applications_get.side_effect = [page1, page2]

    # Act
    result = list(applications.list())

    # Assert
    assert len(result) == PAGE_SIZE + 5
    assert mock_api.list_applications_v1_applications_get.call_count == 2
    mock_api.list_applications_v1_applications_get.assert_has_calls([
        call(page=1, page_size=PAGE_SIZE),
        call(page=2, page_size=PAGE_SIZE),
    ])


def test_versions_list_with_pagination(mock_api) -> None:
    """Test that Versions.list() correctly handles pagination.

    This test verifies that the list method for application versions properly
    aggregates results from multiple paginated API responses.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"

    # Create two pages of results
    page1 = [Mock(spec=ApplicationVersionReadResponse) for _ in range(PAGE_SIZE)]
    page2 = [Mock(spec=ApplicationVersionReadResponse) for _ in range(5)]  # Partial page

    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.side_effect = [page1, page2]

    # Act
    result = list(versions.list(application=mock_app))

    # Assert
    assert len(result) == PAGE_SIZE + 5
    assert mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.call_count == 2
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.assert_has_calls([
        call(application_id=mock_app.application_id, page=1, page_size=PAGE_SIZE),
        call(application_id=mock_app.application_id, page=2, page_size=PAGE_SIZE),
    ])


def test_applications_list_returns_empty_list_when_no_applications(applications, mock_api) -> None:
    """Test that Applications.list() returns an empty list when no applications are available.

    This test verifies that the list method handles empty API responses correctly.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_applications_v1_applications_get.return_value = []

    # Act
    result = list(applications.list())

    # Assert
    assert len(result) == 0
    mock_api.list_applications_v1_applications_get.assert_called_once_with(page=1, page_size=PAGE_SIZE)


def test_applications_list_returns_applications_when_available(applications, mock_api) -> None:
    """Test that Applications.list() returns a list of applications when available.

    This test verifies that the list method correctly returns application objects
    from the API response.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_app1 = Mock(spec=ApplicationReadResponse)
    mock_app2 = Mock(spec=ApplicationReadResponse)
    mock_api.list_applications_v1_applications_get.return_value = [mock_app1, mock_app2]

    # Act
    result = list(applications.list())

    # Assert
    assert len(result) == 2
    assert result[0] == mock_app1
    assert result[1] == mock_app2
    mock_api.list_applications_v1_applications_get.assert_called_once_with(page=1, page_size=PAGE_SIZE)


def test_applications_list_passes_through_api_exception(applications, mock_api) -> None:
    """Test that Applications.list() passes through exceptions from the API.

    This test verifies that exceptions raised by the API client are propagated
    to the caller without being caught or modified.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_applications_v1_applications_get.side_effect = Exception(API_ERROR)

    # Act & Assert
    with pytest.raises(Exception, match=API_ERROR):
        list(applications.list())
    mock_api.list_applications_v1_applications_get.assert_called_once_with(page=1, page_size=PAGE_SIZE)


def test_versions_property_returns_versions_instance(applications) -> None:
    """Test that the versions property returns a Versions instance.

    This test verifies that the versions property correctly initializes
    and returns a Versions instance with the same API client.

    Args:
        applications: Applications instance with mock API.
    """
    # Act
    versions = applications.versions

    # Assert
    assert isinstance(versions, Versions)
    assert versions._api == applications._api


def test_versions_list_returns_versions_for_application(mock_api) -> None:
    """Test that Versions.list() returns versions for a specified application.

    This test verifies that the list method correctly returns version objects
    for a given application from the API response.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"
    mock_version = Mock(spec=ApplicationVersionReadResponse)
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.return_value = [mock_version]

    # Act
    result = list(versions.list(application=mock_app))

    # Assert
    assert len(result) == 1
    assert result[0] == mock_version
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.assert_called_once_with(
        application_id=mock_app.application_id, page=1, page_size=PAGE_SIZE
    )


def test_versions_list_returns_empty_list_when_no_versions(mock_api) -> None:
    """Test that Versions.list() returns an empty list when no versions are available.

    This test verifies that the list method handles empty API responses correctly
    when requesting application versions.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.return_value = []

    # Act
    result = list(versions.list(application=mock_app))

    # Assert
    assert len(result) == 0
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.assert_called_once_with(
        application_id=mock_app.application_id, page=1, page_size=PAGE_SIZE
    )


def test_versions_list_passes_through_api_exception(mock_api) -> None:
    """Test that Versions.list() passes through exceptions from the API.

    This test verifies that exceptions raised by the API client when requesting
    application versions are propagated to the caller without being caught or modified.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.side_effect = Exception(
        API_ERROR
    )

    # Act & Assert
    with pytest.raises(Exception, match=API_ERROR):
        list(versions.list(application=mock_app))
