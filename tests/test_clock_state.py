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
    assert day.southern_hemisphere is False
    assert day.sun.regime is DaylightRegime.NORMAL
    # July in CEST: solar noon runs ~40 min late -> hexagram tilted right.
    assert 8.0 < day.hexagram_rotation < 13.0
    assert day.moon_fraction == pytest.approx(0.74, abs=0.01)


def test_cache_key_uses_the_offset_of_now_on_dst_day(belgrade_noon_context):
    """On the spring-forward day (2026-03-29, Belgrade) midnight is still
    CET (+1) but noon is CEST (+2). The cache key must carry the offset of
    NOW — otherwise it never matches the controller's key after the
    transition and the day context rebuilds every minute."""
    record_now, day = belgrade_noon_context
    tz = record_now.tzinfo
    dst_noon = datetime(2026, 3, 29, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=44.82, longitude=20.46)
    dst_day = build_day_context(
        dst_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    assert dst_day.cache_key == (date(2026, 3, 29), timedelta(hours=2))


def test_is_daylight_on_inverted_midnight_sun_day():
    """Murmansk 2026-05-20: this day's sunset (00:01) falls BEFORE its
    sunrise (01:26) — the sun is up ~22.5 h and noon must be daylight,
    while the short 00:01–01:26 gap is night."""
    tz = ZoneInfo("Europe/Moscow")
    observer = astral.Observer(latitude=68.97, longitude=33.09)
    day = build_day_context(
        datetime(2026, 5, 20, 12, 0, tzinfo=tz),
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    assert day.sun.sunset < day.sun.sunrise  # the inverted shape itself
    noon_tick = build_tick_state(datetime(2026, 5, 20, 12, 0, tzinfo=tz), day)
    assert noon_tick.is_daylight is True
    gap_tick = build_tick_state(datetime(2026, 5, 20, 0, 45, tzinfo=tz), day)
    assert gap_tick.is_daylight is False


def test_tick_state(belgrade_noon_context):
    now, day = belgrade_noon_context
    tick = build_tick_state(now, day)
    assert tick.hour_angle == pytest.approx(0.0)         # 12:00 at the top
    assert tick.minute_angle == pytest.approx(0.0)
    # ~16 days after the summer solstice: ~1 deg/day clockwise from the top.
    assert 12.0 < tick.year_angle < 20.0
    assert tick.is_daylight is True                      # noon in July
