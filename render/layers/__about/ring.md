# Ring Layer

**Script:** [Ring Layer (script)](../ring.py) ·
**Flow:** [diagram](../__flow/ring.md)

## Purpose

Paints the composed ring — THE COMPOSITIONAL RING MODEL (owner decree
2026-08-05): the outer band + the inner band (always both, no single
monolithic plate and no procedural fallback any more), the preset's own
letters at the outer's empty fields, and the outer Great Seal crown text arc
("Crown Text" in the Watch Face window) — the letters and the crown text
stamped with a shared dark halo and a readable (never-upside-down)
rotation.

THE WORLD OFFSET ([World](../../../core/__about/world.md)): the letters and
the crown text are WORLD members — every seat takes `ctx.world_offset`
before its readable rotation is derived, so a glyph carried into the
lower half re-seats readably at its new angle instead of hanging upside
down. `0.0` in Geocentric leaves every seat exactly where it always was.

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
- `paint()`: unconditionally composes `_draw_bands()` then stamps
  `_draw_letter_art()` and `_draw_crown_text()` on top — there is no
  disk-presence gate and no procedural fallback any more.
- `_draw_bands()` (owner decree 2026-08-05, THE COMPOSITIONAL RING
  MODEL): composes the inner minute-track band (`RingSpec.inner_asset`)
  then the outer hour-tick band (`RingSpec.outer_asset`), each with its
  OWN tint (`ring_tint_inner` follows `ring_tint` when `None`).
- `_draw_ring_glyph()`: the ONE stamp shared by both the ring's six letters
  and the outer crown text (Rule #5) — resolves the letter's metal finish, draws
  a multi-sample dark halo from the gold master, rotates the glyph so it
  reads upright through the lower half of the ring (`angles.readable_rotation_deg`);
  `tint`/`opacity` are per-caller (`_draw_letter_art` passes
  `letter_tint`/1.0, `_draw_crown_text` its own `crown_text_tint`/`crown_text_alpha`).
  `draw_shadow=False` (SHADOW/SHINE round, owner ruling 2026-08-06) skips
  the halo entirely — the Dollar's Eye with Shine on already carries its
  own baked light. THE PIXELATION FIX (1440p owner bug, 2026-08-06): the
  halo's own sample count is no longer the fixed `RING_LETTER_SHADOW_
  SAMPLES` — `_shadow_sample_count()` grows it with the stamp circle's
  PIXEL radius (`ctx.dpr`-scaled) so adjacent stamps stay under
  `dial.RING_LETTER_SHADOW_MAX_GAP_PX` device pixels apart (the floor
  never drops below the original 8), and `_normalized_shadow_alpha()`
  renormalizes each stamp's opacity so the composited darkness matches
  the original look at the floor count.
- `_draw_letter_art()`: stamps every hour's letter art at its ring position,
  scaled by `ring_letter_scale` and the per-hour shine-enlarge multiplier;
  `RingSpec.letter_no_shadow` (per-hour) turns `draw_shadow` off for that seat.
- `_draw_crown_text()` ("Crown Text" in the Watch Face window, R-24/Phase-6-debt
  correction, owner 2026-08-05): stamps the preset's crown texts (e.g.
  ANNUIT COEPTIS / NOVUS ORDO SECLORUM) along two angularly-disjoint
  top/bottom arcs sharing one radius, scaled by `crown_text_scale` (on top of
  `ring_letter_scale`), tinted by `crown_text_tint` (follows `ring_tint` when
  `None`) and dimmed by `crown_text_alpha`; a no-op for presets with no crown text.
