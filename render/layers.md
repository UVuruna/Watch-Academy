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
The gray brightness wheel (asset) rotated WITH the hexagram — the white
section centers on the star's top tip (true solar noon), black on solar
midnight — then transparent hue wedges at the same rotation, clipped to
`lit_regions()`: the shared per-regime (start, end, alpha) arcs of the
sunlit day (day alpha between sunrise and sunset, twilight alpha over the
dawn/dusk bands, nothing at night; robust to missing boundaries on
transitional polar days). The disc leaves an empty band before the ring.

### HexagramLayer (DAILY)
Procedural six-diamond star (tip radius + inner vertices at tip/√3):
colored BORDERS run the full circle so the night diamonds stay
recognizable; the FILLS (near-full opacity) are clipped to the same
`lit_regions()`. The star's top tip doubles as the solar-noon pointer —
the DOMY skin ships no separate noon marker (NoonMarkerLayer remains
available to other skins).

### RingLayer (STATIC)
The full ring image when the skin provides one (numerals, minutes and
letters baked into the art); otherwise the procedural donut with ticks,
numerals, letter substitutions and minute numbers.

### WeekdayLayer (DAILY)
"ghost": Sun center + six slots at `WEEKDAY_SLOT_ANGLES +
hexagram_rotation`, current day opaque, rest at `ghost_opacity`;
"center_only": only the current day's body, centered. Bodies draw a skin
image when provided, otherwise a colored disc; the white label is the
weekday SHORT name (MON/TUE/…), never the planet abbreviation.

### YearMarkerLayer (MINUTE)
Date markers along the INSIDE of the dial (owner spec). Modes: "earth"
(year wheel, day/night continent image clipped to a disc — the renders
ship on opaque space backgrounds), "moon" (rides its own cycle via
`moon_cycle_angle`: new at top, full at bottom, clockwise; the moon image
gets the unlit part shadowed by the terminator mask — half-disc ∪/−
ellipse with a = R·|cos 2πf| — and flips 180° for southern-hemisphere
cities), or "both" (Earth at orbit 0.74, Moon at 0.60).

### HandLayer (MINUTE)
Scales the hand image so tip-to-pivot = `length_fraction · radius`
(pivot_y of the image height), rotates about the pivot.
