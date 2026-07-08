"""Sun events and daylight-regime classification.

The five events are computed INDIVIDUALLY: astral.sun.sun() is
all-or-nothing and raises ValueError at high latitudes even when four of
the five events exist — and its message is identical for polar day and
polar night, so exception text can never classify the regime. noon()
never raises (meridian transit is always defined), so the star
rotation is always computable, even in polar night.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Callable
from zoneinfo import ZoneInfo

import astral
import astral.sun

from config import constants


class DaylightRegime(Enum):
    NORMAL = "normal"                # sunrise/sunset and dawn/dusk all exist
    WHITE_NIGHTS = "white_nights"    # sunrise/sunset exist, sky never fully dark
    TWILIGHT_ONLY = "twilight_only"  # sun never rises, but twilight occurs
    POLAR_DAY = "polar_day"          # sun never sets
    POLAR_NIGHT = "polar_night"      # sun never comes near the horizon


def day_length_hm(sun: "SunDay") -> str:
    """Daylight duration of the day as "H:MM" (the octa bottom-arm
    option). Polar day reads 24:00, polar night/twilight-only 0:00;
    inverted midnight-sun days take the complement of the dark gap;
    one-sided transitional days measure against the local midnights."""
    if sun.regime is DaylightRegime.POLAR_DAY:
        return "24:00"
    if sun.regime in (DaylightRegime.POLAR_NIGHT, DaylightRegime.TWILIGHT_ONLY):
        return "0:00"
    full_day = timedelta(days=1)
    if sun.sunrise is not None and sun.sunset is not None:
        if sun.sunset < sun.sunrise:
            lit = full_day - (sun.sunrise - sun.sunset)
        else:
            lit = sun.sunset - sun.sunrise
    else:
        day_start = sun.noon.replace(hour=0, minute=0, second=0, microsecond=0)
        if sun.sunrise is not None:
            lit = day_start + full_day - sun.sunrise
        elif sun.sunset is not None:
            lit = sun.sunset - day_start
        else:
            lit = full_day if sun.regime is DaylightRegime.WHITE_NIGHTS else timedelta()
    minutes = round(lit.total_seconds() / 60)
    return f"{minutes // 60}:{minutes % 60:02d}"


@dataclass(frozen=True)
class SunDay:
    """The five sun events of one local calendar day (tz-aware local times).

    dawn/sunrise/sunset/dusk are None when the event does not occur on
    that day at that latitude (documented behavior, not an error).
    """

    dawn: datetime | None
    sunrise: datetime | None
    noon: datetime
    sunset: datetime | None
    dusk: datetime | None
    regime: DaylightRegime


def compute_sun_day(
    observer: astral.Observer, local_date: date, tz: ZoneInfo
) -> SunDay:
    def try_event(fn: Callable, **kwargs) -> datetime | None:
        try:
            return fn(observer, date=local_date, tzinfo=tz, **kwargs)
        except ValueError:
            # Documented astral behavior: the event does not occur on this
            # day at this latitude (polar day/night, white nights).
            return None

    dawn = try_event(astral.sun.dawn, depression=constants.CIVIL_DEPRESSION)
    sunrise = try_event(astral.sun.sunrise)
    noon = astral.sun.noon(observer, date=local_date, tzinfo=tz)
    if noon.date() != local_date:
        # astral's noon() lacks the local-date re-search the other events
        # have: in UTC+13/+14 zones (e.g. Kiritimati) the transit of the
        # requested UTC day lands on the NEXT local day — mirror astral's
        # own adjustment by asking for the neighboring UTC day.
        shift = timedelta(days=1 if noon.date() > local_date else -1)
        noon = astral.sun.noon(observer, date=local_date - shift, tzinfo=tz)
    sunset = try_event(astral.sun.sunset)
    dusk = try_event(astral.sun.dusk, depression=constants.CIVIL_DEPRESSION)

    return SunDay(
        dawn=dawn,
        sunrise=sunrise,
        noon=noon,
        sunset=sunset,
        dusk=dusk,
        regime=_classify(observer, noon, dawn, sunrise, sunset, dusk),
    )


def _classify(
    observer: astral.Observer,
    noon: datetime,
    dawn: datetime | None,
    sunrise: datetime | None,
    sunset: datetime | None,
    dusk: datetime | None,
) -> DaylightRegime:
    if sunrise is not None or sunset is not None:
        # The sun crosses the horizon; the sky may or may not get fully dark.
        if dawn is not None or dusk is not None:
            return DaylightRegime.NORMAL
        return DaylightRegime.WHITE_NIGHTS
    if dawn is not None or dusk is not None:
        return DaylightRegime.TWILIGHT_ONLY
    # Only noon exists — decide by how high the sun gets at its best.
    # GEOMETRIC elevation: the -0.833 threshold already contains refraction
    # (astral's own sunrise definition); apparent elevation would count it
    # twice and report POLAR_DAY on all-day-twilight days above ~87 deg.
    noon_elevation = astral.sun.elevation(observer, noon, with_refraction=False)
    if noon_elevation > constants.HORIZON_ELEVATION_DEG:
        return DaylightRegime.POLAR_DAY
    if noon_elevation > constants.CIVIL_TWILIGHT_ELEVATION_DEG:
        # All-day twilight: the sun stays between the horizon and civil
        # depression, so no event boundary exists on this day.
        return DaylightRegime.TWILIGHT_ONLY
    return DaylightRegime.POLAR_NIGHT
