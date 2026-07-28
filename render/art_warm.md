# Art Warm

**Script:** [Art Warm (script)](art_warm.py)

## Purpose

Build the dial's derived art (the ring letters' metal finishes) **off the
GUI thread**, so a paint never waits on a recolor.

Owner decree 2026-07-28, after the slow-start measurement. On a cold
raster cache a watch's first paint ran 15 metal recolors *inside*
`paintEvent` — 3.6 s of numpy per watch, ~15 s for the owner's three
watches, with nothing on screen for the whole of it. The ruling:

> FIRST DEFAULT — recolor u pozadini. Kad završi prikaže.

So the paint stopped recoloring. [Asset Recolor](asset_recolor.md)'s
`letter_metal_file` hands back the **gold master** whenever the derived
finish is not yet on disk and records the recipe in the lazy ledger; this
module drains that ledger and calls back so the dial repaints in its real
metal.

## Measured

| | Cold first paint | Recolors on the GUI thread |
|---|---|---|
| Before | 4.20 + 4.79 + 5.67 = **14.78 s** | 45 |
| After | 1.08 + 0.16 + 0.16 = **1.46 s** | **0** |

The recolors did not get cheaper — 49 of them still cost ~13.7 s. They
moved off the path the user is waiting on. (The second and third watches
dropping to 0.16 s is the shared
[Asset Cache](assets.md) `shared_cache`: they reuse what the first
decoded instead of each holding their own copy.)

## Algorithm

```
REPEAT
    jobs <- every recorded recipe whose file is missing,
            minus the ones already attempted this run
    IF no jobs -> DONE
    FOR EACH job:
        IF the caller says stop -> RETURN what was built
        mark attempted
        build the pixels and write them to the raster cache
        tell the caller a dial can repaint now
```

Two details that are load-bearing:

- **Repeat, don't single-pass.** The GUI thread keeps recording new
  recipes while the drain runs — a paint that reaches art the previous
  pass had not seen. One pass would leave the dial half-dressed.
- **Attempt each job at most once.** A cache write can fail (full disk,
  locked file); the recipe then stays "pending" forever. Without the
  attempted set the repeat above would be an endless loop instead of a
  dial that simply keeps its master art.

`on_ready` fires after **each** build, not once at the end, so the metal
arrives letter by letter instead of all at once when the batch finishes.

## Connections

### Uses
- [Asset Recolor](asset_recolor.md) — the pending ledger (`pending_art`,
  `ensure_variant`) and the recipes it holds
- [Profiling (folder)](../config/___config.md) — the "Dial art warmup" timer

### Used by
- [Warm](../app/warm.md) — phase 1 of the one process-wide warm

## Design Decisions

**Why a ledger and not a queue object.** The ledger already existed for
the Encyclopedia's badge variants (owner order 2026-07-26, the same class
of bug one layer up). Letters joined it rather than growing a second
mechanism (Rule #5) — the recipe simply widened to carry the source
metal, the mask mode and the shade.

**Why the shade rides the recipe.** A recipe is recorded under one
watch's display context and built later on a thread that has none. Re-
reading the shade at build time would silently recolor to the shipped
default — the exact leak
[Display Context](../config/___config.md) exists to end.

**Why QImage end to end.** QPixmap must never be touched off the GUI
thread (the R1b threading law).
