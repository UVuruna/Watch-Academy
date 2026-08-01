# Painting

**Script:** [Painting (script)](../painting.py) · **Flow:** [diagram](../__flow/painting.md)

## Purpose
Low-level QPainter primitives shared by every layer: pure drawing and
dial-coordinate helpers with no skin knowledge and no astronomy.
`dial_point`/`draw_pie`/`pie_path` are the ONE place the project's
clockwise-from-top dial angle converts to Qt's counterclockwise-from-
3-o'clock convention (Rule #5).

## Connections

### Uses
- [Context](context.md) — `RenderContext` (asset rasterization inputs)
- [Config (folder)](../../config/___config.md) — `dial`, `palette`
  constants

### Used by
- Every geometry/painting module in this folder ([Shapes](shapes.md),
  [Subdial](subdial.md), [Calendar Mount](calendar_mount.md),
  [Archetype Geometry](archetype_geometry.md), [Weekday
  Body](weekday_body.md)) and every layer in
  [Layers (subfolder)](../layers/___layers.md)

## Functions
- `dial_point(theta_deg, distance)`: point at a dial angle (clockwise
  from top) and distance from the origin — the ONE angle-to-Qt
  conversion.
- `draw_pie(painter, radius, start_deg, end_deg)` / `pie_path(...)`:
  filled pie / clip path between two dial angles, clockwise.
- `draw_pixmap_centered(painter, ctx, asset, pos, height, tint=None,
  desaturate=False, metal=None, saturation=1.0)`: the one shared image
  draw of weekday bodies and the year marker — rasterizes through
  `ctx.cache` and centers on `pos`.
- `draw_outlined_text(painter, center, text, font)`: white label with a
  black outline, readable over bright bodies.
- `draw_name_label(painter, name, pos, label_px)`: one outlined name
  line at a CALLER-supplied size — shared by the weekday bodies and the
  archetype figures (the SET-UNIFORM label law lives in the callers:
  [Weekday Body](weekday_body.md), [Archetype
  Geometry](archetype_geometry.md)).
- `name_label_px(name, target_width)`: the measured pixel size that
  fits `name` within `target_width`, capped/floored at
  `dial.NAME_LABEL_MAX_PX`/`BODY_LABEL_MIN_PX`.
- `tinted_gray(value, tint)`: a gray of brightness `value` through the
  TRITONE map black→tint→white — the Umbra's share of the ring recolor;
  the scalar twin of `AssetCache._tinted`.
- `draw_shadowed_text(painter, center, text, font, color)`: a
  finish-colored label over a drop shadow — subdial texts never draw
  plain white.

## Design Decisions
- **One conversion, everywhere.** `dial_point`/`draw_pie`/`pie_path`
  are the only functions that touch Qt's angle convention; every other
  module in this folder reasons entirely in the project's clockwise-
  from-top degrees.
- **No skin knowledge here.** Skin-dependent geometry (which arm, which
  wheel) lives in [Skin Geometry](skin_geometry.md); this module only
  draws what it is told.
