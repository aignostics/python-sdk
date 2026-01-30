"""Shared constants for the MCP module."""

# Server name used for mounting and tool name prefixes
# Must be valid for tool name prefixes (no spaces, only [a-zA-Z0-9_-])
SERVER_NAME = "aignostics-platform"

# Maximum data points for chart visualizations (for performance and tool result size limits)
# 5000 points keeps scatter chart JSON under ~200KB to avoid MCP client size limits
MAX_CHART_POINTS = 5000
