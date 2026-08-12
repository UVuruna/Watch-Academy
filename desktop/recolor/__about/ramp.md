# Ramp

**Script:** [Ramp (script)](../ramp.py) · **Flow:** [diagram](../__flow/ramp.md)

## Purpose

Steps 8–9 of the pipeline: turn a mapped lightness into the target
metal's actual color, then roll the top of the range toward white so the
metal has a specular.

## Connections

### Uses
- [Color Space Math](space.md) — Oklab, hex parsing, smoothstep
- [Recipe](recipe.md) — a metal's `stops` and `specular`

### Used by
- [Transform](transform.md) — steps 8 and 9 (`sample` + `add_specular`)
- [Mask](mask.md) via [Transform](transform.md) — `body_color` supplies
  the hue the mask centers on
- [Preview](preview.md) — the same `body_color` for its metrics mask

## The law

**A metal is not a color — it is a tonal ramp with varying chroma.**
Chroma is HIGHEST in the body and FALLS toward both ends: shadows go dark
and slightly desaturated, highlights roll off to near-white.

The retired kernel used a flat `S = 1.0` for gold at every lightness.
Expanded, that is `(V, 0.748*V, 0)` — a two-channel image whose blue
channel is identically zero (measured: **52.59%** of the old gold plate's
pixels had B = 0), in which a white highlight is arithmetically
impossible. That single constant is the whole of the "garish, like a
highlighter" verdict.

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
  highlights instead of washing the whole upper half — a few near-white
  pixels against a saturated body.

## Functions

### `body_color(metal, position) -> (3,) linear rgb`
The metal's body color — its ramp sampled at `position` (a scalar), then
reshaped to `(3,)`.

### `sample(metal, lightness) -> linear rgb, same leading shape`
Maps `lightness` in [0,1] through `metal`'s ramp: stops sorted by
position, their hex colors converted to Oklab, each of L/a/b
piecewise-linearly interpolated at `lightness` via `np.interp`, then
converted back to linear RGB and clipped at 0 (never above, since Oklab
can round-trip slightly out of gamut at the low end).

### `add_specular(linear_rgb, lightness, specular) -> linear rgb`
No-op when `specular.strength <= 0`. Otherwise
`weight = smoothstep((lightness - start) / max(1 - start, 1e-6)) * strength`,
and the result is `linear_rgb` lerped toward white by `weight`.
