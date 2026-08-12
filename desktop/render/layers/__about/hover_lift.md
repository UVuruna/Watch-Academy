# Hover Lift Layer

**Script:** [Hover Lift Layer (script)](../hover_lift.py) ·
**Flow:** [diagram](../__flow/hover_lift.md)

## Purpose

The hover Z-LIFT (owner 2026-07-13: "kad radim hover hoću da u trenutku
enlarge bude iznad kazaljki" — when I hover I want the enlarge to be above
the hands, instantly). Stacked LAST in the z-order, it repaints ONLY the
element currently under the cursor, through `lift=True` twins of the
element-owning layers. Each base layer skips its own hovered element via
`Layer._gate`, so nothing ever draws twice — the base pass and this layer's
pass are complementary, never overlapping.

`Cadence.MINUTE`: the hover target can change on any mouse move, so it must
repaint live every frame. Not `hover_variable` — `MINUTE` already covers it.

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Archetype Layer](archetype.md) — `ArchetypeCenterLayer`, `ArchetypeLayer`
  twins
- [Slot Layer](slot.md) — `SlotLayer` twin (covers BOTH angle and center
  seats — see Design Decisions in [Layers (folder)](../___layers.md))
- [Weekday Layer](weekday.md) — `WeekdayLayer` twin
- [Year Marker Layer](year_marker.md) — `YearMarkerLayer` twin

### Used by
- [Compositor](../../__about/compositor.md) — always appended LAST in `_build_layers()`,
  unconditionally, regardless of skin or Elements switches

## Classes

### HoverLiftLayer
`cadence = Cadence.MINUTE`.
- `__init__(skin)`: builds the five `lift=True` twins once —
  `WeekdayLayer`, `SlotLayer`, `YearMarkerLayer`, `ArchetypeLayer`,
  `ArchetypeCenterLayer` — in that fixed order.
- `paint()`: returns immediately when nothing is hovered
  (`ctx.hovered` is None); otherwise calls every twin's `paint()` in turn —
  each twin's own `Layer._gate` (via `_lift = True`) makes it draw ONLY the
  currently-hovered element and skip everything else, so at most one visual
  actually repaints.
