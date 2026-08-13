# Moon Band Layer

**Script:** [Moon Band Layer (script)](../moon_band.py) ·
**Flow:** [diagram](../__flow/moon_band.md)

## Purpose

THE MOON HORIZON BAND (owner verdict 2026-08-09): an arc on the dial's
inner tick circle showing WHEN the Moon stands above the horizon
today, in one of four owner-approved visual styles — "inverted" (the
BELT from the line out to the hour band inverted, owner correction
2026-08-10 — never the whole interior), "silver_thread" (THE DEFAULT —
a thin `MOON_SILVER` thread on the tick roots, filled dot at moonrise,
hollow dot at moonset, radially-seated diamond at culmination),
"ticks" (one discrete GRAY radial segment per degree spanning exactly
the plate's own tick zone, with NOTHING connecting them — no arc, no
thread) and "glow" (round-capped stroked arcs, a smooth bloom with
tapered ends).

Geometry comes entirely from `core.moon.moon_horizon_arcs` — never
re-derived here; one skin field carries the mode (`year_marker.
moon_band_mode`, gating whether this layer draws AT ALL — "horizon"
draws it, "dim_only"/"always_full" draw nothing; the old
`moon_hidden_alpha` below-horizon dimming is RETIRED per the owner's
2026-08-11 correction — the disc is always solid) and one carries
the style (`year_marker.moon_band_style`, read only in "horizon"
mode).

THE HOUR FRAME RULE (owner order 2026-08-13) — and the law it
REPLACED, kept here because the replaced one is a whole class of
mistake. This document used to carry an "INNER-BAND REGISTRATION
LAW": the tick art underneath never rotates with `ctx.world_offset`,
therefore neither may the band drawn on top of it. The premise is
true and the conclusion does not follow. What the band is painted ON
is a matter of geometry (THE LAST LINE — the radius that slices no
inner-ring element); what the band MEANS is a span of hours. The
owner's rule: **the outer circle shows HOURS, the inner circle shows
minutes, seconds and the calendar wheels — so everything drawing
something that happens in HOURS follows the OUTER circle, wherever it
is painted.** He found it on his own dial: the same day, the face
turned by the solar rotation, and the Moon's above-horizon hours
still sitting on the untuned seats, claiming the Moon was up over the
small hours of the morning.

So this layer now shifts every arc by `ctx.world_offset` through the
one door `core.moon.shift_arcs`, shared with `RingLayer._draw_band_
redress` (the per-degree redress of "inverted"/"ticks") and the
eclipse segment, so the band's three halves can never answer
differently. The redress still dresses the PLATE's own fixed 360
points — the span moves, the points do not, which is exactly what
"the Moon is up over THESE hours" means on a turned face.

The other side of the line, for contrast: the inner minute band, the
year wheel and the moon cycle stay put (`render.layers.year_marker.
earth_marker_angle`) — those are positions in the CALENDAR, not in
the day. The two teeth are twins: `tests/test_moon_band.py::test_the_
band_turns_with_the_hours_when_the_world_turns` and `tests/test_year_
marker.py::test_the_calendar_wheels_never_take_the_world_offset`.

THE TICK-ART HONESTY NOTE: the 360 day ticks are the owner's own baked
PNG art (`config.dial.RING_INNER_COMPOSITION`'s base plate), not
individually addressable primitives — there is no hook to recolor them
in place. "inverted" therefore fills the ticks' own measured belt
(`dial.RING_INNER_TICK_INNER_FRACTION` → `RING_INNER_TICK_OUTER_
FRACTION`) with `QPainter.CompositionMode_Difference` (a true RGB
invert of the art under it, not a guessed light color). "ticks" does
NOT approximate with a stroke — a connecting line reads as
"silver_thread" at a glance, which the owner's correction (2026-08-09)
forbids — it draws one discrete `MOON_BAND_TICK_GRAY` radial SEGMENT
per degree over the plate's own steps, with nothing connecting them.

## Connections

### Uses
- [Eclipse Style Door](../../__about/eclipse_style.md) — `resolve_eclipse_style`,
  asked before deciding whether to draw the band's copper segment
- [Moon (core)](../../../core/__about/moon.md) — `MoonArc`,
  `moon_horizon_arcs` — the layer's whole geometry input
- [Config (folder)](../../../config/___config.md) —
  `dial.RING_INNER_TICK_INNER_FRACTION`/`RING_INNER_TICK_OUTER_FRACTION`; `palette.MOON_SILVER`, `MOON_BAND_TICK_GRAY`, `MOON_BAND_LINE_EDGE`
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`

### Used by
- [Compositor](../../__about/compositor.md) — built between `"ring"` and
  `"year_marker"` in the default `z_order`, skipped outright unless
  `skin.show_moon` AND `year_marker.moon_band_mode == "horizon"`
- [Opacity (Watch Face)](../../../app/watch_face/__about/opacity.md) —
  the Moon Horizon Band mode/style picker calls the SAME `_draw_*`
  style methods for its preview tiles (`thumbs.moon_band_style_icon`/
  `moon_band_mode_icon`)

## Classes

### MoonBandLayer
`frame = "interior"`, `cadence = Cadence.DAILY` (the arc only changes
with the day's own moonrise/moonset, never per-tick).
- `paint()`: returns immediately unless `moon_band_mode == "horizon"`;
  otherwise draws every `MoonArc` `core.moon.moon_horizon_arcs` returns
  (one, or two on an up-across-midnight day) in the active style.
- `_draw_inverted`/`_draw_silver_thread`/`_draw_ticks`/`_draw_glow`:
  one method per style, each taking only `(painter, radius, arc)` — no
  `RenderContext` — so the SAME methods double as the Watch Face
  preview tiles' real-algorithm renderer.
- `draw_eclipse_segment(painter, radius, centre_deg, state)`: THE ECLIPSE ON
  THE BAND (owner placement 2026-08-10 — he moved that option off the
  dial circle and onto the line that shows when the Moon stands above
  the horizon). A copper segment with turquoise end caps, straddling
  the band at the eclipse's own hour, drawn whatever the band's own
  style is: the style says how the above-horizon arc looks, this is a
  separate mark laid over it. It runs whenever `paint()`'s call to
  [Eclipse Style Door](../../__about/eclipse_style.md)'s
  `resolve_eclipse_style("lunar", eclipse_lunar_style, band_available=True)`
  answers `"horizon_shadow"` or `"contact_marks"` — and for
  `horizon_shadow` it is the ONLY thing drawn — the Moon's disc is
  deliberately left untouched, because the point of the option is
  DURATION, which no halo and no darkened disc can show.
  `contact_marks` adds its own four contacts over it (below).

  IT READS THE TYPE (eclipse rework, owner order 2026-08-13). The
  segment used to be one identical copper bar for a total, a partial
  and a penumbral eclipse, so picking "horizon_shadow" collapsed the
  three lunar types into one picture. The shadow's DEPTH is now the
  bar's WEIGHT (`_ECLIPSE_SEGMENT_STATE_WEIGHT`): full thickness for
  totality, half for a partial, and a pale DASHED hairline for a
  penumbral eclipse — which also withholds the turquoise end caps, for
  the same reason the disc withholds them (`glow.ECLIPSE_STATE_FRINGE`:
  there is no darkened sky rim to show).

  THE HONEST APPROXIMATION: the catalog stores only the instant of
  greatest eclipse, never contact times, so the segment's width is the
  fixed `constants.ECLIPSE_BAND_DURATION_H` (3 h, a typical umbral
  span). The mark is exact about WHEN the eclipse peaks and only
  indicative about how long it runs; a catalog that one day carries
  contact times is what replaces that constant.

  IT READS `ctx.day.eclipses`, NEVER `ctx.tick`. This layer's cadence is
  DAILY, so `ctx.tick` is None while a cached daily pass composites
  (see [Context](../../__about/context.md)) — the first cut reached for
  the tick's active eclipse and took down three unrelated tests with a
  hard abort. The day's own list is also the RIGHT source: the band
  draws the whole day, so it must mark an eclipse that has not started
  yet and one already over, which is what showing duration means.

  A DEFECT THIS CLOSES, recorded because it nearly shipped: the style
  was wired through settings, spec and picker, and the Moon's disc was
  correctly left alone — but nothing drew on the band, so choosing it
  turned the eclipse's own mark off entirely. Every gate was green.
  What caught it was an independent grader opening the picker tile and
  reporting it as an empty circle.

- `draw_contact_marks(painter, radius, centre_deg, state)`: THE FOUR
  CONTACTS (owner ballot 2026-08-13, `contact_marks`). An ADDITION on
  top of `horizon_shadow`, never a replacement — the copper segment is
  still drawn and these bracket it — so it needs the same
  `moon_band_mode == "horizon"` and falls back to `"halo"` through the
  same door when the band is absent. What it draws: a thin dashed grey
  arc from **P1 to P4**, and a radial tick with a seated diamond at each
  of the four contacts — the umbral pair (**U1**, **U4**) longer, wider
  and copper, the penumbral pair shorter, thinner and grey. A PENUMBRAL
  eclipse draws only P1 and P4, because the Moon never enters the umbra
  and U1/U4 do not exist.

  **THESE ARE NOT OBSERVED CONTACT TIMES, and the code says so in those
  words.** The catalog stores only the instant of GREATEST eclipse (see
  `constants.ECLIPSE_BAND_DURATION_H`). The umbral pair therefore sit at
  half of that same documented 3 h approximation either side of the
  peak — the identical one the segment already draws, kept in the ONE
  place — and the penumbral pair at
  `constants.ECLIPSE_PENUMBRAL_SPAN_RATIO` (1.78) times that. The ratio
  is derived, not guessed a second time: the shadow radii at the Moon's
  distance are ~2.6 lunar radii for the umbra and ~4.6 for the penumbra,
  the Moon crosses both on the same near-straight track, so the two
  chords stand in that ratio (and it is the same 2.40/1.35 that
  `render.moon_face`'s own measured shadow fractions carry). Every one
  of the four lines is INDICATIVE; the marks are dashed for that reason,
  and a catalog that one day carries real contact times replaces
  `ECLIPSE_BAND_DURATION_H` and this ratio at once.

  WHY THE SPAN ARC EXISTS, recorded because the first two cuts failed
  without it: four thin lines are invisible at the scale the distinctness
  tooth measures (0.030 structure against the plain segment, then 0.079
  with the marks widened and diamonds added — both under the 0.20 floor,
  i.e. "the same picture"). What made it a picture of its own was not
  more ink but the thing this style KNOWS and `horizon_shadow` does not:
  the eclipse's WHOLE duration, P1 to P4, drawn as the dashed outer arc.
  That took the three lunar types to 0.229 / 0.238 / 0.248.

## Design Decisions
- THE LAST LINE (owner third round 2026-08-11): every band line sits
  on `dial.RING_INNER_CONTENT_INNER_FRACTION` — the inner side of the
  inner ring, where the five-minute strokes/arrows/numbers stop — so
  it slices NO inner-ring element. The Earth/Moon orbit is tangent to
  the SAME line per body, and the position-pointer arrow bridges from
  there across the band to the small ticks' tips, drawn behind its
  body and clipped out of the body's own circle.
- THE SPLIT ACROSS THE RING (owner z decree, repeat correction
  2026-08-11): the line/glow/thread parts paint in `MoonBandLayer`
  BELOW the ring; the per-degree tick redress of "inverted"/"ticks"
  paints INSIDE the ring layer (`RingLayer._draw_band_redress`,
  between the base plate and the band plates/jewels) — those two
  styles REPLACE the 360 points' own style, and every other ring
  element outranks them. The former `MoonBandTicksLayer` (a whole
  layer above the ring) is retired: it inverted the jewels and the
  big pointers with the belt.
- The four styles after the same correction rounds: "inverted" and
  "ticks" touch ONLY the background and the little points — one
  segment per degree, SPARING a one-degree shoulder around every
  FIFTEENTH degree (the big strokes stand every 15 deg on the
  MEASURED plate, not every 6th as first assumed — his slika 6/7);
  "glow" is round-capped stroked arcs (no filled-wedge banding, no
  flat chopped ends); the thread/dots/diamond wear a slate under-edge
  (`palette.MOON_BAND_LINE_EDGE`) so they read on light plates, and
  the culmination diamond is radially seated, longer than wide.
- Culmination is the arc's own midpoint (`core.moon.MoonArc`'s
  documented owner-approved approximation — no lunar-transit
  computation exists in `core.moon`).
- The style-drawing methods take only a painter/radius/arc so a
  thumbnail preview can call them directly on a bare canvas — the
  picker tiles are never a redrawn sketch of the real paint code.
