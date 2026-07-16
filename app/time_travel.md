# Time Travel

**Script:** [Time Travel (script)](time_travel.py)

## Purpose
The owner's scenario tester, opened from the menu: enter any moment
(calendar picker) and any latitude/longitude — the dial renders that
exact situation (sun arc, hexagram tilt, Earth and Moon positions, moon
phase, hovers) for `TIME_TRAVEL_DURATION_S`, then returns to the present
by itself. The entered wall time is interpreted in the active timezone.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — coordinate ranges, default
  city prefill, duration, the coverage-warning color and the Deep Time
  advertised span
- [UI Style](ui_style.md) — the shared vivid button pills

### Used by
- [App Controller](controller.md) — `_open_time_travel()` passes the
  bundled coverage in (`_travel_coverage()`, the seasons ∩ moon
  intersection) and feeds the frozen (moment, observer) into the tick flow

## Classes

### TimeTravelDialog
Stay-on-top `QDialog`: `QDateTimeEdit` (calendar popup) + two
`QDoubleSpinBox` for latitude/longitude, prefilled with now/Belgrade
(a running simulation seeds them instead). The button row wears the
shared vivid style (owner 2026-07-15): blue **Now** on the LEFT —
closes with `RETURN_TO_NOW`, the controller ends the simulation and
the dial returns to the present immediately — then green OK and
neutral Cancel on the right.

**Coverage guard (owner 2026-07-16).** The moment editor spans the whole
representable calendar (year 1 → 9999, widened past Qt's default 1752
floor) so the owner can dial into deep time and READ the message rather
than have an ancient target silently clamped. When OK is pressed with a
target OUTSIDE the bundled `coverage` (the seasons ∩ moon year span the
controller supplies), a red inline label appears — "Time Travel covers
{first}–{last} for now — the Deep Time data pack extends it to
−13000…+17000 (coming)" — and the dialog stays open WITHOUT travelling,
so Time Travel can never reach the day build's die-visibly SystemExit box.
A far-future/ancient jump that used to close the whole app now just
explains itself.

#### Methods
- `moment()`: naive wall time (controller attaches the timezone)
- `latitude()` / `longitude()`
- `target_within_coverage()`: True when the entered year lies inside the
  supplied coverage (always True when none was given) — the guard tested
  directly, and the gate `accept()` checks before travelling
- `accept()`: refuses an out-of-range target inline (shows the message,
  stays open) instead of accepting
- `RETURN_TO_NOW`: the third dialog result code, produced by Now
