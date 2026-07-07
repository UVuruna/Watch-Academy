# render/

**Planned — implemented in M3.** Everything QPainter. Consumes only
`DayContext` / `TickState` (from core) and `ResolvedSkin` (from skins) —
computes no astronomy itself.

## Planned Files

### `layers.py` — Layer Stack
`Cadence` enum (STATIC: rebuild on skin/size/DPI change; DAILY: rebuild on
day change; MINUTE: painted live) + `Layer` ABC + the seven concrete layers
(closed set): BackgroundLayer (6×4h sector wheel with explicit branches per
daylight regime — always painter-drawn, the daylight arc changes daily),
HexagramLayer, NoonMarkerLayer, RingLayer, WeekdayLayer, YearMarkerLayer
(Earth day/night variants or moon disc with terminator mask), HandLayer
(one class, two instances, rotates about the skin-declared pivot).

### `compositor.py` — Compositor
Z-ordered stack; composites STATIC+DAILY layers into one cached QPixmap at
`logical_size × devicePixelRatio`; per-minute paint = blit cache + MINUTE
layers. Also renders offscreen — the same code path serves the settings
preview and render tests.

### `assets.py` — Asset Cache
Rasterizes SVG/PNG once per (path, size, DPR); flushed on screen/skin change.

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Skins (folder)](../skins/___skins.md),
  [Config (folder)](../config/___config.md)

### Used by
- [App (folder)](../app/___app.md) — widget `paintEvent`, settings preview
