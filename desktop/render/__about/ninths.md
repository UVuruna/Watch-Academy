# Ninths

**Script:** [Ninths (script)](../ninths.py) · **Flow:** [diagram](../__flow/ninths.md)

## Purpose
The Ninth and the thirteenth plate — the dial's extra seats. A theme's
Ninth table and which Ninth is active, whether the alternate Ninth
holds the window, which face the center shows right now, and the
thirteenth (blue-moon / leap) plate and its art.

## Connections

### Uses
- [Context](context.md), [Subdial](subdial.md) — `octa_slot_art`
- [Calendar Mount](calendar_mount.md) — `calendar_wheel`
- [Config (folder)](../../config/___config.md) — `calendar_mounts`,
  `constants`, `defaults`, `pantheon`, `paths`
- [Core (folder)](../../core/___core.md) — `angles`, `continents`,
  `DayContext`, `TickState`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `CenterBodyLayer`
  (`active_thirteenth`, `theme_ninth`, `center_face`,
  `ninth_alt_active`)
- [Compositor](compositor.md) — the hover text shares every one of
  these functions with the paint pass (Rule #5)

## Functions
- `thirteenth_plate(key)`: (display name, resolved art) of a Blue Moon
  13th — graceful-absent like every other plate here.
- `active_thirteenth(skin, day)`: the Calendar pointer's own showing
  13th, or `None` on every other pointer — a mount that names one
  outranks the wheel's own (Ophiuchus/Sol).
- `ninth_table_for(theme, active_alt)`: THE MECHANISM DISPATCH — which
  alt-Ninth table (if any) a theme's Double-Ninth mechanism reads
  (`"easter_egg"`, `"daynight"`, `"term_weekly"`).
- `theme_ninth(theme, active_alt=False, on_date=None)`: (name, art) of
  a theme's Ninth plate, existence-gated, optionally rotated by
  `on_date`.
- `ninth_alt_active(ctx)`: whether the Ninth's ALT face shows right now
  — reads the day's own pre-built anchors or `TickState.is_daylight`,
  never recomputed astronomy.
- `ninth_window_anchor(day, tick)`: `"noon"` / `"midnight"` / `None` —
  which solar ±window the hour hand stands in.
- `center_face(day, tick, has_ninth)`: which face the center's Sunday
  duality shows — `"ruler"` by day, `"servant"` by night, `"ninth"` in
  both solar windows for a theme that names one.
- `dual_seat_ninth(day, tick)`: which SEAT the Ninth's badge borrows on
  a two-badge Sunday, near either solar window.

## Design Decisions
- **The center's face is decided by the SKY, not the wall clock**
  (`center_face`) — every window reads `day.sun.noon` through
  `core.angles.hours_between`, the same anchor the hexagram's own
  rotation reads.
- **A Ninth's existence gate is graceful-absent** (`theme_ninth`
  returns `None` for a theme with no table entry or unlanded art) —
  the SAME lookup the paint pass and the hover share, so they can never
  disagree about whether a Ninth shows.
