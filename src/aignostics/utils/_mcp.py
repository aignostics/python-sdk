"""MCP (Model Context Protocol) server utilities.

This module provides utilities for creating and running a central MCP server
that exposes tools from the Aignostics SDK and any installed plugins. It
includes functions to discover MCP servers, create a combined server, run
the server, and list available tools.

Example:
    # Start MCP server via CLI
    uv run aignostics mcp run

    # List available tools
    uv run aignostics mcp list-tools

    # Use programmatically
    from aignostics.utils import mcp_create_server, mcp_run, mcp_list_tools

    server = mcp_create_server()
    mcp_run()
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import FastMCP
from loguru import logger

from ._constants import __version__
from ._di import locate_implementations

MCP_SERVER_NAME = "Central Aignostics MCP Server"
MCP_TRANSPORT = "stdio"


def mcp_discover_servers() -> list[FastMCP]:
    """Discover all FastMCP server instances from SDK and plugins.

    Uses a plugin discovery mechanism which:
    - Searches the main aignostics package
    - Searches all registered plugin packages via entry points

    Returns:
        list[FastMCP]: List of discovered FastMCP server instances.
    """
    servers = locate_implementations(FastMCP)
    logger.debug(f"Discovered {len(servers)} MCP servers")
    return servers


def mcp_create_server(server_name: str = MCP_SERVER_NAME) -> FastMCP:
    """Create and configure the MCP server with all discovered plugins mounted.

    Creates a new FastMCP server instance and mounts all discovered MCP servers
    from the SDK and plugins. Each mounted server's tools are namespaced
    automatically using FastMCP's built-in prefix feature.

    Args:
        server_name: Human-readable name for the MCP server.

    Returns:
        FastMCP: Configured MCP server ready to run.
    """
    mcp = FastMCP(name=server_name, version=__version__)

    # Mount discovered servers
    servers = mcp_discover_servers()
    seen_names: set[str] = set()
    count = 0

    for server in servers:
        if server is not mcp:  # Don't mount self
            if server.name in seen_names:
                logger.warning(f"Duplicate MCP server name '{server.name}' - skipping to avoid tool collision")
                continue
            seen_names.add(server.name)
            logger.info(f"Mounting MCP server: {server.name}")
            mcp.mount(server, prefix=server.name)
            count += 1

    logger.info(f"Mounted {count} MCP servers")
    return mcp


def mcp_run(server_name: str = MCP_SERVER_NAME) -> None:
    """Run the MCP server using stdio transport.

    Starts an MCP server that exposes SDK functionality to AI agents.
    The server automatically discovers and mounts tools from the SDK
    and any installed plugins.

    Args:
        server_name: Human-readable name for the MCP server.
    """
    server = mcp_create_server(server_name)
    server.run()


def mcp_list_tools(server_name: str = MCP_SERVER_NAME) -> list[dict[str, Any]]:
    """List all available MCP tools.

    Creates the server and returns information about all registered tools
    including those from mounted servers.

    Note:
        This function must be called from a synchronous context. Calling it
        from within an async function will raise RuntimeError.

    Args:
        server_name: Human-readable name for the MCP server.

    Returns:
        list[dict[str, Any]]: List of tool information dictionaries with
            'name' and 'description' keys.
    """
    server = mcp_create_server(server_name)
    # FastMCP's get_tools() is async because mounted servers may need to
    # lazily initialize resources. We use asyncio.run() to bridge sync/async.
    tools = asyncio.run(server.get_tools())
    return [{"name": name, "description": tool.description or ""} for name, tool in tools.items()]
