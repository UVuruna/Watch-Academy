# Raster Store

**Script:** [Raster Store (script)](../raster_store.py)

## Purpose
The disk raster cache's own module — the one place that knows HOW a
derived image lands on disk safely and WHAT its name is keyed by.

Born from the owner's 2026-07-31 crash log: the background art warm
wrote a jewel recolor **directly to its final cache path** with
`QImage.save`, the GUI thread's `jewel_metal_file` saw the path exist
mid-write, and `paintEvent` loaded a truncated PNG — `ValueError`
inside the paint, an unterminated `QPainter`, and a permanently broken
window. A cache file must either be COMPLETE on disk or NOT THERE;
nothing in between may ever be visible to a reader.

The second law (0.14.708): cache names follow the source's **CONTENT**,
not its mtime. Every git operation rewrites mtimes without changing a
pixel, so the old mtime-keyed names orphaned the entire multi-GB cache
on every checkout — the next launch re-paid every recolor and downscale
cold (the owner's 75-second start traces straight back to this).
`source_prefix` is the ONE naming function every cache-path builder
shares, so the naming and the garbage collector can never drift apart.

## Connections

### Uses
- nothing beyond the standard library (`os`, `pathlib`) — deliberately
  dependency-light so subprocess workers can import it without paying
  for Qt-adjacent modules

### Used by
- [Assets](assets.md) — the SVG master disk write
- [Asset Recolor](asset_recolor.md) — `ensure_variant`'s metal-variant
  write, `_recolored_plate`'s subdial write
- [Asset Variants](asset_variants.md) — the working-set downscales, the
  moon-phase plates, the eclipse icon tint, the calendar wheel icon
- [Asset Index](asset_index.md) — calls `compute_fingerprint` (the
  recipe) and INSTALLS itself through `attach_fingerprint_source` (the
  memo). The arrow points one way on purpose: this module must not
  import that one, or the working-set subprocess workers would start
  paying for Qt and `config` to import it.

## Functions
- `atomic_save(image, path)`: save any Qt image object (`QImage` /
  `QPixmap` — anything with `.save(str) -> bool`) to `path` via a
  sibling `.part` file and `os.replace`, so the destination appears
  atomically. Raises `OSError` when the encode or the rename fails
  (after removing the partial file) — callers keep their existing
  "cold cache is only slower, never wrong" fallbacks.
- `compute_fingerprint(path)`: THE RECIPE, unmemoized — sha1 over
  (size, first 64 KiB, last 4 KiB), 12 hex. Always opens the file.
  Split out in 0.14.950 so [Asset Index](asset_index.md) can own the
  persistent memo without this module owning a JSON store (Rule #5 —
  one recipe, whoever remembers it).
- `fingerprint(path)`: the memoized content key. THREE tiers, cheapest
  first: the attached persistent index (survives the process — this is
  what ended the owner's 91.6-second launch), then this module's own
  in-process memo keyed by (size, mtime_ns), then `compute_fingerprint`.
  Documented limit: a same-size edit leaving both sampled windows
  byte-identical keeps the old name — no compressed raster format
  produced by an editor does that in practice.
- `attach_fingerprint_source(getter)`: install the persistent lookup
  (`None` uninstalls — tests). Consulted first; it may answer `None`
  for "not mine", which falls through to the tiers above. Injected
  rather than imported so this module stays standard-library-only.
- `source_prefix(path)`: the leading `<16-hex path stamp>_<12-hex
  fingerprint>` pair every cache name derived from `path` starts with;
  a missing source yields the graceful-absent `_0`.

## Design Decisions
- **`os.replace`, not `Path.rename`** — on Windows, `rename` onto an
  existing destination raises; `replace` is the atomic overwrite in
  both the fresh-write and the concurrent-writer case (two threads
  building the same variant behind different locks still end with one
  complete file).
- **The `.part` sibling lives in the SAME directory** as the final file
  — `os.replace` is only atomic within one volume, and the cache dir is
  the one place guaranteed to be on it.
