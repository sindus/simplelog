"""i18n.py — Minimal EN / FR translation support for SimpleLog."""
from __future__ import annotations

_locale: str = "en"

# id(fn) -> callable — registered retranslate callbacks
_callbacks: dict[int, object] = {}


def register(key: int, fn: object) -> None:
    _callbacks[key] = fn


def unregister(key: int) -> None:
    _callbacks.pop(key, None)


def retranslate_all() -> None:
    for fn in list(_callbacks.values()):
        try:
            fn()  # type: ignore[operator]
        except Exception:
            pass


_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        # ── Menu bar ──────────────────────────────────────────────────
        "menu_file":             "File",
        "menu_edit":             "Edit",
        "menu_language":         "Language",
        "menu_help":             "Help",
        "action_open":           "Open…",
        "action_update":         "Check for Updates",
        "action_quit":           "Quit",
        "action_copy":           "Copy",
        "lang_english":          "English",
        "lang_french":           "Français",
        "action_help_ref":       "CLI Reference",
        # ── Help dialog ───────────────────────────────────────────────
        "help_title":            "CLI Reference — SimpleLog",
        "help_content": (
            "USAGE\n"
            "  simplelog [OPTIONS] [FILE ...]\n"
            "  command | simplelog [OPTIONS]\n"
            "\n"
            "ARGUMENTS\n"
            "  FILE ...          One or more log file paths.\n"
            "\n"
            "OPTIONS\n"
            "  --split MODE      How to open logs on startup.\n"
            "                    tab (default) | vertical | horizontal\n"
            "  --tail N          Lines to load from the end of each file (default: 100).\n"
            "\n"
            "KEYBOARD SHORTCUTS\n"
            "  Ctrl+F            Focus sidebar search\n"
            "  Ctrl+Shift+F      Toggle sidebar\n"
            "\n"
            "EXAMPLES\n"
            "  simplelog\n"
            "  simplelog /var/log/syslog\n"
            "  simplelog --tail 500 /var/log/nginx/access.log\n"
            "  simplelog --split vertical app.log error.log\n"
            "  journalctl -f | simplelog\n"
            "  kubectl logs -f my-pod | simplelog\n"
            "  docker logs -f my-container | simplelog\n"
        ),
        # ── Update dialog ─────────────────────────────────────────────
        "update_title":          "Check for Updates",
        "update_up_to_date":     "You are up to date  ({version}).",
        "update_available":      "Update available: {latest}\n\nCurrent version: {current}",
        "update_download":       "Download",
        "update_error":          "Could not check for updates:\n{error}",
        # ── Status bar ────────────────────────────────────────────────
        "status_ready":          "Ready",
        "history_loaded":        "History loaded: {n:,} events — tailing…",
        # ── Open-mode widget ──────────────────────────────────────────
        "open_as":               "Open as",
        "open_mode_tab":         "New tab",
        "open_mode_vertical":    "Split ↔  side by side",
        "open_mode_horizontal":  "Split ↕  top / bottom",
        # ── CloudWatch panel ──────────────────────────────────────────
        "cw_title":              "CloudWatch",
        "cw_card_connection":    "Connection",
        "cw_field_profile":      "Profile",
        "cw_field_region":       "Region",
        "cw_connect":            "Connect",
        "cw_connecting":         "Connecting…",
        "cw_refresh":            "Refresh",
        "cw_card_groups":        "Log Groups",
        "cw_search_groups":      "Search groups…",
        "cw_card_streams":       "Log Streams",
        "cw_card_options":       "Options",
        "cw_field_lookback":     "Load history",
        "cw_field_poll":         "Poll interval",
        "cw_field_filter":       "Filter pattern",
        "cw_filter_ph":          "CloudWatch filter pattern…",
        "cw_open":               "Open ↗",
        # ── File panel ────────────────────────────────────────────────
        "file_title":            "Log Files",
        "file_card_open":        "Open File",
        "file_desc":             "Browse your filesystem to open any log file.",
        "file_last_lines":       "Last lines:",
        "file_browse":           "Browse & Open ↗",
        "file_card_recent":      "Recent Files",
        "file_no_recent":        "No recent files",
        # ── LogViewer toolbar ─────────────────────────────────────────
        "src_cloudwatch":        "CLOUDWATCH",
        "src_file":              "FILE",
        "src_stdin":             "STDIN",
        "viewer_autoscroll":     "Auto-scroll",
        "viewer_timestamps":     "Timestamps",
        "viewer_clear":          "Clear",
        "viewer_stop":           "Stop",
        "viewer_lines":          "{n:,} lines",
        # ── Sidebar ───────────────────────────────────────────────────────
        "sidebar_search":        "Search",
        "sidebar_filter":        "Filter",
        "sidebar_json_keys":     "JSON Keys",
        "sidebar_add_and":       "+ AND",
        "sidebar_add_or":        "+ OR",
        "sidebar_prev":          "▲ Prev",
        "sidebar_next":          "▼ Next",
        "sidebar_hits":          "{n:,} hits",
        "sidebar_no_hits":       "No results",
        "sidebar_term_ph":       "Term…",
        "sidebar_live_filter":   "Live",
        "sidebar_json_ph":       "Detected keys…",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "File not found",
        "err_cannot_open":       "Cannot open: {path}",
        "err_worker":            "Worker error",
        "err_connection":        "Connection error",
        "err_streams":           "Error loading streams",
        "err_prefix":            "Error: {msg}",
    },
    "fr": {
        # ── Menu bar ──────────────────────────────────────────────────
        "menu_file":             "Fichier",
        "menu_edit":             "Édition",
        "menu_language":         "Langage",
        "menu_help":             "Aide",
        "action_open":           "Ouvrir…",
        "action_update":         "Mettre à jour",
        "action_quit":           "Quitter",
        "action_copy":           "Copier",
        "lang_english":          "English",
        "lang_french":           "Français",
        "action_help_ref":       "Référence CLI",
        # ── Help dialog ───────────────────────────────────────────────
        "help_title":            "Référence CLI — SimpleLog",
        "help_content": (
            "UTILISATION\n"
            "  simplelog [OPTIONS] [FICHIER ...]\n"
            "  commande | simplelog [OPTIONS]\n"
            "\n"
            "ARGUMENTS\n"
            "  FICHIER ...       Un ou plusieurs chemins de fichiers de log.\n"
            "\n"
            "OPTIONS\n"
            "  --split MODE      Disposition à l'ouverture.\n"
            "                    tab (défaut) | vertical | horizontal\n"
            "  --tail N          Lignes à charger depuis la fin du fichier (défaut : 100).\n"
            "\n"
            "RACCOURCIS CLAVIER\n"
            "  Ctrl+F            Activer la recherche dans la sidebar\n"
            "  Ctrl+Shift+F      Afficher / masquer la sidebar\n"
            "\n"
            "EXEMPLES\n"
            "  simplelog\n"
            "  simplelog /var/log/syslog\n"
            "  simplelog --tail 500 /var/log/nginx/access.log\n"
            "  simplelog --split vertical app.log error.log\n"
            "  journalctl -f | simplelog\n"
            "  kubectl logs -f my-pod | simplelog\n"
            "  docker logs -f my-container | simplelog\n"
        ),
        # ── Update dialog ─────────────────────────────────────────────
        "update_title":          "Mise à jour",
        "update_up_to_date":     "L'application est à jour  ({version}).",
        "update_available":      "Mise à jour disponible : {latest}\n\nVersion actuelle : {current}",
        "update_download":       "Télécharger",
        "update_error":          "Impossible de vérifier les mises à jour :\n{error}",
        # ── Status bar ────────────────────────────────────────────────
        "status_ready":          "Prêt",
        "history_loaded":        "Historique chargé : {n:,} événements — surveillance…",
        # ── Open-mode widget ──────────────────────────────────────────
        "open_as":               "Ouvrir comme",
        "open_mode_tab":         "Nouvel onglet",
        "open_mode_vertical":    "Split ↔  côte à côte",
        "open_mode_horizontal":  "Split ↕  haut / bas",
        # ── CloudWatch panel ──────────────────────────────────────────
        "cw_title":              "CloudWatch",
        "cw_card_connection":    "Connexion",
        "cw_field_profile":      "Profil",
        "cw_field_region":       "Région",
        "cw_connect":            "Connecter",
        "cw_connecting":         "Connexion…",
        "cw_refresh":            "Actualiser",
        "cw_card_groups":        "Groupes de logs",
        "cw_search_groups":      "Rechercher…",
        "cw_card_streams":       "Flux de logs",
        "cw_card_options":       "Options",
        "cw_field_lookback":     "Historique",
        "cw_field_poll":         "Intervalle",
        "cw_field_filter":       "Filtre",
        "cw_filter_ph":          "Filtre CloudWatch…",
        "cw_open":               "Ouvrir ↗",
        # ── File panel ────────────────────────────────────────────────
        "file_title":            "Fichiers de logs",
        "file_card_open":        "Ouvrir un fichier",
        "file_desc":             "Parcourez votre système de fichiers pour ouvrir un fichier de log.",
        "file_last_lines":       "Dernières lignes :",
        "file_browse":           "Parcourir & Ouvrir ↗",
        "file_card_recent":      "Fichiers récents",
        "file_no_recent":        "Aucun fichier récent",
        # ── LogViewer toolbar ─────────────────────────────────────────
        "src_cloudwatch":        "CLOUDWATCH",
        "src_file":              "FICHIER",
        "src_stdin":             "STDIN",
        "viewer_autoscroll":     "Défilement auto",
        "viewer_timestamps":     "Timestamps",
        "viewer_clear":          "Effacer",
        "viewer_stop":           "Arrêter",
        "viewer_lines":          "{n:,} lignes",
        # ── Sidebar ───────────────────────────────────────────────────────
        "sidebar_search":        "Recherche",
        "sidebar_filter":        "Filtrer",
        "sidebar_json_keys":     "Clés JSON",
        "sidebar_add_and":       "+ ET",
        "sidebar_add_or":        "+ OU",
        "sidebar_prev":          "▲ Préc",
        "sidebar_next":          "▼ Suiv",
        "sidebar_hits":          "{n:,} résultats",
        "sidebar_no_hits":       "Aucun résultat",
        "sidebar_term_ph":       "Terme…",
        "sidebar_live_filter":   "En direct",
        "sidebar_json_ph":       "Clés détectées…",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "Fichier introuvable",
        "err_cannot_open":       "Impossible d'ouvrir : {path}",
        "err_worker":            "Erreur worker",
        "err_connection":        "Erreur de connexion",
        "err_streams":           "Erreur lors du chargement des flux",
        "err_prefix":            "Erreur : {msg}",
    },
}


def tr(key: str, **kwargs: object) -> str:
    """Return translated string for *key* in the current locale."""
    lang = _STRINGS.get(_locale, _STRINGS["en"])
    text = lang.get(key) or _STRINGS["en"].get(key) or key
    return text.format(**kwargs) if kwargs else text


def set_locale(locale: str) -> None:
    global _locale
    _locale = locale if locale in _STRINGS else "en"


def get_locale() -> str:
    return _locale
