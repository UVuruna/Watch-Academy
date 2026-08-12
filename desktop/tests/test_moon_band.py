"""THE MOON HORIZON BAND — geometry and None-day rule (owner verdict
2026-08-09). `core.moon.moon_horizon_arcs` is the single source the
render layer (`render.layers.moon_band`) and its tests both read.

Angles here are checked against `core.angles.time_to_dial_angle`
directly — the ONE dial mapping (Rule #5) — never re-derived.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

import astral.moon
import pytest
from astral import LocationInfo

from app.controller import build_skin
from app.settings_store import Settings, SettingsStore, replace
from config import constants
from core import angles
from core.moon import moon_horizon_arcs
from render.layers.moon_band import MoonBandLayer


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


# --- SETTINGS defaults + persistence ----------------------------------------


def test_settings_defaults_are_mode_a_silver_thread() -> None:
    """Owner spec: Mode A ("horizon") + style 2 (silver thread) is THE
    DEFAULT."""
    settings = Settings()
    assert settings.moon_band_mode == "horizon"
    assert settings.moon_band_style == "silver_thread"


def test_settings_round_trip_moon_band(tmp_path) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    saved = replace(Settings(), moon_band_mode="dim_only", moon_band_style="glow")
    store.save(saved)
    loaded = store.load()
    assert loaded.moon_band_mode == "dim_only"
    assert loaded.moon_band_style == "glow"


def test_ticks_style_has_no_connecting_arc_line() -> None:
    """Owner correction (2026-08-09, grader round): "ticks" must NOT
    draw a continuous arc/thread — that reads as "silver_thread" at a
    glance, which the approved design forbids. Proof: sweep fine
    angular samples along the SAME radius the arc's own style draws at
    and measure what fraction is painted — "silver_thread" is a
    continuous line (~100% painted); "ticks" is discrete segments with
    real gaps between them (meaningfully under 100%)."""
    import math as _math

    from core.moon import MoonArc
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    arc = MoonArc(180.0, 270.0, 225.0)
    band_radius = 900.0    # large radius: sub-degree gaps are many px wide here

    def _painted_fraction(method_name: str, sample_radius: float) -> float:
        canvas = 2000
        image = QImage(canvas, canvas, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(canvas / 2, canvas / 2)
        layer = MoonBandLayer.__new__(MoonBandLayer)
        getattr(layer, method_name)(painter, band_radius, arc)
        painter.end()
        hits = 0
        samples = 0
        # A dense sweep across the arc's own middle third, well clear of
        # its rise/set ends (dots/diamond on the thread style) and any
        # rounding at the extreme angles.
        for i in range(3000):
            angle = 195.0 + i * (60.0 / 3000.0)
            rad = _math.radians(angle)
            x = round(canvas / 2 + sample_radius * _math.sin(rad))
            y = round(canvas / 2 - sample_radius * _math.cos(rad))
            if image.pixelColor(x, y).alpha() > 0:
                hits += 1
            samples += 1
        return hits / samples

    # The thread rides the line radius itself (owner corrections
    # 2026-08-10/11 — no inset); the gray ticks hang INWARD from it, so
    # they are sampled in the middle of their own measured zone.
    thread_fraction = _painted_fraction("_draw_silver_thread", band_radius)
    ticks_fraction = _painted_fraction("_draw_ticks", band_radius * 0.98)
    assert thread_fraction > 0.9, (
        f"silver_thread must read as a continuous line (got {thread_fraction:.0%} painted)"
    )
    assert ticks_fraction < 0.7, (
        "ticks style must leave real gaps between discrete segments — no "
        f"connecting arc/thread line (got {ticks_fraction:.0%} painted, "
        "too close to a continuous line)"
    )


def test_settings_reject_unknown_mode_falls_back_to_default(tmp_path) -> None:
    """An unrecognized stored value (a hand-edited file, or a retired
    choice) must fall back to the documented default, never raise."""
    store = SettingsStore(tmp_path / "settings.json")
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}, '
        '"display": {"moon_band_mode": "bogus", "moon_band_style": "bogus"}}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.moon_band_mode == constants.MOON_BAND_MODE_DEFAULT
    assert loaded.moon_band_style == constants.MOON_BAND_STYLE_DEFAULT


# --- SKIN wiring + mode/style smoke test ------------------------------------


@pytest.mark.parametrize("style", constants.MOON_BAND_STYLES)
def test_every_style_paints_without_error(style) -> None:
    """A smoke test for all 4 styles: each one paints a real Skin/
    RenderContext-shaped scene without raising, both for the ordinary
    single-arc case and the both-None full-circle case."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    from core.moon import MoonArc

    image = QImage(64, 64, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(32, 32)
    layer = MoonBandLayer.__new__(MoonBandLayer)
    dispatch = {
        "inverted": layer._draw_inverted,
        "ticks": layer._draw_ticks,
        "glow": layer._draw_glow,
    }.get(style, layer._draw_silver_thread)
    dispatch(painter, 28.0, MoonArc(180.0, 270.0, 225.0))
    dispatch(painter, 28.0, MoonArc(180.0, 540.0, 0.0, full_circle=True))
    painter.end()


def test_moon_band_mode_gates_the_skin_field() -> None:
    """`build_skin` overlays `Settings.moon_band_mode`/`_style` onto
    `skin.year_marker` — the plain pass-through `app.controller.
    _overlay_display_settings` performs, checked here without
    constructing a live `WatchController`."""
    settings = replace(
        Settings(), moon_band_mode="always_full", moon_band_style="ticks",
    )
    skin = build_skin(settings, location_display="Belgrade, Serbia")
    assert skin.year_marker.moon_band_mode == "always_full"
    assert skin.year_marker.moon_band_style == "ticks"


def test_redress_paints_inside_the_ring_below_every_ring_element() -> None:
    """THE Z SEAT OF THE BAND REDRESS (owner repeat correction
    2026-08-11, slika 5-7: "OPET INVERT IMA VECI Z INDEX OD JEWELS"):
    the per-degree invert/ticks redress paints INSIDE `RingLayer`,
    after the base-plate blit and BEFORE the band plates — and the
    jewels/crown draw after the bands in `paint` — so every ring
    element outranks the redress by construction. The retired
    above-the-ring layer must never come back."""
    import inspect

    from render.layers import ring as ring_module
    from render.layers.ring import RingLayer

    bands_src = inspect.getsource(RingLayer._draw_bands)
    redress_at = bands_src.index("_draw_band_redress")
    assert redress_at > bands_src.index("draw_pixmap_centered"), (
        "the redress must paint AFTER the base plate"
    )
    assert redress_at < bands_src.index('_blit_band(painter, ctx, "inner")'), (
        "the redress must paint BEFORE the band plates"
    )
    paint_src = inspect.getsource(RingLayer.paint)
    assert paint_src.index("_draw_bands") < paint_src.index("_draw_jewels"), (
        "jewels must draw above the bands (and so above the redress)"
    )
    assert not hasattr(
        __import__("render.layers.moon_band", fromlist=["x"]),
        "MoonBandTicksLayer",
    ), "the above-the-ring ticks layer is retired for good"


def test_spared_seats_follow_the_measured_fifteen_degree_strokes() -> None:
    """THE MEASURED PLATE (owner slika 6/7, 2026-08-11): the big
    strokes stand every FIFTEEN degrees on the plate (pixel-measured),
    so the redress spares a one-degree shoulder around every 15th
    degree and dresses everything else."""
    from render.layers.moon_band import _seat_spared

    for seat in range(0, 360, 15):
        for shoulder in (-1, 0, 1):
            assert _seat_spared((seat + shoulder) % 360)
    assert not _seat_spared(3)
    assert not _seat_spared(7)
    assert not _seat_spared(22)
