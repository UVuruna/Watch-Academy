"""Time -> dial-angle mapping.

The ONE shared mapping (Rule #5) used by the hour hand, every sun-event
arc boundary and the solar-noon marker. All angles are degrees, clockwise,
0 at the top of the dial, ready for QPainter.rotate() in y-down screen
coordinates.
"""

from datetime import datetime, time

from config import constants


def time_to_dial_angle(t: datetime | time) -> float:
    """Dial angle of a local wall-clock time.

    12:00 -> 0 (top), 18:00 -> 90 (right), 00:00 -> 180 (bottom),
    06:00 -> 270 (left).
    """
    secs = t.hour * constants.SECONDS_PER_HOUR + t.minute * 60 + t.second
    return (secs / constants.SECONDS_PER_DAY * 360.0 + constants.DIAL_OFFSET_DEG) % 360.0


def minute_hand_angle(t: datetime | time) -> float:
    """Angle of the large hand: one revolution per hour, 0 at the top."""
    return (t.minute * 60 + t.second) / constants.SECONDS_PER_HOUR * 360.0


def second_hand_angle(t: datetime | time) -> float:
    """Angle of the seconds hand: one revolution per minute, 0 at the top."""
    return t.second * 6.0


def moon_cycle_angle(fraction: float) -> float:
    """Dial angle of the moon-cycle marker: new moon at the TOP (0 deg),
    full moon at the BOTTOM (180 deg), moving clockwise (owner spec)."""
    return (fraction * 360.0) % 360.0


def star_rotation_deg(solar_noon: datetime) -> float:
    """Rotation of the star (and solar-noon arrow) from the dial top.

    Positive rotates clockwise/right — solar noon later than 12:00 local
    (city west of its zone meridian, or DST active); negative rotates
    counterclockwise/left (city east of the meridian). 15 deg per hour of
    offset.

    Computed from integer seconds-since-local-midnight: datetime
    subtraction around noon yields negative timedeltas that invite sign
    bugs.
    """
    secs = (
        solar_noon.hour * constants.SECONDS_PER_HOUR
        + solar_noon.minute * 60
        + solar_noon.second
    )
    return (secs - constants.SOLAR_NOON_SECS) / constants.SECONDS_PER_DEGREE
