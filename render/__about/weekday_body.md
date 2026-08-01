# Weekday Body

**Script:** [Weekday Body (script)](../weekday_body.py) · **Flow:** [diagram](../__flow/weekday_body.md)

## Purpose
Drawing ONE weekday body with its name label — shared by the weekday
ring, the slots and the center seat: the label text for a body, the
single label size the whole set shares, and the body+label draw call
itself.

## Connections

### Uses
- [Context](context.md), [Painting](painting.md) — `draw_name_label`,
  `draw_pixmap_centered`, `name_label_px`
- [Skin Geometry](skin_geometry.md) — `center_duality`,
  `servant_seat_angle`, `visible_occupant`, `weekday_slots`
- [Slot Layout](slot_layout.md) — `servant_holds_the_seat`,
  `weekday_body_size`
- [Config (folder)](../../config/___config.md) — `constants`, `dial`,
  `pantheon`, `paths`
- [Core (folder)](../../core/___core.md) — `continents`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `WeekdayLayer`
  (diamond slots + center Sun), `CenterBodyLayer` (the current day's
  center image)

## Functions
- `weekday_label_text(ctx, body)`: short label below
  `WEEKDAY_FULL_NAME_MIN_DIAMETER`, full name from it up.
- `weekday_label_set_px(ctx)`: the SET-UNIFORM label size for this
  dial's weekday bodies — every name sharing the ring wears the size of
  the smallest fitted member, computed once per paint.
- `draw_body_label(painter, ctx, body, pos, size, label_px=None)`: the
  weekday-name label, using the set-uniform size when given.
- `draw_weekday_body(painter, ctx, body, pos, size, opacity, label_px=None)`:
  one weekday body (skin image or colored disc) with its outlined
  label — shared by the diamond slots and the above-the-hands center
  pass.

## Design Decisions
- **The SET-UNIFORM label law** (owner verdict 2026-07-18):
  `weekday_label_set_px` is a pure, cheap (text-measurement-only)
  function so `WeekdayLayer` (DAILY) and `CenterBodyLayer` (MINUTE) —
  two separate paint passes — agree on one label size without sharing
  mutable state.
- **The Continents theme's live body art overrides the baked plate**
  inside `draw_weekday_body` — the region's earth face follows the
  user's `earth_style` and the sky's own day/night, graceful-absent to
  the baked plate when the live face is missing.
