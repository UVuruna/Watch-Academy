# Fast Travel Flash

**Script:** [Fast Travel Flash (script)](../fast_travel_flash.py) · **Flow:** [diagram](../__flow/fast_travel_flash.md)

## Purpose
The small transient overlay Fast Travel flashes above the dial on every
Ctrl+[ / Ctrl+] theme/option change (R5b FINAL MAP round): an icon plus
the active option's text, popping in at full opacity and fading out on
its own — the only feedback the theme/option pickers give, since they
carry no menu or dialog of their own.

R-30 (2026-08) reuses the SAME overlay for a LOCATION change, and the
owner's order of 2026-08-12 finished that merge. A location used to be a
different-looking flash — large white FONT letters with no icon, centered
across the dial's own middle. His correction: it belongs ABOVE, where the
Ctrl+[ switcher already stands, in the theme's letter plates, with its own
logo beside it. So there is ONE mechanism, ONE position, ONE look now:
`big`, `_position_centered` and `LOCATION_FLASH_FONT_PX` are all retired.

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
  `_cycle_fast_travel_theme()` / `_cycle_fast_travel_option()` and
  `_flash_location()` — called from `_apply_settings_dialog_result()` (a
  Settings preset pick), `_apply_jump()`/`_dialog_jump()` via
  `_flash_jump_location()` (Quick Jump cycling, Greenwich, the poles,
  Time Travel's own Quick Jump rows) and `_end_simulation()` (Ctrl+Home's
  return home, owner order 2026-08-12 — the one path that used to be
  silent). The location's own logo comes from
  `WatchController._LOCATION_FLASH_ICONS`: his two compass roses for the
  poles, the plain one for Greenwich, none for an ordinary city

## Classes

### FastTravelFlash(QWidget)
Carries the same non-focus-stealing topmost window recipe as [Legend
Popup](legend_popup.md) (`Qt.WindowType.ToolTip | FramelessWindowHint |
WindowStaysOnTopHint`, `WA_ShowWithoutActivating`, `native.assert_topmost`
on every show) — necessary here because every Fast Travel shortcut needs
the dial to KEEP holding keyboard focus for the next press.

#### Methods
- `flash(dial_widget, icon_path, emoji, text)`: shows
  `text` beside `icon_path` (falling back to `emoji`, Rule #1 — hiding
  the icon label entirely when BOTH are empty/falsy) positioned above
  `dial_widget`'s current geometry (falling BELOW it when the dial
  hugs the screen's top edge), holds at full opacity for
  `FAST_TRAVEL_FLASH_DURATION_S − FAST_TRAVEL_FLASH_FADE_MS`, then
  fades via a `QGraphicsOpacityEffect` + `QPropertyAnimation`, hiding on
  finish. A flash already in flight restarts cleanly — the latest press
  always wins with a fresh full-opacity display.
- `_icon_pixmap(icon_path)`: the icon at a LOGICAL size of exactly
  `FAST_TRAVEL_FLASH_ICON_PX`, whatever the source and whatever the
  screen's scaling — see [One size, one place](#one-size-one-place)
  below. Still rasterized at `FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE` times
  the target and smoothly scaled down: asked for 28 px directly, Qt
  renders a vector's fine detail below one pixel and the glyph collapses
  (owner report 2026-08-12). The COMPUTED glyphs are drawn that big to
  begin with, so both kinds of source arrive oversized and leave the same
  way.
- `_set_plate_text(text)`: the two-metal plate run, splitting on either
  separator — the picker's " : " or a location's "CITY, COUNTRY". Only the
  picker DRAWS its separator (the colon plate); a comma has no plate and
  needs none, the metal change being the seam.
- `_position_above_or_below(dial_widget)`: reads the dial's own
  `screen().availableGeometry()` to decide above/below and clamp
  horizontally

## The plate text (owner correction 2026-08-11)

EVERY flash's text is rendered by `render.letter_plates.
plate_text_segments_pixmap` — the SAME gold/silver letter plates the
jewels and the crown text wear — never a white font (invisible over a
white desktop). The controller composes "CATEGORY : OPTION" over the colon
plate because the plate library owns no parenthesis.

THE LORD'S DAY PRECEDENT: a glyph with no plate does not kill a keystroke
here. The picker's titles are plate-safe by construction, but a location
carries whatever the world calls itself and the library owns no accented
masters today — so a `MissingPlate` falls back to the styled font FOR THAT
ONE TEXT and names the offending character on stderr, exactly as the
weekday labels do for the apostrophe. Loud and per-string, never a silent
standing font path.

<a id="one-size-one-place"></a>

## One size, one place (owner drift report 2026-08-13)

His report: cycling the category with Ctrl+[, the flash "seems to shift
slightly and to change size" — not always the same distance from the dial
circle, not always the same size.

**Measured before it was believed.** On his 125 % display the flash box
stood **48 px tall for Solar Eclipse / Date / Time and 42 px for Lunar
Eclipse / Sun Turning Points / Moon Stations**, and because
`_position_above_or_below` anchors the box by its BOTTOM edge
(`dial.top() − height − gap`), the whole label — text included — jumped
**3 px** between categories while the icon itself was a quarter smaller
in one family than the other.

**The mechanism** was `QIcon.pixmap()`'s DPI awareness meeting
`QPixmap.scaled()`'s DEVICE pixels. A source that can supply any size —
the SVGs, a raster larger than the request — hands back `n × dpr` device
pixels *already carrying* `devicePixelRatio = dpr`; the two COMPUTED
icons exist at exactly `SUPERSAMPLE × ICON_PX` px, so QIcon can only
return that many, at a dpr of 1. `scaled(28, 28)` then meant 28 DEVICE
pixels for both and PRESERVED each source's own dpr, so one call
produced 22.4 logical px for one family and 28.0 for the other. At
100 % scaling the two agree exactly — which is why it shipped.

Not the suspects it looked like: the letter plates are all 512 px tall
with their ink filling 508 of them, so every glyph shares a cap height
and the text run measured a constant 15.2 logical px in every category
before and after. The size was never fitted to the string.

**The fix** decides the size HERE, in device pixels the widget computes
from its own `devicePixelRatioF()`, and stamps that ratio on the result;
the aspect-preserved image is then centred on a SQUARE canvas, so the
label's box is `ICON_PX` even for art that is not square. Position
follows the declared metric, never the ink. After it, all six categories
measure an identical box top, identical icon size and identical text
height (spread 0.0 on every axis).

**Tooth:** `tests/test_fast_travel_flash.py`, which measures in a
SUBPROCESS under `QT_SCALE_FACTOR=1.25` — a scale factor is read once
when the QApplication is built, and the defect is invisible at 100 %.

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
