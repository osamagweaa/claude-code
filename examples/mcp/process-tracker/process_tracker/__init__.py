"""MCP server package exposing a cross-platform process inspection tool."""

from process_tracker.server import (
    ProcessInfo,
    collect_processes,
    get_running_processes,
    mcp,
)

__all__ = [
    "ProcessInfo",
    "collect_processes",
    "get_running_processes",
    "mcp",
]
