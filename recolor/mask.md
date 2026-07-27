# Mask

**Script:** [Mask (script)](mask.py)

## Purpose

Decide, per pixel, how much of it is the SOURCE metal — step 1 of the
pipeline. Everything the mask does not claim is composited back
unchanged, which is how the gray stone and engraved field of a badge
medallion survive a metal change untouched.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, hue distance, smoothstep
- [Recipe](recipe.md) — the window and ramp bounds

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

## Algorithm (pseudocode)

```
IF mode is "alpha":
    RETURN 1 wherever alpha > 0, else 0

lab        = OKLAB of the linear pixel
saturation = chroma / max(lightness, floor)
body_hue   = OKLAB hue of the SOURCE metal's body color
            (its ramp sampled at tuning.body_position)

distance   = shortest angular distance from the pixel's hue to body_hue
hue_weight = 1 - SMOOTHSTEP((distance - half_width) / soft)
sat_weight = SMOOTHSTEP((saturation - low) / (high - low))

weight = hue_weight * sat_weight * (alpha > 0)
```

## Design Decisions

### Saturation as a RATIO, not absolute chroma

Oklab chroma scales with lightness, so an absolute chroma threshold cuts
the shadows off exactly the way HSV hue noise does. Taking chroma OVER
lightness restores the scale-invariance that HSV's `S = (max-min)/max`
happened to have, without HSV's shadow noise.

### Verified against the retired mask

Measured on the owner's bronze physician plate, with
`saturation_ramp = (0.020, 0.050)` and a 34 deg half-window:

- keeps **100.00%** of the opaque pixels the old HSV mask claimed
- adds **2.55%** of the image — dark metal in the shadows that the HSV
  mask dropped, which is the Oklab-over-HSV improvement showing up
- claims **0.03%** of the neutral stone (i.e. it does not)
- correctly excludes the fully TRANSPARENT pixels that made up 27.9% of
  the old mask's claim and were being recolored for nothing

The owner's 2026-07-12 decree "the mask stays" is therefore honored: the
same pixels change, only the arithmetic finding them is sound in the
dark now.

## Functions

### `metal_weight(linear_rgb, alpha, body_linear, tuning, mode)`
The per-pixel weight in [0,1]. Transparent pixels are always 0.
