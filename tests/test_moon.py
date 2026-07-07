"""Moon-phase golden values against the LIVE moon phases database."""

from datetime import datetime, timezone

import pytest

from core.moon import illumination, phase_fraction
from data.moon_phases import MoonPhaseRepository


@pytest.fixture(scope="module")
def window_2026():
    return MoonPhaseRepository().moon_window(2026)


def test_reference_moment(window_2026):
    """2026-07-07: interpolated fraction 0.7400 (astral cross-check 0.7401)."""
    now = datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc)
    assert phase_fraction(now, window_2026) == pytest.approx(0.74, abs=0.01)


def test_exact_at_anchors(window_2026):
    full_moons = [t for t, f in window_2026.events if f == 0.5 and t.year == 2026]
    assert full_moons, "2026 must contain full moons"
    assert phase_fraction(full_moons[0], window_2026) == pytest.approx(0.5, abs=1e-9)


def test_may_2026_has_five_events(window_2026):
    may = [t for t, _ in window_2026.events if (t.year, t.month) == (2026, 5)]
    assert len(may) == 5  # including two full moons


def test_third_quarter_normalization(window_2026):
    fractions = {f for _, f in window_2026.events}
    assert fractions == {0.0, 0.25, 0.5, 0.75}


def test_window_spans_neighbor_years(window_2026):
    assert window_2026.events[0][0].year == 2025
    assert window_2026.events[-1][0].year == 2027


def test_illumination_curve():
    assert illumination(0.0) == pytest.approx(0.0)
    assert illumination(0.25) == pytest.approx(0.5)
    assert illumination(0.5) == pytest.approx(1.0)
    assert illumination(0.75) == pytest.approx(0.5)
