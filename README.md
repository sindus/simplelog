# SimpleLog

A fast, Material Design log viewer for **AWS CloudWatch**, **local log files**, and **piped stdin** — built with PyQt6.

---

## Features

- **Three log sources** — CloudWatch streams, local files, and piped stdin in a unified interface
- **Split view** — open logs side-by-side (vertical) or stacked (horizontal) directly from the sidebar
- **Configurable tail** — load only the last N lines of large files to prevent UI freezing (default: 100)
- **Live tailing** — files and CloudWatch streams are polled continuously for new events
- **Syntax highlighting** — color-coded `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE`, timestamps, JSON keys
- **Search** — incremental search with `Ctrl+F`, wraps around automatically
- **Multi-tab** — open multiple sources in tabs within each pane
- **Material Design dark theme**

---

## Requirements

- Python 3.11+
- PyQt6 >= 6.6
- AWS credentials configured (for CloudWatch only — `~/.aws/credentials` or environment variables)

---

## Installation

```bash
git clone https://github.com/sindus/simplelog.git
cd simplelog
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### GUI mode (CloudWatch browser)

```bash
python main.py
```

### Open one or more log files

```bash
python main.py /var/log/syslog /var/log/auth.log
```

### Pipe stdin

```bash
journalctl -f | python main.py
kubectl logs -f my-pod | python main.py
```

---

## CLI Reference

```
simplelog [--split MODE] [--tail N] [FILE ...]
command | simplelog [--split MODE]
```

### Arguments

| Argument | Default | Description |
|---|---|---|
| `FILE ...` | — | One or more log file paths. Each opens in its own tab. Glob patterns are not expanded — use your shell: `simplelog logs/*.log`. |
| `--split MODE` | `tab` | How to lay out files on startup. See values below. |
| `--tail N` | `100` | Lines to load from the **end** of each file. Prevents freezing on large files. Use a large value (e.g. `--tail 0` is not supported — use `--tail 999999`) to approximate "all". |

### `--split` values

| Value | Layout | Description |
|---|---|---|
| `tab` | *(default)* | All files open as tabs in a single pane. |
| `vertical` | `│` divider | First file in the left pane, subsequent files in a second pane to the right. |
| `horizontal` | `─` divider | First file in the top pane, subsequent files in a second pane below. |

> The split mode selected via `--split` is also reflected in the sidebar radio buttons inside the app.

### Examples

```bash
# Launch the CloudWatch browser (no arguments)
simplelog

# Tail a single file
simplelog /var/log/syslog

# Load the last 500 lines of a large file
simplelog --tail 500 /var/log/nginx/access.log

# Open multiple files as tabs
simplelog app.log worker.log scheduler.log

# Open two files side-by-side (vertical split)
simplelog --split vertical app.log error.log

# Open two files stacked (horizontal split)
simplelog --split horizontal service-a.log service-b.log

# Split + custom tail
simplelog --split vertical --tail 1000 app.log error.log

# Pipe any command's output
journalctl -f | simplelog
kubectl logs -f my-pod | simplelog
docker logs -f my-container | simplelog

# Pipe with filtering
tail -f /var/log/syslog | grep -i error | simplelog
```

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+F` | Open / focus search bar |
| `Enter` | Find next match |
| `Escape` | Close search bar |

---

## Split view

The split mode is also choosable from the sidebar before opening a source:

- **New tab** — opens in the current pane as a new tab (default)
- **Split ↔ side by side** — creates a second pane to the right
- **Split ↕ top / bottom** — creates a second pane below

Closing the last tab in a secondary pane removes it automatically.

---

## CloudWatch

1. Select an AWS **profile** and **region**, then click **Connect**
2. Browse and filter **log groups**
3. Select a **log stream** (or "All streams")
4. Set lookback window, poll interval, and optional filter pattern
5. Choose how to open it (tab or split), then click **Open ↗**

---

## Project layout

```
simplelog/
├── main.py          # Entry point, CLI argument parsing
├── ui.py            # All PyQt6 UI components
├── workers.py       # Background QThread workers (file, CloudWatch, stdin)
├── cloudwatch.py    # boto3 CloudWatch Logs helpers
├── requirements.txt # Runtime dependencies
└── tests/           # Unit tests
```

---

## Development

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### Run tests

```bash
pytest
```

### Lint

```bash
ruff check .
```

---

## Uninstall

### macOS (.dmg)

```bash
# Remove the app bundle
rm -rf /Applications/SimpleLog.app
```

### Linux — Debian / Ubuntu (.deb)

```bash
sudo apt remove simplelog
# or, if installed directly with dpkg:
sudo dpkg -r simplelog
```

### Linux — AppImage

```bash
# Remove the binary you placed in PATH (default location used by install.sh)
rm -f ~/.local/bin/simplelog
```

---

## License

MIT
