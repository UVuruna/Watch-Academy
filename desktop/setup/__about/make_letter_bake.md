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
([Build Rules](../../../../../rules/BUILD.md) — this project has none), so
this script IS the setup step for now and its output is committed
alongside the assets. When the installer arrives it runs the same
script; nothing about the format changes.

## The matrix

| | |
|---|---|
| plates | **57** — `assets/instrument/letters/` : latin 26, greek 10, numerals 10, symbols 7, emblems 4 |
| finishes | **17** — every `(metal, shade)` pair in `defaults.EAGER_BAKED_SHADES` |
| files | **969**, lossless WebP |

The eager finishes are gold (5 shades), bronze (3), silver (3) and six
thematic colours: `cross_red`, `cross_blue`, `dollar_green`,
`moon_indigo`, `templar_black`, `ceramic`.

## What is NOT baked, and why that is safe

The first version of this script baked all **34** pairs of
`METAL_SHADES` into 1,938 PNGs — 302 MB, committed. The owner's ruling
of 2026-08-12 halved both numbers: bake what is actually used, and let
a custom ring's exotic ramp (copper, brass, rose gold, steel, pewter,
iron) derive the first time somebody asks for one.

Two facts make that free rather than a compromise:

- **Most of the dropped pairs are duplicate pixels.**
  `thematic/gold` and `gold/classic` are the same ramp; so are
  `thematic/silver`, `thematic/bronze*` and the four `gold_*` thematic
  aliases. They exist as separate keys only because the runtime cache
  key carries the `(metal, shade)` pair rather than the ramp — and that
  design stays, because teaching this script the ramp table would be
  exactly the second source of truth the naming design exists to avoid.
  The bake simply stops paying for the duplication *eagerly*.
- **A miss is the ordinary path, not a failure.** `jewel_metal_path`
  records the recipe, `render.art_warm` builds it on the background
  thread, and the dial draws the gold master meanwhile — precisely the
  behaviour that existed before any bake did. Slower once, never wrong.

**Lossless WebP, not PNG** (same decree): identical pixels, roughly
half the bytes. Lossless and not the art bakery's q90, because these
are the final drawn glyphs of every word the program says — the art
bakery's plates get shrunk to 800 px by the dial, these do not.
`raster_store.atomic_save` takes the encoding from the extension, which
`letter_cache_name` owns.

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
