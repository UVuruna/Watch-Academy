# Preview

**Script:** [Preview (script)](../preview.py)

## Purpose

The verification harness — a contact sheet AND a metrics table for a set
of plates, so every change to this package is judged on NUMBERS and not
on vibes (Guideline #1). This is a DEV tool: Pillow lives here and in
`__main__.py` only, never in the algorithm core, which stays numpy-only
for the Colorize SVG port.

## Connections

### Uses
- [Transform](transform.md) — the pipeline under test
- [Mask](mask.md) — `source_weight()`'s own metal mask
- [Filters](filters.md) — `guided_split()` for the `detail_energy` metric
- [Color Space Math](space.md) — `srgb_to_linear`, `linear_to_oklab`
- [Recipe](recipe.md) — the presets under test

### Used by
- [CLI](__main__.md) — `python -m recolor --plates FOLDER`

## The metrics, and what each one caught

Every row is measured over the **source plate's own mask** (`weight`,
computed once by `source_weight`), passed unchanged to every variant, so
all rows describe the same set of pixels and are honestly comparable.

| column | meaning | the failure it names |
|--------|---------|----------------------|
| `mask` | share of the image the mask claims (`coverage`) | mask drift |
| `mean R/G/B` | per-channel means over the mask | a channel being annihilated |
| `B=0` | share of masked pixels with a dead blue channel (`dead_blue`) | the old gold's **52.59%** |
| `blown` | share at or above 254/255 (`clipped`) | the old gold's **11.87%**, silver's **8.17%** |
| `crush` | share at or below 1/255 (`crushed`) | over-darkening |
| `L mean` / `L sd` | Oklab lightness mean and spread over the mask | flatness |
| `detail` | mean absolute high-frequency energy over the mask (`detail_energy`) | relief loss |
| `crop` | p95−p05 lightness range inside a `--crop` window | the owner's circled book page |

`detail` is comparable BETWEEN transformer runs, but not directly against
the source: a metal's ramp deliberately occupies a narrower lightness
band than [0,1], which lowers absolute high-frequency energy without
losing any relief. `crop` is the honest source-vs-output number. When
the mask claims fewer than half the pixels the metrics fall back to
every pixel with `alpha > 0` (`measure`'s `selected` guard), so a broken
mask still produces a readable row instead of an empty one.

## Functions

### `measure(label, rgba, weight, recipe, crop=None) -> Metrics`
One metrics row — a frozen `Metrics` dataclass (`label`, `coverage`,
`mean_rgb`, `dead_blue`, `clipped`, `crushed`, `mean_lightness`,
`lightness_spread`, `detail_energy`, `crop_range`) with a `.row()`
formatter matching `HEADER`.

### `load_rgba(path)` / `save_rgba(rgba, path)`
PNG <-> `(H, W, 4)` float64 in [0,1], sRGB-encoded.

### `source_weight(rgba, source, recipe, mask_mode)`
The source plate's own metal mask — the pixel set every row of the
metrics table is measured over.

### `contact_sheet(cells, path)`
Every variant of one plate, side by side, labelled, on the sheet's own
dark background (`BACKGROUND = (24, 24, 28)`) so transparency does not
read as white.

### `run(plate, source, targets, recipe, out_dir, mask_mode="chroma", crop=None) -> list[Metrics]`
Recolor one plate to every target, write the variants and the contact
sheet, return the metrics rows with the source row first.
