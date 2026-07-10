"""Moon phase from bundled principal-phase instants.

Linear interpolation of the cycle fraction between bracketing principal
phases (New=0.0, First Quarter=0.25, Full=0.5, Third Quarter=0.75) is
exact at the anchors and matches astral to ~0.0001 of a cycle in
between — while astral.moon.phase() is day-granular on a 28-scale and
off by up to ~0.3 day near the instants, so it is not used here.
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from config import constants


@dataclass(frozen=True)
class MoonWindow:
    """Sorted principal-phase events (tz-aware UTC instant, cycle fraction)
    spanning comfortably around the period of interest."""

    events: tuple[tuple[datetime, float], ...]


def phase_fraction(now: datetime, window: MoonWindow) -> float:
    """Cycle fraction at `now`: 0.0 new, 0.25 first quarter, 0.5 full,
    0.75 third quarter. Waxing below 0.5, waning above.

    Raises ValueError when `now` is outside the window span.
    """
    events = window.events
    if not events[0][0] <= now <= events[-1][0]:
        raise ValueError(
            f"{now.isoformat()} is outside the moon window "
            f"({events[0][0].isoformat()} .. {events[-1][0].isoformat()})"
        )
    for (t0, f0), (t1, _) in zip(events, events[1:]):
        if t0 <= now <= t1:
            elapsed = (now - t0) / (t1 - t0)
            return (f0 + elapsed * constants.MOON_CYCLE_QUARTER) % 1.0
    raise ValueError(f"no bracketing phase events around {now.isoformat()}")


def illumination(fraction: float) -> float:
    """Lit fraction of the moon disc (0.0 new .. 1.0 full) from the cycle
    fraction."""
    return (1.0 - math.cos(2.0 * math.pi * fraction)) / 2.0


def moon_rise_set(observer, day: date, tzinfo):
    """Local (moonrise, moonset) on `day` via astral, either None when
    the event does not occur on that calendar date (documented: the
    moon skips a rise or a set roughly once a synodic month, and may do
    so for days at polar latitudes)."""
    import astral.moon

    try:
        rise = astral.moon.moonrise(observer, day, tzinfo)
    except ValueError:
        rise = None
    try:
        setting = astral.moon.moonset(observer, day, tzinfo)
    except ValueError:
        setting = None
    return rise, setting


def chinese_zodiac(now_local: datetime, window: MoonWindow) -> tuple[str, date, date]:
    """("Fire Horse", start, end) of the Chinese year at `now` — the
    year begins at the new moon falling in the Jan 21 – Feb 20 window
    (China time); animal and element follow the sexagenary cycle. The
    moon window spans the neighbor years, so both cusps are present.

    The cusp comparison happens entirely in CHINA's calendar frame
    (review finding): comparing the observer's own local date against
    China's New Year date misclassified the year by up to a day for
    every non-UTC+8 observer around the cusp."""
    china_now = now_local.astimezone(timezone.utc) + timedelta(
        hours=constants.CHINA_UTC_OFFSET_HOURS
    )
    year = china_now.date().year
    start = _chinese_new_year(year, window)
    if china_now.date() < start:
        year -= 1
        start = _chinese_new_year(year, window)
    end = _chinese_new_year(year + 1, window) - timedelta(days=1)
    animal = constants.CHINESE_ANIMALS[(year - 4) % 12]
    element = constants.CHINESE_ELEMENTS[((year - 4) % 10) // 2]
    return f"{element} {animal}", start, end


def _chinese_new_year(year: int, window: MoonWindow) -> date:
    """The Chinese New Year date of `year` (China time)."""
    (lo_m, lo_d), (hi_m, hi_d) = constants.CHINESE_NEW_YEAR_WINDOW
    low, high = date(year, lo_m, lo_d), date(year, hi_m, hi_d)
    for instant, fraction in window.events:
        if fraction == 0.0:
            china = (
                instant + timedelta(hours=constants.CHINA_UTC_OFFSET_HOURS)
            ).date()
            if low <= china <= high:
                return china
    raise ValueError(f"no Chinese New Year of {year} inside the moon window")


def phase_name(fraction: float) -> str:
    """English phase name for a cycle fraction. A PRINCIPAL name (New,
    First Quarter, Full, Third Quarter) applies only within ±half a day
    of its instant — the common convention: the day after the Third
    Quarter the moon is already a Waning Crescent."""
    fraction %= 1.0
    principals = (
        (0.0, "New Moon"),
        (0.25, "First Quarter"),
        (0.5, "Full Moon"),
        (0.75, "Third Quarter"),
        (1.0, "New Moon"),
    )
    for anchor, name in principals:
        if abs(fraction - anchor) <= constants.MOON_PRINCIPAL_WINDOW:
            return name
    if fraction < 0.25:
        return "Waxing Crescent"
    if fraction < 0.5:
        return "Waxing Gibbous"
    if fraction < 0.75:
        return "Waning Gibbous"
    return "Waning Crescent"
