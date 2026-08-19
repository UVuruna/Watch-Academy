"""Time -> dial-angle mapping.

The ONE shared mapping (Rule #5) used by the hour hand, every sun-event
arc boundary and the solar-noon marker. All angles are degrees, clockwise,
0 at the top of the dial, ready for QPainter.rotate() in y-down screen
coordinates.
"""

from datetime import datetime, time

from config import dial


def time_to_dial_angle(t: datetime | time) -> float:
    """Dial angle of a local wall-clock time.

    12:00 -> 0 (top), 18:00 -> 90 (right), 00:00 -> 180 (bottom),
    06:00 -> 270 (left).
    """
    secs = t.hour * dial.SECONDS_PER_HOUR + t.minute * 60 + t.second
    return (secs / dial.SECONDS_PER_DAY * 360.0 + dial.DIAL_OFFSET_DEG) % 360.0


def minute_hand_angle(t: datetime | time) -> float:
    """Angle of the large hand: one revolution per hour, 0 at the top."""
    return (t.minute * 60 + t.second) / dial.SECONDS_PER_HOUR * 360.0


def second_hand_angle(t: datetime | time) -> float:
    """Angle of the seconds hand: one revolution per minute, 0 at the top."""
    return t.second * 6.0


def moon_cycle_angle(fraction: float) -> float:
    """Dial angle of the moon-cycle marker: new moon at the TOP (0 deg),
    full moon at the BOTTOM (180 deg), moving clockwise (owner spec)."""
    return (fraction * 360.0) % 360.0


def ring_position_angle(position: int) -> float:
    """Dial angle of a FIXED ring position/hour (0 top, clockwise) — the
    six hexagram seats (12/16/20/24/4/8) and every other ring hour share
    this one mapping. Equivalent to, and replacing, the two inline copies
    this used to be (`RingLayer._draw_jewels`'s
    `(hour*15+DIAL_OFFSET_DEG)%360` and the compositor's per-letter
    legend hover's `((hour-12)*15)%360` — both the SAME formula written
    two ways; Rule #5, one shared function now). Used by the ring's own
    letters, the per-letter hover legend and the outer Great Seal crown text
    arc (`core.crown_text`) alike, so a pinned letter and its ring seat always
    agree by construction."""
    return (position * 15.0 + dial.DIAL_OFFSET_DEG) % 360.0


def readable_rotation_deg(theta: float) -> float:
    """The glyph rotation that keeps ring-band letters upright as they
    travel around the circle (owner spec): tangential, but the LOWER
    half (90-270 deg) flips 180 deg so text never reads upside down —
    Omega stands upright at the bottom. Shared by the ring's own jewels
    and the outer crown text arc (`render.layers.ring.RingLayer`, Rule #5).

    ONE SEATING LAW (owner defect 2026-08-07 — The One's 18 at the right
    and 6 at the left "lie sideways"): this used to be a SECOND, forked
    copy of the law `core.numerals.seat_rotation` already wrote, and the
    fork differed on exactly the four SQUARE angles — where the numerals
    stand UPRIGHT and the jewels beside them lay down tangentially. Two
    laws, one ring, visibly disagreeing. Rule #5 says there is one law,
    so this is now a thin alias of `seat_rotation`'s `"arc"` seating and
    the square-angle rule reaches the jewels and the crown arcs too.
    `seat_rotation` states the law UNFOLDED (its own documented
    contract — `rot(120) == 300`), while this door has always answered
    in (-180, 180]; the fold below is the only difference between them
    and it is a no-op physically. With it, every NON-square angle is
    bit-identical to the old fork (pinned by `tests/test_angles.py`), so
    nothing else on any dial moves."""
    from core.numerals import fold_angle, seat_rotation

    return fold_angle(seat_rotation(theta, "arc"))


def hours_between(angle_a: float, angle_b: float) -> float:
    """Shortest SIGNED hours from dial angle `angle_b` to `angle_a`,
    wrapped to [-12, 12) — 15 deg/hour, the SAME clockwise-from-top
    mapping `time_to_dial_angle` uses. Shared pure building block for
    every SOLAR-ANCHOR time-window test (round R3b item 3, the CENTER
    seat's dual/ninth face law) — the two angles are typically the
    live hour hand and a solar noon/midnight anchor, but the function
    itself knows nothing about either, so it stays reusable."""
    return ((angle_a - angle_b + 180.0) % 360.0 - 180.0) / 15.0


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
        solar_noon.hour * dial.SECONDS_PER_HOUR
        + solar_noon.minute * 60
        + solar_noon.second
    )
    return (secs - dial.SOLAR_NOON_SECS) / dial.SECONDS_PER_DEGREE
