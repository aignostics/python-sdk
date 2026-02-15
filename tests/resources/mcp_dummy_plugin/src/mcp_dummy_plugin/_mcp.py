"""Dummy MCP tools for E2E testing."""

from fastmcp import FastMCP

mcp = FastMCP("dummy_plugin")


@mcp.tool
def dummy_echo(message: str) -> str:
    """Echo the provided message back."""
    return message


@mcp.tool
def dummy_add(a: int, b: int) -> str:
    """Add two integers and return the result as a string."""
    return str(a + b)
