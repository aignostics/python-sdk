"""Chart configuration and HTML generation for MCP Apps visualization.

This module provides Chart.js configuration builders and HTML templates for
interactive chart visualization in MCP Apps-compatible clients like Claude Desktop.

Architecture:
    SQL Query (DuckDB) -> Chart.js Config JSON -> Tool Result -> MCP App UI -> Chart.js Rendering

The design separates data preparation (Python) from rendering (JavaScript):
- visualize_readouts tool: Runs SQL, builds Chart.js config JSON
- ui://aignostics-platform/chart resource: Generic HTML that renders any Chart.js config
- Chart.js library: Interprets config, renders interactive SVG/Canvas
"""

# ruff: noqa: PLR0913, PLR0917, C901, DOC201

from __future__ import annotations

import contextlib
from functools import lru_cache
from importlib import resources
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    import duckdb

from itertools import starmap

from aignostics.mcp._constants import MAX_CHART_POINTS, SERVER_NAME

# Chart types supported by this module
ChartType = Literal["bar", "pie", "histogram", "scatter", "line"]

# View URI for the chart MCP App resource
# When the server is mounted with prefix=SERVER_NAME, resources are prefixed too.
# The tool metadata references this full URI so clients can find the resource.
VIEW_URI = f"ui://{SERVER_NAME}/chart"

# Local resource path (without prefix) for registering on the server
# FastMCP will prefix this with SERVER_NAME when mounted
RESOURCE_PATH = "ui://chart"


@lru_cache(maxsize=1)
def get_chart_html() -> str:
    """Get the chart HTML template, loading from file on first access."""
    return resources.files("aignostics.mcp").joinpath("_chart_template.html").read_text()


def build_chart_config(
    chart_type: ChartType,
    labels: list[str] | None = None,
    values: list[float | int] | None = None,
    x_values: list[float | int] | None = None,
    y_values: list[float | int] | None = None,
    color_values: list[str] | None = None,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    bins: int = 20,
) -> dict[str, Any]:
    """Build Chart.js configuration for any supported chart type.

    Args:
        chart_type: Type of chart ('bar', 'pie', 'histogram', 'scatter', 'line').
        labels: Category labels for bar/pie/line charts.
        values: Numeric values for bar/pie/line/histogram charts.
        x_values: X-axis values for scatter charts.
        y_values: Y-axis values for scatter charts.
        color_values: Color grouping labels for scatter charts.
        title: Optional chart title.
        x_label: Optional x-axis label.
        y_label: Optional y-axis label.
        bins: Number of bins for histogram (default 20).

    Returns:
        Chart.js configuration dictionary.
    """
    match chart_type:
        case "bar":
            return _bar_config(labels or [], values or [], title, x_label, y_label)
        case "pie":
            return _pie_config(labels or [], values or [], title)
        case "histogram":
            return _histogram_config(values or [], bins, title, x_label)
        case "scatter":
            return _scatter_config(x_values or [], y_values or [], color_values, title, x_label, y_label)
        case "line":
            return _line_config(labels or [], values or [], title, x_label, y_label)


def _bar_config(
    labels: list[str],
    values: list[float | int],
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> dict[str, Any]:
    """Build bar chart configuration."""
    config: dict[str, Any] = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{"data": values, "backgroundColor": "rgba(54, 162, 235, 0.8)", "borderWidth": 1}],
        },
        "options": {
            "responsive": True,
            "plugins": {"legend": {"display": False}},
            "scales": {"y": {"beginAtZero": True}},
        },
        "_meta": {"title": title},
    }
    if x_label:
        config["options"]["scales"]["x"] = {"title": {"display": True, "text": x_label}}
    if y_label:
        config["options"]["scales"]["y"]["title"] = {"display": True, "text": y_label}
    return config


def _pie_config(labels: list[str], values: list[float | int], title: str | None) -> dict[str, Any]:
    """Build pie chart configuration."""
    return {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [{"data": values, "backgroundColor": _generate_colors(len(labels)), "borderWidth": 2}],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "right"}}},
        "_meta": {"title": title},
    }


def _histogram_config(
    values: list[float | int],
    bins: int,
    title: str | None,
    x_label: str | None,
) -> dict[str, Any]:
    """Build histogram configuration (rendered as bar chart)."""
    if not values:
        return _empty_chart_config("No data available for histogram")

    min_val, max_val = min(values), max(values)

    if min_val == max_val:
        bin_labels, counts = [f"{min_val:.2f}"], [len(values)]
    else:
        bin_width = (max_val - min_val) / bins
        bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
        counts = [0] * bins
        for v in values:
            bin_idx = min(int((v - min_val) / bin_width), bins - 1)
            counts[bin_idx] += 1
        bin_labels = [f"{bin_edges[i]:.1f}-{bin_edges[i + 1]:.1f}" for i in range(bins)]

    return {
        "type": "bar",
        "data": {
            "labels": bin_labels,
            "datasets": [
                {
                    "data": counts,
                    "backgroundColor": "rgba(75, 192, 192, 0.8)",
                    "borderWidth": 1,
                    "barPercentage": 1.0,
                    "categoryPercentage": 1.0,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {"legend": {"display": False}},
            "scales": {
                "x": {"title": {"display": bool(x_label), "text": x_label or ""}},
                "y": {"beginAtZero": True, "title": {"display": True, "text": "Count"}},
            },
        },
        "_meta": {"title": title, "subtitle": f"{len(values):,} values in {bins} bins"},
    }


def _scatter_config(
    x_values: list[float | int],
    y_values: list[float | int],
    color_values: list[str] | None,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> dict[str, Any]:
    """Build scatter chart configuration."""
    if not x_values or not y_values:
        return _empty_chart_config("No data available for scatter plot")

    # Round coordinates to 2 decimal places to reduce JSON size
    def pt(x: float, y: float) -> dict[str, float]:
        return {"x": round(float(x), 2), "y": round(float(y), 2)}

    if color_values:
        unique_labels = list(set(color_values))
        colors = _generate_colors(len(unique_labels))
        datasets = []
        for i, label in enumerate(unique_labels):
            points = [pt(x, y) for x, y, c in zip(x_values, y_values, color_values, strict=True) if c == label]
            datasets.append({"label": str(label), "data": points, "backgroundColor": colors[i], "pointRadius": 4})
    else:
        points = list(starmap(pt, zip(x_values, y_values, strict=True)))
        datasets = [{"data": points, "backgroundColor": "rgba(54, 162, 235, 0.6)", "pointRadius": 4}]

    return {
        "type": "scatter",
        "data": {"datasets": datasets},
        "options": {
            "responsive": True,
            "plugins": {"legend": {"display": bool(color_values)}},
            "scales": {
                "x": {"title": {"display": bool(x_label), "text": x_label or ""}},
                "y": {"title": {"display": bool(y_label), "text": y_label or ""}},
            },
        },
        "_meta": {"title": title, "subtitle": f"{len(x_values):,} points"},
    }


def _line_config(
    labels: list[str],
    values: list[float | int],
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> dict[str, Any]:
    """Build line chart configuration."""
    if not labels or not values:
        return _empty_chart_config("No data available for line chart")

    return {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{"data": values, "borderColor": "rgba(255, 99, 132, 1)", "fill": False, "tension": 0.1}],
        },
        "options": {
            "responsive": True,
            "plugins": {"legend": {"display": False}},
            "scales": {
                "x": {"title": {"display": bool(x_label), "text": x_label or ""}},
                "y": {"title": {"display": bool(y_label), "text": y_label or ""}},
            },
        },
        "_meta": {"title": title},
    }


def build_chart_from_sql_result(
    result: duckdb.DuckDBPyConnection,
    chart_type: ChartType,
    title: str | None = None,
    x_column: str | None = None,
    y_column: str | None = None,
    color_column: str | None = None,
) -> dict[str, Any]:
    """Build a chart configuration from a DuckDB query result.

    This function transforms SQL query results into Chart.js configurations.
    It auto-detects columns if not specified. Results are automatically limited
    to MAX_CHART_POINTS for performance.

    Args:
        result: DuckDB query result.
        chart_type: Type of chart to generate.
        title: Optional chart title.
        x_column: Column for x-axis/labels (auto-detected if None).
        y_column: Column for y-axis/values (auto-detected if None).
        color_column: Column for color grouping (scatter only).

    Returns:
        Chart.js configuration dictionary. Includes truncation info in '_meta' if data was limited.
    """
    rows = result.fetchmany(MAX_CHART_POINTS)
    truncated = result.fetchone() is not None
    columns = [col[0] for col in result.description] if result.description else []

    if not rows or not columns:
        return _empty_chart_config("Query returned no results")

    # Auto-detect columns
    if not x_column:
        x_column = columns[0]
    if not y_column:
        y_column = columns[1] if len(columns) > 1 else columns[0]

    # Get column indices
    try:
        x_idx = columns.index(x_column)
    except ValueError:
        return _empty_chart_config(f"Column '{x_column}' not found in result")

    try:
        y_idx = columns.index(y_column)
    except ValueError:
        return _empty_chart_config(f"Column '{y_column}' not found in result")

    color_idx = None
    if color_column:
        with contextlib.suppress(ValueError):
            color_idx = columns.index(color_column)

    # Extract data
    x_values = [row[x_idx] for row in rows]
    y_values = [row[y_idx] for row in rows]
    color_values = [str(row[color_idx]) for row in rows] if color_idx is not None else None

    # Build chart using unified function
    if chart_type == "scatter":
        config = build_chart_config(
            chart_type="scatter",
            x_values=[float(x) if x is not None else 0 for x in x_values],
            y_values=[float(y) if y is not None else 0 for y in y_values],
            color_values=color_values,
            title=title,
            x_label=x_column,
            y_label=y_column,
        )
    elif chart_type == "histogram":
        config = build_chart_config(
            chart_type="histogram",
            values=[float(y) if y is not None else 0 for y in y_values],
            title=title,
            x_label=y_column,
        )
    else:
        # bar, pie, line all use labels + values
        config = build_chart_config(
            chart_type=chart_type,
            labels=[str(x) for x in x_values],
            values=[float(y) if y is not None else 0 for y in y_values],
            title=title,
            x_label=x_column,
            y_label=y_column,
        )

    # Add row count and truncation info to metadata
    if "_meta" not in config:
        config["_meta"] = {}
    config["_meta"]["row_count"] = len(rows)
    if truncated:
        config["_meta"]["truncated"] = True
        config["_meta"]["truncation_message"] = f"Data limited to {len(rows)} points for performance"

    return config


def _generate_colors(n: int) -> list[str]:
    """Generate a list of distinct colors for chart elements."""
    palette = [
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 99, 132, 0.8)",
        "rgba(75, 192, 192, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(153, 102, 255, 0.8)",
        "rgba(255, 159, 64, 0.8)",
        "rgba(199, 199, 199, 0.8)",
        "rgba(83, 102, 255, 0.8)",
        "rgba(255, 99, 255, 0.8)",
        "rgba(99, 255, 132, 0.8)",
    ]
    if n <= len(palette):
        return palette[:n]

    colors = list(palette)
    for i in range(len(palette), n):
        hue = (i * 137.5) % 360
        colors.append(f"hsla({hue}, 70%, 60%, 0.8)")
    return colors


def _empty_chart_config(message: str) -> dict[str, Any]:
    """Create an error configuration when no data is available."""
    return {"error": message, "_meta": {"title": "No Data"}}
