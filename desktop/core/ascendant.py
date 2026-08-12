"""The ASCENDANT — the zodiac sign rising on the eastern horizon
(owner request 2026-07-12: the natal "podznak", cycling through all
twelve signs daily). Pure math: Julian date -> Greenwich mean sidereal
time -> local sidereal time (RAMC) -> the ascendant ecliptic longitude
via the standard spherical formula. Validated against the owner's own
birth chart (20.6.1990 12:15 CEST Belgrade -> Virgo)."""

import math
from datetime import datetime, timezone

_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


def julian_date(moment_utc: datetime) -> float:
    """Astronomical Julian date of a UTC instant (Meeus)."""
    year, month = moment_utc.year, moment_utc.month
    day = moment_utc.day + (
        moment_utc.hour
        + moment_utc.minute / 60.0
        + moment_utc.second / 3600.0
    ) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    century = year // 100
    gregorian = 2 - century + century // 4
    return (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day + gregorian - 1524.5
    )


def ascendant_longitude(
    moment: datetime, latitude: float, longitude: float
) -> float:
    """Ecliptic longitude of the ascendant in degrees [0, 360).
    `moment` may carry any timezone — it is reduced to UTC here;
    east longitude positive, like the rest of the app."""
    moment_utc = moment.astimezone(timezone.utc)
    jd = julian_date(moment_utc)
    t = (jd - 2451545.0) / 36525.0
    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - t ** 3 / 38710000.0
    ) % 360.0
    ramc = math.radians((gmst + longitude) % 360.0)
    obliquity = math.radians(23.4392911 - 0.0130042 * t)
    phi = math.radians(latitude)
    return math.degrees(math.atan2(
        math.cos(ramc),
        -(
            math.sin(ramc) * math.cos(obliquity)
            + math.tan(phi) * math.sin(obliquity)
        ),
    )) % 360.0


def ascendant_sign(
    moment: datetime, latitude: float, longitude: float
) -> str:
    """The rising sign name ("Virgo") at the instant and place."""
    return _SIGNS[
        int(ascendant_longitude(moment, latitude, longitude) // 30.0) % 12
    ]
