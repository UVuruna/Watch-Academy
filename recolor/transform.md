# Transform

**Script:** [Transform (script)](transform.py)

## Purpose

The ONE public entry that runs the whole pipeline. numpy in, numpy out;
no Qt, no file I/O, no wall clock.

## Connections

### Uses
- [Mask](mask.md) — step 1
- [Tone](tone.md) — steps 2–7
- [Ramp](ramp.md) — steps 8–9
- [Color Space Math](space.md) — the sRGB encode/decode at both ends
- [Recipe](recipe.md) — everything tunable

### Used by
- [Preview](preview.md) — the verification harness
- [Assets](../render/assets.md) — the badge/letter metal swap, which
  adapts QImage to numpy around this call

## Algorithm (pseudocode)

```
RECOLOR(rgba, source, target, recipe, mask_mode, image_key):
    recipe = recipe with any per-image BACKUP override applied
    linear = sRGB DECODE of rgba's color channels
    alpha  = rgba's alpha, carried through untouched

    weight    = METAL WEIGHT(linear, alpha,
                             BODY COLOR(source metal), tuning, mask_mode)
    lightness = RELIEF(linear, weight, tuning,
                       target.gamma, target.contrast, target.detail_gain)
    painted   = ADD SPECULAR(SAMPLE(target metal, lightness),
                             lightness, target.specular)

    blended = linear * (1 - weight) + painted * weight
    RETURN sRGB ENCODE(blended) with the original alpha
```

## Parameters

- `rgba`: `(H, W, 4)` float in [0,1], sRGB-encoded
- `source`: the metal the plate was DRAWN in
- `target`: the metal to render
- `mask_mode`: `"chroma"` for art that mixes metal with neutral stone
  (badge medallions), `"alpha"` for art where every opaque pixel is metal
  (ring letters and numerals)
- `image_key`: the source file's stem, consulted ONLY for the per-image
  backup overrides that the shared formula is meant to make unnecessary

## Design Decisions

### Source-agnostic by construction

Ring letters go gold -> bronze/silver; badges go bronze -> gold/silver.
Both are the same call with different arguments, because the de-tint step
measures and removes whatever cast the source happens to carry before a
target is ever consulted. Any of the eleven metals can be either side.

### The composite happens in linear light

The unmasked pixels (gray stone, engraved field) are blended against the
painted metal in linear light, so the soft mask edge is a real optical
crossfade rather than the contrast artifact a gamma-encoded lerp leaves.

### Alpha is never touched

Transparency is carried straight through. The retired kernel recolored
transparent pixels too — 27.9% of what its mask claimed — which was
wasted work that could surface as fringing under any later resample.
