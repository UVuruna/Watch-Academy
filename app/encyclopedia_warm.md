# Encyclopedia Warm

**Script:** [Encyclopedia Warm (script)](encyclopedia_warm.py)

## Purpose

Background pre-materialization of EVERYTHING the Encyclopedia can ever
show (owner order 2026-07-26: "entering the Encyclopedia must never
block the main thread — we have a background loading system, it should
cover this"): the derived metal variants (gold/silver recolors), the
eight live-rendered Moon phase plates, and the disk-cached downscales
the gallery cards and reader pages decode from. Runs once per app
start on the controller's existing warm thread, right after the dial's
own working-set warmup — a no-op once every derived file exists.

The other half of the fix lives in the modules it warms: the
Encyclopedia's topic table now records ONLY paths
(`metal_variant_path`), and a page's first display materializes just
its own few images (`ensure_variant`) — so even a user who opens the
Encyclopedia BEFORE this warm has finished never waits for more than
the open page.

## Connections

### Uses
- [Encyclopedia (subfolder)](encyclopedia/___encyclopedia.md) — `_topics()` is the inventory: every
  topic's card icon and every entry's look/image paths, walked here
  exactly as the dialog would resolve them
- [Asset Recolor](../render/asset_recolor.md) — `ensure_variant` /
  `variant_pending` materialize the recorded gold/silver recolors
  (QImage end to end — the R1b threading law)
- [Asset Variants](../render/asset_variants.md) —
  `scaled_variant_file` builds the decode-ceiling downscales the dialog
  then reads with `build=False`
- [Defaults](../config/defaults.md) — the two decode ceilings
  (`ENCYCLOPEDIA_CARD_ICON_DECODE_PX`,
  `ENCYCLOPEDIA_READER_DECODE_CEILING_PX`)

### Used by
- [App Controller](controller.md) — `_warm_caches` chains this after
  the working-set warmup and the hover-article sweep, on the same
  daemon thread

## Functions

### `warm_encyclopedia(progress=None, should_stop=None)`

Pseudocode (Rule #21 — language-neutral):

```
topics = build the Encyclopedia topic table (paths only, no pixels)
jobs   = every topic's card icon (gallery first — the first screen),
         then every entry's look/image paths, DEDUPLICATED
FOR EACH job:
    IF should_stop() → return
    resolve the path through the art-source fallback
    IF it is a recorded, still-missing metal variant → build it now
    IF the file exists and is wider than its decode ceiling
        → build its disk-cached downscale
    every 25 jobs → progress line (elapsed, done/total, %, rate)
RETURN how many new files were materialized
```

Thread-safe by construction: QImage end to end, per-path locks in
`ensure_variant` — the GUI thread's first-display build and this warm
meeting on the SAME file build it exactly once.

## Design Decisions

- **A separate module, not more `encyclopedia.py`** — that file is
  already past the Rule #20 threshold; the warm walk is its own
  responsibility (background I/O, no widgets) and must be importable
  without the dialog machinery.
- **Gallery icons warm FIRST** — the gallery is the first screen every
  open shows; its 40+ cards benefit before any single article page.
- **`_topics()` is the single inventory** (Rule #5) — no second list
  of themes/plates to drift out of sync; whatever the dialog would
  show is exactly what warms.
