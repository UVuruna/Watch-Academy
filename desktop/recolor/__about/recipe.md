# Recipe

**Script:** [Recipe (script)](../recipe.py) · **Flow:** [diagram](../__flow/recipe.md)

## Purpose

Every number the transformer uses, loaded from `presets/metals.json`.
Nothing in this package hardcodes a threshold, ramp or gain (Rule #4),
and the JSON is DATA rather than code — a new metal costs one entry and
zero lines.

## Connections

### Uses
- nothing (stdlib only: `json`, `dataclasses`, `functools.lru_cache`,
  `pathlib`)

### Used by
- [Mask](mask.md), [Tone](tone.md), [Ramp](ramp.md),
  [Transform](transform.md), [Preview](preview.md), [CLI](__main__.md)

## The one-formula law

Owner decision, 2026-07-27: **the same `Tuning` block must serve every
image.** The transformer runs on the spot; the user never fine-tunes,
and there is no studio in this project (that belongs to Colorize SVG).

`Recipe.overrides` is the documented BACKUP the owner allowed IF a single
parameter set ever proves impossible for some plate. It is deliberately
empty in the shipped `presets/metals.json`. Any entry added to it is an
admission that the shared formula failed for that file and must say so
in its own comment.

## Classes

### `Specular`
The highlight roll-off.

#### Attributes
- `start: float` — where on the mapped lightness the near-white roll-off begins
- `strength: float` — how far toward white it goes

### `Metal`
One metal, described ONCE. The same entry serves both roles: as a SOURCE
it supplies the body color the mask centers on and the de-tint divides
out; as a TARGET it supplies the ramp and the tonal character. That is
what makes the transform source-agnostic.

#### Attributes
- `name: str` — the key it was loaded under
- `stops: tuple[(float, str), ...]` — `(position, "#RRGGBB")` pairs, the ramp
- `gamma: float` — the tonal midpoint shift
- `contrast: float` — the monotone S-curve amount
- `detail_gain: float` — how strongly the high-frequency relief rides on top
- `specular: Specular` — the roll-off

### `Tuning`
The shared algorithm parameters — identical for every image. See the
[schema tree](../__flow/recipe.md) for the full field list grouped by
pipeline stage (MASK / DE-TINT / SPLIT / ANCHOR / CHROMA DETAIL).

### `Recipe`

#### Attributes
- `tuning: Tuning` — the shared block
- `metals: dict[str, Metal]` — name -> `Metal`
- `overrides: dict[str, dict]` — file stem -> a partial tuning patch (the backup)

#### Methods
- `metal(name) -> Metal` — looks one up; raises `KeyError` naming the
  known metals when it is missing
- `for_image(stem) -> Recipe` — this recipe with any per-image backup
  applied; absent an entry — the normal case, and the goal — returns
  `self` unchanged

## Functions

### `load(path=PRESETS) -> Recipe`
Reads and parses the presets file. A malformed file raises: a silent
fallback to built-in numbers would hide exactly the kind of typo that
makes every plate look subtly wrong (Rule #1). `@lru_cache(maxsize=4)`:
the render path resolves a recolor per (file, metal, shade) and
re-parsing the presets for each would be pure waste; everything the
`Recipe` holds is frozen, so the shared cached instance cannot be
mutated by a caller.

## The metals shipped

`gold`, `silver`, `bronze`, `copper`, `brass`, `rose_gold`, `steel`,
`gunmetal`, `platinum`, `pewter`, `iron` — all eleven verified on the
owner's physician plate through the identical formula, no per-metal
special cases.
