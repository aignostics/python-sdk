# Get started with the MCP Server

The Python SDK includes an **MCP (Model Context Protocol) server** that exposes SDK functionality to AI agents like Claude. This lets an AI assistant help you interact with the Aignostics Platform through natural conversation — managing datasets, submitting runs, and querying results.

```{include} ../partials/_get_started_signup.md
```

## Configure Claude Desktop

The MCP server runs through [uv](https://docs.astral.sh/uv/). Install uv first if you don't have it. The command below installs uv if needed, updates it if out of date (including Homebrew-managed installs), and makes it available in your current shell.

**On macOS or Linux:**

```bash
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
else
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    if [ "$(printf '%s\n' "0.6.17" "$UV_VERSION" | sort -V | head -n1)" != "0.6.17" ]; then
        echo "Updating uv to the latest version..."
        UV_PATH=$(which uv)
        if [[ "$UV_PATH" == *"brew"* ]]; then
            echo "Updating uv using Homebrew..."
            brew upgrade uv
        else
            echo "Updating uv using the installer..."
            uv self update
        fi
    else
        echo "uv is up to date"
    fi
fi
```

**On Windows (PowerShell):**

```powershell
winget install --id=Microsoft.VCRedist.2015+.x64 -e
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then add the following to your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aignostics": {
      "command": "uvx",
      "args": ["aignostics", "mcp", "run"]
    }
  }
}
```

Restart Claude Desktop after saving the configuration.

## Run the server from the command line

```bash
uvx aignostics mcp run
uvx aignostics mcp list-tools
```

## Using plugins

The MCP server supports plugins that extend it with additional tools. To run the server with a plugin installed:

```bash
# with a local plugin
uv run --with /path/to/plugin aignostics mcp run

# with a plugin from a git repository
uvx --with git+ssh://git@github.com/org/plugin aignostics mcp run
```

Plugins register themselves via Python entry points; their tools are automatically discovered and namespaced by the MCP server.

## What AI agents can do

Once configured, AI agents can help with platform operations through natural language, using the tools exposed by the SDK and any installed plugins.
