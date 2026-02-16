"""Tests for MCP utilities."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from fastmcp import Client, FastMCP

from aignostics.utils import (
    MCP_SERVER_NAME,
    discover_plugin_packages,
    mcp_create_server,
    mcp_discover_servers,
    mcp_list_tools,
)
from aignostics.utils._di import _implementation_cache

if TYPE_CHECKING:
    from collections.abc import Iterator

# Patch targets
PATCH_LOCATE_IMPLEMENTATIONS = "aignostics.utils._mcp.locate_implementations"


# =============================================================================
# Discovery Tests
# =============================================================================


@pytest.mark.unit
def test_mcp_discover_servers_returns_list(record_property) -> None:
    """Test that mcp_discover_servers returns a list of servers."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    test_server = FastMCP("test_server")
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[test_server]) as mock_locate:
        servers = mcp_discover_servers()
        assert len(servers) == 1
        assert servers[0] is test_server
        mock_locate.assert_called_once()


@pytest.mark.unit
def test_mcp_discover_servers_empty(record_property) -> None:
    """Test that mcp_discover_servers handles no servers found."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        servers = mcp_discover_servers()
        assert servers == []


@pytest.mark.integration
def test_mcp_discover_servers_real_discovery(record_property) -> None:
    """Test discovery without mocking."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    servers = mcp_discover_servers()
    assert isinstance(servers, list)
    for server in servers:
        assert isinstance(server, FastMCP)


# =============================================================================
# Server Creation & Mounting Tests
# =============================================================================


@pytest.mark.unit
def test_mcp_create_server(record_property) -> None:
    """Test server creation."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        server = mcp_create_server()
        assert isinstance(server, FastMCP)
        assert server.name == MCP_SERVER_NAME


@pytest.mark.unit
def test_mcp_create_server_mounts_discovered(record_property) -> None:
    """Test that mcp_create_server mounts discovered servers with their tools."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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
def test_mcp_create_server_skips_duplicate_names(caplog: pytest.LogCaptureFixture, record_property) -> None:
    """Test that servers with duplicate names are skipped with warning."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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
def test_mcp_list_tools_returns_tool_info(record_property) -> None:
    """Test that mcp_list_tools returns correct tool information."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
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
def test_mcp_list_tools_empty(record_property) -> None:
    """Test mcp_list_tools with no discovered tools."""
    record_property("tested-item-id", "SPEC-UTILS-SERVICE")
    with patch(PATCH_LOCATE_IMPLEMENTATIONS, return_value=[]):
        tools = mcp_list_tools()
        # Should return empty list when no plugins have tools
        assert tools == []


# =============================================================================
# E2E Plugin Auto-Discovery Tests
# =============================================================================

DUMMY_PLUGIN_DIR = Path(__file__).resolve().parents[2] / "resources" / "mcp_dummy_plugin"


def _clear_mcp_discovery_caches() -> None:
    """Invalidate DI and plugin caches so MCP discovery starts fresh."""
    _implementation_cache.pop(FastMCP, None)
    discover_plugin_packages.cache_clear()


@pytest.fixture(scope="session")
def install_dummy_mcp_plugin() -> Iterator[None]:
    """Install the dummy MCP plugin in editable mode and make it importable.

    Refreshes site-packages so the running interpreter sees the new package
    and its entry points without a process restart.
    """
    import importlib
    import site

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(DUMMY_PLUGIN_DIR)],
        check=True,
        capture_output=True,
        text=True,
    )

    importlib.invalidate_caches()
    for sp in site.getsitepackages():
        site.addsitedir(sp)

    yield

    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "mcp-dummy-plugin"],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def clear_mcp_caches() -> Iterator[None]:
    """Clear MCP discovery caches before and after the test."""
    _clear_mcp_discovery_caches()
    yield
    _clear_mcp_discovery_caches()


@pytest.mark.e2e
@pytest.mark.timeout(timeout=60)
def test_mcp_server_discovers_and_serves_plugin_tools(
    install_dummy_mcp_plugin, clear_mcp_caches, record_property
) -> None:
    """Full E2E: entry point registration -> discovery -> mount -> client round-trip."""
    record_property("tested-item-id", "TC-UTILS-MCP-01")

    server = mcp_create_server()
    tool_names = list(asyncio.run(server.get_tools()).keys())

    assert "dummy_plugin_dummy_echo" in tool_names
    assert "dummy_plugin_dummy_add" in tool_names

    async def _call_tools() -> tuple[str, str]:
        async with Client(server) as client:
            echo_result = await client.call_tool("dummy_plugin_dummy_echo", {"message": "hello"})
            add_result = await client.call_tool("dummy_plugin_dummy_add", {"a": 2, "b": 3})
            return echo_result.content[0].text, add_result.content[0].text

    echo_text, add_text = asyncio.run(_call_tools())
    assert echo_text == "hello"
    assert add_text == "5"
