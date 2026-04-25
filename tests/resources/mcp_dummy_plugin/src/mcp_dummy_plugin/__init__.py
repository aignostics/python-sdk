"""Dummy MCP plugin for integration testing of plugin auto-discovery."""

from ._cli import cli
from ._mcp import mcp
from ._nav import DummyPluginNavBuilder

__all__ = ["DummyPluginNavBuilder", "cli", "mcp"]
