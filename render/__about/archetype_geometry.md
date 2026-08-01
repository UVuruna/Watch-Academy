# Archetype Geometry

**Script:** [Archetype Geometry (script)](../archetype_geometry.py) · **Flow:** [diagram](../__flow/archetype_geometry.md)

## Purpose
Archetype-mode geometry and figure drawing: which figure the hour hand
lights, how large a figure's portrait or circle art must be for the arm
it stands on, and the draw call that puts a figure plus its name on the
dial. The skin QUERIES (`archetype_key`, `archetype_active`) live with
the other skin queries in [Skin Geometry](skin_geometry.md).

## Connections

### Uses
- [Context](context.md), [Painting](painting.md) — `draw_name_label`,
  `draw_pixmap_centered`, `name_label_px`
- [Skin Geometry](skin_geometry.md) — `arm_half_deg`
- [Slot Layout](slot_layout.md) — `weekday_body_size`
- [Config (folder)](../../config/___config.md) — `archetypes`,
  `constants`, `dial`, `paths`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `ArchetypeLayer`
  (arms), `ArchetypeCenterLayer` (center) — both DAILY but
  hover-variable, painted live
- [Compositor](compositor.md) — `_archetype_lit`/hit-testing read
  `archetype_lit_index`/`archetype_figure_size` the same way the layers
  do

## Functions
- `archetype_lit_index(pointer, hour_angle, rotation=0, offset=0)`: the
  figure whose hour-space holds the hour hand — the circle divides by
  arm count, each space centered on its (solar-rotated) arm.
- `archetype_center_lit(hour_angle, noon_angle)`: whether the center
  figure burns full — within the owner's window of true solar noon OR
  midnight.
- `archetype_art_size(path)` / `archetype_art_ready(path)`: the real
  art's pixel size, or `None` for a missing/placeholder file — the one
  place the header is read.
- `archetype_portrait_height(tip, tan_half)`: the PORTRAIT figure height
  that exactly inscribes the STANDARD 1:2 aspect into its arm's
  diamond.
- `archetype_figure_size(skin, radius, art_file)`: THE ONE sizing entry
  for every archetype figure — CIRCLE type (aspect ≥ threshold) wears
  the weekday slot size, PORTRAIT type wears the inscribed height.
- `draw_archetype_figure(...)`: one figure in its diamond — the art
  scaled in, or the name-fallback when art is missing/placeholder.
- `archetype_label_set_px(ctx, key, arm_width)`: the SET-UNIFORM label
  size for one archetype layout — every name (arms AND center) wears
  the size of the smallest fitted member.

## Design Decisions
- **THE TWO-TYPE LAW (owner decree 2026-07-18)** classifies EVERY
  figure by its own art's aspect ratio, never by a per-art clamp — one
  function (`archetype_figure_size`), two outcomes.
- **Missing/placeholder art reads CIRCLE-sized** — there is no aspect
  ratio to classify, so it falls back to the same size the weekday
  bodies use rather than guessing a portrait height.
