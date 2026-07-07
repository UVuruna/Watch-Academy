"""Composition test: DayContext/TickState built through the real
repositories for a known moment (Belgrade, 2026-07-07 12:00 CEST)."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import astral
import pytest

from core.clock_state import build_day_context, build_tick_state
from core.sun import DaylightRegime
from data.locations import LocationRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository


@pytest.fixture(scope="module")
def belgrade_noon_context():
    record = next(
        r for r in LocationRepository().find_city("Belgrade") if "Serbia" in r.path
    )
    tz = ZoneInfo(record.timezone)
    now = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=record.latitude, longitude=record.longitude)
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return now, day


def test_day_context(belgrade_noon_context):
    now, day = belgrade_noon_context
    assert day.local_date == date(2026, 7, 7)
    assert day.utc_offset == timedelta(hours=2)          # CEST
    assert day.cache_key == (date(2026, 7, 7), timedelta(hours=2))
    assert day.weekday_index == 1                        # Tuesday -> mars
    assert day.sun.regime is DaylightRegime.NORMAL
    # July in CEST: solar noon runs ~40 min late -> hexagram tilted right.
    assert 8.0 < day.hexagram_rotation < 13.0
    assert day.moon_fraction == pytest.approx(0.74, abs=0.01)


def test_tick_state(belgrade_noon_context):
    now, day = belgrade_noon_context
    tick = build_tick_state(now, day)
    assert tick.hour_angle == pytest.approx(0.0)         # 12:00 at the top
    assert tick.minute_angle == pytest.approx(0.0)
    # ~16 days after the summer solstice: ~1 deg/day clockwise from the top.
    assert 12.0 < tick.year_angle < 20.0
