# Watch Face Window

**Script:** [Watch Face Window (script)](../window.py) · **Flow:** [diagram](../__flow/window.md)

## Purpose
The new consolidated visual-customization window (Phase ①+②, R-01):
a left `QListWidget` sidebar of eight sections beside a right
`QStackedWidget` page per section — replacing, over several phases, the
Design / Pointer Theme / Slot Theme windows and the Settings dialog's
Display/Colors groups. THIS PHASE wires five real sections (Pointer,
Ring, Hands, Umbra & Aura, Size) plus three placeholder pages (Themes &
Slots, Colors, Opacity) that simply read "Arrives in a later phase".

## Connections

### Uses
- [Theme](../../__about/theme.md) — `apply_theme`, `size_to_screen`
- `app.watch_face.pointer` / `.ring` / `.hands` / `.umbra_aura` / `.size`
  — one builder module per real section
- [Config (folder)](../../../config/___config.md) — `constants.APP_NAME`,
  `defaults.DIALOG_SQUARE_HEIGHT_FRACTION`, `defaults.SETTINGS_NAV_WIDTH_PX`

### Used by
- [Watch Controller](../../__about/controller.md) — `_open_watch_face`
  (non-modal, one live instance, raised on a second open);
  `_watch_face_setters()` wraps every setter so a pick both applies AND
  refreshes the open window

## Classes

### WatchFaceDialog(QDialog)
Non-modal, LIVE-APPLY — every section's pick calls its setter
immediately; there is nothing to commit, no OK/Cancel.

#### Methods
- `refresh(settings, setters)`: re-supplies the live settings after a
  pick applies, then rebuilds — called by the controller
- `_build()`: rebuilds the sidebar + stack from the `_SECTIONS` registry
  on every pick, KEEPING the previously selected row (the SAME
  "a fresh container reopens at row 0" fix `design_window.DesignDialog
  ._build` already carries for its `QTabWidget`)

## Design Decisions
- `_SECTIONS` is a flat `(title, builder)` tuple, `builder` a
  `(settings, setters, tr) -> QWidget` function or `None` for a
  not-yet-built placeholder — a later phase turns a `None` into a real
  module by matching the SAME shape, no registry redesign needed.
- Sidebar selection persistence mirrors `design_window.py`'s tab
  persistence exactly, for the same reason: every pick routes through
  `refresh()`, which rebuilds the whole sidebar+stack pair.
