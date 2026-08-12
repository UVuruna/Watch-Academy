# Letter Bake

**Script:** [Letter Bake (script)](../letter_bake.py) · **Flow:** [diagram](../__flow/letter_bake.md)

## Purpose

**The letter finishes ship pre-rendered. A launch reads them; it does
not compute them.**

Owner order, 2026-08-12: the whole plate library must be rendered into
every standard metal and every thematic colour AT SETUP, into a folder
the program reads from — *"a ne da ga renderujemo svaki put pri
pokretanju aplikacije"* <!-- lang-ok: the owner's own instruction, quoted -->
— because by now the program uses those letters constantly, and uses
all of them. There is no installer on this machine yet, so the bake is
performed here and committed:
[Make Letter Bake](../../setup/__about/make_letter_bake.md).

What it replaces: every letter finish used to be derived at RUNTIME
from the gold master by `AssetCache._recolored` — an oklab + guided
box filter + specular ramp pass in numpy, per plate, per metal, per
shade. The retirement of the 76 pre-rendered `_silver.png`/`_bronze.png`
files in 0.14.4xx (owner 2026-07-19, *"bolje crtati na licu mesta nego
15MB fajlova"*) <!-- lang-ok: the owner's own ruling, quoted --> was
right for a library of a few jewels on one dial. It stopped being right
when THE ONE PLATE LAW (2026-08-07) routed the JEWELS, the whole CROWN,
the DUALS and the flash through the same library: the same recolors are
now paid on every cold cache, and a cold cache is what a new install,
a new machine and a `raster_cache` sweep all are.

The bake covers **57 plates × 23 ramps** — latin, greek, numerals,
symbols and emblems, in every ramp the transformer offers (the three
metals with all their shades, plus the five ring theme colours and the
rest of `constants.METAL_SHADE_NAMES["thematic"]`).

## The key cannot drift

The baked file is named by **`asset_recolor.letter_cache_name`** — the
SAME function that names the runtime cache entry, and the only one that
does (Rule #5). So a baked name embeds exactly what a runtime name
embeds:

```
<16-hex path stamp>_<12-hex content fingerprint>_letter_<metal>_<shade>_v<VERSION>.png
```

That is not a convention this module has to keep in sync with anything
— it is the same string, from the same call. Three consequences fall
out for free, with no manifest, no version file and nothing to
maintain:

- **Re-draw a plate** → its content fingerprint changes → the baked
  name no longer matches what the runtime asks for → the bake is
  ignored and the finish is derived live, exactly as before the bake
  existed. Re-run the baker to restore the fast path.
- **Bump `METAL_SWAP_VERSION`** (the recolor math changed) → same
  thing, for every plate at once. A stale bake can never paint a
  wrong-looking letter onto the dial.
- **Delete the folder** → the program is only slower.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.assets_dir`

### Used by
- [Asset Recolor](asset_recolor.md) — `jewel_metal_path` consults
  `baked_file` before recording a recipe in the lazy ledger; a hit
  means the dial draws the real finish on its FIRST paint, with no
  gold stand-in and no background drain at all
- [Make Letter Bake](../../setup/__about/make_letter_bake.md) — writes
  what this reads

## Functions

### `bake_dir() -> Path`
`assets/_baked/letters/`. Under `assets/` because it SHIPS (an
installed program has no write access to its own program folder and
must not need any); under a leading underscore because it is derived,
not art — the same convention `assets/_state/` already uses, and the
reason the art-reachability guard names it in `RESOLVED_ELSEWHERE`
rather than the staging ledger: it is not unwired art, it is not art.

### `baked_file(name) -> Path | None`
The baked file for a runtime cache NAME, or None. One dict lookup: the
folder is listed ONCE per process (`os.listdir`, a single directory
read of ~1,300 entries) and never stat-ed per call — this sits on the
path-resolution hot path, which is exactly where `art_file`'s own
positive-results cache was born for the same reason.

### `refresh() -> None`
Re-list the folder. For the baker itself and for tests; the running
program has no reason to, since the bake does not change under it.

## Design Decisions

- **Named by the runtime key, not by a readable stem.** A folder of
  `A_gold.png` would be pleasant to browse and would silently paint
  last month's letters after an art change. The unreadable name is the
  safety property; the baker prints a readable index instead.
- **Consulted BEFORE the ledger, not after.** A hit must skip the
  `_PENDING_VARIANTS` recording entirely — a recipe recorded is a
  recipe the warm thread will dutifully rebuild, which would give back
  precisely the work the bake exists to remove.
- **Listed once, never stat-ed.** `Path.exists()` per resolution is
  what `config.paths`' own comment measured at ~30 filesystem stats per
  second per watch, forever. One `listdir` costs less than a second of
  that.
- **No manifest.** See above: the name IS the manifest. Every scheme
  that stores "which version was baked" somewhere else is a scheme that
  can disagree with itself.
