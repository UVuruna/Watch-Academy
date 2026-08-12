# Time Travel

**Script:** [Time Travel (script)](../time_travel.py) · **Flow:** [diagram](../__flow/time_travel.md)

## Purpose
The owner's scenario tester: enter any moment and any latitude/longitude
— the dial renders that exact situation for `TIME_TRAVEL_DURATION_S`,
then returns to the present by itself. The moment editor accepts any
year of the active coverage INCLUDING BCE (a day spinbox + month combo +
year spinbox + an era combo, since `QDateTimeEdit` cannot hold negative
years). Since R5 MENU REWORK the dialog also GROWS DOWN with its own
Quick Jump section, absorbing the old right-click menu's whole deep
Quick Jump submenu chain; since TT LIVE TRAVEL (R8b) every Quick Jump
row/arrow click travels the LIVE watch immediately, not only on OK.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — coordinate ranges,
  duration, the warning color, the advertised Deep Time span, era
  constants, row icon/arrow pixel sizes
- [Deep Time (core)](../../core/__about/deep_time.md) — era mapping, the
  proxy frame, month lengths, the year-line formatters
- [UI Style](ui_style.md) — the shared vivid button pills
- [Theme](theme.md) — the dark dialog surface, the moment editor's
  combos/spinboxes, `size_to_screen`

### Used by
- [Watch Controller](controller.md) — `_open_time_travel()` passes the
  active coverage, the bundled core coverage, the year-line settings and
  the Deep Time pack flag, plus `jump_callback=self._dialog_jump` and
  `jump_cities=self._settings.jump_cities`

## Classes

### TimeTravelDialog(QDialog)
Stay-on-top. Internally every date is the ASTRONOMICAL year (1 BCE =
year 0); `moment()` returns the 400-year PROXY datetime and `cycles()`
its cycle count. The day spinbox re-clamps live to the proleptic month
length.

#### Methods
- `astro_year()`: the entered astronomical year
- `moment()` / `cycles()`: the naive proxy wall time (the controller
  attaches the active timezone) and its cycle count
- `target_within_coverage()`: True when the entered year lies inside the
  supplied ACTIVE coverage (always True when none was supplied)
- `accept()`: refuses an out-of-range target INLINE (message states the
  Laskar-tier or "install the Deep Time pack" reason, dialog stays open)
  instead of accepting
- `RETURN_TO_NOW`: the third dialog result code (2), produced by the
  "Now" button — ends the simulation immediately
- `_build_jump_section()`: the Quick Jump `QGroupBox` inside a
  `QScrollArea` — turning-point rows (Sun/Moon/eclipses/Day/Month/Year/
  Century/Millennium, `_turning_point_row`, only the arrows are
  clickable) and place rows (North/South Pole, Greenwich, every
  `jump_cities` entry, `_place_button`, single click)
- `_on_jump(kind, city=None)`: calls the constructor's `jump_callback`
  (the controller's `_dialog_jump`, itself built on `_compute_jump`)
  with THIS dialog's own current fields; the callback both travels the
  live watch AND returns the landed state for `_apply_moment` to mirror
  back onto the dialog's own widgets
- `_apply_moment(moment, cycles)`: loads a landed jump into the
  moment-editor widgets, signals blocked so one row click repaints
  `_refresh()` exactly once
- `_refresh_pole_buttons()`: the pole rows' text follows the DIALOG's
  own displayed date (the light/dark seasonal glyph), refreshed after
  every `_apply_moment`
