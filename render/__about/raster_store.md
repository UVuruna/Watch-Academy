# Raster Store

**Script:** [Raster Store (script)](../raster_store.py)

## Purpose
The disk raster cache's own module — the one place that knows HOW a
derived image lands on disk safely. Born from the owner's 2026-07-31
crash log: the background art warm wrote a letter recolor **directly to
its final cache path** with `QImage.save`, the GUI thread's
`letter_metal_file` saw the path exist mid-write, and `paintEvent`
loaded a truncated PNG — `ValueError` inside the paint, an unterminated
`QPainter`, and a permanently broken window. A cache file must either
be COMPLETE on disk or NOT THERE; nothing in between may ever be
visible to a reader.

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

## Functions
- `atomic_save(image, path)`: save any Qt image object (`QImage` /
  `QPixmap` — anything with `.save(str) -> bool`) to `path` via a
  sibling `.part` file and `os.replace`, so the destination appears
  atomically. Raises `OSError` when the encode or the rename fails
  (after removing the partial file) — callers keep their existing
  "cold cache is only slower, never wrong" fallbacks.

## Design Decisions
- **`os.replace`, not `Path.rename`** — on Windows, `rename` onto an
  existing destination raises; `replace` is the atomic overwrite in
  both the fresh-write and the concurrent-writer case (two threads
  building the same variant behind different locks still end with one
  complete file).
- **The `.part` sibling lives in the SAME directory** as the final file
  — `os.replace` is only atomic within one volume, and the cache dir is
  the one place guaranteed to be on it.
