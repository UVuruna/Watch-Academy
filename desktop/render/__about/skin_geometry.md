# Skin Geometry

**Script:** [Skin Geometry (script)](../skin_geometry.py) · **Flow:** [diagram](../__flow/skin_geometry.md)

## Purpose
Skin → geometry queries: every "what does THIS skin say" question a
layer asks — palettes, arm counts and half-angles, the wheel and its
Sunday duality, the seat angles, which laws are active (daylight, cube
look, archetype) and where the weekday slots sit. Pure functions of a
`SkinDefinition`; no painting.

## Connections

### Uses
- [Context](context.md) — `RenderContext` (`hover_factor` only)
- [Config (folder)](../../config/___config.md) — `archetypes`,
  `constants`, `palette`
- [Skins (folder)](../../skins/___skins.md) — `SkinDefinition`

### Used by
- [Shapes](shapes.md), [Slot Layout](slot_layout.md), [Archetype
  Geometry](archetype_geometry.md), [Weekday Body](weekday_body.md),
  [Daylight](daylight.md) — every arm/wheel/duality/daylight query
- [Layers (subfolder)](../layers/___layers.md), [Compositor](compositor.md)
  — hit-testing and paint alike read the SAME functions the layers do
  (Rule #5 — one source of truth per question)

## Functions
- `palette_for(skin)` / `aura_palette_for(skin)`: the active Star+Aura
  base palette, raw vs. Aura-Saturation-scaled.
- `arm_offset_deg(skin)`: THE OFFSET WHEELS table — the Genesis
  inversion (180° on the trio's tertiary wheel) and the Seasons
  rotation (45° on the cross's tertiary wheel); 0 elsewhere.
- `aura_wedge_anchor(skin)`: where a hue's background wedge sits
  relative to its lead ray — arm-centered by default, Rose-specific
  otherwise.
- `polygon_shape(skin)` / `polygon_faces(skin)` / `drawn_arm_count(skin)`
  / `arm_half_deg(skin)`: the star-vs-polygon shape question and the
  arm count/half-angle it implies.
- `rose_star_offsets(skin)` / `rose_star_set(offset)`: the Rose's three
  stars in draw order and each one's figure set.
- `horizontal_duality(skin)` / `center_duality(skin)`: whether a skin's
  Sunday duality rides a blue↔red axis, a vertical axis, or lives in
  one center image.
- `ruler_seat_angle(skin)` / `servant_seat_angle(skin)`: the Ruler's and
  Servant's dial seats, flipped by `_duality_flipped` for the
  Sacred-Axis/geographic theme exceptions.
- `daylight_active(skin)`: whether the day/night law paints this dial —
  always True except the Calendar's/Rose's own switch.
- `cube_look_active(skin)`: whether the CUBE look dresses the drawn
  wheel (Double-Trinity family wheels only).
- `weekday_slots(skin)`: the skin's weekday slots as DRAWN — arm offset
  applied, the Sun pulled into the center or relocated by a duality
  flip.
- `hover_factor(ctx, element)`: the hover-enlarge multiplier.
- `visible_occupant(occupants, today)` / `today_slot_theta(skin, today)`:
  shared-slot priority and today's own slot angle.
- `archetype_key(skin)` / `archetype_active(skin)`: the active
  archetype grid entry, and whether Archetype Mode overrides the dial.
- `wheel_rotation(skin, rotation)`: the drawn wheel's rotation — the
  solar offset, except the Calendar (wedge-fixed).

## Design Decisions
- **One function per question (Rule #5).** Every skin query a layer,
  the compositor's hit-test, and the tests all need is answered by
  exactly one function here — never duplicated inline at a call site.
- **RAW palette vs. Aura-scaled palette are two different functions**
  (`palette_for` vs. `aura_palette_for`) because the Saturation slider
  must move ONLY the background wedges, never the star diamonds
  themselves (owner fix round E, 2026-07-19).
