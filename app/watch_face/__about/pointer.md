# Pointer Section

**Script:** [Pointer Section (script)](../pointer.py) · **Flow:** [diagram](../__flow/pointer.md)

## Purpose
The Watch Face window's Pointer page (R-04): the pointer-variant
gallery, the palette-style wheel pills, the shape/curvature/edge rows
and "Hide night borders" — moved verbatim from
`design_window.DesignDialog._pointer_tab` (same conditional rules, Rule
#5) — plus two additions this phase:

- **R-05:** the "Daylight - Night" checkbox, moved here from
  `app/settings_dialog/display_section.py`'s Archetype group. The OLD
  copy in Settings stays in place until Phase 6 removes it; both wire
  the SAME `daylight` setting. Unlike the Settings copy (always
  enabled — "inert elsewhere" there), THIS copy is enabled only while
  the active pointer actually carries the switch
  (`constants.DAYLIGHT_SWITCH_POINTERS`), per the owner's Watch Face
  spec — an intentional tightening, not a regression, since the row now
  lives beside the pointer it gates on.
- **R-06:** the Earth group (Clean/Atmosphere tiles + label pills),
  moved verbatim from `design_window.DesignDialog._earth_tab`. Sizes do
  NOT live here — see `size.py`.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `pointer_swatch_icon` (gallery
  tiles), `art_thumbnail` (Earth style tiles)
- [Watch Face Shared Widgets](widgets.md) — `pill`, `tile`
- [Config (folder)](../../../config/___config.md) — every pointer/earth
  table `design_window.py` already read
- `render.skin_geometry.daylight_active` — the "Hide night borders" gate

### Used by
- `app.watch_face.window` — registered as the Pointer section's builder

## Design Decisions
- Every scalar pick (`pointer_shape`, `polygon_curvature`,
  `polygon_edge`, `hide_night_borders`, `daylight`, `earth_style`) routes
  through the controller's shared `_set_display_choice(key, value)` —
  no new setter method per row (Rule #5, same discipline
  `design_window.md` documents).
