"""MCP server exposing a cross-platform ``get_running_processes`` tool.

The tool inspects the host operating system's live process table via
``psutil`` and returns a structured list describing each running process. It
is designed with Windows automation in mind, but ``psutil`` is cross-platform,
so the same code runs on Linux and macOS -- which also makes it easy to test.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import psutil
from mcp.server.fastmcp import FastMCP
from typing_extensions import TypedDict

mcp = FastMCP("process-tracker")

SortBy = Literal["cpu", "memory"]


class ProcessInfo(TypedDict):
    """Structured description of a single running process."""

    name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    memory_rss_bytes: int


# Maps the public ``sort_by`` values onto the key used to order results.
_SORT_KEYS: dict[str, Callable[[ProcessInfo], float]] = {
    "cpu": lambda proc: proc["cpu_percent"],
    "memory": lambda proc: proc["memory_percent"],
}


def _iter_process_info() -> list[ProcessInfo]:
    """Take a snapshot of the current process table.

    Individual processes can vanish or deny access between enumeration and
    inspection; such processes are skipped rather than aborting the whole
    snapshot.
    """
    processes: list[ProcessInfo] = []
    for proc in psutil.process_iter(
        ["name", "pid", "cpu_percent", "memory_percent", "memory_info"]
    ):
        try:
            info = proc.info
            memory_info = info.get("memory_info")
            processes.append(
                ProcessInfo(
                    name=info.get("name") or "",
                    pid=int(info["pid"]),
                    cpu_percent=float(info.get("cpu_percent") or 0.0),
                    memory_percent=float(info.get("memory_percent") or 0.0),
                    memory_rss_bytes=int(getattr(memory_info, "rss", 0) or 0),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process disappeared or is protected; skip it cleanly.
            continue
    return processes


def collect_processes(
    limit: int | None = None,
    sort_by: SortBy | None = None,
) -> list[ProcessInfo]:
    """Return running processes, optionally sorted and truncated.

    Args:
        limit: Maximum number of processes to return. ``None`` returns all.
            Must be a non-negative integer when provided.
        sort_by: ``"cpu"`` or ``"memory"`` to sort descending by that metric.
            ``None`` leaves the OS enumeration order untouched.

    Returns:
        A list of :class:`ProcessInfo` records.

    Raises:
        ValueError: If ``sort_by`` is not an accepted value, or if ``limit``
            is not a non-negative integer.
    """
    if sort_by is not None and sort_by not in _SORT_KEYS:
        raise ValueError(
            f"sort_by must be one of {sorted(_SORT_KEYS)}, got {sort_by!r}"
        )
    if limit is not None:
        # ``bool`` is a subclass of ``int`` but is never a valid limit.
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError(f"limit must be an integer, got {type(limit).__name__}")
        if limit < 0:
            raise ValueError(f"limit must be non-negative, got {limit}")

    processes = _iter_process_info()

    if sort_by is not None:
        processes.sort(key=_SORT_KEYS[sort_by], reverse=True)

    if limit is not None:
        processes = processes[:limit]

    return processes


@mcp.tool()
def get_running_processes(
    limit: int | None = None,
    sort_by: SortBy | None = None,
) -> list[ProcessInfo]:
    """List the operating system's currently running processes.

    Args:
        limit: Optional maximum number of processes to return.
        sort_by: Optional metric to sort by, either ``"cpu"`` or ``"memory"``
            (descending). Omit to keep the native enumeration order.

    Returns:
        A list of process records, each containing the process ``name``,
        ``pid``, ``cpu_percent``, ``memory_percent`` and ``memory_rss_bytes``.
    """
    try:
        return collect_processes(limit=limit, sort_by=sort_by)
    except psutil.Error as exc:  # pragma: no cover - defensive OS-level guard
        # Surface OS-level failures to the client as a clean tool error.
        raise RuntimeError(f"Failed to read the process table: {exc}") from exc


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
