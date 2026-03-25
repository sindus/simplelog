# Filter & Search Sidebar — Design Spec

**Date:** 2026-03-25
**Status:** Approved
**Scope:** Global right sidebar in SimpleLog (PyQt6) providing multi-term filter and search on the active log viewer.

---

## 1. Overview

Add a collapsible right sidebar to `MainWindow` containing two panels:

1. **Filter** — hide/show log lines based on one or more text terms (AND/OR conditions). Optionally use detected JSON keys as filter targets.
2. **Search** — find and navigate occurrences of one or more terms (AND/OR). Replaces the existing single-term search bar in the `LogViewer` toolbar.

The sidebar is **global**: one instance per window, always operating on the currently active `LogViewer`. Filter/search terms persist across viewer switches (the same terms are re-applied when you activate a different tab).

---

## 2. Architecture

### 2.1 New widget: `FilterSearchSidebar`

A `QWidget` added to the right of `self._splitter` in `MainWindow._build_ui()`. Width ~280 px, collapsible via a toggle button (or `Ctrl+Shift+F`).

Internal layout (top to bottom):

```
┌──────────────────────────────┐
│  🔍 SEARCH                   │
│  [term input]          [×]   │
│  AND [term input]      [×]   │
│  [+ AND]  [+ OR]             │
│  [▲ Prev]  [▼ Next]  n hits  │
├──────────────────────────────┤
│  🔧 FILTER                   │
│  [term input]          [×]   │
│  OR  [term input]      [×]   │
│  [+ AND]  [+ OR]             │
│  [✓ Live]                    │
├──────────────────────────────┤
│  {} JSON KEYS                │
│  [requestId]  [level]        │
│  [userId]  [service]  ...    │
└──────────────────────────────┘
```

State held by the sidebar:
- `_filter_terms: list[TermRow]`
- `_search_terms: list[TermRow]`
- `_active_viewer: LogViewer | None`

### 2.2 `TermRow`

Lightweight data class:
```python
@dataclass
class TermRow:
    text: str
    operator: Literal["AND", "OR"]   # ignored for first term
```

### 2.3 Changes to `LogViewer`

| Addition | Purpose |
|---|---|
| `_raw_events: list[tuple[int, str]]` | Buffer of all received events (capped at `_MAX_LINES`) |
| `_json_keys: set[str]` | Accumulated top-level JSON keys |
| `json_keys_updated = pyqtSignal(set)` | Emitted when new keys are found |
| `apply_filter(terms)` | Clear QTextEdit, re-render buffer through filter |
| `get_json_keys() -> set[str]` | Returns current key set |
| `apply_search(terms) -> int` | Updates search highlighter, returns match count |
| `search_next() / search_prev()` | Navigate to next/prev search match |

The existing `search_input` QLineEdit and its related code in `_build_ui` / `retranslate` / `_search_next` / `_action_paste` is removed from the toolbar.

### 2.4 Changes to `LogHighlighter`

Add a **dynamic** rule set for search highlights (yellow background `#3a3a00` on matching spans). The highlighter exposes `set_search_terms(terms)` which updates its rules and calls `rehighlight()`.

### 2.5 Changes to `MainWindow`

- `_build_ui`: add `FilterSearchSidebar` to the right of `self._splitter` in the root `QHBoxLayout`.
- `_set_active_pane` and `_add_tab`: notify the sidebar of the new active viewer via `sidebar.set_active_viewer(viewer)`.
- Remove `_action_paste` logic tied to `search_input` (or redirect to sidebar).
- Add `Ctrl+Shift+F` shortcut to toggle sidebar visibility.

---

## 3. Filter Logic

### 3.1 Matching a single line

```
terms = [(text1, op1), (text2, op2), ...]

match = text1 in line          # first term — no operator
for (text, op) in terms[1:]:
    hit = text in line         # case-insensitive
    if op == "AND":
        match = match and hit
    elif op == "OR":
        match = match or hit

show line if match (or if terms is empty)
```

Case-insensitive by default. No regex (keeps it accessible).

### 3.2 Live filter

Filter is applied live as the user types (debounced 150 ms to avoid re-rendering on every keystroke). `apply_filter` clears the `QTextEdit` and re-inserts only matching lines from `_raw_events`.

### 3.3 JSON key filter

Clicking a JSON key chip in the sidebar appends a new filter term row pre-filled with the key name. The user can edit it (e.g., to `"key": "value"` substring matching).

---

## 4. Search Logic

Same multi-term AND/OR model. Instead of hiding non-matching lines, search **highlights** matching spans (yellow background) across all visible lines using `LogHighlighter`. Navigation (`search_next` / `search_prev`) uses `QTextEdit.find()` extended to cycle through terms.

Match count displayed as `n résultats` beneath the navigation buttons.

---

## 5. JSON Key Detection

On each `append_events` call, for each new line:

1. Try `json.loads(line)` — if it parses as a dict, extract top-level keys.
2. Otherwise, use a regex `\{[^}]{1,2000}\}` to find a JSON object substring, then parse.
3. New keys are added to `_json_keys` and `json_keys_updated` is emitted.

The sidebar listens to `json_keys_updated` on the active viewer and updates its key chip panel (sorted alphabetically, max 50 chips to avoid overflow).

---

## 6. Sidebar Toggle

- Button `⟩` / `⟨` in the `MainWindow` toolbar area (or right-edge of the splitter) toggles visibility.
- Keyboard shortcut: `Ctrl+Shift+F`.
- State is not persisted across sessions (intentional; workspace feature will handle layout persistence).

---

## 7. i18n

New translation keys (EN/FR):

| Key | EN | FR |
|---|---|---|
| `sidebar_search` | Search | Recherche |
| `sidebar_filter` | Filter | Filtrer |
| `sidebar_json_keys` | JSON Keys | Clés JSON |
| `sidebar_add_and` | + AND | + ET |
| `sidebar_add_or` | + OR | + OU |
| `sidebar_prev` | ▲ Prev | ▲ Préc |
| `sidebar_next` | ▼ Next | ▼ Suiv |
| `sidebar_hits` | {n} hits | {n} résultats |
| `sidebar_no_hits` | No results | Aucun résultat |
| `sidebar_json_ph` | Detected keys | Clés détectées |
| `sidebar_term_ph` | Term… | Terme… |

---

## 8. Out of Scope

- Regex filter mode (future)
- Negation / exclude filter (future)
- Per-viewer saved filter sets (future, workspace feature)
- Filter on CloudWatch server side (kept as-is via existing `filter_input`)
