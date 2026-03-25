# UI Overhaul — Design Spec

**Date:** 2026-03-25
**Scope:** Three independent but coordinated improvements to SimpleLog's UI.

1. **Sidebar redesign** — IDE-style (VS Code/JetBrains) replacing the current flat dark layout
2. **key=value filter rows** — dedicated two-field row type for JSON key matching in the filter
3. **Inline expandable JSON** — replace `QTextEdit` with `QListView` + custom delegate to render JSON lines as collapsible rows with a key/value table

---

## 1. Sidebar Redesign

### Visual language

| Element | Value |
|---|---|
| Sidebar background | `#090909` |
| Section gap | `2px` solid `#0d0d0d` |
| Term-row block background | `#161616` |
| Term-row block border | `1px solid #2c2c2c`, `border-radius: 5px` |
| Row divider (within block) | `1px solid #2c2c2c` |
| Add buttons (`+ AND/OR/key=val`) | `color: #555`, `border: 1px solid #2a2a2a`, no background |
| JSON key chips | `color: C_TRACE`, `border: 1px solid #ce93d833`, no fill, pill shape |
| Section header | `color: #999`, `font-weight: 500`, `font-size: 11px`, collapse arrow `▼/▶` |

### Section headers

Each section has a clickable header row:
```
▼  Search                         [badge: hit count]
▶  Filter                         [badge: active term count]
▼  JSON Keys                      [badge: key count]
```

- Clicking toggles `collapsed` state (stores in instance variable per section)
- Badge is a small pill `color: #444`, `background: #1a1a1a`

### Term row block

All term rows for a section share one rounded block. Rows are separated by a 1px internal divider. Each row contains:
- **operator toggle** (AND/OR pill, hidden for first row) — `color: C_TS`, `background: #78d9ec1a`
- **input(s)** — transparent background, no border, `font-size: 11px`
- **× remove** — `color: #333`, hover `C_ERR`

### Search section extras

- Prev `▲` / Next `▼` and hit count sit on a compact inline row below the block — not separate large buttons
- Format: `▲  ▼  42 hits` in small muted text, arrows are clickable spans

### Filter section extras

- Three add-buttons: `+ AND` · `+ OR` · `+ key=val`
- Live checkbox remains, styled as small inline toggle

### JSON Keys section

- Chips wrap onto multiple lines (flex-wrap)
- Each chip click: adds a KV row to Filter pre-filled with the key (see §2)
- Cap at 50 chips (unchanged)

---

## 2. key=value Filter Rows

### Data model change

`TermRow` (existing named tuple / dataclass) gains a `key: str = ""` field:

```python
@dataclass
class TermRow:
    text: str
    operator: str = ""   # "" | "AND" | "OR"
    key: str = ""        # non-empty → key=value match mode
```

### `_TermRowWidget` — mode parameter

Constructor gains `mode: Literal["text", "kv"] = "text"`.

**KV mode layout** (replaces single input):
```
[op toggle]  [key input 60px, color C_TRACE]  [=]  [value input flex]  [×]
```

Both inputs emit `changed` on `textChanged`. `to_term_row()` reads both.

### Adding rows

Filter section add-buttons:
- `+ AND` → `_TermRowWidget("AND", mode="text")`
- `+ OR` → `_TermRowWidget("OR", mode="text")`
- `+ key=val` → `_TermRowWidget("AND", mode="kv")`

### JSON key chip click

```python
def _add_filter_from_key(self, key: str) -> None:
    # Always adds a new KV row with key pre-filled, focuses value input
    self._add_filter_row("AND", mode="kv", prefill_key=key)
    self._filter_term_widgets[-1].focus_value_input()
```

### `_line_matches` update

When `term.key` is non-empty:
1. Attempt `json.loads(line)` on the raw message (strip leading timestamp if present)
2. If parse fails → term does **not** match (line is not JSON or key absent)
3. If `term.text == ""` → match if key exists in JSON (key presence filter)
4. Otherwise → `str(data[term.key]).lower()` contains `term.text.lower()` → match

The AND/OR logic across terms is unchanged.

---

## 3. Inline Expandable JSON — QListView Architecture

### Why QListView

`QTextEdit`/`QPlainTextEdit` is a flat document with no concept of interactive per-line widgets. Expandable rows require variable-height items with click handling — a `QListView` + `QAbstractListModel` + `QStyledItemDelegate` is the correct Qt pattern for this.

### `LogItem` — data class

```python
@dataclass
class LogItem:
    ts_ms: int
    message: str          # raw log line (no timestamp prefix)
    is_json: bool
    json_data: dict | None
    main_key: str | None  # resolved "primary" key (message/msg/error/…)
    expanded: bool = False
    visible: bool = True  # False when filtered out
```

`is_json` and `json_data` are resolved at append time via `_try_parse_json(message)`.

### Main content key priority

When `is_json` is True, `main_key` is resolved in this order:

```
message · msg · error · err · data · content · text
· body · log · description · details · payload · result · output · value
```

First key found in `json_data` wins. If none found → `main_key = None`.

### Collapsed display (JSON line)

```
▶  [HH:MM:SS]  <main_value>  ·  key1=val1  ·  key2=val2  ·  +N keys
```

- `main_value`: value of `main_key` (truncated to 80 chars)
- Summary: up to 2 additional keys (excluding `main_key`, excluding timestamp-like keys)
- `+N keys` if more remain
- If `main_key is None`: show first 2 keys as `key=val`, rest hidden

### Expanded display (JSON line)

```
▼  [HH:MM:SS]  <main_value>

   key          value
   ──────────── ──────────────────────────────
   userId       usr_9af3
   status       401
   skills       toto
   …
```

Table with two columns. Key column: `C_TRACE` (purple). Value column: auto-colored (numbers → `C_DEBUG`, booleans → `C_WARN`, strings → `C_TEXT`, null → `C_MUTED`). All keys shown (no truncation in expanded state).

### `LogModel(QAbstractListModel)`

| Method | Behaviour |
|---|---|
| `rowCount()` | Number of **visible** items |
| `data(index, role)` | Returns `LogItem` fields by custom roles |
| `setData(index, value, ExpandedRole)` | Toggle expanded, `dataChanged` for the item |
| `append_events(events)` | Append new `LogItem`s, enforce `_MAX_LINES`, emit `rowsInserted` |
| `apply_filter(terms)` | Set `visible` on all items, `beginResetModel/endResetModel` |
| `clear()` | Reset to empty |
| `get_json_keys()` | Return accumulated `_json_keys` set |

Internal: `_items: list[LogItem]` (all items), `_visible: list[int]` (indices of visible items). `rowCount()` = `len(_visible)`.

### `LogDelegate(QStyledItemDelegate)`

| Method | Behaviour |
|---|---|
| `sizeHint(option, index)` | Plain/collapsed: `ROW_H = 20px`. Expanded: `ROW_H + TABLE_H_ROW * len(json_data) + TABLE_HEADER_H` |
| `paint(painter, option, index)` | Dispatch to `_paint_plain` or `_paint_json` |
| `editorEvent(event, …)` | On `MouseButtonRelease`: check if click ≤ 16px from left → toggle expanded via `model.setData` |

**`_paint_plain(painter, option, item)`**
- Classify line: `_classify_line(text) → "error"|"warn"|"info"|"debug"|"trace"|"plain"`
- Color map: `error→C_ERR`, `warn→C_WARN`, `info→C_INFO`, `debug→C_DEBUG`, `trace→C_TRACE`, `plain→#d4d4d4`
- Draw timestamp in `C_TS`, then message in classified color
- If item has search highlights: draw highlight rect behind the matching span

**`_paint_json(painter, option, item)`**
- Draw `▶/▼` in `C_MUTED`
- Draw timestamp in `C_TS`
- Draw `main_value` in line-classified color (classify based on full JSON string)
- If collapsed: draw summary pills
- If expanded: draw table rows below header row

**Search highlights in delegate**
`LogViewer` owns `_search_highlights: dict[int, list[tuple[int, int]]]` (visible item index → list of (char_start, char_len)). The delegate receives this dict via a `set_search_highlights()` method and draws a semi-transparent `#ffd54f44` rect behind matching character spans. Storing highlights on `LogViewer` (not the model) keeps the model free of display concerns.

### `apply_search` update

`LogViewer.apply_search(terms)` now returns `list[tuple[int, int, int]]` — `(visible_item_index, char_start, char_len)`.

`FilterSearchSidebar` stores these as `_search_matches`. Navigation methods change:

```python
def _scroll_to_match(self, index: int) -> None:
    if self._active_viewer is None or not self._search_matches:
        return
    visible_idx, char_start, char_len = self._search_matches[index]
    self._active_viewer.scroll_to_search_match(visible_idx, char_start, char_len)
```

`LogViewer.scroll_to_search_match(visible_idx, char_start, char_len)` calls `self._list_view.scrollTo(self._model.index(visible_idx))` and updates `_search_highlights` + triggers a repaint. The cursor-based `setTextCursor` path is removed entirely.

### Autoscroll

`LogModel` emits a `rows_appended` signal. `LogViewer` connects:
```python
self._model.rows_appended.connect(self._on_rows_appended)

def _on_rows_appended(self):
    if self.autoscroll_cb.isChecked():
        self._list_view.scrollToBottom()
```

### `timestamps_cb` — timestamp display

`timestamps_cb` (the "show timestamps" checkbox in the viewer toolbar) is **kept**. It becomes a flag on `LogViewer` that the delegate reads.

- `LogViewer` exposes `show_timestamps: bool` property (backed by `timestamps_cb.isChecked()`)
- `LogDelegate` receives a reference to the viewer and checks `viewer.show_timestamps` in `paint()`
- When `show_timestamps` is False, the `[HH:MM:SS]` prefix is omitted from all rendered rows
- The `timestamps_cb.stateChanged` signal connects to `self._list_view.viewport().update()` to repaint

### `_insert_separator` — Enter-key separator

The Enter-key separator feature (`_LogTextEdit.enter_pressed` → `_insert_separator`) is **dropped**. A `QListView` has no document to insert separator text into. This is listed in Out of scope below.

### Re-entrancy guard (`_filtering` / `_pending_during_filter`)

The `_filtering` flag and `_pending_during_filter` buffer are **removed**. They existed because the old `apply_filter` called `QApplication.processEvents()` inside a loop to avoid UI freezes, which could cause re-entrant `append_events` calls.

The new `LogModel.apply_filter` does not call `processEvents()`. It sets `visible` flags and calls `beginResetModel/endResetModel`. For 10k items this is a ~5–15ms operation (flag-setting loop, no rendering) — below perceptible threshold. `append_events` arriving during `apply_filter` will be serialised naturally on the Qt main thread with no re-entrancy risk.

### Font / style

`QListView` inherits the same monospace font as the current `QTextEdit`. Set via `setFont()`.

---

## Architecture Impact

### Files changed

| File | Change |
|---|---|
| `ui.py` | Add `LogItem`, `LogModel`, `LogDelegate`, `_classify_line`, `_try_parse_json`. Rewrite `LogViewer._build_ui` (swap `QTextEdit` → `QListView`). Update `FilterSearchSidebar`. Update `_TermRowWidget`. Update `_line_matches`. |
| `tests/test_filter_logic.py` | Add tests for KV matching, `_try_parse_json`, `_classify_line` |
| `i18n.py` | No new keys needed |

### What is NOT changing

- Worker threads (`workers.py`) — unchanged, they still emit `(ts_ms, message)` tuples
- CloudWatch / file tailing logic — unchanged
- `apply_filter` / `apply_search` public API on `LogViewer` — same signatures, internal implementation changes
- `FilterSearchSidebar.set_active_viewer()` — unchanged

### `LogHighlighter` fate

`LogHighlighter` (QSyntaxHighlighter) is removed. Its regex patterns are ported to `_classify_line()` and inline coloring within `LogDelegate.paint()`. The instance search highlight rules (added in a recent commit) are replaced by the delegate's search highlight mechanism.

---

## Out of scope

- Syntax highlighting of JSON *values* (numbers, strings) beyond the simple color-by-type table rule
- Nested JSON (objects within objects) — flattened to `str(value)` in the table
- Copy-to-clipboard of a single JSON field — future feature
- Performance profiling beyond 10k lines — existing cap unchanged
- Enter-key separator (the `─── HH:MM:SS ───` visual break) — removed, not portable to QListView
