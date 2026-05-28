"""Tests for the applications resource module.

This module contains unit tests for the Applications, Versions, and Documents
classes, verifying their functionality for listing applications, application
versions, and application version release documents.
"""

from datetime import UTC, datetime
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from aignx.codegen.exceptions import NotFoundException
from aignx.codegen.models.application_read_response import ApplicationReadResponse
from aignx.codegen.models.version_document_response import VersionDocumentResponse
from aignx.codegen.models.version_document_visibility import VersionDocumentVisibility

from aignostics_sdk.platform._api import _AuthenticatedApi
from aignostics_sdk.platform._operation_cache import operation_cache_clear
from aignostics_sdk.platform.resources.applications import (
    Applications,
    ApplicationVersionDocument,
    Documents,
    Versions,
)
from aignostics_sdk.platform.resources.utils import PAGE_SIZE

API_ERROR = "API error"
API_REASON_NOT_FOUND = "Not Found"

DOCUMENT_OUTPUT_DESCRIPTION_PDF = "output_description.pdf"
DOCUMENT_MISSING_PDF = "missing.pdf"
DOC_FILENAME_A = "a.pdf"
REQUESTS_GET_PATCH_TARGET = "aignostics.platform.resources.applications.requests.get"


@pytest.fixture
def mock_api() -> Mock:
    """Create a mock ExternalsApi object for testing.

    Returns:
        Mock: A mock instance of ExternalsApi.
    """
    api = Mock(spec=_AuthenticatedApi)
    api.token_provider = lambda: "test-token"
    api.api_client = Mock()
    return api


@pytest.fixture
def applications(mock_api) -> Applications:
    """Create an Applications instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Applications: An Applications instance using the mock API.
    """
    return Applications(mock_api)


@pytest.mark.unit
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
    # Check that calls were made with pagination parameters (ignore timeout/headers)
    calls = mock_api.list_applications_v1_applications_get.call_args_list
    assert calls[0].kwargs["page"] == 1
    assert calls[0].kwargs["page_size"] == PAGE_SIZE
    assert calls[1].kwargs["page"] == 2
    assert calls[1].kwargs["page_size"] == PAGE_SIZE


@pytest.mark.unit
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
    mock_api.list_applications_v1_applications_get.assert_called_once()
    call_kwargs = mock_api.list_applications_v1_applications_get.call_args.kwargs
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == PAGE_SIZE


@pytest.mark.unit
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
    mock_api.list_applications_v1_applications_get.assert_called_once()
    call_kwargs = mock_api.list_applications_v1_applications_get.call_args.kwargs
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == PAGE_SIZE


@pytest.mark.unit
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
    mock_api.list_applications_v1_applications_get.assert_called_once()
    call_kwargs = mock_api.list_applications_v1_applications_get.call_args.kwargs
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == PAGE_SIZE


@pytest.mark.unit
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


# ----------------------------------------------------------------------------------
# Documents resource tests
# ----------------------------------------------------------------------------------


def _make_doc(name: str = DOCUMENT_OUTPUT_DESCRIPTION_PDF) -> VersionDocumentResponse:
    """Build a VersionDocumentResponse codegen model for tests."""
    return VersionDocumentResponse(
        id="11111111-1111-1111-1111-111111111111",
        name=name,
        mime_type="application/pdf",
        visibility=VersionDocumentVisibility.PUBLIC,
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, 12, 0, tzinfo=UTC),
    )


@pytest.fixture(autouse=True)
def _clear_operation_cache_before_each_test() -> None:
    """Ensure the global operation cache does not leak between tests."""
    operation_cache_clear()


@pytest.fixture
def documents(mock_api: Mock) -> Documents:
    """Create a Documents instance bound to a fixed (application, version) pair.

    The mock is augmented with a minimal ``api_client.configuration`` so
    ``download_to_path`` can read host/proxy/SSL settings without hitting the
    real codegen plumbing.
    """
    configuration = MagicMock()
    configuration.host = "https://platform.example.com"
    configuration.proxy = None
    configuration.ssl_ca_cert = None
    configuration.verify_ssl = True
    configuration.token_provider = lambda: "test-token"
    mock_api.api_client = MagicMock()
    mock_api.api_client.configuration = configuration
    return Documents(mock_api, application_id="heta", application_version="1.0.0")


@pytest.mark.unit
def test_documents_list_returns_wrapped_models(documents: Documents, mock_api: Mock) -> None:
    """Documents.list() returns ApplicationVersionDocument instances."""
    mock_api.list_version_documents.return_value = [
        _make_doc(DOC_FILENAME_A),
        _make_doc("b.pdf"),
    ]

    result = documents.list()

    assert len(result) == 2
    assert all(isinstance(item, ApplicationVersionDocument) for item in result)
    assert {d.name for d in result} == {DOC_FILENAME_A, "b.pdf"}
    mock_api.list_version_documents.assert_called_once()
    call_kwargs = mock_api.list_version_documents.call_args.kwargs
    assert call_kwargs["application_id"] == "heta"
    assert call_kwargs["version"] == "1.0.0"


@pytest.mark.unit
def test_documents_list_returns_empty_list(documents: Documents, mock_api: Mock) -> None:
    """Documents.list() handles an empty response."""
    mock_api.list_version_documents.return_value = []

    result = documents.list()

    assert result == []


@pytest.mark.unit
def test_documents_list_uses_cache_then_bypasses_with_nocache(documents: Documents, mock_api: Mock) -> None:
    """list() caches results across calls; nocache=True forces a fresh call."""
    mock_api.list_version_documents.return_value = [_make_doc(DOC_FILENAME_A)]

    # First call hits the API and caches.
    documents.list()
    # Second call returns cached value.
    documents.list()
    assert mock_api.list_version_documents.call_count == 1

    # nocache=True bypasses the cache and re-fetches.
    documents.list(nocache=True)
    assert mock_api.list_version_documents.call_count == 2


@pytest.mark.unit
def test_documents_details_returns_wrapped_model(documents: Documents, mock_api: Mock) -> None:
    """Documents.details() wraps the response in ApplicationVersionDocument."""
    mock_api.get_version_document.return_value = _make_doc(DOCUMENT_OUTPUT_DESCRIPTION_PDF)

    result = documents.details(DOCUMENT_OUTPUT_DESCRIPTION_PDF)

    assert isinstance(result, ApplicationVersionDocument)
    assert result.name == DOCUMENT_OUTPUT_DESCRIPTION_PDF
    assert result.mime_type == "application/pdf"
    call_kwargs = mock_api.get_version_document.call_args.kwargs
    assert call_kwargs["application_id"] == "heta"
    assert call_kwargs["version"] == "1.0.0"
    assert call_kwargs["name"] == DOCUMENT_OUTPUT_DESCRIPTION_PDF


@pytest.mark.unit
def test_documents_details_propagates_not_found(documents: Documents, mock_api: Mock) -> None:
    """Documents.details() propagates a 404 NotFoundException from the codegen client."""
    mock_api.get_version_document.side_effect = NotFoundException(status=404, reason=API_REASON_NOT_FOUND)

    with pytest.raises(NotFoundException):
        documents.details(DOCUMENT_MISSING_PDF)


@pytest.mark.unit
def test_documents_download_to_path_writes_file(documents: Documents, tmp_path: Path) -> None:
    """download_to_path() follows the platform redirect and streams the body to disk."""
    body_response = MagicMock()
    body_response.status_code = HTTPStatus.OK
    body_response.iter_content.return_value = [b"hello ", b"world"]
    body_response.raise_for_status = MagicMock()
    body_response.__enter__.return_value = body_response
    body_response.__exit__.return_value = False

    with patch(
        REQUESTS_GET_PATCH_TARGET,
        return_value=body_response,
    ) as mock_get:
        result = documents.download_to_path(DOCUMENT_OUTPUT_DESCRIPTION_PDF, tmp_path)

    assert result == (tmp_path / DOCUMENT_OUTPUT_DESCRIPTION_PDF).resolve()
    assert result.read_bytes() == b"hello world"
    # Single request to the platform endpoint, requests follows the 307 internally.
    mock_get.assert_called_once()
    called_url = mock_get.call_args.args[0]
    assert called_url.endswith(
        f"/api/v1/applications/heta/versions/1.0.0/documents/{DOCUMENT_OUTPUT_DESCRIPTION_PDF}/file"
    )
    assert mock_get.call_args.kwargs["allow_redirects"] is True


@pytest.mark.unit
def test_documents_download_to_path_404_raises_not_found(documents: Documents, tmp_path: Path) -> None:
    """A 404 from the documents endpoint is mapped to NotFoundException."""
    response = MagicMock()
    response.status_code = HTTPStatus.NOT_FOUND
    response.reason = API_REASON_NOT_FOUND
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    with (
        patch(REQUESTS_GET_PATCH_TARGET, return_value=response),
        pytest.raises(NotFoundException),
    ):
        documents.download_to_path(DOCUMENT_MISSING_PDF, tmp_path)


@pytest.mark.unit
def test_documents_download_to_path_rejects_non_directory(documents: Documents, tmp_path: Path) -> None:
    """download_to_path() raises ValueError when destination is not an existing directory."""
    file_path = tmp_path / "some_file.pdf"
    file_path.write_bytes(b"content")

    with pytest.raises(ValueError, match="is an existing file"):
        documents.download_to_path(DOCUMENT_OUTPUT_DESCRIPTION_PDF, file_path)


@pytest.mark.unit
def test_documents_read_content_returns_bytes(documents: Documents) -> None:
    """read_content() follows the /content redirect and returns the body as bytes."""
    body_response = MagicMock()
    body_response.status_code = HTTPStatus.OK
    body_response.iter_content.return_value = [b"hello ", b"world"]
    body_response.raise_for_status = MagicMock()
    body_response.__enter__.return_value = body_response
    body_response.__exit__.return_value = False

    with patch(
        REQUESTS_GET_PATCH_TARGET,
        return_value=body_response,
    ) as mock_get:
        result = documents.read_content(DOCUMENT_OUTPUT_DESCRIPTION_PDF)

    assert result == b"hello world"
    mock_get.assert_called_once()
    called_url = mock_get.call_args.args[0]
    assert called_url.endswith(
        f"/api/v1/applications/heta/versions/1.0.0/documents/{DOCUMENT_OUTPUT_DESCRIPTION_PDF}/content"
    )
    assert mock_get.call_args.kwargs["allow_redirects"] is True


@pytest.mark.unit
def test_documents_read_content_404_raises_not_found(documents: Documents) -> None:
    """A 404 from the /content endpoint is mapped to NotFoundException."""
    response = MagicMock()
    response.status_code = HTTPStatus.NOT_FOUND
    response.reason = API_REASON_NOT_FOUND
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    with (
        patch(REQUESTS_GET_PATCH_TARGET, return_value=response),
        pytest.raises(NotFoundException),
    ):
        documents.read_content(DOCUMENT_MISSING_PDF)


@pytest.mark.unit
def test_versions_documents_returns_documents_resource(mock_api: Mock) -> None:
    """Versions.documents() returns a Documents instance bound to the version pair."""
    versions = Versions(mock_api)

    docs = versions.documents("heta", "1.0.0")

    assert isinstance(docs, Documents)
    assert docs.application_id == "heta"
    assert docs.application_version == "1.0.0"
    assert docs._api is mock_api


@pytest.mark.unit
def test_versions_documents_resolves_none_to_latest(mock_api: Mock) -> None:
    """Versions.documents(None) resolves to the latest version number."""
    from unittest.mock import patch

    from aignostics_sdk.platform.resources.applications import Versions as _Versions
    from aignostics_sdk.platform.resources.applications import VersionTuple

    latest = Mock(spec=VersionTuple)
    latest.number = "2.3.1"

    versions = _Versions(mock_api)
    with patch.object(versions, "latest", return_value=latest):
        docs = versions.documents("heta", None)

    assert isinstance(docs, Documents)
    assert docs.application_id == "heta"
    assert docs.application_version == "2.3.1"
