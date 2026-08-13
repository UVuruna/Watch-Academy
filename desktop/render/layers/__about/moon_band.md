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

THE INNER-BAND REGISTRATION LAW: the tick band this layer paints over
NEVER rotates with `ctx.world_offset`, in any world mode (`render.
layers.numerals`'s own "ledger §2" — the inner band's plate is keyed
on a fixed `offset_deg=0.0`). This layer therefore never applies
`ctx.world_offset` either — applying it would slide the band out of
registration with the fixed tick art underneath it.

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
  separate mark laid over it. It runs only while
  `eclipse_lunar_style == "horizon_shadow"`, and it is the ONLY thing
  that style draws — the Moon's disc is deliberately left untouched,
  because the point of the option is DURATION, which no halo and no
  darkened disc can show.

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
