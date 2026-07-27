# Preview

**Script:** [Preview (script)](preview.py)

## Purpose

The verification harness — a contact sheet AND a metrics table for a set
of plates, so every change to this package is judged on NUMBERS and not
on vibes (Guideline #1). This is a DEV tool: Pillow lives here and in the
CLI only, never in the algorithm core, which stays numpy-only for the
Colorize SVG port.

## Connections

### Uses
- [Transform](transform.md) — the pipeline under test
- [Mask](mask.md), [Ramp](ramp.md), [Filters](filters.md),
  [Color Space Math](space.md) — for the metrics
- [Recipe](recipe.md) — the presets under test

### Used by
- [Recolor CLI](__main__.py) — `python -m recolor --plates FOLDER`

## The metrics, and what each one caught

Every row is measured over the **source plate's own mask**, passed
unchanged to every variant, so all rows describe the same set of pixels
and are honestly comparable.

| column | meaning | the failure it names |
|--------|---------|----------------------|
| `mask` | share of the image the mask claims | mask drift |
| `mean R/G/B` | per-channel means over the mask | a channel being annihilated |
| `B=0` | share of masked pixels with a dead blue channel | the old gold's **52.59%** |
| `blown` | share at or above 254/255 | the old gold's **11.87%**, silver's **8.17%** |
| `crush` | share at or below 1/255 | over-darkening |
| `L mean` / `L sd` | Oklab lightness mean and spread | flatness |
| `detail` | mean high-frequency energy over the mask | relief loss |
| `crop` | p95−p05 lightness range inside a named window | the owner's circled book page |

`detail` is comparable BETWEEN transformer runs, but not directly against
the source: a metal's ramp deliberately occupies a narrower lightness
band than [0,1], which lowers absolute high-frequency energy without
losing any relief. `crop` is the honest source-vs-output number.

## Functions

### `measure(label, rgba, weight, recipe, crop)`
One metrics row.

### `load_rgba(path)` / `save_rgba(rgba, path)`
PNG <-> `(H, W, 4)` float in [0,1].

### `source_weight(rgba, source, recipe, mask_mode)`
The source plate's own metal mask — the pixel set every row is measured
over.

### `contact_sheet(cells, path)`
Every variant of one plate, side by side, labelled, on the sheet's own
dark background so transparency does not read as white.

### `run(plate, source, targets, recipe, out_dir, mask_mode, crop)`
Recolor one plate to every target, write the variants and the contact
sheet, return the metrics rows with the source row first.
