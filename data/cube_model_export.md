# Cube Model Export

**Script:** [Cube Model Export (script)](cube_model_export.py)

## Purpose

Builds the Character-Cube MODEL — axes, seats, views — that the
sibling **3D Preview** gadget's `Preview3DLightWidget` shows, from
DOMY's own canon data (WORKPLAN Session 28, the second attempt, run
once the gadget's M2/M3 landed). The gadget is its own project, its own
repo (`Gadgets/3D Preview`, beside this one) — its `MODELS.md` is the
authoring guide this module follows; nothing here duplicates it.

**One source of truth (root Rule #19):** every direction, position,
colour and name comes from `config.cube` / `config.palette` /
`core.cube_seating` — nothing here is retyped from the canon. Pure
Python, no Qt, **no gadget import at all** — the gadget's own model
schema (`shared/model_schema.json`) and its four owner views
(`preview3d.cube_model.DEFAULT_VIEWS`) are transcribed as documented
constants rather than imported, so this module builds and is testable
whether or not the sibling gadget folder even exists on the machine.

## Connections

### Uses
- [Character Cube](../config/cube.md) — the 13 axes, the 65 sealed
  terms, the rosters, the sacred figures
- [Cube Seating](../core/cube_seating.md) — `cell_color()` (the shared
  hue derivation) and `family_of`/`SACRED_AXIS` (tier assignment)
- [Encyclopedia UI](../config/encyclopedia_ui.md) —
  `CUBE_DIAGRAM_DIM_OPACITY` / `CUBE_MODEL_GLASS_OPACITY`

### Used by
- [Cube Preview3D Bridge](../render/cube_preview3d.md) — the ONLY
  caller; builds the model once, validates it against the gadget's
  schema, and caches it
- [Cube Preview3D Tests](../tests/___tests.md) — schema/coverage pins

## The direction grammar

A DOMY coordinate `(x, y, z)` with components in {-1, 0, 1} already IS
the gadget's own direction token, letter for letter — no lookup table:

```
FOR each of x, y, z IN ORDER:
    IF the coordinate is nonzero -> emit "+"/"-" and the letter
```

`(1, 1, 1)` → `"+x+y+z"`; `(0, 1, -1)` → `"+y-z"`. This works because
`config.cube`'s own axis order ("X Activation, Y Moral Scope, Z
Self-Regard") IS the gadget's `axisLetters` order.

## The four registers

The gadget's schema fixes the vocabulary to exactly `canon` / `myth` /
`historical` / `movie`. DOMY's own three `FIGURE_SETS` plus the canon
term map onto it directly:

| Gadget register | DOMY source |
|---|---|
| `canon` | `CubeCell.luminous` / `.fallen` — the term itself |
| `myth` | `cube.roster(coords, "archetypal")` |
| `historical` | `cube.roster(coords, "historical")` |
| `movie` | `cube.roster(coords, "modern")` |

## The centre and the two sacred vertices

Doctrine (CUBE.md §The Rosters / §The Sacred Axis) is explicit that no
persona ever holds the centre, and that each sacred vertex names
exactly ONE figure per register (Jesus Christ / Maximilian Kolbe /
Aslan; The Devil / Nero / Sauron — never a second, "fallen-Jesus" or
"luminous-Devil" reading at the same seat). So for these three seats
the figure registers repeat the ONE name in both the luminous and
fallen slots — a true statement, not a fabrication, and the only way to
satisfy the schema's non-empty-string rule without inventing a name
doctrine never gives. The centre's OWN canon-register fallen reading is
likewise empty by doctrine ("no fall touches him") and repeats its
luminous name for the same reason.

## Views

`build_model()` emits:

- **The four owner models** (`primary` / `secondary` / `tertiary` /
  `cube`) — WORKPLAN's amended Session 28 page list. These mirror
  `preview3d.cube_model.DEFAULT_VIEWS` verbatim (transcribed, not
  imported — see the module's own comment on `_OWNER_VIEWS`).
- **One solo view per axis** (`axis:<name>`) and **one per pole**
  (`pole:<luminous name>`) — the 3D analogue of
  `render.cube_diagrams.axis()` / `.pole()`: the target axis (and its
  seat(s)) at full opacity, the rest at `CUBE_DIAGRAM_DIM_OPACITY` (the
  SAME constant the 2D drawer dims by, Rule #5), the glass hidden. The
  camera stands perpendicular to the axis so it reads at its true
  length rather than foreshortening to a point.

## Design Decisions

- **Gadget-free by construction**, not by discipline: the module simply
  never imports `preview3d`. Validating the output is the CALLER's job
  (`render.cube_preview3d`, guarded; this project's own tests).
- **The glass shell wears DOMY's own six pole hues** (`_FACE_ORDER`,
  matching `shared/spec.json`'s `faceOrder`), not the gadget's generic
  demo palette — palette-derived, per root Rule #19.
