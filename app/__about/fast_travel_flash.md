# Fast Travel Flash

**Script:** [Fast Travel Flash (script)](../fast_travel_flash.py) · **Flow:** [diagram](../__flow/fast_travel_flash.md)

## Purpose
The small transient overlay Fast Travel flashes above the dial on every
Ctrl+[ / Ctrl+] theme/option change (R5b FINAL MAP round): an icon plus
the active option's text, popping in at full opacity and fading out on
its own — the only feedback the theme/option pickers give, since they
carry no menu or dialog of their own.

R-30 (2026-08) reuses the SAME overlay, `flash(..., big=True)`, for a
LOCATION change: large "CITY, COUNTRY" text with no icon, centered
across the dial's own middle instead of the small popup above/below it
— one mechanism, two positions/sizes, never a second flash class.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `shortcuts.FAST_TRAVEL_FLASH_*`
  geometry/timing constants, `defaults.icon_path()` for the
  graceful-absent icon lookup
- [Native](native.md) — `assert_topmost`, the same trick [Legend
  Popup](legend_popup.md) uses

### Used by
- [Watch Controller](controller.md) — one instance per watch (per-watch:
  the focused watch flashes its own), triggered from
  `_cycle_fast_travel_theme()` / `_cycle_fast_travel_option()` (small,
  above/below) and, R-30, `_flash_location()` (big, centered) — called
  from `_apply_settings_dialog_result()` (a Settings preset pick),
  `_apply_jump()`/`_dialog_jump()` via `_flash_jump_location()` (Quick
  Jump cycling, Greenwich, the poles, Time Travel's own Quick Jump rows)

## Classes

### FastTravelFlash(QWidget)
Carries the same non-focus-stealing topmost window recipe as [Legend
Popup](legend_popup.md) (`Qt.WindowType.ToolTip | FramelessWindowHint |
WindowStaysOnTopHint`, `WA_ShowWithoutActivating`, `native.assert_topmost`
on every show) — necessary here because every Fast Travel shortcut needs
the dial to KEEP holding keyboard focus for the next press.

#### Methods
- `flash(dial_widget, icon_path, emoji, text, *, big=False)`: shows
  `text` beside `icon_path` (falling back to `emoji`, Rule #1 — hiding
  the icon label entirely when BOTH are empty/falsy) positioned above
  `dial_widget`'s current geometry (falling BELOW it when the dial
  hugs the screen's top edge), holds at full opacity for
  `FAST_TRAVEL_FLASH_DURATION_S − FAST_TRAVEL_FLASH_FADE_MS`, then
  fades via a `QGraphicsOpacityEffect` + `QPropertyAnimation`, hiding on
  finish. A flash already in flight restarts cleanly — the latest press
  always wins with a fresh full-opacity display. `big=True` (R-30)
  swaps `FAST_TRAVEL_FLASH_FONT_PX` for the larger
  `LOCATION_FLASH_FONT_PX` and `_position_above_or_below` for
  `_position_centered`.
- `_position_above_or_below(dial_widget)`: reads the dial's own
  `screen().availableGeometry()` to decide above/below and clamp
  horizontally
- `_position_centered(dial_widget)`: R-30 — dead center of the dial's
  own `frameGeometry()`.

## Design Decisions
- **Built from scratch rather than adapting `LegendPopup`** (Rule #5
  considered): the two overlays share only the window-flag recipe —
  Legend Popup is content-driven (rich-text, scrollable, sized by
  measuring), this one is a fixed tiny icon+label toast with its own
  fade-timer lifecycle. Duplicating the few shared lines was judged
  cheaper than forcing two unrelated widgets to share a base class.
- **No explicit teardown in `WatchController._teardown_windows()`** —
  mirrors [Legend Popup](legend_popup.md)'s own precedent: both are
  plain top-level `QWidget`s Qt reclaims on process exit.
