# Tone

**Script:** [Tone (script)](../tone.py) · **Flow:** [diagram](../__flow/tone.md)

## Purpose

Steps 2–7 of the pipeline: turn the source plate into a single **mapped
lightness** channel in [0,1] that `ramp.py` then paints. No color is
chosen here at all. Everything a metal change must not destroy lives in
this module.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, luminance
- [Filters](filters.md) — the guided form/detail split, twice (the
  relief itself, and the optional chroma-detail texture)
- [Recipe](recipe.md) — `Tuning`, every bound and gain

### Used by
- [Transform](transform.md) — the tonal half of the pipeline (`relief`)

## Design Decisions

### De-tint is what makes the transform source-agnostic

Ring letters and numerals are drawn in GOLD and become bronze and
silver; badge medallions are drawn in BRONZE and become gold and silver.
One code path serves both because the source metal's own cast is
measured from its own masked pixels and divided out before anything
else. The reference is normalized to unit luminance first (`cast =
reference / luminance(reference)`), so the step removes the CAST and
leaves overall brightness alone.

What survives is an honest neutral relief built from all three channels
— against `max(R,G,B)`, which on warm art is the red channel alone.

### The anchor is NOT the reverted percentile remap

A previous attempt (`013b5ca`, reverted the same day the owner saw it)
replaced each pixel's value by its **rank** in the source histogram. That
is a non-uniform remap, and it flattened every relief into a detail-free
wash — "nemamo kontrast, sve je svetlo, izgubili smo sve moguće
detalje".

The anchor here is **one multiply and one offset shared by every
pixel**: `anchor()` rescales `base` so its `tuning.anchor_percentiles`
(e.g. 1st/99th) land at 0 and 1, pivoting on the window's MIDPOINT so a
clamped stretch stays centered rather than sliding the whole plate dark
or bright. Strictly monotone; every light/dark relationship survives
exactly. What it fixes is where the old multiply came FROM: the retired
kernel chased a fixed reference value with a mean, which on dark
medallion art pinned the gain at its 1.90 ceiling and clipped **11.87%**
of the plate to one flat maximum. Robust percentiles cannot do that, and
`tuning.anchor_scale_range` additionally bounds the stretch so a
low-contrast source is never blown into a poster.

### Why the detail is eased near the ends

Detail rides on top of the curve at the same `scale` the form was
stretched by, so its relative strength is preserved. Within
`tuning.detail_headroom` of pure black or white a share of it could only
be clipped away, so `relief()` eases it down to a quarter strength there
(`ease = 0.25 + 0.75 * clip(min(curved, 1-curved) / headroom, 0, 1)`)
instead of throwing it at a wall.

### Chroma detail

What chroma SURVIVES the de-tint is not the metal — it is ink on a page,
patina, painted marks. On an achromatic target such as silver those
would vanish entirely, since the target has no chroma left to carry
them. `_chroma_texture` high-passes the residual saturation
(`chroma / lightness`) via `guided_split` and `relief()` re-injects it as
a small DARKENING (`result -= chroma_detail_gain * texture`), which is
how such marks read on real metal. It is signed and high-pass, so a
large evenly-colored area is untouched: only local chromatic contrast
against its own surroundings counts.

## Functions

### `detint(linear_rgb, weight, strength) -> linear rgb`
Divide out the source metal's measured cast, blended by `strength`.
No-op (returns `linear_rgb` unchanged) when the mask's total weight is
0.

### `anchor(base, weight, tuning) -> (anchored, scale)`
The bounded, monotone rescale described above. Falls back to
`clip(base, 0, 1), 1.0` when no pixel's weight exceeds `_STAT_FLOOR =
0.5`.

### `shape(lightness, gamma, contrast) -> lightness`
Gamma then a monotone S-curve (`curved + contrast * (smoothstep(curved)
- curved)`) that fixes 0 and 1 exactly and stays monotone for `contrast`
in [-2, 1]. This is where a metal's character lives: silver, steel and
gunmetal need far more contrast than gold to read as metal rather than
as paint.

### `relief(linear_rgb, weight, tuning, gamma, contrast, detail_gain) -> lightness`
The whole tonal half, end to end: detint -> Oklab lightness -> guided
split -> anchor -> shape -> detail re-added (eased near the ends) ->
optional chroma-detail subtraction -> clipped to [0,1].

### `_chroma_texture(neutral, lab, radius, tuning) -> texture`
The high-frequency part of the residual chroma-over-lightness ratio.
