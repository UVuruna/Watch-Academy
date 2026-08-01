# Fast Travel Flash

**Script:** [Fast Travel Flash (script)](../fast_travel_flash.py) · **Flow:** [diagram](../__flow/fast_travel_flash.md)

## Purpose
The small transient overlay Fast Travel flashes above the dial on every
Ctrl+[ / Ctrl+] theme/option change (R5b FINAL MAP round): an icon plus
the active option's text, popping in at full opacity and fading out on
its own — the only feedback the theme/option pickers give, since they
carry no menu or dialog of their own.

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
  `_cycle_fast_travel_theme()` / `_cycle_fast_travel_option()`

## Classes

### FastTravelFlash(QWidget)
Carries the same non-focus-stealing topmost window recipe as [Legend
Popup](legend_popup.md) (`Qt.WindowType.ToolTip | FramelessWindowHint |
WindowStaysOnTopHint`, `WA_ShowWithoutActivating`, `native.assert_topmost`
on every show) — necessary here because every Fast Travel shortcut needs
the dial to KEEP holding keyboard focus for the next press.

#### Methods
- `flash(dial_widget, icon_path, emoji, text)`: shows `text` beside
  `icon_path` (falling back to `emoji` when the file has not landed —
  Rule #1) positioned above `dial_widget`'s current geometry (falling
  BELOW it when the dial hugs the screen's top edge), holds at full
  opacity for `FAST_TRAVEL_FLASH_DURATION_S − FAST_TRAVEL_FLASH_FADE_MS`,
  then fades via a `QGraphicsOpacityEffect` + `QPropertyAnimation`,
  hiding on finish. A flash already in flight restarts cleanly — the
  latest press always wins with a fresh full-opacity display.
- `_position_above_or_below(dial_widget)`: reads the dial's own
  `screen().availableGeometry()` to decide above/below and clamp
  horizontally

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
