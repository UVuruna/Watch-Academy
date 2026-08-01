# CLI

**Script:** [Recolor CLI (script)](../__main__.py)

## Purpose

The command-line entry point for the metal transformer:

    python -m recolor IN.png --source bronze --target gold --out OUT.png
    python -m recolor --plates "UV/color transformer" --source bronze

The second form is the owner's verification loop: every `*.png` plate in
the given folder is rendered to every `--targets` metal (default
`gold,silver,bronze`), a labelled contact sheet is written beside the
variants, and a metrics table is printed — a change is judged on numbers,
never on vibes (Guideline #1). Pillow lives here and in `preview.py`
only; the algorithm core stays numpy-only for the Colorize SVG port.

## Connections

### Uses
- [Preview](preview.md) — `load_rgba`/`save_rgba` and `run()` (the
  `--plates` loop: recolor, save variants, write the contact sheet,
  return metrics rows)
- [Recipe](recipe.md) — `load()` reads `--presets` (default
  `presets/metals.json`)
- [Transform](transform.md) — `recolor()`, the single-file path

### Used by
- nothing in this project — invoked directly as `python -m recolor`

## Functions

### `_crop(text)`
Parses `--crop x0,y0,x1,y1` into a `(x0, y0, x1, y1)` int tuple, or
`None` when `--crop` is absent.

### `main(argv)`
Two modes, chosen by whether `--plates` is given:

- **single file** — requires `--target`; recolors `image` once via
  `transform.recolor()` and saves to `--out` (default
  `IMAGE - TARGET.png` beside the input)
- **plates** — every `*.png` under `--plates` (skipping existing
  `"- sheet"` contact sheets, filterable by substring with `--only`),
  rendered to every `--targets` metal via `preview.run()`; writes to
  `--out` (default `research/recolor_preview/`)

`--mask` selects `"chroma"` (art mixing metal with stone — the default)
or `"alpha"` (glyphs, every opaque pixel is metal). Returns exit code 1
if `--plates` matches no files, or if neither `--image`+`--target` nor
`--plates` is given.
