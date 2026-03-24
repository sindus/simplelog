import json
import sys
import time
import urllib.request

from PyQt6.QtCore import QThread, pyqtSignal

import cloudwatch


def _read_last_n_lines(path: str, n: int) -> tuple[list[str], int]:
    """Read the last *n* lines of *path* without loading the whole file.

    Uses binary seeks so it's O(tail size), not O(file size).
    Returns *(lines, eof_byte_offset)* — the offset is used to resume tailing.
    """
    CHUNK = 1 << 14  # 16 KB per backwards step
    with open(path, "rb") as f:
        f.seek(0, 2)
        file_size = f.tell()
        if file_size == 0 or n == 0:
            return [], file_size

        buf = b""
        pos = file_size
        while pos > 0 and buf.count(b"\n") <= n:
            step = min(CHUNK, pos)
            pos -= step
            f.seek(pos)
            buf = f.read(step) + buf

    lines = buf.decode("utf-8", errors="replace").splitlines()
    result = lines[-n:] if len(lines) > n else lines
    return result, file_size


class TailWorker(QThread):
    new_lines    = pyqtSignal(list)  # [(ts_ms, message), ...]
    error        = pyqtSignal(str)
    status       = pyqtSignal(str)
    history_done = pyqtSignal(int)

    def __init__(self, client, log_group, log_stream, filter_pattern,
                 interval_s, lookback_s):
        super().__init__()
        self._client         = client
        self._log_group      = log_group
        self._log_stream     = log_stream
        self._filter_pattern = filter_pattern
        self._interval_ms    = int(interval_s * 1000)
        self._lookback_s     = lookback_s
        self._stop           = False

    def stop(self):
        self._stop = True

    def run(self):
        start_ms = int((time.time() - self._lookback_s) * 1000)
        self.status.emit("Loading history…")
        try:
            events = cloudwatch.fetch_events(
                self._client, self._log_group, self._log_stream or None,
                start_ms=start_ms,
                filter_pattern=self._filter_pattern,
                max_events=None,
            )
            self._last_ts = events[-1][0] + 1 if events else int(time.time() * 1000)
            if events:
                self.new_lines.emit(events)
            self.history_done.emit(len(events))
        except RuntimeError as e:
            self.error.emit(str(e))
            return

        while not self._stop:
            self.msleep(self._interval_ms)
            if self._stop:
                break
            try:
                events = cloudwatch.fetch_events(
                    self._client, self._log_group, self._log_stream or None,
                    start_ms=self._last_ts,
                    filter_pattern=self._filter_pattern,
                    max_events=500,
                )
                if events:
                    self._last_ts = events[-1][0] + 1
                    self.new_lines.emit(events)
                    self.status.emit(f"Updated  —  {len(events)} new events")
                else:
                    self.status.emit("Tailing…  no new events")
            except RuntimeError as e:
                self.error.emit(str(e))


class FileWorker(QThread):
    new_lines = pyqtSignal(list)  # [(ts_ms, message), ...]
    status    = pyqtSignal(str)
    error     = pyqtSignal(str)

    def __init__(self, path, tail_lines=100, interval_ms=200):
        super().__init__()
        self._path        = path
        self._tail_lines  = tail_lines
        self._interval_ms = interval_ms
        self._stop        = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            self.status.emit(f"Loading {self._path}…")
            lines, eof_pos = _read_last_n_lines(self._path, self._tail_lines)
            if lines:
                now = int(time.time() * 1000)
                self.new_lines.emit([(now, line) for line in lines if line])
            self.status.emit(f"Tailing {self._path}")

            # Resume tailing from EOF — only new bytes are read from here on
            with open(self._path, "rb") as f:
                f.seek(eof_pos)
                while not self._stop:
                    raw = f.read()
                    if raw:
                        now = int(time.time() * 1000)
                        events = [
                            (now, line)
                            for line in raw.decode("utf-8", errors="replace").splitlines()
                            if line
                        ]
                        if events:
                            self.new_lines.emit(events)
                    else:
                        self.msleep(self._interval_ms)
        except OSError as e:
            self.error.emit(str(e))


class StdinWorker(QThread):
    new_lines = pyqtSignal(list)  # [(ts_ms, message), ...]
    status    = pyqtSignal(str)
    error     = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        self.status.emit("Reading stdin…")
        try:
            for raw_line in sys.stdin:
                if self._stop:
                    break
                line = raw_line.rstrip()
                if line:
                    ts = int(time.time() * 1000)
                    self.new_lines.emit([(ts, line)])
            self.status.emit("stdin — stream closed")
        except Exception as e:
            self.error.emit(str(e))


class UpdateWorker(QThread):
    """Checks GitHub releases for a newer version."""
    update_available = pyqtSignal(str, str)  # (latest_tag, html_url)
    up_to_date       = pyqtSignal(str)       # (current_version)
    error            = pyqtSignal(str)

    _API = "https://api.github.com/repos/sindus/simplelog/releases/latest"

    def __init__(self, current_version: str):
        super().__init__()
        self._current = current_version

    def run(self):
        try:
            req = urllib.request.Request(
                self._API,
                headers={"User-Agent": f"SimpleLog/{self._current}"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
            latest = data.get("tag_name", "")
            # Normalise: strip leading 'v' for comparison
            def _strip(v: str) -> str:
                return v.lstrip("v")

            if latest and _strip(latest) != _strip(self._current):
                self.update_available.emit(latest, data.get("html_url", ""))
            else:
                self.up_to_date.emit(self._current)
        except Exception as exc:
            self.error.emit(str(exc))
