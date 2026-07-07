# Assets

**Script:** [Assets (script)](assets.py)

## Purpose
Rasterize each skin image once per (path, pixel height): PNG scaled
smoothly, SVG rendered via QSvgRenderer (the explicit QtSvg import also
makes PyInstaller bundle the plugin). Missing/unreadable assets raise
`ValueError` — a broken skin must be visible, never silently blank.

## Connections

### Uses
- PySide6 QtGui/QtSvg

### Used by
- [Layers](layers.md) — hands, hexagram, weekday bodies, year marker
- [App Controller](../app/controller.md) — owns the instance, flushed via
  the compositor on screen change

## Classes

### AssetCache
- `pixmap_by_height(path, logical_height, dpr)`: aspect-preserving,
  device-resolution pixmap with `devicePixelRatio` set
- `flush()`: drop everything (screen/DPI or skin change)
