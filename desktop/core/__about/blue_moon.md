# Blue Moon — the Thirteenth Member

**Script:** [Blue Moon (script)](../blue_moon.py) · **Flow:** [diagram](../__flow/blue_moon.md)

## Purpose

THE BLUE MOON LAW (owner-sealed 2026-07-22, corrected 2026-07-22): every
12-set on the dial gains a hidden 13th member — **Ophiuchus** (the
zodiac's 13th sign), **Sol** (the Sun's 13th month), **Modrenik** (the
Moon's 13th month), and **The Cat** (the Chinese zodiac's 13th animal).
Each exists ONLY under its own trigger, inside its own short date
window; outside trigger+window it does not exist anywhere on the dial or
in the Encyclopedia.

THE AXLE LAW (owner-sealed 2026-07-29) adds a second kind of thirteenth:
the **ALWAYS-CENTERS** (`config.constants.AXLE_ALWAYS_CENTERS` — Hestia,
Jesus, Prudence, Cunning, Peace, Hardness of Heart), which carry NO
trigger and NO window — they stand on every date, because they are the
axles their own wheels turn on, not months a twelve-month calendar
overflows into.

Two trigger families for the four calendar-driven members:
- **`thirteen_moon_year`** gates Ophiuchus/Sol/Modrenik — the calendar
  year holds 13 Full Moons instead of 12 (~37% of years — 365.24 / 29.53
  = 12.37 synodic months/year, so a year never lands exactly on 12).
  Each then keeps its own window (`ophiuchus_window`, `sol_window`,
  `modrenik_window`).
- **`chinese_leap_month`** gates The Cat — the real lunisolar leap-month
  mechanic: the lunar month between two December solstices that carries
  no zhongqi (major solar term). Golden-tested against two independently
  known leap months (`tests/test_blue_moon.py`): 2023 leap 2nd
  (Mar 22 - Apr 19), 2025 leap 6th (Jul 25 - Aug 22).

Pure module (no Qt, no wall clock) — purity-gated by
[Purity Test (script)](../../tests/test_purity.py). Every function takes
already-built data (`MoonWindow`, `YearAnchors`); nothing here reads a
repository or the filesystem, matching [Continents](continents.md) and
[Moon](moon.md).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `THIRTEENTHS`,
  `AXLE_ALWAYS_CENTERS`, `OPHIUCHUS_WINDOW`, `SOL_WINDOW`,
  `MODRENIK_WINDOW_HALF_DAYS`, `MOON_PHASE_FRACTIONS`
- [Deep Time](deep_time.md) — `julian_day`/`delta_t_seconds`, the same
  TT-conversion primitives [Moon](moon.md)'s `illumination` uses
- [Moon](moon.md) — `MoonWindow`
- [Year Wheel](year_wheel.md) — `YearAnchors`

### Used by
- [Clock State](clock_state.md) — `build_day_context` computes
  `chinese_leap_month` and `thirteenth_candidates` ONCE per day and
  stores them as `DayContext.thirteenth_candidates` /
  `DayContext.chinese_leap_month_number`
- [Layers](../../render/layers/___layers.md) — `active_thirteenth(skin, day)`
  resolves `DayContext.thirteenth_candidates` against the active skin's
  own pointer/wheel/mount to the ONE member (if any) the Calendar
  pointer's dial center may show
- [Compositor](../../render/__about/compositor.md) — the Calendar pointer's own
  center hover/Spacebar speak the active 13th's own article

## Functions

- `thirteen_moon_year(year, window)` — the shared trigger: 13 Full Moons
  (UTC instant) in `year`.
- `ophiuchus_window(year)` / `sol_window(year)` / `modrenik_window(dec_solstice)`
  — each 13th's own `(first, last)` inclusive date window.
- `chinese_leap_month(anchors, window)` — the doubled lunar month
  (`ChineseLeapMonth(number, start, end)`) of the "sui" `anchors`
  brackets, or `None` for an ordinary 12-month sui.
- `thirteenth_candidates(on_date, moon_window, anchors, leap)` — every
  calendar-driven trigger+window active on `on_date` (0, 1, or
  occasionally 2), UNIONED with `constants.AXLE_ALWAYS_CENTERS`
  unconditionally — a `frozenset` of `constants.THIRTEENTHS`' keys,
  never empty.

## Classes

### ChineseLeapMonth
Frozen: `number` (the doubled lunar month, 1-12), `start`/`end` (its own
inclusive China-time civil-day span).

## Design Decisions

- **The ALWAYS-CENTERS are a union, not a fifth trigger.** They do not
  fit the "trigger + window" shape at all, so `thirteenth_candidates`
  computes the four calendar-driven facts exactly as it always did, then
  unions in `AXLE_ALWAYS_CENTERS` unconditionally as its last step — one
  line, no branch.
- **The Cat's trigger is deliberately NOT `thirteen_moon_year`.** A
  13-Full-Moon year and a 13-lunar-month Chinese sui are different
  astronomical facts that usually (not always) coincide, so The Cat's
  window is computed and checked independently.
- **No precedence lives here.** `thirteenth_candidates` is an unordered
  fact set — Ophiuchus's and Modrenik's windows genuinely overlap in the
  Dec 7-17 band of a blue-moon December, and both being true is normal,
  not a collision, because the four calendar-driven members live in four
  independent RENDER MODES (the Calendar pointer's wheel vs its mount)
  that never compete for the same seat. Resolving a date's candidates to
  the one member a given skin may show is `render.layers.
  active_thirteenth`'s job, never a date-only tiebreak here.
- **Computed once per day, not per minute.** `chinese_leap_month`
  involves ~13 solar-longitude evaluations — cheap, but its inputs only
  change once a day, so `build_day_context` computes it once and the
  minute-cadence paint pass only ever reads the stored field.
