"""THE BLUE MOON LAW (owner-sealed 2026-07-22, CORRECTED 2026-07-22):
every 12-set on this dial gains a hidden 13th member. It exists ONLY
under its own trigger, during its own short date window; outside
trigger+window it does not exist anywhere, dial or Encyclopedia.

Four members, three triggers:

- **Ophiuchus** (the zodiac's 13th) and **Sol**/**Modrenik** (the Sun's
  and the Moon's 13th months, opposite ends of the year wheel) share ONE
  trigger — `thirteen_moon_year`: the calendar year holds 13 Full Moons
  instead of the usual 12 (~37% of years, because the 29.53-day synodic
  month does not evenly divide the 365.24-day year: 365.24 / 29.53 =
  12.37 cycles/year, so a year holds 12 or 13 Full Moons, never fewer or
  more). Each then keeps its OWN short window (`ophiuchus_window`,
  `sol_window`, `modrenik_window`).
- **The Cat** (the Chinese zodiac's 13th) is NOT solar-triggered at all
  — it rides the REAL lunisolar leap-month mechanic (`chinese_leap_month`):
  the lunar month that carries no zhongqi (major solar term) between two
  December solstices.

`thirteenth_candidates` names every member (0, 1 or occasionally 2) whose
OWN trigger+window holds on a given date — an unordered FACT SET, no
precedence between members: the owner's correction retired R12's global
"any pointer, any theme" law AND its cross-13th precedence tiebreak
(Cat > Ophiuchus > Sol/Modrenik) together, since neither survives the
real rule — **the four members live in FOUR INDEPENDENT MODES on the
Calendar pointer alone and never meet on the dial** (Ophiuchus/Sol on its
zodiac/almanac WHEEL, Modrenik/The Cat on its "months"/"chinese" MOUNT).
More than one candidate being true here is normal, not a collision — e.g.
Ophiuchus's and Modrenik's windows genuinely overlap in the Dec 7-17 band
of a blue-moon December — because a "collision" only exists once a
RENDER MODE tries to show two members at once, which the mode gate
itself makes impossible. Resolving a date's candidates to the ONE member
a given skin may show is `render.layers.active_thirteenth`'s job, read
from the skin's own pointer/wheel/mount, never astronomical "realness".

Pure module (no Qt, no wall clock) — purity-gated by tests/test_purity;
every function takes already-built data (MoonWindow, YearAnchors), never
touches a repository or the filesystem, matching core.continents/core.moon.
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from config import constants
from core.deep_time import delta_t_seconds, julian_day
from core.moon import MoonWindow
from core.year_wheel import YearAnchors

_FULL_MOON_FRACTION = constants.MOON_PHASE_FRACTIONS["Full Moon"]


def thirteen_moon_year(year: int, window: MoonWindow) -> bool:
    """True when calendar year `year` holds 13 Full Moons (UTC instant,
    matching how published full-moon counts are reckoned) rather than
    the usual 12 — see the module docstring for why it is always one or
    the other. `window` must already bracket `year` (any MoonWindow
    covering it works — MoonPhaseRepository.moon_window(year) covers
    year-1..year+1, so `window` built for `year` itself, or for
    `year - 1` / `year + 1`, all answer correctly)."""
    return sum(
        1 for instant, fraction in window.events
        if fraction == _FULL_MOON_FRACTION and instant.year == year
    ) == 13


def ophiuchus_window(year: int) -> tuple[date, date]:
    """(first, last) inclusive date of Ophiuchus's window in `year` —
    the Sun's real transit through the constellation."""
    (lo_m, lo_d), (hi_m, hi_d) = constants.OPHIUCHUS_WINDOW
    return date(year, lo_m, lo_d), date(year, hi_m, hi_d)


def sol_window(year: int) -> tuple[date, date]:
    """(first, last) inclusive date of Sol's window in `year` — carries
    the June solstice."""
    (lo_m, lo_d), (hi_m, hi_d) = constants.SOL_WINDOW
    return date(year, lo_m, lo_d), date(year, hi_m, hi_d)


def modrenik_window(december_solstice: datetime) -> tuple[date, date]:
    """(first, last) inclusive date of Modrenik's window, computed FROM
    the real December solstice instant — `MODRENIK_WINDOW_HALF_DAYS`
    either side, honest across years (unlike a fixed MM-DD pair, since
    the solstice itself drifts a day)."""
    half = timedelta(days=constants.MODRENIK_WINDOW_HALF_DAYS)
    center = december_solstice.date()
    return center - half, center + half


# --- THE CAT: the real lunisolar leap month -----------------------------------


@dataclass(frozen=True)
class ChineseLeapMonth:
    """The doubled lunar month of one 'sui' (December-solstice-to-
    December-solstice span): `number` is the LUNAR month it repeats
    (1-12; "leap 6th month" doubles month 6), `start`/`end` its own
    inclusive CHINA-TIME civil-day span."""

    number: int
    start: date
    end: date


def _solar_longitude(when: datetime) -> float:
    """Apparent geocentric ecliptic longitude of the Sun, degrees
    (Meeus ch. 25 low-precision series — accurate to ~0.01 deg, i.e. a
    few seconds of time). Matches core.moon.illumination's own Meeus-
    series precedent: far more precision than a zhongqi/new-moon
    boundary comparison needs, since lunar months (~29.5 d) and zhongqi
    (~30.4 d average) are never within minutes of each other except by
    the same astronomically negligible coincidence that would also
    threaten a full-precision ephemeris."""
    utc = when.astimezone(timezone.utc)
    jd_tt = julian_day(
        utc.year, utc.month, utc.day,
        (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
    ) + delta_t_seconds(utc.year) / 86400.0
    t = (jd_tt - 2451545.0) / 36525.0
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360.0)
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
        + (0.019993 - 0.000101 * t) * math.sin(2 * m)
        + 0.000289 * math.sin(3 * m)
    )
    true_longitude = l0 + c
    omega = math.radians(125.04 - 1934.136 * t)
    apparent = true_longitude - 0.00569 - 0.00478 * math.sin(omega)
    return apparent % 360.0


def _has_zhongqi(start: datetime, end: datetime) -> bool:
    """True when a major solar term (zhongqi — the Sun's apparent
    longitude crossing a multiple of 30 deg) falls in [start, end). A
    lunar month always spans well under 30 deg of solar motion, so at
    most one crossing is possible — comparing the 30-deg ZONE
    (floor(longitude / 30)) before and after detects it without
    needing the crossing's own instant."""
    lo = _solar_longitude(start)
    hi = _solar_longitude(end)
    if hi < lo:
        hi += 360.0             # unwrap across the 360 -> 0 wrap
    return math.floor(hi / 30.0) > math.floor(lo / 30.0)


def _china_date(instant: datetime) -> date:
    """The CHINA STANDARD TIME (UTC+8) civil date of `instant` — the
    same convention core.moon._chinese_new_year already uses."""
    return (instant.astimezone(timezone.utc) + timedelta(hours=8)).date()


def _china_midnight_utc(day: date) -> datetime:
    """UTC instant of `day`'s own 00:00 China Standard Time."""
    return (
        datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        - timedelta(hours=8)
    )


def chinese_leap_month(
    anchors: YearAnchors, window: MoonWindow
) -> ChineseLeapMonth | None:
    """The leap month of the 'sui' `anchors` brackets (its OWN December
    solstice `instants[4]`, back to the PRIOR one `instants[0]`), or
    None for an ordinary 12-month sui.

    THE RULE (unchanged since antiquity): the lunar month containing
    the December solstice is ALWAYS "the eleventh month". Walking new
    moons forward from it, if 13 (not 12) of them separate this
    solstice's eleventh month from the NEXT one, exactly one of the 12
    months in between carries NO zhongqi (major solar term) — that
    month is the leap month, and it keeps its PRECEDING month's number
    (e.g. a zhongqi-less month right after the 6th is "leap 6th
    month"). Golden-tested against two independently known leap months
    (tests/test_blue_moon.py): 2023 leap 2nd (Mar 22 - Apr 19), 2025
    leap 6th (Jul 25 - Aug 22) — both reproduced exactly."""
    sui_start, sui_end = anchors.instants[0], anchors.instants[4]
    new_moons = sorted(
        instant for instant, fraction in window.events if fraction == 0.0
    )
    i0 = max(i for i, nm in enumerate(new_moons) if nm <= sui_start)
    i1 = max(i for i, nm in enumerate(new_moons) if nm <= sui_end)
    span = i1 - i0
    if span == 12:
        return None
    if span != 13:
        raise ValueError(
            f"{span} lunar months between one sui's December solstices "
            "— expected 12 or 13; the bundled moon window may not cover "
            "this span"
        )
    # `number` holds the TRUE month of segment (j-1) when segment j is
    # examined — exactly the value a leap segment must REPORT (a leap
    # month repeats its PREDECESSOR's number, never its own successor
    # position); the update below advances it to segment j's own
    # number only AFTER j has been confirmed non-leap.
    number = 11
    for j in range(1, span):
        start_day = _china_date(new_moons[i0 + j])
        end_day = _china_date(new_moons[i0 + j + 1])
        if not _has_zhongqi(
            _china_midnight_utc(start_day), _china_midnight_utc(end_day)
        ):
            return ChineseLeapMonth(number, start_day, end_day - timedelta(days=1))
        number = number % 12 + 1
    raise ValueError("13 lunar months found but no zhongqi-less month located")


# --- Which 13ths are candidates today (fact only, no mode/precedence) ---------


def thirteenth_candidates(
    on_date: date,
    moon_window: MoonWindow,
    anchors: YearAnchors,
    leap: ChineseLeapMonth | None,
) -> frozenset[str]:
    """Every 13th (0, 1 or occasionally 2 of `config.constants.
    THIRTEENTHS`' keys) whose OWN trigger+window holds on `on_date` — an
    unordered FACT SET, no precedence between members (see the module
    docstring: the four members live in four independent RENDER MODES
    that never meet, so more than one true candidate here is normal, not
    a collision to resolve). `leap` is the caller's own `chinese_leap_
    month(anchors, moon_window)` result (computed once per DayContext
    rebuild, DAILY cadence — never recomputed here, matching
    core.continents' "thin wrapper" law)."""
    found: set[str] = set()
    if leap is not None and leap.start <= on_date <= leap.end:
        found.add("chinese")
    year = on_date.year
    if thirteen_moon_year(year, moon_window):
        lo, hi = ophiuchus_window(year)
        if lo <= on_date <= hi:
            found.add("ophiuchus")
        lo, hi = sol_window(year)
        if lo <= on_date <= hi:
            found.add("sol")
    # Modrenik can cross the New Year, so both December solstices this
    # year's own YearAnchors already carries are checked — `instants[4]`
    # (this year's) and `instants[0]` (last year's, relevant to early-
    # January dates) — never a second repository call (Rule #5).
    for solstice, solstice_year in (
        (anchors.instants[4], year), (anchors.instants[0], year - 1),
    ):
        lo, hi = modrenik_window(solstice)
        if lo <= on_date <= hi and thirteen_moon_year(solstice_year, moon_window):
            found.add("modrenik")
    return frozenset(found)
