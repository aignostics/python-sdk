---
name: visualize-readouts
description: |
  Create interactive charts and visualizations from readout data (cells and slides).

  USE THIS SKILL WHEN THE USER:
  - Asks to visualize, chart, plot, graph, or display readout data
  - Wants a bar chart, pie chart, histogram, scatter plot, or line chart
  - Asks for cell positions, cell locations, spatial distribution, or cell map
  - Wants to see where cells are located on a slide
  - Asks to plot cells, show cells, or map cells
  - Requests cell type distribution or cell class breakdown visually
  - Wants to compare categories visually (e.g., "compare cell types")
  - Asks for distribution plots of numeric features (area, size, etc.)
  - Uses words like: distribution, scatter, plot, chart, graph, visualize, display, show me, map

  CRITICAL: Check the schema FIRST to discover exact column names. Do NOT guess.
---

# Visualize Readouts

Create interactive charts from readout data using the `visualize_readouts` tool.
Charts render directly in the conversation with hover tooltips and click interactions.

## When to Use This Skill

Use this skill when the user wants to:
- Visualize cell or slide data distributions (bar chart, pie chart)
- See spatial distribution of cells (scatter plot)
- Understand numeric feature distributions (histogram)
- Track trends across categories or slides (line chart)
- Create any visual representation of readout data

## Prerequisites

You need a run ID. If not provided by the user, find one with:
```
list_runs()
```

## Available Chart Types

| Chart Type | Best For | Example Use Case |
|------------|----------|------------------|
| **bar** | Comparing categories | Cell counts by type, slide metrics |
| **pie** | Showing proportions | % of cells in each tissue region |
| **histogram** | Numeric distributions | Nucleus area, slide area distributions |
| **scatter** | Spatial/correlation data | Cell positions, feature correlations |
| **line** | Ordered trends | Counts across slides, ordered categories |

## Available Tables

The `visualize_readouts` tool queries two tables:

| Table | Description | Typical Columns |
|-------|-------------|-----------------|
| `cells` | Cell-level data (many rows per slide) | CELL_CLASS, CENTROID_X, CENTROID_Y, IN_CARCINOMA, etc. |
| `slides` | Slide-level data (one row per slide) | SLIDE_ID, TOTAL_CELLS, AREA_MM2, etc. |

Both tables have an `external_id` column for per-slide filtering.

## Workflow

### Step 1: Check the Schema (REQUIRED)

Always check the schema first to discover available columns.

**Option A - Read the MCP resources (preferred, no tool call needed):**
```
Read resource: readouts://schema/cell
Read resource: readouts://schema/slide
```

Note: These static resources work after any run's readouts have been downloaded.
The schema is identical across all runs, so no run_id is needed in the URI.

**Option B - Use the tool:**
```
get_readout_schema(run_id="<RUN_ID>", readout_type="cell")
get_readout_schema(run_id="<RUN_ID>", readout_type="slide")
```

Look for:
- Classification columns (e.g., `CELL_CLASS`, `cell_type`)
- Boolean columns (e.g., `IN_CARCINOMA`, `IN_STROMA`)
- Coordinate columns (e.g., `CENTROID_X`, `CENTROID_Y`)
- Numeric feature columns (e.g., `nucleus_area`, `AREA_MM2`)

### Step 2: Create the Visualization

Use the `visualize_readouts` tool with an appropriate SQL query.

#### Bar Chart: Category Distribution

**Cell types:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="bar",
    sql="SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS ORDER BY count DESC",
    title="Cell Distribution by Type"
)
```

**Slide metrics:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="bar",
    sql="SELECT external_id, TOTAL_CELLS FROM slides ORDER BY TOTAL_CELLS DESC",
    title="Total Cells per Slide"
)
```

#### Pie Chart: Proportional Breakdown

**Tissue regions:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="pie",
    sql="""
        SELECT 'Carcinoma' as region, SUM(CASE WHEN IN_CARCINOMA THEN 1 ELSE 0 END) as cells FROM cells
        UNION ALL
        SELECT 'Stroma', SUM(CASE WHEN IN_STROMA THEN 1 ELSE 0 END) FROM cells
        UNION ALL
        SELECT 'Other', SUM(CASE WHEN NOT IN_CARCINOMA AND NOT IN_STROMA THEN 1 ELSE 0 END) FROM cells
    """,
    title="Cells by Tissue Region"
)
```

#### Histogram: Feature Distribution

**Cell feature:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="histogram",
    sql="SELECT nucleus_area FROM cells WHERE nucleus_area IS NOT NULL",
    title="Nucleus Area Distribution"
)
```

**Slide feature:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="histogram",
    sql="SELECT AREA_MM2 FROM slides WHERE AREA_MM2 IS NOT NULL",
    title="Slide Area Distribution"
)
```

#### Scatter Plot: Spatial or Correlation Data

**Cell spatial distribution:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="scatter",
    sql="SELECT CENTROID_X, CENTROID_Y, CELL_CLASS FROM cells",
    title="Cell Spatial Distribution",
    color_column="CELL_CLASS"
)
```

**Feature correlation:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="scatter",
    sql="SELECT nucleus_area, cytoplasm_area FROM cells WHERE nucleus_area IS NOT NULL",
    title="Nucleus vs Cytoplasm Area",
    x_column="nucleus_area",
    y_column="cytoplasm_area"
)
```

Note: Charts are automatically limited to 5,000 points for performance. If truncated, the response will indicate this.

#### Line Chart: Trends

**Cells per slide:**
```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="line",
    sql="SELECT external_id, COUNT(*) as cells FROM cells GROUP BY external_id ORDER BY external_id",
    title="Cell Counts per Slide"
)
```

### Step 3: Per-Slide Filtering (Optional)

To visualize data from a specific slide:

```
visualize_readouts(
    run_id="<RUN_ID>",
    chart_type="bar",
    sql="""
        SELECT CELL_CLASS, COUNT(*) as count
        FROM cells
        WHERE external_id LIKE '%slide001.tiff'
        GROUP BY CELL_CLASS
        ORDER BY count DESC
    """,
    title="Cell Distribution - Slide 001"
)
```

## Tips

- **Schema first**: Always check the schema - column names vary by application version
- **Automatic limits**: Charts are automatically limited to 5,000 points for performance (truncation is indicated in response)
- **Use aggregations**: For bar/pie/line charts, use `GROUP BY` and `COUNT(*)` or `SUM()`
- **Handle NULLs**: Filter out NULL values for histograms: `WHERE column IS NOT NULL`
- **Color by category**: For scatter plots, use `color_column` to color points by a categorical column
- **Combine with queries**: Use `query_readouts_sql` first to explore data, then visualize
- **Drill-down**: Clicking chart elements (bar/pie) can trigger follow-up queries in supported clients
- **Both tables**: You can join cells and slides tables if needed for complex analysis

## Example Conversations

**User**: "Show me a chart of cell types in my run"

```
visualize_readouts(
    run_id="abc-123",
    chart_type="bar",
    sql="SELECT CELL_CLASS, COUNT(*) as count FROM cells GROUP BY CELL_CLASS ORDER BY count DESC",
    title="Cell Type Distribution"
)
```

**User**: "Plot the spatial positions of cells colored by type"

```
visualize_readouts(
    run_id="abc-123",
    chart_type="scatter",
    sql="SELECT CENTROID_X, CENTROID_Y, CELL_CLASS FROM cells",
    title="Cell Spatial Distribution",
    color_column="CELL_CLASS"
)
```

**User**: "Compare cell counts across slides"

```
visualize_readouts(
    run_id="abc-123",
    chart_type="bar",
    sql="SELECT external_id, COUNT(*) as cells FROM cells GROUP BY external_id ORDER BY cells DESC",
    title="Cells per Slide"
)
```

**User**: "What does the slide area distribution look like?"

```
visualize_readouts(
    run_id="abc-123",
    chart_type="histogram",
    sql="SELECT AREA_MM2 FROM slides WHERE AREA_MM2 IS NOT NULL",
    title="Slide Area Distribution"
)
```

## How It Works

The `visualize_readouts` tool uses MCP Apps to render interactive charts:

1. Your SQL query runs via DuckDB on the local readout CSV files
2. Results are automatically limited to 5,000 points for performance
3. The tool returns a Chart.js configuration as JSON (with `_meta.truncated: true` if data was limited)
4. The MCP App UI (served as `ui://aignostics-platform/chart`) receives the configuration
5. Chart.js renders the interactive chart in a sandboxed iframe
6. Users can hover for tooltips and click for drill-down queries

This approach supports all chart types with a single tool and UI resource. If the response includes `_meta.truncated: true`, inform the user that the visualization shows a subset of the data.
