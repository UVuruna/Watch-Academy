"""Golden values for the time -> dial-angle mapping."""

from datetime import time

import pytest

from core import angles


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


def test_hexagram_rotation_sign_convention():
    from datetime import datetime

    # Solar noon an hour EARLY (east of the zone meridian) -> -15 deg (left).
    assert angles.hexagram_rotation_deg(datetime(2026, 7, 7, 11, 0, 0)) == pytest.approx(-15.0)
    # Solar noon an hour LATE (west, or DST) -> +15 deg (right).
    assert angles.hexagram_rotation_deg(datetime(2026, 7, 7, 13, 0, 0)) == pytest.approx(15.0)
    assert angles.hexagram_rotation_deg(datetime(2026, 7, 7, 12, 0, 0)) == pytest.approx(0.0)
