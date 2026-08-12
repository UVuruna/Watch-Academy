# Make Letter Bake

**Script:** [Make Letter Bake (script)](../make_letter_bake.py) · **Flow:** [diagram](../__flow/make_letter_bake.md)

## Purpose

The SETUP step that pre-renders the letter library into every finish
the program can ask for, so that no launch ever derives one.

Owner order, 2026-08-12: render all the letters into the standard
metals and the thematic colours at setup, into a folder the program
reads from. His reason, and it is the right one: the plate library
stopped being a handful of ring jewels the day THE ONE PLATE LAW routed
the JEWELS, the whole CROWN, the DUALS and the Fast-Travel flash
through it. The program now uses those letters constantly and uses all
of them, so deriving them per install — a numpy oklab pass with a
guided box filter and a specular ramp, per plate, per metal, per shade
— is work that should have been done once, by us, before shipping.

There is no build pipeline on this machine yet
([Ship Rules](../../../../../rules/SHIP.md) — this project has none), so
this script IS the setup step for now and its output is committed
alongside the assets. When the installer arrives it runs the same
script; nothing about the format changes.

## The matrix

| | |
|---|---|
| plates | **57** — `assets/instrument/letters/` : latin 26, greek 10, numerals 10, symbols 7, emblems 4 |
| finishes | **34** — every `(metal, shade)` pair in `defaults.METAL_SHADES` |
| files | **1,938** |

The finishes are gold (5 shades), bronze (3), silver (3) and the
THEMATIC pseudo-metal (23: the five ring theme colours plus every
remaining transformer ramp — copper, brass, rose gold, steel, pewter,
iron and the metal ramps by their own names).

Several pairs share one ramp — `gold/classic` and `thematic/gold` are
both the `gold` ramp, and their pixels are identical. They are baked
TWICE anyway, and deliberately: the runtime cache key carries the
`(metal, shade)` pair, not the ramp, so collapsing them here would
require this script to know the ramp table — a second source of truth,
which is the one thing the bake's naming design exists to avoid. The
duplication costs a few MB and buys the guarantee that what is written
is exactly what is asked for.

## Connections

### Uses
- [Asset Recolor](../../render/__about/asset_recolor.md) —
  `letter_cache_name` (THE naming function, shared with the runtime)
  and `bake_letter_finish` (the same recolor kernel `ensure_variant`
  runs, with the shade named explicitly instead of read from a watch's
  display context)
- [Letter Bake](../../render/__about/letter_bake.md) — `bake_dir`, the
  destination it writes and the program reads
- [Config (folder)](../../config/___config.md) — `defaults.METAL_SHADES`
  (the matrix), `paths.assets_dir`

### Used by
- nobody at runtime — a setup/maintenance script, like
  [Make Deep Time](make_deep_time.md) and
  [Make Observatory](make_observatory.md)

## Running it

```
python -m setup.make_letter_bake            # bake what is missing
python -m setup.make_letter_bake --force    # rebuild everything
python -m setup.make_letter_bake --list     # report the matrix, no work
```

**When to re-run:** after adding a plate to the library, after
re-drawing one, and after bumping `defaults.METAL_SWAP_VERSION`. In all
three cases the program stays CORRECT without a re-run — the stale
files simply stop matching and the finishes derive live again — it just
stops being fast. `tests/test_letter_bake.py` fails when coverage
drops, so a forgotten re-run is caught rather than merely regretted.

## Design Decisions

- **Plates are read off DISK, not from a glyph table.** The bake must
  cover what EXISTS, including a plate dropped in since the last time
  any table was edited. A table would have re-created, in this script,
  precisely the "art landed and nothing knows about it" failure THE
  THEME COMPLETION LAW was written for.
- **Missing files only, unless `--force`.** Adding one plate costs one
  plate.
- **One unbakeable plate is skipped, loudly, never fatal.** A partial
  bake is a partially fast program; an aborted bake is no bake at all.
- **`QGuiApplication`, not `QApplication`.** No widgets are involved
  and it works headless.
