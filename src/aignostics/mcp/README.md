# Aignostics MCP Server

An MCP (Model Context Protocol) server that enables LLMs like Claude to interact with the Aignostics Platform via natural language. Query application runs, analyze cell and slide readout data, and explore pathology results through conversational AI.

## What It Can Do

### Run Management
- **List runs** - View your recent application runs with status and statistics
- **Check status** - Get detailed information about specific runs including item counts, errors, and termination reasons
- **View items** - Inspect individual items within a run and their processing states
- **Download readouts** - Fetch slide and cell readout CSV files to a local cache
- **Flexible identification** - All tools accept either run IDs (UUID) or external IDs (item/slide names)

### Readout Analysis (Powered by DuckDB)
- **SQL queries** - Run arbitrary SQL against cell and slide readout data
- **Schema inspection** - View available columns and their types
- **Cell summaries** - Get distribution statistics by cell class and tissue region
- **Filtered queries** - Query cells with complex filter expressions

### Authentication
- **User info** - Verify authentication and view organization details

## What It Cannot Do

- **Submit new runs** - This server is read-only for analysis
- **Cancel or delete runs** - No modification of existing runs
- **Upload files** - Cannot upload WSI files to the platform
- **Modify readout data** - Read-only access to downloaded readouts
- **Access other organizations' data** - Scoped to your authenticated user

## Installation

The MCP server is included with the Aignostics SDK:

```bash
# Install with MCP support
pip install "aignostics[mcp]"

# Or with uv
uv add "aignostics[mcp]"
```

## Authentication

The MCP server needs access to the Aignostics Platform API. There are two ways to authenticate:

### Option 1: Pre-authenticate via CLI (Recommended)

Run this once before using the MCP server:

```bash
# Login to staging (default)
aignostics user login

# Login to production
AIGNOSTICS_API_ROOT=https://platform.aignostics.com aignostics user login
```

The token is cached at `~/.aignostics/token.json` and auto-refreshes. The MCP server will use this cached token automatically.

### Option 2: Custom Token Cache Location

If you need tokens stored in a different location (e.g., for containerized environments), set `AIGNOSTICS_CACHE_DIR`:

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "python",
      "args": ["-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com",
        "AIGNOSTICS_CACHE_DIR": "/path/to/secure/cache"
      }
    }
  }
}
```

Then login once with the same cache dir:
```bash
AIGNOSTICS_CACHE_DIR=/path/to/secure/cache aignostics user login
```

### Option 3: Refresh Token via Environment (CI/Automated)

For fully automated setups where interactive login isn't possible:

**Set in shell profile** (`.bashrc`, `.zshrc`) - token is never in config files:
```bash
export AIGNOSTICS_REFRESH_TOKEN="$(cat ~/.aignostics/.token | cut -d: -f1)"
```

**Or use a wrapper script:**
```bash
#!/bin/bash
# ~/.local/bin/aignostics-mcp-wrapper.sh
export AIGNOSTICS_REFRESH_TOKEN=$(cat ~/.aignostics/.token 2>/dev/null | cut -d: -f1)
exec python -m aignostics.mcp
```

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "/home/you/.local/bin/aignostics-mcp-wrapper.sh",
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

> **Note**: Most users don't need Options 2 or 3. If you've logged in via `aignostics user login`, the SDK automatically uses the cached token. These options are only for isolated environments or CI systems.

### Why Can't the Server Handle Login?

The initial OAuth2 login requires opening a browser for user interaction. Since MCP servers run as background processes without a UI, browser-based login isn't possible. Once authenticated (via either method above), the server handles token refresh automatically.

---

## Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

**For production:**
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

**If installed locally (e.g., in a virtual environment):**
```json
{
  "mcpServers": {
    "aignostics": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

### VS Code with GitHub Copilot

Add to your VS Code settings (`settings.json`):

```json
{
  "github.copilot.chat.mcp.servers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

Or in your workspace `.vscode/settings.json` for project-specific configuration.

### Claude Code (CLI)

Add to your Claude Code MCP configuration at `~/.claude/claude_mcp_config.json`:

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "--with", "aignostics[mcp]", "python", "-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

**Using a local development install:**
```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uv",
      "args": ["run", "python", "-m", "aignostics.mcp"],
      "cwd": "/path/to/python-sdk",
      "env": {
        "AIGNOSTICS_API_ROOT": "https://platform-staging.aignostics.com"
      }
    }
  }
}
```

---

## Available Tools

### Core Tools

| Tool | Description |
|------|-------------|
| `list_runs` | List recent runs with optional limit and application filter |
| `get_run_status` | Get detailed status, statistics, and termination info for a run |
| `get_run_items` | List all items in a run with their states and errors |
| `download_readouts` | Download slide and cell readout CSVs to local cache |

### Query Tools

| Tool | Description |
|------|-------------|
| `query_readouts_sql` | Execute arbitrary SQL on `slides` and `cells` tables |
| `get_readout_schema` | View available columns and types for readout data |
| `query_slide_readouts` | Query slide-level measurements with optional column selection |
| `query_cell_readouts` | Query cell data with filters, column selection, and limits |
| `summarize_cells` | Get cell distribution by class and tissue region |

### Compound Skills

| Tool | Description |
|------|-------------|
| `run_summary` | Complete run overview with items, errors, and available artifacts |
| `readout_analysis` | Download readouts and generate statistical summary |

### Authentication

| Tool | Description |
|------|-------------|
| `get_current_user` | Show authenticated user email and organization |

---

## Run ID vs External ID

All tools that accept a `run_id` parameter actually accept either:

- **Run ID (UUID)**: The platform-assigned identifier for an entire run (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
- **External ID**: A user-provided identifier for an item/slide within a run (e.g., `slide_001.svs`, `patient123/sample_A`)

The server automatically resolves external IDs by searching for runs containing an item with that identifier. This allows you to work with human-readable names instead of UUIDs:

```
You: Show me the status of slide_001.svs
Claude: [calls get_run_status("slide_001.svs")]
        Found run abc-123... with slide_001.svs. Status: TERMINATED...

You: Analyze the readouts for patient123/biopsy_A
Claude: [calls readout_analysis("patient123/biopsy_A")]
        Downloaded readouts for run xyz-789...
```

**Note**: If multiple runs contain items with the same external ID, the most recent run is used.

---

## Example Conversations

### Getting Started
```
You: Show me my recent runs
Claude: [calls list_runs] Here are your 5 most recent runs...

You: What's the status of run abc-123?
Claude: [calls get_run_status] This run has completed with 10 items processed...
```

### Analyzing Readouts
```
You: Download the readouts for run abc-123 and show me the cell distribution
Claude: [calls readout_analysis] Downloaded 2 files. Here's the summary:
        - Total cells: 45,231
        - Carcinoma cells: 12,456 (27.5%)
        - Lymphocytes: 8,234 (18.2%)
        ...

You: How many cells are in carcinoma regions?
Claude: [calls query_readouts_sql with "SELECT COUNT(*) FROM cells WHERE IN_CARCINOMA = true"]
        There are 23,456 cells in carcinoma regions.

You: Show me the average nucleus area by cell class
Claude: [calls query_readouts_sql with appropriate SQL]
        Here's the breakdown...
```

### Troubleshooting
```
You: Why did run xyz-789 fail?
Claude: [calls run_summary] This run terminated with 2 user errors:
        - Item 1: Invalid file format - the uploaded file is not a valid WSI
        - Item 2: Resolution metadata missing
```

---

## Downloaded Readouts

Readouts are downloaded to a visible location in your home directory:

```
~/aignostics_readouts/{run_id}/
├── slide_readouts.csv
└── cell_readouts.csv
```

**Custom location:** Set `AIGNOSTICS_MCP_READOUTS_DIR` to change where files are stored:

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "python",
      "args": ["-m", "aignostics.mcp"],
      "env": {
        "AIGNOSTICS_MCP_READOUTS_DIR": "/path/to/your/readouts"
      }
    }
  }
}
```

The files persist between sessions. To refresh data for a run, delete its directory.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AIGNOSTICS_API_ROOT` | Platform API URL | `https://platform.aignostics.com` |
| `AIGNOSTICS_MCP_READOUTS_DIR` | Directory for downloaded readouts | `~/aignostics_readouts` |
| `AIGNOSTICS_CACHE_DIR` | Directory for auth token cache | `~/.aignostics` |
| `AIGNOSTICS_REFRESH_TOKEN` | Refresh token for non-interactive auth | None (uses cached token) |

---

## Troubleshooting

### "Authentication required" errors
Ensure you've logged in via one of:
```bash
# Option 1: CLI login (browser-based)
aignostics user login

# Option 2: Set refresh token in your MCP config
# Add AIGNOSTICS_REFRESH_TOKEN to the env section
```

### "Run not found" errors
- Verify the run ID or external ID is correct
- Ensure you're connected to the right environment (staging vs production)
- If using an external ID, check that an item with that name exists in your runs

### "No readouts found" errors
- The run may not have completed successfully
- Check `get_run_status` to see if items succeeded

### SQL query errors
- Use `get_readout_schema` to see available columns
- Column names are case-sensitive (e.g., `CELL_CLASS`, not `cell_class`)

---

## Claude Code Skills

The `skills/` directory contains workflow guides specifically for **Claude Code** (the CLI tool). These are not MCP tools - they're markdown-based instructions that guide Claude Code through common workflows when users invoke them with slash commands.

### Available Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `aignostics-quickstart` | `/aignostics-quickstart` | Introduction to the platform and available tools. Use when new to Aignostics. |
| `analyze-readouts` | `/analyze-readouts` | Step-by-step guide for analyzing cell and slide readout data with SQL examples. |
| `troubleshoot-run` | `/troubleshoot-run` | Diagnose failed runs, understand error types (USER_ERROR vs SYSTEM_ERROR), and resolve issues. |

### When Are Skills Used?

Skills are **Claude Code-specific** and are triggered when:
1. A user invokes them via slash command in Claude Code (e.g., typing `/analyze-readouts`)
2. Claude Code detects the skill is relevant based on the user's question

**Skills vs MCP Tools:**
- **MCP Tools** (`list_runs`, `query_readouts_sql`, etc.) - Executable functions the LLM calls to interact with the platform
- **Skills** - Workflow documentation that teaches the LLM *how* to use the tools effectively for specific tasks

Think of skills as "recipes" that combine multiple tool calls into coherent workflows.

### Skill File Format

Each skill is a markdown file with YAML frontmatter:

```markdown
---
name: skill-name
description: When to use this skill (used for auto-detection)
---

# Skill Title

Workflow instructions, examples, and tips...
```

The `description` field helps Claude Code automatically suggest the skill when relevant.

---

## Development

### Running the server directly
```bash
# From the SDK repository
uv run python -m aignostics.mcp

# With environment variable
AIGNOSTICS_API_ROOT=https://platform-staging.aignostics.com uv run python -m aignostics.mcp
```

### Testing tool functions
```python
from aignostics.mcp._server import list_runs, query_readouts_sql

# Test listing runs
print(list_runs(limit=3))

# Test SQL query - works with run ID or external ID
print(query_readouts_sql("your-run-id", "SELECT COUNT(*) FROM cells"))
print(query_readouts_sql("slide_001.svs", "SELECT COUNT(*) FROM cells"))  # by external ID
```

---

## License

MIT License - See the main SDK license for details.
