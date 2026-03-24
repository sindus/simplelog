"""Unit tests for workers._read_last_n_lines."""
import os
import tempfile

import pytest

from workers import _read_last_n_lines

# ── helpers ───────────────────────────────────────────────────────────────────

def _write_tmp(lines: list[str]) -> str:
    """Write *lines* to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    f.write("\n".join(lines))
    if lines:
        f.write("\n")
    f.close()
    return f.name


# ── tests ─────────────────────────────────────────────────────────────────────

def test_empty_file():
    path = _write_tmp([])
    try:
        lines, pos = _read_last_n_lines(path, 100)
        assert lines == []
        assert pos == 0
    finally:
        os.unlink(path)


def test_fewer_lines_than_requested():
    path = _write_tmp(["alpha", "beta", "gamma"])
    try:
        lines, pos = _read_last_n_lines(path, 100)
        assert lines == ["alpha", "beta", "gamma"]
        assert pos > 0
    finally:
        os.unlink(path)


def test_exactly_n_lines():
    content = [f"line{i}" for i in range(10)]
    path = _write_tmp(content)
    try:
        lines, _ = _read_last_n_lines(path, 10)
        assert lines == content
    finally:
        os.unlink(path)


def test_last_n_lines_from_large_file():
    total = 500
    content = [f"line{i}" for i in range(total)]
    path = _write_tmp(content)
    try:
        lines, _ = _read_last_n_lines(path, 50)
        assert len(lines) == 50
        assert lines[0] == "line450"
        assert lines[-1] == "line499"
    finally:
        os.unlink(path)


def test_eof_position_matches_file_size():
    raw = "foo\nbar\nbaz\n"
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    f.write(raw)
    f.close()
    try:
        _, pos = _read_last_n_lines(f.name, 10)
        assert pos == len(raw.encode())
    finally:
        os.unlink(f.name)


def test_n_zero_returns_empty():
    path = _write_tmp(["a", "b", "c"])
    try:
        lines, pos = _read_last_n_lines(path, 0)
        assert lines == []
        assert pos > 0
    finally:
        os.unlink(path)


def test_single_line_no_trailing_newline():
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    f.write("only line")
    f.close()
    try:
        lines, _ = _read_last_n_lines(f.name, 5)
        assert lines == ["only line"]
    finally:
        os.unlink(f.name)


@pytest.mark.parametrize("n", [1, 10, 100, 1000])
def test_never_returns_more_than_n(n):
    content = [f"x{i}" for i in range(200)]
    path = _write_tmp(content)
    try:
        lines, _ = _read_last_n_lines(path, n)
        assert len(lines) <= n
    finally:
        os.unlink(path)
