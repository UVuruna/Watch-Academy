# Moon Band Layer

**Script:** [Moon Band Layer (script)](../moon_band.py) ·
**Flow:** [diagram](../__flow/moon_band.md)

## Purpose

THE MOON HORIZON BAND (owner verdict 2026-08-09): an arc on the dial's
inner tick circle showing WHEN the Moon stands above the horizon
today, in one of four owner-approved visual styles — "inverted"
(darker fill + inverted ticks inside the arc), "silver_thread" (THE
DEFAULT — a thin `MOON_SILVER` thread, filled dot at moonrise, hollow
dot at moonset, diamond at culmination), "ticks" (TICKS-ONLY, owner
correction 2026-08-09: one discrete `MOON_SILVER` radial segment per
degree, slightly longer than the plate's own ticks, with NOTHING
connecting them — no arc, no thread, so it reads distinctly from
"silver_thread" at a glance) and "glow" (layered translucent arcs,
brightest near culmination).

Geometry comes entirely from `core.moon.moon_horizon_arcs` — never
re-derived here; one skin field carries the mode (`year_marker.
moon_band_mode`, gating whether this layer draws AT ALL — "horizon"
draws it, "dim_only"/"always_full" draw nothing, `moon_hidden_alpha`
dimming keeps working independently of this switch) and one carries
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
in place. "inverted" is approximated with a stroked arc drawn AT the
tick radius using `QPainter.CompositionMode_Difference` (a true RGB
invert of whatever sits under the stroke, not a guessed light color).
"ticks" does NOT approximate with a stroke — a connecting line reads
as "silver_thread" at a glance, which the owner's correction (2026-08-09)
forbids — it draws one discrete `MOON_SILVER` radial SEGMENT per
degree instead, matching the baked art's own 1-per-degree spacing,
with nothing connecting them.

## Connections

### Uses
- [Moon (core)](../../../core/__about/moon.md) — `MoonArc`,
  `moon_horizon_arcs` — the layer's whole geometry input
- [Config (folder)](../../../config/___config.md) —
  `dial.MINUTES_RADIUS_FRACTION`; `palette.MOON_SILVER`
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_pie`

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

## Design Decisions
- The band sits on `dial.MINUTES_RADIUS_FRACTION` (the inner tick
  band's own live radius), never a second guessed radius.
- Culmination is the arc's own midpoint (`core.moon.MoonArc`'s
  documented owner-approved approximation — no lunar-transit
  computation exists in `core.moon`).
- The style-drawing methods take only a painter/radius/arc so a
  thumbnail preview can call them directly on a bare canvas — the
  picker tiles are never a redrawn sketch of the real paint code.
