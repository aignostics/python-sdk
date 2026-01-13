---
name: analyze-readouts
description: Analyze cell and slide readouts from Aignostics Platform runs. Use when user asks about readout data, cell distributions, tissue analysis, or wants to explore ML inference results.
---

# Analyzing Aignostics Readouts

This skill guides you through analyzing readout data from the Aignostics Platform.

## Prerequisites

Ensure the MCP server is connected. The following tools are available:
- `list_runs` - List recent application runs
- `get_run_status` - Check run status and statistics
- `download_readouts` - Download CSV readouts to local cache
- `query_readouts_sql` - Run arbitrary SQL queries (most powerful)
- `get_readout_schema` - Inspect available columns
- `summarize_cells` - Quick cell distribution summary

## Workflow

### 1. Find a Run with Results

```
First, list recent runs to find one with successful items:
→ list_runs(limit=5)

Look for runs with "X/Y succeeded" where X > 0.
```

### 2. Check Run Details

```
Get full details including available artifacts:
→ run_summary(run_id)

This shows items, errors, and available artifact types.
```

### 3. Download and Explore Schema

```
Download readouts and check what columns are available:
→ download_readouts(run_id)
→ get_readout_schema(run_id, "cell")
→ get_readout_schema(run_id, "slide")
```

### 4. Analyze with SQL

The `query_readouts_sql` tool is your most powerful option. It exposes:
- `cells` table - cell-level data (many rows)
- `slides` table - slide-level measurements (typically 1 row)

**Common Queries:**

Cell distribution by class:
```sql
SELECT CELL_CLASS, COUNT(*) as count
FROM cells
GROUP BY CELL_CLASS
ORDER BY count DESC
```

Cells in carcinoma regions:
```sql
SELECT CELL_CLASS, COUNT(*) as total,
       SUM(CASE WHEN IN_CARCINOMA THEN 1 ELSE 0 END) as in_carcinoma
FROM cells
GROUP BY CELL_CLASS
```

Average nucleus size by cell type:
```sql
SELECT CELL_CLASS,
       ROUND(AVG(NUCLEUS_AREA), 2) as avg_area,
       ROUND(AVG(NUCLEUS_ROUNDNESS), 3) as avg_roundness
FROM cells
GROUP BY CELL_CLASS
ORDER BY avg_area DESC
```

Slide-level tissue breakdown:
```sql
SELECT
    ABSOLUTE_AREA_VALID_TISSUE as tissue_area,
    ABSOLUTE_AREA_CARCINOMA as carcinoma_area,
    ROUND(ABSOLUTE_AREA_CARCINOMA * 100.0 / ABSOLUTE_AREA_VALID_TISSUE, 2) as carcinoma_pct
FROM slides
```

## Tips

1. **Start broad, then narrow**: Use `summarize_cells()` first, then drill down with SQL
2. **Check schema first**: Column names vary by application - always check with `get_readout_schema()`
3. **Use SQL for complex analysis**: The generic SQL tool supports JOINs, window functions, CTEs
4. **Tissue regions**: Columns starting with `IN_` indicate which tissue region a cell belongs to
5. **Nucleus features**: `NUCLEUS_*` columns contain morphological measurements

## Common Questions

**"How many cells are in the carcinoma region?"**
```sql
SELECT COUNT(*) FROM cells WHERE IN_CARCINOMA = true
```

**"What's the cell type breakdown in stroma vs carcinoma?"**
```sql
SELECT
    CELL_CLASS,
    SUM(CASE WHEN IN_CARCINOMA THEN 1 ELSE 0 END) as in_carcinoma,
    SUM(CASE WHEN IN_STROMA THEN 1 ELSE 0 END) as in_stroma
FROM cells
GROUP BY CELL_CLASS
ORDER BY in_carcinoma DESC
```

**"Show me the largest cells"**
```sql
SELECT CELL_CLASS, CELL_ID, NUCLEUS_AREA, X, Y
FROM cells
ORDER BY NUCLEUS_AREA DESC
LIMIT 10
```
