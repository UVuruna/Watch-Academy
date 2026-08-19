# Pointer Geometry

**Script:** [Pointer Geometry (script)](../pointer_geometry.py) · **Flow:** [diagram](../__flow/pointer_geometry.md)

## Purpose

What a pointer IS as a shape. The pointer is the star at the middle of
the dial; this module holds only the numbers that decide its FORM.

Layer: config — pure Python, no Qt, no wall clock.

## Why it exists

`config/constants.py` carried **38 top-level sections** — app identity,
era notation, weekday bodies, pointer geometry, ring finishes, zodiac,
translation languages, UI scale, seating — under one docstring. That is a
junk drawer, not a directory: nobody could say what the module was ABOUT,
and every session that needed one constant read past thirty-seven
subjects it did not care about. The [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s
R15 asked for a topic split; the owner ruled on **2026-08-19**, naming
each destination module himself, and this file is one of them.

The move was mechanical and total: each section travelled WHOLE, with
its comments, and every caller was repointed to the real module. **No
re-export shim was left behind** (`rules/CODE.md` — No backward
compatibility), and `config/constants.py` was deleted in the same round.

## Contents

- **Arm and wedge counts** — `POINTER_POINTS` (how many arms each
  pointer draws), `POINTER_DIAL_COUNTS`, and the calendar pointer's
  `CALENDAR_WEDGES` / `CALENDAR_WEDGE_DEG` with the
  `GREGORIAN_MONTH_NAMES` that ride one wedge each.
- **Arm half-angles** — `POINTER_ARM_HALF_ANGLE_DEG`, how wide an arm
  is at the hub, per pointer.
- **Shape and edges** — `POINTER_SHAPES` / `POINTER_SHAPE_DEFAULT`
  (star or polygon), `POLYGON_POINTERS` (which pointers may be drawn as
  a polygon at all), `POLYGON_CURVATURE_RANGE` / `_DEFAULT` and
  `POLYGON_EDGE_MODES` / `_DEFAULT` (smooth concave or V-notched).

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Render (folder)](../../render/___render.md) — the star and polygon
  geometry, the arm hit-test, the aura wedges
- [Calendar Mounts](calendar_mounts.md) — the twelve wedges' month
  names
- [App (folder)](../../app/___app.md) — the Watch Face pointer page

## Design Decisions

- **Names are NOT here.** `config/pointer_names.py` holds the display
  names, the wheel labels and the arm labels. A rename is a copy
  decision, a half-angle is a drawing decision, and the two change for
  entirely different reasons — keeping them apart means a copy change
  never touches a geometry file.
- **The month names stayed with the wedge count.** Twelve wedges and
  twelve month names are one fact stated twice; splitting them would let
  the two disagree.
