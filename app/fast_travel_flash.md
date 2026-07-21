# Fast Travel Flash

**Script:** [Fast Travel Flash (script)](fast_travel_flash.py)

## Purpose
The small transient overlay Fast Travel flashes above the dial on every
Ctrl+[ / Ctrl+] theme/option change (R5b FINAL MAP round, owner spec sealed
2026-07-21): an icon + the active option's text, popping in at full opacity
and fading out on its own — the only feedback the theme/option pickers give,
since they carry no menu or dialog of their own.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `FAST_TRAVEL_FLASH_*` geometry/
  timing constants, `icon_path()` for the graceful-absent icon lookup
- [Native](native.md) — `assert_topmost` to ride above the topmost dial,
  the SAME trick [Legend Popup](legend_popup.md) already uses

### Used by
- [Watch Controller](controller.md) — one instance per watch (owner spec:
  "per-watch — the focused watch flashes its own"), triggered from
  `_cycle_fast_travel_theme()` / `_cycle_fast_travel_option()`

## Classes

### FastTravelFlash
`QWidget` subclass carrying the SAME non-focus-stealing topmost window
recipe [Legend Popup](legend_popup.md) already established (`Qt.WindowType.
ToolTip | FramelessWindowHint | WindowStaysOnTopHint`, `WA_ShowWithoutActivating`,
`native.assert_topmost` on every show) — necessary here for a reason the
Legend Popup does not share: every Fast Travel shortcut needs the DIAL to
keep holding keyboard focus for the NEXT press (`ClockWidget.keyPressEvent`),
so the flash must never steal it, even for an instant.

#### Methods
- `flash(dial_widget, icon_path, emoji, text)`: shows `text` beside
  `icon_path` (the owner's file, falling back to `emoji` when the file has
  not landed — Rule #1, the SAME `icon_path()` graceful-absent contract
  every other UI-chrome consumer follows) positioned ABOVE `dial_widget`'s
  current on-screen geometry (`FAST_TRAVEL_FLASH_GAP_PX` clear of its top
  edge) — BELOW it instead when the dial hugs the screen's top edge (owner
  spec), read from the dial's own `screen().availableGeometry()`. Holds at
  full opacity for `FAST_TRAVEL_FLASH_DURATION_S − FAST_TRAVEL_FLASH_FADE_MS`,
  then fades to transparent over `FAST_TRAVEL_FLASH_FADE_MS` via a
  `QGraphicsOpacityEffect` + `QPropertyAnimation`, hiding itself when the
  fade finishes. A flash already in flight (rapid repeated Ctrl+[ presses)
  restarts cleanly: the running fade animation and hold timer both stop,
  opacity resets to 1.0, and the hold timer re-arms — so the LATEST press
  always wins with a fresh full-opacity display, never a half-faded stack.

## Design Decisions
- Built from scratch rather than adapting `LegendPopup` (Rule #5 considered):
  the two overlays differ in almost everything but the window-flag recipe —
  Legend Popup is content-driven (rich-text HTML, scrollable, sized by
  measuring), this one is a fixed tiny icon+label toast with its own
  fade-timer lifecycle. Duplicating the SHARED four-flag window recipe (a
  few lines) was judged cheaper than forcing two unrelated widgets to share
  one class.
- No `close()` call in `WatchController._teardown_windows()`: mirrors
  `LegendPopup`'s own precedent — neither is explicitly torn down there,
  both are plain top-level `QWidget`s Qt reclaims on process exit.
