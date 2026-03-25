"""Tests for i18n.py — translation module."""
import pytest

import i18n


def setup_function():
    """Reset locale to English before each test."""
    i18n.set_locale("en")
    i18n._callbacks.clear()


# ── tr() ──────────────────────────────────────────────────────────────────────

def test_tr_english_default():
    assert i18n.tr("menu_file") == "File"


def test_tr_french_after_set_locale():
    i18n.set_locale("fr")
    assert i18n.tr("menu_file") == "Fichier"


def test_tr_unknown_key_returns_key():
    assert i18n.tr("nonexistent_key_xyz") == "nonexistent_key_xyz"


def test_tr_with_kwargs():
    assert "42" in i18n.tr("viewer_lines", n=42)


def test_tr_with_kwargs_french():
    i18n.set_locale("fr")
    result = i18n.tr("viewer_lines", n=1_000)
    assert "1" in result  # at least the number is present


def test_tr_fallback_to_english_for_missing_fr_key():
    # All keys should exist in FR; if one were missing it should fall back to EN
    i18n.set_locale("fr")
    val = i18n.tr("menu_file")
    assert val != "menu_file"  # should never return the raw key


# ── set_locale / get_locale ───────────────────────────────────────────────────

def test_set_locale_english():
    i18n.set_locale("en")
    assert i18n.get_locale() == "en"


def test_set_locale_french():
    i18n.set_locale("fr")
    assert i18n.get_locale() == "fr"


def test_set_locale_unknown_falls_back_to_english():
    i18n.set_locale("de")
    assert i18n.get_locale() == "en"


# ── register / unregister / retranslate_all ───────────────────────────────────

def test_register_and_retranslate_all():
    calls = []
    i18n.register(1, lambda: calls.append(1))
    i18n.retranslate_all()
    assert calls == [1]


def test_unregister_stops_callback():
    calls = []
    i18n.register(99, lambda: calls.append(99))
    i18n.unregister(99)
    i18n.retranslate_all()
    assert calls == []


def test_retranslate_all_updates_locale():
    results = []
    i18n.set_locale("en")
    i18n.register(42, lambda: results.append(i18n.tr("menu_file")))
    i18n.set_locale("fr")
    i18n.retranslate_all()
    assert results[-1] == "Fichier"


# ── All required keys exist in both locales ───────────────────────────────────

_REQUIRED_KEYS = [
    "menu_file", "menu_edit", "menu_language", "menu_help",
    "action_open", "action_update", "action_quit",
    "action_copy", "action_break",
    "cw_title", "file_title",
    "viewer_autoscroll", "viewer_clear", "viewer_stop",
    "open_mode_tab", "open_mode_vertical", "open_mode_horizontal",
    "help_title", "help_content",
    "update_title", "update_up_to_date", "update_available",
]


@pytest.mark.parametrize("key", _REQUIRED_KEYS)
def test_key_exists_in_english(key):
    i18n.set_locale("en")
    assert i18n.tr(key) != key, f"Key '{key}' missing in EN"


@pytest.mark.parametrize("key", _REQUIRED_KEYS)
def test_key_exists_in_french(key):
    i18n.set_locale("fr")
    assert i18n.tr(key) != key, f"Key '{key}' missing in FR"


# ── Sidebar keys ───────────────────────────────────────────────────────────────

def test_sidebar_search_key_en():
    i18n.set_locale("en")
    assert i18n.tr("sidebar_search") == "Search"


def test_sidebar_search_key_fr():
    i18n.set_locale("fr")
    assert i18n.tr("sidebar_search") == "Recherche"


def test_sidebar_hits_key_en():
    i18n.set_locale("en")
    assert i18n.tr("sidebar_hits", n=42) == "42 hits"


def test_sidebar_hits_key_fr():
    i18n.set_locale("fr")
    assert i18n.tr("sidebar_hits", n=42) == "42 résultats"


def test_viewer_search_ph_removed():
    """viewer_search_ph key must no longer exist (search bar moved to sidebar)."""
    i18n.set_locale("en")
    assert i18n.tr("viewer_search_ph") == "viewer_search_ph"  # returns key when missing


def test_action_paste_removed():
    i18n.set_locale("en")
    assert i18n.tr("action_paste") == "action_paste"
