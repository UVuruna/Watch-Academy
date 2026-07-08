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
- `tooltip_at(x, y, size) -> str | None`: hover text at every dial size,
  ALL CENTERED (rich-text `<div align='center'>`), in priority order —
  today's body; the octa info slot (zodiac sign span / Chinese year
  span); the Moon marker (two lines: phase + illumination, cycle day);
  the Earth marker (owner format: day/week ordinals, zodiac with span,
  date — plus the season event name while it glows); the STAR ARMS
  (hexa arms name their two zodiac signs; cross/octa cardinal arms give
  the exact solstice/equinox instant; octa diagonals describe their
  season with dates, duration and the middle date the arrow points at —
  a trailing * flags solar-rotation imprecision; hexa arms append,
  after a blank line, the encyclopedic blurb of the arm's body in the
  ACTIVE weekday theme, from the
  [Symbolism Repository](../data/symbolism.md)); the twilight bands.
  With `legend` off, tooltip_at returns None for EVERYTHING — combined
  with click-through the dial has zero interaction (owner spec)

The layer stack follows `skin.z_order`; the current day's center body
(and, on the octa pointer, the bottom-arm info slot) are appended LAST
so they draw above the hands (owner spec). `_rotation()` feeds the
shared Star/Aura/Umbra/slot rotation into every RenderContext: the
solar offset, or 0 with solar rotation off (upright mode).
