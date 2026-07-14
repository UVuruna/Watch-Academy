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
  city prefill, duration
- [UI Style](ui_style.md) — the shared vivid button pills

### Used by
- [App Controller](controller.md) — `_open_time_travel()` feeds the
  frozen (moment, observer) into the tick flow

## Classes

### TimeTravelDialog
Stay-on-top `QDialog`: `QDateTimeEdit` (calendar popup) + two
`QDoubleSpinBox` for latitude/longitude, prefilled with now/Belgrade
(a running simulation seeds them instead). The button row wears the
shared vivid style (owner 2026-07-15): blue **Now** on the LEFT —
closes with `RETURN_TO_NOW`, the controller ends the simulation and
the dial returns to the present immediately — then green OK and
neutral Cancel on the right.

#### Methods
- `moment()`: naive wall time (controller attaches the timezone)
- `latitude()` / `longitude()`
- `RETURN_TO_NOW`: the third dialog result code, produced by Now
