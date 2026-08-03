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
    async def health(self) -> Health:
        return Health(status=Health.Code.UP)

    async def info(self, mask_secrets=True) -> dict:
        return {"version": "1.0.0"}
```

**FastAPI Dependency Injection:**

`BaseService.get_service()` returns a cached FastAPI dependency function that yields a service instance.
The same function object is returned on repeated calls (required for `dependency_overrides` in tests).

```python
from typing import Annotated
from fastapi import Depends
from aignostics.my_module._service import Service


@router.get("/endpoint")
async def endpoint(service: Annotated[Service, Depends(Service.get_service())]):
    return service.do_something()
```

**Settings Accessor:**

`BaseService.settings()` exposes `self._settings` as a public method for callers that need access
to the service's configuration object.

```python
service = MyService()
settings = service.settings()  # Returns the BaseSettings instance
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
from pydantic_settings import BaseSettings


class MySettings(BaseSettings):  # load_settings is bound to BaseSettings, not pydantic.BaseModel
    api_url: str = "https://api.example.com"


settings = load_settings(MySettings)
```

**Health Checks:**

```python
from aignostics.utils import Health, BaseService


class MyService(BaseService):
    async def health(self) -> Health:
        return Health(status=Health.Code.UP, details={"database": "connected"})
```

## User Agent Detection (`_user_agent.py`)

`user_agent()` auto-detects CI/CD context (no configuration). The optional
trailing parts of the format above come from environment: `PYTEST_CURRENT_TEST`
(pytest), `GITHUB_RUN_ID` + `GITHUB_REPOSITORY` (GitHub Actions). Platform is
`platform.platform()`, repository URL is read from package metadata
(`__repository_url__`).

## MCP Server System (`_mcp.py`)

The MCP module provides utilities for creating and running Model Context Protocol servers that expose SDK functionality to AI agents. All exported via `aignostics.utils`. Constants: `MCP_SERVER_NAME` (`"Central Aignostics MCP Server"`), `MCP_TRANSPORT` (`"stdio"`).

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
