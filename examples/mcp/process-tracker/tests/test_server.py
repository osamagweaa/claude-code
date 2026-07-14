"""Unit tests for the process-tracker MCP server.

The tests exercise three concerns called out by the tool specification:

* the MCP tool *schema* (name, arguments, optionality, description),
* *argument handling* (``limit`` truncation, ``sort_by`` ordering, validation),
* the *execution output* structure (required fields and their types).

Process enumeration is monkeypatched to a deterministic snapshot so the
ordering/limit logic can be asserted precisely without depending on whatever
happens to be running on the test host.
"""

from __future__ import annotations

import asyncio

import psutil
import pytest

from process_tracker import server
from process_tracker.server import (
    ProcessInfo,
    collect_processes,
    get_running_processes,
)


def _proc(name: str, pid: int, cpu: float, mem: float, rss: int) -> ProcessInfo:
    return ProcessInfo(
        name=name,
        pid=pid,
        cpu_percent=cpu,
        memory_percent=mem,
        memory_rss_bytes=rss,
    )


@pytest.fixture
def fake_snapshot(monkeypatch: pytest.MonkeyPatch) -> list[ProcessInfo]:
    """Patch the OS enumeration with a fixed, unsorted set of processes."""
    processes = [
        _proc("alpha", 1, cpu=5.0, mem=10.0, rss=1_000),
        _proc("bravo", 2, cpu=50.0, mem=2.0, rss=200),
        _proc("charlie", 3, cpu=1.0, mem=40.0, rss=4_000),
    ]
    monkeypatch.setattr(server, "_iter_process_info", lambda: list(processes))
    return processes


# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #
def test_tool_registered_with_expected_schema() -> None:
    tools = asyncio.run(server.mcp.list_tools())
    tool = next((t for t in tools if t.name == "get_running_processes"), None)

    assert tool is not None, "get_running_processes must be registered as a tool"
    assert tool.description, "tool must document itself for the LLM client"

    props = tool.inputSchema.get("properties", {})
    assert set(props) == {"limit", "sort_by"}
    # Both arguments are optional.
    assert tool.inputSchema.get("required", []) == []


# --------------------------------------------------------------------------- #
# Output structure
# --------------------------------------------------------------------------- #
def test_output_records_have_required_fields(
    fake_snapshot: list[ProcessInfo],
) -> None:
    result = collect_processes()

    assert len(result) == len(fake_snapshot)
    for record in result:
        assert set(record) == {
            "name",
            "pid",
            "cpu_percent",
            "memory_percent",
            "memory_rss_bytes",
        }
        assert isinstance(record["name"], str)
        assert isinstance(record["pid"], int)
        assert isinstance(record["cpu_percent"], float)
        assert isinstance(record["memory_percent"], float)
        assert isinstance(record["memory_rss_bytes"], int)


# --------------------------------------------------------------------------- #
# Argument handling
# --------------------------------------------------------------------------- #
def test_limit_restricts_number_of_results(
    fake_snapshot: list[ProcessInfo],
) -> None:
    assert len(collect_processes(limit=2)) == 2


def test_limit_zero_returns_empty(fake_snapshot: list[ProcessInfo]) -> None:
    assert collect_processes(limit=0) == []


def test_sort_by_cpu_orders_descending(
    fake_snapshot: list[ProcessInfo],
) -> None:
    result = collect_processes(sort_by="cpu")
    cpu_values = [r["cpu_percent"] for r in result]
    assert cpu_values == sorted(cpu_values, reverse=True)
    assert result[0]["name"] == "bravo"


def test_sort_by_memory_orders_descending(
    fake_snapshot: list[ProcessInfo],
) -> None:
    result = collect_processes(sort_by="memory")
    mem_values = [r["memory_percent"] for r in result]
    assert mem_values == sorted(mem_values, reverse=True)
    assert result[0]["name"] == "charlie"


def test_sort_and_limit_combine(fake_snapshot: list[ProcessInfo]) -> None:
    result = collect_processes(limit=1, sort_by="cpu")
    assert len(result) == 1
    assert result[0]["name"] == "bravo"


def test_invalid_sort_by_raises() -> None:
    with pytest.raises(ValueError, match="sort_by"):
        collect_processes(sort_by="disk")  # type: ignore[arg-type]


def test_negative_limit_raises(fake_snapshot: list[ProcessInfo]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        collect_processes(limit=-1)


def test_bool_limit_rejected(fake_snapshot: list[ProcessInfo]) -> None:
    # ``bool`` is a subclass of ``int``; it must not be accepted as a limit.
    with pytest.raises(ValueError, match="integer"):
        collect_processes(limit=True)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Tool entry point + resilience
# --------------------------------------------------------------------------- #
def test_tool_callable_returns_list(fake_snapshot: list[ProcessInfo]) -> None:
    result = get_running_processes(limit=2, sort_by="memory")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "charlie"


def test_iter_skips_inaccessible_processes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeMemory:
        rss = 4_096

    class _FakeProc:
        def __init__(
            self, info: dict[str, object], raises: Exception | None = None
        ) -> None:
            self._info = info
            self._raises = raises

        @property
        def info(self) -> dict[str, object]:
            if self._raises is not None:
                raise self._raises
            return self._info

    healthy = _FakeProc(
        {
            "name": "ok",
            "pid": 1,
            "cpu_percent": 1.5,
            "memory_percent": 2.5,
            "memory_info": _FakeMemory(),
        }
    )
    denied = _FakeProc({}, raises=psutil.AccessDenied())
    gone = _FakeProc({}, raises=psutil.NoSuchProcess(999))

    monkeypatch.setattr(
        psutil,
        "process_iter",
        lambda attrs=None: iter([healthy, denied, gone]),
    )

    result = server._iter_process_info()
    assert len(result) == 1
    assert result[0]["name"] == "ok"
    assert result[0]["memory_rss_bytes"] == 4_096
