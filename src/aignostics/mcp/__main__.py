"""Entry point for running MCP server as a module.

Usage:
    # Run the local stdio server (for Claude Desktop, VS Code, Claude Code)
    python -m aignostics.mcp

    # With environment specification
    AIGNOSTICS_API_ROOT=https://platform.aignostics.com python -m aignostics.mcp
"""

from __future__ import annotations


def main() -> None:
    """Run the MCP server in local stdio mode."""
    from ._server import run_server

    run_server()


if __name__ == "__main__":
    main()
