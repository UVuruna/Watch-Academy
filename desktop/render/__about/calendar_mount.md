# Calendar Mount

**Script:** [Calendar Mount (script)](../calendar_mount.py) · **Flow:** [diagram](../__flow/calendar_mount.md)

## Purpose
The calendar wheel and the 12-SET pointer mounts: which of the
Calendar's two wheels (Zodiac / Almanac) is active, its wedge bounds
and day arrow, plus the DESIGN ZODIAC law's twelve-seat mounts (zodiac,
months, Chinese animals, Slavic months, …) — each mount's own wheel,
per-index angle, mark height, art entries and the currently-lit index.

## Connections

### Uses
- [Context](context.md), [Painting](painting.md) — `dial_point`,
  `draw_name_label`, `draw_pixmap_centered`
- [Subdial](subdial.md) — `octa_slot_art`
- [Config (folder)](../../config/___config.md) — `calendar_mounts`,
  `constants`
- [Core (folder)](../../core/___core.md) — `DayContext`, `TickState`,
  `almanac_marker_angle`, `almanac_month_index`

### Used by
- [Shapes](shapes.md) — `calendar_wedge_bounds`, `calendar_wheel` (the
  Calendar pointer's own arm geometry)
- [Ninths](ninths.md) — `calendar_wheel` (the Blue Moon Law's wheel-picked
  thirteenth)
- [Layers (subfolder)](../layers/___layers.md) — `BackgroundLayer` calls
  `_draw_calendar_mount` after its wedge loop
- [Compositor](compositor.md) — the mount seat hover (`_calendar_mount_tooltip`)

## Functions
- `calendar_wheel(skin)`: which wheel is active — `palette_style`
  carries it (paint = Zodiac, light = Almanac).
- `calendar_wedge_bounds(wheel)`: the twelve wedge (start, end) dial
  angles — Zodiac boundaries ON the cardinals, Almanac wedges CENTERED
  on them.
- `calendar_day_arrow(angle_deg, radius)`: the Almanac Earth-marker
  day-arrow triangle.
- `calendar_mount_wheel(mount)`: which wedge geometry a mount's marks
  ride, read from the roster's own Dozen System (A/B).
- `calendar_mount_angle(mount, index)` / `calendar_mount_mark_height(mount, radius)`:
  THE SEAT LAW — one formula for a 12-seat or a 24-seat mount, no
  per-seat table.
- `calendar_mount_entries(mount)`: the mount's (name, art-or-None) pairs
  in seat order, always graceful-absent.
- `calendar_mount_current_index(mount, day)`: the seat TODAY owns, by
  the roster's own `follows` declaration (`"sign"` / `"month"` / `None`).
- `chinese_mount_dimmed_index(day)`: THE CAT'S DIMMING LAW — which seat
  dims while The Cat holds the dial center.
- `_draw_calendar_mount(painter, ctx, mount)`: the DAILY paint pass —
  one mark per seat, missing art falls back to a name label.

## Design Decisions
- **A mount rides its OWN fixed geometry**, independent of whichever
  wheel the background wedges currently paint — the marks never jump
  when the owner switches Zodiac/Almanac colors.
- **THE SEAT LAW is one formula, no per-roster table** (owner decree
  2026-07-29, root Rule #19): a 12-set's bracket vanishes and each
  member sits on its wedge center; a 24-set's two members sit a quarter
  wedge either side.
