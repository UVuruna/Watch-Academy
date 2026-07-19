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


def test_stay_on_top_flag_follows_the_z_mode(app):
    """Fix round A (owner verdict 2026-07-19, screenshots): with the
    dial in "top" z-mode it is natively HWND_TOPMOST, so the Observatory
    must carry WindowStaysOnTopHint too to open ABOVE it (matching
    Settings/Time Travel/Guide) — off by default (2026-07-13 intent:
    a normal window everywhere else)."""
    from PySide6.QtCore import Qt

    from app.observatory import ObservatoryDialog

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    now = datetime(2026, 7, 18, 12, 0, tzinfo=tz)
    normal = ObservatoryDialog(now, observer, tz)
    assert not (normal.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
    on_top = ObservatoryDialog(now, observer, tz, stay_on_top=True)
    assert on_top.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


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


# --- Fix round D (owner verdicts 2026-07-19) -----------------------------------

# Task 1 — zoom math / y-fit ----------------------------------------------------

def test_zoom_narrows_view_and_autofits_y(app):
    """Zooming in around the cursor's x narrows the view symmetrically
    toward that point, and the y axis re-fits to the narrower slice
    (never wider than the un-zoomed y range for a monotonically-varying
    series like the day-length curve)."""
    dialog = _open(None)
    chart = dialog._day_chart
    chart.resize(800, 240)
    full_span = chart._full_xhi - chart._full_xlo
    full_ylo, full_yhi = chart._ylo, chart._yhi
    # Zoom in repeatedly at the left edge of the plot (near day 1).
    for _ in range(6):
        chart._zoom_at(60.0, defaults.OBSERVATORY_ZOOM_FACTOR)
    zoomed_span = chart._xhi - chart._xlo
    assert zoomed_span < full_span
    assert chart._xlo >= chart._full_xlo - 1e-6
    assert chart._xhi <= chart._full_xhi + 1e-6
    # The day-length curve is smooth — a narrow early-year slice has a
    # tighter y range than the whole year (peak at the June solstice).
    assert (chart._yhi - chart._ylo) < (full_yhi - full_ylo)
    dialog.accept()


def test_zoom_clamps_to_the_minimum_span(app):
    dialog = _open(None)
    chart = dialog._envelope
    chart.resize(800, 240)
    full_span = chart._full_xhi - chart._full_xlo
    for _ in range(200):
        chart._zoom_at(400.0, 0.5)
    min_span = full_span * defaults.OBSERVATORY_ZOOM_MIN_FRACTION
    assert (chart._xhi - chart._xlo) >= min_span - 1e-6
    dialog.accept()


def test_double_click_resets_the_view(app):
    dialog = _open(None)
    chart = dialog._envelope
    chart.resize(800, 240)
    chart._zoom_at(400.0, 0.3)
    assert (chart._xhi - chart._xlo) < (chart._full_xhi - chart._full_xlo)
    chart._reset_view()
    assert chart._xlo == pytest.approx(chart._full_xlo)
    assert chart._xhi == pytest.approx(chart._full_xhi)
    dialog.accept()


# Task 2 — the Days/Hours units switch ------------------------------------------

def test_units_switch_is_a_pure_times_24_display_transform(app):
    dialog = _open(None)
    envelope = dialog._envelope
    ys_before = list(envelope._series[0]["ys"])
    # Default: days.
    assert "24" not in envelope._fmt_y(1.0)
    dialog._units_combo.setCurrentIndex(1)   # Hours
    assert "24" in envelope._fmt_y(1.0)
    # The underlying series is untouched by the unit switch — display only.
    assert envelope._series[0]["ys"] == ys_before
    dialog._units_combo.setCurrentIndex(0)   # back to days
    assert "24" not in envelope._fmt_y(1.0)
    dialog.accept()


def test_units_switch_reaches_the_season_chart_diff_line(app):
    dialog = _open(None)
    season = dialog._season_chart
    dialog._units_combo.setCurrentIndex(1)   # Hours
    assert "24" in season._diff_fmt(1.0)
    dialog._units_combo.setCurrentIndex(0)   # Days
    assert "24" not in season._diff_fmt(1.0)
    dialog.accept()


# Task 3 — every light/dark peak marked ------------------------------------------

def test_light_dark_extrema_finds_every_local_peak(data):
    marks = data.light_dark_extrema()
    assert len(marks) >= 2          # at least one light peak + one dark peak
    kinds = {kind for _, _, kind in marks}
    assert kinds <= {"light_peak", "dark_peak"}
    assert "light_peak" in kinds and "dark_peak" in kinds
    years = [year for year, _, _ in marks]
    assert years == sorted(years)   # ascending, from the ascending bundle
    # Peaks and troughs must alternate (a real local-extrema series).
    for (_, _, a), (_, _, b) in zip(marks, marks[1:]):
        assert a != b


def test_envelope_vmarks_include_every_measured_peak(app):
    dialog = _open(None)
    extrema = ObservatoryData().light_dark_extrema()
    # 2 sealed era marks (Anno Lucis, Age of Darkness) + one per extremum.
    assert len(dialog._envelope._vmarks) == 2 + len(extrema)
    dialog.accept()


# Task 4 — the Laskar long envelope bundle + chart -------------------------------

def test_laskar_envelope_bundle_integrity(data):
    laskar = data.laskar_envelope()
    years = laskar["years"]
    assert len(years) == len(laskar["signed_days"]) == len(laskar["envelope_days"])
    assert 300 < len(years) < 1000          # "~1000 points" budget (Task 4)
    assert years == sorted(years)
    assert min(years) <= -195000 and max(years) >= 195000   # +/-200,000-yr window
    # The envelope is the |sin|=1 bound on the signed oscillation.
    for signed, envelope in zip(laskar["signed_days"], laskar["envelope_days"]):
        assert envelope >= 0
        assert abs(signed) <= envelope + 1e-6
    meta = data.laskar_envelope_meta()
    lo, hi = meta["de441_window_years"]
    assert lo < -12000 and hi > 16000        # the DE441-measured window
    assert "coming_ecc_min" in meta["extrema"]
    ecc_min = meta["extrema"]["coming_ecc_min"]
    assert 20000 < ecc_min["year"] < 35000   # ~+28,000 CE (owner's suspected trough)
    assert ecc_min["envelope_days"] < 3.0    # near-vanishing amplitude


def test_laskar_envelope_render_smoke(app):
    dialog = _open(None)
    chart = dialog._laskar_chart
    chart.resize(800, 240)
    assert not chart.grab().isNull()
    assert chart._full_xlo is not None
    # The +/- band shares one legend entry (dedup, Task 4).
    labels = [label for label, _ in chart._legend()]
    assert labels.count(dialog._tr("amplitude envelope")) == 1
    dialog.accept()
