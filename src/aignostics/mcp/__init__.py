"""MCP Server for Aignostics Platform.

This module provides a Model Context Protocol (MCP) server that allows LLMs
to interact with the Aignostics platform via natural language queries.

The server operates in local stdio mode, suitable for Claude Desktop, VS Code
with GitHub Copilot, and Claude Code.

Usage:
    # Run the server
    python -m aignostics.mcp

Programmatic usage:
    from aignostics.mcp import run_server

    run_server()

Authentication:
    The server uses cached authentication tokens from the Aignostics SDK.
    Users must first authenticate via `aignostics user login`.
"""

from ._server import mcp, run_server

__all__ = ["mcp", "run_server"]
