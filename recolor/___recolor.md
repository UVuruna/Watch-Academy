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

### `recipe.py` — The Tunables
Dataclasses for the whole algorithm plus the per-metal entries, loaded
from `presets/metals.json`. NOTHING in this package hardcodes a number
(Rule #4); the JSON is the single source of truth and is data, not code,
so new metals need no new lines.

### `space.py` — Color Space Math
sRGB <-> linear light, linear RGB <-> Oklab, hex parsing. Pure numpy,
vectorized, no per-pixel Python.

### `filters.py` — Edge-Preserving Split Primitive
O(1)-per-pixel box filter (cumulative sums) and the guided filter built
on it. This is what separates form from detail without the halos a plain
Gaussian would leave along every engraving line. No scipy, no OpenCV —
numpy only, so the package ports cleanly.

### `mask.py` — Which Pixels Are Metal
The Oklab hue window + chroma ramp that tells bronze relief from gray
stone, and the whole-glyph alpha mode for ring letters. One function,
two modes — the two old kernels differed ONLY here (Rule #5).

### `tone.py` — De-tint, Split, Anchor, Curve
Steps 2–7: the neutral relief map and everything that shapes it before
a color is ever chosen.

### `ramp.py` — Gradient Map And Specular
Steps 8–9: sampling a metal's ramp at a lightness, in Oklab so the
interpolation never shifts hue or muddies the midtones.

### `transform.py` — The Orchestrator
`recolor(rgba, source, target, recipe)` — the one public entry that runs
the pipeline end to end. numpy in, numpy out; no Qt, no file I/O.

### `preview.py` — The Verification Harness
Builds the contact sheet AND the metrics table (clipping %, per-channel
means, masked-region detail range) for a set of source images. Every
change to this package is judged on numbers, never on vibes.

### `__main__.py` — CLI
`python -m recolor IN.png --source bronze --target gold --out OUT.png`
and `python -m recolor --preview` for the owner's test plates. PIL lives
here and in `preview.py` only — the algorithm core stays numpy-only.

## Connections

### Uses
- nothing in this project — the package is deliberately standalone

### Used by
- [Assets](../render/assets.md) — the badge/letter metal swap adapts
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
