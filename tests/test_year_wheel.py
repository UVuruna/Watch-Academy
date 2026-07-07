"""Year-wheel golden values against the LIVE seasons database.

The four cardinal points must land EXACTLY on 0/90/180/270 — naive
linear interpolation over the tropical year puts the autumn equinox at
~92.3 deg and these tests reject it.
"""

from datetime import datetime, timedelta, timezone

import pytest

from core.year_wheel import year_marker_angle
from data.seasons import SeasonsRepository


@pytest.fixture(scope="module")
def anchors_2026():
    return SeasonsRepository().year_anchors(2026)


def test_cardinal_points_exact(anchors_2026):
    spring, summer, autumn, winter = anchors_2026.instants[1:5]
    assert year_marker_angle(spring, anchors_2026) == pytest.approx(270.0, abs=1e-9)
    assert year_marker_angle(summer, anchors_2026) == pytest.approx(0.0, abs=1e-9)
    assert year_marker_angle(autumn, anchors_2026) == pytest.approx(90.0, abs=1e-9)
    assert year_marker_angle(winter, anchors_2026) == pytest.approx(180.0, abs=1e-9)


def test_angle_is_monotonic_through_summer_quarter(anchors_2026):
    summer, autumn = anchors_2026.instants[2], anchors_2026.instants[3]
    quarter = autumn - summer
    samples = [
        year_marker_angle(summer + quarter * i / 8, anchors_2026) for i in range(1, 8)
    ]
    assert samples == sorted(samples)
    assert 40.0 < samples[3] < 50.0  # halfway through the quarter is near 45 deg


def test_outside_span_fails_loudly(anchors_2026):
    with pytest.raises(ValueError, match="outside the anchor span"):
        year_marker_angle(
            anchors_2026.instants[0] - timedelta(days=1), anchors_2026
        )


def test_mockup_day_earth_near_top():
    """20.6.2025 (mockup) is a day before the summer solstice — the Earth
    marker must sit within ~2 deg of the dial top."""
    anchors = SeasonsRepository().year_anchors(2025)
    angle = year_marker_angle(
        datetime(2025, 6, 20, 14, 34, tzinfo=timezone.utc), anchors
    )
    assert min(angle, 360.0 - angle) < 2.0


def test_winter_field_trap(anchors_2026):
    """entry.start is the PREVIOUS December solstice; winter.start is THIS
    year's December solstice; end is NEXT year's spring equinox."""
    instants = anchors_2026.instants
    assert (instants[0].year, instants[0].month) == (2025, 12)
    assert (instants[4].year, instants[4].month) == (2026, 12)
    assert (instants[5].year, instants[5].month) == (2027, 3)
