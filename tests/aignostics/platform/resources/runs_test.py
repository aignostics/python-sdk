"""Tests for the runs resource module.

This module contains unit tests for the Runs class and Run class,
verifying their functionality for listing, creating, and managing application runs.
"""

from unittest.mock import Mock

import pytest
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import (
    InputArtifactCreationRequest,
    ItemCreationRequest,
    ItemResultReadResponse,
    RunCreationResponse,
    RunReadResponse,
)

from aignostics.platform.resources.runs import (
    LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    Run,
    Runs,
)
from aignostics.platform.resources.utils import PAGE_SIZE


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
    return Run(mock_api, "test-run-id")


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
    external_id, custom_metadata, sort, page_size) work together correctly.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    app_id = "test-app"
    app_version = "1.0.0"
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
    mock_run_data = Mock(
        spec=RunReadResponse,
        num_preceding_items_org=5,
        num_preceding_items_platform=100,
    )
    mock_api.get_run_v1_runs_run_id_get.return_value = mock_run_data
    result = app_run.details(hide_platform_queue_position=hide_platform_queue_position)
    assert result.num_preceding_items_org == 5
    assert result.num_preceding_items_platform == expected_platform_queue_position
