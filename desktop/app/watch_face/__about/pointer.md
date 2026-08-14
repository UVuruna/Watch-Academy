# Pointer Section

**Script:** [Pointer Section (script)](../pointer.py) · **Flow:** [diagram](../__flow/pointer.md)

## Purpose
The Watch Face window's Pointer page (R-04): the pointer-variant
gallery, the palette-style wheel pills, the shape/curvature/edge rows
and "Hide night borders" — moved verbatim from the RETIRED
`design_window.DesignDialog._pointer_tab` (same conditional rules, Rule
#5; Phase 6 FINAL cleanup deleted that window outright) — plus **R-05:**
the "Daylight - Night" checkbox, moved here from the also-RETIRED
`app/settings_dialog/display_section.py`'s Archetype group — same
`daylight` setting, now with only ONE reader/writer. Unlike that old
Settings copy (always enabled — "inert elsewhere" there), THIS copy is
enabled only while the active pointer actually carries the switch
(`constants.DAYLIGHT_SWITCH_POINTERS`), per the owner's Watch Face
spec — an intentional tightening, not a regression, since the row now
lives beside the pointer it gates on.

**R-06's Earth group moved out again, 2026-08-10:** the owner ruled on
the rendering-proposals page that the Moon and the Earth are part of
the HANDS system — "they are what MOVES and points" — so the Earth
group (style/label/"Position pointer" rows, plus the position-pointer
shape gallery) now lives in [Hands & Bodies](bodies.md)'s "Earth" group.
This module keeps only the pointer VARIANT the hour/minute hands ride.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `pointer_swatch_icon` (gallery
  tiles)
- [Controls](controls.md) — `picture_group`, the one gallery door
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) — every pointer table
  `design_window.py` already read
- `render.skin_geometry.daylight_active` — the "Hide night borders" gate

### Used by
- `app.watch_face.window` — registered as the Pointer section's builder

## Design Decisions
- Every scalar pick (`pointer_shape`, `polygon_curvature`,
  `polygon_edge`, `hide_night_borders`, `daylight`) routes through the
  controller's shared `_set_display_choice(key, value)` — no new setter
  method per row (Rule #5, same discipline `design_window.md`
  documents).
