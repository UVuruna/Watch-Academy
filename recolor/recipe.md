# Recipe

**Script:** [Recipe (script)](recipe.py)

## Purpose

Every number the transformer uses, loaded from `presets/metals.json`.
Nothing in this package hardcodes a threshold, ramp or gain (Rule #4),
and the JSON is DATA rather than code — a new metal costs one entry and
zero lines.

## Connections

### Uses
- nothing (stdlib only)

### Used by
- [Mask](mask.md), [Tone](tone.md), [Ramp](ramp.md),
  [Transform](transform.md), [Preview](preview.md)

## The one-formula law

Owner decision, 2026-07-27: **the same `tuning` block must serve every
image.** The transformer runs on the spot; the user never fine-tunes,
and there is no studio in this project (that belongs to Colorize SVG).

`Recipe.overrides` is the documented BACKUP the owner allowed IF a single
parameter set ever proves impossible for some plate. It is deliberately
empty. Any entry added to it is an admission that the shared formula
failed for that file and must say so in its own comment.

## Classes

### Specular
The highlight roll-off.

#### Attributes
- `start`: where on the mapped lightness the near-white roll-off begins
- `strength`: how far toward white it goes

### Metal
One metal, described ONCE. The same entry serves both roles: as a SOURCE
it supplies the body color the mask centers on and the de-tint divides
out; as a TARGET it supplies the ramp and the tonal character. That is
what makes the transform source-agnostic.

#### Attributes
- `name`: the key it was loaded under
- `stops`: `(position, "#RRGGBB")` pairs — the ramp
- `gamma`: the tonal midpoint shift
- `contrast`: the monotone S-curve amount
- `detail_gain`: how strongly the high-frequency relief rides on top
- `specular`: the roll-off

### Tuning
The shared algorithm parameters — identical for every image.

#### Attributes
- `hue_half_width_deg`, `hue_soft_deg`: the mask's hue window
- `saturation_ramp`: Oklab chroma-over-lightness bounds, below which a
  pixel is neutral stone rather than metal
- `body_position`: where along a metal's ramp its body color is sampled
- `detint_strength`: how completely the source metal's cast is removed
- `detail_radius_fraction`, `detail_radius_min`: the guided filter's
  window as a fraction of the smaller image side, so a 256px letter and
  a 2048px medallion separate the same physical scale of detail
- `detail_epsilon`: the variance below which structure counts as texture
  rather than as an edge
- `detail_headroom`: how close to black/white the form may come before
  the detail riding on it is eased down
- `anchor_percentiles`, `anchor_scale_range`: the robust window that maps
  to [0,1] and the bound on the resulting stretch
- `chroma_detail_gain`: how much residual chroma texture is re-injected
  as lightness

### Recipe

#### Attributes
- `tuning`: the shared block
- `metals`: name -> `Metal`
- `overrides`: file stem -> a partial tuning patch (the backup)

#### Methods
- `metal(name)`: look one up, naming the known metals when it is missing
- `for_image(stem)`: this recipe with any per-image backup applied;
  absent an entry — the normal case, and the goal — returns itself

## Functions

### `load(path)`
Read the presets. A malformed file raises: a silent fallback to built-in
numbers would hide exactly the kind of typo that makes every plate look
subtly wrong (Rule #1).

## The metals shipped

`gold`, `silver`, `bronze`, `copper`, `brass`, `rose_gold`, `steel`,
`gunmetal`, `platinum`, `pewter`, `iron` — all eleven verified on the
owner's physician plate through the identical formula, no per-metal
special cases.
