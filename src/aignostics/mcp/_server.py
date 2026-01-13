"""MCP Server implementation for Aignostics Platform.

Uses DuckDB for high-performance SQL querying of readout data.

Note: SQL injection warnings (S608) are intentionally suppressed - this MCP tool
is designed to allow LLMs/users to run arbitrary SQL queries on local CSV data.
"""
# ruff: noqa: S608, S110, C901, PLR0914, PLR1702

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from itertools import islice
from pathlib import Path
from typing import ParamSpec, TypeVar

import duckdb
import requests
from aignx.codegen.exceptions import UnauthorizedException

from aignostics import platform
from aignostics.platform._authentication import remove_cached_token
from aignostics.platform._client import Client

from ._settings import configure_environment, get_readout_cache_path

# Type variables for the retry decorator
P = ParamSpec("P")
R = TypeVar("R")

# Lazy import for mcp to avoid import errors if not installed
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    _msg = "MCP server requires the 'mcp' package. Install with: uv add 'mcp[cli]' or pip install 'mcp[cli]'"
    raise ImportError(_msg) from e

# Initialize MCP server
mcp = FastMCP("aignostics-readouts")

# Configure environment on module load
configure_environment()


def _clear_client_cache() -> None:
    """Clear the cached API client instances.

    This forces re-authentication on the next API call.
    """
    Client._api_client_cached = None
    Client._api_client_uncached = None


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
            # Token expired or invalid - clear caches and retry once
            remove_cached_token()
            _clear_client_cache()
            return func(*args, **kwargs)

    return wrapper


def _get_client() -> platform.Client:
    """Get an authenticated platform client.

    Returns:
        Authenticated Platform client instance.
    """
    return platform.Client()


def _resolve_run_id(client: platform.Client, identifier: str) -> str:
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
        platform.NotFoundException: If no matching run is found.
    """
    # First, try to use it directly as a run_id
    try:
        run = client.runs(identifier)
        run.details()  # Validate it exists
        return identifier
    except platform.NotFoundException:
        pass

    # Not a valid run_id, try to find a run by external_id
    runs = list(client.runs.list(external_id=identifier, page_size=1))
    if runs:
        return runs[0].run_id

    # No match found
    msg = f"No run found with run_id or external_id: {identifier}"
    raise platform.NotFoundException(msg)


# =============================================================================
# TIER 1: Core Tools
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
    client = _get_client()

    runs_iter = client.runs.list(application_id=app_id) if app_id else client.runs.list()
    runs = list(islice(runs_iter, limit))

    if not runs:
        return "No runs found."

    lines = ["| Run ID | Application | Version | State | Items |", "|--------|-------------|---------|-------|-------|"]

    for run in runs:
        details = run.details()
        stats = details.statistics
        items_summary = f"{stats.item_succeeded_count}/{stats.item_count} succeeded"
        # Show full run_id so LLM can use it directly with other tools
        lines.append(
            f"| {run.run_id} | {details.application_id} | "
            f"{details.version_number[:15]}... | {details.state.value} | {items_summary} |"
        )

    return "\n".join(lines)


@mcp.tool()
@_retry_on_auth_failure
def get_run_status(run_id: str) -> str:
    """Get detailed status of a specific run.

    Args:
        run_id: The run ID or external ID (item identifier) to check.

    Returns:
        Detailed status including state, statistics, and any errors.
    """
    client = _get_client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        details = run.details()
    except platform.NotFoundException:
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
        lines.extend(
            [
                "",
                "### Item Statistics",
                f"- Total: {stats.item_count}",
                f"- Succeeded: {stats.item_succeeded_count}",
                f"- Processing: {stats.item_processing_count}",
                f"- Pending: {stats.item_pending_count}",
                f"- User Errors: {stats.item_user_error_count}",
                f"- System Errors: {stats.item_system_error_count}",
                f"- Skipped: {stats.item_skipped_count}",
            ]
        )

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
    client = _get_client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        items = list(run.results())
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    if not items:
        return "No items found in this run."

    lines = [
        f"## Items in Run: {resolved_id}",
        "",
        "| # | External ID | State | Output | Error |",
        "|---|-------------|-------|--------|-------|",
    ]

    max_id_len = 30
    max_error_len = 50
    for i, item in enumerate(items, 1):
        external_id = item.external_id[-max_id_len:] if len(item.external_id) > max_id_len else item.external_id
        error = ""
        if item.error_message:
            if len(item.error_message) > max_error_len:
                error = item.error_message[:max_error_len] + "..."
            else:
                error = item.error_message
        lines.append(f"| {i} | ...{external_id} | {item.state.value} | {item.output.value} | {error} |")

    return "\n".join(lines)


# =============================================================================
# TIER 2: Artifact/Readout Tools
# =============================================================================


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
    client = _get_client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        items = list(run.results())
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    downloaded = []

    for item in items:
        if item.output != platform.ItemOutput.FULL:
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

            # Determine output path
            if output_dir:
                out_path = Path(output_dir) / f"{readout_type}_readouts.csv"
                out_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                out_path = get_readout_cache_path(resolved_id, readout_type)

            # Download
            if artifact.download_url:
                response = requests.get(artifact.download_url, timeout=300)
                response.raise_for_status()
                out_path.write_bytes(response.content)
                downloaded.append(f"- {readout_type}: {out_path} ({len(response.content):,} bytes)")

    if not downloaded:
        return "No readouts found in this run. The run may not have completed successfully."

    return "## Downloaded Readouts\n\n" + "\n".join(downloaded)


@mcp.tool()
@_retry_on_auth_failure
def query_readouts_sql(run_id: str, sql: str) -> str:
    """Execute an arbitrary SQL query on the readout data.

    This is a powerful tool for complex analysis. The readout tables are available as:
    - 'slides' - slide-level measurements (typically 1 row with many columns)
    - 'cells' - cell-level data (many rows with cell features)

    Args:
        run_id: The run ID or external ID (item identifier) to query readouts for.
        sql: SQL query to execute. Use 'slides' and 'cells' as table names.
             Example: "SELECT CELL_CLASS, COUNT(*) as n FROM cells GROUP BY CELL_CLASS"

    Returns:
        Query results as markdown table, or error message.
    """
    # Resolve identifier to run_id
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    # Ensure readouts are downloaded
    slide_path = get_readout_cache_path(resolved_id, "slide")
    cell_path = get_readout_cache_path(resolved_id, "cell")

    if not slide_path.exists() or not cell_path.exists():
        download_readouts(resolved_id)

    if not slide_path.exists() and not cell_path.exists():
        return f"No readouts found for run {run_id}. Download readouts first."

    try:
        # Create connection with the readout tables
        con = duckdb.connect()

        # Register tables if files exist
        if slide_path.exists():
            con.execute(f"CREATE VIEW slides AS SELECT * FROM read_csv_auto('{slide_path}', header=true, skip=1)")
        if cell_path.exists():
            con.execute(f"CREATE VIEW cells AS SELECT * FROM read_csv_auto('{cell_path}', header=true, skip=1)")

        # Execute the user's query
        result = con.execute(sql)
        rows = result.fetchall()
        columns = result.description

        if not rows:
            return "Query returned no results."

        # Format as markdown
        col_names = [col[0] for col in columns]
        header = "| " + " | ".join(col_names) + " |"
        separator = "| " + " | ".join(["---"] * len(col_names)) + " |"

        lines = [header, separator]
        max_rows = 100
        for i, row in enumerate(rows):
            if i >= max_rows:
                lines.append(f"\n*Showing first {max_rows} of {len(rows)} rows*")
                break
            row_str = "| " + " | ".join(str(v) if v is not None else "" for v in row) + " |"
            lines.append(row_str)

        return "\n".join(lines)

    except Exception as e:
        # Provide helpful error with available columns
        error_msg = f"SQL Error: {e}\n\n"

        try:
            con = duckdb.connect()
            if cell_path.exists():
                cell_table = f"read_csv_auto('{cell_path}', header=true, skip=1)"
                cols = con.execute(f"DESCRIBE SELECT * FROM {cell_table}").fetchall()
                error_msg += f"**Available cell columns:** {', '.join(c[0] for c in cols[:20])}...\n"
            if slide_path.exists():
                slide_table = f"read_csv_auto('{slide_path}', header=true, skip=1)"
                cols = con.execute(f"DESCRIBE SELECT * FROM {slide_table}").fetchall()
                error_msg += f"**Available slide columns:** {', '.join(c[0] for c in cols[:20])}...\n"
        except Exception:
            pass

        return error_msg


@mcp.tool()
@_retry_on_auth_failure
def get_readout_schema(run_id: str, readout_type: str = "cell") -> str:
    """Get the schema (column names and types) of a readout file.

    Args:
        run_id: The run ID or external ID (item identifier) to get schema for.
        readout_type: Type of readout ('slide' or 'cell', default 'cell').

    Returns:
        Table schema with column names and types.
    """
    # Resolve identifier to run_id
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    cache_path = get_readout_cache_path(resolved_id, readout_type)

    if not cache_path.exists():
        download_readouts(resolved_id)

    if not cache_path.exists():
        return f"No {readout_type} readouts found for run {run_id}."

    try:
        con = duckdb.connect()
        result = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{cache_path}', header=true, skip=1)")
        rows = result.fetchall()

        lines = [
            f"## {readout_type.title()} Readout Schema",
            "",
            "| Column | Type |",
            "|--------|------|",
        ]
        lines.extend(f"| {row[0]} | {row[1]} |" for row in rows)

        lines.append(f"\n*Total columns: {len(rows)}*")
        return "\n".join(lines)

    except Exception as e:
        return f"Error reading schema: {e}"


@mcp.tool()
@_retry_on_auth_failure
def query_slide_readouts(run_id: str, columns: str | None = None) -> str:
    """Query slide-level readout measurements.

    Args:
        run_id: The run ID or external ID (item identifier) to query readouts for.
        columns: Comma-separated list of columns to include (optional).

    Returns:
        Slide readout data as markdown.
    """
    # Resolve identifier to run_id
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    cache_path = get_readout_cache_path(resolved_id, "slide")

    if not cache_path.exists():
        download_readouts(resolved_id)

    if not cache_path.exists():
        return f"No slide readouts found for run {run_id}."

    try:
        con = duckdb.connect()

        if columns:
            col_list = ", ".join(c.strip() for c in columns.split(","))
            sql = f"SELECT {col_list} FROM read_csv_auto('{cache_path}', header=true, skip=1)"
        else:
            sql = f"SELECT * FROM read_csv_auto('{cache_path}', header=true, skip=1)"

        result = con.execute(sql)
        rows = result.fetchall()
        col_names = [col[0] for col in result.description]

        # For slide readouts (usually 1 row), show as key-value pairs
        max_metrics = 50
        if len(rows) == 1:
            lines = ["## Slide Readouts", ""]
            row = rows[0]
            shown = 0
            for key, value in zip(col_names, row, strict=True):
                if shown >= max_metrics:
                    lines.append(f"\n*Showing first {max_metrics} of {len(col_names)} measurements*")
                    break
                if value is not None:
                    lines.append(f"- **{key}:** {value}")
                    shown += 1
            return "\n".join(lines)

        # Multiple rows - show as table
        header = "| " + " | ".join(col_names) + " |"
        separator = "| " + " | ".join(["---"] * len(col_names)) + " |"
        lines = ["## Slide Readouts", "", header, separator]
        for row in rows:
            row_str = "| " + " | ".join(str(v) if v is not None else "" for v in row) + " |"
            lines.append(row_str)
        return "\n".join(lines)

    except Exception as e:
        return f"Error querying slide readouts: {e}"


@mcp.tool()
@_retry_on_auth_failure
def query_cell_readouts(
    run_id: str,
    filter_expr: str | None = None,
    columns: str | None = None,
    limit: int = 100,
) -> str:
    """Query cell-level readout data with optional filtering.

    Args:
        run_id: The run ID or external ID (item identifier) to query readouts for.
        filter_expr: SQL WHERE clause (e.g., "IN_CARCINOMA = true", "CELL_CLASS = 'Carcinoma cell'").
        columns: Comma-separated list of columns to include.
        limit: Maximum number of rows to return (default 100).

    Returns:
        Filtered cell data as markdown table.
    """
    # Resolve identifier to run_id
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    cache_path = get_readout_cache_path(resolved_id, "cell")

    if not cache_path.exists():
        download_readouts(resolved_id)

    if not cache_path.exists():
        return f"No cell readouts found for run {run_id}."

    try:
        con = duckdb.connect()
        table = f"read_csv_auto('{cache_path}', header=true, skip=1)"

        # Get total count
        total_result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        total = total_result[0] if total_result else 0

        # Build query
        col_clause = columns or "*"
        where_clause = f"WHERE {filter_expr}" if filter_expr else ""

        # Get filtered count if filtering
        if filter_expr:  # noqa: SIM108
            filtered_result = con.execute(f"SELECT COUNT(*) FROM {table} {where_clause}").fetchone()
            filtered = filtered_result[0] if filtered_result else 0
        else:
            filtered = total

        # Execute main query
        sql = f"SELECT {col_clause} FROM {table} {where_clause} LIMIT {limit}"
        result = con.execute(sql)
        rows = result.fetchall()
        col_names = [col[0] for col in result.description]

        # Format output
        header = f"## Cell Readouts\n\n*Showing {len(rows)} of {filtered:,} cells"
        if filter_expr:
            header += f" (filtered from {total:,} total)"
        header += "*\n"

        if not rows:
            return header + "\nNo cells match the filter criteria."

        table_header = "| " + " | ".join(col_names) + " |"
        separator = "| " + " | ".join(["---"] * len(col_names)) + " |"
        lines = [header, table_header, separator]
        for row in rows:
            row_str = "| " + " | ".join(str(v) if v is not None else "" for v in row) + " |"
            lines.append(row_str)

        return "\n".join(lines)

    except Exception as e:
        return f"Error querying cell readouts: {e}\n\nUse get_readout_schema() to see available columns."


@mcp.tool()
@_retry_on_auth_failure
def summarize_cells(run_id: str, group_by: str = "CELL_CLASS") -> str:
    """Get summary statistics of cell readouts.

    Args:
        run_id: The run ID or external ID (item identifier) to summarize.
        group_by: Column to group by (default: CELL_CLASS).

    Returns:
        Summary statistics including counts and distributions.
    """
    # Resolve identifier to run_id
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    cache_path = get_readout_cache_path(resolved_id, "cell")

    if not cache_path.exists():
        download_readouts(resolved_id)

    if not cache_path.exists():
        return f"No cell readouts found for run {run_id}."

    try:
        con = duckdb.connect()
        table = f"read_csv_auto('{cache_path}', header=true, skip=1)"

        # Get total count
        total_result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        total = total_result[0] if total_result else 0

        lines = [
            f"## Cell Summary for Run {resolved_id[:8]}...",
            "",
            f"**Total Cells:** {total:,}",
            "",
        ]

        # Group by specified column
        try:
            result = con.execute(f"""
                SELECT {group_by}, COUNT(*) as count
                FROM {table}
                GROUP BY {group_by}
                ORDER BY count DESC
            """)
            rows = result.fetchall()

            lines.extend([f"### Distribution by {group_by}", ""])
            for value, count in rows:
                pct = count / total * 100
                lines.append(f"- **{value}:** {count:,} ({pct:.1f}%)")
        except Exception:
            lines.append(f"*Column '{group_by}' not found or invalid*")

        # Add tissue region distribution
        try:
            # Get columns that start with IN_
            cols_result = con.execute(f"DESCRIBE SELECT * FROM {table}")
            all_cols = [row[0] for row in cols_result.fetchall()]
            tissue_cols = [c for c in all_cols if c.startswith("IN_")]

            if tissue_cols:
                lines.extend(["", "### Cells by Tissue Region"])
                for col in tissue_cols:
                    try:
                        count_result = con.execute(f"SELECT SUM(CAST({col} AS INTEGER)) FROM {table}").fetchone()
                        count = count_result[0] if count_result else None
                        if count is not None and total > 0:
                            pct = count / total * 100
                            region = col.replace("IN_", "").replace("_", " ").title()
                            lines.append(f"- **{region}:** {count:,} ({pct:.1f}%)")
                    except Exception:
                        pass
        except Exception:
            pass

        return "\n".join(lines)

    except Exception as e:
        return f"Error summarizing cells: {e}"


# =============================================================================
# TIER 3: Authentication Info
# =============================================================================


@mcp.tool()
@_retry_on_auth_failure
def get_current_user() -> str:
    """Get information about the currently authenticated user.

    Returns:
        User email and organization information.
    """
    client = _get_client()

    try:
        me = client.me()
        return f"**User:** {me.user.email}\n**Organization:** {me.organization.name}"
    except Exception as e:
        return f"Not authenticated or error: {e}"


# =============================================================================
# SKILLS: High-Level Compound Operations
# =============================================================================


@mcp.tool()
@_retry_on_auth_failure
def run_summary(run_id: str) -> str:
    """Get a comprehensive summary of a run including status, items, and errors.

    This is a high-level skill that combines multiple queries into one.

    Args:
        run_id: The run ID or external ID (item identifier) to summarize.

    Returns:
        Complete run summary with all details.
    """
    client = _get_client()

    try:
        resolved_id = _resolve_run_id(client, run_id)
        run = client.runs(resolved_id)
        details = run.details()
        items = list(run.results())
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    lines = [
        f"# Run Summary: {resolved_id}",
        "",
        "## Overview",
        f"- **Application:** {details.application_id}",
        f"- **Version:** {details.version_number}",
        f"- **State:** {details.state.value}",
    ]

    if details.termination_reason:
        lines.append(f"- **Termination:** {details.termination_reason.value}")
    if details.error_message:
        lines.append(f"- **Error:** {details.error_message}")

    # Statistics
    if details.statistics:
        stats = details.statistics
        lines.extend(
            [
                "",
                "## Statistics",
                f"- **Total Items:** {stats.item_count}",
                f"- **Succeeded:** {stats.item_succeeded_count}",
                f"- **Failed:** {stats.item_user_error_count + stats.item_system_error_count}",
                f"- **Skipped:** {stats.item_skipped_count}",
            ]
        )

    # Item details
    max_error_preview = 100
    if items:
        lines.extend(["", "## Items"])
        for i, item in enumerate(items, 1):
            status_icon = "✓" if item.termination_reason == platform.ItemTerminationReason.SUCCEEDED else "✗"
            name = item.external_id.split("/")[-1][:40]
            lines.append(f"{i}. {status_icon} `{name}`")
            if item.error_message:
                if len(item.error_message) > max_error_preview:
                    error_short = item.error_message[:max_error_preview] + "..."
                else:
                    error_short = item.error_message
                lines.append(f"   - Error: {error_short}")

    # Available artifacts
    successful_items = [it for it in items if it.output == platform.ItemOutput.FULL]
    if successful_items:
        artifact_names: set[str] = set()
        for item in successful_items:
            artifact_names.update(art.name for art in item.output_artifacts)
        lines.extend(["", "## Available Artifacts"])
        lines.extend(f"- {name}" for name in sorted(artifact_names))

    return "\n".join(lines)


@mcp.tool()
@_retry_on_auth_failure
def readout_analysis(run_id: str) -> str:
    """Download readouts and generate a complete analysis.

    This is a high-level skill that downloads readouts and provides statistics.

    Args:
        run_id: The run ID or external ID (item identifier) to analyze.

    Returns:
        Downloaded file paths and statistical summary.
    """
    # Resolve identifier to run_id first
    client = _get_client()
    try:
        resolved_id = _resolve_run_id(client, run_id)
    except platform.NotFoundException:
        return f"Run not found: {run_id}"

    # Download readouts
    download_result = download_readouts(resolved_id)

    if "No readouts found" in download_result:
        return str(download_result)

    lines = [download_result, ""]

    # Add cell summary
    cell_summary = summarize_cells(resolved_id)
    lines.append(cell_summary)

    # Add slide summary (key metrics only)
    slide_path = get_readout_cache_path(resolved_id, "slide")
    if slide_path.exists():
        try:
            con = duckdb.connect()
            table = f"read_csv_auto('{slide_path}', header=true, skip=1)"

            lines.extend(["", "## Key Slide Metrics"])

            key_metrics = [
                "ABSOLUTE_AREA",
                "ABSOLUTE_AREA_VALID_TISSUE",
                "ABSOLUTE_AREA_CARCINOMA",
                "ABSOLUTE_AREA_STROMA",
            ]
            for metric in key_metrics:
                try:
                    value_result = con.execute(f"SELECT {metric} FROM {table}").fetchone()
                    value = value_result[0] if value_result else None
                    if value is not None:
                        lines.append(f"- **{metric.replace('_', ' ').title()}:** {value:,.0f} μm²")
                except Exception:
                    pass
        except Exception:
            pass

    return "\n".join(lines)


# =============================================================================
# Server Entry Point
# =============================================================================


def run_server() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
