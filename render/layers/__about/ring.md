# Ring Layer

**Script:** [Ring Layer (script)](../ring.py) ·
**Flow:** [diagram](../__flow/ring.md)

## Purpose

Paints the composed ring — THE COMPOSITIONAL RING MODEL (owner decree
2026-08-05), sharpened by THE FIDELITY RULING (owner correction
2026-08-06, [the ledger](../../../research/ring_rework.md) §2). FIVE
things, drawn in ONE ordered pass, and the ORDER is the composition:

| # | Drawn | Source |
|---|---|---|
| 1 | the INNER base — 360 day hairlines, 60 minute strokes, the quarter/octa ARROWS | HIS ART, blitted (`RING_INNER_COMPOSITION[variant]["base"]`) |
| 2 | the live INNER numbers | computed, into the seats step 1 leaves empty |
| 3 | the OUTER band — the metal, its black rim AND the hour numerals | computed whole |
| 4 | the preset's LETTER art | HIS ART, on the seats step 3 left bare |
| 5 | the CROWN TEXT arc outside the band | HIS ART |

Nothing is stacked on content it can collide with, which is the ruling's
first law. **The outer plate PNG is no longer blitted at all** — it
already carries printed numerals, and a live numeral drawn over them is
the defect the ruling was issued for (an Ω with a printed 0 beneath it).
The INNER plate blitted here is the NUMBERLESS twin its variant composes
from, not the file the user picked: `seconds.png` IS `simple_point.png`
with the numbers set into it, so blitting the base and composing the
numbers live reproduces his plate exactly — the number even OCCLUDES the
inner half of the five-minute stroke it stands on, leaving the outer stub
showing, which is what his own numbered plates do.

The letters and the crown text are stamped with a shared dark halo and a
readable (never-upside-down) rotation.

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
- [Asset Recolor](../../__about/asset_recolor.md) — `jewel_metal_file` (gold master →
  silver/bronze finish, disk-cached)
- [Numeral Bands](../../__about/numeral_bands.md) — the two computed band plates
- [Numeral Layers](numerals.md) — `band_spec`, the shared cache key
- [Numerals](../../../core/__about/numerals.md) — `inner_composition`, the
  numberless base each variant composes from
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_pixmap_centered`

### Used by
- [Compositor](../../__about/compositor.md) — fourth layer in the default `z_order`,
  stacked into the cached STATIC/DAILY composite

## Classes

### RingLayer
`cadence = Cadence.STATIC`.
- `paint()`: unconditionally composes `_draw_bands()` then stamps
  `_draw_jewels()` and `_draw_crown_text()` on top — there is no
  disk-presence gate and no procedural fallback any more.
- `_draw_bands()` (THE FIDELITY RULING, owner correction 2026-08-06):
  blits the inner variant's NUMBERLESS base art, then the COMPUTED inner
  number plate, then the COMPUTED outer band — in that order, so the
  letters `paint()` stamps next have the metal under them and nothing
  over them. `RingSpec.outer_asset` is no longer drawn (it still names
  the preset's outer, which `render.asset_variants.ring_face_color`
  samples); `ring_tint_inner` follows `ring_tint` when `None`, and both
  computed plates answer the tint/saturation sliders through their own
  `BandSpec` ([Numeral Layers](numerals.md)).
- `_blit_band()`: the shared blit for both computed plates (Rule #5) —
  one `drawImage` of a plate built at most once per settings change.
- `_draw_ring_glyph()`: the ONE stamp shared by both the ring's six letters
  and the outer crown text (Rule #5) — resolves the letter's metal finish, draws
  a multi-sample dark halo from the gold master, rotates the glyph so it
  reads upright through the lower half of the ring
  (`angles.readable_rotation_deg` — since 2026-08-07 THE ONE SEATING LAW,
  an alias of `core.numerals.seat_rotation`, so a jewel standing on one of
  the four SQUARE angles stands UPRIGHT exactly like the numeral beside it;
  before that these were two forks of one law and The One's 18 and 6 lay
  sideways. Templar's crosses at 90/270 are symmetric, so this is
  invisible there; LOOP's Π at 16h is not on a square angle and does not
  move);
  `tint`/`opacity` are per-caller (`_draw_jewels` passes
  `jewels_tint`/1.0, `_draw_crown_text` its own `crown_text_tint`/`crown_text_alpha`).
  `draw_shadow=False` (SHADOW/SHINE round, owner ruling 2026-08-06) skips
  the halo entirely — the Dollar's Eye with Shine on already carries its
  own baked light. THE PIXELATION FIX (1440p owner bug, 2026-08-06): the
  halo's own sample count is no longer the fixed `RING_JEWEL_SHADOW_
  SAMPLES` — `shadow_sample_count()` grows it with the stamp circle's
  PIXEL radius (`ctx.dpr`-scaled) so adjacent stamps stay under
  `dial.RING_JEWEL_SHADOW_MAX_GAP_PX` device pixels apart (the floor
  never drops below the original 8), and `normalized_shadow_alpha()`
  renormalizes each stamp's opacity so the composited darkness matches
  the original look at the floor count. Both functions moved to
  `render.numeral_bands` (Crown Polish round, owner correction
  2026-08-06) — the live crown's own baked glyph tiles now stamp the
  SAME shadow, and `numeral_bands` is the shared home both this layer
  and the crown builder can import without a cycle (this layer already
  imports FROM `numeral_bands`, never the other way).
- `_draw_jewels()`: stamps every hour's jewel art at its ring position,
  scaled by `ring_jewels_scale` and the per-hour shine-enlarge multiplier;
  `RingSpec.jewel_no_shadow` (per-hour) turns `draw_shadow` off for that seat.
- `_draw_crown_text()` ("Crown Text" in the Watch Face window, R-24/Phase-6-debt
  correction, owner 2026-08-05): stamps the preset's crown texts (e.g.
  ANNUIT COEPTIS / NOVUS ORDO SECLORUM) along two angularly-disjoint
  top/bottom arcs sharing one radius, scaled by `crown_text_scale` ALONE
  (THE DECOUPLED SCALES, owner defect 2026-08-07: `ring_jewels_scale` used
  to multiply this too, so the Jewels slider grew the crown — each term
  now scales its own family, and since both default to 1.0 the folded
  constant is exactly 1.0 and no default dial changed), tinted by
  `crown_text_tint` (follows `ring_tint` when `None`) and dimmed by
  `crown_text_alpha`; a no-op for presets with no crown text. The LIVE
  crown ([Numerals](numerals.md)) answers `crown_text_scale` through the
  same expression, so one slider sizes every crown arc on the dial.
