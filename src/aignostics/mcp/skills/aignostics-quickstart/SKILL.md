---
name: aignostics-quickstart
description: Quick introduction to the Aignostics Platform MCP tools. Use when user is new to Aignostics or asks how to get started with the platform.
---

# Aignostics Platform Quick Start

Welcome! This skill introduces you to the Aignostics Platform tools.

## What is Aignostics?

Aignostics provides AI/ML applications for computational pathology - analyzing whole slide images (WSI) from tissue samples to detect cancer, classify cells, and generate quantitative readouts.

## Available Tools

### Core Tools (Start Here)
| Tool | Purpose |
|------|---------|
| `list_runs` | See your recent runs |
| `get_run_status` | Check a specific run's progress |
| `get_current_user` | Verify your authentication |

### Readout Analysis
| Tool | Purpose |
|------|---------|
| `download_readouts` | Download results to local cache |
| `query_readouts_sql` | Run SQL queries on readout data |
| `get_readout_schema` | See available columns |
| `summarize_cells` | Quick cell distribution stats |
| `query_cell_readouts` | Filter and view cell data |
| `query_slide_readouts` | View slide-level metrics |

### Compound Skills
| Tool | Purpose |
|------|---------|
| `run_summary` | Complete run overview with items and errors |
| `readout_analysis` | Download + analyze in one step |

## Getting Started

### Step 1: Check Authentication
```
→ get_current_user()
```
Should show your email and organization.

### Step 2: List Your Runs
```
→ list_runs(limit=5)
```
Shows recent runs with their status.

### Step 3: Explore a Successful Run
Find a run with succeeded items, then:
```
→ run_summary(run_id)
→ readout_analysis(run_id)
```

### Step 4: Query the Data
Use SQL for custom analysis:
```
→ query_readouts_sql(run_id, "SELECT * FROM cells LIMIT 5")
```

## What's in the Readouts?

### Cell Readouts (`cells` table)
Each row is one detected cell with:
- `CELL_CLASS` - Classification (e.g., "Carcinoma cell", "Lymphocyte")
- `X`, `Y` - Position in the slide
- `IN_*` columns - Which tissue region (CARCINOMA, STROMA, VESSEL, etc.)
- `NUCLEUS_*` columns - Morphological features (area, roundness, etc.)

### Slide Readouts (`slides` table)
One row with ~4500 measurements including:
- `ABSOLUTE_AREA_*` - Tissue areas in μm²
- `RELATIVE_AREA_*` - Percentages
- Various quality control metrics

## Common First Questions

**"How many cells were detected?"**
```sql
SELECT COUNT(*) as total_cells FROM cells
```

**"What types of cells are there?"**
```sql
SELECT CELL_CLASS, COUNT(*) as count
FROM cells GROUP BY CELL_CLASS ORDER BY count DESC
```

**"How much of the tissue is carcinoma?"**
```sql
SELECT
    ROUND(ABSOLUTE_AREA_CARCINOMA * 100.0 / ABSOLUTE_AREA_VALID_TISSUE, 1) as carcinoma_pct
FROM slides
```

## Next Steps

- Use `/analyze-readouts` for detailed data analysis workflows
- Use `/troubleshoot-run` if you encounter errors
