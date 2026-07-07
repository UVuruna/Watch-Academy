# render/

Everything QPainter. Consumes `DayContext`/`TickState` (from core) and a
`SkinDefinition` (from skins) — computes no astronomy itself. All layers
paint in a center-origin coordinate system with dial angles (degrees
clockwise from top) converted to Qt's conventions only inside the local
helpers.

## Files

### `layers.py` — Layer Stack
`Cadence` enum (STATIC: rebuild on skin/size/DPI change; DAILY: rebuild on
day change; MINUTE: painted live) + `Layer` ABC + the seven concrete
layers (closed set): BackgroundLayer (six 4-hour sectors + darkening
overlays per daylight regime — always painter-drawn, the daylight arc
changes daily), HexagramLayer (asset or procedural star, rotated to solar
noon), NoonMarkerLayer, RingLayer (donut, ticks, 24h numerals with
per-skin letters, minute numbers), WeekdayLayer (Sun center + six diamond
slots that rotate WITH the hexagram; "ghost" and "center_only" modes),
YearMarkerLayer (Earth day/night variant or procedural moon with
terminator mask), HandLayer (one class, two instances, rotates about the
skin-declared pivot). See [Layers](layers.md).

### `compositor.py` — Compositor
Z-ordered stack from the skin's `z_order`; composites STATIC+DAILY layers
into one cached pixmap at device resolution; the per-minute paint blits
the cache and draws MINUTE layers live. `render_offscreen()` uses the
same paint path for tests and the future settings preview.
See [Compositor](compositor.md).

### `assets.py` — Asset Cache
Rasterizes PNG/SVG once per (path, pixel height); flushed on screen/skin
change; missing assets raise loudly. See [Assets](assets.md).

## Connections

### Uses
- [Core (folder)](../core/___core.md) — `DayContext`, `TickState`, angle mapping
- [Skins (folder)](../skins/___skins.md) — `SkinDefinition`
- [Config (folder)](../config/___config.md) — dial constants, slot angles

### Used by
- [App (folder)](../app/___app.md) — widget `paintEvent` delegates to the
  compositor; controller feeds day/tick and invalidations
- [Tests (folder)](../tests/___tests.md) — offscreen smoke tests
