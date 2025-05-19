"""Tests for the runs resource module.

This module contains unit tests for the Runs class and ApplicationRun class,
verifying their functionality for listing, creating, and managing application runs.
"""

from unittest.mock import Mock, call

import pytest
from aignx.codegen.api.public_api import PublicApi
from aignx.codegen.models import (
    InputArtifactCreationRequest,
    ItemCreationRequest,
    ItemResultReadResponse,
    RunCreationResponse,
    RunReadResponse,
)

from aignostics.platform.resources.runs import ApplicationRun, Runs
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
def app_run(mock_api) -> ApplicationRun:
    """Create an ApplicationRun instance with a mock API for testing.

    Args:
        mock_api: A mock instance of ExternalsApi.

    Returns:
        ApplicationRun: An ApplicationRun instance using the mock API.
    """
    return ApplicationRun(mock_api, "test-run-id")


def test_runs_list_with_pagination(runs, mock_api) -> None:
    """Test that Runs.list() correctly handles pagination.

    This test verifies that the list method properly aggregates results from
    multiple paginated API responses and converts them to ApplicationRun instances.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    page1 = [Mock(spec=RunReadResponse, application_run_id=f"run-{i}") for i in range(PAGE_SIZE)]
    page2 = [Mock(spec=RunReadResponse, application_run_id=f"run-{i + PAGE_SIZE}") for i in range(5)]
    mock_api.list_application_runs_v1_runs_get.side_effect = [page1, page2]

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == PAGE_SIZE + 5
    assert all(isinstance(run, ApplicationRun) for run in result)
    assert mock_api.list_application_runs_v1_runs_get.call_count == 2
    mock_api.list_application_runs_v1_runs_get.assert_has_calls([
        call(page=1, page_size=PAGE_SIZE),
        call(page=2, page_size=PAGE_SIZE),
    ])


def test_runs_list_with_application_version_filter(runs, mock_api) -> None:
    """Test that Runs.list() correctly filters by application version.

    This test verifies that the application version filter parameter is
    correctly passed to the API client.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    app_version_id = "test-app-version"
    mock_api.list_application_runs_v1_runs_get.return_value = []

    # Act
    list(runs.list(for_application_version=app_version_id))

    # Assert
    mock_api.list_application_runs_v1_runs_get.assert_called_once_with(
        application_version_id=app_version_id, page=1, page_size=PAGE_SIZE
    )


def test_application_run_results_with_pagination(app_run, mock_api) -> None:
    """Test that ApplicationRun.results() correctly handles pagination.

    This test verifies that the results method properly aggregates results
    from multiple paginated API responses when requesting run results.

    Args:
        app_run: ApplicationRun instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    page1 = [Mock(spec=ItemResultReadResponse) for _ in range(PAGE_SIZE)]
    page2 = [Mock(spec=ItemResultReadResponse) for _ in range(5)]
    mock_api.list_run_results_v1_runs_application_run_id_results_get.side_effect = [page1, page2]

    # Act
    result = list(app_run.results())

    # Assert
    assert len(result) == PAGE_SIZE + 5
    assert mock_api.list_run_results_v1_runs_application_run_id_results_get.call_count == 2
    mock_api.list_run_results_v1_runs_application_run_id_results_get.assert_has_calls([
        call(application_run_id=app_run.application_run_id, page=1, page_size=PAGE_SIZE),
        call(application_run_id=app_run.application_run_id, page=2, page_size=PAGE_SIZE),
    ])


def test_runs_call_returns_application_run(runs) -> None:
    """Test that Runs.__call__() returns an ApplicationRun instance.

    This test verifies that calling the Runs instance as a function correctly
    initializes and returns an ApplicationRun instance with the specified run ID.

    Args:
        runs: Runs instance with mock API.
    """
    # Act
    run_id = "test-run-id"
    app_run = runs(run_id)

    # Assert
    assert isinstance(app_run, ApplicationRun)
    assert app_run.application_run_id == run_id
    assert app_run._api == runs._api


def test_runs_create_returns_application_run(runs, mock_api) -> None:
    """Test that Runs.create() returns an ApplicationRun instance.

    This test verifies that the create method correctly calls the API client
    to create a new run and returns an ApplicationRun instance for the created run.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    run_id = "new-run-id"
    mock_items = [
        ItemCreationRequest(
            reference="item-1",
            input_artifacts=[
                InputArtifactCreationRequest(name="artifact-1", download_url="url", metadata={"key": "value"})
            ],
        )
    ]
    mock_api.create_application_run_v1_runs_post.return_value = RunCreationResponse(application_run_id=run_id)

    # Mock the validation method to prevent it from making actual API calls
    runs._validate_input_items = Mock()

    # Act
    app_run = runs.create(application_version="mock", items=mock_items)

    # Assert
    assert isinstance(app_run, ApplicationRun)
    assert app_run.application_run_id == run_id
    mock_api.create_application_run_v1_runs_post.assert_called_once()
    # Check that a RunCreationRequest was passed to the API call
    call_args = mock_api.create_application_run_v1_runs_post.call_args[0][0]
    assert call_args.application_version_id == "mock"
    assert call_args.items == mock_items


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
    mock_api.list_application_runs_v1_runs_get.side_effect = NotFoundException()

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == 0
    mock_api.list_application_runs_v1_runs_get.assert_called_once_with(page=1, page_size=PAGE_SIZE)


def test_paginate_with_not_found_exception_after_full_page(runs, mock_api) -> None:
    """Test that paginate handles NotFoundException after a full page.

    This test verifies that when we get exactly PAGE_SIZE items on the first page
    and then a NotFoundException on the second page, we correctly return just the
    first page's items.

    Args:
        runs: Runs instance with mock API.
        mock_api: Mock ExternalsApi instance.
    """
    # Arrange
    from aignx.codegen.exceptions import NotFoundException

    # Return exactly PAGE_SIZE items for first page, then throw NotFoundException
    full_page = [Mock(spec=RunReadResponse, application_run_id=f"run-{i}") for i in range(PAGE_SIZE)]
    mock_api.list_application_runs_v1_runs_get.side_effect = [full_page, NotFoundException()]

    # Act
    result = list(runs.list())

    # Assert
    assert len(result) == PAGE_SIZE
    assert mock_api.list_application_runs_v1_runs_get.call_count == 2
    mock_api.list_application_runs_v1_runs_get.assert_has_calls([
        call(page=1, page_size=PAGE_SIZE),
        call(page=2, page_size=PAGE_SIZE),
    ])
