# Blue Moon — the Thirteenth Member

**Script:** [Blue Moon (script)](blue_moon.py)

## Purpose

Owner-sealed 2026-07-22: every 12-set on the dial gains a hidden 13th
member — **Ophiuchus** (the zodiac's 13th sign), **Sol** (the Sun's 13th
month, International Fixed Calendar), **Modrenik** (the Moon's 13th
month, an invented Slavic sibling), and **The Cat** (the Chinese
zodiac's 13th animal). Each exists ONLY under its own trigger and ONLY
inside its own short date window; outside trigger+window it does not
exist anywhere, dial or Encyclopedia.

Two trigger families:

- **`thirteen_moon_year`** gates Ophiuchus/Sol/Modrenik — the calendar
  year holds 13 Full Moons instead of 12 (~37% of years: the 29.53-day
  synodic month does not evenly divide the 365.24-day year). Each then
  keeps its own window: `ophiuchus_window` (Nov 29 - Dec 17, the Sun's
  real transit), `sol_window` (Jun 18 - Jul 15, carries the June
  solstice), `modrenik_window` (14 days either side of the REAL December
  solstice instant — computed, not a fixed MM-DD pair).
- **`chinese_leap_month`** gates The Cat — the REAL lunisolar leap-month
  mechanic: the lunar month between two December solstices that carries
  no zhongqi (major solar term, the Sun's apparent ecliptic longitude
  crossing a multiple of 30°). Solved via a Meeus ch. 25 low-precision
  solar-longitude series (matching `core.moon.illumination`'s own Meeus
  precedent) walking the bundled New Moon instants in China Standard
  Time. Golden-tested against two independently verified leap months:
  2023 leap 2nd (Mar 22 - Apr 19), 2025 leap 6th (Jul 25 - Aug 22) — both
  reproduced exactly against the bundled ephemeris.

`active_thirteenth` resolves which one (if any) owns the dial CENTER on
a given date, with a documented precedence for the one genuine window
overlap (Ophiuchus/Modrenik can both trigger in the Dec 7-17 band of a
blue-moon December).

Pure module — no Qt, no wall clock (purity-gated by
[Purity test](../tests/test_purity.py)). Every function takes
already-built data (`MoonWindow`, `YearAnchors`); nothing here reads a
repository or the filesystem, matching `core.continents`/`core.moon`.

## Connections

### Uses
- [Constants (script)](../config/constants.py) — `THIRTEENTHS`,
  `OPHIUCHUS_WINDOW`, `SOL_WINDOW`, `MODRENIK_WINDOW_HALF_DAYS`,
  `MOON_PHASE_FRACTIONS`.
- [Deep Time (script)](deep_time.py) — `julian_day`/`delta_t_seconds`,
  the same TT-conversion primitives `core.moon.illumination` uses.
- [Moon (script)](moon.py) — `MoonWindow`.
- [Year Wheel (script)](year_wheel.py) — `YearAnchors`.

### Used by
- [Clock State (script)](clock_state.py) — `build_day_context` computes
  `chinese_leap_month` and `active_thirteenth` ONCE per day (DAILY
  cadence, matching every other `DayContext` field) and stores them as
  `DayContext.active_thirteenth` / `DayContext.chinese_leap_month_number`
  — never recomputed on the MINUTE-cadence paint pass.
- [Layers (folder)](../render/___render.md) — `CenterBodyLayer` reads
  `DayContext.active_thirteenth` first, outranking the theme's ordinary
  center face while it holds; `_draw_calendar_mount`'s "chinese" mount
  dims the doubled month's own animal from
  `DayContext.chinese_leap_month_number`.
- [Compositor (script)](../render/compositor.md) — the center hover
  speaks the active 13th's own article first, noting that the theme's
  ordinary center steps aside.

## Functions

- `thirteen_moon_year(year, window)` — the shared trigger: 13 Full Moons
  (UTC) in `year`.
- `ophiuchus_window(year)` / `sol_window(year)` / `modrenik_window(dec_solstice)`
  — each 13th's own (first, last) inclusive window.
- `chinese_leap_month(anchors, window)` — the doubled lunar month
  (number + its own China-time span) of the sui `anchors` brackets, or
  `None`.
- `active_thirteenth(on_date, moon_window, anchors, leap)` — the
  precedence resolver: one of `config.constants.THIRTEENTHS`' keys, or
  `None`.

## Design Decisions

- **The Cat's trigger is deliberately NOT `thirteen_moon_year`.** A
  13-Full-Moon year and a 13-lunar-month Chinese sui are different
  astronomical facts that usually (not always) coincide — the task is
  explicit that The Cat rides the real lunisolar mechanic, not the
  shared solar trigger, so its window is computed independently and
  checked FIRST in `active_thirteenth`.
- **Precedence favors the more astronomically real trigger.** The only
  genuine overlap is Ophiuchus vs Modrenik (both share `thirteen_moon_year`
  and their windows touch in December); Ophiuchus wins because it names
  a real transit, Modrenik an invented sibling. The Cat outranks both
  because a real lunisolar absence is rarer and more literally computed
  than either. Sol and Modrenik never collide with each other.
- **Computed once per day, not per minute.** `chinese_leap_month`
  involves ~13 solar-longitude evaluations — cheap, but its inputs
  (`YearAnchors`, `MoonWindow`) only change once a day, so
  `build_day_context` computes it once and `CenterBodyLayer` (MINUTE
  cadence) only ever reads the stored field — the same "DayContext
  holds what changes daily" law every other field on it follows.
