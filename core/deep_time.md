# Deep Time

**Script:** [Deep Time (script)](deep_time.py)

## Purpose
The pure calendar mathematics behind the Deep Time span (Session 16,
owner 2026-07-17): era notation formatting (the ONE dual-calendar
formatter used everywhere a year displays), the astronomical-year
convention (1 BCE = year 0), the 400-year Gregorian PROXY mapping that
lets Python `datetime` (years 1–9999) carry moments across
−13000…+17000, the proleptic-Gregorian Julian Day, and the ΔT model
the analytic moon illumination needs.

## The proxy mapping (why it is exact)

Python `datetime` holds years 1–9999 only, but the Deep Time pack spans
−13000…+17000. The proleptic Gregorian calendar repeats EXACTLY every
400 years (146,097 days = 20,871 weeks): shifting any instant by whole
400-year cycles preserves month lengths, leap status, weekdays and every
interval between two equally-shifted instants. So a deep moment is
carried as a PROXY `datetime` shifted by `400 × cycles` years into the
canonical window [2000, 2399] (`PROXY_WINDOW_FIRST/LAST` in constants),
and every dial computation (year-wheel interpolation, moon-fraction
interpolation, sun arcs, weekday) runs on proxies unchanged — the
results are identical to what a deep-capable datetime would produce.
Years 2–9998 need no shift (`proxy_cycles` returns 0); 1 and 9999 shift
too because their season anchors reach one year past them.

The REAL astronomical year of a proxy datetime is
`dt.year − 400 × cycles`; display sites add `DayContext.year_shift`
(= −400 × cycles) before formatting.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — era notations, the Anno
  Lucis offset, the proxy window and cycle constants

### Used by
- [Moon](moon.md) — `julian_day` + `delta_t_seconds` for the analytic
  illumination
- [App Controller](../app/controller.md) — proxy canonicalization for
  deep travel, quick-jump unit arithmetic
- [Time Travel](../app/time_travel.md) — era combos, the dual-year
  header, coverage/tier lines
- [Deep Time Repository](../data/deep_time.md) — proxy shift for the
  pack's instants
- [Layers](../render/layers.md), [Compositor](../render/compositor.md)
  — `format_year` wherever a year renders
- [Tests (folder)](../tests/___tests.md) — era/proxy/JD/ΔT goldens

## Functions

- `format_year(astro_year, notation)`: THE dual-calendar formatter —
  `"2026"` / `"4500 BCE"` (bce_ce), `"4500 BC"` (bc_ad), `"-4499"`
  (astronomical), `"A.L. 6105"` (anno_lucis, A.L. = astronomical year
  + 4079 — owner sealed 2026-07-16). CE years in the era notations
  render WITHOUT a suffix, so the present-day dial is unchanged.
- `dual_year(astro_year, notation)`: `"4500 BCE · A.L. -420"` — the
  active notation's form beside the A.L. form (beside the CE form when
  the active notation IS Anno Lucis); the Time Travel header line.
- `era_names(notation)`: the era combo entries — `("CE", "BCE")`,
  `("AD", "BC")`, or `()` for the era-free notations.
- `display_from_astro(astro_year, notation)` /
  `astro_from_display(display_year, era_index, notation)`: the spinbox
  mapping, 1 BCE = year 0 (era_index 1 = the "before" era).
- `proxy_cycles(astro_year)`: whole 400-year cycles to ADD so the year
  AND both neighbors are datetime-representable — 0 for 2…9998, else
  into the canonical window.
- `canonical_proxy(y, m, d, hh, mm)`: `(naive proxy datetime, cycles)`
  for any astronomical calendar moment.
- `julian_day(year, month, day, day_fraction)`: proleptic-Gregorian JD
  (Meeus 7.1 with floor — valid for negative years); golden-tested
  against the research events database.
- `delta_t_seconds(year)`: the Espenak & Meeus 2006 piecewise ΔT
  polynomials — within minutes of the Swiss Ephemeris model over the
  bundled era and within ~4 h of it at the −13000/+17000 edges
  (measured 2026-07-17; the deviation is part of the deep illumination
  tolerance).
- `is_leap(year)` / `month_length(year, month)`: proleptic Gregorian,
  negative-year-safe (year 0 IS a leap year).
- `shift_calendar(year, month, day, *, years=0, months=0)`: quick-jump
  unit arithmetic — Feb 29 clamps to Feb 28 on a non-leap target, month
  ends clamp likewise; era edges are ordinary arithmetic in
  astronomical years (no year-0 gap).

## Design Decisions
- Era LABEL strings and the A.L. offset live in `config.constants`
  (settings validation needs them); the FUNCTIONS live here so config
  stays a data layer.
- The canonical proxy window opens at 2000: modern tzdata rules and the
  sun model's reference era, and any deep window [y−1, y+1] lands
  inside [1999, 2400] with slack.
