from unittest.mock import Mock

import pytest
from aignx.codegen.api.externals_api import ExternalsApi
from aignx.codegen.models import ApplicationVersionReadResponse
from aignx.codegen.models.application_read_response import ApplicationReadResponse

from aignostics.client.resources.applications import Applications, Versions


@pytest.fixture
def mock_api():
    return Mock(spec=ExternalsApi)


@pytest.fixture
def applications(mock_api):
    return Applications(mock_api)


# @pytest.mark.specifications("SAM-56")
# @pytest.mark.labels("custom-label")
@pytest.mark.requirements("SAM-2")
@pytest.mark.description(
    "Verifies that the applications list method returns an empty list when the API returns no applications"
)
def test_applications_list_returns_empty_list_when_no_applications(applications, mock_api):
    # Arrange
    mock_api.list_applications_v1_applications_get.return_value = []

    # Act
    result = applications.list()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
    mock_api.list_applications_v1_applications_get.assert_called_once()


def test_applications_list_returns_applications_when_available(applications, mock_api):
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


def test_applications_list_passes_through_api_exception(applications, mock_api):
    # Arrange
    mock_api.list_applications_v1_applications_get.side_effect = Exception("API error")

    # Act & Assert
    with pytest.raises(Exception, match="API error"):
        applications.list()
    mock_api.list_applications_v1_applications_get.assert_called_once()


def test_versions_property_returns_versions_instance(applications):
    # Act
    versions = applications.versions

    # Assert
    assert isinstance(versions, Versions)
    assert versions._api == applications._api


def test_versions_list_returns_versions_for_application(mock_api):
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


def test_versions_list_returns_empty_list_when_no_versions(mock_api):
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


def test_versions_list_passes_through_api_exception(mock_api):
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
