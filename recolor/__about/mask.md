# Mask

**Script:** [Mask (script)](../mask.py) · **Flow:** [diagram](../__flow/mask.md)

## Purpose

Decide, per pixel, how much of it is the SOURCE metal — step 1 of the
pipeline. Everything the mask does not claim is composited back
unchanged, which is how the gray stone and engraved field of a badge
medallion survive a metal change untouched.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, hue distance, smoothstep
- [Recipe](recipe.md) — `Tuning`, the window and ramp bounds

### Used by
- [Transform](transform.md) — step 1
- [Preview](preview.md) — the pixel set every metrics row is measured over

## Two modes, one function

The retired code carried two near-copies of the entire recolor
(`_metal_swapped` for badges, `_letter_recolored` for ring letters) that
differed ONLY in how the mask was computed. Here that is one parameter
(Rule #5):

| mode | for | rule |
|------|-----|------|
| `"chroma"` | badge medallions — metal relief mixed with GRAY stone and engravings | a soft hue window around the source metal's own body hue, times a saturation ramp |
| `"alpha"` | ring letters and numerals | every opaque pixel simply IS metal; a glyph mixes no stone, so there is nothing to detect |

Any other `mode` string raises `ValueError`.

## Design Decisions

### Saturation as a RATIO, not absolute chroma

Oklab chroma scales with lightness, so an absolute chroma threshold cuts
the shadows off exactly the way HSV hue noise does. Taking chroma OVER
lightness (clamped by `_BLACK_FLOOR = 1e-4`) restores the
scale-invariance HSV's `S = (max-min)/max` happened to have, without
HSV's shadow noise.

### Verified against the retired mask

Measured on the owner's bronze physician plate, with
`saturation_ramp = (0.020, 0.050)` and a 34deg half-window:

- keeps **100.00%** of the opaque pixels the old HSV mask claimed
- adds **2.55%** of the image — dark metal in the shadows that the HSV
  mask dropped, the Oklab-over-HSV improvement showing up
- claims **0.03%** of the neutral stone (i.e. it does not)
- correctly excludes the fully TRANSPARENT pixels that made up 27.9% of
  the old mask's claim and were being recolored for nothing

The owner's 2026-07-12 decree "the mask stays" is therefore honored: the
same pixels change, only the arithmetic finding them is sound in the
dark now.

## Functions

### `metal_weight(linear_rgb, alpha, body_linear, tuning, mode) -> weight`
The per-pixel weight in [0,1]. Transparent pixels (`alpha <= 0`) are
always 0.
