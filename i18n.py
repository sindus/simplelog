"""i18n.py — Minimal EN / FR translation support for SimpleLog."""
from __future__ import annotations

import json
from pathlib import Path

_locale: str = "en"
_PREFS_PATH = Path.home() / ".config" / "simplelog" / "prefs.json"

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
        "action_close_all":      "Close All Logs",
        "action_update":         "Check for Updates",
        "action_quit":           "Quit",
        "action_copy":           "Copy",
        "action_break":          "Break",
        "lang_english":          "English",
        "lang_french":           "Français",
        "lang_german":           "Deutsch",
        "lang_spanish":          "Español",
        "lang_chinese":          "中文",
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
        "update_install":        "Install Update",
        "update_downloading":    "Downloading update…",
        "update_restarting":     "Update downloaded. The app will restart now.",
        "update_error":          "Could not check for updates:\n{error}",
        "update_install_error":  "Update failed:\n{error}",
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
        "cw_auth_mode":          "Auth mode",
        "cw_auth_profile":       "AWS Profile",
        "cw_auth_keys":          "Access Keys",
        "cw_field_profile":      "Profile",
        "cw_field_access_key":   "Access Key ID",
        "cw_field_secret_key":   "Secret Access Key",
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
        # ── Workspace panel ───────────────────────────────────────────
        "ws_title":              "Workspaces",
        "ws_name_ph":            "Workspace name…",
        "ws_save_btn":           "Save current layout",
        "ws_name_required":      "Enter a name first…",
        "ws_open":               "Open",
        "ws_rename":             "Rename",
        "ws_delete":             "Delete",
        "ws_logs_count":         "{n} log{s}",
        "ws_no_logs":            "Workspace: no saveable logs open.",
        "ws_saved":              "Workspace \"{name}\" saved ({n} log(s)).",
        "ws_file_missing":       "Workspace: file not found — {path}",
        "ws_no_logs_to_open":    "Workspace \"{name}\": no logs to open",
        "ws_cw_error":           "Workspace: CloudWatch error — {error}",
        "ws_opened":             "Workspace \"{name}\": {opened} log(s) opened",
        "ws_skipped":            ", {n} skipped",
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
        "action_close_all":      "Fermer tous les logs",
        "action_update":         "Mettre à jour",
        "action_quit":           "Quitter",
        "action_copy":           "Copier",
        "action_break":          "Break",
        "lang_english":          "English",
        "lang_french":           "Français",
        "lang_german":           "Deutsch",
        "lang_spanish":          "Español",
        "lang_chinese":          "中文",
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
        "update_install":        "Installer la mise à jour",
        "update_downloading":    "Téléchargement de la mise à jour…",
        "update_restarting":     "Mise à jour téléchargée. L'application va redémarrer.",
        "update_error":          "Impossible de vérifier les mises à jour :\n{error}",
        "update_install_error":  "Échec de la mise à jour :\n{error}",
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
        "cw_auth_mode":          "Mode d'auth",
        "cw_auth_profile":       "Profil AWS",
        "cw_auth_keys":          "Clés d'accès",
        "cw_field_profile":      "Profil",
        "cw_field_access_key":   "Access Key ID",
        "cw_field_secret_key":   "Secret Access Key",
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
        # ── Workspace panel ───────────────────────────────────────────
        "ws_title":              "Espaces de travail",
        "ws_name_ph":            "Nom du workspace…",
        "ws_save_btn":           "Enregistrer le layout actuel",
        "ws_name_required":      "Entre un nom d'abord…",
        "ws_open":               "Ouvrir",
        "ws_rename":             "Renommer",
        "ws_delete":             "Supprimer",
        "ws_logs_count":         "{n} log{s}",
        "ws_no_logs":            "Workspace : aucun log sauvegardable ouvert.",
        "ws_saved":              "Workspace « {name} » enregistré ({n} log(s)).",
        "ws_file_missing":       "Workspace : fichier introuvable — {path}",
        "ws_no_logs_to_open":    "Workspace « {name} » : aucun log à ouvrir",
        "ws_cw_error":           "Workspace : erreur CloudWatch — {error}",
        "ws_opened":             "Workspace « {name} » : {opened} log(s) ouvert(s)",
        "ws_skipped":            ", {n} ignoré(s)",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "Fichier introuvable",
        "err_cannot_open":       "Impossible d'ouvrir : {path}",
        "err_worker":            "Erreur worker",
        "err_connection":        "Erreur de connexion",
        "err_streams":           "Erreur lors du chargement des flux",
        "err_prefix":            "Erreur : {msg}",
    },
    "de": {
        # ── Menu bar ──────────────────────────────────────────────────
        "menu_file":             "Datei",
        "menu_edit":             "Bearbeiten",
        "menu_language":         "Sprache",
        "menu_help":             "Hilfe",
        "action_open":           "Öffnen…",
        "action_close_all":      "Alle Logs schließen",
        "action_update":         "Auf Updates prüfen",
        "action_quit":           "Beenden",
        "action_copy":           "Kopieren",
        "action_break":          "Break",
        "lang_english":          "English",
        "lang_french":           "Français",
        "lang_german":           "Deutsch",
        "lang_spanish":          "Español",
        "lang_chinese":          "中文",
        "action_help_ref":       "CLI-Referenz",
        # ── Help dialog ───────────────────────────────────────────────
        "help_title":            "CLI-Referenz — SimpleLog",
        "help_content": (
            "VERWENDUNG\n"
            "  simplelog [OPTIONEN] [DATEI ...]\n"
            "  befehl | simplelog [OPTIONEN]\n"
            "\n"
            "ARGUMENTE\n"
            "  DATEI ...         Ein oder mehrere Log-Dateipfade.\n"
            "\n"
            "OPTIONEN\n"
            "  --split MODUS     Ansicht beim Start.\n"
            "                    tab (Standard) | vertical | horizontal\n"
            "  --tail N          Zeilen vom Dateiende (Standard: 100).\n"
            "\n"
            "TASTENKÜRZEL\n"
            "  Ctrl+F            Sidebar-Suche fokussieren\n"
            "  Ctrl+Shift+F      Sidebar umschalten\n"
            "\n"
            "BEISPIELE\n"
            "  simplelog\n"
            "  simplelog /var/log/syslog\n"
            "  simplelog --tail 500 /var/log/nginx/access.log\n"
            "  simplelog --split vertical app.log error.log\n"
            "  journalctl -f | simplelog\n"
            "  kubectl logs -f my-pod | simplelog\n"
            "  docker logs -f my-container | simplelog\n"
        ),
        # ── Update dialog ─────────────────────────────────────────────
        "update_title":          "Auf Updates prüfen",
        "update_up_to_date":     "Sie sind auf dem neuesten Stand  ({version}).",
        "update_available":      "Update verfügbar: {latest}\n\nAktuelle Version: {current}",
        "update_download":       "Herunterladen",
        "update_install":        "Update installieren",
        "update_downloading":    "Update wird heruntergeladen…",
        "update_restarting":     "Update heruntergeladen. Die App wird jetzt neu gestartet.",
        "update_error":          "Updates konnten nicht geprüft werden:\n{error}",
        "update_install_error":  "Update fehlgeschlagen:\n{error}",
        # ── Status bar ────────────────────────────────────────────────
        "status_ready":          "Bereit",
        "history_loaded":        "Verlauf geladen: {n:,} Ereignisse — läuft…",
        # ── Open-mode widget ──────────────────────────────────────────
        "open_as":               "Öffnen als",
        "open_mode_tab":         "Neuer Tab",
        "open_mode_vertical":    "Split ↔  nebeneinander",
        "open_mode_horizontal":  "Split ↕  oben / unten",
        # ── CloudWatch panel ──────────────────────────────────────────
        "cw_title":              "CloudWatch",
        "cw_card_connection":    "Verbindung",
        "cw_auth_mode":          "Auth-Modus",
        "cw_auth_profile":       "AWS-Profil",
        "cw_auth_keys":          "Zugriffsschlüssel",
        "cw_field_profile":      "Profil",
        "cw_field_access_key":   "Access Key ID",
        "cw_field_secret_key":   "Secret Access Key",
        "cw_field_region":       "Region",
        "cw_connect":            "Verbinden",
        "cw_connecting":         "Verbinde…",
        "cw_refresh":            "Aktualisieren",
        "cw_card_groups":        "Log-Gruppen",
        "cw_search_groups":      "Gruppen suchen…",
        "cw_card_streams":       "Log-Streams",
        "cw_card_options":       "Optionen",
        "cw_field_lookback":     "Verlauf laden",
        "cw_field_poll":         "Abfrageintervall",
        "cw_field_filter":       "Filtermuster",
        "cw_filter_ph":          "CloudWatch-Filtermuster…",
        "cw_open":               "Öffnen ↗",
        # ── File panel ────────────────────────────────────────────────
        "file_title":            "Log-Dateien",
        "file_card_open":        "Datei öffnen",
        "file_desc":             "Durchsuchen Sie Ihr Dateisystem, um eine Log-Datei zu öffnen.",
        "file_last_lines":       "Letzte Zeilen:",
        "file_browse":           "Durchsuchen & Öffnen ↗",
        "file_card_recent":      "Zuletzt geöffnet",
        "file_no_recent":        "Keine zuletzt geöffneten Dateien",
        # ── LogViewer toolbar ─────────────────────────────────────────
        "src_cloudwatch":        "CLOUDWATCH",
        "src_file":              "DATEI",
        "src_stdin":             "STDIN",
        "viewer_autoscroll":     "Auto-Scrollen",
        "viewer_timestamps":     "Zeitstempel",
        "viewer_clear":          "Löschen",
        "viewer_stop":           "Stoppen",
        "viewer_lines":          "{n:,} Zeilen",
        # ── Sidebar ───────────────────────────────────────────────────────
        "sidebar_search":        "Suche",
        "sidebar_filter":        "Filter",
        "sidebar_json_keys":     "JSON-Schlüssel",
        "sidebar_add_and":       "+ UND",
        "sidebar_add_or":        "+ ODER",
        "sidebar_prev":          "▲ Vorh.",
        "sidebar_next":          "▼ Nächste",
        "sidebar_hits":          "{n:,} Treffer",
        "sidebar_no_hits":       "Keine Ergebnisse",
        "sidebar_term_ph":       "Begriff…",
        "sidebar_live_filter":   "Live",
        "sidebar_json_ph":       "Erkannte Schlüssel…",
        # ── Workspace panel ───────────────────────────────────────────
        "ws_title":              "Arbeitsbereiche",
        "ws_name_ph":            "Name des Arbeitsbereichs…",
        "ws_save_btn":           "Aktuelles Layout speichern",
        "ws_name_required":      "Zuerst einen Namen eingeben…",
        "ws_open":               "Öffnen",
        "ws_rename":             "Umbenennen",
        "ws_delete":             "Löschen",
        "ws_logs_count":         "{n} Log{s}",
        "ws_no_logs":            "Arbeitsbereich: keine speicherbaren Logs geöffnet.",
        "ws_saved":              "Arbeitsbereich \"{name}\" gespeichert ({n} Log(s)).",
        "ws_file_missing":       "Arbeitsbereich: Datei nicht gefunden — {path}",
        "ws_no_logs_to_open":    "Arbeitsbereich \"{name}\": keine Logs zum Öffnen",
        "ws_cw_error":           "Arbeitsbereich: CloudWatch-Fehler — {error}",
        "ws_opened":             "Arbeitsbereich \"{name}\": {opened} Log(s) geöffnet",
        "ws_skipped":            ", {n} übersprungen",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "Datei nicht gefunden",
        "err_cannot_open":       "Kann nicht geöffnet werden: {path}",
        "err_worker":            "Worker-Fehler",
        "err_connection":        "Verbindungsfehler",
        "err_streams":           "Fehler beim Laden der Streams",
        "err_prefix":            "Fehler: {msg}",
    },
    "es": {
        # ── Menu bar ──────────────────────────────────────────────────
        "menu_file":             "Archivo",
        "menu_edit":             "Editar",
        "menu_language":         "Idioma",
        "menu_help":             "Ayuda",
        "action_open":           "Abrir…",
        "action_close_all":      "Cerrar todos los logs",
        "action_update":         "Buscar actualizaciones",
        "action_quit":           "Salir",
        "action_copy":           "Copiar",
        "action_break":          "Break",
        "lang_english":          "English",
        "lang_french":           "Français",
        "lang_german":           "Deutsch",
        "lang_spanish":          "Español",
        "lang_chinese":          "中文",
        "action_help_ref":       "Referencia CLI",
        # ── Help dialog ───────────────────────────────────────────────
        "help_title":            "Referencia CLI — SimpleLog",
        "help_content": (
            "USO\n"
            "  simplelog [OPCIONES] [ARCHIVO ...]\n"
            "  comando | simplelog [OPCIONES]\n"
            "\n"
            "ARGUMENTOS\n"
            "  ARCHIVO ...       Una o más rutas de archivos de log.\n"
            "\n"
            "OPCIONES\n"
            "  --split MODO      Disposición al iniciar.\n"
            "                    tab (predeterminado) | vertical | horizontal\n"
            "  --tail N          Líneas desde el final del archivo (predeterminado: 100).\n"
            "\n"
            "ATAJOS DE TECLADO\n"
            "  Ctrl+F            Enfocar la búsqueda de la barra lateral\n"
            "  Ctrl+Shift+F      Alternar barra lateral\n"
            "\n"
            "EJEMPLOS\n"
            "  simplelog\n"
            "  simplelog /var/log/syslog\n"
            "  simplelog --tail 500 /var/log/nginx/access.log\n"
            "  simplelog --split vertical app.log error.log\n"
            "  journalctl -f | simplelog\n"
            "  kubectl logs -f my-pod | simplelog\n"
            "  docker logs -f my-container | simplelog\n"
        ),
        # ── Update dialog ─────────────────────────────────────────────
        "update_title":          "Buscar actualizaciones",
        "update_up_to_date":     "Estás al día  ({version}).",
        "update_available":      "Actualización disponible: {latest}\n\nVersión actual: {current}",
        "update_download":       "Descargar",
        "update_install":        "Instalar actualización",
        "update_downloading":    "Descargando actualización…",
        "update_restarting":     "Actualización descargada. La app se reiniciará ahora.",
        "update_error":          "No se pudieron buscar actualizaciones:\n{error}",
        "update_install_error":  "Error en la actualización:\n{error}",
        # ── Status bar ────────────────────────────────────────────────
        "status_ready":          "Listo",
        "history_loaded":        "Historial cargado: {n:,} eventos — siguiendo…",
        # ── Open-mode widget ──────────────────────────────────────────
        "open_as":               "Abrir como",
        "open_mode_tab":         "Nueva pestaña",
        "open_mode_vertical":    "Split ↔  lado a lado",
        "open_mode_horizontal":  "Split ↕  arriba / abajo",
        # ── CloudWatch panel ──────────────────────────────────────────
        "cw_title":              "CloudWatch",
        "cw_card_connection":    "Conexión",
        "cw_auth_mode":          "Modo auth",
        "cw_auth_profile":       "Perfil AWS",
        "cw_auth_keys":          "Claves de acceso",
        "cw_field_profile":      "Perfil",
        "cw_field_access_key":   "Access Key ID",
        "cw_field_secret_key":   "Secret Access Key",
        "cw_field_region":       "Región",
        "cw_connect":            "Conectar",
        "cw_connecting":         "Conectando…",
        "cw_refresh":            "Actualizar",
        "cw_card_groups":        "Grupos de logs",
        "cw_search_groups":      "Buscar grupos…",
        "cw_card_streams":       "Flujos de logs",
        "cw_card_options":       "Opciones",
        "cw_field_lookback":     "Cargar historial",
        "cw_field_poll":         "Intervalo",
        "cw_field_filter":       "Patrón de filtro",
        "cw_filter_ph":          "Patrón de filtro CloudWatch…",
        "cw_open":               "Abrir ↗",
        # ── File panel ────────────────────────────────────────────────
        "file_title":            "Archivos de logs",
        "file_card_open":        "Abrir archivo",
        "file_desc":             "Navega por tu sistema de archivos para abrir un archivo de log.",
        "file_last_lines":       "Últimas líneas:",
        "file_browse":           "Explorar & Abrir ↗",
        "file_card_recent":      "Archivos recientes",
        "file_no_recent":        "Sin archivos recientes",
        # ── LogViewer toolbar ─────────────────────────────────────────
        "src_cloudwatch":        "CLOUDWATCH",
        "src_file":              "ARCHIVO",
        "src_stdin":             "STDIN",
        "viewer_autoscroll":     "Auto-scroll",
        "viewer_timestamps":     "Marcas de tiempo",
        "viewer_clear":          "Limpiar",
        "viewer_stop":           "Detener",
        "viewer_lines":          "{n:,} líneas",
        # ── Sidebar ───────────────────────────────────────────────────────
        "sidebar_search":        "Buscar",
        "sidebar_filter":        "Filtrar",
        "sidebar_json_keys":     "Claves JSON",
        "sidebar_add_and":       "+ Y",
        "sidebar_add_or":        "+ O",
        "sidebar_prev":          "▲ Ant.",
        "sidebar_next":          "▼ Sig.",
        "sidebar_hits":          "{n:,} resultados",
        "sidebar_no_hits":       "Sin resultados",
        "sidebar_term_ph":       "Término…",
        "sidebar_live_filter":   "En vivo",
        "sidebar_json_ph":       "Claves detectadas…",
        # ── Workspace panel ───────────────────────────────────────────
        "ws_title":              "Espacios de trabajo",
        "ws_name_ph":            "Nombre del workspace…",
        "ws_save_btn":           "Guardar diseño actual",
        "ws_name_required":      "Introduce un nombre primero…",
        "ws_open":               "Abrir",
        "ws_rename":             "Renombrar",
        "ws_delete":             "Eliminar",
        "ws_logs_count":         "{n} log{s}",
        "ws_no_logs":            "Workspace: no hay logs guardables abiertos.",
        "ws_saved":              "Workspace \"{name}\" guardado ({n} log(s)).",
        "ws_file_missing":       "Workspace: archivo no encontrado — {path}",
        "ws_no_logs_to_open":    "Workspace \"{name}\": no hay logs que abrir",
        "ws_cw_error":           "Workspace: error de CloudWatch — {error}",
        "ws_opened":             "Workspace \"{name}\": {opened} log(s) abiertos",
        "ws_skipped":            ", {n} omitidos",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "Archivo no encontrado",
        "err_cannot_open":       "No se puede abrir: {path}",
        "err_worker":            "Error del worker",
        "err_connection":        "Error de conexión",
        "err_streams":           "Error al cargar los flujos",
        "err_prefix":            "Error: {msg}",
    },
    "zh": {
        # ── Menu bar ──────────────────────────────────────────────────
        "menu_file":             "文件",
        "menu_edit":             "编辑",
        "menu_language":         "语言",
        "menu_help":             "帮助",
        "action_open":           "打开…",
        "action_close_all":      "关闭所有日志",
        "action_update":         "检查更新",
        "action_quit":           "退出",
        "action_copy":           "复制",
        "action_break":          "中断",
        "lang_english":          "English",
        "lang_french":           "Français",
        "lang_german":           "Deutsch",
        "lang_spanish":          "Español",
        "lang_chinese":          "中文",
        "action_help_ref":       "CLI 参考",
        # ── Help dialog ───────────────────────────────────────────────
        "help_title":            "CLI 参考 — SimpleLog",
        "help_content": (
            "用法\n"
            "  simplelog [选项] [文件 ...]\n"
            "  命令 | simplelog [选项]\n"
            "\n"
            "参数\n"
            "  文件 ...          一个或多个日志文件路径。\n"
            "\n"
            "选项\n"
            "  --split 模式      启动时的布局方式。\n"
            "                    tab（默认）| vertical | horizontal\n"
            "  --tail N          从文件末尾加载的行数（默认：100）。\n"
            "\n"
            "键盘快捷键\n"
            "  Ctrl+F            聚焦侧边栏搜索\n"
            "  Ctrl+Shift+F      切换侧边栏\n"
            "\n"
            "示例\n"
            "  simplelog\n"
            "  simplelog /var/log/syslog\n"
            "  simplelog --tail 500 /var/log/nginx/access.log\n"
            "  simplelog --split vertical app.log error.log\n"
            "  journalctl -f | simplelog\n"
            "  kubectl logs -f my-pod | simplelog\n"
            "  docker logs -f my-container | simplelog\n"
        ),
        # ── Update dialog ─────────────────────────────────────────────
        "update_title":          "检查更新",
        "update_up_to_date":     "已是最新版本  ({version})。",
        "update_available":      "发现新版本：{latest}\n\n当前版本：{current}",
        "update_download":       "下载",
        "update_install":        "安装更新",
        "update_downloading":    "正在下载更新…",
        "update_restarting":     "更新已下载，应用即将重启。",
        "update_error":          "无法检查更新：\n{error}",
        "update_install_error":  "更新失败：\n{error}",
        # ── Status bar ────────────────────────────────────────────────
        "status_ready":          "就绪",
        "history_loaded":        "历史记录已加载：{n:,} 条事件 — 正在追踪…",
        # ── Open-mode widget ──────────────────────────────────────────
        "open_as":               "打开方式",
        "open_mode_tab":         "新标签页",
        "open_mode_vertical":    "Split ↔  左右分割",
        "open_mode_horizontal":  "Split ↕  上下分割",
        # ── CloudWatch panel ──────────────────────────────────────────
        "cw_title":              "CloudWatch",
        "cw_card_connection":    "连接",
        "cw_auth_mode":          "认证方式",
        "cw_auth_profile":       "AWS 配置文件",
        "cw_auth_keys":          "访问密钥",
        "cw_field_profile":      "配置文件",
        "cw_field_access_key":   "Access Key ID",
        "cw_field_secret_key":   "Secret Access Key",
        "cw_field_region":       "区域",
        "cw_connect":            "连接",
        "cw_connecting":         "连接中…",
        "cw_refresh":            "刷新",
        "cw_card_groups":        "日志组",
        "cw_search_groups":      "搜索日志组…",
        "cw_card_streams":       "日志流",
        "cw_card_options":       "选项",
        "cw_field_lookback":     "加载历史",
        "cw_field_poll":         "轮询间隔",
        "cw_field_filter":       "过滤模式",
        "cw_filter_ph":          "CloudWatch 过滤模式…",
        "cw_open":               "打开 ↗",
        # ── File panel ────────────────────────────────────────────────
        "file_title":            "日志文件",
        "file_card_open":        "打开文件",
        "file_desc":             "浏览文件系统以打开日志文件。",
        "file_last_lines":       "最后几行：",
        "file_browse":           "浏览并打开 ↗",
        "file_card_recent":      "最近文件",
        "file_no_recent":        "无最近文件",
        # ── LogViewer toolbar ─────────────────────────────────────────
        "src_cloudwatch":        "CLOUDWATCH",
        "src_file":              "文件",
        "src_stdin":             "STDIN",
        "viewer_autoscroll":     "自动滚动",
        "viewer_timestamps":     "时间戳",
        "viewer_clear":          "清除",
        "viewer_stop":           "停止",
        "viewer_lines":          "{n:,} 行",
        # ── Sidebar ───────────────────────────────────────────────────────
        "sidebar_search":        "搜索",
        "sidebar_filter":        "过滤",
        "sidebar_json_keys":     "JSON 键",
        "sidebar_add_and":       "+ 与",
        "sidebar_add_or":        "+ 或",
        "sidebar_prev":          "▲ 上一个",
        "sidebar_next":          "▼ 下一个",
        "sidebar_hits":          "{n:,} 个结果",
        "sidebar_no_hits":       "无结果",
        "sidebar_term_ph":       "关键词…",
        "sidebar_live_filter":   "实时",
        "sidebar_json_ph":       "已检测到的键…",
        # ── Workspace panel ───────────────────────────────────────────
        "ws_title":              "工作区",
        "ws_name_ph":            "工作区名称…",
        "ws_save_btn":           "保存当前布局",
        "ws_name_required":      "请先输入名称…",
        "ws_open":               "打开",
        "ws_rename":             "重命名",
        "ws_delete":             "删除",
        "ws_logs_count":         "{n} 个日志",
        "ws_no_logs":            "工作区：没有可保存的日志。",
        "ws_saved":              "工作区\"{name}\"已保存（{n} 个日志）。",
        "ws_file_missing":       "工作区：文件未找到 — {path}",
        "ws_no_logs_to_open":    "工作区\"{name}\"：没有可打开的日志",
        "ws_cw_error":           "工作区：CloudWatch 错误 — {error}",
        "ws_opened":             "工作区\"{name}\"：已打开 {opened} 个日志",
        "ws_skipped":            "，跳过 {n} 个",
        # ── Error / dialog messages ───────────────────────────────────
        "err_file_not_found":    "文件未找到",
        "err_cannot_open":       "无法打开：{path}",
        "err_worker":            "Worker 错误",
        "err_connection":        "连接错误",
        "err_streams":           "加载流时出错",
        "err_prefix":            "错误：{msg}",
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


def load_locale() -> None:
    """Load persisted locale preference on startup."""
    global _locale
    try:
        prefs = json.loads(_PREFS_PATH.read_text(encoding="utf-8"))
        candidate = prefs.get("locale", "en")
        if candidate in _STRINGS:
            _locale = candidate
    except Exception:
        pass


def save_locale() -> None:
    """Persist current locale to prefs file."""
    try:
        _PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            prefs = json.loads(_PREFS_PATH.read_text(encoding="utf-8"))
        except Exception:
            prefs = {}
        prefs["locale"] = _locale
        tmp = _PREFS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(prefs, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_PREFS_PATH)
    except Exception:
        pass
