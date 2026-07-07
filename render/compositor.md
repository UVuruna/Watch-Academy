# Compositor

**Script:** [Compositor (script)](compositor.py)

## Purpose
Owns the layer stack and the cadence-driven cache: STATIC+DAILY layers
render into one pixmap at device resolution (rebuilt when the day
context, size or DPI changes); each minute-paint blits the cache and
draws the MINUTE layers (hands, year marker) live.

## Connections

### Uses
- [Layers](layers.md), [Assets](assets.md),
  [Clock State](../core/clock_state.md), [Skins (folder)](../skins/___skins.md)

### Used by
- [Clock Widget](../app/widget.md) — `paintEvent` delegate
- [App Controller](../app/controller.md) — `set_day()` / `invalidate()`
- [Tests (folder)](../tests/___tests.md) — `render_offscreen()`

## Classes

### Compositor
- `set_day(day)`: new day context, drops the composite
- `invalidate()`: size/DPI/screen change — drops composite AND rasterized assets
- `paint(painter, size, dpr, tick)`: blit composite + MINUTE layers;
  raises if called before the first day context (startup order is a
  controller guarantee)
- `render_offscreen(size, dpr, day, tick) -> QImage`: same path, headless
