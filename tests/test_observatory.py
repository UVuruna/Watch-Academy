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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QPushButton,
    QSplitter,
    QWidget,
)

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
    """Fix round G, Task 1: the clamp is now the SMALLER of the fraction
    and the absolute floor (`_min_zoom_span`) — on the envelope's huge
    multi-millennial span the absolute floor wins, letting the user zoom
    far tighter than the old fraction-only clamp allowed."""
    from app.observatory import _min_zoom_span

    dialog = _open(None)
    chart = dialog._envelope
    chart.resize(800, 240)
    full_span = chart._full_xhi - chart._full_xlo
    for _ in range(200):
        chart._zoom_at(400.0, 0.5)
    min_span = _min_zoom_span(full_span)
    assert min_span < full_span * defaults.OBSERVATORY_ZOOM_MIN_FRACTION
    assert (chart._xhi - chart._xlo) >= min_span - 1e-6
    assert (chart._xhi - chart._xlo) <= min_span + 1e-6
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


# --- Fix round G (owner verdicts 2026-07-19, slika 8 + addendum) ---------------

def _panel_of(chart) -> QWidget:
    """Walk up from a chart widget to its splitter-pane panel (Fix round
    G, Task 2/3 — every chart lives inside a small title+filter+chart
    container that IS the splitter child)."""
    widget = chart
    while widget.parentWidget() is not None:
        widget = widget.parentWidget()
        if isinstance(widget.parentWidget(), QSplitter):
            return widget
    raise AssertionError("chart is not inside a splitter panel")


def _enlarge_button_of(chart) -> QPushButton:
    panel = _panel_of(chart)
    buttons = [b for b in panel.findChildren(QPushButton) if b.text() == "Enlarge"]
    assert len(buttons) == 1
    return buttons[0]


# Task 1 — the adaptive tick ladder ----------------------------------------------

def test_nice_step_ladder_is_year_friendly():
    from app.observatory import _nice_step

    # Near/at the tightened max-zoom floor, the ladder bottoms out at a
    # 1-year pitch (owner: "na max zumu TICK na 1 GODINU").
    assert _nice_step(6, 8) == 1
    assert _nice_step(8, 8) == 1
    # A ~50-year window already reads far finer than the old fixed
    # look (single-digit years), proving the pitch genuinely adapts.
    assert _nice_step(50, 8) == 10
    # The full multi-millennial span keeps a coarse, "today's density"
    # pitch (thousands of years) — not hundreds of gridlines.
    assert _nice_step(30_000, 8) == 5000
    assert _nice_step(400_000, 8) == 50_000


def test_tick_pitch_adapts_from_full_span_to_max_zoom(app):
    """The tick-ladder unit test the round asks for: the SAME chart, at
    its full span, shows a coarse pitch; zoomed to the tightened max
    (OBSERVATORY_ZOOM_MIN_SPAN_FLOOR), the pitch is exactly 1 year."""
    dialog = _open(None)
    chart = dialog._envelope
    chart.resize(800, 240)

    full_ticks = chart._x_ticks()
    full_step = full_ticks[1] - full_ticks[0]
    assert full_step >= 1000

    for _ in range(200):
        chart._zoom_at(400.0, 0.5)
    assert (chart._xhi - chart._xlo) <= defaults.OBSERVATORY_ZOOM_MIN_SPAN_FLOOR + 1e-6
    zoomed_ticks = chart._x_ticks()
    assert len(zoomed_ticks) >= 2
    assert zoomed_ticks[1] - zoomed_ticks[0] == 1
    dialog.accept()


def test_y_ticks_honor_the_hours_scale(app):
    """Fix round G, Task 1: the Hours switch recomputes nice y-ticks IN
    the scaled space, so the tick values land on round HOUR numbers
    (not leftover day-fraction noise) once converted."""
    dialog = _open(None)
    envelope = dialog._envelope
    envelope.resize(800, 240)

    day_ticks = envelope._y_ticks()
    assert len(day_ticks) >= 2

    dialog._units_combo.setCurrentIndex(1)   # Hours
    assert envelope._y_scale == 24.0
    hour_ticks = [value * 24 for value in envelope._y_ticks()]
    for value in hour_ticks:
        assert value == pytest.approx(round(value), abs=1e-6)

    dialog._units_combo.setCurrentIndex(0)   # back to Days
    assert envelope._y_scale == 1.0
    dialog.accept()


def test_day_length_chart_shows_months_full_then_days_zoomed(app):
    """Task 1's day-length carve-out: the full year shows the 12
    calendar months; zoomed in tight it falls to real calendar days."""
    dialog = _open(None)
    chart = dialog._day_chart
    chart.resize(800, 240)

    full_ticks = chart._x_ticks()
    assert len(full_ticks) == 12
    assert chart._fmt_x(full_ticks[0]) == "Jan"
    assert not chart._is_zoomed()

    chart._zoom_at(50.0, 0.02)
    assert chart._is_zoomed()
    label = chart._fmt_x(chart._xlo)
    month_part, _, day_part = label.partition(" ")
    assert month_part == "Jan"
    assert day_part.isdigit()
    dialog.accept()


# Task 2 — adjustable chart height (QSplitter) -----------------------------------

def test_splitter_holds_one_panel_per_chart(app):
    dialog = _open(None)
    dialog.resize(900, 3000)
    dialog.show()
    QApplication.processEvents()
    assert dialog._splitter.orientation() == Qt.Orientation.Vertical
    assert dialog._splitter.childrenCollapsible() is False
    assert dialog._splitter.count() == 5
    sizes = dialog._splitter.sizes()
    assert len(sizes) == 5
    assert all(size >= defaults.OBSERVATORY_CHART_MIN_HEIGHT_PX for size in sizes)
    dialog.close()


def test_dragging_the_splitter_grows_the_chart_widget(app):
    dialog = _open(None)
    dialog.resize(900, 3000)
    dialog.show()
    QApplication.processEvents()
    before = dialog._season_chart.height()
    sizes = dialog._splitter.sizes()
    sizes[0] += 200
    sizes[1] -= 200
    dialog._splitter.setSizes(sizes)
    QApplication.processEvents()
    after = dialog._season_chart.height()
    assert after == before + 200
    dialog.close()


def test_splitter_sizes_persist_across_reopens_this_session(app, monkeypatch):
    """Task 2: SESSION-only persistence — a module-level cache (no
    settings key), matching that this dialog's own window geometry is
    likewise not written to disk."""
    import app.observatory as observatory_module
    monkeypatch.setattr(observatory_module, "_last_splitter_sizes", None)

    dialog1 = _open(None)
    dialog1.resize(900, 3000)
    dialog1.show()
    QApplication.processEvents()
    custom = list(dialog1._splitter.sizes())
    custom[0] += 200
    custom[1] -= 200
    dialog1._splitter.setSizes(custom)
    QApplication.processEvents()
    dialog1._on_splitter_moved(0, 0)   # simulate the drag signal
    assert observatory_module._last_splitter_sizes == custom
    dialog1.close()

    dialog2 = _open(None)
    dialog2.resize(900, 3000)
    dialog2.show()
    QApplication.processEvents()
    assert dialog2._splitter.sizes() == custom
    dialog2.close()


# Task 3 — the per-chart Enlarge dialog -------------------------------------------

def test_every_panel_has_exactly_one_enlarge_button(app):
    dialog = _open(None)
    dialog.show()
    QApplication.processEvents()
    for chart in (
        dialog._season_chart, dialog._envelope, dialog._eclipse_chart,
        dialog._day_chart, dialog._laskar_chart,
    ):
        button = _enlarge_button_of(chart)
        assert button.isVisible()
    dialog.close()


def test_enlarge_dialog_hosts_the_same_chart_and_carries_zoom_state(app, monkeypatch):
    """Task 3: reparenting (not copying) the panel means the SAME chart
    instance, its zoom/pan view AND its checkbox state, carry into the
    enlarged dialog and back out again untouched."""
    import app.observatory as observatory_module

    dialog = _open(None)
    dialog.resize(900, 3000)
    dialog.show()
    QApplication.processEvents()

    chart = dialog._season_chart
    chart.resize(800, 240)
    # Toggling a series checkbox re-fits the full view (existing Fix
    # round D behavior) — so flip it FIRST, then zoom, so the captured
    # "before" state below is what actually survives the round trip.
    checkboxes = {
        box.text(): box for box in _panel_of(chart).findChildren(QCheckBox)
    }
    checkboxes[dialog._tr("Summer")].setChecked(True)
    visible_before = {entry["key"] for entry in chart._visible()}
    assert "summer" in visible_before

    chart._zoom_at(400.0, 0.3)
    view_before = (chart._xlo, chart._xhi)
    assert chart._is_zoomed()

    index_before = dialog._splitter.indexOf(_panel_of(chart))

    captured = []
    mid_flight = {}

    class _RecordingEnlarge(observatory_module._EnlargeDialog):
        def exec(self):
            # IMPORTANT: inspect the "genuinely open" state IN HERE —
            # _open_enlarged only restores the panel to the splitter
            # AFTER exec() returns (matching the real modal flow, where
            # restoration happens after the user closes the window).
            # Checking `self` from OUTSIDE exec() would see the panel
            # already moved back out.
            mid_flight["chart_embedded"] = chart.parentWidget() is not None
            mid_flight["grab_ok"] = not self.grab().isNull()
            mid_flight["view"] = (chart._xlo, chart._xhi)
            captured.append(self)
            return 0

    monkeypatch.setattr(observatory_module, "_EnlargeDialog", _RecordingEnlarge)

    button = _enlarge_button_of(chart)
    assert button.isVisible()
    button.click()

    assert len(captured) == 1
    enlarged = captured[0]
    assert enlarged._chart is chart          # the SAME widget, not a copy
    assert mid_flight["chart_embedded"]      # genuinely hosted while "open"
    assert mid_flight["grab_ok"]             # builds and paints without error
    assert mid_flight["view"] == view_before  # zoom carried IN

    # State survived the round trip untouched.
    assert (chart._xlo, chart._xhi) == view_before
    assert {entry["key"] for entry in chart._visible()} == visible_before

    # The panel (title + filter + chart) is back where it was.
    assert dialog._splitter.indexOf(_panel_of(chart)) == index_before
    assert button.isVisible()
    dialog.close()


def test_enlarge_dialog_extended_legend_and_laskar_caption(app, monkeypatch):
    """Task 3: the extended legend carries every series' color chip and
    a current-value readout, and the Laskar chart's info strip keeps
    its doctrine caption (owner: "the Laskar chart keeps its doctrine
    caption")."""
    import app.observatory as observatory_module

    dialog = _open(None)
    dialog.resize(900, 3000)
    dialog.show()
    QApplication.processEvents()
    chart = dialog._laskar_chart

    captured = []

    class _RecordingEnlarge(observatory_module._EnlargeDialog):
        def exec(self):
            captured.append(self)
            return 0

    monkeypatch.setattr(observatory_module, "_EnlargeDialog", _RecordingEnlarge)
    _enlarge_button_of(chart).click()

    enlarged = captured[0]
    texts = [label.text() for label in enlarged.findChildren(QLabel)]
    assert any("Analytic orbital solution" in text for text in texts)
    # Every legend label appears with a ": value" readout.
    for label, _ in chart._legend():
        assert any(text.startswith(f"{label}:") for text in texts)
    dialog.close()


def test_enlarge_dialog_render_smoke_for_every_chart(app, monkeypatch):
    """Offscreen smoke: every chart's enlarged view builds and paints
    without error WHILE GENUINELY OPEN (extended legend + info strip +
    the reparented chart itself, not just the shell left behind after
    the panel already returned to the splitter)."""
    import app.observatory as observatory_module

    dialog = _open(None)
    dialog.resize(900, 3000)
    dialog.show()
    QApplication.processEvents()

    grabbed_ok = []
    chart_embedded = []

    class _RecordingEnlarge(observatory_module._EnlargeDialog):
        def exec(self):
            chart_embedded.append(self._chart.parentWidget() is not None)
            grabbed_ok.append(not self.grab().isNull())
            return 0

    monkeypatch.setattr(observatory_module, "_EnlargeDialog", _RecordingEnlarge)

    for chart in (
        dialog._season_chart, dialog._envelope, dialog._eclipse_chart,
        dialog._day_chart, dialog._laskar_chart,
    ):
        grabbed_ok.clear()
        chart_embedded.clear()
        _enlarge_button_of(chart).click()
        assert chart_embedded == [True]
        assert grabbed_ok == [True]
    dialog.close()


def test_dialog_with_splitter_renders_at_a_small_size(app):
    """Task 2's "plays fine with the per-panel scroll" claim: a small
    window still lays out and paints (the scroll area takes over)
    without error — no crash, no zero-sized splitter."""
    dialog = _open(None)
    dialog.resize(900, 400)
    dialog.show()
    QApplication.processEvents()
    assert dialog._splitter.count() == 5
    assert not dialog.grab().isNull()
    dialog.close()
