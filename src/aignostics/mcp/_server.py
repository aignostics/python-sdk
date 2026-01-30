"""MCP Server implementation for Aignostics Platform readouts.

Uses DuckDB for high-performance SQL querying of readout data.

Note: SQL injection warnings (S608) are intentionally suppressed - this MCP tool
is designed to allow LLMs/users to run arbitrary SQL queries on local CSV data.

The SLF001 warnings for accessing Client._api_client_cached and _api_client_uncached
are suppressed as this is necessary to clear the cached client on auth failures.
"""

# ruff: noqa: S608, SLF001, C901, PLR0912, PLR0913, PLR0917

from __future__ import annotations

import json
import os
from functools import wraps
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypeVar

import duckdb
import requests
from aignx.codegen.exceptions import NotFoundException, UnauthorizedException
from fastmcp import FastMCP
from fastmcp.server.apps import ResourceCSP, ResourceUI, ToolUI
from fastmcp.tools.tool import ToolResult
from loguru import logger
from mcp import types

from aignostics.mcp._charts import RESOURCE_PATH, VIEW_URI, build_chart_from_sql_result, get_chart_html
from aignostics.mcp._constants import SERVER_NAME
from aignostics.platform import Client, ItemOutput
from aignostics.platform._authentication import remove_cached_token

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# Type variables for the retry decorator
P = ParamSpec("P")
R = TypeVar("R")

# Constants
EXTERNAL_ID_MAX_LEN = 30
MAX_SQL_RESULT_ROWS = 100

# CSP metadata for the chart viewer - allows loading Chart.js and MCP Apps SDK from CDN
# - unpkg.com: MCP Apps SDK (@modelcontextprotocol/ext-apps)
# - esm.sh: Chart.js (properly bundled ES module with all dependencies)
CHART_RESOURCE_UI = ResourceUI(csp=ResourceCSP(resource_domains=["https://unpkg.com", "https://esm.sh"]))  # pyright: ignore[reportCallIssue]

# Initialize MCP server
mcp = FastMCP(SERVER_NAME)

# Default cache directory for downloaded readouts
DEFAULT_CACHE_DIR = Path.home() / "aignostics_readouts"

# Cache for DuckDB connections per run_id
_duckdb_connections: dict[str, duckdb.DuckDBPyConnection] = {}

# Cache for schema data by readout_type (schema is identical across all runs)
_schema_cache: dict[str, list[tuple[str, str]]] = {}


# =============================================================================
# Settings and Configuration
# =============================================================================


def _get_readouts_dir() -> Path:
    """Get the readouts directory from environment or use default.

    The directory can be configured via AIGNOSTICS_MCP_READOUTS_DIR.
    Default is ~/aignostics_readouts.

    Returns:
        Path to the readouts directory.
    """
    env_dir = os.environ.get("AIGNOSTICS_MCP_READOUTS_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


def _get_cache_dir() -> Path:
    """Get the cache directory, creating it if needed.

    Returns:
        Path to the MCP cache directory.
    """
    cache_dir = _get_readouts_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_readout_cache_dir(run_id: str) -> Path:
    """Get the cache directory for a run's readouts.

    Args:
        run_id: The run ID.

    Returns:
        Path to the run's readout cache directory.
    """
    cache_dir = _get_cache_dir() / run_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_readout_cache_path(run_id: str, readout_type: str, external_id: str) -> Path:
    """Get the cache path for a specific readout file.

    Args:
        run_id: The run ID.
        readout_type: Type of readout ('slide' or 'cell').
        external_id: External ID to include in filename for per-slide filtering.

    Returns:
        Path to the cached readout file.
    """
    cache_dir = _get_readout_cache_dir(run_id)
    # Sanitize external_id for use in filename (replace path separators)
    safe_id = external_id.replace("/", "_").replace("\\", "_")
    return cache_dir / f"{readout_type}_readouts_{safe_id}.csv"


def _has_readout_files(run_id: str, readout_type: str) -> bool:
    """Check if any readout files exist for a run.

    Args:
        run_id: The run ID.
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        True if at least one readout file exists.
    """
    cache_dir = _get_readout_cache_dir(run_id)
    return bool(list(cache_dir.glob(f"{readout_type}_readouts_*.csv")))


# =============================================================================
# DuckDB Connection Caching
# =============================================================================


def _extract_external_id_from_filename(filename: str, readout_type: str) -> str:
    """Extract the external_id from a readout filename.

    Args:
        filename: The filename (e.g., 'cell_readouts_slide_xyz.tiff.csv').
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        The extracted external_id (e.g., 'slide_xyz.tiff').
    """
    prefix = f"{readout_type}_readouts_"
    suffix = ".csv"
    return filename[len(prefix) : -len(suffix)]


def _build_union_all_query(run_id: str, readout_type: str) -> str | None:
    """Build a UNION ALL query for all readout files of a given type.

    Uses UNION ALL instead of glob patterns for better DuckDB performance
    with multiple CSV files. Adds an 'external_id' column to enable easy
    per-slide filtering in queries.

    Args:
        run_id: The run ID.
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        SQL query string or None if no files found.
    """
    cache_dir = _get_readout_cache_dir(run_id)
    files = sorted(cache_dir.glob(f"{readout_type}_readouts_*.csv"))

    if not files:
        return None

    # Add external_id column to enable per-slide filtering
    # Note: path separators in external_id are sanitized to underscores in filenames
    union_parts = []
    for f in files:
        external_id = _extract_external_id_from_filename(f.name, readout_type)
        # Escape single quotes in SQL strings ('' is the SQL escape for ')
        safe_id = external_id.replace("'", "''")
        safe_path = str(f).replace("'", "''")
        union_parts.append(
            f"SELECT *, '{safe_id}' as external_id "
            f"FROM read_csv_auto('{safe_path}', header=true, skip=1)"
        )

    return " UNION ALL ".join(union_parts)


def _get_duckdb_connection(run_id: str) -> duckdb.DuckDBPyConnection:
    """Get or create a cached DuckDB connection with views for a run.

    Creates the connection and views once per run, reusing for subsequent queries.
    Uses UNION ALL to combine all per-slide readout files, with an 'external_id' column
    added to enable per-slide filtering (e.g., WHERE external_id LIKE '%slide.tiff').

    Args:
        run_id: The run ID.

    Returns:
        DuckDB connection with slides and cells views configured.

    Raises:
        FileNotFoundError: If no readout files exist for this run.
    """
    if run_id in _duckdb_connections:
        return _duckdb_connections[run_id]

    has_slides = _has_readout_files(run_id, "slide")
    has_cells = _has_readout_files(run_id, "cell")

    if not has_slides and not has_cells:
        msg = f"No readout files found for run {run_id}"
        raise FileNotFoundError(msg)

    con = duckdb.connect()

    if has_slides:
        slide_query = _build_union_all_query(run_id, "slide")
        if slide_query:
            con.execute(f"CREATE VIEW slides AS {slide_query}")
            logger.debug(f"Created slides view for run {run_id} using UNION ALL")
    if has_cells:
        cell_query = _build_union_all_query(run_id, "cell")
        if cell_query:
            con.execute(f"CREATE VIEW cells AS {cell_query}")
            logger.debug(f"Created cells view for run {run_id} using UNION ALL")

    _duckdb_connections[run_id] = con
    return con


def _clear_duckdb_connection(run_id: str) -> None:
    """Clear a cached DuckDB connection for a run.

    Called after re-downloading readouts to ensure fresh data is used.
    Note: Schema cache is NOT cleared because schema is identical across all runs.

    Args:
        run_id: The run ID.
    """
    if run_id in _duckdb_connections:
        try:
            _duckdb_connections[run_id].close()
        except Exception:
            logger.debug(f"Failed to close DuckDB connection for run {run_id}")
        del _duckdb_connections[run_id]
        logger.debug(f"Cleared DuckDB connection for run {run_id}")


def _get_schema(run_id: str, readout_type: str) -> list[tuple[str, str]]:
    """Get cached schema for a readout type.

    Returns schema from first matching file plus the 'external_id' column
    that is added when combining files via UNION ALL to enable per-slide filtering.

    Schema is cached globally by readout_type (not per-run) because the schema
    is identical across all runs. The run_id is only needed to find files if
    the schema hasn't been cached yet.

    Args:
        run_id: The run ID (used to find files if schema not yet cached).
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        List of (column_name, column_type) tuples.
    """
    # Schema is cached globally by type since it's identical across all runs
    if readout_type in _schema_cache:
        return _schema_cache[readout_type]

    if not _has_readout_files(run_id, readout_type):
        return []

    # Get schema from first file
    cache_dir = _get_readout_cache_dir(run_id)
    files = sorted(cache_dir.glob(f"{readout_type}_readouts_*.csv"))
    if not files:
        return []

    first_file = files[0]
    con = duckdb.connect()
    result = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{first_file}', header=true, skip=1)")
    schema = [(row[0], row[1]) for row in result.fetchall()]
    # Add external_id column that UNION ALL adds for per-slide filtering
    schema.append(("external_id", "VARCHAR"))
    _schema_cache[readout_type] = schema
    return schema


# =============================================================================
# Helper Functions
# =============================================================================


def _clear_client_cache() -> None:
    """Clear the cached API client instances.

    This forces re-authentication on the next API call.
    """
    Client._api_client_cached = None
    Client._api_client_uncached = None


def _markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Format data as a markdown table.

    Args:
        headers: Column headers.
        rows: List of rows, each row is a sequence of cell values.

    Returns:
        Markdown formatted table string.
    """

    def cell(v: Any) -> str:  # noqa: ANN401
        return str(v) if v is not None else ""

    lines = [
        "| " + " | ".join(cell(h) for h in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def _retry_on_auth_failure(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that retries once on authentication failure.

    If an UnauthorizedException is raised (e.g., expired token), this decorator:
    1. Removes the cached token file
    2. Clears the cached API client instances
    3. Retries the operation once

    This handles the case where the cached token has expired and needs refresh.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function that handles auth failures gracefully.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except UnauthorizedException:
            logger.debug("Authentication failed, clearing token and retrying")
            remove_cached_token()
            _clear_client_cache()
            return func(*args, **kwargs)

    return wrapper


def _resolve_run_id(client: Client, identifier: str) -> str:
    """Resolve a run_id or external_id to a run_id.

    Accepts either:
    - A run_id (UUID) - used directly
    - An external_id (item identifier) - finds the run containing that item

    Args:
        client: Authenticated platform client.
        identifier: Either a run_id or an external_id.

    Returns:
        The resolved run_id.

    Raises:
        NotFoundException: If no matching run is found.
    """
    # First, try to use it directly as a run_id
    try:
        run = client.runs(identifier)
        run.details()  # Validate it exists
        return identifier
    except NotFoundException:
        pass

    # Not a valid run_id, try to find a run by external_id
    runs = list(client.runs.list(external_id=identifier, page_size=1))
    if runs:
        return runs[0].run_id

    # No match found
    msg = f"No run found with run_id or external_id: {identifier}"
    raise NotFoundException(msg)


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool()
@_retry_on_auth_failure
def list_runs(
    limit: int = 10,
    app_id: str | None = None,
) -> str:
    """List recent application runs.

    Args:
        limit: Maximum number of runs to return (default 10).
        app_id: Optional application ID to filter by.

    Returns:
        Markdown table of runs with ID, application, version, state, and item counts.
    """
    client = Client()

    runs_iter = client.runs.list(application_id=app_id) if app_id else client.runs.list()
    runs = list(islice(runs_iter, limit))

    if not runs:
        return "No runs found."

    headers = ["Run ID", "Application", "Version", "State", "Items"]
    rows = []
    for run in runs:
        details = run.details()
        stats = details.statistics
        rows.append([
            run.run_id,
            details.application_id,
            details.version_number,
            details.state.value,
            f"{stats.item_succeeded_count}/{stats.item_count} succeeded",
        ])

    return _markdown_table(headers, rows)


@mcp.tool()
@_retry_on_auth_failure
def get_run_status(run_id: str) -> str:
    """Get detailed status of a specific run.

    Args:
        run_id: The run ID or external ID (item identifier) to check.

    Returns:
        Detailed status including state, statistics, and any errors.
    """
    client = Client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        details = run.details()
    except NotFoundException:
        return f"Run not found: {run_id}"

    lines = [
        f"## Run Status: {resolved_id}",
        "",
        f"- **Application:** {details.application_id}",
        f"- **Version:** {details.version_number}",
        f"- **State:** {details.state.value}",
    ]

    if details.termination_reason:
        lines.append(f"- **Termination Reason:** {details.termination_reason.value}")
    if details.error_message:
        lines.append(f"- **Error:** {details.error_message}")

    if details.statistics:
        stats = details.statistics
        lines.extend([
            "",
            "### Item Statistics",
            f"- Total: {stats.item_count}",
            f"- Succeeded: {stats.item_succeeded_count}",
            f"- Processing: {stats.item_processing_count}",
            f"- Pending: {stats.item_pending_count}",
            f"- User Errors: {stats.item_user_error_count}",
            f"- System Errors: {stats.item_system_error_count}",
            f"- Skipped: {stats.item_skipped_count}",
        ])

    return "\n".join(lines)


@mcp.tool()
@_retry_on_auth_failure
def get_run_items(run_id: str) -> str:
    """Get all items in a run with their states.

    Args:
        run_id: The run ID or external ID (item identifier) to get items for.

    Returns:
        List of items with their states and any errors.
    """
    client = Client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        items = list(run.results())
    except NotFoundException:
        return f"Run not found: {run_id}"

    if not items:
        return "No items found in this run."

    headers = ["#", "External ID", "State", "Output", "Error"]
    rows = []
    for i, item in enumerate(items, 1):
        ext_id = item.external_id
        external_id = f"...{ext_id[-EXTERNAL_ID_MAX_LEN:]}" if len(ext_id) > EXTERNAL_ID_MAX_LEN else ext_id
        rows.append([i, external_id, item.state.value, item.output.value, item.error_message or ""])

    return f"## Items in Run: {resolved_id}\n\n{_markdown_table(headers, rows)}"


def _download_readouts_impl(run_id: str, output_dir: str | None = None) -> str:
    """Internal implementation for downloading readouts.

    Downloads readouts from all items in a run to separate files per item.
    Each file includes the item's external_id in the filename to enable
    per-slide filtering via DuckDB's filename column.

    Args:
        run_id: The run ID or external ID (item identifier) to download readouts for.
        output_dir: Optional output directory. Uses cache if not specified.

    Returns:
        Summary of downloaded files.
    """
    client = Client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        items = list(run.results())
    except NotFoundException:
        return f"Run not found: {run_id}"

    # Clear cached DuckDB connection since we're downloading fresh data
    _clear_duckdb_connection(resolved_id)

    downloaded_cells: list[str] = []
    downloaded_slides: list[str] = []

    for item in items:
        if item.output != ItemOutput.FULL:
            continue

        for artifact in item.output_artifacts:
            if "readout" not in artifact.name:
                continue

            # Determine readout type
            if "slide" in artifact.name:
                readout_type = "slide"
            elif "cell" in artifact.name:
                readout_type = "cell"
            else:
                continue

            # Determine output path (include external_id for per-slide files)
            if output_dir:
                # Sanitize external_id for filename
                safe_id = item.external_id.replace("/", "_").replace("\\", "_")
                out_path = Path(output_dir) / f"{readout_type}_readouts_{safe_id}.csv"
                out_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                out_path = _get_readout_cache_path(resolved_id, readout_type, item.external_id)

            # Download
            if artifact.download_url:
                response = requests.get(artifact.download_url, timeout=300)
                response.raise_for_status()
                out_path.write_bytes(response.content)
                size_mb = len(response.content) / (1024 * 1024)
                if readout_type == "cell":
                    downloaded_cells.append(f"  - {out_path.name} ({size_mb:.1f} MB)")
                else:
                    downloaded_slides.append(f"  - {out_path.name} ({size_mb:.2f} MB)")

    if not downloaded_cells and not downloaded_slides:
        return "No readouts found in this run. The run may not have completed successfully."

    lines = ["## Downloaded Readouts", ""]
    if downloaded_cells:
        lines.append(f"**Cell readouts ({len(downloaded_cells)} files):**")
        lines.extend(downloaded_cells)
        lines.append("")
    if downloaded_slides:
        lines.append(f"**Slide readouts ({len(downloaded_slides)} files):**")
        lines.extend(downloaded_slides)

    return "\n".join(lines)


@mcp.tool()
@_retry_on_auth_failure
def download_readouts(run_id: str, output_dir: str | None = None) -> str:
    """Download slide and cell readouts for a run.

    Args:
        run_id: The run ID or external ID (item identifier) to download readouts for.
        output_dir: Optional output directory. Uses cache if not specified.

    Returns:
        Paths to the downloaded files.
    """
    return _download_readouts_impl(run_id, output_dir)


@mcp.tool()
@_retry_on_auth_failure
def query_readouts_sql(run_id: str, sql: str) -> str:
    """Execute an arbitrary SQL query on the readout data.

    This is a powerful tool for complex analysis. The readout tables are available as:
    - 'cells' - cell-level data (typically has a large number of rows)
    - 'slides' - slide-level data (typically has a larger number of columns)

    CRITICAL: Check schema first to discover exact column names. Do NOT guess.

    Args:
        run_id: The run ID or external ID (item identifier) to query readouts for.
        sql: SQL query to execute. Use 'slides' and 'cells' as table names.
             Example: "SELECT CELL_CLASS, COUNT(*) as n FROM cells GROUP BY CELL_CLASS"

    Returns:
        Query results as markdown table, or error message.
    """
    client = Client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except NotFoundException:
        return f"Run not found: {run_id}"

    has_slides, has_cells = _ensure_readouts_exist(resolved_id)

    if not has_slides and not has_cells:
        return f"No readouts found for run {run_id}. Download readouts first."

    try:
        # Get cached connection with views already configured
        con = _get_duckdb_connection(resolved_id)

        # Execute the user's query
        result = con.execute(sql)
        rows = result.fetchmany(MAX_SQL_RESULT_ROWS)
        columns = result.description

        if not rows:
            return "Query returned no results."

        truncated = result.fetchone() is not None
        headers = [col[0] for col in columns]
        suffix = " (truncated)" if truncated else ""

        return f"{_markdown_table(headers, list(rows))}\n\n*{len(rows)} rows{suffix}*"

    except FileNotFoundError:
        return f"No readouts found for run {run_id}. Download readouts first."
    except Exception as e:
        # Provide helpful error with available columns
        error_msg = f"SQL Error: {e}\n\n"

        # Use cached schema for error context
        cell_schema = _get_schema(resolved_id, "cell")
        slide_schema = _get_schema(resolved_id, "slide")

        if cell_schema:
            col_names = [c[0] for c in cell_schema[:20]]
            error_msg += f"**Available cell columns:** {', '.join(col_names)}...\n"
        if slide_schema:
            col_names = [c[0] for c in slide_schema[:20]]
            error_msg += f"**Available slide columns:** {', '.join(col_names)}...\n"

        return error_msg


def _ensure_readouts_exist(resolved_id: str) -> tuple[bool, bool]:
    """Ensure readouts exist for a run, downloading if necessary.

    Args:
        resolved_id: The resolved run ID.

    Returns:
        Tuple of (has_slides, has_cells) booleans.
    """
    if not (_has_readout_files(resolved_id, "slide") or _has_readout_files(resolved_id, "cell")):
        _download_readouts_impl(resolved_id)

    return _has_readout_files(resolved_id, "slide"), _has_readout_files(resolved_id, "cell")


@mcp.tool()
@_retry_on_auth_failure
def get_readout_schema(run_id: str, readout_type: str = "cell") -> str:
    """Get the schema (column names and types) of a readout file.

    This tool also populates the global schema cache, making the schema available
    via the static MCP resources readouts://schema/cell and readouts://schema/slide.

    Args:
        run_id: The run ID or external ID (item identifier) to get schema for.
        readout_type: Type of readout ('slide' or 'cell', default 'cell').

    Returns:
        Table schema with column names and types.
    """
    client = Client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except NotFoundException:
        return f"Run not found: {run_id}"

    _ensure_readouts_exist(resolved_id)

    schema = _get_schema(resolved_id, readout_type)
    if not schema:
        return f"No {readout_type} readouts found for run {run_id}."

    return _format_schema_markdown(schema, readout_type)


@mcp.tool()
@_retry_on_auth_failure
def get_current_user() -> str:
    """Get information about the currently authenticated user.

    Returns:
        User email and organization information.
    """
    client = Client()

    try:
        me = client.me()
        return f"**User:** {me.user.email}\n**Organization:** {me.organization.name}"
    except Exception as e:
        return f"Not authenticated or error: {e}"


# =============================================================================
# MCP Resources
# =============================================================================


def _format_schema_markdown(schema: list[tuple[str, str]], readout_type: str) -> str:
    """Format schema as markdown table.

    Args:
        schema: List of (column_name, column_type) tuples.
        readout_type: Type of readout ('slide' or 'cell').

    Returns:
        Markdown formatted schema table.
    """
    table = _markdown_table(["Column", "Type"], schema)
    return f"## {readout_type.title()} Readout Schema\n\n{table}\n\n*Total columns: {len(schema)}*"


@mcp.resource("readouts://schema/cell")
def cell_schema_resource() -> str:
    """Cell readout schema.

    Provides column names and types for the cells table without requiring
    a tool call. Schema is discovered from the first run that downloads readouts
    and is identical across all runs.

    Returns:
        Markdown table of column names and types, or a helpful message if
        no schema has been discovered yet.
    """
    if "cell" not in _schema_cache:
        return (
            "Cell schema not yet available. Use download_readouts or get_readout_schema "
            "with any run_id to discover the schema."
        )
    return _format_schema_markdown(_schema_cache["cell"], "cell")


@mcp.resource("readouts://schema/slide")
def slide_schema_resource() -> str:
    """Slide readout schema.

    Provides column names and types for the slides table without requiring
    a tool call. Schema is discovered from the first run that downloads readouts
    and is identical across all runs.

    Returns:
        Markdown table of column names and types, or a helpful message if
        no schema has been discovered yet.
    """
    if "slide" not in _schema_cache:
        return (
            "Slide schema not yet available. Use download_readouts or get_readout_schema "
            "with any run_id to discover the schema."
        )
    return _format_schema_markdown(_schema_cache["slide"], "slide")


# =============================================================================
# MCP Apps: Interactive Visualization
# =============================================================================


@mcp.resource(
    RESOURCE_PATH,  # ui://chart (prefixed when mounted)
    ui=CHART_RESOURCE_UI,  # Structured UI metadata
)
def chart_view() -> str:
    """Interactive chart viewer using Chart.js.

    This resource provides a generic HTML template that can render any Chart.js
    configuration. The chart type (bar, pie, histogram, scatter, line) is determined
    by the configuration passed from the visualize_readouts tool.

    The UI uses the MCP Apps SDK to:
    - Receive chart configuration from tool results
    - Render interactive charts with Chart.js
    - Support drill-down queries via click handlers

    Returns:
        HTML content for the MCP App iframe.
    """
    return get_chart_html()


@mcp.tool(ui=ToolUI(resource_uri=VIEW_URI))  # pyright: ignore[reportCallIssue]
@_retry_on_auth_failure
def visualize_readouts(
    run_id: str,
    chart_type: Literal["bar", "pie", "histogram", "scatter", "line"],
    sql: str,
    title: str | None = None,
    x_column: str | None = None,
    y_column: str | None = None,
    color_column: str | None = None,
) -> ToolResult:
    """Generate an interactive visualization from readout data.

    Creates charts that render directly in MCP Apps-compatible clients like
    Claude Desktop. The chart is interactive with hover tooltips and optional
    drill-down capabilities. Results are automatically limited for performance.

    CRITICAL: Check schema first to discover exact column names. Do NOT guess.

    Chart Types:
    - bar: Category comparisons (e.g., cell counts by type)
    - pie: Proportional breakdown (e.g., % of cells in each region)
    - histogram: Distribution of numeric values (e.g., nucleus area distribution)
    - scatter: Spatial or correlation plots (e.g., cell positions by type)
    - line: Trends over ordered categories

    Args:
        run_id: The run ID or external ID.
        chart_type: Type of chart to generate.
        sql: SQL query to execute on cells/slides tables. The query should return
             data suitable for the chart type:
             - bar/pie/line: Two columns (label, value)
             - histogram: One numeric column to bin
             - scatter: Two or three columns (x, y, optional_color)
        title: Optional chart title.
        x_column: Column for x-axis/labels. Auto-detected from first column if not specified.
        y_column: Column for y-axis/values. Auto-detected from second column if not specified.
        color_column: Optional column for color grouping (scatter plots only).

    Returns:
        JSON chart configuration for the MCP App UI to render.

    Examples:
        # Bar chart of cell types
        visualize_readouts(
            run_id="abc-123",
            chart_type="bar",
            sql="SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS ORDER BY count DESC",
            title="Cell Distribution"
        )

        # Pie chart of tissue regions
        visualize_readouts(
            run_id="abc-123",
            chart_type="pie",
            sql="SELECT 'Carcinoma' as region, SUM(CASE WHEN IN_CARCINOMA THEN 1 ELSE 0 END) as count FROM cells
                 UNION ALL
                 SELECT 'Stroma', SUM(CASE WHEN IN_STROMA THEN 1 ELSE 0 END) FROM cells",
            title="Cells by Tissue Region"
        )

        # Scatter plot of cell positions (auto-limited for performance)
        visualize_readouts(
            run_id="abc-123",
            chart_type="scatter",
            sql="SELECT CENTROID_X, CENTROID_Y, CELL_CLASS FROM cells",
            title="Cell Spatial Distribution",
            color_column="CELL_CLASS"
        )
    """

    # Helper to wrap result in ToolResult with UI metadata
    # The meta.ui.resourceUri tells Claude Desktop to render the result with the MCP App
    def _chart_result(data: dict[str, Any]) -> ToolResult:
        return ToolResult(
            content=[types.TextContent(type="text", text=json.dumps(data))],
            meta={"ui": {"resourceUri": VIEW_URI}},
        )

    client = Client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except NotFoundException:
        return _chart_result({"error": f"Run not found: {run_id}"})

    has_slides, has_cells = _ensure_readouts_exist(resolved_id)

    if not has_slides and not has_cells:
        return _chart_result({"error": f"No readouts found for run {run_id}. Download readouts first."})

    try:
        # Get cached connection with views already configured
        con = _get_duckdb_connection(resolved_id)

        # Execute the user's query
        result = con.execute(sql)

        # Build chart configuration (automatically limited to MAX_CHART_POINTS)
        chart_config = build_chart_from_sql_result(
            result=result,
            chart_type=chart_type,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column,
        )

        return _chart_result(chart_config)

    except FileNotFoundError:
        return _chart_result({"error": f"No readouts found for run {run_id}. Download readouts first."})
    except Exception as e:
        # Provide helpful error with available columns
        error_data: dict[str, str | list[str]] = {"error": f"SQL Error: {e}"}

        cell_schema = _get_schema(resolved_id, "cell")
        slide_schema = _get_schema(resolved_id, "slide")

        hints: list[str] = []
        if cell_schema:
            col_names = [c[0] for c in cell_schema[:10]]
            hints.append(f"Cell columns: {', '.join(col_names)}...")
        if slide_schema:
            col_names = [c[0] for c in slide_schema[:10]]
            hints.append(f"Slide columns: {', '.join(col_names)}...")

        if hints:
            error_data["hints"] = hints

        return _chart_result(error_data)
