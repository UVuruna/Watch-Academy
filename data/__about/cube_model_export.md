# Cube Model Export

**Script:** [Cube Model Export (script)](../cube_model_export.py) ·
**Flow:** [diagram](../__flow/cube_model_export.md)

## Purpose

Exports DOMY's Character Cube canon as a renderer-neutral MODEL dict
for the sibling **3D Preview** gadget (`Gadgets/3D Preview`) — axes,
the seats they point at, what each seat says in each register, and the
views that pick who speaks. **One source of truth (root Rule #19):**
every direction, position, colour and name comes from `config.cube` /
`config.encyclopedia_ui` / `core.cube_seating` — nothing here is
retyped from the canon. Pure Python, no Qt, **no gadget import at
all** — the gadget's own schema and its four owner views are
transcribed as documented constants (`_GROUP_PATH`, `_OWNER_VIEWS`)
rather than imported, so this module builds and is testable whether or
not the `3D Preview` folder exists on the machine. Validating the
OUTPUT against the gadget's schema is the caller's job.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `config.cube` (the 13
  axes, the rosters, the sacred figures), `config.encyclopedia_ui` —
  `CUBE_DIAGRAM_DIM_OPACITY` / `CUBE_MODEL_GLASS_OPACITY`
- [Core (folder)](../../core/___core.md) —
  `core.cube_seating.cell_color` / `family_of` / `SACRED_AXIS` /
  `CELL_BY_COORDS`

### Used by
- [Cube Preview3D Bridge](../../render/__about/cube_preview3d.md) — the ONLY
  caller; builds the model once, validates it against the gadget's
  schema, caches it
- [Tests (folder)](../../tests/___tests.md) — `test_cube_preview3d.py`
  imports the module directly

## Functions

- `build_model(size=1.0)`: the whole model dict — `name`, `label`,
  `root`, `size`, `registers`, `sacred`, `axes` (13 entries), `cells`
  (26 seats + centre), `glass` (opacity + 6 pole colours), `views`.
  See [flow](../__flow/cube_model_export.md).
- `_token(coords)`: a coordinate to the gadget's direction token — see
  the flow doc's direction-grammar section.
- `_figure_names(coords)` / `_seat_names(coords)`: register → figure
  names for one of the 27 cells, across the four registers (`canon`,
  `myth`, `historical`, `movie`).
- `_axis_entry(axis)` / `_cell_entry(coords, half)` /
  `_cell_entries(size)`: the `axes[]` / `cells[]` model entries.
- `_expand(name, label, camera, groups)`: short group-name opacities
  expanded to every group's full path (an unmentioned group is `0`,
  never left out — so switching views never leaves a stale group lit).
- `_axis_solo_view(axis)` / `_pole_solo_views(axis)` / `_lit_view(...)`:
  the computed per-axis / per-pole solo views.
- `_side_camera(coords)` / `_cross(a, b)`: a camera direction
  perpendicular to a given axis, via a 3D cross product against a
  reference vector, so the axis reads at true length instead of
  foreshortening to a point.

## Design Decisions

- **The centre and the two sacred vertices never split by register:**
  doctrine holds that no persona ever occupies the centre, and each
  sacred vertex names exactly one figure per register — so for these
  three seats `_figure_names` repeats the SAME name in both the
  luminous and fallen slots (a true statement, not a fabrication; the
  only way to satisfy the schema's non-empty-string rule without
  inventing a name doctrine never gives).
- **Gadget-free by construction**, not by discipline: the module simply
  never imports `preview3d`; the gadget's group-path tree
  (`_GROUP_PATH`) and its four default views (`_OWNER_VIEWS`) are
  hand-transcribed constants, re-compared by hand if the gadget's own
  values change.
- **The glass shell wears DOMY's own six pole hues** (`_FACE_ORDER`,
  matching the gadget's `faceOrder`), not the gadget's generic demo
  palette — palette-derived, per root Rule #19.
