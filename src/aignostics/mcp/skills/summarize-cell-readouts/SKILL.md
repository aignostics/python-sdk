---
name: summarize-cell-readouts
description: |
  Analyze and summarize cell-level readout data from Aignostics Platform application runs.

  USE THIS SKILL WHEN THE USER:
  - Asks about cell counts, cell numbers, how many cells, total cells
  - Wants cell type distributions, cell class breakdowns, or cell statistics
  - Asks about tissue regions (carcinoma, stroma, tumor) and cell locations
  - Requests cell summaries, cell analysis, or cell composition
  - Wants to know what types of cells were detected in a slide or run
  - Needs a breakdown of cells by category, class, region, or type
  - Wants to analyze HETA (H&E Tissue Analyzer) or pathology results
  - Asks: "summarize cells", "what cells", "cell breakdown", "analyze cells"
  - Uses words like: cells, count, summary, analyze, breakdown, statistics, distribution

  CRITICAL: Check the schema FIRST to discover exact column names. Do NOT guess.
---

# Summarize Cell Readouts

Analyze cell-level data from an Aignostics Platform run to understand cell distributions,
tissue region breakdowns, and cell type statistics.

## When to Use This Skill

Use this skill when the user wants to:
- Get cell counts and statistics from a run
- Understand cell type distributions
- Analyze tissue region membership
- Get a summary or overview of cell-level results
- Compare cell populations across different categories

## Prerequisites

You need a run ID. If not provided by the user, find one with:
```
list_runs()
```

## Workflow

### Step 1: Download Readouts (if needed)

First, ensure the readout data is downloaded and cached locally:

```
download_readouts(run_id="<RUN_ID>")
```

This downloads both slide and cell readouts. The data is cached, so subsequent
queries will be fast.

### Step 2: Check the Schema (REQUIRED)

**Always check the schema first** to discover available columns. Column names vary by application version.

**Option A - Read the MCP resource (preferred, no tool call needed):**
```
Read resource: readouts://schema/cell
```

Note: This static resource works after any run's readouts have been downloaded.
The schema is identical across all runs, so no run_id is needed in the URI.

**Option B - Use the tool:**
```
get_readout_schema(run_id="<RUN_ID>", readout_type="cell")
```

Look for:
- A column for cell type/class classification
- Boolean `IN_*` columns for tissue region membership
- Columns for morphological features
- Coordinate columns for cell locations
- `external_id` - The slide identifier (added automatically, enables per-slide filtering)

### Step 3: List Available Slides (Optional)

To see which slides are available for analysis:

```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="SELECT DISTINCT external_id FROM cells"
)
```

This shows all slide identifiers in the run. Users can then filter by specific slides.

### Step 4: Get Total Cell Count

For all slides:
```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="SELECT COUNT(*) as total_cells FROM cells"
)
```

For a specific slide (use LIKE for partial matching):
```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="SELECT COUNT(*) as total_cells FROM cells WHERE external_id LIKE '%slide_name.tiff'"
)
```

### Step 5: Cell Distribution by Class

Get the breakdown of cells by their classification. Use the cell class column name from the schema:

```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="""
        SELECT
            <CELL_CLASS_COLUMN>,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
        FROM cells
        GROUP BY <CELL_CLASS_COLUMN>
        ORDER BY count DESC
    """
)
```

To filter for a specific slide, add a WHERE clause:
```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="""
        SELECT
            <CELL_CLASS_COLUMN>,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
        FROM cells
        WHERE external_id LIKE '%slide_name%'
        GROUP BY <CELL_CLASS_COLUMN>
        ORDER BY count DESC
    """
)
```

### Step 6: Tissue Region Breakdown

Count cells in each tissue region. Use the `IN_*` column names from the schema:

```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="""
        SELECT
            SUM(CASE WHEN <IN_REGION_1> THEN 1 ELSE 0 END) as region_1,
            SUM(CASE WHEN <IN_REGION_2> THEN 1 ELSE 0 END) as region_2,
            COUNT(*) as total
        FROM cells
    """
)
```

### Step 7: Cross-tabulation (Optional)

For deeper analysis, cross-tabulate cell types by tissue region:

```
query_readouts_sql(
    run_id="<RUN_ID>",
    sql="""
        SELECT
            <CELL_CLASS_COLUMN>,
            SUM(CASE WHEN <IN_REGION_1> THEN 1 ELSE 0 END) as region_1,
            SUM(CASE WHEN <IN_REGION_2> THEN 1 ELSE 0 END) as region_2,
            COUNT(*) as total
        FROM cells
        GROUP BY <CELL_CLASS_COLUMN>
        ORDER BY total DESC
    """
)
```

## Output Format

Present the results clearly:

**Cell Summary for Run: `<RUN_ID>`**

### Overview
- **Total Cells Analyzed:** X

### Cell Type Distribution
| Cell Type | Count | Percentage |
|-----------|-------|------------|
| [from query results] | N | X% |
| ... | ... | ... |

### Tissue Region Distribution
| Region | Cell Count | Percentage |
|--------|------------|------------|
| [from query results] | N | X% |
| ... | ... | ... |

### Key Findings
- [Highlight notable patterns]
- [Note any unusual distributions]

## Tips

- **Schema first**: Always check the schema - column names vary by application version
- **Per-slide filtering**: Use `WHERE external_id LIKE '%partial_name%'` to filter by slide
- **List slides first**: If the user asks about a specific slide, run `SELECT DISTINCT external_id FROM cells` to show available slides
- **Boolean columns**: The `IN_*` columns are boolean. Use `SUM(CASE WHEN col THEN 1 ELSE 0 END)` to count
- **Caching**: After the first query, subsequent queries are fast due to connection caching
- **Large datasets**: Cell readouts can have millions of rows. Percentages help understand proportions
- **NULL handling**: Some cells may have NULL values for certain columns - consider filtering or handling
- **Combine queries**: You can run multiple SQL queries efficiently thanks to connection caching
- **Path sanitization**: Path separators (`/`, `\`) in external_id are converted to underscores in storage
