"""Tests for the runs resource module.

This module contains unit tests for the Runs class and Run class,
verifying their functionality for listing, creating, and managing application runs.
"""

from unittest.mock import Mock, patch

import pytest
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import (
    InputArtifactCreationRequest,
    ItemCreationRequest,
    ItemResultReadResponse,
    RunCreationResponse,
    RunReadResponse,
)

from aignostics.platform.resources.runs import LIST_APPLICATION_RUNS_MAX_PAGE_SIZE, Artifact, Run, Runs
from aignostics.platform.resources.utils import PAGE_SIZE

_PLATFORM_HOST = "https://platform.aignostics.com"
_PATCH_GET_AUTH = "aignostics.platform.resources.runs.get_token"
_PATCH_REQUESTS_GET = "aignostics.platform.resources.runs.requests.get"
_PATCH_SETTINGS = "aignostics.platform.resources.runs.settings"
_PATCH_DOWNLOAD_FILE = "aignostics.platform.resources.runs.download_file"
_PRESIGNED_URL = "https://storage.googleapis.com/presigned-url"
_PROXY_URL = "https://corporate-proxy:8080"
_MIME_TYPE_CSV = "text/csv"


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


@pytest.fixture
def artifact_instance(mock_api) -> Artifact:
    """Create an Artifact instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        Artifact: An Artifact instance using the mock API.
    """
    return Artifact(mock_api, "test-run-id", "artifact-123")


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


@pytest.mark.unit
def test_artifact_get_download_url_returns_presigned_url(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url extracts the presigned URL from a 307 redirect.

    The implementation calls GET /api/v1/runs/{run_id}/artifacts/{artifact_id}/file with
    allow_redirects=False and returns the Location header from the 307 response.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    expected_url = "https://storage.googleapis.com/presigned-url?token=abc"
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    mock_response = Mock()
    mock_response.status_code = 307
    mock_response.headers = {"Location": expected_url}

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=mock_response) as mock_get,
    ):
        result = artifact_instance.get_download_url()

    assert result == expected_url
    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args
    assert call_kwargs.args[0] == "https://platform.aignostics.com/api/v1/runs/test-run-id/artifacts/artifact-123/file"
    assert call_kwargs.kwargs["allow_redirects"] is False
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.unit
def test_artifact_get_download_url_retries_on_service_exception(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url retries when a 5xx response is received.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    error_response = Mock()
    error_response.status_code = 503
    error_response.reason = "Service Unavailable"

    success_response = Mock()
    success_response.status_code = 307
    success_response.headers = {"Location": _PRESIGNED_URL}

    mock_settings = Mock()
    mock_settings.run_retry_attempts = 2
    mock_settings.run_retry_wait_min = 0.0
    mock_settings.run_retry_wait_max = 0.0

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_SETTINGS, return_value=mock_settings),
        patch(
            _PATCH_REQUESTS_GET,
            side_effect=[error_response, success_response],
        ) as mock_get,
    ):
        result = artifact_instance.get_download_url()

    assert result == _PRESIGNED_URL
    assert mock_get.call_count == 2


@pytest.mark.unit
def test_artifact_get_download_url_raises_not_found(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url raises NotFoundException for a 404 response.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    from aignx.codegen.exceptions import NotFoundException

    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    not_found_response = Mock()
    not_found_response.status_code = 404
    not_found_response.reason = "Not Found"

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=not_found_response),
        pytest.raises(NotFoundException),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_raises_service_exception_on_timeout(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url wraps requests.Timeout in ServiceException.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    import requests as requests_lib
    from aignx.codegen.exceptions import ServiceException

    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(
            _PATCH_REQUESTS_GET,
            side_effect=requests_lib.Timeout("Connection timed out"),
        ),
        pytest.raises(ServiceException),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_raises_service_exception_on_connection_error(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url wraps requests.ConnectionError in ServiceException.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    import requests as requests_lib
    from aignx.codegen.exceptions import ServiceException

    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(
            _PATCH_REQUESTS_GET,
            side_effect=requests_lib.ConnectionError("Connection refused"),
        ),
        pytest.raises(ServiceException),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_raises_runtime_error_on_missing_location_header(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url raises RuntimeError when redirect has no Location header.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    redirect_response = Mock()
    redirect_response.status_code = 307
    redirect_response.headers = {}  # No Location header

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=redirect_response),
        pytest.raises(RuntimeError, match="missing Location header"),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_raises_api_exception_on_4xx(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url raises ApiException for 4xx client errors.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    from aignx.codegen.exceptions import ApiException

    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    bad_request_response = Mock()
    bad_request_response.status_code = 400
    bad_request_response.reason = "Bad Request"

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=bad_request_response),
        pytest.raises(ApiException),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_passes_proxy_and_ssl_config(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url forwards proxy and SSL config from the API client.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None
    mock_api.api_client.configuration.proxy = _PROXY_URL
    mock_api.api_client.configuration.ssl_ca_cert = "/path/to/ca-bundle.crt"
    mock_api.api_client.configuration.verify_ssl = True

    mock_response = Mock()
    mock_response.status_code = 307
    mock_response.headers = {"Location": _PRESIGNED_URL}

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=mock_response) as mock_get,
    ):
        result = artifact_instance.get_download_url()

    assert result == _PRESIGNED_URL
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["proxies"] == {
        "http": _PROXY_URL,
        "https": _PROXY_URL,
    }
    assert call_kwargs["verify"] == "/path/to/ca-bundle.crt"


@pytest.mark.unit
def test_artifact_download_uses_codegen_client(artifact_instance, mock_api) -> None:
    """Test that Artifact.download delegates to the codegen API client.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.get_artifact_url_v1_runs_run_id_artifacts_artifact_id_file_get.return_value = b"content"

    result = artifact_instance.download()

    assert result == b"content"
    mock_api.get_artifact_url_v1_runs_run_id_artifacts_artifact_id_file_get.assert_called_once()
    call_kwargs = mock_api.get_artifact_url_v1_runs_run_id_artifacts_artifact_id_file_get.call_args.kwargs
    assert call_kwargs["run_id"] == "test-run-id"
    assert call_kwargs["artifact_id"] == "artifact-123"


@pytest.mark.unit
def test_run_get_artifact_download_url_delegates_to_artifact(app_run, mock_api) -> None:
    """Test that Run.get_artifact_download_url delegates to Artifact.get_download_url.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    mock_response = Mock()
    mock_response.status_code = 307
    mock_response.headers = {"Location": _PRESIGNED_URL}

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_REQUESTS_GET, return_value=mock_response),
    ):
        result = app_run.get_artifact_download_url("artifact-123")

    assert result == _PRESIGNED_URL


@pytest.mark.unit
def test_ensure_artifacts_downloaded_uses_output_artifact_id(app_run, mock_api, tmp_path) -> None:
    """Test that ensure_artifacts_downloaded resolves URLs via get_artifact_download_url.

    Verifies that the method uses output_artifact_id to resolve presigned URLs
    instead of using the deprecated download_url field.

    Args:
        app_run: Run instance with mock API.
        mock_api: Mock ExternalsApi instance.
        tmp_path: Temporary directory for test files.
    """
    from aignx.codegen.models import ArtifactOutput, ArtifactState, OutputArtifactResultReadResponse

    artifact = OutputArtifactResultReadResponse.model_construct(
        output_artifact_id="artifact-abc",
        name="cell_classification",
        metadata={"checksum_base64_crc32c": "AAAA", "media_type": _MIME_TYPE_CSV},
        state=ArtifactState.TERMINATED,
        output=ArtifactOutput.AVAILABLE,
    )
    item = ItemResultReadResponse.model_construct(
        external_id="slide-1",
        output_artifacts=[artifact],
    )

    presigned_url = _PRESIGNED_URL

    with (
        patch.object(app_run, "get_artifact_download_url", return_value=presigned_url) as mock_get_url,
        patch(_PATCH_DOWNLOAD_FILE) as mock_download_file,
        patch("aignostics.platform.resources.runs.get_mime_type_for_artifact", return_value=_MIME_TYPE_CSV),
        patch("aignostics.platform.resources.runs.mime_type_to_file_ending", return_value=".csv"),
    ):
        app_run.ensure_artifacts_downloaded(tmp_path, item)

        mock_get_url.assert_called_once_with("artifact-abc")
        mock_download_file.assert_called_once_with(
            presigned_url,
            str(tmp_path / "slide-1" / "cell_classification.csv"),
            "AAAA",
        )


@pytest.mark.unit
def test_ensure_artifacts_downloaded_skips_artifact_without_id(app_run, tmp_path) -> None:
    """Test that ensure_artifacts_downloaded skips artifacts with no output_artifact_id.

    Args:
        app_run: Run instance with mock API.
        tmp_path: Temporary directory for test files.
    """
    from aignx.codegen.models import ArtifactOutput, ArtifactState, OutputArtifactResultReadResponse

    artifact = OutputArtifactResultReadResponse.model_construct(
        output_artifact_id=None,
        name="cell_classification",
        metadata={"checksum_base64_crc32c": "AAAA"},
        state=ArtifactState.TERMINATED,
        output=ArtifactOutput.AVAILABLE,
    )
    item = ItemResultReadResponse.model_construct(
        external_id="slide-1",
        output_artifacts=[artifact],
    )

    with (
        patch.object(app_run, "get_artifact_download_url") as mock_get_url,
        patch(_PATCH_DOWNLOAD_FILE) as mock_download_file,
    ):
        app_run.ensure_artifacts_downloaded(tmp_path, item, print_status=False)

        mock_get_url.assert_not_called()
        mock_download_file.assert_not_called()


@pytest.mark.unit
def test_ensure_artifacts_downloaded_skips_existing_file_with_matching_checksum(app_run, tmp_path) -> None:
    """Test that ensure_artifacts_downloaded skips files that already exist with correct checksum.

    Args:
        app_run: Run instance with mock API.
        tmp_path: Temporary directory for test files.
    """
    from aignx.codegen.models import ArtifactOutput, ArtifactState, OutputArtifactResultReadResponse

    artifact = OutputArtifactResultReadResponse.model_construct(
        output_artifact_id="artifact-abc",
        name="result",
        metadata={"checksum_base64_crc32c": "test_checksum"},
        state=ArtifactState.TERMINATED,
        output=ArtifactOutput.AVAILABLE,
    )
    item = ItemResultReadResponse.model_construct(
        external_id="slide-1",
        output_artifacts=[artifact],
    )

    # Create the file so it "already exists"
    item_dir = tmp_path / "slide-1"
    item_dir.mkdir()
    existing_file = item_dir / "result.csv"
    existing_file.write_bytes(b"existing content")

    with (
        patch.object(app_run, "get_artifact_download_url") as mock_get_url,
        patch(_PATCH_DOWNLOAD_FILE) as mock_download_file,
        patch("aignostics.platform.resources.runs.get_mime_type_for_artifact", return_value=_MIME_TYPE_CSV),
        patch("aignostics.platform.resources.runs.mime_type_to_file_ending", return_value=".csv"),
        patch("aignostics.platform.resources.runs.calculate_file_crc32c", return_value="test_checksum"),
    ):
        app_run.ensure_artifacts_downloaded(tmp_path, item, print_status=False)

        mock_get_url.assert_not_called()
        mock_download_file.assert_not_called()


@pytest.mark.unit
def test_artifact_get_download_url_raises_service_exception_on_request_exception(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url wraps generic requests.RequestException in ServiceException.

    Covers the fallback except clause for non-Timeout/ConnectionError request failures,
    e.g. TooManyRedirects or other requests.RequestException subclasses.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    import requests as requests_lib
    from aignx.codegen.exceptions import ServiceException

    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    mock_settings = Mock()
    mock_settings.run_retry_attempts = 1
    mock_settings.run_retry_wait_min = 0.0
    mock_settings.run_retry_wait_max = 0.0

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_SETTINGS, return_value=mock_settings),
        patch(
            _PATCH_REQUESTS_GET,
            side_effect=requests_lib.TooManyRedirects("Too many redirects"),
        ),
        pytest.raises(ServiceException),
    ):
        artifact_instance.get_download_url()


@pytest.mark.unit
def test_artifact_get_download_url_raises_runtime_error_on_unexpected_status(artifact_instance, mock_api) -> None:
    """Test that Artifact.get_download_url raises RuntimeError for unexpected 2xx/3xx status codes.

    The endpoint should only return 307 redirects or error codes; any other status
    (e.g. 200 OK) is unexpected and should raise a RuntimeError.

    Args:
        artifact_instance: Artifact instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    mock_api.api_client = Mock()
    mock_api.api_client.configuration.host = _PLATFORM_HOST
    mock_api.api_client.configuration.token_provider = None

    unexpected_response = Mock()
    unexpected_response.status_code = 200  # Not a redirect, not an error

    mock_settings = Mock()
    mock_settings.run_retry_attempts = 1
    mock_settings.run_retry_wait_min = 0.0
    mock_settings.run_retry_wait_max = 0.0

    with (
        patch(_PATCH_GET_AUTH, return_value="test-token"),
        patch(_PATCH_SETTINGS, return_value=mock_settings),
        patch(_PATCH_REQUESTS_GET, return_value=unexpected_response),
        pytest.raises(RuntimeError, match="Unexpected status 200"),
    ):
        artifact_instance.get_download_url()
