# MCP Process Tracker

A small, self-contained [Model Context Protocol](https://modelcontextprotocol.io)
server that exposes a single tool, **`get_running_processes`**, for inspecting the
host operating system's live process table.

It is built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
(the official Python MCP SDK) and uses [`psutil`](https://github.com/giampaolo/psutil)
to read process information. `psutil` is cross-platform, so although this example is
framed around **Windows automation**, the same code runs (and is tested) on Linux and
macOS.

## The `get_running_processes` tool

| Argument  | Type                        | Required | Description                                                       |
| --------- | --------------------------- | -------- | ----------------------------------------------------------------- |
| `limit`   | `int`                       | No       | Maximum number of processes to return. Must be non-negative.      |
| `sort_by` | `"cpu"` \| `"memory"`       | No       | Sort descending by CPU or memory usage. Omit to keep OS order.    |

Each returned record is a structured object:

```json
{
  "name": "chrome.exe",
  "pid": 4242,
  "cpu_percent": 12.5,
  "memory_percent": 3.1,
  "memory_rss_bytes": 268435456
}
```

* `name` — process image name
* `pid` — process ID
* `cpu_percent` — CPU usage percentage (as reported by `psutil`)
* `memory_percent` — resident memory as a percentage of total physical memory
* `memory_rss_bytes` — resident set size in bytes

Processes that vanish or deny access mid-enumeration are skipped cleanly rather than
aborting the whole snapshot, and invalid arguments raise a clear `ValueError` that the
MCP client receives as a structured tool error.

## Install & run

```bash
uv sync
uv run mcp-process-tracker   # serves over stdio
```

### Register with Claude Code

```bash
claude mcp add process-tracker -- uv run --directory /path/to/process-tracker mcp-process-tracker
```

Or add it to a `.mcp.json`:

```json
{
  "mcpServers": {
    "process-tracker": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/process-tracker", "mcp-process-tracker"]
    }
  }
}
```

## Development

```bash
uv sync            # install runtime + dev dependencies
uv run pytest      # run the test suite
uv run ruff check .
uv run ruff format --check .
uv run mypy process_tracker
```
