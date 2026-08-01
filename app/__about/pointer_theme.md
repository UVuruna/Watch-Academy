# Pointer Theme

**Script:** [Pointer Theme (script)](../pointer_theme.py) · **Flow:** [diagram](../__flow/pointer_theme.md)

## Purpose
The mini window replacing the old 1st Slot ▸ Weekday submenu chain (R5
MENU REWORK item 3B): picks the weekday-BODY theme the star pointer's
own arms wear (`Settings.weekday_theme`) via the shared [Weekday Theme
Grid](weekday_theme_grid.md). While the CALENDAR pointer is active this
window grows a second tab — the MOUNT, the roster riding the Calendar's
twelve wedges (Pointers REWORK phase 2) — since a mount is CONTENT (a
roster with art, wanting a gallery) rather than SHAPE (the Design
window's own Pointer tab).

**Interpretation note (agent judgment, carried over from the pre-migration
doc, still unconfirmed by the owner):** the spec names this window
"Pointer theme" without pinning exactly which setting it edits. The 1st
Slot's own weekday-body layer is the one thing actually drawn ON the
pointer's arms, so that is what this window edits; the fuller per-slot
picture (mode, roster, metal) lives in [Slot Theme](slot_theme.md)
instead.

## Connections

### Uses
- [Weekday Theme Grid](weekday_theme_grid.md) — both galleries
- [Theme](theme.md) — `apply_theme`, `size_to_screen`

### Used by
- [Watch Controller](controller.md) — `_open_pointer_theme` (non-modal,
  one live instance, raised on a second open); `_refresh_menu_gating`
  grays the top-level menu entry AND live-grays this window's own grid
  while it is open

## Classes

### PointerThemeDialog(QDialog)
Non-modal (`.show()`), LIVE-APPLY — every option this window absorbed
already applied instantly in the old menu, so a pick calls
`on_pick(theme)` immediately; there is nothing to commit, no OK/Cancel.

#### Methods
- `__init__(current_theme, on_pick, current_mount=None, on_pick_mount=None, ...)`:
  `current_mount` is the live mount while the Calendar pointer is
  active, and `None` on every other pointer — so the window is the
  single weekday gallery everywhere except the Calendar, where it grows
  the mount tab
- `_build(current_theme, current_mount)`: returns the weekday gallery
  alone, or a `QTabWidget` of the weekday gallery + the mount gallery
- `refresh(current_theme, current_mount=None)`: rebuilds the content so
  the newly active tile's border moves — called by the controller right
  after a pick applies, keeping the window open; the OLD content widget
  is `setParent(None)` BEFORE `deleteLater()` (Qt defers the deletion to
  the event loop, so without the reparent the replaced widget stays a
  live child and anything walking the tree still finds it)
- `set_gate(available, reason)`: grays the content in place and shows a
  banner when the picker becomes unavailable (Archetype mode ON, the
  Pointer hidden, or the 1st Slot off) while the window is already open
