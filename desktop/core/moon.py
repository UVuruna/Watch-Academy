"""Moon phase from bundled principal-phase instants.

Linear interpolation of the cycle fraction between bracketing principal
phases (New=0.0, First Quarter=0.25, Full=0.5, Third Quarter=0.75) is
exact at the anchors and matches astral to ~0.0001 of a cycle in
between — while astral.moon.phase() is day-granular on a 28-scale and
off by up to ~0.3 day near the instants, so it is not used here.

The ILLUMINATION is analytic since Session 16 (owner slike 4-7,
2026-07-17): the cycle-fraction cosine was exact at the principals but
up to ~3 p.p. off mid-phase (ours 10.3% vs the true ~11.5%); the
compact Meeus 48.4 elongation series reads the true lit fraction at any
instant. Measured against the DE441 events database (2026-07-17): max
0.35 p.p. deviation at principal instants across 1560-2640, max
2.4 p.p. at the −13000/+17000 pack edges (ΔT model dominated) — better
than the interpolation everywhere, so it serves the WHOLE span.
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from config import constants
from core import angles
from core.deep_time import delta_t_seconds, julian_day, real_year


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


def illumination(when: datetime, cycles: int = 0) -> float:
    """TRUE lit fraction of the moon disc (0.0 new .. 1.0 full) at a
    tz-aware instant — the compact analytic elongation series (Meeus
    48.4): sun mean anomaly, moon mean anomaly and mean elongation with
    the principal periodic terms; k = (1 − cos(D + corrections)) / 2,
    which is the phase-angle form i = 180° − D − corrections,
    k = (1 + cos i)/2. `cycles` is the deep-time proxy shift — the
    series evaluates at the REAL epoch (TT via ΔT), so a deep travel's
    illumination matches its own pack-driven markers."""
    utc = when.astimezone(timezone.utc)
    year = real_year(utc.year, cycles)
    jd_tt = julian_day(
        year, utc.month, utc.day,
        (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
    ) + delta_t_seconds(year) / 86400.0
    t = (jd_tt - 2451545.0) / 36525.0
    # Mean elongation of the Moon, sun mean anomaly, moon mean anomaly
    # (Meeus ch. 47 polynomials — degrees).
    d = (297.8501921 + 445267.1114034 * t - 0.0018819 * t * t
         + t**3 / 545868.0 - t**4 / 113065000.0)
    m = (357.5291092 + 35999.0502909 * t - 0.0001536 * t * t
         + t**3 / 24490000.0)
    mp = (134.9633964 + 477198.8675055 * t + 0.0087414 * t * t
          + t**3 / 69699.0 - t**4 / 14712000.0)
    d, m, mp = (math.radians(x % 360.0) for x in (d, m, mp))
    corrected = d + math.radians(
        6.289 * math.sin(mp)
        - 2.100 * math.sin(m)
        + 1.274 * math.sin(2 * d - mp)
        + 0.658 * math.sin(2 * d)
        + 0.214 * math.sin(2 * mp)
        - 0.110 * math.sin(d)
    )
    return (1.0 - math.cos(corrected)) / 2.0


def nominal_illumination(fraction: float) -> float:
    """The NOMINAL lit fraction of a cycle position (0.0 new .. 1.0
    full) — the ring's own cosine mapping. Used only where a dial ANGLE
    is read hypothetically (the ring tick hover: "what would stand
    here"), never for the live moon — that is `illumination`."""
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
    return chinese_name_of_year(year), start, end


def chinese_name_of_year(year: int) -> str:
    """"Fire Horse" of a calendar year — the sexagenary arithmetic
    alone. Shared by chinese_zodiac and the deep-time correction (a
    400-year proxy shift moves the sexagenary cycle by 40, so the
    controller renames the year from the REAL astronomical year)."""
    animal = constants.CHINESE_ANIMALS[(year - 4) % 12]
    element = constants.CHINESE_ELEMENTS[((year - 4) % 10) // 2]
    return f"{element} {animal}"


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


@dataclass(frozen=True)
class MoonArc:
    """One above-horizon span on the dial's tick circle, in the ONE
    shared dial-angle mapping (`core.angles.time_to_dial_angle`):
    degrees clockwise from the top, UNWRAPPED so `end_deg >= start_deg`
    (the render side takes `% 360` itself when it draws). `culmination_deg`
    is the arc's own midpoint — the render layer's silver-thread diamond
    and the glow's brightness peak both read it.

    THE MIDPOINT CULMINATION RULE (owner spec 2026-08-09, "midpoint of
    the arc is an acceptable culmination approximation if core has no
    culmination time"): `core.moon` has no lunar-transit computation —
    only rise/set — so this is the approximation actually used; a real
    transit time would replace this field's source, never its shape.
    """

    start_deg: float
    end_deg: float
    culmination_deg: float
    full_circle: bool = False


def moon_horizon_arcs(
    moonrise: datetime | None, moonset: datetime | None
) -> tuple[MoonArc, ...]:
    """The Moon's above-horizon arc(s) for the Moon Horizon Band (owner
    verdict 2026-08-09), built from the SAME `moonrise`/`moonset` pair
    `core.clock_state._is_moon_up` already reads, and the SAME dial
    mapping the hour hand uses (`core.angles.time_to_dial_angle`) — no
    angle formula is re-derived here.

    THE NONE-DAY RULE (mirrors `_is_moon_up`'s own policy exactly, Rule
    #5 — one law, not a second fork of it): a day is missing a rise or
    a set roughly once a synodic month, and BOTH missing only happens
    at polar latitudes.
      * both None -> the moon skips both events because it never sets
        (or never rises) today; `_is_moon_up` treats this as VISIBLE
        ("dimming a moon someone can see would be the worse lie") and
        this mirrors that: a single FULL-CIRCLE arc, `full_circle=True`.
      * rise is None (only sets today) -> already up at local midnight,
        arc runs from the dial's midnight point (00:00) to the set.
      * set is None (only rises today) -> stays up past local midnight,
        arc runs from the rise to the dial's midnight point (24:00,
        the SAME dial point as 00:00, reached by sweeping forward).
      * both present, rise before set -> the plain single arc.
      * both present, rise AFTER set (the moon was already up at
        midnight, sets, then rises again before the next midnight) ->
        TWO arcs: midnight-to-set and rise-to-midnight, each with its
        own midpoint culmination (there is no single "the" midpoint of
        a span split by the dial's own seam).
    """
    midnight = time(0, 0, 0)
    start_of_day = angles.time_to_dial_angle(midnight)
    end_of_day = start_of_day + 360.0

    if moonrise is None and moonset is None:
        return (
            MoonArc(
                start_of_day, end_of_day,
                (start_of_day + 180.0) % 360.0, full_circle=True,
            ),
        )
    if moonrise is None:
        end = _unwrap(start_of_day, angles.time_to_dial_angle(moonset))
        return (_arc(start_of_day, end),)
    if moonset is None:
        # Anchor the rise INTO the day's own domain
        # (`start_of_day` .. `end_of_day`) before sweeping to midnight:
        # `time_to_dial_angle` returns 0..360, while the domain starts at
        # the midnight point, so an unanchored rise makes the sweep run a
        # whole extra lap and the band reads as a 24h moon.
        start = _unwrap(start_of_day, angles.time_to_dial_angle(moonrise))
        return (_arc(start, end_of_day),)

    rise_deg = _unwrap(start_of_day, angles.time_to_dial_angle(moonrise))
    set_deg = angles.time_to_dial_angle(moonset)
    if moonrise <= moonset:
        end = _unwrap(rise_deg, set_deg)
        return (_arc(rise_deg, end),)

    # Up at midnight, sets, then rises again before the next midnight.
    first_end = _unwrap(start_of_day, set_deg)
    return (_arc(start_of_day, first_end), _arc(rise_deg, end_of_day))


def shift_arcs(
    arcs: tuple[MoonArc, ...], offset_deg: float
) -> tuple[MoonArc, ...]:
    """`arcs` carried by the WORLD OFFSET (`core.world.world_offset_deg`).

    THE HOUR FRAME RULE (owner order 2026-08-13, correcting the doctrine
    `render.layers.moon_band` used to carry): the outer circle shows
    HOURS and the inner circle shows minutes, seconds and the calendar
    wheels — so ANYTHING that draws a span of hours belongs to the outer
    circle's frame and must turn with it, wherever on the dial it is
    painted. The horizon band is drawn on the inner circle's radius for
    a purely GEOMETRIC reason (it must slice no inner-ring element), and
    an earlier round read that placement as membership: it pinned the
    band to the fixed tick art and wrote "NEVER rotates with
    `ctx.world_offset` in any world mode" into the module docstring. The
    owner saw the result on his own dial — the same day showing the Moon
    up over the afternoon hours while the rotated face had those seats
    reading 00:00-09:53 — and named the law the code was missing.

    The three exempt things are exempt for the OPPOSITE reason, and the
    line between them is not placement but UNITS: the inner minute band,
    the year wheel and the moon cycle are positions in the calendar, not
    in the day (`render.layers.year_marker.earth_marker_angle`).

    The span is preserved exactly — only the seat moves — so a
    `full_circle` arc stays a full circle and a two-arc midnight split
    stays split at the same two places."""
    return tuple(
        MoonArc(
            arc.start_deg + offset_deg,
            arc.end_deg + offset_deg,
            (arc.culmination_deg + offset_deg) % 360.0,
            full_circle=arc.full_circle,
        )
        for arc in arcs
    )


def _unwrap(start_deg: float, raw_end_deg: float) -> float:
    """`raw_end_deg` nudged forward by whole laps until it is >=
    `start_deg` — the arc always sweeps CLOCKWISE (forward in time)."""
    end = raw_end_deg
    while end < start_deg:
        end += 360.0
    return end


def _arc(start_deg: float, end_deg: float) -> "MoonArc":
    return MoonArc(start_deg, end_deg, (start_deg + end_deg) / 2.0 % 360.0)
