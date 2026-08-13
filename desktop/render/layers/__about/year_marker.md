# Year Marker Layer

**Script:** [Year Marker Layer (script)](../year_marker.py) ·
**Flow:** [diagram](../__flow/year_marker.md)

## Purpose

Paints the moving bodies along the inside of the dial: the Earth (riding the
year wheel, summer solstice at the top — or the Calendar's own almanac
month wedges), the Moon (riding its own cycle, new moon at the top, full
at the bottom, clockwise, showing the current illumination) and — since
the owner's order of 2026-08-12 — THE ECLIPSE, a third body of its own.
The Elements switches (`show_earth`/`show_moon`/`show_eclipse`) pick which
of the three draw, and the eclipse's switch is independent of the other two.
During a ±12h (Earth) or ±6h (Moon) event window — a season turning point,
a principal moon phase — the marker RELOCATES radially onto the ring band
centerline and grows a colored glow (golden for the Sun's stations, silver
for the Moon's).

**THE ECLIPSE IS NO LONGER A COSTUME** (owner order 2026-08-12, ballot
A1/B2/C1/D1/E1/F1). Until that round a solar eclipse was drawn ON the Earth
marker and a lunar eclipse ON the Moon marker, which seated the event at the
Earth's DATE angle or the Moon's PHASE angle — never at the hour it
happens — and made a solar eclipse vanish whenever the Earth was switched
off. Now `_draw_eclipse_body` seats it at `angles.time_to_dial_angle` of its
own greatest-eclipse instant in local time, on the bodies' own orbit lane,
for `constants.ECLIPSE_BODY_WINDOW_H` (±12 h) around that instant; the Earth
and the Moon keep their own seats, art and faces on an eclipse day exactly
as on any other. The three module-level helpers `eclipse_body_angle`,
`eclipse_body_scale` and `eclipse_body_orbit` are the seating law in one
place, so the layer and its teeth read the same numbers. `eclipse_body_orbit`
also carries THE ESCAPE: a solar eclipse happens at new moon (seat: the top)
and a lunar one at full moon (seat: the bottom), so when the eclipse would
TOUCH a drawn marker — measured between centres, `dial.ECLIPSE_BODY_CLEARANCE`,
not by the exact hour — the ECLIPSE leaves for the ring band and the marker
keeps the ordinary circle.

The escape has a SECOND half, `marker_yields_band`, and it is not optional:
a marker inside its own event window is itself relocated to the ring band —
and a full Moon is band-bound for six hours around precisely the instant a
lunar eclipse happens. A first cut measured the markers where they currently
STOOD, so the eclipse escaped from on top of the Moon to on top of the Moon;
the render showed it, `tests/test_eclipse.py` now holds it. The collision is
therefore measured against the markers' ORDINARY circle, and when it fires
the marker gives the band up: the eclipse takes the ring, the marker takes
the circle with its own new-/full-moon face — the owner's sentence,
one-directional, never negotiated. The eclipse STYLES themselves are unchanged; they
paint on the new body.

ONE SEAT, TWO READERS (owner report + question 2026-08-12: "the hover does
not seem to follow the Moon's relocation off the ring when it overlaps the
eclipse", and "how is the hover not simply every time the cursor crosses
that element's own dimensions — what imaginary space is it following?"). It
was following one: `Compositor._element_at` carried its own hand-written
copy of this file's geometry, so each relocation the paint learned had to be
copied there too, and the ones that were not — the Moon's rim-riding lane
split, the transit shrink, and the band-yielding above — left the cursor
answering at a seat nothing was drawn at. The copy is retired. The seats,
lanes and sizes of both markers are module functions now — `moon_marker_angle`,
`moon_marker_orbit`, `moon_marker_scale`, `earth_marker_angle`,
`earth_marker_orbit`, `earth_marker_scale` — the layer paints with them and
the hit test answers with them, so what is drawn IS what the cursor finds,
by construction rather than by two edits staying in step.

The module also exports a standalone helper,
`earth_region(latitude, longitude)`, imported directly by
`render/compositor.py` for hover/tooltip text — not only used internally by
the layer. It resolves the continent LIVE from the day context's own
coordinates on every call (R-28 fix, 2026-08) — nothing about the region is
baked into the skin, so a Quick Jump/Time Travel/Greenwich simulation moves
the Earth marker's face exactly like an ordinary location change does.

THE LINE AND THE BODIES (owner correction 2026-08-10, the four-styles
screenshot round — SUPERSEDES the 2026-08-09 "clear orbit lane"
clearance and its hexagram-apothem floor): the QUIET (non-glowing)
orbit radius is computed fresh every paint by `config.dial.
earth_moon_orbit_fraction(ring_size, half_size)`, now a PER-BODY
TANGENT fit — `dial.RING_INNER_CONTENT_INNER_FRACTION` (THE LAST
LINE: the inner side of the inner ring, where the five-minute
strokes/arrows/numbers stop, owner third round 2026-08-11 — so the
body never slices any inner-ring element) scaled by
`dial.interior_scale`, minus THIS body's own half-size — BOTH bodies
touch that line, each on its own radius, and the Moon Horizon Band's
thread rides the SAME line behind them. The
skin's own `orbit_fraction`/`moon_orbit_fraction` fields stay NOMINAL,
read only by `moon_transit_opacity`'s touch-angle approximation.
A literal transit — the Moon crossing the Earth — still exists (the
two radii differ only by the bodies' half-size difference);
`render/compositor.py`'s `_element_at` hit-test computes the identical
radius so hover/click always matches the drawn position. Pinned by
`tests/test_earth_moon_orbit.py`. The GLOWING relocation below (to the
ring band centerline, during a season/eclipse event window) is
untouched — that overlap is the owner's own approved dramatic effect.
The position pointer is drawn BEHIND the body (owner correction
2026-08-11, "IZA NE ISPRED ZEMLJE" — his second time saying it), its
dimensions proportional to the body's own half-size, bridging the
tick zone: base hidden under the disc, tip on the thread line at the
tick roots (`tests/test_marker_pointer.py`). The 2026-07-12
below-horizon Moon dimming is RETIRED (owner 2026-08-11, "mesec opet
ima OPACITY!!!") — the band says whether the Moon is up; the disc is
always solid; `moon_hidden_alpha` stays stored but unread.

THE POSITION POINTER (off by default) lives in
[`marker_marks.draw_pointer`](../../__about/marker_marks.md) since
2026-08-10, when the owner approved a chevron and a gem beside the
triangle; every shape rides the body's own dial angle rather than a
fixed screen "up". Its z has flipped twice: the 2026-08-09 grader round
moved it ON TOP of the body, and the owner's 2026-08-11 screenshot
round reversed that as wrong — it is BEHIND the body now (see THE LINE
AND THE BODIES above), which is what he had asked for the first time.

THE WORLD OFFSET ([World](../../../core/__about/world.md)): both markers are
drawn ON the turning dial face, so both take `ctx.world_offset`. At night
that is +180, which stands the WINTER solstice where the summer solstice
stood and the FULL moon where the new moon stood. The rim-transit test
between them keeps the RAW angles — the same offset on both leaves their
separation unchanged.

`Cadence.MINUTE`: eclipse windows, season-event glow and moon transit
opacity are all evaluated against `ctx.tick`, and both markers relocate
within a tick-scale window — needs a per-tick repaint. Not `hover_variable`
— `MINUTE` already repaints every frame; the individually-hoverable "earth"
and "moon" elements are gated with `Layer._gate` like any other MINUTE
layer, and their lift twin lives in `HoverLiftLayer`.

## Connections

### Uses
- [Eclipse Style Door](../../__about/eclipse_style.md) — `resolve_eclipse_style`,
  asked before `_draw_moon`'s umbra_sweep/halo dispatch
- [Asset Variants](../../__about/asset_variants.md) — `moon_lit_region`
- [Calendar Mount](../../__about/calendar_mount.md) — `calendar_day_arrow`,
  `calendar_wheel`
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Daylight](../../__about/daylight.md) — `moon_transit_opacity`
- [Config (folder)](../../../config/___config.md) — `dial.earth_moon_orbit_fraction`,
  `dial.interior_scale`, `dial.GLOW_RING_RADIUS_FRACTION`
- [Eclipse Glow](../../__about/eclipse_glow.md) — `draw_event_glow`,
  `eclipse_render_state`, `eclipse_state_glow_strength`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_outlined_text`,
  `draw_pixmap_centered`, `tinted_gray`
- [Skin Geometry](../../__about/skin_geometry.md) — `hover_factor`
- [Subdial](../../__about/subdial.md) — `display_year`

### Used by
- [Compositor](../../__about/compositor.md) — fifth layer in the default `z_order`
  (skipped only when `show_earth`, `show_moon` AND `show_eclipse` are all
  off — the eclipse body is independent of the two markers, so two
  switches are no longer enough to retire the layer); also imports the
  module-level `earth_region()` function directly for hover text
- [Eclipse Plates](../../__about/eclipse_plates.md) — the Encyclopedia's
  own pictures of these same styles, drawn through the same painters
- [Hover Lift Layer](hover_lift.md) — a `lift=True` twin repaints whichever
  of "earth"/"moon" is hovered, above the hands

## Classes

### YearMarkerLayer
`cadence = Cadence.MINUTE`.
- `paint()`: draws the Earth, then the Moon, then the ECLIPSE body — each
  gated independently by its own Elements switch and `Layer._gate`. The
  eclipse is drawn LAST so it stands above both markers on the day it
  belongs to.
- `_draw_earth()`: resolves the year-wheel angle (almanac month wedge under
  the Calendar pointer, the shared six-anchor season wheel otherwise),
  relocates + glows during a season window (an eclipse no longer touches
  this marker at all), picks the
  region/day-night art variant (`earth_region()` below), clips to the
  marker disc, and draws the FOUR exclusive label modes
  (`_draw_earth_label`: weekday / date / date+weekday / full date+year).
- `_draw_moon()`: hands the face to
  [`render.moon_face`](../../__about/moon_face.md), which owns the three
  owner-approved treatments of the unlit half and decides whether the
  face is clipped first (the cut styles) or covered after (the opaque
  one). Its `darken_state`/`lunar_magnitude` arguments are now passed
  ONLY by `_draw_eclipse_body` — the Moon marker itself never darkens.
  A lunar eclipse takes one of five routes there: "umbra_sweep" draws
  Earth's shadow as a real curved edge across the disc; "blood_moon"
  (owner ballot 2026-08-13) ramps the colour toward copper with DEPTH IN
  THE UMBRA and leaves the penumbra grey ([Moon
  Face](../../__about/moon_face.md)); "danjon_scale" gives the disc the
  indicative Danjon step's own colour and hangs the five-cell legend
  beneath it ([Eclipse Danjon](../../__about/eclipse_danjon.md));
  "halo" keeps the older whole-disc multiply by a neutral (or copper, at
  totality) gray; and "horizon_shadow"/"contact_marks" leave the disc
  alone because the event is written on the Moon Horizon Band instead.
  `spec.eclipse_lunar_style` is read through [Eclipse Style
  Door](../../__about/eclipse_style.md)'s `resolve_eclipse_style` first,
  so the only fallback that can still fire here is the CONTEXT one — the
  two band styles resolve to "halo" when `moon_band_mode != "horizon"`,
  and say why.

  THE DANJON GAUGE IS TURNED BACK UPRIGHT in the southern hemisphere.
  The disc above it is deliberately upside down (the lit side really
  does swap, owner spec), but the gauge carries a READ value in letter
  plates, and text is not a phase.
- `_draw_eclipse_body()`: the third body — seat, glow, pointer and the
  chosen style. It is the ONE caller that has an observer in hand, so it
  is the one that passes `event.distance_km` down to
  [Solar Eclipse](../../__about/solar_eclipse.md)'s `draw_solar_eclipse`
  — the `totality_path` style's whole subject (owner ballot 2026-08-13).
  Read off the event, never recomputed, so the arc and the hover's
  "path {d} km away" reason can never disagree. Also: solar art drawn WHOLE (no disc clip: `sun_eclipse.png` is
  a black disc in rays on transparency, and clipping would cut the rays
  off), lunar handed to `_draw_moon` with the eclipse state.
- `_eclipse_glow_paint()`: the body's halo colour and strength — red,
  amber for annular, blood-moon bronze for lunar, and the muted silver at
  half strength when the event is real but not visible from here.
- `_day_fraction(day_length)`: the day's share of 24 h, parsed off the
  SAME "HH:MM" string the octa's bottom arm displays — the Sun's
  day/night wedge station is a picture of that number, so the two
  cannot disagree.

THE MOVING BODIES (owner verdict 2026-08-10). Everything about HOW the
two markers are drawn is now a user menu, picked in Watch Face ▸ Hands &
Bodies and carried on the spec: the unlit half, the crossing, the
pointer's shape, both eclipse treatments and both bodies' four life
stations. This layer only dispatches — the drawing lives in
[`moon_face`](../../__about/moon_face.md) and
[`marker_marks`](../../__about/marker_marks.md).

THE FOUR STATIONS take the halo's place at a principal instant: new moon
is birth, first quarter youth, full moon the zenith of maturity, last
quarter age, and the Sun's four turning points are the same arc across
the year. An eclipse outranks a station — when both fall on one tick the
eclipse's own treatment is what shows.

THE CROSSING no longer dims anything. The translucent pass was retired
with the owner's cross on the proposals page; the three survivors read
`moon_transit_nearness` and either split the lane, shrink the Moon, or
let it occult the Earth outright.

### earth_region (module function)
`earth_region(latitude, longitude) -> str` — the Earth marker's art region:
the active location's continent (via `config.continents.
continent_from_coordinates`), except at extreme latitudes where the planet
honestly shows its pole. Both coordinates come straight from the day
context, so the region is recomputed every paint — no stale skin-baked
default.

## THE CALENDAR WHEELS DO NOT TURN (owner order 2026-08-13)

`earth_marker_angle` and `moon_marker_angle` take **no world offset**.
North is always the summer solstice and always the new moon, in every
world mode and at every solar rotation.

The line this draws: the world offset moves what the CLOCK draws — the
hour hand, the hour numbers, the jewels, the crown, the eclipse body at
its hour — because those are positions in TIME. The year wheel and the
moon cycle are positions in the CALENDAR, and a calendar does not swing
when the sky is redrawn. The inner minute band was already exempt for
exactly this reason; these two now join it.

The eclipse body deliberately does NOT join them: it is seated at the
hour of greatest eclipse, which is a position in time like the hour hand,
so it keeps riding the offset. Its collision test against the Earth still
works, because both sides of that test are SCREEN angles.

Both angles are single functions with a single caller path on purpose.
Two places in this module used to recompute them inline, and one of those
copies is why the Moon's cast shadow fell beside the Earth instead of on
it whenever the Almanac wheel was active — the shadow read the plain year
angle while the marker read the almanac one. Teeth:
`tests/test_year_marker.py`, plus
`tests/test_world_mode.py::test_earth_and_moon_keep_their_calendar_seats_at_night`,
which pins the DRAWN position through the compositor's own hit test.
