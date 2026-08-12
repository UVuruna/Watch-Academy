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


def test_jewels_flow_on_the_side_squares_and_stand_on_top_and_bottom():
    """ONE SEATING LAW, as amended by THE FLOWING SIDES (owner
    2026-08-11: "6 and 18 behave exactly like 45 and 15"): only the top
    and bottom seats stand upright; the side squares flow with the half
    they open clockwise, which lands both at -90 in this door's folded
    output. Still ONE law for jewels, crown arcs and numerals — the
    amendment moved the law itself, not a fork of it."""
    for square in (0.0, 180.0, 360.0):
        assert angles.readable_rotation_deg(square) == pytest.approx(0.0)
    for side in (90.0, 270.0, -90.0):
        assert angles.readable_rotation_deg(side) == pytest.approx(-90.0)


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
    # Turn the world by a whole 90 deg and exactly the two hours that
    # moved ONTO the top and bottom seats stand up (the side squares
    # flow — THE FLOWING SIDES amendment, 2026-08-11).
    seated = [
        (hour, (angles.ring_position_angle(hour) + 90.0) % 360.0)
        for hour in range(1, 25)
    ]
    upright = sorted(
        hour for hour, theta in seated
        if angles.readable_rotation_deg(theta) == pytest.approx(0.0)
    )
    assert upright == [6, 18]
