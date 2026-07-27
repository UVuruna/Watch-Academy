# Color Space Math

**Script:** [Color Space Math (script)](space.py)

## Purpose

sRGB <-> linear light, linear RGB <-> Oklab, hex parsing and the
smoothstep ramp — the arithmetic every other module in the package
builds on.

## Connections

### Uses
- nothing (numpy only, by design)

### Used by
- [Mask](mask.md), [Tone](tone.md), [Ramp](ramp.md),
  [Transform](transform.md), [Preview](preview.md)

## Design Decisions

### Why linear light for the mixing

The retired kernel did all of its mixing on gamma-encoded sRGB values.
Multiplying a gamma-encoded number by a gain is not a brightness change
— it is a brightness change plus an uncontrolled contrast change, which
is a large part of why one global gain behaved so unpredictably from
plate to plate. Blending, gain and gradient interpolation all happen in
LINEAR light here; only the final encode returns to sRGB.

### Why Oklab for the decisions

- **Lightness.** `V = max(R,G,B)` is not a lightness at all: on warm
  bronze art it is the RED channel (measured mean R 0.3721 vs mean V
  0.3740 on the owner's plate), so two thirds of the image is discarded
  before anything begins. Oklab's `L` is perceptually uniform and reads
  all three channels.
- **Hue.** HSV hue is `(max-min)` divided by a vanishing denominator, so
  in the deep shadows of a relief it is numeric noise — a mask built on
  it drops exactly the dark metal it should keep. Oklab's hue angle
  stays meaningful down to near-black.
- **Interpolation.** Between two ramp stops Oklab moves in a straight
  perceptual line: no muddy midtones (linear RGB's failure), no hue
  drift (sRGB's failure).

## Functions

### `srgb_to_linear(srgb)` / `linear_to_srgb(linear)`
The IEC 61966-2-1 transfer function, both directions, clamped to [0,1].

### `luminance(linear_rgb)`
Rec.709 relative luminance Y of a (..., 3) linear array.

### `linear_to_oklab(linear_rgb)` / `oklab_to_linear(lab)`
Ottosson's Oklab, via the LMS cube-root stage. The forward direction
clamps LMS at zero before the cube root: the de-tint step can push a
channel slightly negative, and a graceful clip there beats a NaN
propagating through the whole plate.

### `oklab_chroma_hue(lab)`
Chroma (>= 0) and hue in degrees [0, 360).

### `hue_distance(hue, center)`
Shortest angular distance in degrees [0, 180] — the mask's window is
circular, so a plain subtraction would break across 0/360.

### `hex_to_linear(value)`
`"#RRGGBB"` -> a (3,) linear array. How ramp stops enter the pipeline.

### `smoothstep(x)`
The Hermite ramp, clamped outside its edges. Every soft threshold in the
package (mask edges, specular roll-off, the tonal S-curve) is built from
this one function.
