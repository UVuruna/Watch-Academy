"""The Observatory (Session 17): the committed series-bundle integrity,
the season/day-length math goldens, and an offscreen render smoke for
each chart. Headless (QT_QPA_PLATFORM=offscreen)."""

import math
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date, datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import defaults
from core.sun import compute_sun_day, day_length_curve, day_length_minutes
from data.deep_time import DeepTimeRepository
from data.observatory import ObservatoryData


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def data():
    return ObservatoryData()


# --- bundle integrity ---------------------------------------------------------

def test_season_bundle_is_parallel_and_monotonic(data):
    series = data.season_series()
    years = series["years"]
    assert len(years) > 500
    assert years == sorted(years)
    for key in ("spring", "summer", "autumn", "winter", "light", "dark"):
        assert len(series[key]) == len(years)
        assert all(math.isfinite(value) for value in series[key])


def test_season_bundle_spans_the_deep_range(data):
    first, last = data.season_span()
    assert first < -12000       # the deep past
    assert last > 16000         # the deep future


def test_light_dark_are_the_derived_half_sums(data):
    """light = spring + summer, dark = autumn + winter — the linearity
    the bundle relies on (halves derived, not stored)."""
    series = data.season_series()
    for index in (0, len(series["years"]) // 2, -1):
        light = series["spring"][index] + series["summer"][index]
        dark = series["autumn"][index] + series["winter"][index]
        assert series["light"][index] == pytest.approx(light, abs=1e-6)
        assert series["dark"][index] == pytest.approx(dark, abs=1e-6)


def test_present_bin_light_exceeds_dark_by_about_seven_and_a_half(data):
    """The measured record near today: the light half is ~7.5 days
    longer than the dark (Anno Lucis 'today' value 7.542)."""
    series = data.season_series()
    years = series["years"]
    index = min(range(len(years)), key=lambda k: abs(years[k] - 2026))
    delta = series["light"][index] - series["dark"][index]
    assert delta == pytest.approx(7.54, abs=0.2)


def test_eras_carry_the_sealed_anno_lucis(data):
    eras = data.season_eras()
    assert eras["anno_lucis_year"] == -4078          # 4079 BCE
    assert eras["age_of_light"] == [-4078, 6423]
    assert eras["next_anno_lucis"] == 16429


def test_eclipse_density_bundle(data):
    density = data.eclipse_density()
    assert len(density["years"]) == len(density["solar"]) == len(density["lunar"])
    assert sum(density["solar"]) == data.eclipse_meta()["totals"]["solar"]
    assert sum(density["lunar"]) == data.eclipse_meta()["totals"]["lunar"]


# --- day-length goldens (Belgrade) -------------------------------------------

def test_belgrade_solstice_day_lengths():
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    june = day_length_minutes(compute_sun_day(observer, date(2026, 6, 21), tz))
    december = day_length_minutes(compute_sun_day(observer, date(2026, 12, 21), tz))
    assert june == 935          # 15:35 — the mockup day's daylight
    assert december == 527      # 8:47


def test_belgrade_curve_extremes_fall_on_the_solstices():
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    curve = day_length_curve(observer, tz, 2026, step_days=2)
    peak = max(curve, key=lambda pair: pair[1])
    trough = min(curve, key=lambda pair: pair[1])
    assert peak[0].month == 6 and peak[1] == pytest.approx(935, abs=2)
    assert trough[0].month == 12 and trough[1] == pytest.approx(527, abs=2)


# --- render smoke -------------------------------------------------------------

def _open(deep):
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    now = datetime(2026, 7, 18, 12, 0, tzinfo=tz)
    from app.observatory import ObservatoryDialog

    dialog = ObservatoryDialog(
        now, observer, tz, cycles=0, deep=deep, translations={}
    )
    dialog.resize(880, 740)
    return dialog


def test_render_smoke_without_deep_pack(app):
    """The partial installation: every chart draws from the committed
    bundles alone (the eclipse chart on its density fallback)."""
    dialog = _open(None)
    for chart in (
        dialog._season_chart, dialog._envelope,
        dialog._eclipse_chart, dialog._day_chart,
    ):
        chart.resize(800, 240)
        assert not chart.grab().isNull()
    dialog.accept()


def test_render_smoke_with_deep_pack(app):
    """With the pack the eclipse chart draws the exact nearest-eclipse
    scatter; skipped cleanly when the gitignored pack is absent."""
    deep = DeepTimeRepository.detect()
    if deep is None:
        pytest.skip("Deep Time pack not installed")
    dialog = _open(deep)
    assert dialog._eclipse_chart._deep_mode
    assert dialog._eclipse_chart._solar and dialog._eclipse_chart._lunar
    assert not dialog._eclipse_chart.grab().isNull()
    dialog.accept()


def test_season_checkbox_toggles_series_visibility(app):
    dialog = _open(None)
    chart = dialog._season_chart
    # Default: only the two halves lit (the owner's own graph).
    visible = {entry["key"] for entry in chart._visible()}
    assert visible == {"light", "dark"}
    chart.set_visible("summer", True)
    assert "summer" in {entry["key"] for entry in chart._visible()}
    dialog.accept()
