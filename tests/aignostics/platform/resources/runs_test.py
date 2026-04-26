"""Tests for the runs resource module.

This module contains unit tests for the Runs class and Run class,
verifying their functionality for listing, creating, and managing application runs.
"""

from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.exceptions import ApiException, NotFoundException, ServiceException
from aignx.codegen.models import (
    InputArtifactCreationRequest,
    ItemCreationRequest,
    ItemResultReadResponse,
    RunCreationResponse,
    RunReadResponse,
)

from aignostics.platform.resources.runs import LIST_APPLICATION_RUNS_MAX_PAGE_SIZE, Artifact, Run, Runs
from aignostics.platform.resources.utils import PAGE_SIZE

_PLATFORM_HOST = "https://platform-staging.aignostics.com"
_RUN_ID = "test-run-id"
_ARTIFACT_ID = "artifact-123"
_PRESIGNED_URL = "https://storage.googleapis.com/bucket/file?sig=abc123"
_PATCH_REQUESTS_GET = "aignostics.platform.resources.runs.requests.get"
_PATCH_GET_TOKEN = "aignostics.platform.resources.runs.get_token"  # noqa: S105 (mock target string, not a credential)
_PATCH_SETTINGS = "aignostics.platform.resources.runs.settings"


@pytest.fixture
def mock_api() -> Mock:
    """Create a mock ExternalsApi object for testing.

    Returns:
        Mock: A mock instance of ExternalsApi.
    """
    return Mock(spec=PublicApi)


@pytest.fixture
def runs(mock_api) -> Runs:
    """Create a Runs instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Runs: A Runs instance using the mock API.
    """
    return Runs(mock_api)


@pytest.fixture
def app_run(mock_api) -> Run:
    """Create an Run instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Run: An Run instance using the mock API.
    """
    return Run(mock_api, _RUN_ID)


@pytest.fixture
def configured_api(mock_api) -> Mock:
    """Wire a Mock API client to expose a `configuration` matching real codegen shape.

    Returns:
        Mock: The same `mock_api` fixture, with `api_client.configuration`
            populated with `host`, `proxy`, `ssl_ca_cert`, `verify_ssl`.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.proxy = None
    mock_api.api_client.configuration.ssl_ca_cert = None
    mock_api.api_client.configuration.verify_ssl = True
    return mock_api


@pytest.fixture
def artifact(configured_api) -> Artifact:
    """Create an Artifact instance bound to a configured mock API."""
    return Artifact(configured_api, _RUN_ID, _ARTIFACT_ID)


def _redirect_response(location: str | None, status: int = HTTPStatus.TEMPORARY_REDIRECT) -> MagicMock:
    """Build a context-manager-shaped Mock response with the given status + Location."""
    response = MagicMock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.status_code = status
    response.headers = {"Location": location} if location is not None else {}
    response.reason = HTTPStatus(status).phrase or "Unknown"
    return response


def _error_response(status: int) -> MagicMock:
    """Build a context-manager-shaped Mock response with the given non-redirect status."""
    response = MagicMock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.status_code = status
    response.headers = {}
    response.reason = HTTPStatus(status).phrase
    return response


@pytest.mark.unit
def test_runs_list_with_pagination(runs, mock_api) -> None:
    """Test that Runs.list() correctly handles pagination.

    This test verifies that the list method properly aggregates results from
    multiple paginated API responses and converts them to Run instances.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    # Since list() now uses LIST_APPLICATION_RUNS_MAX_PAGE_SIZE, adjust expectations
    page1 = [Mock(spec=RunReadResponse, run_id=f"run-{i}") for i in range(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE)]
    page2 = [Mock(spec=RunReadResponse, run_id=f"run-{i + LIST_APPLICATION_RUNS_MAX_PAGE_SIZE}") for i in range(5)]
    mock_api.list_runs_v1_runs_get.side_effect = [page1, page2]

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE + 5
    assert all(isinstance(run, Run) for run in result)
    assert mock_api.list_runs_v1_runs_get.call_count == 2
    # Check that the calls were made with the expected parameters (ignoring _request_timeout and _headers)
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["page"] == 1
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["application_id"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["application_version"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["page"] == 2
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["application_id"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["application_version"] is None


@pytest.mark.unit
def test_runs_list_with_application_version_filter(runs, mock_api) -> None:
    """Test that Runs.list() correctly filters by application version.

    This test verifies that the application version filter parameter is
    correctly passed to the API client.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    app_id = "test-app"
    app_version = "version"
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(application_id=app_id, application_version=app_version))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["application_id"] == app_id
    assert call_kwargs["application_version"] == app_version
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE


@pytest.mark.unit
def test_application_run_results_with_pagination(app_run, mock_api) -> None:
    """Test that Run.results() correctly handles pagination.

    This test verifies that the results method properly aggregates results
    from multiple paginated API responses when requesting run results.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    page1 = [Mock(spec=ItemResultReadResponse) for _ in range(PAGE_SIZE)]
    page2 = [Mock(spec=ItemResultReadResponse) for _ in range(5)]
    mock_api.list_run_items_v1_runs_run_id_items_get.side_effect = [page1, page2]

    # Act
    result = list(app_run.results())

    # Assert
    assert len(result) == PAGE_SIZE + 5
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_count == 2
    # Check that the calls were made with the expected parameters (ignoring _request_timeout and _headers)
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[0][1]["run_id"] == app_run.run_id
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[0][1]["page"] == 1
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[0][1]["page_size"] == PAGE_SIZE
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[1][1]["run_id"] == app_run.run_id
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[1][1]["page"] == 2
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list[1][1]["page_size"] == PAGE_SIZE


@pytest.mark.unit
def test_runs_call_returns_application_run(runs) -> None:
    """Test that Runs.__call__() returns an Run instance.

    This test verifies that calling the Runs instance as a function correctly
    initializes and returns an Run instance with the specified run ID.

    Args:
        runs: Runs instance with mock API.
    """
    # Act
    run_id = "test-run-id"
    app_run = runs(run_id)

    # Assert
    assert isinstance(app_run, Run)
    assert app_run.run_id == run_id
    assert app_run._api == runs._api


@pytest.mark.unit
def test_runs_submit_returns_application_run(runs, mock_api) -> None:
    """Test that Runs.submit() returns an Run instance.

    This test verifies that the submit method correctly calls the API client
    to submit a new run and returns an Run instance for the submitted run.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    run_id = "new-run-id"
    mock_items = [
        ItemCreationRequest(
            external_id="item-1",
            input_artifacts=[
                InputArtifactCreationRequest(name="artifact-1", download_url="url", metadata={"key": "value"})
            ],
        )
    ]
    mock_api.create_run_v1_runs_post.return_value = RunCreationResponse(run_id=run_id)

    # Mock the validation method to prevent it from making actual API calls
    runs._validate_input_items = Mock()

    # Act
    app_run = runs.submit(application_id="test", items=mock_items, application_version="1.0.0")

    # Assert
    assert isinstance(app_run, Run)
    assert app_run.run_id == run_id
    mock_api.create_run_v1_runs_post.assert_called_once()
    # Check that a RunCreationRequest was passed to the API call
    call_args = mock_api.create_run_v1_runs_post.call_args[0][0]
    assert call_args.application_id == "test"
    assert call_args.items == mock_items
    assert call_args.version_number == "1.0.0"


@pytest.mark.unit
def test_paginate_with_not_found_exception_on_first_page(runs, mock_api) -> None:
    """Test that paginate handles NotFoundException on the first page gracefully.

    This test verifies that when a NotFoundException is raised on the first page request,
    the paginate function returns an empty iterator without error.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    from aignx.codegen.exceptions import NotFoundException

    # Make the API throw NotFoundException on the first call
    mock_api.list_runs_v1_runs_get.side_effect = NotFoundException()

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == 0
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert call_kwargs["application_id"] is None
    assert call_kwargs["application_version"] is None


@pytest.mark.unit
def test_paginate_with_not_found_exception_after_full_page(runs, mock_api) -> None:
    """Test that paginate handles NotFoundException after a full page.

    This test verifies that when we get exactly LIST_APPLICATION_RUNS_MAX_PAGE_SIZE items on the first page
    and then a NotFoundException on the second page, we correctly return just the
    first page's items.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    from aignx.codegen.exceptions import NotFoundException

    # Return exactly LIST_APPLICATION_RUNS_MAX_PAGE_SIZE items for first page, then throw NotFoundException
    full_page = [Mock(spec=RunReadResponse, run_id=f"run-{i}") for i in range(LIST_APPLICATION_RUNS_MAX_PAGE_SIZE)]
    mock_api.list_runs_v1_runs_get.side_effect = [full_page, NotFoundException()]

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert mock_api.list_runs_v1_runs_get.call_count == 2
    # Check that the calls were made with the expected parameters (ignoring _request_timeout and _headers)
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["page"] == 1
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["application_id"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[0][1]["application_version"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["page"] == 2
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["application_id"] is None
    assert mock_api.list_runs_v1_runs_get.call_args_list[1][1]["application_version"] is None


@pytest.mark.unit
def test_runs_list_with_external_id_filter(runs, mock_api) -> None:
    """Test that Runs.list() correctly filters by external ID.

    This test verifies that the external_id filter parameter is
    correctly passed to the API client.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    external_id = "test-external-id"
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(external_id=external_id))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["external_id"] == external_id
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE


@pytest.mark.unit
def test_runs_list_with_custom_metadata_filter(runs, mock_api) -> None:
    """Test that Runs.list() correctly filters by custom metadata.

    This test verifies that the custom_metadata filter parameter in JSONPath format
    is correctly passed to the API client.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    custom_metadata = "$.experiment_id=='exp-123'"
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(custom_metadata=custom_metadata))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["custom_metadata"] == custom_metadata
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE


@pytest.mark.unit
def test_runs_list_with_sort_ascending(runs, mock_api) -> None:
    """Test that Runs.list() correctly applies ascending sort.

    This test verifies that the sort parameter for ascending order
    is correctly passed to the API client as a list.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    sort_field = "created_at"
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(sort=sort_field))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["sort"] == [sort_field]
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE


@pytest.mark.unit
def test_runs_list_with_descending_sort(runs, mock_api) -> None:
    """Test that Runs.list() correctly applies descending sort.

    This test verifies that the sort parameter with '-' prefix for descending order
    is correctly passed to the API client as a list.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    sort_field = "-created_at"
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(sort=sort_field))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["sort"] == [sort_field]
    assert call_kwargs["page"] == 1
    assert call_kwargs["page_size"] == LIST_APPLICATION_RUNS_MAX_PAGE_SIZE


@pytest.mark.unit
def test_runs_list_with_custom_page_size(runs, mock_api) -> None:
    """Test that Runs.list() correctly uses custom page size.

    This test verifies that a custom page_size parameter is correctly
    passed to the paginate function and API client.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    custom_page_size = 50
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(page_size=custom_page_size))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["page_size"] == custom_page_size
    assert call_kwargs["page"] == 1


@pytest.mark.unit
def test_runs_list_with_page_size_exceeding_max_raises_error(runs, mock_api) -> None:
    """Test that Runs.list() raises ValueError when page_size exceeds maximum.

    This test verifies that attempting to use a page_size greater than the
    maximum allowed value (100) raises a ValueError.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    invalid_page_size = 101

    # Act & Assert
    with pytest.raises(ValueError, match="page_size is must be less than or equal to 100"):
        list(runs.list(page_size=invalid_page_size))

    # Verify API was never called
    mock_api.list_runs_v1_runs_get.assert_not_called()


@pytest.mark.unit
def test_runs_list_with_all_filters_combined(runs, mock_api) -> None:
    """Test that Runs.list() correctly combines all filter parameters.

    This test verifies that all filter parameters (application_id, application_version,
    for_organization, external_id, custom_metadata, sort, page_size) work together correctly.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    app_id = "test-app"
    app_version = "1.0.0"
    org_id = "org-789"
    external_id = "ext-123"
    custom_metadata = "$.experiment=='test'"
    sort_field = "-created_at"
    page_size = 25
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(
        runs.list(
            application_id=app_id,
            application_version=app_version,
            for_organization=org_id,
            external_id=external_id,
            custom_metadata=custom_metadata,
            sort=sort_field,
            page_size=page_size,
        )
    )

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["application_id"] == app_id
    assert call_kwargs["application_version"] == app_version
    assert call_kwargs["for_organization"] == org_id
    assert call_kwargs["external_id"] == external_id
    assert call_kwargs["custom_metadata"] == custom_metadata
    assert call_kwargs["sort"] == [sort_field]
    assert call_kwargs["page_size"] == page_size
    assert call_kwargs["page"] == 1


@pytest.mark.unit
def test_runs_list_with_nocache_true(runs, mock_api) -> None:
    """Test that Runs.list() respects the nocache parameter.

    This test verifies that the nocache parameter is correctly passed through
    to list_data (nocache is handled by the caching decorator, not passed to API).

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(nocache=True))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    # nocache is handled by caching decorator, not passed to API
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert "nocache" not in call_kwargs


@pytest.mark.unit
def test_runs_list_with_none_sort_not_passed_as_list(runs, mock_api) -> None:
    """Test that Runs.list() doesn't wrap None sort in a list.

    This test verifies that when sort is None, it's passed as None
    rather than [None] to the API.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    mock_api.list_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(sort=None))

    # Assert
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["sort"] is None


@pytest.mark.unit
def test_runs_list_delegates_to_list_data(runs, mock_api) -> None:
    """Test that Runs.list() correctly delegates to list_data() and wraps results.

    This test verifies that list() calls list_data() with all parameters
    and converts RunData objects to Run objects.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    app_id = "test-app"
    app_version = "1.0.0"
    external_id = "ext-123"
    custom_metadata = "$.test=='value'"
    sort_field = "-created_at"
    page_size = 25

    # Create mock RunData responses
    mock_responses = [Mock(spec=RunReadResponse, run_id=f"run-{i}") for i in range(3)]
    mock_api.list_runs_v1_runs_get.return_value = mock_responses

    # Act
    result = list(
        runs.list(
            application_id=app_id,
            application_version=app_version,
            external_id=external_id,
            custom_metadata=custom_metadata,
            sort=sort_field,
            page_size=page_size,
            nocache=True,
        )
    )

    # Assert
    # Verify we got Run objects with correct run_ids
    assert len(result) == 3
    assert all(isinstance(run, Run) for run in result)
    assert [run.run_id for run in result] == ["run-0", "run-1", "run-2"]

    # Verify all parameters were passed to the API
    mock_api.list_runs_v1_runs_get.assert_called_once()
    call_kwargs = mock_api.list_runs_v1_runs_get.call_args[1]
    assert call_kwargs["application_id"] == app_id
    assert call_kwargs["application_version"] == app_version
    assert call_kwargs["external_id"] == external_id
    assert call_kwargs["custom_metadata"] == custom_metadata
    assert call_kwargs["sort"] == [sort_field]
    assert call_kwargs["page_size"] == page_size
    # nocache is handled by caching decorator, not passed to API
    assert "nocache" not in call_kwargs


@pytest.mark.unit
def test_application_run_results_with_filters(app_run, mock_api) -> None:
    """Test that Run.results() correctly maps item_ids and external_ids to API parameters.

    Verifies that:
    - item_ids maps to item_id__in
    - external_ids maps to external_id__in
    """
    # Arrange
    item_ids = ["item-1", "item-2"]
    external_ids = ["ext-1", "ext-2"]
    page1 = [Mock(spec=ItemResultReadResponse) for _ in range(PAGE_SIZE)]
    page2 = [Mock(spec=ItemResultReadResponse) for _ in range(3)]
    mock_api.list_run_items_v1_runs_run_id_items_get.side_effect = [page1, page2]

    # Act
    result = list(app_run.results(item_ids=item_ids, external_ids=external_ids))

    # Assert - filters are passed and pagination still works
    assert len(result) == PAGE_SIZE + 3
    assert mock_api.list_run_items_v1_runs_run_id_items_get.call_count == 2
    for call in mock_api.list_run_items_v1_runs_run_id_items_get.call_args_list:
        call_kwargs = call[1]
        assert call_kwargs["item_id__in"] == item_ids
        assert call_kwargs["external_id__in"] == external_ids
        assert call_kwargs["run_id"] == app_run.run_id


@pytest.mark.unit
def test_application_run_results_without_filters_omits_filter_kwargs(app_run, mock_api) -> None:
    """Test that Run.results() does not pass filter kwargs when no filters are provided."""
    # Arrange
    mock_api.list_run_items_v1_runs_run_id_items_get.return_value = []

    # Act
    list(app_run.results())

    # Assert
    call_kwargs = mock_api.list_run_items_v1_runs_run_id_items_get.call_args[1]
    assert "item_id__in" not in call_kwargs
    assert "external_id__in" not in call_kwargs


@pytest.mark.unit
def test_application_run_results_with_empty_list_filters_omits_filter_kwargs(app_run, mock_api) -> None:
    """Test that Run.results() treats empty lists same as None (no filter applied)."""
    # Arrange
    mock_api.list_run_items_v1_runs_run_id_items_get.return_value = []

    # Act - empty lists should behave like None
    list(app_run.results(item_ids=[], external_ids=[]))

    # Assert - filter kwargs should NOT be present
    call_kwargs = mock_api.list_run_items_v1_runs_run_id_items_get.call_args[1]
    assert "item_id__in" not in call_kwargs
    assert "external_id__in" not in call_kwargs


@pytest.mark.unit
@pytest.mark.parametrize(
    ("hide_platform_queue_position", "expected_platform_queue_position"),
    [
        (True, None),
        (False, 100),
    ],
)
def test_run_details_can_hide_platform_queue_position(
    app_run,
    mock_api,
    hide_platform_queue_position: bool,
    expected_platform_queue_position: int | None,
) -> None:
    """Test that Run.details handles hide_platform_queue_position correctly."""
    run_data = RunReadResponse.model_construct(
        num_preceding_items_org=5,
        num_preceding_items_platform=100,
    )
    mock_api.get_run_v1_runs_run_id_get.return_value = run_data
    result = app_run.details(hide_platform_queue_position=hide_platform_queue_position)
    assert result.num_preceding_items_org == run_data.num_preceding_items_org
    assert result.num_preceding_items_platform == expected_platform_queue_position


@pytest.mark.unit
def test_run_details_retries_on_not_found_then_succeeds(app_run, mock_api) -> None:
    """Test that Run.details retries on NotFoundException and succeeds when the run becomes available.

    This verifies the outer retry logic that handles read replica lag by retrying
    NotFoundException until the run is found.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    from aignx.codegen.exceptions import NotFoundException

    run_data = RunReadResponse.model_construct(run_id="test-run-id")
    mock_api.get_run_v1_runs_run_id_get.side_effect = [
        NotFoundException(),
        NotFoundException(),
        run_data,
    ]

    result = app_run.details()

    assert result.run_id == "test-run-id"
    assert mock_api.get_run_v1_runs_run_id_get.call_count == 3


@pytest.mark.unit
def test_run_details_raises_not_found_after_timeout(app_run, mock_api) -> None:
    """Test that Run.details re-raises NotFoundException after the retry timeout expires.

    This verifies that the outer retry gives up after the configured delay and
    surfaces the NotFoundException to the caller.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    from aignx.codegen.exceptions import NotFoundException

    mock_api.get_run_v1_runs_run_id_get.side_effect = NotFoundException()

    with pytest.raises(NotFoundException):
        app_run.details()

    assert mock_api.get_run_v1_runs_run_id_get.call_count > 1


@pytest.mark.unit
def test_run_details_does_not_retry_other_exceptions(app_run, mock_api) -> None:
    """Test that the outer retry does not catch non-NotFoundException errors.

    This verifies that exceptions like ForbiddenException pass straight through
    the outer retry without being retried.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    from aignx.codegen.exceptions import ForbiddenException

    mock_api.get_run_v1_runs_run_id_get.side_effect = ForbiddenException()

    with pytest.raises(ForbiddenException):
        app_run.details()

    assert mock_api.get_run_v1_runs_run_id_get.call_count == 1


# ---------------------------------------------------------------------------
# Artifact / Run.get_artifact_download_url
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "redirect_status",
    [
        HTTPStatus.MOVED_PERMANENTLY,
        HTTPStatus.FOUND,
        HTTPStatus.TEMPORARY_REDIRECT,
        HTTPStatus.PERMANENT_REDIRECT,
    ],
)
def test_artifact_get_download_url_returns_location_for_any_redirect(artifact, redirect_status) -> None:
    """Any 3xx redirect status with a Location header yields the presigned URL.

    The /file endpoint contractually returns 307, but the SDK accepts every
    well-known redirect status so the SDK keeps working if the API ever flips
    one for cache reasons.
    """
    response = _redirect_response(_PRESIGNED_URL, status=redirect_status)

    with (
        patch(_PATCH_GET_TOKEN, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=response) as mock_get,
    ):
        url = artifact.get_download_url()

    assert url == _PRESIGNED_URL
    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == f"{_PLATFORM_HOST}/api/v1/runs/{_RUN_ID}/artifacts/{_ARTIFACT_ID}/file"
    assert mock_get.call_args.kwargs["allow_redirects"] is False
    assert mock_get.call_args.kwargs["stream"] is True
    assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
    assert "User-Agent" in mock_get.call_args.kwargs["headers"]


@pytest.mark.unit
def test_artifact_get_download_url_strips_trailing_slash_from_host(configured_api) -> None:
    """Trailing slash on configuration.host must not produce a `//api/v1/...` URL."""
    configured_api.api_client.configuration.host = f"{_PLATFORM_HOST}/"
    art = Artifact(configured_api, _RUN_ID, _ARTIFACT_ID)
    response = _redirect_response(_PRESIGNED_URL)

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=response) as mock_get,
    ):
        art.get_download_url()

    assert mock_get.call_args.args[0] == f"{_PLATFORM_HOST}/api/v1/runs/{_RUN_ID}/artifacts/{_ARTIFACT_ID}/file"


@pytest.mark.unit
def test_artifact_get_download_url_redirect_without_location_raises(artifact) -> None:
    """A 3xx response with no Location header is an SDK-level RuntimeError.

    Bypassing the codegen means we own the redirect contract; this asserts we
    fail loudly instead of returning None/empty string.
    """
    response = _redirect_response(location=None, status=HTTPStatus.TEMPORARY_REDIRECT)

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=response),
        pytest.raises(RuntimeError, match="missing Location header"),
    ):
        artifact.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_404_raises_not_found(artifact) -> None:
    """404 from the /file endpoint maps to NotFoundException (codegen-style)."""
    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=_error_response(HTTPStatus.NOT_FOUND)),
        pytest.raises(NotFoundException),
    ):
        artifact.get_download_url()


@pytest.mark.unit
@pytest.mark.parametrize(
    "client_status",
    [HTTPStatus.FORBIDDEN, HTTPStatus.GONE, HTTPStatus.UNPROCESSABLE_ENTITY],
)
def test_artifact_get_download_url_4xx_raises_api_exception(artifact, client_status) -> None:
    """4xx responses other than 404 surface as ApiException with the original status.

    Includes 410 because the API contract says deleted artifacts return 410 Gone.
    """
    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=_error_response(client_status)),
        pytest.raises(ApiException) as exc_info,
    ):
        artifact.get_download_url()
    assert exc_info.value.status == client_status


@pytest.mark.unit
def test_artifact_get_download_url_unexpected_2xx_raises_runtime(artifact) -> None:
    """A 200 (or other unexpected non-error, non-redirect) is RuntimeError.

    Per Dima's clarification on PR #478: the endpoint never returns 200 in
    practice. If it ever does, we fail explicitly rather than silently passing
    a body off to webbrowser.open().
    """
    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=_error_response(HTTPStatus.OK)),
        pytest.raises(RuntimeError, match="Unexpected status 200"),
    ):
        artifact.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_5xx_retries_then_succeeds(artifact) -> None:
    """A transient 5xx is retried; once it succeeds the presigned URL is returned."""
    error = _error_response(HTTPStatus.SERVICE_UNAVAILABLE)
    success = _redirect_response(_PRESIGNED_URL)

    fake_settings = Mock()
    fake_settings.run_retry_attempts = 3
    fake_settings.run_retry_wait_min = 0.0
    fake_settings.run_retry_wait_max = 0.0
    fake_settings.run_timeout = 5.0

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_SETTINGS, return_value=fake_settings),
        patch(_PATCH_REQUESTS_GET, side_effect=[error, success]) as mock_get,
    ):
        url = artifact.get_download_url()

    assert url == _PRESIGNED_URL
    assert mock_get.call_count == 2  # one retry was needed


@pytest.mark.unit
def test_artifact_get_download_url_5xx_exhausts_retries_then_raises(artifact) -> None:
    """If 5xx persists for all retry attempts, ServiceException is reraised."""
    fake_settings = Mock()
    fake_settings.run_retry_attempts = 2
    fake_settings.run_retry_wait_min = 0.0
    fake_settings.run_retry_wait_max = 0.0
    fake_settings.run_timeout = 5.0

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_SETTINGS, return_value=fake_settings),
        patch(
            _PATCH_REQUESTS_GET,
            return_value=_error_response(HTTPStatus.SERVICE_UNAVAILABLE),
        ) as mock_get,
        pytest.raises(ServiceException),
    ):
        artifact.get_download_url()
    assert mock_get.call_count == fake_settings.run_retry_attempts


@pytest.mark.unit
@pytest.mark.parametrize(
    "exc_factory",
    [
        lambda: requests.Timeout("timed out"),
        lambda: requests.ConnectionError("dns failure"),
        lambda: requests.RequestException("misc"),
    ],
)
def test_artifact_get_download_url_network_errors_become_service_exception(artifact, exc_factory) -> None:
    """`requests` exceptions are wrapped as ServiceException so retry can act on them.

    Without this wrapping the e2e tests in PR #507 hung — `requests.HTTPError`
    escaped the retry loop and surfaced as a wrong exception type.
    """
    fake_settings = Mock()
    fake_settings.run_retry_attempts = 1  # don't waste test time on retries
    fake_settings.run_retry_wait_min = 0.0
    fake_settings.run_retry_wait_max = 0.0
    fake_settings.run_timeout = 5.0

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_SETTINGS, return_value=fake_settings),
        patch(_PATCH_REQUESTS_GET, side_effect=exc_factory()),
        pytest.raises(ServiceException),
    ):
        artifact.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_passes_proxy_and_ca_bundle(configured_api) -> None:
    """Proxy and custom CA bundle from codegen Configuration are honored.

    Enterprise installs frequently set these via env; a previous draft of this
    code ignored them, which would have broken downloads behind a proxy.
    """
    configured_api.api_client.configuration.proxy = "http://proxy.local:3128"
    configured_api.api_client.configuration.ssl_ca_cert = "/etc/ssl/corp-ca.pem"
    configured_api.api_client.configuration.verify_ssl = False
    art = Artifact(configured_api, _RUN_ID, _ARTIFACT_ID)
    response = _redirect_response(_PRESIGNED_URL)

    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=response) as mock_get,
    ):
        art.get_download_url()

    kwargs = mock_get.call_args.kwargs
    assert kwargs["proxies"] == {"http": "http://proxy.local:3128", "https": "http://proxy.local:3128"}
    # CA bundle path takes precedence over verify_ssl=False
    assert kwargs["verify"] == "/etc/ssl/corp-ca.pem"


@pytest.mark.unit
def test_run_get_artifact_download_url_delegates_to_artifact(app_run, configured_api) -> None:
    """Run.get_artifact_download_url is the documented entry point and must just delegate.

    Keeping this thin protects callers from internal refactors of `Artifact`.
    """
    response = _redirect_response(_PRESIGNED_URL)
    with (
        patch(_PATCH_GET_TOKEN, return_value="t"),
        patch(_PATCH_REQUESTS_GET, return_value=response),
    ):
        # Replace mock_api on the existing Run with the configured one
        app_run._api = configured_api
        url = app_run.get_artifact_download_url(_ARTIFACT_ID)
    assert url == _PRESIGNED_URL


@pytest.mark.unit
def test_run_artifact_returns_artifact_handle(app_run) -> None:
    """Run.artifact() returns an Artifact bound to the right run/artifact pair."""
    handle = app_run.artifact(_ARTIFACT_ID)
    assert isinstance(handle, Artifact)
    assert handle.run_id == _RUN_ID
    assert handle.artifact_id == _ARTIFACT_ID
