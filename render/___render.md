# render/

Everything QPainter. Consumes `DayContext`/`TickState` (from core) and a
`SkinDefinition` (from skins) — computes no astronomy itself. All layers
paint in a center-origin coordinate system with dial angles (degrees
clockwise from top) converted to Qt's conventions only inside the local
helpers.

## Files

### `layers.py` — Layer Stack
`Cadence` enum (STATIC: rebuild on skin/size/DPI change; DAILY: rebuild on
day change; MINUTE: painted live) + the `Layer.hover_variable` flag (a
DAILY layer whose APPEARANCE changes with hover/reveal, so the compositor
draws it LIVE, never in the cached composite — owner 2026-07-17, ROADMAP
15f) + `Layer` ABC + the concrete layers
(closed set): BackgroundLayer (the Umbra brightness wheel + the Aura
period wedges over the sunlit arc), StarLayer (procedural N-diamond
star, top tip at solar noon or upright), RingLayer (ring art or the
procedural donut with ticks, numerals, per-skin letters), WeekdayLayer
(hover-variable — themed bodies on the pointer's slots; "ghost" and
"center_only" modes), CenterBodyLayer and BottomSlotLayer (above the
hands), YearMarkerLayer (Earth day/night variant, moon with terminator
mask, event glow), HandLayer (one class, one shared scale, hub 15 design
units above the canvas bottom). The ARCHETYPE layers are hover-variable
too, and every archetype figure — arms AND center — shares ONE size via
`archetype_figure_height()` / `archetype_center_height()` (owner
2026-07-17, ROADMAP 15g). See [Layers](layers.md).

### `compositor.py` — Compositor
Z-ordered stack from the skin's `z_order`, partitioned into paint STEPS
(owner 2026-07-17, ROADMAP 15f): each maximal run of hover-INVARIANT
STATIC/DAILY layers is one cached pixmap; the MINUTE layers AND the
HOVER-VARIABLE layers (the weekday bodies, the archetype figures) paint
LIVE. Because the default `z_order` seats the weekday_set BELOW the
ring, pulling it out splits the cache into TWO segments — base
(background, star) below the live bodies, ring above them — so a hover
enter/leave or an Omega reveal rebuilds NOTHING (the composite key is
size/DPI + day + the Calendar's intraday lit wedge; hover and reveal are
absent). `render_offscreen()` uses the same paint path for tests and the
future settings preview. See [Compositor](compositor.md).

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
