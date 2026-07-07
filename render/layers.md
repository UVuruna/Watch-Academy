# Layers

**Script:** [Layers (script)](layers.py)

## Purpose
The seven dial layers, each tagged with a rebuild `Cadence`. Shared
helpers `dial_point()` and `draw_pie()` are the only places that convert
dial angles (clockwise from top) to Qt's counterclockwise-from-3-o'clock
system.

## Connections

### Uses
- [Angles](../core/angles.md) — sun-event → arc-angle mapping
- [Clock State](../core/clock_state.md), [Sun](../core/sun.md) — regime
  branches for the background bands
- [Assets](assets.md) — pixmap rasterization
- [Config (folder)](../config/___config.md) — weekday slot angles, dial constants

### Used by
- [Compositor](compositor.md)

## Classes

### Cadence / Layer / RenderContext
STATIC | DAILY | MINUTE; the ABC every layer implements; the frozen
per-paint context (skin, day, tick, radius, cache, dpr — `tick` is None
while compositing non-MINUTE layers).

### BackgroundLayer (DAILY)
Sector wheel + `_bands()`: per-regime (start, end, brightness) arcs —
NORMAL (twilight/night/twilight), WHITE_NIGHTS (no dark), TWILIGHT_ONLY
(band or all-day twilight), POLAR_DAY (no overlay), POLAR_NIGHT (all
dark).

### HexagramLayer / NoonMarkerLayer (DAILY)
Both rotate by `day.hexagram_rotation`; hexagram draws the skin asset (or
a procedural star outline), the marker a triangle in the ring band.

### RingLayer (STATIC)
Donut fill, 24 hour ticks, numerals with per-skin letter substitutions
(D-Ω-M-Y), minute numbers.

### WeekdayLayer (DAILY)
"ghost": Sun center + six slots at `WEEKDAY_SLOT_ANGLES +
hexagram_rotation`, current day opaque, rest at `ghost_opacity`;
"center_only": only the current day's body, centered. Bodies draw a skin
image when provided, otherwise a colored disc with a 3-letter label.

### YearMarkerLayer (MINUTE)
Earth variant chosen by `tick.is_daylight` (`<variant>_day` /
`<variant>_night`), procedural disc fallback; "moon_phase" mode draws the
terminator mask (half-disc ∪/− ellipse with a = R·|cos 2πf|).

### HandLayer (MINUTE)
Scales the hand image so tip-to-pivot = `length_fraction · radius`
(pivot_y of the image height), rotates about the pivot.
