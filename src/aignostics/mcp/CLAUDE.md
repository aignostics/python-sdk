# CLAUDE.md - MCP Server Module

This file provides guidance to Claude Code when working with the `mcp` module in this repository.

## Module Overview

The MCP (Model Context Protocol) module provides an MCP server implementation for AI agents to interact with Aignostics Platform readout data. It enables natural language analysis of cell and slide-level data from application runs.

## Key Components

**Core Files:**

- `_server.py` - MCP server implementation with tools and resources
- `_charts.py` - Chart.js configuration builders for MCP Apps
- `_chart_template.html` - HTML template for interactive chart rendering (loaded via `@lru_cache`)
- `_constants.py` - Shared constants (`SERVER_NAME`, `MAX_CHART_POINTS`) to avoid circular imports
- `__init__.py` - Module exports (exposes `mcp` instance for auto-discovery)

**Skills:**

- `skills/summarize-cell-readouts/SKILL.md` - Guided workflow for cell analysis
- `skills/visualize-readouts/SKILL.md` - Interactive chart visualization workflow

## Architecture

### Data Flow

```
Platform API → Download Readouts → CSV Files → DuckDB Views → SQL Queries → Results
                    ↓
              Per-slide files:
              cell_readouts_<external_id>.csv
              slide_readouts_<external_id>.csv
```

### DuckDB Integration

Readouts are stored as CSV files and queried via DuckDB views:

- **UNION ALL Pattern**: Multiple per-slide CSV files are combined using UNION ALL for optimal performance (glob patterns were found to hang on large datasets)
- **`external_id` Column**: Added automatically to enable per-slide filtering in queries
- **Connection Caching**: DuckDB connections are cached per run for performance
- **Schema Caching**: Column information is cached to speed up error messages and schema lookups

## Tools

| Tool | Purpose |
|------|---------|
| `list_runs` | List recent runs with status/item counts |
| `get_run_status` | Detailed run status with statistics |
| `get_run_items` | Items in a run with external IDs, states, errors |
| `download_readouts` | Download slide/cell CSV readouts (per-slide files) |
| `query_readouts_sql` | Execute SQL on `slides`/`cells` tables |
| `get_readout_schema` | Show column names and types |
| `get_current_user` | Show authenticated user/org |
| `visualize_readouts` | Generate interactive charts (bar, pie, histogram, scatter, line) |

## Per-Slide Filtering

Each readout file is saved with the slide's external_id in the filename:

```
cell_readouts_slide001.tiff.csv
cell_readouts_slide002.tiff.csv
```

When creating DuckDB views, an `external_id` column is added to enable filtering:

```sql
-- Query all slides
SELECT CELL_CLASS, COUNT(*) FROM cells GROUP BY CELL_CLASS

-- Query specific slide (exact match after path sanitization)
SELECT CELL_CLASS, COUNT(*) FROM cells
WHERE external_id = 'slide001.tiff'
GROUP BY CELL_CLASS

-- Query with partial match (recommended for user queries)
SELECT CELL_CLASS, COUNT(*) FROM cells
WHERE external_id LIKE '%slide001%'
GROUP BY CELL_CLASS

-- List all available slides
SELECT DISTINCT external_id FROM cells
```

**Path Sanitization**: Path separators (`/`, `\`) in external_id are converted to underscores for filesystem safety. So `a/b/c/slide.tiff` becomes `a_b_c_slide.tiff` in the filename and `external_id` column.

## Interactive Visualization (MCP Apps)

The MCP server supports interactive chart visualization using **MCP Apps** - the official standard for embedding interactive UIs in AI chat clients like Claude Desktop.

### Architecture

```
SQL Query (DuckDB) → Chart.js Config JSON → Tool Result → MCP App UI → Chart.js Rendering
```

**How One Tool + One Resource Supports All Chart Types:**

The design separates **data preparation** (Python) from **rendering** (JavaScript):

| Component | Role | Location |
|-----------|------|----------|
| `visualize_readouts` tool | Runs SQL, builds Chart.js config JSON | Python (server) |
| `ui://aignostics-platform/chart` resource | Generic HTML that renders any Chart.js config | Browser (iframe) |
| Chart.js library | Interprets config, renders interactive Canvas | Browser (from CDN) |

The Python tool returns different configs based on `chart_type`:
```python
# chart_type="bar" → {"type": "bar", "data": {...}}
# chart_type="pie" → {"type": "pie", "data": {...}}
# chart_type="scatter" → {"type": "scatter", "data": {...}}
```

The UI resource is **chart-type agnostic** - it just passes the config to Chart.js:
```javascript
new Chart(canvas, config);  // Chart.js handles bar/pie/scatter/etc based on config.type
```

### Supported Chart Types

| Chart Type | Use Case | SQL Pattern |
|------------|----------|-------------|
| `bar` | Category comparisons | `SELECT category, COUNT(*) FROM cells GROUP BY category` |
| `pie` | Proportional breakdown | Same as bar, rendered as pie |
| `histogram` | Numeric distributions | `SELECT numeric_column FROM cells` (auto-binned) |
| `scatter` | Spatial/correlations | `SELECT x, y, color_category FROM cells` |
| `line` | Ordered trends | `SELECT ordered_category, value FROM ...` |

### Data Flow

1. **User asks**: "Show me a bar chart of cell types"
2. **Claude calls**: `visualize_readouts(run_id, "bar", "SELECT CELL_CLASS, COUNT(*) FROM cells GROUP BY CELL_CLASS")`
3. **Tool executes**: SQL via DuckDB, returns Chart.js config JSON
4. **Claude Desktop**: Fetches `ui://aignostics-platform/chart` resource
5. **HTML renders**: In sandboxed iframe, receives tool result via MCP Apps protocol
6. **Chart.js renders**: Interactive chart with hover tooltips

### Example Chart Configurations

**Bar Chart (Cell Distribution):**
```json
{
  "type": "bar",
  "data": {
    "labels": ["Lymphocyte", "Carcinoma", "Fibroblast"],
    "datasets": [{
      "data": [1000, 500, 300],
      "backgroundColor": "rgba(54, 162, 235, 0.8)"
    }]
  },
  "_meta": {
    "title": "Cell Distribution"
  }
}
```

**Scatter Chart (Spatial Distribution):**
```json
{
  "type": "scatter",
  "data": {
    "datasets": [
      {"label": "Lymphocyte", "data": [{"x": 100, "y": 200}, ...], "backgroundColor": "blue"},
      {"label": "Carcinoma", "data": [{"x": 150, "y": 250}, ...], "backgroundColor": "red"}
    ]
  },
  "_meta": {
    "title": "Cell Spatial Distribution",
    "row_count": 5000,
    "truncated": true,
    "truncation_message": "Data limited to 5000 points for performance"
  }
}
```

### Security Model

- All UIs run in **sandboxed iframes** (MCP Apps standard)
- **CSP policy**: Only allows Chart.js from CDN (`cdn.jsdelivr.net`, `unpkg.com`)
- **User data stays local**: DuckDB queries local CSV files
- **Auditable communication**: All UI-to-host messages go through JSON-RPC

## Resources

MCP resources provide schema information and UI components:

- `readouts://schema/cell` - Cell readout column schema (static, discovered from first run)
- `readouts://schema/slide` - Slide readout column schema (static, discovered from first run)
- `ui://aignostics-platform/chart` - Interactive chart viewer (MCP App)

### Schema Resource Design

**Why static URIs?** Schema resources use static URIs (no `run_id` in the path) because the schema is identical across all runs. The schema is discovered from the first run that downloads readouts and then cached globally. Claude can read `readouts://schema/cell` without needing to know a specific run_id.

**Schema cache behavior:**
- Schema is cached globally by readout type (`cell` or `slide`), not per-run
- Once discovered from any run, the schema is available for all subsequent queries
- The schema cache is **NOT** cleared when DuckDB connections are cleared (e.g., when re-downloading readouts)
- This is intentional: schema is a property of the application output format, not individual runs
- If the application version changes and introduces new columns, restart the MCP server to pick up the new schema

## Usage Patterns

### Basic Analysis Workflow

```python
# 1. List available runs
list_runs(limit=5)

# 2. Download readouts for a run (also populates global schema cache)
download_readouts(run_id="abc-123")

# 3. Check available columns (schema is now cached and available via static resource)
# Option A: Use the tool
get_readout_schema(run_id="abc-123", readout_type="cell")
# Option B: Read the static resource (no run_id needed after first download)
# readouts://schema/cell

# 4. List available slides
query_readouts_sql(run_id="abc-123", sql="SELECT DISTINCT external_id FROM cells")

# 5. Run analysis queries
query_readouts_sql(
    run_id="abc-123",
    sql="""
        SELECT CELL_CLASS, COUNT(*) as count
        FROM cells
        GROUP BY CELL_CLASS
        ORDER BY count DESC
    """
)
```

### Per-Slide Analysis

```python
# Filter to specific slide
query_readouts_sql(
    run_id="abc-123",
    sql="""
        SELECT CELL_CLASS, COUNT(*) as count
        FROM cells
        WHERE external_id LIKE '%my_slide.tiff'
        GROUP BY CELL_CLASS
    """
)
```

## Configuration

**Environment Variables:**

- `AIGNOSTICS_MCP_READOUTS_DIR` - Custom directory for downloaded readouts (default: `~/aignostics_readouts`)

**Cache Structure:**

```
~/aignostics_readouts/
└── <run_id>/
    ├── cell_readouts_<external_id_1>.csv
    ├── cell_readouts_<external_id_2>.csv
    ├── slide_readouts_<external_id_1>.csv
    └── slide_readouts_<external_id_2>.csv
```

## Authentication

The MCP server uses the same authentication as the SDK:

- Tokens cached in `~/.aignostics/token.json`
- Auto-retry on `UnauthorizedException` (clears token and retries once)
- Device flow authentication if no valid token exists

## Claude Desktop Integration

### Prerequisites

**Install the SDK** (if not using uvx):
```bash
uv pip install aignostics
```

Note: Authentication is handled automatically when you first use the MCP tools. A browser window will open for device flow authentication, and the token is cached at `~/.aignostics/token.json`.

### Setup

1. **Locate your Claude Desktop config file**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the Aignostics MCP server configuration**:

   **Option A - Using uvx (recommended, no installation needed):**
   ```json
   {
     "mcpServers": {
       "aignostics": {
         "command": "uvx",
         "args": ["--with", "aignostics", "aignostics", "mcp", "run"]
       }
     }
   }
   ```

   **Option B - Using a local installation:**
   ```json
   {
     "mcpServers": {
       "aignostics": {
         "command": "aignostics",
         "args": ["mcp", "run"]
       }
     }
   }
   ```

   **Option C - Using a local development version:**
   ```json
   {
     "mcpServers": {
       "aignostics": {
         "command": "/path/to/.local/bin/uv",
         "args": [
           "run",
           "--directory",
           "/path/to/python-sdk",
           "aignostics",
           "mcp",
           "run"
         ],
         "env": {
           "AIGNOSTICS_API_ROOT": "https://platform.aignostics.com"
         }
       }
     }
   }
   ```

   Replace `/path/to/.local/bin/uv` with the output of `which uv` and `/path/to/python-sdk` with your SDK directory.

3. **Restart Claude Desktop** to load the new MCP server.

### Available Tools

Once configured, Claude Desktop will have access to these tools:

| Tool | Description |
|------|-------------|
| `list_runs` | List your recent application runs |
| `get_run_status` | Get detailed status of a specific run |
| `get_run_items` | List items/slides in a run |
| `download_readouts` | Download readout data for analysis |
| `query_readouts_sql` | Run SQL queries on readout data |
| `get_readout_schema` | Inspect available columns |
| `get_current_user` | Verify authentication |
| `visualize_readouts` | Generate interactive charts (auto-limited to 5,000 points) |

### Using Skills

Skills are guided workflows that help Claude perform complex analysis tasks. They provide step-by-step instructions for common use cases.

#### Available Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| `summarize-cell-readouts` | `skills/summarize-cell-readouts/SKILL.md` | Cell count analysis, distributions, tissue regions |
| `visualize-readouts` | `skills/visualize-readouts/SKILL.md` | Interactive chart visualization (bar, pie, scatter, etc.) |

#### Skill Discovery

Skills are discovered by Claude based on keyword matching in their YAML frontmatter `description` field. The descriptions include:
- Trigger phrases (e.g., "scatter plot", "cell positions", "visualize")
- Common user queries (e.g., "show me", "how many cells", "cell breakdown")
- **CRITICAL reminder**: Always check the schema first via resources (`readouts://schema/cell`, `readouts://schema/slide`) or `get_readout_schema()` tool

#### How to Use Skills with Claude Desktop

**Option 1: Reference the skill in your prompt (recommended)**

Simply describe what you want, and Claude will use the appropriate tools:
```
"Summarize the cells in my latest run"
"How many carcinoma cells are there in run abc-123?"
"Show me the cell distribution by tissue region"
```

**Option 2: Provide the skill as context**

For more guided analysis, paste the skill content into your conversation:

1. Open the skill file (e.g., `skills/summarize-cell-readouts/SKILL.md`)
2. Copy the content
3. Paste it into Claude Desktop with a message like:
   ```
   Please follow this workflow to analyze my run abc-123:

   [paste skill content here]
   ```

#### Skill: `summarize-cell-readouts`

Analyzes cell-level readout data from application runs. Use it when you want to:
- Get cell counts and statistics
- Understand cell type distributions
- Analyze tissue region membership
- Compare cell populations

The skill guides Claude through:
1. Downloading readouts
2. Checking the schema for available columns
3. Running SQL queries for cell distributions
4. Presenting results in a clear format

### Example Conversations

**Basic run exploration:**
```
You: What runs do I have?
Claude: [calls list_runs] You have 3 recent runs...

You: Tell me about run abc-123
Claude: [calls get_run_status] This run processed 10 slides...
```

**Cell analysis:**
```
You: Summarize the cells in run abc-123
Claude: [follows summarize-cell-readouts skill]
        [calls download_readouts, get_readout_schema, query_readouts_sql]
        Here's the cell summary:
        - Total cells: 4.5 million
        - Carcinoma cells: 36%
        - Lymphocytes: 17%
        ...
```

**Custom SQL queries:**
```
You: Show me the average nucleus area by cell type
Claude: [calls query_readouts_sql with custom SQL]
        Here are the results...
```

**Interactive visualization:**
```
You: Show me a bar chart of cell types
Claude: [calls visualize_readouts with chart_type="bar"]
        [Interactive chart appears in conversation]

You: Plot the spatial distribution of cells colored by type
Claude: [calls visualize_readouts with chart_type="scatter", color_column="CELL_CLASS"]
        [Scatter plot with colored points appears]
```

### Troubleshooting

**"Not authenticated" errors:**
- Run `aignostics user login` (or `uvx aignostics user login`) to authenticate
- Check that `~/.aignostics/token.json` exists and is not expired

**Server not appearing in Claude Desktop:**
- Verify the config file path is correct
- Check JSON syntax in the config file
- Restart Claude Desktop completely (quit and reopen)
- Check Claude Desktop logs for errors

**Slow queries:**
- First query downloads readouts (can take time for large runs)
- Subsequent queries use cached data and are fast

## Development Notes

### Adding New Tools

1. Add function with `@mcp.tool()` decorator
2. Add `@_retry_on_auth_failure` if it calls the Platform API
3. Use `Client()` directly for authenticated API access
4. Use `_resolve_run_id()` to accept both run_id and external_id
5. Return markdown-formatted strings for best display

### Performance Considerations

- **UNION ALL vs Glob**: Use UNION ALL to combine CSV files (glob patterns hang on large datasets)
- **Connection Caching**: DuckDB connections are reused per run
- **Schema Caching**: Avoid repeated DESCRIBE queries
- **Lazy Download**: Readouts are only downloaded when first queried (via `_ensure_readouts_exist()`)
- **HTML Template Caching**: Chart HTML template loaded once via `@lru_cache`
- **Chart Point Limiting**: `visualize_readouts` automatically limits data to `MAX_CHART_POINTS` (5,000) for browser performance and MCP client tool result size limits; truncation is indicated in `_meta`
- **SQL Result Limiting**: `query_readouts_sql` limits results to `MAX_SQL_RESULT_ROWS` (100) for readable text output

### Testing

Unit tests are in `tests/aignostics/mcp/server_test.py`:

- Test tools by calling the decorated functions directly
- Mock `Client` class for API calls: `patch("aignostics.mcp._server.Client")`
- Use temporary directories for readout files
- Clear caches between tests with `clean_caches` fixture
