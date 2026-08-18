# Controller — Time Travel

**Script:** [Controller Simulation (script)](../controller_simulation.py)
· **Flow:** [diagram](../__flow/controller_simulation.md)

## Purpose
The moment the watch is showing when it is not now. `_TimeTravelMixin`
is one of the five responsibility mixins
[Watch Controller](controller.md) inherits (WA-R14 of the
[OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-19).

It holds the jump arithmetic, the simulation lifecycle and the Time
Travel dialog that drives them. It reads the same repositories the live
tick does, so a traveled dial and a live dial are never two code paths.

## Connections

### Uses
- [Time Travel](time_travel.md) — the dialog and its Quick Jump rows
- [Core (folder)](../../core/___core.md) — `build_tick_state`,
  `date_is_solstice`, `deep_time.*` (`canonical_proxy`, `julian_day_of`,
  `proxy_cycles`, `shift_calendar`)
- [Data (folder)](../../data/___data.md) — the PROCESS-WIDE
  `shared_deep_time`, `shared_moon_phases`, `shared_seasons` accessors
- [Config (folder)](../../config/___config.md) — `constants`,
  `defaults` (the Fast Travel themes), `shortcuts`

### Used by
- [Watch Controller](controller.md) — inherits the mixin; `_on_tick`
  reads `_simulated_moment()` on every tick
- [Controller Shortcuts](controller_shortcuts.md) — `_apply_jump` is
  where every Fast Travel step lands
- [Controller Dialogs](controller_dialogs.md) — the Observatory reads
  `_active_simulation_or_now()`

## Class attributes (they travelled with their group)
- `_UNIT_JUMPS` — the calendar units (day/month/year/century/millennium)
- `_ECLIPSE_JUMP_PATTERN` — `next`/`prev`, `solar`/`lunar`, and an
  OPTIONAL catalog type suffix fed straight to
  `data.deep_time.eclipse_after`/`eclipse_before`'s `type_` filter
- `_TIME_JUMPS` — hour/minute/second, returned WITHOUT the
  minute-flooring tail the calendar branch applies (flooring a
  one-second step would erase it)

## Module-level names
- `_SUN_MOON_JUMP_PATTERN` — `(next|prev)_(sun|moon)` with an optional
  phase suffix, so ONE `_compute_jump` branch answers both the Time
  Travel dialog's broad rows and Fast Travel's narrowed ones
- `_SOLSTICE_ANCHOR_INDICES` / `_EQUINOX_ANCHOR_INDICES` /
  `_QUARTER_MOON_FRACTIONS` — the index and fraction tables the filters read
- `_filtered_sun_anchors(instants, phase_filter)` /
  `_filtered_moon_events(events, phase_filter)` — the year's anchors and
  principal phases, narrowed only when the filter asks

## The methods
- `_compute_jump(...)` — the pure arithmetic behind every travel entry
  point; returns the landed `(moment, observer, cycles)` or `None` on an
  edge clamp
- `_apply_jump` (shortcuts) · `_dialog_jump` (the dialog's Quick Jump
  rows, which also mirrors the landing back onto the dialog's fields)
- `_start_simulation` / `_end_simulation` / `_simulated_moment` /
  `_active_simulation_or_now`
- `_effective_travel_date` / `_effective_is_daylight` /
  `_verses_in_the_open` — what the rest of the app asks about a
  traveled moment
- `_open_time_travel` — the dialog host, kept here because it wires the
  jump callback and the city list this module owns

## Design Decisions
- **The landed moment is not a frozen frame** (owner spec 2026-08-11):
  `_start_simulation` anchors `_sim_started = monotonic()` and
  `_simulated_moment()` adds the real elapsed seconds back on every
  read, so a traveled dial shows a running transition (day into night,
  an eclipse closing). Every reader goes through `_simulated_moment()`
  rather than the stored tuple.
- **The filters are module-level functions, not methods** — they take
  instants and return instants, touch no `self`, and are unit-tested
  directly by `tests/test_shortcuts_r5b.py`.
