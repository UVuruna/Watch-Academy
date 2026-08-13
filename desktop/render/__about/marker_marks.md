# Marker Marks

**Script:** [Marker Marks (script)](../marker_marks.py) · **Flow:** [diagram](../__flow/marker_marks.md)

## Purpose
Everything drawn AROUND an Earth/Moon marker rather than on its face:
the position pointer's three shapes, the four life stations' marks, and
the solar eclipse's own geometry. One module because all three answer
the same question with the same inputs — given a body at a dial angle,
with a radius, what ornament does it wear? — and all three were
approved in the owner's single 2026-08-10 pass over the
rendering-proposals page.

The Moon's own FACE is the other half and lives in
[Moon Face](moon_face.md); the halo behind a relocated marker is older
and still lives in [Eclipse Glow](eclipse_glow.md).

## The angle is never "up"
Every mark here takes the body's own dial angle and is built from
`painting.dial_point`, so it points along the RADIUS at the body's
actual seat on the circle. This is written down because the owner had
to correct it once (2026-08-10): the proposals page drew each pointer
straight up, which is only correct for a body at the top of the dial.
The shipped code was already radial — the mockup was the thing that was
wrong — and `tests/test_marker_pointer.py` pins it for all three shapes
so the drawing and the drawings of the drawing cannot drift again.

## The 2026-08-10 screenshot corrections
The owner's four-styles screenshot round re-cut two of the three
shapes: the CHEVRON is now the SAME triangle geometry drawn as LINE
only (the open-V first cut was far too wide and looked unrelated to
the triangle beside it). All three are PROPORTIONAL to the body's own
half-size, drawn BEHIND the body ("IZA NE ISPRED ZEMLJE"), bridging
the tick zone: base hidden under the disc, tip on the thread line at
the tick roots (`dial.earth_moon_orbit_fraction`'s tangent fit puts
the body's edge on the little pointers' tip line).

## The direction follows the body (owner correction 2026-08-11)
`draw_pointer` takes an optional `tip_radius` — the marked point's own
radius, the 360 small pointers' tips. A body on its ordinary orbit
sits INSIDE that circle, so the arrow points OUTWARD, as before; a
body relocated onto the ring band (its event window) sits OUTSIDE it,
so the arrow FLIPS and points INWARD at the same marked point instead.
`tip_radius=None` reproduces the ordinary outward case from the
measured plate ratio, unchanged. The owner's own words for the flip:
"obrni strelicu... jer je sada na RINGU" (slika 4/5).

## The gem, rewritten (owner correction 2026-08-11)
The GEM shape no longer hides part of itself under the disc: one
vertex sits on the body's own edge, the other on the marked point, and
the WHOLE diamond lives in the gap between the body's circle and the
360 tips' circle (slika 2/3 — parts under the disc used to make it
read like the triangle beside it). Its width is a fraction of its own
height (`dial.MARKER_GEM_WIDTH_RATIO`, always < 1) so height is never
less than width — "ako je ista vrednost moze blago veca visina".
`MARKER_GEM_LENGTH_RATIO` is retired; the gem's length is now simply
the gap itself.

## The stations
New moon is birth, first quarter youth, full moon the zenith of
maturity, last quarter age; winter solstice, spring equinox, summer
solstice and autumn equinox are the same arc across the year. Both
bodies share one grammar so the language is learned once and read on
two clocks — the reason `arc_grammar` is the default for each.

`inner_glow` follows the owner's own specification of intensity: the
glow's RADIUS never changes, only its alpha, so a full moon burns
brighter rather than reaching further. Youth carries a glow both inside
the dark half and outside; age carries the same OUTER strength with no
inner glow at all; birth carries light almost entirely inside. The
numbers are `constants.MOON_STATION_GLOW`.

## Connections

### Uses
- [Painting](painting.md) — `dial_point`, the one clockwise-from-top
  polar conversion
- [Moon Face](moon_face.md) — `dark_region`, so the inner glow and the
  shadow agree about where the dark half is
- [Config (folder)](../../config/___config.md) — `constants` (the
  rosters, the glow ramp, the station lookups), `dial` (the pointer's
  proportional length/width ratios and the tick-line measurements), `palette` (`INSTRUMENT_SEASON_COLORS`,
  the marker border, the glow colours)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer`
  draws every pointer, station mark and solar eclipse through here
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds each
  picker's preview from the same functions

## The eclipse "bite", repainted as seen (owner correction 2026-08-11)
A black offset-occulter circle over the already-black eclipse art was
invisible ("ne moze crni isecak na crnoj eklipsi") — the base art
under the bite is now `config.defaults.ECLIPSE_SOLAR_ART`, the owner's
own icon (a black disc in rays), and the bite paints the VISIBLE
remainder BRIGHT rather than painting a dark occulter over dark art.
The old procedural corona-spikes block is gone. (SUPERSEDED the same
week — the bite is now his own two body plates composited, below. The
correction that produced this paragraph still stands and is the reason
the composition draws his own art rather than a procedural silhouette;
only the mechanics changed.)

## THE SIZE RATIO — the occulter is the Sun's own size (owner bug 2026-08-13)
His words, looking at `solar_partial_bite.png`: *"kruznica delimicnog
pomracenja je manja od kruznice sunca"* — and he was right, by a factor
of four.

The 2026-08-11 cut expressed the magnitude as a lunar PHASE and asked
`moon_lit_region` for the matching lit AREA. A phase terminator is a
half-ellipse of semi-axis `r*|cos 2*pi*f|`, so at the catalogue's
typical partial magnitude 0.62 the dark curve was drawn **0.24 r**
wide. Correct area, wrong object: the picture said *a small body
crossed the Sun*, and the bite's curvature was a tight little circle
instead of the Sun's own.

At a solar eclipse the Moon's apparent diameter is within a few percent
of the Sun's — that is the whole reason eclipses look the way they do —
and which side of 1.0 the ratio falls on is what DECIDES the type.
`marker_marks._SOLAR_SIZE_RATIO` states it per state (total 1.05,
hybrid 1.00, annular 0.95, partial 1.00), with the catalogue ranges in
its comment. A partial eclipse is a near-MISS IN ALIGNMENT, not a small
Moon.

So `solar_occulter_geometry(state, radius, covered)` returns the
occulter's radius from that table and its centre DISTANCE from the
magnitude:

```
d = R + r - 2 * R * magnitude
```

— the same formula, and deliberately the same shape, as the lunar
side's `render.moon_face.draw_umbra_sweep`; the `2 *` factor always
multiplies the radius of the body being ECLIPSED (the Moon there, the
Sun here). Magnitude 0 lands exactly on tangency, full coverage on
`d = 0`. The bite then fills the intersection with the silhouette
colour and the remainder bright, both clipped to the Sun's disc, so the
body always reads at its true size. ANNULAR (occulter centred and
genuinely smaller) and TOTAL (corona and silhouette) keep their own
branches untouched. `_ANNULAR_SHRINK` stays a deliberate legibility
exaggeration of the true 0.95 ratio — at a real 0.95 the ring of fire
is two pixels wide on a dial mark.

Tooth: `tests/test_eclipse.py::test_the_partial_occulter_is_the_suns_own_size`,
counter-proved by restoring the phase formula (it reports 0.240).

## THE ECLIPSE REWORK (owner order 2026-08-13)
His words: *"skoro sve slikamo isto ... zato i treba rework"* — and a
full render of the matrix proved him right twice over. Four
combinations rendered ONE byte-identical picture, and a further pair
(`solar_partial_halo` at magnitude 0.62 against `solar_total_halo` at
1.05) was the same picture to the eye while a hash called it different.
Three collapses lived in this module and all three are closed here:

- **`halo` was empty.** The style returned without drawing, so the
  caller's glow was the entire picture and the only thing separating a
  62 % partial from totality was the glow's own alpha. It now draws a
  MAGNITUDE RING outside the body — radius, thickness and alpha all
  rising with the covered fraction — and the body itself is still
  untouched, which is the property the style is chosen for. The ring is
  PEARL, not the type's colour: the first cut drew it in the eclipse
  red, inside a red halo, and it was invisible.
- **`bite` collapsed into `halo` at totality.** It returned early when
  the Sun was fully covered, so the two styles drew the same thing at
  the one moment the style exists for. Totality now paints the CORONA
  and the black silhouette inside it — the only thing a person actually
  sees.
- **`hybrid` was an alias of `total`** (`config.glow.ECLIPSE_TYPE_STATE`),
  which made the two identical in every style at once. A hybrid eclipse
  is total along part of its ground track and annular along the rest,
  so every style here now draws BOTH AT ONCE, one rule learned once:
  the `bite` shows the corona with a ring of fire along half the limb,
  the `magnitude_arc` splits its sweep across two lanes (the annular
  half on an inner ring, the total half on the outer), and the `halo`
  wears two concentric rings instead of one.

## THE BITE IS HIS OWN TWO BODIES (owner art + owner rule, 2026-08-13)
The same evening as the rework, the owner drew two plates —
`shared/assets/instrument/icons/eclipse_body_sun.png` (his rayed yellow
Sun) and `eclipse_body_moon.png` (a black disc with a rim glow) — and
ruled that the `bite` style is nothing but those two composited. He had
named them `eclipse_light`/`eclipse_dark` and renamed them himself,
because colour is the least important thing about them and "dark" reads
as a dark Sun rather than as the Moon.

**ONE composition, all four types.** Draw his Sun, then his Moon over it
at the `occulter_radius` and `centre_distance` `solar_occulter_geometry`
already returns, clipped so the dark disc covers the Sun's YELLOW DISC
and never its rays. In his words: at totality cover the whole disc and
leave only the rays; at every other type the dark disc is smaller or
offset, so part of the yellow disc survives beside the rays. Totality is
simply the case where the composition happens to cover everything —
never a different picture drawn a different way.

The geometry he confirmed, type by type: ANNULAR — the Moon IS centred,
merely too far away to be big enough, so the dark disc shrinks and stays
put. PARTIAL — the Moon does not cross the centre, so a disc of the
Sun's own size is offset and the dark edge is that disc's real circular
arc at its real offset. TOTAL — covered, rays alone. HYBRID — see below.

**Everything is MEASURED off his files, never guessed**
(`marker_marks._SUN_PLATE_*`, `_MOON_PLATE_*`; `tests/test_eclipse_plates.py`
re-measures them and fails if a constant drifts from the art):

| Plate | Measurement | Fraction of half-size |
|-------|-------------|----------------------|
| `eclipse_body_sun.png` (576²) | last fully solid yellow ring — the DISC | 0.623 |
| | outermost ring carrying any ink — the RAY TIPS | 0.889 |
| `eclipse_body_moon.png` (360²) | last ring of pure black — the Moon's limb | 0.925 |
| | rim glow, which runs to the frame edge and is cut there | 1.000 |

Two consequences fall straight out of those numbers. The Sun plate is
scaled so its yellow disc is exactly the body radius, which puts his ray
tips at 0.889/0.623 = **1.427** body radii — past the **1.38** the
transparent window margin reserves (`_MARK_REACH_LIMIT`), so the plate is
CLIPPED at that wall. It costs the outer 3 % of the ray tips on the ~13 %
of the limb still carrying a spoke out there, at under half alpha; no
continuous ink exists to cut, so no hard circular edge can appear.
Shrinking the plate instead would have drawn the Sun 3 % smaller than the
geometry every other mark is built on. And the Moon plate is scaled by its
BLACK BODY, not its frame: the occulter is the solid disc, his rim glow is
extra light beyond it, and the clip to the yellow disc keeps that glow off
the rays.

**The procedural corona is retired.** Totality was shown to the owner with
the argument that his yellow rays are not what a real corona looks like —
pearly white, irregular, long streamers — and he ruled against it: it is
his instrument and this is how it represents an eclipse. `_corona` and
`_ring_of_fire` are both gone; the `bite` style draws no procedural marks
at all any more.

**Only the PNGs are ever read.** The `.svg` twins beside them are dead
twice over: Qt renders SVG Tiny 1.2 and silently drops `mask`, `filter`
and `feColorMatrix`, so his mask-built Moon comes out a flat olive disc —
and by his own account his exporter mangles them anyway, which is why he
redrew both as PNG. Never wire the SVG back in.

## THE GHOST RING — how a hybrid stays its own picture
A hybrid begins annular, turns total across the middle of its path and
ends annular. We draw ONE picture, at greatest eclipse, and at the
epicentre a hybrid IS total — so the honest composition is the total one,
and both would cover the disc completely (ratios 1.00 and 1.05, both
landing on centre distance zero). That is the collapse the rework closed,
about to re-open.

So the hybrid's second half is carried by an added MARK rather than by a
faked geometry: **one thin ring of fire hugging the inside of the dark
limb**, in the annular orange. It says *totality here, the ring of fire
elsewhere along this path* — and it is true, which the half-and-half split
it replaced never was (no eclipse looks like that from anywhere).

Its WIDTH is measured, not chosen: exactly the rim-glow band of his own
Moon plate (1.000 − 0.925), a fifth of the annular ring's own
`1 − _ANNULAR_SHRINK`. Only its strength is a decision, and a narrow one —
the ring is the ONE thing separating hybrid from total, so it has to clear
the distinctness measure's structure floor of 0.20. Measured: **0.171 at
alpha 0.55** (below the floor — the same picture), 0.221 at 0.70,
**0.291 at 0.90**, which is what ships.

The tooth is [`tests/test_eclipse_distinctness.py`](../../tests/___tests.md),
which compares every legal (type, style) pair with a perceptual measure
rather than a hash — deliberately blind to global brightness, because
that blindness is exactly what let the owner's pair pass a hash.

## Functions
- `draw_pointer(painter, shape, angle_deg, dial_radius, orbit_fraction, half_size_fraction, color, tip_radius=None)`
- `draw_station_mark(painter, style, station, radius, color)` — the
  Moon's grammar; `draw_sun_station_mark(...)` is its solar twin, which
  adds the seasonal halo and the day/night wedge.
- `draw_solar_eclipse(painter, style, radius, state, magnitude, paint_face)`
- `station_of_moon_event(name)` / `station_of_season_event(name)` — the
  event name a tick already carries, resolved to one of the four
  stations, or None when the instant is not a principal one.
