"""Two-tier render state.

DayContext is rebuilt when the cache key (local date, UTC offset) changes
— the offset component catches DST transitions, where the hexagram
legitimately jumps 15 deg. TickState is rebuilt every minute and is
deliberately tiny.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import astral

from core import angles
from core.moon import MoonWindow, illumination, phase_fraction
from core.sun import DaylightRegime, SunDay, compute_sun_day
from core.year_wheel import YearAnchors, year_marker_angle


@dataclass(frozen=True)
class DayContext:
    """Everything that changes at most once per (local day, UTC offset)."""

    local_date: date
    utc_offset: timedelta
    weekday_index: int              # datetime.weekday(): Monday=0 .. Sunday=6
    sun: SunDay
    hexagram_rotation: float        # degrees, also the solar-noon arrow
    year_anchors: YearAnchors
    moon_fraction: float            # cycle fraction at day-context build time
    moon_illumination: float
    southern_hemisphere: bool       # the moon appears rotated 180 deg there

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
    is_daylight: bool               # sun above the horizon right now


def build_day_context(
    now_local: datetime,
    observer: astral.Observer,
    year_anchors: YearAnchors,
    moon_window: MoonWindow,
) -> DayContext:
    sun_day = compute_sun_day(observer, now_local.date(), now_local.tzinfo)
    fraction = phase_fraction(now_local, moon_window)
    return DayContext(
        local_date=now_local.date(),
        utc_offset=now_local.utcoffset(),
        weekday_index=now_local.date().weekday(),
        sun=sun_day,
        hexagram_rotation=angles.hexagram_rotation_deg(sun_day.noon),
        year_anchors=year_anchors,
        moon_fraction=fraction,
        moon_illumination=illumination(fraction),
        southern_hemisphere=observer.latitude < 0,
    )


def build_tick_state(now_local: datetime, day: DayContext) -> TickState:
    return TickState(
        hour_angle=angles.time_to_dial_angle(now_local),
        minute_angle=angles.minute_hand_angle(now_local),
        second_angle=angles.second_hand_angle(now_local),
        year_angle=year_marker_angle(now_local, day.year_anchors),
        is_daylight=_is_daylight(now_local, day.sun),
    )


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
