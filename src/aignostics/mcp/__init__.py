"""MCP server module for exposing readout tools to AI agents.

This module provides an MCP server that exposes tools for querying
and analyzing application run readouts from the Aignostics Platform.
"""

from ._server import mcp

__all__ = ["mcp"]
