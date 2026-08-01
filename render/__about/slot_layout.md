# Slot Layout

**Script:** [Slot Layout (script)](../slot_layout.py) · **Flow:** [diagram](../__flow/slot_layout.md)

## Purpose
Where the seats and slots SIT — the dial's seating layout. Which slots
a skin enables, the full slot layout (position, radius and role per
slot), seat rotation/scale/orbit, the classic weekday slot, and the
duality questions that decide who holds the Sunday and the center seat.

## Connections

### Uses
- [Skin Geometry](skin_geometry.md) — `archetype_active`,
  `center_duality`, `servant_seat_angle`, `visible_occupant`,
  `weekday_slots`
- [Config (folder)](../../config/___config.md) — `constants`, `dial`,
  `pantheon`, `paths`

### Used by
- [Archetype Geometry](archetype_geometry.md) — `weekday_body_size`
- [Weekday Body](weekday_body.md) — `servant_holds_the_seat`,
  `weekday_body_size`
- [Layers (subfolder)](../layers/___layers.md) — `SlotLayer`
  (`slot_layout`, `slot_view`, the seat geometry trio),
  `WeekdayLayer`/`CenterBodyLayer` (`weekday_classic_slot`,
  `sunday_dual_face`, `center_dual_face`, `center_seat_body_key`)
- [Compositor](compositor.md) — hit-testing shares the exact same seat
  geometry as the paint

## Functions
- `enabled_slots(skin)`: the enabled slots in order — strictly
  1→2→3, empty in Archetype Mode.
- `slot_layout(skin)`: the owner's SLOT POSITION MATRIX — slot index →
  seat (`"classic"`, `"center"`, or a dial angle), branched by pointer
  and slot count.
- `slot_seat_rotation(skin, rotation)` / `slot_seat_scale(skin)` /
  `slot_seat_orbit(skin, seat)`: the seat geometry trio shared by paint
  and hit-test.
- `weekday_body_size(skin, radius)` / `weekday_body_orbit(skin)`: the
  ONE size for every weekday body (diamond slots AND the hexa/trio
  center Sun), and the romb-center orbit fraction.
- `weekday_classic_slot(skin)`: which slot (if any) drives the classic
  weekday unit.
- `slot_view(skin, index)`: a slot's (mode, style, theme, metal,
  roster) — the roster is per slot.
- `sunday_dual_face(skin)` / `center_dual_face(skin)`: whether the
  Servant holds his OWN seat, or the duality lives in one center image
  — mutually exclusive given a dual asset exists.
- `servant_holds_the_seat(skin, today)`: whether the Servant wins his
  seat today, by the shared-slot priority rule.
- `center_seat_body_key(skin, today)`: which body key occupies the
  classic unit's center seat, independent of any duality.

## Design Decisions
- **The owner's slot count/pointer matrix is written as one function**
  (`slot_layout`), not a per-pointer subclass — the mapping is data
  shaped like a table, not behavior that varies.
- **`sunday_dual_face` and `center_dual_face` are complementary, never
  both true.** Given a theme's dual asset exists, a Sunday resolves
  through exactly one of the two seat laws.
