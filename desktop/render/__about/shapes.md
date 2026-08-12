# Shapes

**Script:** [Shapes (script)](../shapes.py) · **Flow:** [diagram](../__flow/shapes.md)

## Purpose
Star, polygon and arm PATH geometry — the `QPainterPath`/`QPolygonF`
shapes the star and aura layers paint: which arms are drawn and in
which z-order passes, the aura wedge bounds, star diamonds, curved
polygon faces, and the arm shape a skin selects.

## Connections

### Uses
- [Painting](painting.md) — `dial_point`
- [Skin Geometry](skin_geometry.md) — `arm_half_deg`, `arm_offset_deg`,
  `aura_wedge_anchor`, `polygon_faces`, `polygon_shape`,
  `rose_star_offsets`
- [Calendar Mount](calendar_mount.md) — `calendar_wedge_bounds`,
  `calendar_wheel`
- [Config (folder)](../../config/___config.md) — `constants`, `palette`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `StarLayer` (`drawn_arms`,
  `arm_shape_path`), `BackgroundLayer` (`aura_wedge_bounds`)
- [Compositor](compositor.md) — the arm hit-test reads `arm_shape_path`

## Functions
- `drawn_arms(skin, colors)`: the whole drawn wheel as (angle, hue) arm
  tuples grouped into z-ordered PASSES — one loop for every pointer and
  both shapes (star/polygon), including the Calendar's two hexagrams
  and the Rose's three stars.
- `aura_wedge_bounds(skin, palette)`: each hue's background wedge
  (start, end) dial angles — anchored on that hue's lead ray via
  `aura_wedge_anchor`.
- `star_inner_radius(skin, tip)`: where a star's own inner vertices
  sit — `tip / (2·cos(half))`.
- `polygon_curvature(skin)` / `polygon_boundary_radius(skin, tip)`: the
  applied edge-pull fraction and the radius of a polygon face's color-
  boundary corners.
- `star_diamond_path(skin, tip, theta)` / `polygon_face_path(skin, tip, theta)`:
  the two arm shapes.
- `arm_shape_path(skin, tip, theta)`: THE ONE arm-geometry entry point —
  picks the polygon face or the star diamond.

## Design Decisions
- **One loop draws every pointer and both shapes** (`drawn_arms`, Rule
  #5) — the Calendar and the Rose are special-cased for their multi-star
  geometry, everything else shares one formula.
- **Curvature only touches TRUE polygons.** The Calendar's twelve-point
  and the Rose's twenty-four-point "polygons" are stars with touching
  arms (`polygon_faces` answers False for them) and never curve.
- **The two shapes meet at the star's own inner radius** — a polygon's
  edge midpoint at full curvature (1.0) lands exactly where the star's
  side vertex already sits, so a fully-curved hexagon IS the hexagram.
