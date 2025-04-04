"""Tests for the applications resource module.

This module contains unit tests for the Applications and Versions classes,
verifying their functionality for listing applications and application versions.
"""

from unittest.mock import Mock

import pytest
from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.models import ApplicationVersionReadResponse
from aignx.codegen.models.application_read_response import ApplicationReadResponse

from aignostics.client.resources.applications import Applications, Versions


@pytest.fixture
def mock_api() -> Mock:
    """Create a mock ExternalsApi object for testing.

    Returns:
        Mock: A mock instance of ExternalsApi.
    """
    return Mock(spec=ExternalsApi)


@pytest.fixture
def applications(mock_api) -> Applications:
    """Create an Applications instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Applications: An Applications instance using the mock API.
    """
    return Applications(mock_api)


def test_applications_list_returns_empty_list_when_no_applications(applications, mock_api) -> None:
    """Test that Applications.list() returns an empty list when no applications are available.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_applications_v1_applications_get.return_value = []

    # Act
    result = applications.list()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
    mock_api.list_applications_v1_applications_get.assert_called_once()


def test_applications_list_returns_applications_when_available(applications, mock_api) -> None:
    """Test that Applications.list() returns a list of applications when available.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_app1 = Mock(spec=ApplicationReadResponse)
    mock_app2 = Mock(spec=ApplicationReadResponse)
    mock_api.list_applications_v1_applications_get.return_value = [mock_app1, mock_app2]

    # Act
    result = applications.list()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == mock_app1
    assert result[1] == mock_app2
    mock_api.list_applications_v1_applications_get.assert_called_once()


def test_applications_list_passes_through_api_exception(applications, mock_api) -> None:
    """Test that Applications.list() passes through exceptions from the API.

    Args:
        applications: Applications instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_applications_v1_applications_get.side_effect = Exception("API error")

    # Act & Assert
    with pytest.raises(Exception, match="API error"):
        applications.list()
    mock_api.list_applications_v1_applications_get.assert_called_once()


def test_versions_property_returns_versions_instance(applications) -> None:
    """Test that the versions property returns a Versions instance.

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
    result = versions.list(for_application=mock_app)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == mock_version
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.assert_called_once_with(
        application_id=mock_app.application_id
    )


def test_versions_list_returns_empty_list_when_no_versions(mock_api) -> None:
    """Test that Versions.list() returns an empty list when no versions are available.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.return_value = []

    # Act
    result = versions.list(for_application=mock_app)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.assert_called_once_with(
        application_id=mock_app.application_id
    )


def test_versions_list_passes_through_api_exception(mock_api) -> None:
    """Test that Versions.list() passes through exceptions from the API.

    Args:
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    versions = Versions(mock_api)
    mock_app = Mock(spec=ApplicationReadResponse)
    mock_app.application_id = "test-app-id"
    mock_api.list_versions_by_application_id_v1_applications_application_id_versions_get.side_effect = Exception(
        "API error"
    )

    # Act & Assert
    with pytest.raises(Exception, match="API error"):
        versions.list(for_application=mock_app)
