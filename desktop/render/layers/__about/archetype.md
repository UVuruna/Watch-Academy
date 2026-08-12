# Archetype Layers

**Script:** [Archetype Layers (script)](../archetype.py) ·
**Flow:** [diagram](../__flow/archetype.md)

## Purpose

Two layers for Archetype mode (owner sealed package 2026-07-16), which
overrides the weekday model entirely: `ArchetypeLayer` draws each diamond's
own archetype figure — the arm whose hour-space holds the hour hand draws
FULL, the rest ghost at the weekday ghost opacity (an ARCHETYPE CLOCK, not a
gallery); `ArchetypeCenterLayer` draws the archetype's centre figure (the
Eye / the Hearth / the Seal / the Union / the Throne — the Compass has
none) where the weekday centre body used to live, ABOVE the hands, burning
FULL only within `ARCHETYPE_CENTER_WINDOW_DEG` of true solar noon or
midnight. Both fall back to the figure's NAME when its art is a
placeholder; the reveal window forces every figure full regardless of the
lit/window logic.

`ArchetypeLayer` is `Cadence.DAILY` with `hover_variable = True`: the lit
arm changes with the hour hand's daily sweep through the archetype
hour-space, but hover-enlarge changes appearance every frame, so it paints
live like `WeekdayLayer` (same owner rationale, ROADMAP 15f).
`ArchetypeCenterLayer` is `Cadence.MINUTE`: its noon/midnight WINDOW is
evaluated against the live hour angle every tick, so it needs no
`hover_variable` flag — `MINUTE` already repaints it live.

## Connections

### Uses
- [Archetype Geometry](../../__about/archetype_geometry.md) — `archetype_art_ready`,
  `archetype_center_lit`, `archetype_figure_size`, `archetype_label_set_px`,
  `draw_archetype_figure`
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_name_label`,
  `draw_pixmap_centered`
- [Skin Geometry](../../__about/skin_geometry.md) — `archetype_key`, `arm_half_deg`,
  `hover_factor`
- [Slot Layout](../../__about/slot_layout.md) — `weekday_body_orbit`
- [Config (folder)](../../../config/___config.md) — `archetypes` (per-key
  figure tables), `pantheon` (`rotating_art_file` for the Tetramorph's daily
  art rotation)

### Used by
- [Compositor](../../__about/compositor.md) — `ArchetypeLayer` takes `WeekdayLayer`'s
  z-slot when Archetype mode is active; `ArchetypeCenterLayer` takes
  `CenterBodyLayer`'s slot, appended above the hands
- [Hover Lift Layer](hover_lift.md) — `lift=True` twins of both classes
  repaint the hovered arm figure or centre figure above the hands

## Classes

### ArchetypeLayer
`cadence = Cadence.DAILY`, `hover_variable = True`.
- `paint()`: for each figure in the active archetype key's arm list — gated
  per-arm through `Layer._gate` — resolves any daily art rotation, classifies
  the figure's own art as circle (weekday-body-sized) or portrait (the
  per-pointer lancet fraction, THE TWO-TYPE LAW), and draws it full or
  ghosted depending on whether it holds the hour hand's current hour-space
  or the reveal window is active.

### ArchetypeCenterLayer
`cadence = Cadence.MINUTE`.
- `paint()`: no-ops when the active key has no centre or the element is
  hovered-away (`Layer._gate`); otherwise sizes the centre by the same
  TWO-TYPE LAW, computes `lit` from `archetype_center_lit(hour_angle,
  star_rotation)` (or the reveal window), and draws the art or — if the art
  is a placeholder (`archetype_art_ready`) — the centre's name label at the
  SAME set-uniform size `ArchetypeLayer`'s arms compute.
