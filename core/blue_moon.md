# Blue Moon — the Thirteenth Member

**Script:** [Blue Moon (script)](blue_moon.py)

## Purpose

Owner-sealed 2026-07-22, CORRECTED 2026-07-22: every 12-set on the dial
gains a hidden 13th member — **Ophiuchus** (the zodiac's 13th sign),
**Sol** (the Sun's 13th month, International Fixed Calendar),
**Modrenik** (the Moon's 13th month, an invented Slavic sibling), and
**The Cat** (the Chinese zodiac's 13th animal). Each exists ONLY under
its own trigger and ONLY inside its own short date window; outside
trigger+window it does not exist anywhere, dial or Encyclopedia.

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

`thirteenth_candidates` names every member (0, 1 or occasionally 2)
whose OWN trigger+window holds on a given date — an unordered FACT SET,
no precedence between members. Ophiuchus's and Modrenik's windows do
genuinely overlap in the Dec 7-17 band of a blue-moon December, so both
can be candidates at once — this module no longer picks a winner there.
**THE OWNER'S CORRECTION (retiring R12's global law):** the four members
actually live in FOUR INDEPENDENT RENDER MODES on the Calendar pointer
alone and never meet on the dial — Ophiuchus/Sol on its zodiac/almanac
WHEEL (`SkinDefinition.palette_style`), Modrenik/The Cat on its
"months"/"chinese" MOUNT (`SkinDefinition.calendar_mount`) — so
resolving a date's candidates to the ONE member a given skin may show is
[Layers](../render/layers.md)' `active_thirteenth(skin, day)`, never a
date-only tiebreak here.

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
  `chinese_leap_month` and `thirteenth_candidates` ONCE per day (DAILY
  cadence, matching every other `DayContext` field) and stores them as
  `DayContext.thirteenth_candidates` / `DayContext.chinese_leap_month_number`
  — never recomputed on the MINUTE-cadence paint pass.
- [Layers (folder)](../render/___render.md) — `active_thirteenth(skin,
  day)` resolves `DayContext.thirteenth_candidates` against the skin's
  own pointer/wheel/mount to the ONE member (if any) the Calendar
  pointer's dial center may show — `CenterBodyLayer` draws it there,
  gated to `skin.pointer == "calendar"` alone (every other pointer's
  ordinary center laws reign untouched); `_draw_calendar_mount`'s
  "chinese" mount dims the doubled month's own animal from
  `DayContext.chinese_leap_month_number`.
- [Compositor (script)](../render/compositor.md) — the Calendar
  pointer's own center hover/Spacebar speak the active 13th's own
  article.

## Functions

- `thirteen_moon_year(year, window)` — the shared trigger: 13 Full Moons
  (UTC) in `year`.
- `ophiuchus_window(year)` / `sol_window(year)` / `modrenik_window(dec_solstice)`
  — each 13th's own (first, last) inclusive window.
- `chinese_leap_month(anchors, window)` — the doubled lunar month
  (number + its own China-time span) of the sui `anchors` brackets, or
  `None`.
- `thirteenth_candidates(on_date, moon_window, anchors, leap)` — every
  trigger+window active on `on_date`, a `frozenset` of
  `config.constants.THIRTEENTHS`' keys (0, 1 or occasionally 2 members).

## Design Decisions

- **The Cat's trigger is deliberately NOT `thirteen_moon_year`.** A
  13-Full-Moon year and a 13-lunar-month Chinese sui are different
  astronomical facts that usually (not always) coincide — the task is
  explicit that The Cat rides the real lunisolar mechanic, not the
  shared solar trigger, so its window is computed and checked
  independently in `thirteenth_candidates`.
- **No precedence lives here (owner correction, retiring R12).** The
  only genuine window overlap is Ophiuchus vs Modrenik (both share
  `thirteen_moon_year` and their windows touch in December) — R12 picked
  a winner by "astronomical realness"; the owner's correction found the
  real rule instead: the four members live in four INDEPENDENT RENDER
  MODES (the Calendar pointer's wheel vs its mount) that never compete
  for the same seat, so `thirteenth_candidates` reports BOTH as true
  facts and leaves the mode-resolution entirely to
  `render.layers.active_thirteenth`, which reads the ACTIVE skin
  settings (a mount that owns a 13th outranks the wheel when both are
  active at once — see its own docstring).
- **Computed once per day, not per minute.** `chinese_leap_month`
  involves ~13 solar-longitude evaluations — cheap, but its inputs
  (`YearAnchors`, `MoonWindow`) only change once a day, so
  `build_day_context` computes it once and `CenterBodyLayer` (MINUTE
  cadence) only ever reads the stored field — the same "DayContext
  holds what changes daily" law every other field on it follows.
