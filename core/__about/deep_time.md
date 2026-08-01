# Deep Time

**Script:** [Deep Time (script)](../deep_time.py) · **Flow:** [diagram](../__flow/deep_time.md)

## Purpose
Pure calendar mathematics behind the Deep Time span: era-notation
formatting (the one dual-calendar formatter used everywhere a year
displays), the astronomical-year convention (1 BCE = year 0), the
400-year Gregorian PROXY mapping that lets Python `datetime` (years
1-9999) carry moments across roughly -13000...+17000, the
proleptic-Gregorian Julian Day, the Espenak & Meeus 2006 ΔT model, the
true Maya Long Count, and three more third-calendar shapes (Kali Yuga,
Olympiad, Unix time).

## The proxy mapping (why it is exact)
The proleptic Gregorian calendar repeats EXACTLY every 400 years
(146,097 days = 20,871 weeks): shifting any instant by whole 400-year
cycles preserves month lengths, leap status, weekdays and every interval
between two equally-shifted instants. A deep moment is carried as a
PROXY `datetime` shifted by `400 x cycles` years into the canonical
window `[PROXY_WINDOW_FIRST, PROXY_WINDOW_FIRST + 399]`, and every dial
computation (year-wheel interpolation, moon-fraction interpolation, sun
arcs, weekday) runs on the proxy unchanged. Years 2-9998 need no shift
(`proxy_cycles` returns 0); 1 and 9999 shift too because their season
anchors reach one year past them. The real astronomical year of a proxy
is `real_year(proxy_year, cycles) = proxy_year - cycles * GREGORIAN_CYCLE_YEARS`.

## The three THIRD_ERA shapes
`format_year_line`'s `third_era` argument dispatches to one of three
shapes:
1. **Uniform offset** (`third_era_year`, `constants.THIRD_ERA_OFFSETS`)
   — most eras (AUC, Byzantine, Hebrew, Chinese, Kali Yuga) are a
   constant `+N` on the astronomical-year axis; Anno Hegirae is the one
   exception, a lunar display-grade approximation
   `AH ~= (CE - 622) * 33/32`.
2. **Year-only formatter** (`olympiad_year`) — the ancient Olympiad, a
   4-year cycle count from 776 BCE (astro -775,
   `constants.OLYMPIAD_EPOCH_YEAR`); ground-truthed against a second
   independent anchor (293rd Olympiad = 393 CE).
3. **Date-level formatter** (`maya_long_count`, `unix_epoch_seconds`) —
   both need the full displayed `(month, day)`, not just the year, since
   both are true day counts from a fixed epoch, walked via
   `julian_day(..., day_fraction=0.5)` (noon lands exactly on the
   integer JDN).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — era notations, the
  Anno Lucis offset, the Maya epoch JDN, the proxy window and cycle
  constants

### Used by
- [Moon](moon.md) — `julian_day` + `delta_t_seconds` for the analytic
  illumination
- [Blue Moon](blue_moon.md) — `julian_day` + `delta_t_seconds` for the
  solar-longitude (zhongqi) series
- [Watch Controller](../../app/__about/controller.md) — proxy canonicalization
  for deep travel, quick-jump unit arithmetic
- [Time Travel](../../app/__about/time_travel.md) — era combos, the dual-year
  header, coverage/tier lines
- [Deep Time Repository](../../data/__about/deep_time.md) — proxy shift
  for the pack's instants
- [Layers](../../render/layers/___layers.md), [Compositor](../../render/__about/compositor.md)
  — `format_year_line` wherever a year renders
- [Tests (folder)](../../tests/___tests.md) — era/proxy/JD/ΔT goldens

## Functions

- `format_official(astro_year, notation, show_suffix=False)`: the
  OFFICIAL year form — positive years bare (`"2026"`) unless
  `show_suffix`; negative years always carry the era label
  (`"44 BCE"`/`"44 BC"`).
- `format_anno_lucis(astro_year)`: `"6105. Anno Lucis"` —
  `astro_year + ANNO_LUCIS_OFFSET`.
- `format_year_line(astro_year, notation, show_suffix=False, third_era="none", month=1, day=1)`:
  THE dual-calendar formatter — official year + Anno Lucis, plus the
  optional third calendar.
- `is_age_of_light(astro_year)`: True within the sealed span
  `AGE_OF_LIGHT_START_YEAR..AGE_OF_LIGHT_END_YEAR`.
- `third_era_year(astro_year, third_era)`: the offset eras' third-year
  value (not called for "maya"/"olympiad"/"unix").
- `olympiad_year(astro_year)`: `"N. Olympiad · Year K"`.
- `maya_long_count(astro_year, month, day)`: `"baktun.katun.tun.uinal.kin"`.
- `unix_epoch_seconds(astro_year, month, day)`: seconds since the Unix
  epoch to the displayed date's own midnight UTC.
- `era_names(notation)`: `(current, before)` label pair.
- `display_from_astro(astro_year)` / `astro_from_display(display_year, era_index)`:
  the moment-editor spinbox mapping (1 BCE = year 0).
- `proxy_cycles(astro_year)`: whole 400-year cycles to add so the year
  and both neighbors are datetime-representable.
- `canonical_proxy(year, month, day, hour=0, minute=0)`: `(naive proxy
  datetime, cycles)`.
- `real_year(proxy_year, cycles)`: the astronomical year of a proxy
  datetime's year.
- `is_leap(astro_year)` / `month_length(astro_year, month)`: proleptic
  Gregorian, negative-year-safe (year 0 IS leap).
- `shift_calendar(year, month, day, *, years=0, months=0)`: quick-jump
  unit arithmetic, day clamped to the target month's length.
- `julian_day(year, month, day, day_fraction=0.0)`: proleptic-Gregorian
  Julian Day (Meeus 7.1 with floor).
- `julian_day_of(when, cycles=0)`: JD of a tz-aware moment, un-shifting
  the proxy frame first.
- `delta_t_seconds(year)`: TT - UT seconds, the Espenak & Meeus 2006
  piecewise polynomials (nine branches by year range).

## Design Decisions
- Era LABEL strings and the Anno Lucis offset live in `config.constants`
  (settings validation needs them); the FUNCTIONS live here so config
  stays a data layer.
- The canonical proxy window opens at year 2000 — modern tzdata rules
  and the sun model's reference era; any deep window `[y-1, y+1]` lands
  inside `[1999, 2400]` with slack.
