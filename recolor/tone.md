# Tone

**Script:** [Tone (script)](tone.py)

## Purpose

Steps 2–7: turn the source plate into a single **mapped lightness**
channel in [0,1] that the ramp then paints. No color is chosen here at
all. Everything a metal change must not destroy lives in this module.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, luminance, smoothstep
- [Filters](filters.md) — the guided form/detail split
- [Recipe](recipe.md) — every bound and gain

### Used by
- [Transform](transform.md) — the tonal half of the pipeline

## Algorithm (pseudocode)

```
DE-TINT (the source-agnostic step)
    reference = mean linear RGB of the MASKED pixels
    cast      = reference / luminance(reference)      (unit luminance)
    neutral   = pixel / cast                          (blended by strength)

LIGHTNESS
    L = OKLAB L of the neutral pixel

SPLIT
    radius       = detail_radius_fraction * the smaller image side
    base, detail = GUIDED SPLIT of L at that radius

ANCHOR
    low, high = the 1st and 99th percentile of base over MASKED pixels
    scale     = CLAMP(1 / (high - low), anchor_scale_range)
    midpoint  = (low + high) / 2
    anchored  = CLAMP(0.5 + (base - midpoint) * scale, 0, 1)

CURVE
    curved = anchored ^ gamma
    curved = curved + contrast * (SMOOTHSTEP(curved) - curved)

DETAIL BACK
    ease   = 0.25 + 0.75 * CLAMP(min(curved, 1-curved) / headroom, 0, 1)
    result = curved + detail * scale * detail_gain * ease

CHROMA DETAIL (optional)
    result = result - chroma_detail_gain * HIGH-PASS(chroma / L)

RETURN CLAMP(result, 0, 1)
```

## Design Decisions

### De-tint is what makes the transform source-agnostic

Ring letters and numerals are drawn in GOLD and become bronze and
silver; badge medallions are drawn in BRONZE and become gold and silver.
One code path serves both because the source metal's own cast is
measured from its own masked pixels and divided out before anything
else. The reference is normalized to unit luminance first, so the step
removes the CAST and leaves overall brightness alone.

What survives is an honest neutral relief built from all three channels
— against `max(R,G,B)`, which on warm art is the red channel alone.

### The anchor is NOT the reverted percentile remap

A previous attempt (`013b5ca`, reverted the same day the owner saw it)
replaced each pixel's value by its **rank** in the source histogram. That
is a non-uniform remap, and it flattened every relief into a detail-free
wash — "nemamo kontrast, sve je svetlo, izgubili smo sve moguće
detalje".

The anchor here is **one multiply and one offset shared by every pixel**.
Strictly monotone; every light/dark relationship survives exactly, just
as the straight multiply it replaces did. What it fixes is where that
multiply came FROM: the old one chased a fixed `reference_value` with a
mean, which on dark medallion art pinned the gain at its 1.90 ceiling
and clipped **11.87%** of the plate to one flat maximum. Robust
percentiles cannot do that, and `anchor_scale_range` additionally stops
a low-contrast source from being stretched into a poster.

It pivots on the window's MIDPOINT rather than its low end, so a clamped
stretch stays centered instead of sliding the whole plate dark or bright.

### Why the detail is eased near the ends

Detail rides on top of the curve at the same scale the form was
stretched by, so its relative strength is preserved. Within
`detail_headroom` of pure black or white a share of it could only be
clipped away, so it is eased down to a quarter strength there instead of
being thrown at a wall — visible relief in the deepest shadow beats a
mathematically pure addition that the clamp eats.

### Chroma detail

What chroma SURVIVES the de-tint is not the metal — it is ink on a page,
patina, painted marks. On an achromatic target such as silver those
would vanish entirely, since the target has no chroma left to carry
them. The high-pass of the residual saturation is therefore re-injected
as a small DARKENING, which is how such marks read on real metal. It is
signed and high-pass, so a large evenly-colored area is untouched: only
local chromatic contrast against its own surroundings counts.

## Functions

### `detint(linear_rgb, weight, strength)`
Divide out the source metal's measured cast. Returns linear RGB.

### `anchor(base, weight, tuning)`
Returns `(anchored, scale)` — the bounded, monotone rescale.

### `shape(lightness, gamma, contrast)`
Gamma then a monotone S-curve that fixes 0 and 1 exactly. This is where
a metal's character lives: silver, steel and gunmetal need far more
contrast than gold to read as metal rather than as paint.

### `relief(linear_rgb, weight, tuning, gamma, contrast, detail_gain)`
The whole tonal half, end to end. Returns the mapped lightness.
