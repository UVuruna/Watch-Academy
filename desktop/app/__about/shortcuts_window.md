# Shortcuts Window

**Script:** [Shortcuts Window (script)](../shortcuts_window.py)

## Purpose

R-37: a read-only reference dialog listing EVERY keyboard shortcut the
dial answers to — one row per `config.shortcuts.SHORTCUTS` entry
(Shortcut / Action), enumerated PROGRAMMATICALLY off the same table
`app.widget.ClockWidget.keyPressEvent` reads for real key dispatch and
`app.controller._build_menu`'s own shortcut-column labels use (Rule
#19 — never a hand-written copy that can drift from what actually
fires). Rows keep the table's own curated order (Ring/Slots/Fast
Travel/Locations, as the config module's own section comments group
them) rather than sorting alphabetically, which would scatter that
story.

Born from R-38's audit finding: the Greenwich shortcut (Ctrl+0) IS
wired and working, but a stale code comment elsewhere still claimed
"Ctrl+G" (already `open_guide`'s) — exactly the kind of drift a
hand-maintained shortcut list invites. This window is the answer: the
owner (or a future session) can always see the REAL, current bindings
at a glance, sourced from the one place they are defined.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `shortcuts.SHORTCUTS`,
  `shortcuts.shortcut_display()`, `constants.APP_NAME`,
  `defaults.SHORTCUTS_WINDOW_WIDTH_PX`/`HEIGHT_PX`
- [UI Style](ui_style.md) — the Close button pill
- [Theme](theme.md) — the dark dialog surface + table
- [UI Text Catalog](../../config/__about/ui_text.md) — `ui()`, wrapped by `_tr`

### Used by
- [Watch Controller](controller.md) — the right-click menu's
  "⌨️ Shortcuts…" entry (`_open_shortcuts()`), opened MODAL like Report
  (a reference snapshot, never left open alongside the dial)

## Classes

### `ShortcutsDialog(QDialog)`
Stay-on-top, built once from `shortcuts.SHORTCUTS` at construction (the
table never changes at runtime, so there is nothing to refresh).

#### Methods
- `__init__(overlay=None, parent=None)`: builds the two-column table
  (`shortcut_display(action_id)` for the combo, the translated
  `description` for the action), a non-editable, non-selectable,
  stretch-second-column table, and a Close button.

## Design Decisions
- **Table, not a QMenu-mirroring tree** — the shortcuts are flat
  (every entry is one physical chord), so a two-column table reads
  faster than nested groups that would need inventing a taxonomy the
  config module's own comments already provide informally.
- **Modal, like Report** — a static reference has nothing to stay
  live for; the non-modal trio (Encyclopedia/Guide/Observatory) is
  reserved for content the owner reads WHILE using the dial.
