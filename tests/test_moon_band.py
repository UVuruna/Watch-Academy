"""THE MOON HORIZON BAND — geometry and None-day rule (owner verdict
2026-08-09). `core.moon.moon_horizon_arcs` is the single source the
render layer (`render.layers.moon_band`) and its tests both read.

Angles here are checked against `core.angles.time_to_dial_angle`
directly — the ONE dial mapping (Rule #5) — never re-derived.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

import astral.moon
from astral import LocationInfo

from core import angles
from core.moon import moon_horizon_arcs


def _angle(hour: int, minute: int = 0) -> float:
    return angles.time_to_dial_angle(time(hour, minute))


def test_both_none_is_a_full_circle() -> None:
    """Polar edge: the moon skips both events. Mirrors `_is_moon_up`'s
    own "never lie about hiding a visible moon" policy — treated as UP,
    so the band covers the whole ring."""
    arcs = moon_horizon_arcs(None, None)
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.full_circle is True
    assert arc.end_deg - arc.start_deg == 360.0


def test_rise_only_runs_from_midnight_to_set() -> None:
    """No rise today (already up at 00:00), sets at 06:00."""
    moonset = datetime(2026, 1, 1, 6, 0)
    arcs = moon_horizon_arcs(None, moonset)
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.start_deg == _angle(0, 0)
    assert arc.end_deg % 360.0 == _angle(6, 0)
    assert not arc.full_circle


def test_set_only_runs_from_rise_to_midnight() -> None:
    """Rises at 20:00, stays up past midnight (no set today)."""
    moonrise = datetime(2026, 1, 1, 20, 0)
    arcs = moon_horizon_arcs(moonrise, None)
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.start_deg == _angle(20, 0)
    assert arc.end_deg % 360.0 == _angle(0, 0)
    assert arc.end_deg > arc.start_deg


def test_ordinary_day_single_arc() -> None:
    """Rise before set, same day — the plain single-arc case."""
    moonrise = datetime(2026, 1, 1, 6, 0)
    moonset = datetime(2026, 1, 1, 18, 0)
    arcs = moon_horizon_arcs(moonrise, moonset)
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc.start_deg == _angle(6, 0)
    assert arc.end_deg % 360.0 == _angle(18, 0)
    assert arc.culmination_deg == (arc.start_deg + arc.end_deg) / 2.0 % 360.0


def test_up_across_midnight_gives_two_arcs() -> None:
    """Set (04:00) happens BEFORE rise (22:00) that same calendar day:
    up at midnight, sets, then rises again before the next midnight."""
    moonrise = datetime(2026, 1, 1, 22, 0)
    moonset = datetime(2026, 1, 1, 4, 0)
    arcs = moon_horizon_arcs(moonrise, moonset)
    assert len(arcs) == 2
    first, second = arcs
    assert first.start_deg == _angle(0, 0)
    assert first.end_deg % 360.0 == _angle(4, 0)
    assert second.start_deg == _angle(22, 0)
    assert second.end_deg % 360.0 == _angle(0, 0)


def test_golden_belgrade_mockup_day() -> None:
    """The suite's golden Belgrade mockup day (2025-06-20): the arc's
    endpoints must equal `time_to_dial_angle` applied to astral's own
    moonrise/moonset for that day — no angle is re-derived by the band
    geometry, it only orders/unwraps what astral reports."""
    tz = ZoneInfo("Europe/Belgrade")
    belgrade = LocationInfo("Belgrade", "Serbia", "Europe/Belgrade", 44.8, 20.47)
    day = datetime(2025, 6, 20, tzinfo=tz).date()
    moonrise = astral.moon.moonrise(belgrade.observer, day, tz)
    moonset = astral.moon.moonset(belgrade.observer, day, tz)
    assert moonrise is not None and moonset is not None

    arcs = moon_horizon_arcs(moonrise, moonset)
    expected_start = angles.time_to_dial_angle(moonrise)
    expected_end = angles.time_to_dial_angle(moonset)
    if moonrise <= moonset:
        assert len(arcs) == 1
        assert arcs[0].start_deg == expected_start
        assert arcs[0].end_deg % 360.0 == expected_end
    else:
        assert len(arcs) == 2
        assert arcs[0].start_deg == angles.time_to_dial_angle(time(0, 0))
        assert arcs[0].end_deg % 360.0 == expected_end
        assert arcs[1].start_deg == expected_start
        assert arcs[1].end_deg % 360.0 == angles.time_to_dial_angle(time(0, 0))
