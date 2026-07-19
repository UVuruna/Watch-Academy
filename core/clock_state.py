"""Two-tier render state.

DayContext is rebuilt when the cache key (local date, UTC offset) changes
— the offset component catches DST transitions, where the star
legitimately jumps 15 deg. TickState is rebuilt every minute and is
deliberately tiny.
"""

import math
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta

import astral
import astral.moon
import astral.sun

from config import constants
from core import angles, ascendant
from core.moon import (
    MoonWindow,
    chinese_zodiac,
    illumination,
    moon_rise_set,
    phase_fraction,
)
from core.sun import DaylightRegime, SunDay, compute_sun_day, day_length_hm
from core.year_wheel import YearAnchors, year_marker_angle, zodiac_sign

# Cycle fraction of a principal instant -> event name (for the glow).
_MOON_EVENT_NAMES = {
    fraction: name for name, fraction in constants.MOON_PHASE_FRACTIONS.items()
}


@dataclass(frozen=True)
class EclipseEvent:
    """One catalog eclipse near `now` (ROADMAP 15h item 11): `kind`
    decides which marker the render affects ("solar" -> Earth,
    "lunar" -> Moon), `instant`/`type`/`magnitude` feed the hover text
    and the magnitude-scaled glow strength. Built ONLY from the
    OPTIONAL Deep Time pack (data/deep_time.py); absent it,
    DayContext.eclipses is always empty and no eclipse ever renders —
    the absence is a supported state (Rule #1), not a silent gap."""

    kind: str                       # "solar" | "lunar"
    instant: datetime               # UT, proxy-shifted like every other
                                    # DayContext instant in deep travel
    type: str                       # total/annular/hybrid/partial/penumbral
    magnitude: float | None
    # Greatest-eclipse ground point (solar only, from the catalog; None
    # for lunar and for solar rows the finder reported no surface point).
    lat: float | None = None
    lon: float | None = None
    # VISIBILITY (fix round E, owner verdict "može", 2026-07-19): whether
    # THIS observer can actually see the event at its instant — LUNAR:
    # the Moon above the horizon; SOLAR: the Sun above the horizon AND
    # within `constants.ECLIPSE_SOLAR_VISIBILITY_KM` of the greatest-
    # eclipse point. Stamped by `_active_eclipse` (has the observer's
    # coordinates in hand); a fresh catalog row defaults to True so
    # every pre-existing test/caller that never touches visibility is
    # unaffected (Rule #6 — no silent behavior change for old callers).
    visible: bool = True
    # The observer's great-circle distance to the greatest-eclipse point
    # (solar only, km) — None when unknown (lunar, or no catalog point);
    # the hover's "path {d} km away" reason reads this directly instead
    # of recomputing the geometry (Rule #5).
    distance_km: float | None = None


@dataclass(frozen=True)
class DayContext:
    """Everything that changes at most once per (local day, UTC offset)."""

    local_date: date
    utc_offset: timedelta
    weekday_index: int              # datetime.weekday(): Monday=0 .. Sunday=6
    sun: SunDay
    star_rotation: float            # degrees, also the solar-noon arrow
    year_anchors: YearAnchors
    moon_window: MoonWindow         # principal-phase instants — the MINUTE
                                    # tick reads the live cycle fraction from
                                    # it (owner bug 2026-07-14: a day-time New
                                    # Moon left the marker stale until
                                    # midnight when the fraction lived here)
    moonrise: datetime | None       # local instants on this date; None when
    moonset: datetime | None        # the moon skips the event that day
    southern_hemisphere: bool       # the moon appears rotated 180 deg there
    zone: str                       # "north" | "tropics" | "south" — event
                                    # naming and the wet/dry season split
    day_length: str                 # "15:35" — octa bottom-arm option
    zodiac_name: str                # tropical sign, cusps on the year wheel
    zodiac_symbol: str
    zodiac_start: date              # local first day of the sign
    zodiac_end: date                # local first day of the NEXT sign
    chinese_name: str               # "Fire Horse" — element + animal
    chinese_start: date             # Chinese New Year (China time)
    chinese_end: date               # day before the next one
    season_events: tuple[tuple[datetime, str], ...]   # anchor instants + names
    anchor_day_lengths: tuple[str, ...]  # "15:23" at each anchor's local date
                                         # (cardinal arm hover, owner spec)
    moon_events: tuple[tuple[datetime, str], ...]     # principal instants + names
    tzinfo: object                  # the active timezone (hover instant display)
    latitude: float = 0.0           # observer coordinates — the minute tick
    longitude: float = 0.0          # computes the ASCENDANT from them
    # Deep Time eclipse catalog (ROADMAP 15h item 11): up to 4 candidates
    # (nearest solar/lunar eclipse before and after the day-context build
    # instant) — always empty without the optional pack. build_tick_state
    # picks the one (if any) whose ±3h window covers "now".
    eclipses: tuple[EclipseEvent, ...] = ()
    # Deep Time (Session 16): every datetime above lives in the 400-year
    # PROXY frame, shifted by deep_cycles Gregorian cycles (0 in normal
    # operation). The REAL astronomical year of any of them is
    # core.deep_time.real_year(dt.year, deep_cycles) — display sites
    # convert before formatting a year, the illumination evaluates at
    # the real epoch. The controller stamps it after the build
    # (build_day_context itself is frame-agnostic).
    deep_cycles: int = 0

    @property
    def cache_key(self) -> tuple[date, timedelta]:
        return (self.local_date, self.utc_offset)


@dataclass(frozen=True)
class TickState:
    """Everything recomputed on the minute tick."""

    hour_angle: float
    minute_angle: float
    second_angle: float             # used only when the seconds hand is on
    year_angle: float               # moves ~1 deg/day; cheap to keep smooth
    moon_fraction: float            # LIVE cycle fraction (0 new .. 0.5 full)
    moon_illumination: float        # lit disc fraction right now
    is_daylight: bool               # sun above the horizon right now
    is_moon_up: bool                # moon above the horizon right now
    time_hm: str                    # "14:34" — the octa pointer's digital slot
    season_event: str | None       # "Summer Solstice" within ±12 h, else None
    moon_event: str | None         # "Full Moon" within ±6 h, else None
    ascendant_sign: str = ""        # the rising sign right now ("Virgo") —
                                    # the South slot's Ascendant mode
                                    # (owner request 2026-07-12)
    eclipse_event: EclipseEvent | None = None  # active catalog eclipse
                                    # within ITS ±3h window, else None —
                                    # always None without the Deep Time pack


def build_day_context(
    now_local: datetime,
    observer: astral.Observer,
    year_anchors: YearAnchors,
    moon_window: MoonWindow,
    eclipses: tuple[EclipseEvent, ...] = (),
) -> DayContext:
    sun_day = compute_sun_day(observer, now_local.date(), now_local.tzinfo)
    moonrise, moonset = moon_rise_set(observer, now_local.date(), now_local.tzinfo)
    if abs(observer.latitude) <= constants.TROPIC_LATITUDE_DEG:
        zone = "tropics"
    else:
        zone = "south" if observer.latitude < 0 else "north"
    event_names = constants.ZONE_SEASON_EVENT_NAMES[zone]
    sign_name, sign_symbol, sign_start, sign_end = zodiac_sign(now_local, year_anchors)
    chinese_name, chinese_start, chinese_end = chinese_zodiac(now_local, moon_window)
    return DayContext(
        local_date=now_local.date(),
        utc_offset=now_local.utcoffset(),
        weekday_index=now_local.date().weekday(),
        sun=sun_day,
        star_rotation=angles.star_rotation_deg(sun_day.noon),
        year_anchors=year_anchors,
        moon_window=moon_window,
        moonrise=moonrise,
        moonset=moonset,
        southern_hemisphere=observer.latitude < 0,
        zone=zone,
        day_length=day_length_hm(sun_day),
        zodiac_name=sign_name,
        zodiac_symbol=sign_symbol,
        zodiac_start=sign_start.astimezone(now_local.tzinfo).date(),
        zodiac_end=sign_end.astimezone(now_local.tzinfo).date(),
        chinese_name=chinese_name,
        chinese_start=chinese_start,
        chinese_end=chinese_end,
        season_events=tuple(
            (instant, event_names[round(angle) % 360])
            for instant, angle in zip(year_anchors.instants, year_anchors.angles)
        ),
        anchor_day_lengths=tuple(
            day_length_hm(
                compute_sun_day(
                    observer,
                    instant.astimezone(now_local.tzinfo).date(),
                    now_local.tzinfo,
                )
            )
            for instant in year_anchors.instants
        ),
        moon_events=tuple(
            (instant, _MOON_EVENT_NAMES[fraction % 1.0])
            for instant, fraction in moon_window.events
        ),
        tzinfo=now_local.tzinfo,
        latitude=observer.latitude,
        longitude=observer.longitude,
        eclipses=eclipses,
    )


def build_tick_state(now_local: datetime, day: DayContext) -> TickState:
    year_angle = year_marker_angle(now_local, day.year_anchors)
    if day.southern_hemisphere:
        # Owner spec (FINAL.txt #4): the seasons are opposite south of
        # the equator, so the date marker runs MIRRORED — 21 June (their
        # shortest day) sits at the bottom (Ω), 22 December at the top (M).
        year_angle = (year_angle + 180.0) % 360.0
    # LIVE per-minute (owner bug 2026-07-14): a New Moon at 11:43 must
    # wrap the marker and the cycle-day readout at 11:43 — not at the
    # next day-context rebuild.
    moon_fraction = phase_fraction(now_local, day.moon_window)
    return TickState(
        hour_angle=angles.time_to_dial_angle(now_local),
        minute_angle=angles.minute_hand_angle(now_local),
        second_angle=angles.second_hand_angle(now_local),
        year_angle=year_angle,
        moon_fraction=moon_fraction,
        # TRUE analytic illumination at the instant (Session 16, owner
        # slike 4-7) — evaluated at the REAL epoch in deep travel.
        moon_illumination=illumination(now_local, day.deep_cycles),
        is_daylight=_is_daylight(now_local, day.sun),
        is_moon_up=_is_moon_up(now_local, day),
        time_hm=now_local.strftime("%H:%M"),
        ascendant_sign=ascendant.ascendant_sign(
            now_local, day.latitude, day.longitude
        ),
        season_event=_active_event(
            now_local, day.season_events, constants.SEASON_GLOW_WINDOW_H
        ),
        moon_event=_active_event(
            now_local, day.moon_events, constants.MOON_GLOW_WINDOW_H
        ),
        eclipse_event=_active_eclipse(
            now_local, day, constants.ECLIPSE_GLOW_WINDOW_H
        ),
    )


def _active_eclipse(
    now: datetime, day: "DayContext", window_hours: float
) -> EclipseEvent | None:
    """The catalog eclipse (if any) whose instant lies within
    ±window_hours of now — always None when `eclipses` is empty (no
    Deep Time pack, ROADMAP 15h item 11 absence rule). The winning event
    is stamped with THIS observer's visibility (fix round E) before
    it rides into the tick — every other candidate is left alone
    (visibility is only ever read off the active one)."""
    limit = timedelta(hours=window_hours)
    for event in day.eclipses:
        if abs(now - event.instant) <= limit:
            return _with_visibility(event, day.latitude, day.longitude)
    return None


def _with_visibility(
    event: EclipseEvent, latitude: float, longitude: float
) -> EclipseEvent:
    """Observer-relative visibility at the eclipse's own instant (fix
    round E, owner verdict "može", 2026-07-19): LUNAR visible <=> the
    Moon stands above the horizon; SOLAR visible <=> the Sun stands
    above the horizon AND the observer's great-circle distance to the
    catalog's greatest-eclipse point is within
    `constants.ECLIPSE_SOLAR_VISIBILITY_KM`. Evaluated at the INSTANT
    (astral's own elevation formulas), never the day's rise/set edges —
    the ±3h glow window is short enough that the instant is what
    matters. Pure function of its inputs (no wall clock), matching the
    rest of this tick-time state."""
    observer = astral.Observer(latitude=latitude, longitude=longitude)
    if event.kind == "lunar":
        moon_up = astral.moon.elevation(observer, event.instant) > 0.0
        return replace(event, visible=moon_up)
    sun_up = (
        astral.sun.elevation(observer, event.instant, with_refraction=False)
        > constants.HORIZON_ELEVATION_DEG
    )
    if event.lat is None or event.lon is None:
        # No catalog ground point to measure against — visibility rests
        # on daylight alone (better than a crash; documented absence).
        return replace(event, visible=sun_up)
    distance = _great_circle_km(latitude, longitude, event.lat, event.lon)
    visible = sun_up and distance <= constants.ECLIPSE_SOLAR_VISIBILITY_KM
    return replace(event, visible=visible, distance_km=distance)


def _great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine great-circle distance in km — the eclipse visibility's
    only geometry need (mean Earth radius, `constants.EARTH_RADIUS_KM`)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * constants.EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _active_event(
    now: datetime, events: tuple[tuple[datetime, str], ...], window_hours: float
) -> str | None:
    """Name of the event whose instant lies within ±window_hours of now."""
    limit = timedelta(hours=window_hours)
    for instant, name in events:
        if abs(now - instant) <= limit:
            return name
    return None


def _is_moon_up(now: datetime, day: DayContext) -> bool:
    """Whether the moon stands above the horizon (owner spec
    2026-07-12: the marker dims below it). Skip days (one event
    missing) read from the present event; both missing (polar edge) is
    treated as up — dimming a moon someone can see would be the worse
    lie."""
    rise, sets = day.moonrise, day.moonset
    if rise is None and sets is None:
        return True
    if rise is not None and sets is not None:
        if rise <= sets:
            return rise <= now <= sets
        return now >= rise or now <= sets      # up across midnight
    if rise is None:                           # was up, only sets today
        return now <= sets
    return now >= rise                         # only rises today


def _is_daylight(now: datetime, sun: SunDay) -> bool:
    if sun.regime is DaylightRegime.POLAR_DAY:
        return True
    if sun.regime in (DaylightRegime.POLAR_NIGHT, DaylightRegime.TWILIGHT_ONLY):
        return False
    if sun.sunrise is not None and sun.sunset is not None:
        if sun.sunset < sun.sunrise:
            # Inverted midnight-sun transition day (e.g. Murmansk in May):
            # this day's sunset falls just after local midnight, BEFORE its
            # sunrise — daylight is the complement of the dark gap.
            return now <= sun.sunset or now >= sun.sunrise
        return sun.sunrise <= now <= sun.sunset
    # Transitional one-sided days at high latitudes: only one boundary
    # exists on this date.
    if sun.sunrise is not None:
        return now >= sun.sunrise
    if sun.sunset is not None:
        return now <= sun.sunset
    return False
