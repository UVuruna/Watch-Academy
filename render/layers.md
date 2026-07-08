# Layers

**Script:** [Layers (script)](layers.py)

## Purpose
The dial layers, each tagged with a rebuild `Cadence`. Shared helpers
`dial_point()` and `draw_pie()` are the only places that convert dial
angles (clockwise from top) to Qt's counterclockwise-from-3-o'clock
system. Pointer-variant helpers live here too: `palette_for()` (the
active Star+Aura palette preset — one source for the star diamonds AND
the background wedges), `visible_occupant()` (shared-slot priority),
`today_slot_theta()` (today's slot angle, None for the hexa center Sun)
and `draw_event_glow()` (the season/moon event halo).

The three named dial elements (owner naming): the **Star** (the
pointer), the **Aura** (colored period wedges) and the **Umbra** (gray
brightness wheel). `RenderContext.rotation` carries their shared
rotation: the solar-noon offset, or 0 when the user turns solar
rotation off (upright mode — better for reading exact positions).

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
**octa** (8 × 45°). The arm count drives the star geometry, the Aura
wedge count and the weekday slot layout (`POINTER_WEEKDAY_SLOTS`).
Shared slots (cross pairs two bodies on three arms) show only the
priority winner: the occupant whose weekday comes NEXT from today —
today itself always wins (`visible_occupant`). Each pointer draws with
its palette preset (`PALETTE_PRESETS[(pointer, palette_style)]`): hexa
and octa ship "paint" and "light" versions (subtractive vs additive
primaries, measured from the owner's art), the cross a single seasons
palette (summer yellow top, autumn red right, winter blue bottom,
spring green left).

## Classes

### Cadence / Layer / RenderContext
STATIC | DAILY | MINUTE; the ABC every layer implements; the frozen
per-paint context (skin, day, tick, radius, cache, dpr — `tick` is None
while compositing non-MINUTE layers).

### BackgroundLayer (DAILY)
The UMBRA (gray brightness wheel) rotated with the star, then the AURA
(transparent hue wedges) at the same rotation, clipped to
`lit_regions()`: the shared per-regime (start, end, alpha) arcs of the
sunlit day (day alpha between sunrise and sunset, twilight alpha over the
dawn/dusk bands, nothing at night; robust to missing boundaries on
transitional polar days). With no `base_asset` (the product default) the
Umbra is drawn procedurally, matching the owner's measured art: 30
sections of 12° — the lightest and darkest are SINGLE sections centered
on the top tip (true solar noon) and the bottom (true midnight), the
remaining 28 form 14 mirror-symmetric pairs. The 16 shades follow
`UMBRA_SCALES[umbra_contrast]` — "full" 255..0 step 17, "soft" the
middle half of the scale (188..68 step 8, symmetric about 128).

### StarLayer (DAILY)
Procedural N-diamond star (N = pointer arm count; arm half-angles from
`POINTER_ARM_HALF_ANGLE_DEG`, inner vertices at `tip / (2·cos(half))` —
tip/√3 for the hexagram; the CROSS borrows the octa arm shape — "octa
without the diagonals", slim diamonds with gaps): colored BORDERS run
the full circle so the night diamonds stay recognizable; the FILLS
(near-full opacity) are clipped to the same `lit_regions()`. The star's
top tip doubles as the solar-noon pointer — the DOMY skin ships no
separate noon marker (NoonMarkerLayer remains available to other skins,
and stays SOLAR even in upright mode).

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

### BottomSlotLayer (MINUTE)
Octa only: the bottom arm (`OCTA_TIME_SLOT_ANGLE + rotation`) carries
user-selected info instead of a body — the digital time "12:24" (no
seconds, keeping the font big), the date "8 Jul", the day length
"15:25" or the zodiac sign name. Fit-to-width so it never overflows the
slot, drawn ABOVE the hands like the center body (owner spec). In
zodiac mode the slot hover shows the sign's date span.

### YearMarkerLayer (MINUTE)
Date markers along the INSIDE of the dial (owner spec). Modes: "earth"
(year wheel, day/night continent image clipped to a disc — the renders
ship on opaque space backgrounds), "moon" (rides its own cycle via
`moon_cycle_angle`: new at top, full at bottom, clockwise; the moon image
gets the unlit part shadowed by the terminator mask — half-disc ∪/−
ellipse with a = R·|cos 2πf| — and flips 180° for southern-hemisphere
cities), or "both" (shared rim at orbit 0.75; the smaller Moon transits
OVER the Earth at `MOON_TRANSIT_OPACITY` when they meet). During event
windows (`tick.season_event` ±12 h around a solstice/equinox,
`tick.moon_event` ±6 h around a principal phase) the marker gets a soft
radial halo via `draw_event_glow()`.

### HandLayer (MINUTE)
Owner convention: every hand canvas is exactly its designed size and
rotates about a point `HAND_HUB_OFFSET_UNITS` (15) above the canvas
bottom. ALL hands share ONE scale — the longest hand's tip reaches
`HandsSpec.reach_fraction` of the dial radius and the others keep their
drawn proportions.
