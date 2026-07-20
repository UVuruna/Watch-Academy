# Layers

**Script:** [Layers (script)](layers.py)

## Purpose
The dial layers, each tagged with a rebuild `Cadence`. Shared helpers
`dial_point()` and `draw_pie()` are the only places that convert dial
angles (clockwise from top) to Qt's counterclockwise-from-3-o'clock
system. Pointer-variant helpers live here too: `palette_for()` (the
active Star+Aura BASE palette preset — one source for both the star
diamonds AND, through `aura_palette_for()`, the background wedges) and
`aura_palette_for()` (fix round E, owner verdict 2026-07-19, slika 2 —
RE-SCOPED from `palette_for` itself: `skin.pointer_saturation`, the
slider now labeled "Aura" in Settings ▸ Colors, scales ONLY the Aura
wedges here — `StarLayer` reads `palette_for` directly and stays
perfectly raw regardless of the slider; the storage key is unchanged,
only the scope and the label moved. RING has its OWN independent
Saturation slider, `ring_saturation`, applied at `RingLayer` instead —
see its note below), `visible_occupant()` (shared-slot priority),
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
- [Angles](../core/angles.md) — sun-event → arc-angle mapping;
  `ring_position_angle`/`readable_rotation_deg` for the ring's own
  letters AND the outer motto arc
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
- **THE TWO-TYPE LAW** (owner decree 2026-07-18, round two —
  screenshots; height law FIXED round A 2026-07-19 — screenshots showed
  lancets overflowing their diamonds and the Trinity center huge):
  `archetype_figure_size(skin, radius, art_file)` is the ONE sizing
  entry for every archetype figure, arms AND center — classified by the
  art's OWN aspect ratio (width/height), no per-art clamp, no
  set-minimum (the 15g clamp era — `archetype_set_height()` /
  `archetype_figure_height()` / `archetype_fit_height()` — is deleted
  whole; `ARCHETYPE_FIGURE_HEIGHT_OF_TIP` is ALSO gone now — round A
  replaced the free per-pointer fraction with the inscribed-height law
  below). Two types:
  - **CIRCLE** (aspect ≥ `ARCHETYPE_PORTRAIT_ASPECT_MAX` = 0.70 —
    rondels, medallions, the square Scale glass, and WIDE art like
    Saturn's rings, and any missing/placeholder art) wears
    `weekday_body_size(skin, radius)` — THE SLOT SIZE, IDENTICAL to
    the weekday bodies. Wide art stays height-based ON PURPOSE (owner:
    "planeta istih dimenzija kao ostale, prstenovi vire" — the ball
    matches every other circle, the rings overflow the frame,
    deliberately — no clamp, no defensive code). Round A tightened the
    threshold 0.85 → 0.70 (measured lancet cluster 0.37–0.58, rondel
    cluster 0.99–1.03) after the ChatGPT-set Providence_Eye center
    (aspect 0.842) wrongly fell PORTRAIT-side under 0.85 and drew at
    the tall lancet height — the "Trinity ogroman centar" bug.
  - **PORTRAIT** (aspect < the threshold — the tall lancet vitraž
    windows: persons, temperaments) wears `archetype_portrait_height
    (tip, tan_half)` — the INSCRIBED height for the STANDARD aspect
    (`ARCHETYPE_PORTRAIT_STANDARD_ASPECT` = 0.5, i.e. 1:2), not the
    art's own aspect: the old `archetype_fit_height` formula
    (`tip·tan_half / (aspect + tan_half)`) reintroduced as a small
    helper and evaluated at the STANDARD aspect instead of per-art, so
    every portrait is UNIFORM and a 1:2 lancet inscribes its diamond
    EXACTLY. Art wider than 0.5 may still overflow sideways until the
    owner reforces it to the standard — transitional, documented, not
    clamped.
- `ArchetypeLayer` (DAILY but HOVER-VARIABLE — painted LIVE, never in
  the cached composite, owner 2026-07-17 ROADMAP 15f; at the weekday_set
  z spot): the figures at the romb center (`weekday_body_orbit`), EACH
  sized by its OWN art via `archetype_figure_size` (a layout can mix
  circle and portrait figures — e.g. Prism paint's reused Scale glass
  next to the Person lancets) with the arm color visible around them;
  the lit figure FULL, the rest at the weekday `ghost_opacity`; the
  reveal window turns everything full. With `skin.archetype_names` on
  (owner 2026-07-18, Session 21-C — its OWN Settings switch, separate
  from the weekday bodies' `show_weekday_names`) the lit figure carries
  its display name. Each figure is a per-arm HOVER-ENLARGE
  target (`"archetype:<index>"`, owner slika 8): the base pass skips
  the hovered figure and the HoverLift twin (`ArchetypeLayer(lift=True)`)
  redraws it enlarged above the hands — exactly like the slots.
- `ArchetypeCenterLayer` (MINUTE, above the hands like
  CenterBodyLayer): the center figure — the Eye / Hearth / Seal /
  Union / Throne, none on the Compass — hover-enlarged as
  `"archetype:center"` (its lift twin joins HoverLiftLayer). It follows
  its OWN art's type via `archetype_figure_size` — no longer the
  weekday Sun's `center_scale`, which sized it larger, nor a per-art
  clamp of its own — and reveal can no longer resize it; the
  `_element_at` hit disc matches (halved to a radius, the center's own
  art type). THE CENTER WINDOW (owner seal 2026-07-18): it burns FULL
  only while the hour
  hand stands within `ARCHETYPE_CENTER_WINDOW_DEG` (15°, ±1h) of TRUE
  solar noon OR solar midnight (`archetype_center_lit()`) — 4 of the
  24 hours, ~16.7% of the day — and draws at the weekday
  `ghost_opacity` the rest of the time, exactly like an un-lit arm
  figure; `noon_angle` is `day.star_rotation` (the hexagram's top
  vertex, the SOLAR noon angle — correct in both upright and rotating
  modes, never the drawn rotation). The reveal window ("show me
  everything") still forces it full regardless, short-circuiting
  before the window check ever reads `ctx.tick`.
- `archetype_art_ready(path)` + `draw_archetype_figure()` — the
  graceful placeholder path: a missing file or a committed 1×1
  placeholder draws the figure's NAME in the outlined label style
  (fitted to the diamond width), never a stretched pixel — through the
  shared `draw_name_label()` below.
- **`draw_name_label()`** (owner ROADMAP 15h item 4, reworked 2026-07-18
  Session 21-C — owner verdict) — the ONE on-dial NAME-label draw
  shared by the weekday bodies (`draw_body_label`, the diamond slots'
  and the info slot's body text) AND the archetype figures
  (`draw_archetype_figure`'s named/fallback path, `ArchetypeCenterLayer`'s
  placeholder path). `draw_name_label` itself is now DUMB: it draws
  `name` as ONE outlined line at the `label_px` the CALLER supplies —
  no measuring, no wrapping inside the draw call. THE TWO-LINE WRAP
  (item 4c, `_wrap_name_lines`) IS REVOKED (owner slika: the Compass
  Ages dial showed "Youth" huge beside a tiny "Childhood" — ugly) —
  `_wrap_name_lines` and its tests are gone whole (Rule #6, no
  leftovers); every name is one line again.
  THE SET-UNIFORM LAW (owner verdict 2026-07-18, replaces the per-label
  fit): every name sharing a RING — the archetype layout's figures
  (arms AND the center, kept in the SAME set on purpose for uniformity)
  and the weekday bodies of a dial (the diamond slots and the hexa/trio
  ghost/opaque center Sun, whichever draws) — wears the size of the
  SMALLEST fitted member. `name_label_px(name, target_width)` is the
  per-name fit (the largest bold pixel size whose width spans
  `target_width`, capped at `defaults.NAME_LABEL_MAX_PX`, floored at
  `BODY_LABEL_MIN_PX` — a flat pixel ceiling, deliberately dial-size-
  independent, reasoned from the 720-dial short-weekday "TUE" look);
  `weekday_label_set_px(ctx)` and `archetype_label_set_px(ctx, key,
  arm_width)` compute the SET's answer ONCE per paint (not per label) —
  each is a PURE, cheap (text measurement only) function, so two
  separate paint passes that share one ring (`WeekdayLayer`/
  `CenterBodyLayer`; `ArchetypeLayer`/`ArchetypeCenterLayer`) recompute
  the identical set and agree on one size without any shared mutable
  state. The hover-enlarged twin scales that same base size (multiplies
  the SET answer by its own `hover_factor`, never recomputes the set).
  The old per-path constants (`ARCHETYPE_NAME_WIDTH_FRACTION`,
  `ARCHETYPE_NAME_MAX_OF_FIGURE`, `BODY_LABEL_SIZE`,
  `NAME_LABEL_LINE_OFFSET_FRACTION`) are gone — `defaults.
  NAME_LABEL_WIDTH_FRACTION` is the one shared width fraction,
  `defaults.NAME_LABEL_MAX_PX` the one shared cap.
- The Earth marker stays (it is the instrument, not a slot): its label
  is drawn by `_draw_earth_label`, reading the single `skin.earth_label`
  enum (owner 2026-07-18, ROADMAP 15h — replaces the old
  `show_earth_date`/`earth_weekday` bool pair, Rule #6, deleted
  everywhere) — FOUR EXCLUSIVE modes, the Design ▸ Earth submenu:
  "off" draws nothing; "weekday" writes "FRI" centered (it must work
  without the date); "date" writes "8 Jul" centered; "date_weekday"
  stacks the date over the abbreviated weekday (the OLD combined "Full
  Date" meaning, renamed now that a true Full Date exists); "full"
  stacks the date over the YEAR (`display_year` — the compact OFFICIAL
  form, "4500 BCE" — the exact two-row shape the deep-travel year
  complication already uses). All four work in normal AND archetype
  mode. During a DEEP travel (Session 16 — `day.deep_cycles != 0`) the
  YEAR row OUTRANKS the weekday in "date_weekday" mode — far from the
  present the marker must say WHEN; in "full" mode a deep travel is a
  no-op difference, since the year row is already showing (`display_year`
  un-shifts the deep proxy frame regardless of mode).

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
dial center where the sun lives, keyed off THIS seat's own dial
position, symmetric on the center seat), then the owner's ONE master
plate resolved by [Assets](assets.md)`.subdial_plate_file()` (Rule #19,
owner decree 2026-07-20 — the old twelve-plate seat×finish sheet is
retired; the seat never reaches the file, only the shadow above;
recolored live to any letter finish that isn't the master's own); with
no plate art at all, a procedural circle in the ring's face color
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
STATIC | DAILY | MINUTE; the ABC every layer implements, plus the
`Layer.hover_variable` flag (default False; True on WeekdayLayer and
ArchetypeLayer — a DAILY layer whose APPEARANCE changes with hover/reveal,
so the compositor draws it LIVE and never bakes it into the cached
composite, owner 2026-07-17 ROADMAP 15f); the frozen per-paint context
(skin, day, tick, radius, cache, dpr — `tick` is None while compositing
non-MINUTE layers).

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
owner's gold LETTER art overlaid by calculation
(`RING_LETTER_RADIUS_FRACTION` / `RING_LETTER_ART_SCALE`) so the tint
never touches the letters; otherwise the procedural donut with ticks,
numerals, letter substitutions and minute numbers (untinted fallback).
`RingSpec.letter_art` holds the GOLD master per hour; `RingSpec.
letter_metal` the active finish ("gold"/"silver"/"bronze") — silver and
bronze are no longer pre-rendered files (owner decree 2026-07-19:
"bolje crtati na licu mesta nego 15MB fajlova", retiring
setup/make_silver_letters.py / make_bronze_letters.py and their ~15 MB
of `<Stem>_silver.png`/`<Stem>_bronze.png`) — `_draw_letter_art`
resolves the finish through `render.assets.letter_metal_file(gold_asset,
metal)` at paint time, disk-cached like every other derived asset; the
shadow silhouette always reads the gold file directly (the alpha mask
is identical on every finish).

**RING SATURATION (owner 2026-07-18, Session 21-D — its own Settings ▸
Colors slider, independent of Pointer Saturation):** `skin.ring_saturation`
scales `AssetCache._saturated`'s HSV desaturation on the ring PLATE
pixmap, applied AFTER the tint recolor (`draw_pixmap_centered(...,
tint=ring_tint, saturation=ring_saturation)` — saturating the PRE-tint
source would be a no-op, since the master plate art is grayscale), and
on the letter overlay's own pixmap (`_draw_letter_art`, saturation
only — the letters are explicitly UNTINTED by `ring_tint`, but the
owner's ask groups plate + letters as one "ring band" saturation
target, so both take the slider; the letter SHADOW copy is skipped —
a pure black silhouette has none to scale).

**GROUND-TRUTHED SCOPE (owner explicitly asked "what does the ring path
actually cover"):** `ring_tint` itself reaches FAR beyond the ring —
it also recolors the HANDS (`HandLayer.paint`, "the hands follow the
clock tint... one hue recolors the whole body") and the UMBRA
(`BackgroundLayer._draw_umbra`, "the Umbra follows the ring hue") and,
under the "theme" plate style, the SUBDIAL plate
(`draw_slot_roundel`/`subdial_plate_file`). `ring_saturation` is
DELIBERATELY narrower: it touches ONLY the ring band's own art (the
plate + its letters) — the hands, Umbra and subdial plate are
untouched by this slider even though they share `ring_tint`.

**THE OUTER MOTTO ARC (MOTO-FIX round, owner correction 2026-07-19, the
dollar's Great Seal reference image — the first round's layout was
"katastrofa", both mottos sweeping the same overlapping top-heavy
arc):** while the active preset carries a `motto`
(`data.rings.validate_preset`, Mason today), `_draw_motto` draws the
two Great Seal mottos as curved text just OUTSIDE the ring band,
EXACTLY like the real seal: ANNUIT COEPTIS arcs over the TOP (its own A
pinned at 8h, S at 16h, reading CLOCKWISE the short way through noon —
no motto letter pins noon anymore, the arc simply passes over the G)
and NOVUS ORDO SECLORUM arcs under the BOTTOM (its own N pinned at 4h,
ORDO's own final O at the bottom/24h, M at 20h, reading
COUNTERCLOCKWISE — `core.motto.motto_glyph_angles`'s new `clockwise`
flag, False for this one — left to right THROUGH the bottom, the
classic coin lower-banner direction). The two arcs are now angularly
DISJOINT (top 300-360-60 deg, bottom 120-180-240 deg, each a 120 deg
span) — "MASON outside, G inside" reads ONCE around the outside now,
not twice. The per-glyph angles are pre-solved at LOAD time by
[Motto](../core/motto.md)'s `motto_glyph_angles` (never recomputed at
paint time); `RingLayer` only draws. The stamp itself — metal finish,
dark halo, tangential rotation that flips 180° through the lower half
(`core.angles.readable_rotation_deg`) — is the SHARED `_draw_ring_glyph`
helper (Rule #5): `_draw_letter_art` (the ring's own six letters) and
`_draw_motto` both call it, differing only in asset, radius and
height. NEITHER the rotation formula nor `_draw_ring_glyph` itself
changed for this round — `readable_rotation_deg` already derives "tops
outward" (top half) or "tops inward" (bottom half, the classic coin
orientation) from the angle alone, so feeding it the new bottom arc's
decreasing angles draws every glyph upright automatically; the
MOTO-FIX round only corrected the ANGLE math (`core.motto`) and the pin
config (`Database/ring_presets.json`). The motto reuses the EXACT SAME
PNG library the ring's own letters draw from
(`constants.RING_LETTER_FILES` — zero new art) at a smaller size
(`RING_MOTTO_SIZE`, half `RING_LETTER_ART_SCALE`) and wears ONE finish
for the whole inscription (`RingSpec.motto_metal` = the active
`settings.ring_finish` — read as continuous text, not a seat-by-seat
split like `letter_metal`).

ONE SHARED RADIUS, not two: the first round gave each motto its own
radius because pinned letters intentionally OVERLAPPED in angle (both
mottos' own O at noon, own S at 16h — the "MASON reads twice" design).
The corrected layout drops that shared-angle design — the two arcs
never share an angle now — so both draw at the SAME
`RING_MOTTO_RADIUS_FRACTION` (`RING_MOTTO_RADIUS_STEP` is deleted, Rule
#6 — no leftover unused constant). `defaults.dial_window_margin_fraction`
still grows to cover the motto's own outer reach whenever
`skin.ring.motto` is non-empty (a no-op term in its `max()` for every
other preset — DOMY/MORPH/Omega and every custom ring keep their old
margin exactly), now measured from the single shared radius instead of
the outer of two. See [Ring Presets](../data/rings.md) for the exact
pin table and [The DOMY Canon](../CANON.md)'s §The Banknote for the
doctrine.

### WeekdayLayer (DAILY, hover-variable — painted LIVE)
`hover_variable = True` (owner 2026-07-17, ROADMAP 15f): the bodies
enlarge on hover and go full on reveal, so the compositor draws this
layer LIVE every frame instead of baking it into the cached composite — a
hover enter/leave rebuilds NOTHING.
Draws only while a slot DRIVES the classic unit
(`weekday_classic_slot`). "ghost": bodies on the pointer's slots at
`slot angle + hexagram_rotation`, current day opaque, rest at
`ghost_opacity`; the hexa and trio layouts additionally center a ghost
Sun (cross/octa seat the Sun on an arm). "center_only": nothing here —
the center pass draws it. EVERY body — the diamond slots AND the
hexa/trio center Sun — is `weekday_body_size()` (owner 2026-07-18,
his screenshots: the center used to draw `center_scale × seat factor`,
~170 px against 144 px diamonds, and the reveal center dropped the seat
factor and SHRANK to ~114 px; one formula now, both states, and it
retired the old "Sun is 1.20×" note — only the center_only showcase
keeps `center_scale`). Bodies draw a skin image when provided,
otherwise a colored disc; the white label is the weekday SHORT name
(MON/TUE/…) below 720 px, the full name from 720 up.

### CenterBodyLayer (MINUTE)
The current day's CENTER image ABOVE the hands: the opaque Sun on
Sundays in ghost mode (hexa/trio), or today's body in center_only mode.
Slot images never move up here. Sized by `weekday_body_size()` — the
same as the diamond bodies, in the normal state and during the reveal
alike (owner 2026-07-18); center_only keeps its own `center_scale`
showcase, and the compositor's center hit disc mirrors both drawn
sizes exactly.

**THE DUAL/NINTH CENTER TIME WINDOWS (owner INSTRUCTION #5 + solar
amendment, round R3b item 3):** on a real Sunday, when the classic
unit's duality lives in ONE merged center image instead of the
Compass/Seasons' two separate seats — `center_dual_face(skin)`, the
COMPLEMENT of `sunday_dual_face` (hexa/trio ALWAYS merge the Sun into
the center; `center_only` mode merges it for every pointer, since there
are no seats to hold a second face there) — the SOLAR clock, not the
wall clock, may swap which face draws: `center_face(day, tick,
has_ninth)` reads `day.sun.noon` (the SAME anchor the hexagram's own
rotation reads) through `core.angles.hours_between` and returns
`"ruler"` (GOOD, the default), `"servant"` (EVIL, near solar midnight)
or — only for a theme that names one — `"ninth"` (near solar noon).
`theme_ninth(theme)` is the ONE existence-gated lookup into
`constants.WEEKDAY_THEME_NINTHS` both this layer and the compositor's
hover share (Rule #5) — a theme with no table entry, or whose plate has
not landed, never offers "ninth"; its midnight window then WIDENS from
±1h to ±2h (owner: "za one koje nemaju 9tog… 22h i 2h"). The
ghost-reveal Sun (`ctx.reveal_active`) always reads plain — the reveal
promises the ordinary "two persons, a union", never a third face.
`CENTER_NOON_WINDOW_HOURS` / `CENTER_MIDNIGHT_WINDOW_HOURS` /
`CENTER_MIDNIGHT_WINDOW_HOURS_NO_NINTH` (`config/constants.py`) are the
tunable window widths.

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
cities. This geometry is `render.assets.moon_lit_region(fraction,
radius)` (extracted 2026-07-19 out of `_draw_moon` so the
Encyclopedia's live-rendered Moon pages,
`render.assets.moon_phase_image`, share the EXACT same shape and never
drift apart — replacing the eight pre-baked plates, owner decree
"bolje crtati na licu mesta nego 15MB fajlova"); the extraction fixed a
real bug — AT THE EXACT QUARTERS (fraction 0.25/0.75) the terminator
semi-axis is mathematically zero, and Qt's `addEllipse` on a
zero-width rect used to degenerate the `united`/`subtracted` boolean
op to an EMPTY path, rendering the moon fully DARK instead of exactly
half-lit; `moon_lit_region` now special-cases the collapse and returns
the half-disc directly). With both markers on they share the rim at orbit 0.75 and the
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

**Eclipse display (owner 2026-07-18, ROADMAP 15h item 11 — implemented,
refining the sealed glow-metal triad):** `ctx.tick.eclipse_event`
(`core.clock_state.EclipseEvent`, ±3h window,
`constants.ECLIPSE_GLOW_WINDOW_H`; always `None` without the OPTIONAL
Deep Time pack — see [Deep Time](../data/deep_time.md) for the absence
rule) rides the SAME relocation-to-ring-band mechanic as the
season/moon glow — no new hit-test path, exactly as the Session 21-C
note predicted. A SOLAR eclipse (`kind == "solar"`) makes the Earth
marker's OWN existing "season event" glow turn RED/orange-red
(depending on state, below) instead of golden and swaps its drawn art
to `ECLIPSE_SOLAR_ART` — the Planets theme's Eclipsed-Sun dual
(`assets/weekday/planets/primary/sun_eclipse.png`, source-mapped
by `paths.art_file`, falling back to whichever art source actually
ships the file). A LUNAR eclipse (`kind == "lunar"`) turns the Moon
marker's glow the blood-moon BRONZE (`GLOW_ECLIPSE_LUNAR_COLOR`, the
SAME hex as `BRONZE_LETTER_TINT` — reused verbatim, not a new color)
and darkens the disc — see THE STATE TABLE below.

**THE STATE TABLE (fix round C, owner decree 2026-07-19):** the type→state
lookup, `eclipse_render_state(event)`, maps `(event.kind, event.type)`
through `defaults.ECLIPSE_TYPE_STATE`. The catalog's TYPE vocabulary was
ground-truthed directly from `Database/deep_time.sqlite`'s real rows —
solar: `partial` / `annular` / `total` / `hybrid`; lunar: `partial` /
`penumbral` / `total` (no other values exist in either table). `hybrid`
has no dedicated owner state and maps to `solar_total` — a hybrid
eclipse shows true totality along most of its ground track, the closer
of the two sealed states, a deliberate choice rather than the
unknown-type fallback. An unknown/missing type (should not occur — the
generator only ever writes the vocabulary above) documented-falls-back
to the kind's `partial` state via `defaults.ECLIPSE_STATE_FALLBACK`
(Rule #1: a plausible middle ground, never a crash).

| State | Disc brightness | Glow strength | Fringe |
|---|---|---|---|
| lunar_total | 7% | 1.0 (full) | yes |
| lunar_partial | 18% | 0.6 | yes |
| lunar_penumbral | 60% | 0.25 | no |
| solar_total | n/a (art only) | 1.0 (full) | n/a |
| solar_annular | n/a (art only) | 1.0, own orange-red hue | n/a |
| solar_partial | n/a (art only) | magnitude-linear (unchanged) | n/a |

The state alone sets the disc BRIGHTNESS — never magnitude, never
translucency — via `defaults.ECLIPSE_STATE_MOON_BRIGHTNESS`. The owner's
complaint about the old build: a TRANSLUCENT bronze `SourceOver` wash
whose alpha ALSO scaled with magnitude read as "a visible moon shining
bronze, sometimes more sometimes less transparent". The fix:
`_draw_moon(..., darken_state=...)` fills the WHOLE disc (lit and unlit
halves alike — totality dims the full face) with
`QPainter.CompositionMode_Multiply` against an OPAQUE gray whose value
is the state's brightness fraction (0..1 → 0..255) — multiplying by a
neutral gray scales R/G/B equally, i.e. true value-down with the hue
untouched, drawn fully opaque over the normal phase render (never a
partial-alpha overlay a bright pixel can bleed through). **BLOOD MOON
(TASK 5, owner verdict "may", fix round E, 2026-07-19):** `lunar_total`
ALONE swaps the neutral gray for `tinted_gray(value,
defaults.ECLIPSE_TOTAL_MOON_TINT)` — the SAME black→tint→white tritone
`RingLayer`'s ring recolor uses (see its own note below) — so the
near-black disc reads dark AND visibly copper-red, not a flat gray;
`lunar_partial`/`lunar_penumbral` keep the plain neutral gray (only
totality dims the whole face enough for a color cast to read honestly).
Solar states never darken the disc — only the ANNULAR "ring of fire"
gets its own glow color (`GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR`, hotter
orange-red than the plain `GLOW_ECLIPSE_SOLAR_COLOR`), same black-sun
art as total.

**VISIBILITY (TASK 4, owner verdict "may", fix round E, 2026-07-19):**
`EclipseEvent.visible` (computed observer-relative in
`core.clock_state._with_visibility` — see
[Clock State](../core/clock_state.md), per the purity law — never here)
mutes BOTH markers' glow the SAME way when False: color swaps to
`defaults.GLOW_ECLIPSE_INVISIBLE_COLOR` (a desaturated silver-gray) and
`strength` is multiplied by `defaults.ECLIPSE_INVISIBLE_STRENGTH_FACTOR`
(0.5) — checked AFTER the normal state color/strength are computed, so
it overrides them regardless of type/state. The art swap
(`ECLIPSE_SOLAR_ART`) and the disc darkening/copper tint above are
UNTOUCHED by visibility — the event is real, only the glow reads
"can't actually see this one from here". `Compositor._eclipse_hover_line`
names the reason (see [Compositor](compositor.md)).

Glow STRENGTH is likewise state-driven
(`eclipse_state_glow_strength(state, magnitude)`,
`defaults.ECLIPSE_STATE_GLOW_STRENGTH`) EXCEPT `solar_partial`, the
owner's one named exception ("SOLAR partial: art + glow scaled by
magnitude") — it alone keeps the original magnitude-linear mapping via
`eclipse_glow_strength(magnitude)`, linear between
`ECLIPSE_GLOW_STRENGTH_MIN/MAX` over `ECLIPSE_MAGNITUDE_MIN/MAX`,
clamped outside. The turquoise fringe (Option C, below) is likewise
withheld for `lunar_penumbral` (`defaults.ECLIPSE_STATE_FRINGE`) — real
penumbral eclipses show no visible ozone-band rim.

**LUNAR ECLIPSE OPTION C (owner sealed 2026-07-18):** the bronze glow
gains a thin TURQUOISE FRINGE at its OUTER edge — the real ozone-band
color at the umbra's rim during totality. `draw_event_glow()` takes an
optional `fringe_color` parameter (None for every other caller,
unchanged): when given, it adds THREE extra gradient stops on top of
the existing core/mid/edge triad — transparent → peak → transparent —
straddling `ECLIPSE_LUNAR_FRINGE_STOP` (a fraction of the halo radius,
`ECLIPSE_LUNAR_FRINGE_HALF_WIDTH` wide either side), inserted AFTER the
bronze mid stop and BEFORE the fully-transparent edge stop so it reads
as a separate ring rather than blending into the bronze core. The
lunar eclipse call is the only one that passes
`fringe_color=ECLIPSE_LUNAR_FRINGE_COLOR` (`#40E0D0`-family turquoise,
`ECLIPSE_LUNAR_FRINGE_ALPHA` peak, scaled by the state/magnitude
`strength` exactly like the bronze glow itself, and withheld outright
for `lunar_penumbral`, see THE STATE TABLE above).

`draw_event_glow()`'s optional `strength` parameter (default 1.0, so
every pre-existing season/moon call is unchanged) is where every glow
color above lands, whichever function computed it (state-fixed via
`eclipse_state_glow_strength`, or magnitude-linear via
`eclipse_glow_strength` for `solar_partial`). The Earth/Moon hover text
(`_earth_text`/`_moon_text` in [Compositor](compositor.md)) NAMES the
active eclipse (kind, type, magnitude, local instant) via
`_eclipse_hover_line()`, reading `EclipseEvent.type` directly — the
SAME vocabulary the state table maps — outranking the plain
season-event line on the Earth hover.

### HandLayer (MINUTE)
Owner convention: every hand canvas is exactly its designed size and
rotates about a point `HAND_HUB_OFFSET_UNITS` (15) above the canvas
bottom. ALL hands share ONE scale — the longest hand's tip reaches
`HandsSpec.reach_fraction` of the dial radius and the others keep their
drawn proportions.
