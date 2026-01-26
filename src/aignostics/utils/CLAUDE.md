# CLAUDE.md - Utils Module

This file provides guidance to Claude Code when working with the `utils` module in this repository.

## Module Overview

The utils module provides core infrastructure and shared utilities used across all other modules:

- **Dependency Injection**: Custom DI container for service management
- **Logging**: Structured logging with multiple backends (Logfire, Sentry)
- **Configuration**: Pydantic-based settings management
- **Health Checking**: Service health monitoring
- **File System**: Path utilities and data directory management
- **Process Management**: Cross-platform subprocess utilities

## Key Components

**Core Infrastructure:**

- `_service.py` - `BaseService` abstract base class for service discovery
- `_di.py` - Dependency injection container with service discovery
- `_settings.py` - Settings management with Pydantic validation
- `_log.py` - Structured logging configuration
- `_health.py` - Health check framework
- `_user_agent.py` - Enhanced user agent generation with CI/CD context
- `boot.py` - Application bootstrap and initialization

**System Utilities:**

- `_fs.py` - File system operations and path sanitization
- `_process.py` - Process information and subprocess utilities
- `_constants.py` - Project metadata and environment detection
- `_console.py` - Rich console interface

**Navigation & GUI:**

- `_nav.py` - Navigation infrastructure (`NavItem`, `NavGroup`, `BaseNavBuilder`, `gui_get_nav_groups`)
- `_gui.py` - GUI utilities and NiceGUI helpers (conditional on `nicegui`)
- `_notebook.py` - Marimo notebook utilities (conditional on `marimo`)

**Integration Services:**

- `_sentry.py` - Sentry error monitoring (conditional on `sentry`)
- `_mcp.py` - MCP server utilities for AI agent integration

## Usage Patterns

**Service Discovery:**

```python
from aignostics.utils import locate_implementations, locate_subclasses
from aignostics.utils import BaseService

# Find all service implementations
services = locate_implementations(BaseService)

# Find all subclasses of a type
subclasses = locate_subclasses(BaseService)

# Services inherit from BaseService
class MyService(BaseService):
    def health(self) -> Health:
        return Health(status=Health.Code.UP)

    def info(self, mask_secrets=True) -> dict:
        return {"version": "1.0.0"}
```

**User Agent Generation:**

```python
from aignostics.utils import user_agent

# Generate enhanced user agent with CI/CD context
ua = user_agent()
# Format: {project_name}-python-sdk/{version} ({platform}; +{repository_url}; {pytest_test}; {github_run_url})

# Examples:
# "aignostics-python-sdk/1.0.0-beta.7 (macOS-15.0-arm64-arm-64bit; +https://github.com/aignostics/python-sdk)"
# "aignostics-python-sdk/1.0.0-beta.7 (Linux-6.1-x86_64; +https://github.com/aignostics/python-sdk; tests/platform/test_auth.py::test_login)"
# "aignostics-python-sdk/1.0.0-beta.7 (Linux-6.1-x86_64; +https://github.com/aignostics/python-sdk; +https://github.com/org/repo/actions/runs/123)"
# "aignostics-python-sdk/1.0.0-beta.7 (Linux-6.1-x86_64; +https://github.com/aignostics/python-sdk; tests/.../test_e2e.py; +https://github.com/org/repo/actions/runs/456)"

# Used automatically by:
# - SDK metadata system (platform._sdk_metadata)
# - API client HTTP headers
# - Logging context
```

**Logging:**

```python
from loguru import logger


logger.debug("Application started", extra={"correlation_id": "123"})
```

**Settings Management:**

```python
from aignostics.utils import load_settings
from pydantic import BaseModel

class MySettings(BaseModel):
    api_url: str = "https://api.example.com"

settings = load_settings(MySettings)
```

**Health Checks:**

```python
from aignostics.utils import Health, BaseService

class MyService(BaseService):
    def health(self) -> Health:
        return Health(
            status=Health.Code.UP,
            details={"database": "connected"}
        )
```

**MCP Server Utilities:**

```python
from aignostics.utils import (
    MCP_SERVER_NAME,
    MCP_TRANSPORT,
    mcp_create_server,
    mcp_run,
    mcp_list_tools,
    mcp_discover_servers,
)

# Constants
print(MCP_SERVER_NAME)  # "Central Aignostics MCP Server"
print(MCP_TRANSPORT)    # "stdio"

# Create and configure MCP server
server = mcp_create_server()
server = mcp_create_server(server_name="Custom Server")

# Run MCP server (blocking)
mcp_run()

# List available tools
tools = mcp_list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Discover all MCP servers from SDK and plugins
servers = mcp_discover_servers()
```

## Technical Implementation

**User Agent System (`_user_agent.py`):**

Enhanced user agent generation with automatic CI/CD context detection.

**Format:** `{project_name}-python-sdk/{version_full} ({platform}; +{repository_url}; {optional_parts})`

**Detection:**

- **Platform**: `platform.platform()` (e.g., `macOS-15.0-arm64-arm-64bit`, `Linux-6.1-x86_64`)
- **Repository URL**: From package metadata (`__repository_url__`)
- **Pytest**: `PYTEST_CURRENT_TEST` environment variable
- **GitHub Actions**: `GITHUB_RUN_ID` + `GITHUB_REPOSITORY` environment variables

**Usage in SDK:**

1. **SDK Metadata**: Included in every run's metadata (`platform._sdk_metadata.build_sdk_metadata()`)
2. **HTTP Headers**: Set in API client configuration for all HTTP requests
3. **Logging Context**: Available for structured logging and observability
4. **Debugging**: Provides traceability from API requests back to specific tests or workflow runs

**Key Features:**

- **Automatic Context Detection**: No manual configuration required
- **CI/CD Integration**: Captures GitHub Actions workflow context with direct links to runs
- **Test Traceability**: Links API requests to specific pytest tests
- **Platform Identification**: Detailed OS detection via `platform.platform()` for debugging
- **Lightweight**: Minimal performance overhead, simple environment variable reads

**Service Discovery System:**

- Dynamic discovery of implementations and subclasses
- Automatic module loading across the package
- Caching of discovered implementations
- No decorator needed - uses class inheritance

**Structured Logging:**

- Multiple backend support (Logfire, Sentry, Console)
- Correlation ID tracking
- Structured JSON output
- Performance monitoring integration
- Error tracking and alerting

**Settings Architecture:**

- Pydantic models for type safety
- Environment variable binding
- Validation and transformation
- Sensitive data masking
- Multi-environment support

**Health Monitoring:**

- Service-level health checks
- Dependency health aggregation
- Standardized health reporting format
- Integration with monitoring systems

## File Organization

**Core Files:**

- `__init__.py` - Public API exports and module coordination
- `boot.py` - Application initialization and setup
- `_service.py` - `BaseService` abstract base class
- `_di.py` - Dependency injection implementation
- `_settings.py` - Configuration management
- `_log.py` - Logging infrastructure
- `_health.py` - Health check framework
- `_user_agent.py` - User agent string generation

**System Utilities:**

- `_fs.py` - File system operations
- `_process.py` - Process utilities
- `_constants.py` - Environment and metadata
- `_console.py` - Console interface

**Navigation & GUI:**

- `_nav.py` - Navigation infrastructure for GUI sidebar
- `_gui.py` - GUI framework utilities (conditional on `nicegui`)
- `_notebook.py` - Marimo notebook integration (conditional on `marimo`)

**Integration Modules:**

- `_sentry.py` - Error monitoring (conditional on `sentry`)
- `_mcp.py` - MCP server utilities

## Development Notes

**Service Management:**

- Dynamic service discovery via inheritance
- Module-wide implementation scanning
- Cached discovery results for performance
- BaseService abstract class pattern

**Configuration Patterns:**

- Environment-based configuration
- Pydantic validation and transformation
- Sensitive data handling
- Development vs production settings

**Observability:**

- Structured logging with correlation IDs
- Error tracking and performance monitoring
- Health check aggregation
- Telemetry and metrics collection

**Testing Considerations:**

- Mock dependency injection for unit tests
- Isolated service testing
- Configuration override for test environments
- Health check validation
- Log output verification

**Performance Considerations:**

- Lazy service initialization
- Efficient module discovery
- Minimal overhead logging
- Optimized path operations
- Memory-efficient configuration loading

**Cross-Platform Support:**

- Windows, macOS, and Linux compatibility
- Path separator handling
- Process creation flags
- File system permissions
- Environment variable handling

## MCP Server System (`_mcp.py`)

The MCP module provides utilities for creating and running Model Context Protocol servers that expose SDK functionality to AI agents.

**Functions:**

- `mcp_discover_servers()` - Discover all FastMCP server instances from SDK and plugins
- `mcp_create_server(server_name)` - Create and configure the MCP server with discovered plugins
- `mcp_run(server_name)` - Run the MCP server using stdio transport
- `mcp_list_tools(server_name)` - List all available MCP tools

**CLI Commands:**

```bash
uv run aignostics mcp run         # Run MCP server
uv run aignostics mcp list-tools  # List all discovered tools
```

**Claude Desktop Integration:**

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

## MCP Plugin Development

Plugins can expose MCP tools by:

1. Registering via entry points in `pyproject.toml`:
   ```toml
   [project.entry-points."aignostics.plugins"]
   my_plugin = "my_plugin"
   ```

2. Creating a FastMCP instance in `_mcp.py`:
   ```python
   from fastmcp import FastMCP

   mcp = FastMCP("my_plugin")

   @mcp.tool
   def my_tool(param: str) -> str:
       """Tool description."""
       return f"Result: {param}"
   ```

3. Exporting the instance in `__init__.py`:
   ```python
   from ._mcp import mcp
   __all__ = ["mcp"]
   ```

Tools are namespaced automatically (e.g., `my_plugin_my_tool`).
