"""MCP server exposing a cross-platform ``get_running_processes`` tool.

The tool inspects the host operating system's live process table via
``psutil`` and returns a structured list describing each running process. It
is designed with Windows automation in mind, but ``psutil`` is cross-platform,
so the same code runs on Linux and macOS -- which also makes it easy to test.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Literal

import psutil
from mcp.server.fastmcp import FastMCP
from typing_extensions import TypedDict

mcp = FastMCP("process-tracker")

SortBy = Literal["cpu", "memory"]

# Default wait (seconds) used to measure CPU usage when the caller sorts by
# CPU but does not specify their own interval. CPU percentage is a *rate*: it
# only has meaning across two reads separated by a short delay (see
# ``_iter_process_info``). 0.1s keeps the tool responsive while still producing
# a real number instead of psutil's priming ``0.0``.
DEFAULT_CPU_INTERVAL = 0.1


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


def _iter_process_info(cpu_interval: float | None = None) -> list[ProcessInfo]:
    """Take a snapshot of the current process table.

    CPU percentage is measured as a *rate of change* between two reads, like
    working out a car's speed from two photos taken a moment apart. psutil's
    first read of a process always returns ``0.0`` (it just starts the clock);
    a real value appears only on a second read after some time has passed.

    Args:
        cpu_interval: When greater than ``0``, prime every process's CPU
            counter, wait this many seconds, then read again to obtain real CPU
            percentages. When ``None`` or ``0``, skip the wait and report the
            single-shot value (which is typically ``0.0``) -- fast, but not a
            meaningful CPU measurement.

    Individual processes can vanish or deny access between enumeration and
    inspection; such processes are skipped rather than aborting the whole
    snapshot.
    """
    procs = list(
        psutil.process_iter(
            ["name", "pid", "cpu_percent", "memory_percent", "memory_info"]
        )
    )

    sampling = cpu_interval is not None and cpu_interval > 0
    if sampling:
        assert cpu_interval is not None  # guaranteed by ``sampling``; guides mypy
        # First read primes psutil's per-process CPU clock (returns ~0.0); the
        # real percentage comes from the second read after the wait below.
        for proc in procs:
            try:
                proc.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        time.sleep(cpu_interval)

    processes: list[ProcessInfo] = []
    for proc in procs:
        try:
            info = proc.info
            if sampling:
                cpu = float(proc.cpu_percent(None))
            else:
                cpu = float(info.get("cpu_percent") or 0.0)
            memory_info = info.get("memory_info")
            processes.append(
                ProcessInfo(
                    name=info.get("name") or "",
                    pid=int(info["pid"]),
                    cpu_percent=cpu,
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
    cpu_interval: float | None = None,
) -> list[ProcessInfo]:
    """Return running processes, optionally sorted and truncated.

    Args:
        limit: Maximum number of processes to return. ``None`` returns all.
            Must be a non-negative integer when provided.
        sort_by: ``"cpu"`` or ``"memory"`` to sort descending by that metric.
            ``None`` leaves the OS enumeration order untouched.
        cpu_interval: Seconds to wait while measuring CPU usage (see
            :func:`_iter_process_info`). ``None`` means "auto": a real
            measurement is taken only when ``sort_by="cpu"`` (otherwise CPU is
            not needed and the wait is skipped). Pass an explicit value to force
            or disable sampling regardless of ``sort_by``. Must be a
            non-negative number when provided.

    Returns:
        A list of :class:`ProcessInfo` records.

    Raises:
        ValueError: If ``sort_by`` is not an accepted value, if ``limit`` is
            not a non-negative integer, or if ``cpu_interval`` is not a
            non-negative number.
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
    if cpu_interval is not None:
        if isinstance(cpu_interval, bool) or not isinstance(cpu_interval, (int, float)):
            raise ValueError(
                f"cpu_interval must be a number, got {type(cpu_interval).__name__}"
            )
        if cpu_interval < 0:
            raise ValueError(f"cpu_interval must be non-negative, got {cpu_interval}")

    # Auto policy: measure CPU only when the caller sorts by it, unless they
    # asked for a specific interval.
    effective_interval = cpu_interval
    if effective_interval is None and sort_by == "cpu":
        effective_interval = DEFAULT_CPU_INTERVAL

    processes = _iter_process_info(cpu_interval=effective_interval)

    if sort_by is not None:
        processes.sort(key=_SORT_KEYS[sort_by], reverse=True)

    if limit is not None:
        processes = processes[:limit]

    return processes


@mcp.tool()
def get_running_processes(
    limit: int | None = None,
    sort_by: SortBy | None = None,
    cpu_interval: float | None = None,
) -> list[ProcessInfo]:
    """List the operating system's currently running processes.

    Args:
        limit: Optional maximum number of processes to return.
        sort_by: Optional metric to sort by, either ``"cpu"`` or ``"memory"``
            (descending). Omit to keep the native enumeration order.
        cpu_interval: Optional seconds to spend measuring CPU usage. Leave unset
            for automatic behaviour (a real CPU measurement is taken when
            ``sort_by="cpu"``); set a value like ``0.5`` to force an accurate
            measurement, or ``0`` to skip it for speed.

    Returns:
        A list of process records, each containing the process ``name``,
        ``pid``, ``cpu_percent``, ``memory_percent`` and ``memory_rss_bytes``.
    """
    try:
        return collect_processes(
            limit=limit, sort_by=sort_by, cpu_interval=cpu_interval
        )
    except psutil.Error as exc:  # pragma: no cover - defensive OS-level guard
        # Surface OS-level failures to the client as a clean tool error.
        raise RuntimeError(f"Failed to read the process table: {exc}") from exc


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
