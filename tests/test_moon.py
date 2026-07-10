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


def test_waning_segment_runs_forward(window_2026):
    """Third Quarter → New Moon spans 0.75 → 1.0, NOT 0.75 → 0.0 backward:
    2026-07-10 noon sits mid-segment at ≈0.85 (a natural refactor to
    (f1−f0) interpolation would render it as near-full 0.44 instead of a
    waning crescent — this pins the direction)."""
    now = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
    assert phase_fraction(now, window_2026) == pytest.approx(0.852, abs=0.002)


def test_wrap_to_zero_at_new_moon_anchor(window_2026):
    new_moons = [t for t, f in window_2026.events if f == 0.0 and t.year == 2026]
    assert new_moons, "2026 must contain new moons"
    assert phase_fraction(new_moons[0], window_2026) == pytest.approx(0.0, abs=1e-9)


def test_moon_rise_set_belgrade():
    """Belgrade 2026-07-10 (waning crescent): the moon rises just after
    midnight and sets mid-afternoon — 00:43 / 16:33 local per astral
    (minute resolution). The Moon hover's od–do line reads these."""
    from datetime import date
    from zoneinfo import ZoneInfo

    import astral

    from config import defaults
    from core.moon import moon_rise_set

    city = defaults.DEFAULT_CITY
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    rise, setting = moon_rise_set(
        observer, date(2026, 7, 10), ZoneInfo(city["timezone"])
    )
    assert rise.strftime("%H:%M") == "00:43"
    assert setting.strftime("%H:%M") == "16:33"
    assert rise.tzinfo is not None and setting.tzinfo is not None


def test_meteorological_summer_2026():
    """Cross-arm hover bounds (owner spec): summer runs from halfway
    spring-equinox→summer-solstice to halfway summer-solstice→autumn-
    equinox — 2026: 5 May 23:35 to 7 Aug 04:14 (UTC anchors carry
    seconds, so the printed anchor minutes round differently)."""
    from core.year_wheel import meteorological_span
    from data.seasons import SeasonsRepository

    anchors = SeasonsRepository().year_anchors(2026)
    start, end = meteorological_span(anchors, 360.0)   # the summer solstice
    assert start.strftime("%d %b %H:%M") == "05 May 23:35"
    assert end.strftime("%d %b %H:%M") == "07 Aug 04:14"


def test_outside_window_fails_loudly(window_2026):
    with pytest.raises(ValueError, match="outside the moon window"):
        phase_fraction(datetime(2031, 1, 1, tzinfo=timezone.utc), window_2026)


def test_coverage_edge_year_still_interpolates():
    """1551 has no 1550 neighbor — the 2-year window must still bracket
    instants inside the year itself."""
    window = MoonPhaseRepository().moon_window(1551)
    assert window.events[0][0].year == 1551
    mid = datetime(1551, 7, 1, tzinfo=timezone.utc)
    assert 0.0 <= phase_fraction(mid, window) < 1.0


def test_may_2026_has_five_events(window_2026):
    may = [(t, f) for t, f in window_2026.events if (t.year, t.month) == (2026, 5)]
    assert len(may) == 5
    assert sum(1 for _, f in may if f == 0.5) == 2  # two full moons


def test_third_quarter_normalization(window_2026):
    fractions = {f for _, f in window_2026.events}
    assert fractions == {0.0, 0.25, 0.5, 0.75}


def test_window_spans_neighbor_years(window_2026):
    assert window_2026.events[0][0].year == 2025
    assert window_2026.events[-1][0].year == 2027


def test_phase_names_follow_the_common_convention():
    """A principal name holds only around its instant; the day after the
    Third Quarter (owner checked online for 8 July 2026) the moon must
    already read Waning Crescent."""
    from core.moon import phase_name

    assert phase_name(0.75) == "Third Quarter"          # the instant itself
    assert phase_name(0.76) == "Third Quarter"          # within +-half a day
    assert phase_name(0.774) == "Waning Crescent"       # ~0.7 days after
    assert phase_name(0.0) == "New Moon"
    assert phase_name(0.98) == "Waning Crescent"
    assert phase_name(0.99) == "New Moon"               # approaching the instant
    assert phase_name(0.12) == "Waxing Crescent"
    assert phase_name(0.35) == "Waxing Gibbous"
    assert phase_name(0.5) == "Full Moon"
    assert phase_name(0.6) == "Waning Gibbous"


def test_illumination_curve():
    assert illumination(0.0) == pytest.approx(0.0)
    assert illumination(0.25) == pytest.approx(0.5)
    assert illumination(0.5) == pytest.approx(1.0)
    assert illumination(0.75) == pytest.approx(0.5)
