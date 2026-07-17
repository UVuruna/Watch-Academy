# Layers

**Script:** [Layers (script)](layers.py)

## Purpose
The dial layers, each tagged with a rebuild `Cadence`. Shared helpers
`dial_point()` and `draw_pie()` are the only places that convert dial
angles (clockwise from top) to Qt's counterclockwise-from-3-o'clock
system. Pointer-variant helpers live here too: `palette_for()` (the
active Star+Aura palette preset — one source for the star diamonds AND
the background wedges), `visible_occupant()` (shared-slot priority),
`today_slot_theta()` (today's slot angle, None for the hexa center Sun),
`draw_event_glow()` (the season/moon event halo), the SLOT system:
`slot_layout()`, `slot_view()`, `weekday_classic_slot()` and the seat
geometry trio `slot_seat_rotation()` / `slot_seat_scale()` /
`slot_seat_orbit()` (see [The Slot System](#the-slot-system)) — and
the ARCHETYPE MODE helpers (see
[The Archetype Mode](#the-archetype-mode)).

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
- [Archetypes](../config/archetypes.md) — the archetype grid, figure
  tables and render tunables

### Used by
- [Compositor](compositor.md)

## Pointer Variants
A skin renders with one of six pointer layouts
(`SkinDefinition.pointer`, user-overridable): **trio** (Trinity, 3
hexa-shaped arms), **cross** (Seasons, 4 × 90°), **hexa** (Prism, 6 ×
60°), **octa** (Compass, 8 × 45°), **aurora** (no arms — day-hue wedges
only) and **calendar** (no arms — twelve calendar wedges). The arm
count drives the star geometry, the Aura wedge count and the weekday
slot layout (`POINTER_WEEKDAY_SLOTS`). Shared slots (cross pairs two
bodies on three arms) show only the priority winner: the occupant whose
weekday comes NEXT from today — today itself always wins
(`visible_occupant`). Each pointer draws with its palette preset
(`PALETTE_PRESETS[(pointer, palette_style)]`): hexa and octa ship
"paint" and "light" versions (subtractive vs additive primaries,
measured from the owner's art), the cross a single seasons palette
(summer yellow top, autumn red right, winter blue bottom, spring green
left).

<a id="the-calendar-pointer"></a>

### The Calendar Pointer (owner 2026-07-16)
The **Calendar** divides the 24h dial into TWELVE 2-hour wedges and,
like Aurora, draws NO star arms — the Aura carries the wedge colors
(`BackgroundLayer`; `StarLayer` skips it). The `palette_style` PICKS
THE WHEEL (`calendar_wheel()`): **paint = the Zodiac Dozen** (wedge
boundaries ON the cardinal axes, first hue = the wedge starting at the
12h line = Cancer, sign boundaries aligned with the year wheel) and
**light = the Almanac (Month) Dozen** (wedges CENTERED on the axes,
first hue = the wedge centered on the top = June). `calendar_wedge_bounds()`
returns the twelve `(start, end)` dial angles; the wedges are
CALENDAR-FIXED — they never ride the solar rotation.

One wedge LIGHTS by raising its opacity
(`CALENDAR_WEDGE_ALPHA` + `CALENDAR_WEDGE_LIT_DELTA`);
`calendar_lit_index()` chooses it from `SkinDefinition.calendar_lighting`:
**"hour"** — the wedge under the hour hand (the Chinese double-hour /
shichen: the noon Horse wedge, the midnight Rat…), **"year"** — the
current month's wedge (Almanac) or the current sign's (Zodiac). The lit
index rides `RenderContext.calendar_lit` (the compositor computes it
from the live tick and keys the DAILY composite on it, so the shichen
relights intraday even though the wedges live below the ring).

On the Almanac wheel ONLY the Earth marker leaves the shared six-anchor
season wheel for the Almanac's OWN real-calendar mapping
(`core.year_wheel.almanac_marker_angle`): every month spans 30° with
the 1st on its wedge-start line (one small ring tick ≈ one day). There
it gains the **day-ARROW** (`calendar_day_arrow()`,
`YearMarkerLayer._draw_earth`) — a small gold triangle at the marker's
exact tick pointing OUTWARD at the ring, so the ring reads today's date
to the day. The Moon marker keeps its own lunation orbit. The wedge
HOVER (`Compositor._calendar_tooltip`) is modest: the month + the
double-hour's animal (Almanac) or the sign + its dates (Zodiac).

<a id="the-archetype-mode"></a>

## The Archetype Mode

THE ARCHETYPE MODE (owner sealed package 2026-07-16; grid and figure
tables in [Archetypes](../config/archetypes.md)): with
`skin.archetype_mode` on and an armed pointer drawn, each diamond
carries its archetype's stained-glass FIGURE and the dial becomes an
ARCHETYPE CLOCK. The machinery:

- `archetype_key(skin)` / `archetype_active(skin)` — the active grid
  entry; None/False off the mode, on Aurora/Calendar (no archetype)
  and with the Pointer element off (no diamonds, no figures).
- **The one override gate:** `enabled_slots()` answers EMPTY while the
  mode is active, so the weekday model and ALL THREE SLOTS die
  together — rendering, hit-testing and layer building all read the
  slot chain through it — while the user's settings stay untouched
  (toggling back restores everything).
- `archetype_lit_index(pointer, hour_angle, rotation)` — the figure
  whose HOUR-SPACE holds the hour hand: the circle divides by arms
  (trio 3×8h, cross 4×6h, hexa 6×4h, octa 8×3h), every space CENTERED
  on its arm; the spaces ride the DRAWN (solar-rotated) arms. The
  compositor computes it from the live tick and keys the DAILY
  composite on it, like the Calendar's shichen wedge.
- `ArchetypeLayer` (DAILY, at the weekday_set z spot): the figures at
  the romb center (`weekday_body_orbit`), scaled into the diamond by
  `ARCHETYPE_FIGURE_HEIGHT_OF_TIP` and then CLAMPED to the romb for the
  art's own aspect (`archetype_fit_height`, owner slika 8 2026-07-17 —
  the glass never overflows its diamond) with the arm color visible
  around them; the lit figure FULL, the rest at the weekday
  `ghost_opacity`; the reveal window turns everything full. With Names
  on the lit figure carries its display name. Each figure is a per-arm
  HOVER-ENLARGE target (`"archetype:<index>"`, owner slika 8): the base
  pass skips the hovered figure and the HoverLift twin
  (`ArchetypeLayer(lift=True)`) redraws it enlarged above the hands —
  exactly like the slots.
- `ArchetypeCenterLayer` (MINUTE, above the hands like
  CenterBodyLayer): the center figure — the Eye / Hearth / Seal /
  Union / Throne, none on the Compass — full opacity, hover-enlarged
  as `"archetype:center"` (its lift twin joins HoverLiftLayer).
- `archetype_art_ready(path)` + `draw_archetype_figure()` — the
  graceful placeholder path: a missing file or a committed 1×1
  placeholder draws the figure's NAME in the outlined label style
  (fitted to the diamond width), never a stretched pixel.
- The Earth marker stays (it is the instrument, not a slot): its label
  is drawn by `_draw_earth_label`, where the DATE and the abbreviated
  WEEKDAY are MUTUALLY EXCLUSIVE (owner 2026-07-17, ROADMAP 15e — the two
  Design ▸ Earth switches). WEEKDAY alone (`skin.earth_weekday`) writes
  "FRI" centered (it must work without the date); DATE alone
  (`skin.show_earth_date`) writes "8 Jul" centered. Both are GENERAL Earth
  options working in normal AND archetype mode. During a DEEP travel
  (Session 16 — `day.deep_cycles != 0`) the DATE additionally carries the
  YEAR beneath it (`display_year` — the compact OFFICIAL form, "4500
  BCE"): far from the present the marker must say WHEN. The exclusivity is
  normalized at settings load, so the render never sees both on.

**Year texts (Session 16, owner amendment 2026-07-17):** the date
complication's year row and the Earth marker's deep-year row render
the compact OFFICIAL form via `display_year(ctx)` →
`core.deep_time.format_official` (the subdials cannot carry the full
paired line); the Anno Lucis pairing lives in the hover legends
([Compositor](compositor.md)).

<a id="the-slot-system"></a>

## The Slot System
Up to THREE user slots (owner matrix 2026-07-14), enabled strictly
1 → 2 → 3, each carrying one mode: weekday, digital time, two-row
date, day length, small seconds, zodiac, ascendant or Chinese zodiac.
`slot_layout(skin)` maps each enabled slot to its SEAT — `"classic"`
(the rotating weekday unit), `"center"`, or a dial angle:

- **one slot** — weekday drives the classic unit; any other mode sits
  at 24h on the Trinity, the center elsewhere;
- **two slots** — Trinity/Prism seat the pair on the 240°/120° arms;
  Seasons/Compass give whichever slot is weekday the classic unit and
  the other the center, or flank both at 225°/135° when neither is;
- **three slots** — top 0° + right + left; the Seasons lock the 1st
  slot on the classic unit (coerced in the controller);
- **pinned** (Aurora, Calendar, or the pointer off) — 180° alone, the
  225°/135° pair, the 0°/120°/240° trio; weekday shows today alone in a
  seat.

Seat geometry (owner 2026-07-15): `slot_seat_rotation()` lets seats
ride the star's solar rotation ONLY while an armed pointer is drawn —
Aurora, Calendar and pointer-off stay on natural round angles;
`slot_seat_scale()`
sizes slots per pointer (`SLOT_SIZE_BY_POINTER`: 125% on the slim-armed
Seasons/Compass, 150% elsewhere and pinned); `slot_seat_orbit()` shifts
ANGLE seats outward to the diamond's widest point on the slim-armed
pointers (`SLOT_SEAT_OUTWARD`). The CLASSIC weekday-by-colors unit
(drawn by `WeekdayLayer`, hit-tested in the compositor) inherits the
SAME geometry (owner 2026-07-15 — the three slots must behave
identically): its bodies carry `slot_seat_scale()` too, and ride the
ROMB CENTER via `weekday_body_orbit()` — half the star tip
(`WEEKDAY_ROMB_CENTER_OF_TIP`), which is the diamond's diagonal-cross
radius on EVERY pointer, so the by-colors slot centers in its romb
uniformly (the seated 2nd/3rd slots keep their own arm geometry).
`slot_view(skin, index)` resolves a
slot's (mode, astrology style, theme, metal, roster) — the roster is
per slot (owner 2026-07-15), so a seated weekday body first tries
`defaults.pantheon_seat` when its slot says "pantheon" and keeps the
planetary art when the seat's plate has not landed (the shared safety
law); `weekday_classic_slot()`
names the slot driving the classic unit (None when every slot is
seated).

**Subdials:** every flat slot face (text modes, flat astrology art)
sits on the watch-face plate drawn by `draw_slot_roundel()`: a LIVE
outward shadow first (`_draw_subdial_shadow` — offset away from the
dial center where the sun lives, symmetric on the center seat), then
the owner's plate art resolved by
[Assets](assets.md)`.subdial_plate_file()` (per letter finish and seat,
recolored from his one master when a finish has no art of its own);
with no plate art at all, a procedural circle in the ring's face color
rimmed with the finish metal. Two PLATE STYLES (owner A/B spec
2026-07-15, `skin.subdial_style`): "theme" colorizes the tapisserie
field to the clock tint, "black" keeps the standard dark AP field.
Every subdial accent wears the letter-FINISH metal (`_finish_color`):
the complication texts (`draw_shadowed_text` — finish color over a
drop shadow, never white) and the SMALL SECONDS mode
(`draw_small_seconds`): 4 larger NSEW ticks + 4 smaller between —
finish-colored on "theme", white on "black", shadowed either way —
plus the active set's hand in miniature, finish-tinted over its own
drop shadow; while seated it replaces the big seconds hand.

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
transitional polar days). With the Colorful element off the same lit
arcs are drawn in plain white (`COLORFUL_OFF_COLOR`) instead of the
palette hues — the day/twilight indication itself never disappears
(owner spec). With no `base_asset` (the product default) the
Umbra is drawn procedurally in the user's chosen form: **fine** (30
sections of 12°, 16 shades — the owner's measured art), **coarse** (24
sections, 13 shades) — both with single lightest/darkest sections
centered on the top tip (true solar noon) and the bottom (true
midnight), the rest in mirror pairs — or **gradient** (a continuous
per-pixel conical sweep, mirror-symmetric). Shade values come from
`umbra_ladder(shades, contrast)`: "full" runs endpoint-inclusive over
0..255 (16 → step 17); "half"/"light"/"dark" take the bin centers of
their half-windows — middle 64..192 (188..68), bright 128..255
(252..132), dark 0..127 (124..4), all exact step 8; the gradient
sweeps the same spans continuously. Under a ring tint every gray is
channel-multiplied by the hue (`tinted_gray`) — the Umbra follows the
clock body's recolor; the hands do the same through the asset cache.

### StarLayer (DAILY)
Procedural N-diamond star (N = pointer arm count; arm half-angles from
`POINTER_ARM_HALF_ANGLE_DEG`, inner vertices at `tip / (2·cos(half))` —
tip/√3 for the hexagram; the CROSS borrows the octa arm shape — "octa
without the diagonals", slim diamonds with gaps — and the TRIO is half
of hexa, three hexa-shaped arms with gaps): colored BORDERS run
the full circle so the night diamonds stay recognizable; the FILLS
(near-full opacity) are clipped to the same `lit_regions()`. The star's
top tip IS the solar-noon pointer.

### RingLayer (STATIC)
The full ring image when the skin provides one (numerals and minutes
baked into the art), channel-multiplied by the ring tint, with the
owner's gold/silver LETTER art overlaid by calculation
(`RING_LETTER_RADIUS_FRACTION` / `RING_LETTER_ART_SCALE`) so the tint
never touches the letters; otherwise the procedural donut with ticks,
numerals, letter substitutions and minute numbers (untinted fallback).

### WeekdayLayer (DAILY)
Draws only while a slot DRIVES the classic unit
(`weekday_classic_slot`). "ghost": bodies on the pointer's slots at
`slot angle + hexagram_rotation`, current day opaque, rest at
`ghost_opacity`; the hexa and trio layouts additionally center a ghost
Sun (cross/octa seat the Sun on an arm). "center_only": nothing here —
the center pass draws it. Bodies draw a skin image when provided,
otherwise a colored disc; the white label is the weekday SHORT name
(MON/TUE/…) below 720 px, the full name from 720 up.

### CenterBodyLayer (MINUTE)
The current day's CENTER image ABOVE the hands: the opaque Sun on
Sundays in ghost mode (hexa only), or today's body in center_only mode.
Slot images never move up here.

### SlotLayer (MINUTE)
One instance per placement pass draws every SEATED slot from
`slot_layout()` (the classic seat belongs to WeekdayLayer): angle
seats render BELOW the hands, the center seat in a `centered=True`
instance ABOVE them; a `lift=True` twin joins the hover-enlarge pass.
Each slot draws its mode via `_draw_slot`: the digital time "12:24",
the TWO-ROW date, the day length, the small seconds, a today-only
weekday body (`_draw_weekday_slot` — the 1st slot wears
`draw_weekday_body`, the 2nd/3rd their own theme art + metal), the
tropical zodiac (text, or the owner's sign / logo / constellation
PNG), the ascendant or the Chinese zodiac. Flat faces sit on the
subdial plate (see [The Slot System](#the-slot-system)); text is
fit-to-width. Position, size and orbit come from the seat geometry
trio, so the compositor hit-test shares the exact same numbers.

### YearMarkerLayer (MINUTE)
Date markers along the INSIDE of the dial (owner spec), each behind its
Elements switch: the Earth (`show_earth`: year wheel, day/night
continent image clipped to a disc — the renders ship on opaque space
backgrounds) and the Moon (`show_moon`: rides its own cycle via
`moon_cycle_angle`, new at top, full at bottom, clockwise; the moon image
gets the unlit part shadowed by the terminator mask — half-disc ∪/−
ellipse with a = R·|cos 2πf| — and flips 180° for southern-hemisphere
cities). With both markers on they share the rim at orbit 0.75 and the
smaller Moon transits OVER the Earth at `MOON_TRANSIT_OPACITY` when they
meet. The Earth draws the user's `earth_style` variant (clean or
atmosphere — both bundled per continent and day/night). During event windows
(`tick.season_event` ±12 h around a solstice/equinox, `tick.moon_event`
±6 h around a principal phase) the glowing marker RELOCATES radially
to the RING BAND CENTERLINE (owner rework 2026-07-16,
`defaults.GLOW_RING_RADIUS_FRACTION` = the numeral/letter radius),
keeping its own angle (the Moon still glows at its cycle reading), so a
compact halo via `draw_event_glow()` STRADDLES the ring — shining both
inside and outside the circle and reading over any background instead of
having to be huge. The colors carry the source: the Sun's events glow
GOLDEN (`GLOW_SUN_COLOR`), the Moon's phases SILVER (`GLOW_MOON_COLOR`);
the halo diameter stays 2× the marker's. Because the glow sits at the
ring band and can be hover-enlarged, its extent (owner 2026-07-16 bug:
a bottom-of-ring halo was square-cut at the window edge) is folded into
the transparent window margin — `defaults.dial_window_margin_fraction(skin)`
computes it LIVE from the user's settings (owner slike 1–3, 2026-07-17):
the LARGER of the Earth/Moon markers (each carrying its earth/moon scale)
relocated to `GLOW_RING_RADIUS_FRACTION`, × `GLOW_RADIUS_SCALE` × the
user's `hover_enlarge`, against the ring-letter overhang at the
letter-scale slider — so the halo can never clip and any size/hover/
letter slider re-sizes the window to fit exactly (no waste). The MARGIN
GAP fix (owner slika 4, ROADMAP 15e): the only over-reservation was the
anti-aliasing epsilon (`DIAL_WINDOW_MARGIN_EPSILON`, tightened 0.01 → 0.003
of the diameter — the old value left a fixed ~7 px gap at a 720 dial); the
`max(earth, moon)`, the glow-halo × hover product and the ring-letter floor
are each an exact bound, not waste (both markers glow at the ring band,
hover and glow do stack, and the letters genuinely overhang). At
max-everything the hovered glowing marker now lands within ~1–2 px of the
edge and never clips (pinned both ways by the margin tests).

### HandLayer (MINUTE)
Owner convention: every hand canvas is exactly its designed size and
rotates about a point `HAND_HUB_OFFSET_UNITS` (15) above the canvas
bottom. ALL hands share ONE scale — the longest hand's tip reaches
`HandsSpec.reach_fraction` of the dial radius and the others keep their
drawn proportions.
