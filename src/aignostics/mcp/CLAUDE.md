# CLAUDE.md - MCP Module

This file provides comprehensive guidance to Claude Code and human engineers when working with the `mcp` module in this repository.

## Module Overview

The MCP (Model Context Protocol) module provides an MCP server that enables LLMs to interact with the Aignostics Platform via natural language. It exposes run management and readout querying capabilities through standardized MCP tools.

### Core Responsibilities

**Run Management:**

- List and inspect application runs
- Check run status, statistics, and item details
- Download artifacts and readouts
- **Flexible identification**: All tools accept either run IDs (UUID) or external IDs (item identifiers)

**Readout Analysis (powered by DuckDB):**

- Query slide-level and cell-level readout data using SQL
- Get schema information for available columns
- Summarize cell distributions and tissue regions
- Perform complex analytical queries with full SQL support

**High-Level Skills:**

- Compound operations that combine multiple tool calls
- Optimized for common LLM workflows
- Error handling with helpful guidance

### Operating Mode

The server operates in **local stdio mode**, suitable for:
- Claude Desktop
- VS Code with GitHub Copilot
- Claude Code (CLI)

Authentication uses cached tokens from the Aignostics SDK (`~/.aignostics/token.json`).

## Architecture & Design Patterns

### Module Structure

```
src/aignostics/mcp/
├── __init__.py              # Public exports (mcp, run_server)
├── __main__.py              # Entry point for `python -m aignostics.mcp`
├── _server.py               # MCP server implementation (stdio transport)
├── _settings.py             # Environment configuration
├── README.md                # User documentation
├── CLAUDE.md                # This file
└── skills/                  # Claude Code workflow skills
    ├── aignostics-quickstart/SKILL.md
    ├── analyze-readouts/SKILL.md
    └── troubleshoot-run/SKILL.md
```

### Authentication Architecture

The server uses cached authentication from the Aignostics SDK:

```
┌──────────────────────────────────────────────────────┐
│ Local stdio server                                   │
│ ┌──────────────────────────────────────────────────┐ │
│ │ MCP Tool Handler                                 │ │
│ │  - Calls _get_client()                           │ │
│ │  - Returns Client() instance                     │ │
│ │  - Client uses cached token from disk            │ │
│ │    (~/.aignostics/token.json)                    │ │
│ │  - Token auto-refreshes if expired               │ │
│ └──────────────────────────────────────────────────┘ │
│                      ↓                               │
│            Platform Client Layer                     │
│            (aignostics.platform.Client)              │
│                      ↓                               │
│         Aignostics Platform API                      │
└──────────────────────────────────────────────────────┘
```

**Auth Retry Pattern:**
- `@_retry_on_auth_failure` decorator on all tools
- Handles `UnauthorizedException` from expired tokens
- Clears cached token and retries operation once
- Transparent to tool caller

### Run ID vs External ID Resolution

All tools that accept a `run_id` parameter actually accept either:

- **Run ID (UUID)**: The platform-assigned identifier for an entire run
- **External ID**: A user-provided identifier for an item/slide within a run

The `_resolve_run_id()` helper function handles this transparently.

### Tool Design Pattern

Each tool follows a consistent pattern:

```python
@mcp.tool()
def tool_name(required_param: str, optional_param: str | None = None) -> str:
    """Tool description for LLM.

    Args:
        required_param: Description of parameter.
        optional_param: Optional description.

    Returns:
        Markdown-formatted result string.
    """
    client = _get_client()  # Gets client with cached token
    # Implementation
    return "## Result\n\nMarkdown content..."
```

### DuckDB Integration

The module uses DuckDB for high-performance SQL querying:

```python
# Direct CSV querying without loading into memory
con = duckdb.connect()
table = f"read_csv_auto('{cache_path}', header=true, skip=1)"
result = con.execute(f"SELECT * FROM {table} WHERE ...")
```

### Caching Strategy

Readouts are downloaded to a visible location in the user's home directory:

```
~/aignostics_readouts/
└── {run_id}/
    ├── slide_readouts.csv
    └── cell_readouts.csv
```

- Default path: `~/aignostics_readouts/{run_id}/`
- Configurable via `AIGNOSTICS_MCP_READOUTS_DIR` environment variable

## Tools Reference

The server exposes 12 tools organized by tier:

| Tier | Tools | Purpose |
|------|-------|---------|
| Core | `list_runs`, `get_run_status`, `get_run_items` | Basic run operations |
| Query | `query_readouts_sql`, `get_readout_schema`, `query_slide_readouts`, `query_cell_readouts`, `summarize_cells`, `download_readouts` | Data analysis |
| Auth | `get_current_user` | Authentication info |
| Skills | `run_summary`, `readout_analysis` | Compound workflows |

## Usage

### Running the Server

```bash
# Run the local stdio server
uv run python -m aignostics.mcp

# With environment specification
AIGNOSTICS_API_ROOT=https://platform.aignostics.com uv run python -m aignostics.mcp
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform.aignostics.com"
      }
    }
  }
}
```

### VS Code with GitHub Copilot

```json
{
  "github.copilot.chat.mcp.servers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform.aignostics.com"
      }
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform.aignostics.com"
      }
    }
  }
}
```

## Environment Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AIGNOSTICS_API_ROOT` | Platform API URL | `https://platform.aignostics.com` |
| `AIGNOSTICS_MCP_READOUTS_DIR` | Readout cache directory | `~/aignostics_readouts` |
| `AIGNOSTICS_CACHE_DIR` | Auth token cache directory | `~/.aignostics` |

## Dependencies

The MCP module requires:

- `mcp>=1.0.0,<2` - MCP server framework
- `duckdb` - SQL query engine (already a main SDK dependency)

Install with:

```bash
uv sync --extra mcp
```

## Testing

### Manual Testing

```python
from aignostics.mcp._server import list_runs, query_readouts_sql

# Test basic functionality
print(list_runs(limit=3))

# Test SQL queries (works with run ID or external ID)
print(query_readouts_sql("your-run-id", "SELECT COUNT(*) FROM cells"))
print(query_readouts_sql("slide_001.svs", "SELECT COUNT(*) FROM cells"))  # by external ID
```

### Verifying Tool Registration

```python
from aignostics.mcp._server import mcp

print(f"Registered tools: {len(mcp._tool_manager._tools)}")
for name in sorted(mcp._tool_manager._tools):
    print(f"  - {name}")
```

## Common Patterns

### Workflow: Analyze a Run

```
1. list_runs(limit=5)           → Find a run with succeeded items
2. run_summary(run_id)          → Get overview and available artifacts
3. download_readouts(run_id)    → Cache the data locally
4. get_readout_schema(run_id)   → See available columns
5. query_readouts_sql(...)      → Run custom analysis
```

### Workflow: Troubleshoot Failures

```
1. get_run_status(run_id)       → Check termination reason
2. get_run_items(run_id)        → See which items failed
3. Look at error messages       → Identify USER_ERROR vs SYSTEM_ERROR
```

## Lint Suppressions

The module uses several ruff noqa directives:

```python
# ruff: noqa: S608   - SQL injection (intentional for LLM queries)
# ruff: noqa: S110   - try-except-pass (graceful degradation)
# ruff: noqa: C901   - Complexity (compound tools are inherently complex)
# ruff: noqa: PLR0914, PLR1702 - Local variables and nesting
```

These are intentional design choices for an MCP tool that:
- Must allow arbitrary SQL queries
- Should gracefully handle partial failures
- Combines multiple operations in compound tools

## Future Enhancements

Potential improvements:

1. **Resources**: Add MCP resources for application/version discovery
2. **Prompts**: Pre-built prompt templates for common analyses
3. **Streaming**: Stream large query results
4. **Cache management**: Tool to clear/refresh cached readouts
5. **Run submission**: Tool to submit new runs (currently read-only)
