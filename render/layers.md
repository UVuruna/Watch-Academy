# Layers

**Script:** [Layers (script)](layers.py)

## Purpose
The dial layers, each tagged with a rebuild `Cadence`. Shared helpers
`dial_point()` and `draw_pie()` are the only places that convert dial
angles (clockwise from top) to Qt's counterclockwise-from-3-o'clock
system. Pointer-variant helpers live here too: `pointer_palette()`
(skin palette when its length matches the arm count, else the reference
palette), `visible_occupant()` (shared-slot priority) and
`today_slot_theta()` (today's slot angle, None for the hexa center Sun).

## Connections

### Uses
- [Angles](../core/angles.md) — sun-event → arc-angle mapping
- [Clock State](../core/clock_state.md), [Sun](../core/sun.md) — regime
  branches for the background bands
- [Assets](assets.md) — pixmap rasterization
- [Config (folder)](../config/___config.md) — pointer slots, gray-wheel
  scales, dial constants

### Used by
- [Compositor](compositor.md)

## Pointer Variants
A skin renders with one of three pointer layouts (`SkinDefinition.pointer`,
user-overridable): **hexa** (6 arms, 60° each), **cross** (4 × 90°),
**octa** (8 × 45°). The arm count drives the star geometry, the period-hue
wedge count, the gray-wheel section count and the weekday slot layout
(`POINTER_WEEKDAY_SLOTS`). Shared slots (cross pairs two bodies on three
arms) show only the priority winner: the occupant whose weekday comes
NEXT from today — today itself always wins (`visible_occupant`).

## Classes

### Cadence / Layer / RenderContext
STATIC | DAILY | MINUTE; the ABC every layer implements; the frozen
per-paint context (skin, day, tick, radius, cache, dpr — `tick` is None
while compositing non-MINUTE layers).

### BackgroundLayer (DAILY)
The gray brightness wheel rotated WITH the star — the lightest section
pair straddles the top tip (true solar noon), the darkest the bottom —
then transparent hue wedges at the same rotation, clipped to
`lit_regions()`: the shared per-regime (start, end, alpha) arcs of the
sunlit day (day alpha between sunrise and sunset, twilight alpha over the
dawn/dusk bands, nothing at night; robust to missing boundaries on
transitional polar days). With no `base_asset` (the product default) the
wheel is drawn procedurally: 32 sections for every pointer — the
lightest and darkest are SINGLE sections centered on the top tip (true
solar noon) and the bottom (true midnight), the remaining 30 form 15
mirror-symmetric pairs. The 17 shades are spaced evenly between
`GRAY_WHEEL_SCALES[gray_contrast]` endpoints — "full" spans 0..255,
"soft" the gentler 60..195 window.

### HexagramLayer (DAILY)
Procedural N-diamond star (N = pointer arm count; inner vertices at
`tip / (2·cos(π/N))` — tip/√3 for the hexagram): colored BORDERS run the
full circle so the night diamonds stay recognizable; the FILLS
(near-full opacity) are clipped to the same `lit_regions()`. The star's
top tip doubles as the solar-noon pointer — the DOMY skin ships no
separate noon marker (NoonMarkerLayer remains available to other skins).

### RingLayer (STATIC)
The full ring image when the skin provides one (numerals, minutes and
letters baked into the art); otherwise the procedural donut with ticks,
numerals, letter substitutions and minute numbers.

### WeekdayLayer (DAILY)
"ghost": bodies on the pointer's slots at `slot angle +
hexagram_rotation`, current day opaque, rest at `ghost_opacity`; the
hexa layout additionally centers a ghost Sun (cross/octa seat the Sun on
an arm). "center_only": nothing here — the center pass draws it. Bodies
draw a skin image when provided, otherwise a colored disc; the white
label is the weekday SHORT name (MON/TUE/…) below 720 px, the full name
from 720 up.

### CenterBodyLayer (MINUTE)
The current day's CENTER image ABOVE the hands: the opaque Sun on
Sundays in ghost mode (hexa only), or today's body in center_only mode.
Slot images never move up here.

### TimeTextLayer (MINUTE)
Octa only: the bottom arm (`OCTA_TIME_SLOT_ANGLE + hexagram_rotation`)
carries the digital time instead of a body — always "12:24" (no
seconds, keeping the font big), fit-to-width so it never overflows the
slot, drawn ABOVE the hands like the center body (owner spec).

### YearMarkerLayer (MINUTE)
Date markers along the INSIDE of the dial (owner spec). Modes: "earth"
(year wheel, day/night continent image clipped to a disc — the renders
ship on opaque space backgrounds), "moon" (rides its own cycle via
`moon_cycle_angle`: new at top, full at bottom, clockwise; the moon image
gets the unlit part shadowed by the terminator mask — half-disc ∪/−
ellipse with a = R·|cos 2πf| — and flips 180° for southern-hemisphere
cities), or "both" (shared rim at orbit 0.75; the smaller Moon transits
OVER the Earth at `MOON_TRANSIT_OPACITY` when they meet).

### HandLayer (MINUTE)
Owner convention: every hand canvas is exactly its designed size and
rotates about a point `HAND_HUB_OFFSET_UNITS` (15) above the canvas
bottom. ALL hands share ONE scale — the longest hand's tip reaches
`HandsSpec.reach_fraction` of the dial radius and the others keep their
drawn proportions.
