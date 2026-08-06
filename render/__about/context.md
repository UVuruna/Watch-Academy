# Render Context

**Script:** [Context (script)](../context.py) · **Flow:** [diagram](../__flow/context.md)

## Purpose
The render protocol — the three types every layer speaks. `Cadence`
says how often a layer's content changes, `RenderContext` carries
everything a layer may read for one paint, and `Layer` is the closed
ABC the compositor stacks. Every layer paints in a coordinate system
whose origin is the dial centre; dial angles are degrees CLOCKWISE from
the top (the core convention), converted to Qt's counterclockwise-
from-3-o'clock only inside the pie/position helpers in
[Painting](painting.md).

## Connections

### Uses
- [Core (folder)](../../core/___core.md) — `DayContext`, `TickState`;
  [World](../../core/__about/world.md) supplies the two rotation numbers
  the compositor stamps on every context
- [Assets](assets.md) — `AssetCache`
- [Skins (folder)](../../skins/___skins.md) — `SkinDefinition`

### Used by
- Every module in this folder and in [Layers (subfolder)](../layers/___layers.md) — `Layer`
  is the base class every paint layer subclasses; `RenderContext` is
  threaded through every geometry/painting function
- [Compositor](compositor.md) — builds one `RenderContext` per paint
  (and a hover/reveal-free one per offscreen composite group)

## Classes

### Cadence (Enum)
`STATIC` (rebuild on skin/size/DPI change), `DAILY` (rebuild on
`DayContext` change), `MINUTE` (painted live every tick). Drives
[Compositor](compositor.md)'s cache-vs-live partition of the layer
stack.

### RenderContext (frozen dataclass)
- `skin`, `day`, `tick` (`None` while compositing STATIC/DAILY groups),
  `radius`, `cache`, `dpr` — the paint's fixed inputs
- `rotation` — THE POINTER ROTATION ([World](../../core/__about/world.md)):
  the Star/Aura/Umbra/slot rotation. Geocentric — the solar offset, or 0
  in upright mode. Heliocentric — the night PHASE alone, because the
  star stands still and the world turns under it
- `world_offset` — THE WORLD OFFSET (same module): how far the dial FACE
  has turned. The outer numeral band, the ring letters, the crown text,
  the daylight arcs, the Earth and Moon markers, the hour hand and every
  hover hit zone that reads the dial band ride this ONE number together.
  Exactly `0.0` in Geocentric, so that mode is a bit-for-bit no-op; the
  INNER band and the minute/seconds hands never take it
- `hovered` — the element under the cursor (`"earth"`, `"moon"`,
  `"octa_slot"`, `"body:<name>"`, …), drawn `hover_enlarge` times larger
- `reveal_active` — the Omega-reveal window is open
- `archetype_lit` — the archetype figure whose hour-space holds the
  hour hand, or `None` off the mode

### Layer (ABC)
- `cadence: Cadence` — declared by each subclass
- `hover_variable: bool` — True on layers whose APPEARANCE changes with
  hover/reveal even though their content is DAILY (`WeekdayLayer`,
  `ArchetypeLayer`); the compositor never bakes these into the cached
  composite, so a hover enter/leave or a reveal rebuilds nothing
- `_gate(ctx, element)` — True when THIS pass draws `element`: the base
  pass draws everything but the hovered element, the `lift=True` twin
  (`HoverLiftLayer`) draws only it, above the hands
- `paint(painter, ctx)` — abstract; every layer implements it
