"""Golden values for the time -> dial-angle mapping."""

from datetime import time

import pytest

from core import angles, numerals


@pytest.mark.parametrize(
    ("clock", "expected"),
    [
        (time(12, 0, 0), 0.0),      # noon at the top
        (time(18, 0, 0), 90.0),     # evening on the right
        (time(0, 0, 0), 180.0),     # midnight at the bottom
        (time(6, 0, 0), 270.0),     # morning on the left
        (time(21, 0, 0), 135.0),
    ],
)
def test_dial_angle_quadrants(clock, expected):
    assert angles.time_to_dial_angle(clock) == pytest.approx(expected)


def test_minute_hand_full_hour_revolution():
    assert angles.minute_hand_angle(time(10, 0, 0)) == pytest.approx(0.0)
    assert angles.minute_hand_angle(time(10, 30, 0)) == pytest.approx(180.0)
    assert angles.minute_hand_angle(time(10, 45, 0)) == pytest.approx(270.0)


def test_moon_cycle_angle_mapping():
    # New moon at the TOP, full moon at the BOTTOM, clockwise (owner spec).
    assert angles.moon_cycle_angle(0.0) == pytest.approx(0.0)
    assert angles.moon_cycle_angle(0.5) == pytest.approx(180.0)
    assert angles.moon_cycle_angle(0.25) == pytest.approx(90.0)
    assert angles.moon_cycle_angle(1.0) == pytest.approx(0.0)


def test_star_rotation_sign_convention():
    from datetime import datetime

    # Solar noon an hour EARLY (east of the zone meridian) -> -15 deg (left).
    assert angles.star_rotation_deg(datetime(2026, 7, 7, 11, 0, 0)) == pytest.approx(-15.0)
    # Solar noon an hour LATE (west, or DST) -> +15 deg (right).
    assert angles.star_rotation_deg(datetime(2026, 7, 7, 13, 0, 0)) == pytest.approx(15.0)
    assert angles.star_rotation_deg(datetime(2026, 7, 7, 12, 0, 0)) == pytest.approx(0.0)


def test_ring_position_angle_matches_the_six_hexagram_seats():
    # The Dollar ring's own six positions (CANON.md §The Banknote).
    assert angles.ring_position_angle(12) == pytest.approx(0.0)     # top
    assert angles.ring_position_angle(16) == pytest.approx(60.0)
    assert angles.ring_position_angle(20) == pytest.approx(120.0)
    assert angles.ring_position_angle(24) == pytest.approx(180.0)   # bottom
    assert angles.ring_position_angle(4) == pytest.approx(240.0)
    assert angles.ring_position_angle(8) == pytest.approx(300.0)
    # Equivalent to the two inline formulas this replaces (Rule #5):
    # `(hour*15+DIAL_OFFSET_DEG)%360` and `((hour-12)*15)%360`.
    for hour in range(24):
        assert angles.ring_position_angle(hour) == pytest.approx(
            ((hour - 12) * 15.0) % 360.0
        )


def test_readable_rotation_flips_only_the_lower_half():
    # Upper half: no flip.
    assert angles.readable_rotation_deg(0.0) == pytest.approx(0.0)
    assert angles.readable_rotation_deg(45.0) == pytest.approx(45.0)
    assert angles.readable_rotation_deg(315.0) == pytest.approx(-45.0)
    # Lower half: flipped 180 deg so Omega stands upright at the bottom.
    assert angles.readable_rotation_deg(180.0) == pytest.approx(0.0)
    assert angles.readable_rotation_deg(135.0) == pytest.approx(-45.0)
    assert angles.readable_rotation_deg(225.0) == pytest.approx(45.0)


def test_jewels_stand_upright_on_the_square_angles():
    """ONE SEATING LAW (owner defect 2026-08-07): The One's own 18 (the
    right, 90 deg) and 6 (the left, 270 deg) lay SIDEWAYS while the
    numerals beside them stood upright, because the jewels and the crown
    arcs went through this door while the numerals went through
    `core.numerals.seat_rotation` — two forks of one law, disagreeing on
    exactly the four square angles. This door is now that law."""
    for square in (0.0, 90.0, 180.0, 270.0, 360.0, -90.0):
        assert angles.readable_rotation_deg(square) == pytest.approx(0.0)


def test_one_seating_law_for_jewels_and_numerals():
    """The two doors agree at EVERY angle now, not only the square ones
    — the reconciliation Rule #5 demands (no second copy left to drift
    out of step with the first)."""
    for tenth in range(3600):
        theta = tenth / 10.0
        assert angles.readable_rotation_deg(theta) == pytest.approx(
            numerals.fold_angle(numerals.seat_rotation(theta, "arc"))
        )


def test_upright_law_survives_a_rotated_offset():
    """The Heliocentric case: with the world turned by an arbitrary
    offset, whatever jewel LANDS on a square angle is the one that
    stands up — the law is about the SEAT, never about the hour."""
    offset = 37.5
    seated = [
        (hour, (angles.ring_position_angle(hour) + offset) % 360.0)
        for hour in range(1, 25)
    ]
    upright = [
        hour for hour, theta in seated
        if angles.readable_rotation_deg(theta) == pytest.approx(0.0)
    ]
    # 37.5 deg is 2.5 hours of band: no hour seat lands square, so
    # nothing stands upright — every jewel rides the arc.
    assert upright == []
    # Turn the world by a whole 90 deg and exactly the four hours that
    # moved ONTO the square angles stand up.
    seated = [
        (hour, (angles.ring_position_angle(hour) + 90.0) % 360.0)
        for hour in range(1, 25)
    ]
    upright = sorted(
        hour for hour, theta in seated
        if angles.readable_rotation_deg(theta) == pytest.approx(0.0)
    )
    assert upright == [6, 12, 18, 24]
