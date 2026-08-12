# Eclipse Glow

**Script:** [Eclipse Glow (script)](../eclipse_glow.py) · **Flow:** [diagram](../__flow/eclipse_glow.md)

## Purpose
Eclipse and event GLOW — strength, state and the radial paint. An
eclipse's render STATE and how strongly it glows for a given magnitude,
plus the radial-gradient halo the year marker paints behind an event
body (season turning point, moon phase, or eclipse).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `glow` (the color/alpha/
  radius constants and the type→state lookup table)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer` calls
  `draw_event_glow` for every relocated marker, and resolves the
  eclipse render state/strength before it
- [Compositor](compositor.md) — `_eclipse_hover_line` names the active
  eclipse using the same `eclipse_render_state`/type vocabulary

## Functions
- `draw_event_glow(painter, pos, marker_radius, color, strength=1.0,
  fringe_color=None)`: the compact radial halo — core/mid/edge gradient
  stops, plus an optional thin outer FRINGE ring (the lunar-eclipse
  turquoise ozone band).
- `eclipse_glow_strength(magnitude)`: magnitude-linear glow intensity,
  clamped and mapped to `ECLIPSE_GLOW_STRENGTH_MIN/MAX` — used only for
  `solar_partial`, the one state that stays magnitude-driven.
- `eclipse_render_state(event)`: the catalog (kind, type) → render
  STATE lookup, falling back to the kind's `partial` state for an
  unknown/missing type rather than raising.
- `eclipse_state_glow_strength(state, magnitude)`: the state-driven
  glow fraction for every state except `solar_partial`.

## Design Decisions
- **`fringe_color` is `None` for every caller but the lunar eclipse** —
  the parameter exists so `draw_event_glow` stays the one shared glow
  painter (Rule #5) rather than growing a lunar-only sibling.
- **An unrecognized (kind, type) pair degrades to `partial`, never
  raises** (Rule #1) — the eclipse catalog's generator only ever writes
  the documented type vocabulary, so this is a documented fallback for
  a row that should not occur, not a silently swallowed error.
