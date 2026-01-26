"""Tests for MCP utilities."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from fastmcp import FastMCP

from aignostics.utils import (
    MCP_SERVER_NAME,
    mcp_create_server,
    mcp_discover_servers,
    mcp_list_tools,
)

# Patch targets
PATCH_LOCATE_IMPLEMENTATIONS = "aignostics.utils._mcp.locate_implementations"


# =============================================================================
# Discovery Tests
# =============================================================================


@pytest.mark.unit
def test_mcp_discover_servers_returns_list() -> None:
    """Test that mcp_discover_servers returns a list of servers."""
    test_server = FastMCP("test_server")
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[test_server]) as mock_locate:
        servers = mcp_discover_servers()
        assert len(servers) == 1
        assert servers[0] is test_server
        mock_locate.assert_called_once()


@pytest.mark.unit
def test_mcp_discover_servers_empty() -> None:
    """Test that mcp_discover_servers handles no servers found."""
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        servers = mcp_discover_servers()
        assert servers == []


@pytest.mark.integration
def test_mcp_discover_servers_real_discovery() -> None:
    """Test discovery without mocking."""
    servers = mcp_discover_servers()
    assert isinstance(servers, list)
    for server in servers:
        assert isinstance(server, FastMCP)


# =============================================================================
# Server Creation & Mounting Tests
# =============================================================================


@pytest.mark.unit
def test_mcp_create_server() -> None:
    """Test server creation."""
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        server = mcp_create_server()
        assert isinstance(server, FastMCP)
        assert server.name == MCP_SERVER_NAME


@pytest.mark.unit
def test_mcp_create_server_mounts_discovered() -> None:
    """Test that mcp_create_server mounts discovered servers with their tools."""
    plugin1 = FastMCP("plugin1")
    plugin2 = FastMCP("plugin2")

    @plugin1.tool
    def plugin1_tool() -> str:
        """Plugin 1 tool."""
        return "p1"

    @plugin2.tool
    def plugin2_tool() -> str:
        """Plugin 2 tool."""
        return "p2"

    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[plugin1, plugin2]):
        server = mcp_create_server()
        assert isinstance(server, FastMCP)
        assert server.name == MCP_SERVER_NAME
        # Verify exactly 2 tools from both plugins are mounted with namespacing
        tools = asyncio.run(server.get_tools())
        tool_names = list(tools.keys())
        assert len(tool_names) == 2
        # Verify namespacing: tools should be prefixed with server name
        plugin1_tools = [n for n in tool_names if "plugin1" in n]
        plugin2_tools = [n for n in tool_names if "plugin2" in n]
        assert len(plugin1_tools) == 1
        assert len(plugin2_tools) == 1
        assert "plugin1_tool" in plugin1_tools[0]
        assert "plugin2_tool" in plugin2_tools[0]


@pytest.mark.unit
def test_mcp_create_server_skips_duplicate_names(caplog: pytest.LogCaptureFixture) -> None:
    """Test that servers with duplicate names are skipped with warning."""
    dup1 = FastMCP("duplicate_name")
    dup2 = FastMCP("duplicate_name")
    unique = FastMCP("unique_name")

    @dup1.tool
    def dup1_tool() -> str:
        """Dup1 tool."""
        return "dup1"

    @dup2.tool
    def dup2_tool() -> str:
        """Dup2 tool - should NOT be mounted."""
        return "dup2"

    @unique.tool
    def unique_tool() -> str:
        """Unique tool."""
        return "unique"

    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[dup1, dup2, unique]):
        server = mcp_create_server()
        assert isinstance(server, FastMCP)
        # Verify warning was logged for duplicate
        assert "Duplicate MCP server name 'duplicate_name'" in caplog.text
        # Verify only first duplicate and unique server were mounted (2 servers, not 3)
        tools = asyncio.run(server.get_tools())
        tool_names = list(tools.keys())
        assert len(tool_names) == 2
        # dup1_tool should be present (first occurrence)
        assert any("dup1_tool" in name for name in tool_names)
        # dup2_tool should NOT be present (duplicate skipped)
        assert not any("dup2_tool" in name for name in tool_names)
        # unique_tool should be present
        assert any("unique_tool" in name for name in tool_names)


# =============================================================================
# Tool Listing Tests
# =============================================================================


@pytest.mark.unit
def test_mcp_list_tools_returns_tool_info() -> None:
    """Test that mcp_list_tools returns correct tool information."""
    test_server = FastMCP("test")

    @test_server.tool
    def test_tool(param: str) -> str:
        """A test tool."""
        return param

    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[test_server]):
        tools = mcp_list_tools()
        assert len(tools) == 1
        assert "test_tool" in tools[0]["name"]
        assert tools[0]["description"] == "A test tool."


@pytest.mark.unit
def test_mcp_list_tools_empty() -> None:
    """Test mcp_list_tools with no discovered tools."""
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        tools = mcp_list_tools()
        # Should return empty list when no plugins have tools
        assert tools == []
