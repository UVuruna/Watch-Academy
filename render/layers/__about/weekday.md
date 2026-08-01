# Weekday Layer

**Script:** [Weekday Layer (script)](../weekday.py) ·
**Flow:** [diagram](../__flow/weekday.md)

## Purpose

Paints the seven weekday bodies on the pointer's arm slots, rotating WITH
the star, BELOW the hands. The hexa and trio pointers keep the Sun centered;
cross/octa give every body its own slot — shared slots show only the
priority winner (`visible_occupant`). Two display modes: "ghost" (every
visible slot, non-current faint) and "center_only" (nothing here — the
current day's body draws in the center instead, via `CenterBodyLayer`,
ABOVE the hands). Also draws the SERVANT face at the 24h seat for
dual-Sunday themes, including the two-badge Ninth windows near solar
noon/midnight that borrow the Ruler's or Servant's seat.

`Cadence.DAILY`: which body is "today" changes once a day. `hover_variable
= True`: hover-enlarge and the reveal window change these bodies'
appearance every frame, so the compositor never bakes this layer into the
cached composite — it paints live (owner 2026-07-17, ROADMAP 15f); a hover
enter/leave rebuilds nothing.

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Ninths](../../__about/ninths.md) — `dual_seat_ninth`, `ninth_alt_active`, `theme_ninth`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_pixmap_centered`
- [Skin Geometry](../../__about/skin_geometry.md) — `center_duality`, `hover_factor`,
  `servant_seat_angle`, `visible_occupant`, `weekday_slots`
- [Slot Layout](../../__about/slot_layout.md) — `servant_holds_the_seat`,
  `weekday_body_orbit`, `weekday_body_size`, `weekday_classic_slot`
- [Weekday Body](../../__about/weekday_body.md) — `draw_weekday_body`,
  `weekday_label_set_px`

### Used by
- [Compositor](../../__about/compositor.md) — third layer in the default `z_order` (skips
  when `show_weekday` is off; replaced by `ArchetypeLayer` in Archetype
  mode)
- [Hover Lift Layer](hover_lift.md) — a `lift=True` twin repaints the
  hovered body above the hands

## Classes

### WeekdayLayer
`cadence = Cadence.DAILY`, `hover_variable = True`.
- `paint()`: no-ops when every slot is seated (`weekday_classic_slot` is
  None — the seated slots draw instead) or in `center_only` mode; otherwise
  draws the center-duality Sun (hexa/trio wheels, unless today is Sunday or
  the reveal window is active), then every occupied arm slot at its orbit
  and rotation, then the Servant face at the 24h seat if the theme has one.
