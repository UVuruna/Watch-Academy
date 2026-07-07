"""Offscreen render smoke tests — the same compositor path the widget
paints with, driven headless (QT_QPA_PLATFORM=offscreen)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def frame(app):
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    return compositor.render_offscreen(360.0, 1.0, day, tick)


def test_frame_size_and_transparency(frame):
    assert frame.width() == 360 and frame.height() == 360
    # Corners lie outside the dial circle -> fully transparent.
    assert frame.pixelColor(2, 2).alpha() == 0
    assert frame.pixelColor(357, 357).alpha() == 0


def test_frame_is_painted(frame):
    # Ring band (top edge, just inside the outer radius) must be opaque.
    assert frame.pixelColor(180, 8).alpha() > 200
    # Center area (sun body / hands hub) must be painted.
    assert frame.pixelColor(180, 180).alpha() > 0


def test_dial_is_not_mirrored(frame):
    """The 14–18h sector (RIGHT of the dial, clockwise) is orange; the
    06–10h sector (LEFT) is green. A sign slip in dial_point()/draw_pie()
    that mirrors the dial swaps them — symmetric probes can't see it."""
    right = frame.pixelColor(310, 130)   # dial angle ≈ +69° → orange sector
    assert right.alpha() > 200
    assert right.red() > 150 and right.red() > right.blue()
    assert right.red() > right.green()   # orange family, not green
    left = frame.pixelColor(50, 130)     # dial angle ≈ 291° → green sector
    assert left.alpha() > 200
    assert left.green() > left.red()     # green family, not orange


def test_bands_never_crash_across_polar_year(app):
    """Transitional high-latitude days can lack ANY single boundary event
    even in NORMAL/WHITE_NIGHTS regimes — _bands must degrade, not raise
    (a crash here happens inside paintEvent, where Qt swallows it and the
    dial silently goes blank for the whole day)."""
    from datetime import date, timedelta

    from core.sun import compute_sun_day
    from render.layers import BackgroundLayer

    layer = BackgroundLayer(defaults.DEFAULT_SKIN)
    cities = [
        astral.Observer(latitude=69.6489, longitude=18.9551),   # Tromso
        astral.Observer(latitude=68.97, longitude=33.09),       # Murmansk
        astral.Observer(latitude=78.2232, longitude=15.6267),   # Longyearbyen
    ]
    tz = ZoneInfo("Europe/Oslo")
    day = date(2026, 1, 1)
    while day.year == 2026:
        for observer in cities:
            sun_day = compute_sun_day(observer, day, tz)
            for start, end, shade in layer._bands(sun_day):
                assert end > start
                assert 0.0 <= shade <= 1.0
        day += timedelta(days=1)


def test_moon_terminator_quarters(app):
    """The procedural moon must show the lit half on the correct side at
    the quarter anchors and a full disc at full moon — never all-dark."""
    from types import SimpleNamespace

    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QImage, QPainter

    from render.layers import RenderContext, YearMarkerLayer

    layer = YearMarkerLayer(defaults.DEFAULT_SKIN)
    lit = defaults.DEFAULT_SKIN.year_marker.moon_lit_color

    def render_moon(fraction):
        image = QImage(100, 100, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(50, 50)
        ctx = RenderContext(
            skin=defaults.DEFAULT_SKIN,
            day=SimpleNamespace(moon_fraction=fraction),
            tick=None, radius=50.0, cache=AssetCache(), dpr=1.0,
        )
        layer._draw_moon(painter, ctx, QPointF(0, 0), 80.0)
        painter.end()
        return image

    def is_lit(image, x, y):
        color = image.pixelColor(x, y)
        return color.alpha() > 0 and color.red() > 150

    first_quarter = render_moon(0.25)
    assert is_lit(first_quarter, 65, 50) and not is_lit(first_quarter, 35, 50)
    full = render_moon(0.5)
    assert is_lit(full, 65, 50) and is_lit(full, 35, 50)
    third_quarter = render_moon(0.75)
    assert is_lit(third_quarter, 35, 50) and not is_lit(third_quarter, 65, 50)


def test_noon_sector_is_yellowish(frame):
    # At 12:00 in July the top sector (yellow) is in full daylight; sample
    # inside the background, off the hexagram center line and outside the
    # minute-number radius, at dial angle ~0 +/- a bit.
    color = frame.pixelColor(180, 66)
    assert color.alpha() > 200
    assert color.red() > 150 and color.green() > 120
    assert color.blue() < color.red()  # yellow/orange family, not blue
