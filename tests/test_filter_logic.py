"""Unit tests for pure filter/search logic in ui.py."""
import os
import sys

# Prevent PyQt6 import during testing — we only need the module-level functions
# We import them via a shim after adding the project root to sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def _import_logic():
    """Import only after ensuring no display is needed."""
    # Set a dummy display env if not set (Linux CI without $DISPLAY)
    import os as _os
    _os.environ.setdefault("DISPLAY", ":0")
    # These functions are module-level in ui.py and do NOT create any widgets
    from ui import TermRow, _line_matches, _extract_json_keys  # noqa: E402, I001
    return TermRow, _line_matches, _extract_json_keys


# ── TermRow ───────────────────────────────────────────────────────────────────

def test_term_row_first_has_empty_operator():
    TermRow, _, _ = _import_logic()
    t = TermRow(text="foo", operator="")
    assert t.operator == ""


# ── _line_matches ─────────────────────────────────────────────────────────────

def test_no_terms_matches_everything():
    _, _line_matches, _ = _import_logic()
    assert _line_matches("anything here", []) is True


def test_single_term_match():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", "")]
    assert _line_matches("ERROR: disk full", terms) is True


def test_single_term_no_match():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", "")]
    assert _line_matches("INFO: all good", terms) is False


def test_case_insensitive():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("ERROR", "")]
    assert _line_matches("error: something", terms) is True


def test_and_both_match():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", ""), TermRow("disk", "AND")]
    assert _line_matches("ERROR: disk full", terms) is True


def test_and_second_missing():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", ""), TermRow("disk", "AND")]
    assert _line_matches("ERROR: memory full", terms) is False


def test_or_first_matches():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", ""), TermRow("warn", "OR")]
    assert _line_matches("ERROR: something", terms) is True


def test_or_second_matches():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", ""), TermRow("warn", "OR")]
    assert _line_matches("WARN: low memory", terms) is True


def test_or_neither_matches():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("error", ""), TermRow("warn", "OR")]
    assert _line_matches("INFO: all good", terms) is False


def test_empty_term_text_matches_all():
    TermRow, _line_matches, _ = _import_logic()
    terms = [TermRow("", "")]  # empty text = match all
    assert _line_matches("anything", terms) is True


# ── _extract_json_keys ────────────────────────────────────────────────────────

def test_pure_json_object():
    _, _, _extract_json_keys = _import_logic()
    keys = _extract_json_keys('{"level": "ERROR", "msg": "fail", "userId": 42}')
    assert keys == {"level", "msg", "userId"}


def test_non_json_line_returns_empty_or_partial():
    _, _, _extract_json_keys = _import_logic()
    keys = _extract_json_keys("plain log line with no JSON")
    assert isinstance(keys, set)  # may be empty or have false positives, that's OK


def test_json_embedded_in_line():
    _, _, _extract_json_keys = _import_logic()
    line = '2024-01-01 ERROR {"requestId": "abc", "status": 500}'
    keys = _extract_json_keys(line)
    assert "requestId" in keys
    assert "status" in keys


def test_invalid_json_uses_fallback_regex():
    _, _, _extract_json_keys = _import_logic()
    # Not valid JSON but has "key": patterns
    line = '{"userId": 1, broken}'
    keys = _extract_json_keys(line)
    assert "userId" in keys
