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

| Argument       | Type                  | Required | Description                                                                                 |
| -------------- | --------------------- | -------- | ------------------------------------------------------------------------------------------- |
| `limit`        | `int`                 | No       | Maximum number of processes to return. Must be non-negative.                                |
| `sort_by`      | `"cpu"` \| `"memory"` | No       | Sort descending by CPU or memory usage. Omit to keep OS order.                              |
| `cpu_interval` | `float`               | No       | Seconds to spend measuring CPU. Omit for automatic behaviour; `0` skips it. Non-negative.   |

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
* `cpu_percent` — CPU usage percentage (see the note below)
* `memory_percent` — resident memory as a percentage of total physical memory
* `memory_rss_bytes` — resident set size in bytes

Processes that vanish or deny access mid-enumeration are skipped cleanly rather than
aborting the whole snapshot, and invalid arguments raise a clear `ValueError` that the
MCP client receives as a structured tool error.

### A note on `cpu_percent`

CPU usage is a *rate*: it only has meaning when measured across two reads a short moment
apart (like working out a car's speed from two photos). `psutil`'s first read of a
process always returns `0.0` — it just starts the clock — so a single snapshot cannot
report real CPU numbers.

Because of that, the tool measures CPU on a two-read basis:

* When you pass `sort_by="cpu"`, it automatically waits a short interval
  (`DEFAULT_CPU_INTERVAL`, 0.1s) between two reads so the ranking is meaningful.
* When you don't need CPU (e.g. `sort_by="memory"` or no sort), it skips the wait and
  `cpu_percent` may be `0.0` — fast, but not a real measurement.
* Pass `cpu_interval` explicitly to override: a value like `0.5` forces an accurate
  measurement (a longer wait smooths the reading), and `0` disables it for speed.

On a mostly idle machine, even a correct two-read measurement can read near `0.0`
simply because little CPU is being used during the interval — that is expected, not a bug.

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
