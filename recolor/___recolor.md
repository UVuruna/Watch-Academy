# recolor/

The **metal transformer** — a self-contained, Qt-free, numpy-only mini
library that turns one drawn metal master into ANY other metal, live,
from rules instead of from files (Rule #19).

It exists because the previous recolor kernel (`render.assets.
AssetCache._recolor_to_shade`, retired by this package) replaced every
masked pixel's hue AND saturation with a flat constant and scaled its
value by one global gain. That is mathematically a two-channel image:
gold `classic` = `HSV(44.9°, S=1.0, V)` expands to `(V, 0.748·V, 0)` —
the blue channel is identically **zero**, so every detail carried by
chroma is destroyed before anything else happens, no highlight can ever
roll off to white (hence "garish"), and the 1.90 gain ceiling clipped
~12% of a medallion to one flat maximum. Silver, at `S=0`, reduced to
`max(R,G,B)`, which for warm bronze art is **the red channel alone**
(measured on the owner's plate: mean R 0.3721 vs mean V 0.3740).

## The law this package follows

A metal is not a COLOR — it is a **tonal ramp with varying chroma**:
dark and slightly desaturated in shadow, most chromatic in the body,
rolling off to near-white at the specular. Every metal is described by
ONE such ramp; the algorithm is identical for all of them, and the
transform is **source-metal agnostic** — gold masters become bronze and
silver (ring letters and numerals), bronze masters become gold and
silver (badge medallions), through the same code path.

## Pipeline

```
INPUT rgba (sRGB)
  0  decode         sRGB -> linear light (all mixing happens in linear)
  1  mask           which pixels are metal (Oklab hue window + chroma
                    ramp, or the whole opaque glyph)
  2  de-tint        measure the SOURCE metal's own chromaticity from the
                    masked pixels and divide it out -> a neutral relief
                    that uses all THREE channels, never max(R,G,B)
  3  lightness      Oklab L (perceptual), not HSV V
  4  split          guided filter -> L_base (form) + L_detail (engraving
                    lines, book drawings, hair, drapery)
  5  anchor         L_base linearly rescaled between robust percentiles
                    of the MASKED region only, stretch factor bounded
  6  curve          per-metal gamma + monotone S-curve (contrast)
  7  detail back    L_detail re-added at the anchored scale
  8  gradient map   L -> the target metal's ramp, interpolated in Oklab
  9  specular       top of the range rolled toward white
 10  composite      source*(1-mask) + metal*mask, linear -> sRGB, alpha
                    untouched
OUTPUT rgba (sRGB)
```

### Step 5 is NOT the reverted percentile remap

A previous attempt (`013b5ca`, reverted the same day) remapped every
pixel by its **rank** in the source histogram — a non-monotone-in-shape
equalization that flattened all relief. Step 5 here is a **linear
rescale between two anchor values**: strictly monotone, ratio-order
preserving, and it never moves two pixels' relationship except by one
shared scale and offset. The relief survives by construction; only the
window it lands in changes. The bounded `anchor_scale_range` stops a
low-contrast source from being stretched into a poster.

## Files

| File | Tier | One line |
|------|------|----------|
| `transform.py` | Algorithmic | the orchestrator — `recolor()`, the one public entry — [about](__about/transform.md) · [flow](__flow/transform.md) |
| `mask.py` | Algorithmic | step 1 — which pixels are metal (Oklab hue window + chroma ramp, or alpha) — [about](__about/mask.md) · [flow](__flow/mask.md) |
| `tone.py` | Algorithmic | steps 2–7 — de-tint, split, anchor, curve — [about](__about/tone.md) · [flow](__flow/tone.md) |
| `ramp.py` | Algorithmic | steps 8–9 — gradient map and specular — [about](__about/ramp.md) · [flow](__flow/ramp.md) |
| `space.py` | Algorithmic | sRGB/linear/Oklab color math — [about](__about/space.md) · [flow](__flow/space.md) |
| `filters.py` | Algorithmic | the guided-filter form/detail split primitive — [about](__about/filters.md) · [flow](__flow/filters.md) |
| `recipe.py` | Algorithmic | the tunables — dataclasses loaded from `presets/metals.json` — [about](__about/recipe.md) · [flow](__flow/recipe.md) |
| `preview.py` | Standard | verification harness — contact sheet + metrics table — [about](__about/preview.md) |
| `__main__.py` | Standard | CLI — `python -m recolor` — [about](__about/__main__.md) |
| `__init__.py` | Trivial | re-exports `Metal`, `Recipe`, `Specular`, `Tuning`, `load`, `recolor` |

`presets/metals.json` is the data file `recipe.py` loads — not a Python
module, so it carries no tier of its own; its schema is the
[Recipe flow diagram](__flow/recipe.md)'s visual tree.

## Connections

### Uses
- nothing in this project — the package is deliberately standalone

### Used by
- [Assets](../render/__about/assets.md) — the badge/letter metal swap adapts
  QImage to numpy and calls `transform.recolor`

## Design Decisions

- **Qt-free and dependency-light on purpose.** This package is the seed
  of the Colorize SVG port; anything Qt or scipy in the core would have
  to be unwritten later. `tests/test_purity.py` guards it.
- **One formula for every image.** The owner's requirement is that the
  algorithm just works, with no per-image fine-tuning. `presets/
  metals.json` may carry per-image overrides as a documented BACKUP if a
  single parameter set ever proves impossible — that escape hatch is
  deliberately last, not first.
- **All metals, not three.** Adding copper, brass, rose gold, steel,
  gunmetal, platinum, pewter or iron costs one JSON entry and zero code,
  so they are all present from day one.
- **`recipe.py`'s data model reused beyond metals.** Since the
  ENLARGE/THEMATIC round (owner 2026-07-27) the ring's THEMATIC finish
  colors — `cross_red`, `cross_blue`, `dollar_green`, `moon_indigo`,
  `templar_black` — are ordinary colored ramps in `presets/metals.json`,
  one entry each, zero code (see
  [Config (folder)](../config/___config.md)'s `RING_THEMATIC_SHADES`).
