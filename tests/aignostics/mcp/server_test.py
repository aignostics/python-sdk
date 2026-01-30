"""Unit tests for MCP server tools and helpers."""

# ruff: noqa: PLR6301

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from aignostics.mcp._server import (
    DEFAULT_CACHE_DIR,
    _clear_duckdb_connection,
    _duckdb_connections,
    _ensure_readouts_exist,
    _extract_external_id_from_filename,
    _format_schema_markdown,
    _get_cache_dir,
    _get_duckdb_connection,
    _get_readout_cache_path,
    _get_readouts_dir,
    _get_schema,
    _resolve_run_id,
    _schema_cache,
)

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def clean_caches() -> Generator[None, None, None]:
    """Clear all caches before and after test."""
    _duckdb_connections.clear()
    _schema_cache.clear()
    yield
    _duckdb_connections.clear()
    _schema_cache.clear()


@pytest.fixture
def mock_readouts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up a temporary readouts directory."""
    readouts_dir = tmp_path / "readouts"
    readouts_dir.mkdir()
    monkeypatch.setenv("AIGNOSTICS_MCP_READOUTS_DIR", str(readouts_dir))
    return readouts_dir


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content for testing."""
    return (
        "# HETA Readout v1.0\n"  # Header line to skip
        "CELL_CLASS,CENTROID_X,CENTROID_Y,IN_CARCINOMA,IN_STROMA\n"
        "Lymphocyte,100.5,200.3,true,false\n"
        "Carcinoma cell,150.2,250.1,true,false\n"
        "Fibroblast,300.0,400.0,false,true\n"
    )


@pytest.fixture
def run_with_readouts(mock_readouts_dir: Path, sample_csv_content: str, clean_caches: None) -> str:
    """Create a run directory with sample readout files using per-slide naming."""
    run_id = "test-run-123"
    run_dir = mock_readouts_dir / run_id
    run_dir.mkdir()

    # Create cell readouts with per-slide naming convention
    cell_file = run_dir / "cell_readouts_slide001.tiff.csv"
    cell_file.write_text(sample_csv_content)

    # Create slide readouts with per-slide naming convention
    slide_content = "# Slide Readout v1.0\nSLIDE_ID,TOTAL_CELLS,AREA_MM2\nslide-001,1000,25.5\n"
    slide_file = run_dir / "slide_readouts_slide001.tiff.csv"
    slide_file.write_text(slide_content)

    return run_id


# =============================================================================
# Tests: Configuration Functions
# =============================================================================


@pytest.mark.unit
class TestConfigurationFunctions:
    """Tests for configuration helper functions."""

    def test_get_readouts_dir_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default readouts directory."""
        monkeypatch.delenv("AIGNOSTICS_MCP_READOUTS_DIR", raising=False)
        assert _get_readouts_dir() == DEFAULT_CACHE_DIR

    def test_get_readouts_dir_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test readouts directory from environment variable."""
        monkeypatch.setenv("AIGNOSTICS_MCP_READOUTS_DIR", "/custom/path")
        assert _get_readouts_dir() == Path("/custom/path")

    def test_get_cache_dir_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_cache_dir creates the directory if it doesn't exist."""
        new_dir = tmp_path / "new_cache_dir"
        monkeypatch.setenv("AIGNOSTICS_MCP_READOUTS_DIR", str(new_dir))
        assert not new_dir.exists()
        result = _get_cache_dir()
        assert result == new_dir
        assert new_dir.exists()

    def test_get_readout_cache_path(self, mock_readouts_dir: Path) -> None:
        """Test readout cache path generation with external_id."""
        path = _get_readout_cache_path("run-123", "cell", "slide001.tiff")
        assert path == mock_readouts_dir / "run-123" / "cell_readouts_slide001.tiff.csv"

    def test_get_readout_cache_path_creates_run_dir(self, mock_readouts_dir: Path) -> None:
        """Test that get_readout_cache_path creates the run directory."""
        run_dir = mock_readouts_dir / "new-run"
        assert not run_dir.exists()
        _get_readout_cache_path("new-run", "slide", "slide001.tiff")
        assert run_dir.exists()

    def test_extract_external_id_from_filename(self) -> None:
        """Test extracting external_id from readout filename."""
        # Simple case
        assert _extract_external_id_from_filename("cell_readouts_slide001.tiff.csv", "cell") == "slide001.tiff"
        assert _extract_external_id_from_filename("slide_readouts_slide001.tiff.csv", "slide") == "slide001.tiff"

        # With sanitized path separators (slashes become underscores)
        assert _extract_external_id_from_filename("cell_readouts_a_b_c_slide.tiff.csv", "cell") == "a_b_c_slide.tiff"

        # Complex filename
        assert (
            _extract_external_id_from_filename("cell_readouts_my_complex_slide_name.svs.csv", "cell")
            == "my_complex_slide_name.svs"
        )


# =============================================================================
# Tests: DuckDB Connection Caching
# =============================================================================


@pytest.mark.unit
class TestDuckDBConnectionCaching:
    """Tests for DuckDB connection caching."""

    def test_get_connection_creates_new(self, run_with_readouts: str) -> None:
        """Test that a new connection is created when not cached."""
        assert run_with_readouts not in _duckdb_connections
        con = _get_duckdb_connection(run_with_readouts)
        assert con is not None
        assert run_with_readouts in _duckdb_connections

    def test_get_connection_returns_cached(self, run_with_readouts: str) -> None:
        """Test that the same connection is returned from cache."""
        con1 = _get_duckdb_connection(run_with_readouts)
        con2 = _get_duckdb_connection(run_with_readouts)
        assert con1 is con2

    def test_get_connection_creates_views(self, run_with_readouts: str) -> None:
        """Test that views are created for slides and cells tables."""
        con = _get_duckdb_connection(run_with_readouts)

        # Query the cells view
        result = con.execute("SELECT COUNT(*) FROM cells").fetchone()
        assert result is not None
        assert result[0] == 3  # 3 cells in sample data

        # Query the slides view
        result = con.execute("SELECT COUNT(*) FROM slides").fetchone()
        assert result is not None
        assert result[0] == 1  # 1 slide in sample data

    def test_get_connection_adds_external_id_column(self, run_with_readouts: str) -> None:
        """Test that external_id column is added to views for per-slide filtering."""
        con = _get_duckdb_connection(run_with_readouts)

        # Query the external_id column from cells
        result = con.execute("SELECT DISTINCT external_id FROM cells").fetchall()
        assert result is not None
        assert len(result) == 1  # 1 slide in test data
        assert result[0][0] == "slide001.tiff"  # Extracted from filename

        # Query the external_id column from slides
        result = con.execute("SELECT DISTINCT external_id FROM slides").fetchall()
        assert result is not None
        assert len(result) == 1
        assert result[0][0] == "slide001.tiff"

    def test_external_id_filtering_with_like(self, run_with_readouts: str) -> None:
        """Test that external_id can be used for filtering with LIKE."""
        con = _get_duckdb_connection(run_with_readouts)

        # Filter with exact match
        result = con.execute("SELECT COUNT(*) FROM cells WHERE external_id = 'slide001.tiff'").fetchone()
        assert result is not None
        assert result[0] == 3  # All 3 cells match

        # Filter with partial match (LIKE)
        result = con.execute("SELECT COUNT(*) FROM cells WHERE external_id LIKE '%slide001%'").fetchone()
        assert result is not None
        assert result[0] == 3

        # Filter with no match
        result = con.execute("SELECT COUNT(*) FROM cells WHERE external_id = 'nonexistent.tiff'").fetchone()
        assert result is not None
        assert result[0] == 0

    def test_get_connection_no_files_raises(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test that FileNotFoundError is raised when no readout files exist."""
        run_dir = mock_readouts_dir / "empty-run"
        run_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="No readout files found"):
            _get_duckdb_connection("empty-run")

    def test_clear_connection_removes_from_cache(self, run_with_readouts: str) -> None:
        """Test that clear_duckdb_connection removes the connection from cache."""
        _get_duckdb_connection(run_with_readouts)
        assert run_with_readouts in _duckdb_connections

        _clear_duckdb_connection(run_with_readouts)
        assert run_with_readouts not in _duckdb_connections

    def test_clear_connection_preserves_schema_cache(self, run_with_readouts: str) -> None:
        """Test that clear_duckdb_connection does NOT clear schema cache (schema is global)."""
        # Populate schema cache
        _get_schema(run_with_readouts, "cell")
        _get_schema(run_with_readouts, "slide")
        assert "cell" in _schema_cache
        assert "slide" in _schema_cache

        _clear_duckdb_connection(run_with_readouts)

        # Schema cache should be preserved since it's global across all runs
        assert "cell" in _schema_cache
        assert "slide" in _schema_cache


# =============================================================================
# Tests: Schema Caching
# =============================================================================


@pytest.mark.unit
class TestSchemaCaching:
    """Tests for schema caching."""

    def test_get_schema_returns_columns(self, run_with_readouts: str) -> None:
        """Test that schema returns column names and types."""
        schema = _get_schema(run_with_readouts, "cell")
        # 5 data columns + 1 external_id column from UNION ALL
        assert len(schema) == 6  # CELL_CLASS, CENTROID_X, CENTROID_Y, IN_CARCINOMA, IN_STROMA, external_id

        col_names = [col[0] for col in schema]
        assert "CELL_CLASS" in col_names
        assert "CENTROID_X" in col_names
        assert "IN_CARCINOMA" in col_names
        assert "external_id" in col_names  # Added by UNION ALL query for per-slide filtering

    def test_get_schema_caches_result(self, run_with_readouts: str) -> None:
        """Test that schema is cached globally by type after first call."""
        cache_key = "cell"
        assert cache_key not in _schema_cache

        schema1 = _get_schema(run_with_readouts, "cell")
        assert cache_key in _schema_cache

        schema2 = _get_schema(run_with_readouts, "cell")
        assert schema1 is schema2  # Same object from cache

    def test_get_schema_no_file_returns_empty(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test that empty list is returned when file doesn't exist."""
        run_dir = mock_readouts_dir / "partial-run"
        run_dir.mkdir()

        schema = _get_schema("partial-run", "cell")
        assert schema == []


# =============================================================================
# Tests: Helper Functions
# =============================================================================


@pytest.mark.unit
class TestHelperFunctions:
    """Tests for helper functions."""

    def test_markdown_table_basic(self) -> None:
        """Test markdown table formatting with basic data."""
        from aignostics.mcp._server import _markdown_table

        headers = ["Name", "Value"]
        rows = [("foo", 1), ("bar", 2)]
        result = _markdown_table(headers, rows)

        assert "| Name | Value |" in result
        assert "| --- | --- |" in result
        assert "| foo | 1 |" in result
        assert "| bar | 2 |" in result

    def test_markdown_table_handles_none(self) -> None:
        """Test markdown table handles None values."""
        from aignostics.mcp._server import _markdown_table

        headers = ["A", "B"]
        rows = [("x", None), (None, "y")]
        result = _markdown_table(headers, rows)

        assert "| x |  |" in result
        assert "|  | y |" in result

    def test_markdown_table_empty_rows(self) -> None:
        """Test markdown table with no rows."""
        from aignostics.mcp._server import _markdown_table

        headers = ["Col1", "Col2"]
        rows: list[tuple[str, str]] = []
        result = _markdown_table(headers, rows)

        assert "| Col1 | Col2 |" in result
        assert "| --- | --- |" in result
        # Should only have header and separator lines
        assert result.count("\n") == 1

    def test_format_schema_markdown(self) -> None:
        """Test schema markdown formatting."""
        schema = [("col1", "VARCHAR"), ("col2", "INTEGER")]
        result = _format_schema_markdown(schema, "cell")

        assert "## Cell Readout Schema" in result
        assert "| Column | Type |" in result
        assert "| col1 | VARCHAR |" in result
        assert "| col2 | INTEGER |" in result
        assert "Total columns: 2" in result

    def test_ensure_readouts_exist_when_present(self, run_with_readouts: str) -> None:
        """Test ensure_readouts_exist returns True when files exist."""
        has_slides, has_cells = _ensure_readouts_exist(run_with_readouts)
        assert has_slides is True
        assert has_cells is True


# =============================================================================
# Tests: Run ID Resolution
# =============================================================================


@pytest.mark.unit
class TestResolveRunId:
    """Tests for run ID resolution."""

    def test_resolve_run_id_direct_match(self) -> None:
        """Test resolving a valid run_id directly."""
        mock_client = MagicMock()
        mock_run = MagicMock()
        mock_client.runs.return_value = mock_run

        result = _resolve_run_id(mock_client, "run-uuid-123")

        assert result == "run-uuid-123"
        mock_client.runs.assert_called_once_with("run-uuid-123")
        mock_run.details.assert_called_once()

    def test_resolve_run_id_by_external_id(self) -> None:
        """Test resolving via external_id when run_id not found."""
        from aignx.codegen.exceptions import NotFoundException

        mock_client = MagicMock()
        mock_run = MagicMock()
        mock_run.details.side_effect = NotFoundException("Not found")
        mock_client.runs.return_value = mock_run

        # external_id search returns a result
        mock_list_result = MagicMock()
        mock_list_result.run_id = "resolved-run-id"
        mock_client.runs.list.return_value = iter([mock_list_result])

        result = _resolve_run_id(mock_client, "external-123")

        assert result == "resolved-run-id"
        mock_client.runs.list.assert_called_once_with(external_id="external-123", page_size=1)

    def test_resolve_run_id_not_found_raises(self) -> None:
        """Test that NotFoundException is raised when no match found."""
        from aignx.codegen.exceptions import NotFoundException

        mock_client = MagicMock()
        mock_run = MagicMock()
        mock_run.details.side_effect = NotFoundException("Not found")
        mock_client.runs.return_value = mock_run
        mock_client.runs.list.return_value = iter([])  # No results

        with pytest.raises(NotFoundException, match="No run found"):
            _resolve_run_id(mock_client, "nonexistent")


# =============================================================================
# Tests: MCP Tools (Integration with Mocks)
# =============================================================================


@pytest.mark.unit
class TestMCPTools:
    """Tests for MCP tool functions.

    Note: MCP tools decorated with @mcp.tool() become FunctionTool objects.
    We call the decorated functions directly.
    """

    def test_list_runs_returns_markdown_table(self) -> None:
        """Test that list_runs returns a properly formatted markdown table."""
        from aignostics.mcp._server import list_runs

        mock_run = MagicMock()
        mock_details = MagicMock()
        mock_details.application_id = "heta"
        mock_details.version_number = "1.0.0"
        mock_details.state.value = "TERMINATED"
        mock_details.statistics.item_succeeded_count = 5
        mock_details.statistics.item_count = 5
        mock_run.run_id = "run-123"
        mock_run.details.return_value = mock_details

        with patch("aignostics.mcp._server.Client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.runs.list.return_value = iter([mock_run])
            mock_get_client.return_value = mock_client

            # Call the decorated function directly
            result = list_runs(limit=1)

        assert "| Run ID |" in result
        assert "run-123" in result
        assert "heta" in result
        assert "TERMINATED" in result

    def test_list_runs_no_runs(self) -> None:
        """Test list_runs when no runs exist."""
        from aignostics.mcp._server import list_runs

        with patch("aignostics.mcp._server.Client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.runs.list.return_value = iter([])
            mock_get_client.return_value = mock_client

            result = list_runs()

        assert result == "No runs found."

    def test_get_run_status_returns_details(self) -> None:
        """Test that get_run_status returns detailed information."""
        from aignostics.mcp._server import get_run_status

        mock_details = MagicMock()
        mock_details.application_id = "heta"
        mock_details.version_number = "2.0.0"
        mock_details.state.value = "PROCESSING"
        mock_details.termination_reason = None
        mock_details.error_message = None
        mock_details.statistics.item_count = 10
        mock_details.statistics.item_succeeded_count = 5
        mock_details.statistics.item_processing_count = 3
        mock_details.statistics.item_pending_count = 2
        mock_details.statistics.item_user_error_count = 0
        mock_details.statistics.item_system_error_count = 0
        mock_details.statistics.item_skipped_count = 0

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = "run-456"
            mock_client = MagicMock()
            mock_run = MagicMock()
            mock_run.details.return_value = mock_details
            mock_client.runs.return_value = mock_run
            mock_get_client.return_value = mock_client

            result = get_run_status("run-456")

        assert "## Run Status: run-456" in result
        assert "**Application:** heta" in result
        assert "**State:** PROCESSING" in result
        assert "Total: 10" in result

    def test_get_current_user_returns_info(self) -> None:
        """Test that get_current_user returns user and org info."""
        from aignostics.mcp._server import get_current_user

        with patch("aignostics.mcp._server.Client") as mock_get_client:
            mock_client = MagicMock()
            mock_me = MagicMock()
            mock_me.user.email = "test@example.com"
            mock_me.organization.name = "Test Org"
            mock_client.me.return_value = mock_me
            mock_get_client.return_value = mock_client

            result = get_current_user()

        assert "test@example.com" in result
        assert "Test Org" in result

    def test_query_readouts_sql_executes_query(self, run_with_readouts: str) -> None:
        """Test that query_readouts_sql executes SQL and returns results."""
        from aignostics.mcp._server import query_readouts_sql

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_with_readouts
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = query_readouts_sql(
                run_with_readouts, "SELECT CELL_CLASS, COUNT(*) as n FROM cells GROUP BY CELL_CLASS ORDER BY n DESC"
            )

        assert "| CELL_CLASS |" in result
        assert "Lymphocyte" in result

    def test_query_readouts_sql_truncation_indicator(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test that query_readouts_sql shows truncation indicator when results exceed limit."""
        from aignostics.mcp._server import MAX_SQL_RESULT_ROWS, query_readouts_sql

        # Create a run with many rows (more than MAX_SQL_RESULT_ROWS)
        run_id = "truncation-test-run"
        run_dir = mock_readouts_dir / run_id
        run_dir.mkdir()

        # Generate CSV with more rows than the limit
        num_rows = MAX_SQL_RESULT_ROWS + 10
        csv_lines = ["# Header\nID,VALUE"]
        csv_lines.extend([f"{i},{i * 10}" for i in range(num_rows)])
        cell_file = run_dir / "cell_readouts_slide001.csv"
        cell_file.write_text("\n".join(csv_lines))

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_id
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = query_readouts_sql(run_id, "SELECT * FROM cells")

        # Should indicate truncation
        assert "(truncated)" in result
        assert f"{MAX_SQL_RESULT_ROWS} rows" in result

    def test_query_readouts_sql_no_truncation_when_under_limit(self, run_with_readouts: str) -> None:
        """Test that query_readouts_sql does not show truncation for small results."""
        from aignostics.mcp._server import query_readouts_sql

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_with_readouts
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = query_readouts_sql(run_with_readouts, "SELECT * FROM cells")

        # Should not indicate truncation (only 3 rows in test data)
        assert "(truncated)" not in result
        assert "3 rows" in result

    def test_get_readout_schema_returns_columns(self, run_with_readouts: str) -> None:
        """Test that get_readout_schema returns column information."""
        from aignostics.mcp._server import get_readout_schema

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_with_readouts
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = get_readout_schema(run_with_readouts, "cell")

        assert "## Cell Readout Schema" in result
        assert "| Column | Type |" in result
        assert "CELL_CLASS" in result

    def test_get_run_items_returns_markdown_table(self) -> None:
        """Test that get_run_items returns a properly formatted markdown table."""
        from aignostics.mcp._server import get_run_items
        from aignostics.platform import ItemOutput, ItemState

        mock_item = MagicMock()
        mock_item.external_id = "slide001.tiff"
        mock_item.state = ItemState.TERMINATED
        mock_item.output = ItemOutput.FULL
        mock_item.error_message = None

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = "run-789"
            mock_client = MagicMock()
            mock_run = MagicMock()
            mock_run.results.return_value = iter([mock_item])
            mock_client.runs.return_value = mock_run
            mock_get_client.return_value = mock_client

            result = get_run_items("run-789")

        assert "## Items in Run: run-789" in result
        assert "| # | External ID |" in result
        assert "slide001.tiff" in result
        assert "TERMINATED" in result

    def test_get_run_items_no_items(self) -> None:
        """Test get_run_items when no items exist."""
        from aignostics.mcp._server import get_run_items

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = "run-empty"
            mock_client = MagicMock()
            mock_run = MagicMock()
            mock_run.results.return_value = iter([])
            mock_client.runs.return_value = mock_run
            mock_get_client.return_value = mock_client

            result = get_run_items("run-empty")

        assert result == "No items found in this run."

    def test_download_readouts_downloads_files(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test that download_readouts downloads readout files."""
        from aignostics.mcp._server import download_readouts
        from aignostics.platform import ItemOutput

        mock_item = MagicMock()
        mock_item.external_id = "slide001.tiff"
        mock_item.output = ItemOutput.FULL

        mock_artifact = MagicMock()
        mock_artifact.name = "cell_readout.csv"
        mock_artifact.download_url = "https://example.com/cell_readout.csv"
        mock_item.output_artifacts = [mock_artifact]

        csv_content = b"# Header\nCOL1,COL2\nval1,val2\n"

        mock_response = MagicMock()
        mock_response.content = csv_content
        mock_response.raise_for_status = MagicMock()

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
            patch("aignostics.mcp._server.requests.get") as mock_requests_get,
        ):
            mock_requests_get.return_value = mock_response
            mock_resolve.return_value = "download-run"
            mock_client = MagicMock()
            mock_run = MagicMock()
            mock_run.results.return_value = iter([mock_item])
            mock_client.runs.return_value = mock_run
            mock_get_client.return_value = mock_client

            result = download_readouts("download-run")

        assert "## Downloaded Readouts" in result
        assert "Cell readouts" in result

    def test_download_readouts_no_readouts(self) -> None:
        """Test download_readouts when no readouts are available."""
        from aignostics.mcp._server import download_readouts
        from aignostics.platform import ItemOutput

        mock_item = MagicMock()
        mock_item.external_id = "slide001.tiff"
        mock_item.output = ItemOutput.NONE  # Not FULL, so no artifacts downloaded
        mock_item.output_artifacts = []

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = "no-readouts-run"
            mock_client = MagicMock()
            mock_run = MagicMock()
            mock_run.results.return_value = iter([mock_item])
            mock_client.runs.return_value = mock_run
            mock_get_client.return_value = mock_client

            result = download_readouts("no-readouts-run")

        assert "No readouts found" in result


# =============================================================================
# Tests: MCP Resources
# =============================================================================


@pytest.mark.unit
class TestMCPResources:
    """Tests for MCP resource functions.

    Note: MCP resources decorated with @mcp.resource() become Resource objects.
    We call the decorated functions directly.
    """

    def test_cell_schema_resource_returns_schema(self, run_with_readouts: str) -> None:
        """Test cell schema resource returns column information after cache is populated."""
        from aignostics.mcp._server import cell_schema_resource

        # First populate the cache by calling _get_schema
        _get_schema(run_with_readouts, "cell")

        # Now the static resource should return the schema
        result = cell_schema_resource()

        assert "## Cell Readout Schema" in result
        assert "CELL_CLASS" in result

    def test_cell_schema_resource_not_yet_discovered(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test cell schema resource returns helpful message when not yet discovered."""
        from aignostics.mcp._server import cell_schema_resource

        result = cell_schema_resource()

        assert "Cell schema not yet available" in result
        assert "download_readouts" in result
        assert "get_readout_schema" in result

    def test_slide_schema_resource_returns_schema(self, run_with_readouts: str) -> None:
        """Test slide schema resource returns column information after cache is populated."""
        from aignostics.mcp._server import slide_schema_resource

        # First populate the cache by calling _get_schema
        _get_schema(run_with_readouts, "slide")

        # Now the static resource should return the schema
        result = slide_schema_resource()

        assert "## Slide Readout Schema" in result
        assert "SLIDE_ID" in result

    def test_slide_schema_resource_not_yet_discovered(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test slide schema resource returns helpful message when not yet discovered."""
        from aignostics.mcp._server import slide_schema_resource

        result = slide_schema_resource()

        assert "Slide schema not yet available" in result
        assert "download_readouts" in result
        assert "get_readout_schema" in result

    def test_schema_resource_persists_after_clearing_duckdb(self, run_with_readouts: str) -> None:
        """Test that schema resource works after clearing DuckDB connection."""
        from aignostics.mcp._server import cell_schema_resource

        # Populate the schema cache
        _get_schema(run_with_readouts, "cell")

        # Clear the DuckDB connection (simulates re-downloading readouts)
        _clear_duckdb_connection(run_with_readouts)

        # Schema should still be available (it's global, not per-run)
        result = cell_schema_resource()
        assert "## Cell Readout Schema" in result
        assert "CELL_CLASS" in result


# =============================================================================
# Tests: Auth Retry Decorator
# =============================================================================


@pytest.mark.unit
class TestAuthRetryDecorator:
    """Tests for the auth retry decorator."""

    def test_retry_on_auth_failure_retries_once(self) -> None:
        """Test that auth failure triggers retry."""
        from aignx.codegen.exceptions import UnauthorizedException

        from aignostics.mcp._server import _retry_on_auth_failure

        call_count = 0
        err_msg = "Token expired"

        @_retry_on_auth_failure
        def failing_then_succeeding() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise UnauthorizedException(err_msg)
            return "success"

        with (
            patch("aignostics.mcp._server.remove_cached_token"),
            patch("aignostics.mcp._server._clear_client_cache"),
        ):
            result = failing_then_succeeding()

        assert result == "success"
        assert call_count == 2

    def test_retry_clears_token_on_failure(self) -> None:
        """Test that token is cleared on auth failure."""
        from aignx.codegen.exceptions import UnauthorizedException

        from aignostics.mcp._server import _retry_on_auth_failure

        err_msg = "Token expired"

        @_retry_on_auth_failure
        def always_fails() -> None:
            raise UnauthorizedException(err_msg)

        with (
            patch("aignostics.mcp._server.remove_cached_token") as mock_remove,
            patch("aignostics.mcp._server._clear_client_cache") as mock_clear,
            pytest.raises(UnauthorizedException),
        ):
            always_fails()

        mock_remove.assert_called_once()
        mock_clear.assert_called_once()


# =============================================================================
# Tests: Chart Configuration Builders (Consolidated)
# =============================================================================


@pytest.mark.unit
class TestChartBuilders:
    """Tests for chart configuration builder functions using parameterization."""

    @pytest.mark.parametrize("chart_type", ["bar", "pie", "line"])
    def test_build_chart_config_labels_values(self, chart_type: str) -> None:
        """Test chart types that use labels and values."""
        from aignostics.mcp._charts import build_chart_config

        config = build_chart_config(
            chart_type=chart_type,  # type: ignore[arg-type]
            labels=["A", "B", "C"],
            values=[10, 20, 30],
            title=f"Test {chart_type.title()} Chart",
        )

        expected_type = "bar" if chart_type == "bar" else chart_type
        assert config["type"] == expected_type
        assert config["_meta"]["title"] == f"Test {chart_type.title()} Chart"

    def test_build_chart_config_histogram(self) -> None:
        """Test histogram chart configuration."""
        from aignostics.mcp._charts import build_chart_config

        values = [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
        config = build_chart_config(
            chart_type="histogram",
            values=values,
            bins=5,
            title="Test Histogram",
        )

        assert config["type"] == "bar"  # Histogram rendered as bar
        assert len(config["data"]["labels"]) == 5
        assert sum(config["data"]["datasets"][0]["data"]) == 10
        assert "10 values in 5 bins" in config["_meta"]["subtitle"]

    def test_build_chart_config_scatter(self) -> None:
        """Test scatter chart configuration."""
        from aignostics.mcp._charts import build_chart_config

        config = build_chart_config(
            chart_type="scatter",
            x_values=[1.0, 2.0, 3.0],
            y_values=[4.0, 5.0, 6.0],
            title="Test Scatter",
        )

        assert config["type"] == "scatter"
        assert len(config["data"]["datasets"]) == 1
        assert len(config["data"]["datasets"][0]["data"]) == 3
        assert "3 points" in config["_meta"]["subtitle"]

    def test_build_chart_config_scatter_with_colors(self) -> None:
        """Test scatter chart with color grouping."""
        from aignostics.mcp._charts import build_chart_config

        config = build_chart_config(
            chart_type="scatter",
            x_values=[1.0, 2.0, 3.0, 4.0],
            y_values=[1.0, 2.0, 3.0, 4.0],
            color_values=["A", "A", "B", "B"],
        )

        assert config["type"] == "scatter"
        assert len(config["data"]["datasets"]) == 2  # Two groups

    @pytest.mark.parametrize(
        ("chart_type", "values"),
        [
            ("histogram", []),
            ("scatter", []),
            ("line", []),
        ],
    )
    def test_build_chart_config_empty_values(self, chart_type: str, values: list) -> None:
        """Test chart types handle empty values gracefully."""
        from aignostics.mcp._charts import build_chart_config

        if chart_type == "scatter":
            config = build_chart_config(chart_type=chart_type, x_values=values, y_values=values)  # type: ignore[arg-type]
        else:
            config = build_chart_config(chart_type=chart_type, values=values, labels=values)  # type: ignore[arg-type]

        assert "error" in config


@pytest.mark.unit
class TestChartFromSqlResult:
    """Tests for building charts from SQL results."""

    @pytest.mark.parametrize("chart_type", ["bar", "pie"])
    def test_build_chart_from_sql_result(self, run_with_readouts: str, chart_type: str) -> None:
        """Test building charts from SQL result."""
        from aignostics.mcp._charts import build_chart_from_sql_result
        from aignostics.mcp._server import _get_duckdb_connection

        con = _get_duckdb_connection(run_with_readouts)
        result = con.execute("SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS")

        config = build_chart_from_sql_result(result=result, chart_type=chart_type, title="Cell Distribution")  # type: ignore[arg-type]

        assert config["type"] == chart_type
        assert config["_meta"]["title"] == "Cell Distribution"

    def test_build_chart_from_sql_result_empty(self, run_with_readouts: str) -> None:
        """Test building chart from empty SQL result."""
        from aignostics.mcp._charts import build_chart_from_sql_result
        from aignostics.mcp._server import _get_duckdb_connection

        con = _get_duckdb_connection(run_with_readouts)
        result = con.execute("SELECT CELL_CLASS FROM cells WHERE 1=0")

        config = build_chart_from_sql_result(result=result, chart_type="bar")

        assert "error" in config
        assert "no results" in config["error"].lower()

    def test_build_chart_from_sql_result_invalid_column(self, run_with_readouts: str) -> None:
        """Test building chart with invalid column name."""
        from aignostics.mcp._charts import build_chart_from_sql_result
        from aignostics.mcp._server import _get_duckdb_connection

        con = _get_duckdb_connection(run_with_readouts)
        result = con.execute("SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS")

        config = build_chart_from_sql_result(result=result, chart_type="bar", x_column="nonexistent_column")

        assert "error" in config
        assert "not found" in config["error"].lower()

    def test_build_chart_from_sql_result_truncation_metadata(self, mock_readouts_dir: Path, clean_caches: None) -> None:
        """Test that chart builder adds truncation metadata when results exceed limit."""
        from aignostics.mcp._charts import build_chart_from_sql_result
        from aignostics.mcp._constants import MAX_CHART_POINTS
        from aignostics.mcp._server import _get_duckdb_connection

        # Create a run with many rows (more than MAX_CHART_POINTS)
        run_id = "chart-truncation-test"
        run_dir = mock_readouts_dir / run_id
        run_dir.mkdir()

        # Generate CSV with more rows than the chart limit
        num_rows = MAX_CHART_POINTS + 100
        csv_lines = ["# Header\nX,Y"]
        csv_lines.extend([f"{i},{i * 2}" for i in range(num_rows)])
        cell_file = run_dir / "cell_readouts_slide001.csv"
        cell_file.write_text("\n".join(csv_lines))

        con = _get_duckdb_connection(run_id)
        result = con.execute("SELECT X, Y FROM cells")

        config = build_chart_from_sql_result(result=result, chart_type="scatter")

        # Should have truncation metadata
        assert "_meta" in config
        assert config["_meta"]["truncated"] is True
        assert "truncation_message" in config["_meta"]
        assert str(MAX_CHART_POINTS) in config["_meta"]["truncation_message"]
        assert config["_meta"]["row_count"] == MAX_CHART_POINTS

    def test_build_chart_from_sql_result_no_truncation_small_data(self, run_with_readouts: str) -> None:
        """Test that chart builder does not add truncation metadata for small results."""
        from aignostics.mcp._charts import build_chart_from_sql_result
        from aignostics.mcp._server import _get_duckdb_connection

        con = _get_duckdb_connection(run_with_readouts)
        result = con.execute("SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS")

        config = build_chart_from_sql_result(result=result, chart_type="bar")

        # Should have row_count but NOT truncation
        assert "_meta" in config
        assert config["_meta"]["row_count"] == 3  # 3 cell types in test data
        assert "truncated" not in config["_meta"]


@pytest.mark.unit
class TestColorGeneration:
    """Tests for color generation utility."""

    @pytest.mark.parametrize("count", [3, 20])
    def test_generate_colors(self, count: int) -> None:
        """Test color generation produces valid CSS colors."""
        from aignostics.mcp._charts import _generate_colors

        colors = _generate_colors(count)
        assert len(colors) == count
        assert all("rgba" in c or "hsla" in c for c in colors)


# =============================================================================
# Tests: Visualization Tool
# =============================================================================


@pytest.mark.unit
class TestVisualizeReadoutsTool:
    """Tests for the visualize_readouts MCP tool."""

    @pytest.mark.parametrize("chart_type", ["bar", "pie", "scatter"])
    def test_visualize_readouts_chart_types(self, run_with_readouts: str, chart_type: str) -> None:
        """Test visualize_readouts with different chart types."""
        import json

        from fastmcp.tools.tool import ToolResult

        from aignostics.mcp._server import visualize_readouts

        sql = "SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS"
        if chart_type == "scatter":
            sql = "SELECT CENTROID_X, CENTROID_Y, CELL_CLASS FROM cells"

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_with_readouts
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = visualize_readouts(
                run_id=run_with_readouts,
                chart_type=chart_type,  # type: ignore[arg-type]
                sql=sql,
            )

        assert isinstance(result, ToolResult)
        data = json.loads(result.content[0].text)
        assert data["type"] == chart_type

    def test_visualize_readouts_sql_error(self, run_with_readouts: str) -> None:
        """Test visualize_readouts handles SQL errors gracefully."""
        import json

        from aignostics.mcp._server import visualize_readouts

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.return_value = run_with_readouts
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = visualize_readouts(
                run_id=run_with_readouts,
                chart_type="bar",
                sql="SELECT nonexistent_column FROM cells",
            )

        data = json.loads(result.content[0].text)
        assert "error" in data
        assert "SQL Error" in data["error"]

    def test_visualize_readouts_run_not_found(self) -> None:
        """Test visualize_readouts when run is not found."""
        import json

        from aignx.codegen.exceptions import NotFoundException

        from aignostics.mcp._server import visualize_readouts

        with (
            patch("aignostics.mcp._server.Client") as mock_get_client,
            patch("aignostics.mcp._server._resolve_run_id") as mock_resolve,
        ):
            mock_resolve.side_effect = NotFoundException("Not found")
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            result = visualize_readouts(
                run_id="nonexistent-run",
                chart_type="bar",
                sql="SELECT * FROM cells",
            )

        data = json.loads(result.content[0].text)
        assert "error" in data
        assert "not found" in data["error"].lower()


# =============================================================================
# Tests: Chart UI Resource
# =============================================================================


@pytest.mark.unit
class TestChartUIResource:
    """Tests for the chart UI MCP resource."""

    def test_chart_view_returns_html(self) -> None:
        """Test that chart_view resource returns valid HTML with MCP Apps SDK."""
        from aignostics.mcp._server import chart_view

        html = chart_view()

        # Check basic HTML structure
        assert "<!DOCTYPE html>" in html
        assert 'id="chart"' in html
        assert "canvas" in html.lower()
        assert "chart.js" in html.lower()
        assert "new App(" in html
        # Check MCP Apps SDK integration
        assert "@modelcontextprotocol/ext-apps" in html
        assert "ontoolresult" in html
