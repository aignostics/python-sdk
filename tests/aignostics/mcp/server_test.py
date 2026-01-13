"""Tests for MCP server module."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from aignx.codegen.exceptions import UnauthorizedException

from aignostics import platform

if TYPE_CHECKING:
    from pathlib import Path
from aignostics.mcp._server import (
    _clear_client_cache,
    _resolve_run_id,
    _retry_on_auth_failure,
    download_readouts,
    get_current_user,
    get_readout_schema,
    get_run_items,
    get_run_status,
    list_runs,
    query_cell_readouts,
    query_readouts_sql,
    query_slide_readouts,
    run_summary,
    summarize_cells,
)

# =============================================================================
# _clear_client_cache Tests
# =============================================================================


@pytest.mark.unit
def test_clear_client_cache_clears_cached_api_clients() -> None:
    """Test that cached API client instances are cleared."""
    from aignostics.platform._client import Client

    # Set up cached clients
    Client._api_client_cached = MagicMock()
    Client._api_client_uncached = MagicMock()

    _clear_client_cache()

    assert Client._api_client_cached is None
    assert Client._api_client_uncached is None


# =============================================================================
# _retry_on_auth_failure Tests
# =============================================================================


@pytest.mark.unit
def test_retry_on_auth_failure_returns_result_on_success() -> None:
    """Test that function result is returned when no auth failure."""
    call_count = 0

    @_retry_on_auth_failure
    def successful_func() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_func()
    assert result == "success"
    assert call_count == 1


@pytest.mark.unit
def test_retry_on_auth_failure_retries_once_on_unauthorized() -> None:
    """Test that function is retried once on UnauthorizedException."""
    call_count = 0

    @_retry_on_auth_failure
    def auth_failing_then_success() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise UnauthorizedException(status=401, reason="Unauthorized")
        return "success_after_retry"

    with (
        patch("aignostics.mcp._server.remove_cached_token") as mock_remove,
        patch("aignostics.mcp._server._clear_client_cache") as mock_clear,
    ):
        result = auth_failing_then_success()

    assert result == "success_after_retry"
    assert call_count == 2
    mock_remove.assert_called_once()
    mock_clear.assert_called_once()


@pytest.mark.unit
def test_retry_on_auth_failure_raises_on_second_failure() -> None:
    """Test that exception is raised if retry also fails."""
    call_count = 0

    @_retry_on_auth_failure
    def always_failing() -> str:
        nonlocal call_count
        call_count += 1
        raise UnauthorizedException(status=401, reason="Always unauthorized")

    with (
        patch("aignostics.mcp._server.remove_cached_token"),
        patch("aignostics.mcp._server._clear_client_cache"),
        pytest.raises(UnauthorizedException),
    ):
        always_failing()

    assert call_count == 2  # Original call + one retry


# =============================================================================
# _resolve_run_id Tests
# =============================================================================


@pytest.mark.unit
def test_resolve_run_id_returns_identifier_when_valid_run_id() -> None:
    """Test that identifier is returned directly when it's a valid run ID."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_client.runs.return_value = mock_run

    result = _resolve_run_id(mock_client, "valid-run-id-123")

    assert result == "valid-run-id-123"
    mock_client.runs.assert_called_once_with("valid-run-id-123")
    mock_run.details.assert_called_once()


@pytest.mark.unit
def test_resolve_run_id_searches_by_external_id_when_not_run_id() -> None:
    """Test that external_id search is used when identifier is not a run ID."""
    mock_client = MagicMock()
    mock_run = MagicMock()
    mock_run.run_id = "found-run-id-456"

    # First call (direct lookup) raises NotFoundException
    mock_client.runs.return_value.details.side_effect = platform.NotFoundException("Not found")
    # Second call (list by external_id) returns result
    mock_client.runs.list.return_value = iter([mock_run])

    result = _resolve_run_id(mock_client, "slide_001.svs")

    assert result == "found-run-id-456"
    mock_client.runs.list.assert_called_once_with(external_id="slide_001.svs", page_size=1)


@pytest.mark.unit
def test_resolve_run_id_raises_not_found_when_no_match() -> None:
    """Test that NotFoundException is raised when neither lookup succeeds."""
    mock_client = MagicMock()

    # Direct lookup fails
    mock_client.runs.return_value.details.side_effect = platform.NotFoundException("Not found")
    # External ID search returns empty
    mock_client.runs.list.return_value = iter([])

    with pytest.raises(platform.NotFoundException) as exc_info:
        _resolve_run_id(mock_client, "nonexistent-id")

    assert "No run found" in str(exc_info.value)


# =============================================================================
# MCP Tool Tests
# =============================================================================


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock platform client and patch _get_client to return it.

    Yields:
        Mock platform client instance.
    """
    client = MagicMock()
    with patch("aignostics.mcp._server._get_client", return_value=client):
        yield client


@pytest.mark.unit
def test_list_runs_returns_markdown_table(mock_client: MagicMock) -> None:
    """Test that list_runs returns a formatted markdown table."""
    # Set up mock run data
    mock_run = MagicMock()
    mock_run.run_id = "run-123-abc"
    mock_details = MagicMock()
    mock_details.application_id = "test-app"
    mock_details.version_number = "1.0.0-test-version"
    mock_details.state = platform.RunState.TERMINATED
    mock_details.statistics = MagicMock()
    mock_details.statistics.item_succeeded_count = 5
    mock_details.statistics.item_count = 5
    mock_run.details.return_value = mock_details

    mock_client.runs.list.return_value = iter([mock_run])

    result = list_runs(limit=1)

    assert "Run ID" in result
    assert "Application" in result
    assert "run-123-abc" in result
    assert "test-app" in result
    assert "5/5 succeeded" in result


@pytest.mark.unit
def test_list_runs_returns_message_when_empty(mock_client: MagicMock) -> None:
    """Test that list_runs returns appropriate message when no runs exist."""
    mock_client.runs.list.return_value = iter([])

    result = list_runs()

    assert result == "No runs found."


@pytest.mark.unit
def test_get_run_status_returns_detailed_status(mock_client: MagicMock) -> None:
    """Test that get_run_status returns formatted status information."""
    mock_run = MagicMock()
    mock_details = MagicMock()
    mock_details.application_id = "heta-app"
    mock_details.version_number = "2.0.0"
    mock_details.state = platform.RunState.TERMINATED
    mock_details.termination_reason = platform.RunTerminationReason.ALL_ITEMS_PROCESSED
    mock_details.error_message = None
    mock_details.statistics = MagicMock()
    mock_details.statistics.item_count = 10
    mock_details.statistics.item_succeeded_count = 8
    mock_details.statistics.item_processing_count = 0
    mock_details.statistics.item_pending_count = 0
    mock_details.statistics.item_user_error_count = 1
    mock_details.statistics.item_system_error_count = 1
    mock_details.statistics.item_skipped_count = 0
    mock_run.details.return_value = mock_details

    mock_client.runs.return_value = mock_run

    result = get_run_status("test-run-id")

    assert "Run Status" in result
    assert "heta-app" in result
    assert "2.0.0" in result
    assert "TERMINATED" in result
    assert "ALL_ITEMS_PROCESSED" in result
    assert "Total: 10" in result
    assert "Succeeded: 8" in result


@pytest.mark.unit
def test_get_run_status_handles_not_found(mock_client: MagicMock) -> None:
    """Test that get_run_status handles non-existent runs gracefully."""
    mock_client.runs.return_value.details.side_effect = platform.NotFoundException("Not found")
    mock_client.runs.list.return_value = iter([])

    result = get_run_status("nonexistent-run")

    assert "Run not found" in result


@pytest.mark.unit
def test_get_current_user_returns_user_info(mock_client: MagicMock) -> None:
    """Test that get_current_user returns formatted user information."""
    mock_me = MagicMock()
    mock_me.user.email = "test@example.com"
    mock_me.organization.name = "Test Organization"
    mock_client.me.return_value = mock_me

    result = get_current_user()

    assert "test@example.com" in result
    assert "Test Organization" in result


@pytest.mark.unit
def test_get_current_user_handles_auth_error(mock_client: MagicMock) -> None:
    """Test that get_current_user handles authentication errors gracefully."""
    mock_client.me.side_effect = Exception("Authentication failed")

    result = get_current_user()

    assert "Not authenticated" in result or "error" in result.lower()


# =============================================================================
# get_run_items Tests
# =============================================================================


@pytest.mark.unit
def test_get_run_items_returns_item_table(mock_client: MagicMock) -> None:
    """Test that get_run_items returns a formatted table of items."""
    mock_run = MagicMock()
    mock_item = MagicMock()
    mock_item.external_id = "slide_001.svs"
    mock_item.state = platform.ItemState.TERMINATED
    mock_item.output = platform.ItemOutput.FULL
    mock_item.error_message = None
    mock_run.results.return_value = [mock_item]

    mock_client.runs.return_value = mock_run

    result = get_run_items("test-run-id")

    assert "Items in Run" in result
    assert "External ID" in result
    assert "slide_001.svs" in result
    assert "TERMINATED" in result


@pytest.mark.unit
def test_get_run_items_shows_error_messages(mock_client: MagicMock) -> None:
    """Test that get_run_items displays error messages for failed items."""
    mock_run = MagicMock()
    mock_item = MagicMock()
    mock_item.external_id = "bad_slide.svs"
    mock_item.state = platform.ItemState.TERMINATED
    mock_item.output = platform.ItemOutput.NONE
    mock_item.error_message = "File format not supported"
    mock_run.results.return_value = [mock_item]

    mock_client.runs.return_value = mock_run

    result = get_run_items("test-run-id")

    assert "File format not supported" in result


@pytest.mark.unit
def test_get_run_items_handles_empty_run(mock_client: MagicMock) -> None:
    """Test that get_run_items handles runs with no items."""
    mock_run = MagicMock()
    mock_run.results.return_value = []

    mock_client.runs.return_value = mock_run

    result = get_run_items("empty-run-id")

    assert "No items found" in result


# =============================================================================
# download_readouts Tests
# =============================================================================


@pytest.mark.unit
def test_download_readouts_downloads_files(mock_client: MagicMock, tmp_path: Path) -> None:
    """Test that download_readouts downloads readout files to specified directory."""
    mock_run = MagicMock()
    mock_item = MagicMock()
    mock_item.output = platform.ItemOutput.FULL

    mock_artifact = MagicMock()
    mock_artifact.name = "slide_readout.csv"
    mock_artifact.download_url = "https://example.com/slide_readout.csv"
    mock_item.output_artifacts = [mock_artifact]

    mock_run.results.return_value = [mock_item]
    mock_client.runs.return_value = mock_run

    with patch("aignostics.mcp._server.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"col1,col2\nval1,val2"
        mock_get.return_value = mock_response

        result = download_readouts("test-run-id", output_dir=str(tmp_path))

    assert "Downloaded Readouts" in result
    assert "slide" in result
    assert (tmp_path / "slide_readouts.csv").exists()


@pytest.mark.unit
def test_download_readouts_handles_no_readouts(mock_client: MagicMock) -> None:
    """Test that download_readouts handles runs without readouts."""
    mock_run = MagicMock()
    mock_item = MagicMock()
    mock_item.output = platform.ItemOutput.NONE
    mock_item.output_artifacts = []
    mock_run.results.return_value = [mock_item]

    mock_client.runs.return_value = mock_run

    result = download_readouts("test-run-id")

    assert "No readouts found" in result


# =============================================================================
# SQL Query Tools Tests (with real DuckDB)
# =============================================================================


@pytest.fixture
def mock_client_with_readouts(tmp_path: Path) -> MagicMock:
    """Create mock client with sample readout CSV files for SQL query testing.

    This fixture:
    1. Creates sample slide and cell readout CSV files
    2. Patches _get_client to return a mock client
    3. Patches AIGNOSTICS_MCP_READOUTS_DIR to point to tmp_path

    Yields:
        Mock platform client instance with readout files available.
    """
    # Create sample readout files
    run_dir = tmp_path / "test-run-id"
    run_dir.mkdir()

    slide_path = run_dir / "slide_readouts.csv"
    slide_path.write_text("# Header comment\nABSOLUTE_AREA,TISSUE_AREA\n1000,800\n")

    cell_path = run_dir / "cell_readouts.csv"
    cell_path.write_text(
        "# Header comment\nCELL_CLASS,X,Y,IN_CARCINOMA\nTumor,100,200,true\nTumor,150,250,true\nStroma,300,400,false\n"
    )

    # Create mock client
    client = MagicMock()
    client.runs.return_value.details.return_value = MagicMock()

    with (
        patch("aignostics.mcp._server._get_client", return_value=client),
        patch.dict(os.environ, {"AIGNOSTICS_MCP_READOUTS_DIR": str(tmp_path)}),
    ):
        yield client


@pytest.mark.unit
def test_query_readouts_sql_executes_query(mock_client_with_readouts: MagicMock) -> None:
    """Test that query_readouts_sql executes SQL and returns results."""
    result = query_readouts_sql("test-run-id", "SELECT COUNT(*) as total FROM cells")

    assert "total" in result
    assert "3" in result  # 3 cells in test data


@pytest.mark.unit
def test_query_readouts_sql_handles_invalid_query(mock_client_with_readouts: MagicMock) -> None:
    """Test that query_readouts_sql handles SQL errors gracefully."""
    result = query_readouts_sql("test-run-id", "SELECT nonexistent_column FROM cells")

    assert "Error" in result or "error" in result.lower()


@pytest.mark.unit
def test_get_readout_schema_returns_columns(mock_client_with_readouts: MagicMock) -> None:
    """Test that get_readout_schema returns column information."""
    result = get_readout_schema("test-run-id", "cell")

    assert "Schema" in result
    assert "CELL_CLASS" in result
    assert "Column" in result
    assert "Type" in result


@pytest.mark.unit
def test_query_slide_readouts_returns_data(mock_client_with_readouts: MagicMock) -> None:
    """Test that query_slide_readouts returns slide-level data."""
    result = query_slide_readouts("test-run-id")

    assert "Slide Readouts" in result
    assert "ABSOLUTE_AREA" in result
    assert "1000" in result


@pytest.mark.unit
def test_query_cell_readouts_returns_filtered_data(mock_client_with_readouts: MagicMock) -> None:
    """Test that query_cell_readouts returns filtered cell data."""
    result = query_cell_readouts("test-run-id", filter_expr="CELL_CLASS = 'Tumor'", limit=10)

    assert "Cell Readouts" in result
    assert "Tumor" in result
    assert "2" in result  # 2 tumor cells


@pytest.mark.unit
def test_summarize_cells_returns_distribution(mock_client_with_readouts: MagicMock) -> None:
    """Test that summarize_cells returns cell distribution statistics."""
    result = summarize_cells("test-run-id", group_by="CELL_CLASS")

    assert "Cell Summary" in result
    assert "Total Cells" in result
    assert "3" in result  # 3 total cells
    assert "Tumor" in result
    assert "Stroma" in result


# =============================================================================
# Compound Tool Tests (Skills)
# =============================================================================


@pytest.mark.unit
def test_run_summary_returns_complete_summary(mock_client: MagicMock) -> None:
    """Test that run_summary returns a comprehensive run overview."""
    mock_run = MagicMock()
    mock_details = MagicMock()
    mock_details.application_id = "heta"
    mock_details.version_number = "1.0.0"
    mock_details.state = platform.RunState.TERMINATED
    mock_details.termination_reason = platform.RunTerminationReason.ALL_ITEMS_PROCESSED
    mock_details.error_message = None
    mock_details.statistics = MagicMock()
    mock_details.statistics.item_count = 2
    mock_details.statistics.item_succeeded_count = 2
    mock_details.statistics.item_user_error_count = 0
    mock_details.statistics.item_system_error_count = 0
    mock_details.statistics.item_skipped_count = 0
    mock_run.details.return_value = mock_details

    mock_item = MagicMock()
    mock_item.external_id = "slide.svs"
    mock_item.output = platform.ItemOutput.FULL
    mock_item.termination_reason = platform.ItemTerminationReason.SUCCEEDED
    mock_item.error_message = None
    mock_artifact = MagicMock()
    mock_artifact.name = "cell_readout.csv"
    mock_item.output_artifacts = [mock_artifact]
    mock_run.results.return_value = [mock_item]

    mock_client.runs.return_value = mock_run

    result = run_summary("test-run-id")

    assert "Run Summary" in result
    assert "heta" in result
    assert "Statistics" in result
    assert "Items" in result
    assert "Available Artifacts" in result
