# Ramp

**Script:** [Ramp (script)](ramp.py)

## Purpose

Steps 8–9: turn a mapped lightness into the target metal's actual color,
then roll the top of the range toward white so the metal has a specular.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, hex parsing, smoothstep
- [Recipe](recipe.md) — a metal's stops and specular

### Used by
- [Transform](transform.md) — steps 8 and 9
- [Mask](mask.md) via [Transform](transform.md) — `body_color` supplies
  the hue the mask centers on
- [Preview](preview.md) — the same body color for its metrics mask

## The law

**A metal is not a color — it is a tonal ramp with varying chroma.**
Chroma is HIGHEST in the body and FALLS toward both ends: shadows go dark
and slightly desaturated, highlights roll off to near-white.

The retired kernel used a flat `S = 1.0` for gold at every lightness.
Expanded, that is `(V, 0.748*V, 0)` — a two-channel image whose blue
channel is identically zero (measured: **52.59%** of the old gold plate's
pixels had B = 0), and in which a white highlight is arithmetically
impossible. That single constant is the whole of the "garish, like a
highlighter" verdict.

## Algorithm (pseudocode)

```
SAMPLE(metal, lightness):
    positions, colors = the metal's stops, sorted
    labs              = OKLAB of each stop color (converted from hex via linear)
    FOR each of L, a, b:
        interpolate PIECEWISE-LINEAR at `lightness` over (positions, labs)
    RETURN linear RGB of the interpolated Oklab

BODY COLOR(metal, position) = SAMPLE(metal, position)
    -- the ONE point that serves as the mask's hue center and the
       de-tint's reference, so a metal is described exactly once

ADD SPECULAR(rgb, lightness, specular):
    weight = SMOOTHSTEP((lightness - start) / (1 - start)) * strength
    RETURN LERP(rgb, white, weight)
```

## Design Decisions

- **Interpolation in Oklab.** Linear RGB interpolation goes muddy through
  the midtones; sRGB interpolation drifts the hue. Oklab moves in a
  straight perceptual line between stops.
- **A metal is described exactly once.** The mask's hue center and the
  de-tint's reference are both `body_color`, the ramp sampled at
  `tuning.body_position` — there is no second place to keep in sync.
- **`np.interp` clamps outside the stop range**, which is exactly the
  wanted behavior at both ends of the ramp.
- **The specular is confined by a smoothstep** so it lands on genuine
  highlights instead of washing the whole upper half. It is what gives
  the metal its "sjaj": a few near-white pixels against a saturated
  body.

## Functions

### `body_color(metal, position)`
The metal's body color as linear RGB — its ramp sampled at `position`.

### `sample(metal, lightness)`
Map lightness in [0,1] through the ramp -> linear RGB.

### `add_specular(linear_rgb, lightness, specular)`
Roll the top of the range toward white.
