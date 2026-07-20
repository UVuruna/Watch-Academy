# Deep Time

**Script:** [Deep Time (script)](deep_time.py)

## Purpose
The pure calendar mathematics behind the Deep Time span (Session 16,
owner 2026-07-17): era notation formatting (the ONE dual-calendar
formatter used everywhere a year displays), the astronomical-year
convention (1 BCE = year 0), the 400-year Gregorian PROXY mapping that
lets Python `datetime` (years 1–9999) carry moments across
−13000…+17000, the proleptic-Gregorian Julian Day, the ΔT model the
analytic moon illumination needs, and (MAYA round, owner 2026-07-20)
the TRUE Maya Long Count — the one THIRD_ERAS entry that is a pure day
count rather than a year offset.

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

<a id="maya-long-count"></a>

## The Maya Long Count (MAYA round, owner 2026-07-20)

Owner question: "Jel Maje nisu imale kalendar? Zašto nemamo njihov?"
— every other `THIRD_ERAS` entry is a uniform "CE + N" offset on the
astronomical-year axis (`third_era_year`), but the Maya Long Count has
no year concept at all: it is a TRUE DAY COUNT from a fixed epoch, the
same shape as this project's own Julian Day machinery. `maya_long_count`
walks the displayed calendar DATE's Julian Day Number instead of the
year:

1. `julian_day(year, month, day, 0.5)` — noon (`day_fraction=0.5`)
   lands exactly on the integer JDN (the `.5` cancels the formula's own
   `-1524.5` constant), the same trick the eclipse lookups already use.
2. `days = int(jdn) - constants.MAYA_EPOCH_JDN` — the GMT correlation
   epoch, JDN 584,283 (11 August 3114 BCE proleptic Gregorian, 6
   September 3114 BCE Julian).
3. Radix chain, largest to smallest: baktun (144,000 days) → katun
   (7,200) → tun (360) → uinal (20) → kin (1) — `divmod` all the way
   down, formatted `"baktun.katun.tun.uinal.kin"`.

Golden-tested against two independently known anchors that turned out
mutually consistent from the sealed epoch alone (`tests/test_deep_time.py`):
21 December 2012 = 13.0.0.0.0, 1 January 2000 = 12.19.6.15.2 — the
second value cross-checked against the first via plain `datetime.date`
subtraction (independent of `julian_day`), agreeing exactly. Because
the Long Count needs a full DATE and not just a year, `format_year_line`
grew two new (defaulted, backward-compatible) parameters, `month`/`day`
— every caller whose `third_era` can be "maya" passes the real
displayed date; the offset eras ignore them entirely.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — era notations, the Anno
  Lucis offset, the Maya epoch JDN, the proxy window and cycle
  constants

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
  — `format_year_line` wherever a year renders
- [Tests (folder)](../tests/___tests.md) — era/proxy/JD/ΔT goldens

## Functions

- `format_official(astro_year, notation, show_suffix)`: the OFFICIAL
  year form — positive years bare (`"2026"`) unless `show_suffix` opts
  the label in; negative years ALWAYS carry it (`"44 BCE"`/`"44 BC"`).
- `format_year_line(astro_year, notation, show_suffix, third_era, month, day)`:
  THE dual-calendar formatter — the official year with the Anno Lucis
  year always beside it (`"2026 · 6105. Anno Lucis"`), plus the
  optional third calendar (`"… · 2779. AUC"`). `month`/`day` (MAYA
  round, owner 2026-07-20, default 1 Jan) matter ONLY for `third_era
  == "maya"` — see [The Maya Long Count](#maya-long-count) above;
  every other era ignores them.
- `third_era_year(astro_year, third_era)`: the offset eras' third-
  calendar year — uniform `+N` on the astronomical axis, except Anno
  Hegirae's lunar display-grade approximation. NOT called for "maya"
  (a day count, not a year offset) — `format_year_line` special-cases
  that branch to `maya_long_count` instead.
- `maya_long_count(astro_year, month, day)` (MAYA round, owner
  2026-07-20): the true Long Count string, `"baktun.katun.tun.uinal.kin"`
  — see the dedicated section above.
- `format_anno_lucis(astro_year)` (owner fix-round B, 2026-07-19): just
  the Anno Lucis half of the year line — `"6105. Anno Lucis"` —
  derived ONCE and reused by both `format_year_line` and the Earth
  hover card's own era block (`render.compositor._earth_text`).
- `is_age_of_light(astro_year)` (owner fix-round B, 2026-07-19): True
  within the sealed Age of Light span — astronomical −4078…6423
  inclusive (4079 BCE → 6423 CE,
  `research/ephemeris/anno_lucis.json`) — else the Age of Darkness;
  the boundary constants (`AGE_OF_LIGHT_START/END_YEAR`) live in
  `config.constants`. The Earth hover card's era badge/title is its
  only caller today.
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
