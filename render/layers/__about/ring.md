# Ring Layer

**Script:** [Ring Layer (script)](../ring.py) ·
**Flow:** [diagram](../__flow/ring.md)

## Purpose

Paints the outer ring: the donut face (art asset or a procedural fallback),
the 24 hour ticks, the 24h numerals with any per-skin letters swapped in,
the 5-minute numbers along the inner edge, and — when the skin carries
letter art — the owner's gold/silver/bronze letter glyphs and the outer
Great Seal motto arc, both stamped with a shared dark halo and a
readable (never-upside-down) rotation.

`Cadence.STATIC`: nothing on this layer depends on the day or the live
tick — only the skin (letters, tint, saturation) and the dial's size/DPI —
so it rebuilds only on a skin/size/DPI change. Not `hover_variable`.

## Connections

### Uses
- [Asset Recolor](../../__about/asset_recolor.md) — `letter_metal_file` (gold master →
  silver/bronze finish, disk-cached)
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_pixmap_centered`

### Used by
- [Compositor](../../__about/compositor.md) — fourth layer in the default `z_order`,
  stacked into the cached STATIC/DAILY composite

## Classes

### RingLayer
`cadence = Cadence.STATIC`.
- `paint()`: with a ring art asset, draws the tinted/saturated plate then
  `_draw_letter_art()` and `_draw_motto()` on top (untinted); with no asset,
  falls back to a procedural donut — ticks, bold numerals per hour (or a
  letter where the skin defines one), and 5-minute numbers.
- `_draw_ring_glyph()`: the ONE stamp shared by both the ring's six letters
  and the outer motto (Rule #5) — resolves the letter's metal finish, draws
  a multi-sample dark halo from the gold master, rotates the glyph so it
  reads upright through the lower half of the ring (`angles.readable_rotation_deg`).
- `_draw_letter_art()`: stamps every hour's letter art at its ring position,
  scaled by `ring_letter_scale` and the per-hour shine-enlarge multiplier.
- `_draw_motto()`: stamps the preset's motto texts (e.g. ANNUIT COEPTIS /
  NOVUS ORDO SECLORUM) along two angularly-disjoint top/bottom arcs sharing
  one radius; a no-op for presets with no motto.
