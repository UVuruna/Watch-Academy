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
    """The 14–18h side (RIGHT of the dial, clockwise) is orange; the
    06–10h side (LEFT) is green. A sign slip in dial_point()/draw_pie()
    that mirrors the dial swaps them — symmetric probes can't see it."""
    right = frame.pixelColor(297, 135)   # dial angle ≈ +69°, inside the disc
    assert right.alpha() > 200
    assert right.red() > 150 and right.red() > right.blue()
    assert right.red() > right.green()   # orange family, not green
    left = frame.pixelColor(63, 135)     # dial angle ≈ 291° → green side
    assert left.alpha() > 200
    assert left.green() > left.red()     # green family, not orange


def test_disc_touches_the_ring(frame):
    """Owner spec (emphasized twice): NO empty space between the disc and
    the ring — the pixel just inside the disc edge (0.85R, probe at 90°
    between star tips; the ring art with its seconds scale starts at
    0.858R) must be painted."""
    assert frame.pixelColor(333, 180).alpha() > 200


def test_lit_regions_never_crash_across_polar_year(app):
    """Transitional high-latitude days can lack ANY single boundary event
    even in NORMAL/WHITE_NIGHTS regimes — lit_regions must degrade, not
    raise (a crash here happens inside paintEvent, where Qt swallows it
    and the dial silently goes blank for the whole day)."""
    from datetime import date, timedelta

    from core.sun import compute_sun_day
    from render.layers import lit_regions

    spec = defaults.DEFAULT_SKIN.background
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
            for start, end, alpha in lit_regions(sun_day, spec):
                assert end > start
                assert 0.0 < alpha <= 1.0
        day += timedelta(days=1)


def _procedural_moon_skin():
    """DEFAULT_SKIN with the moon image stripped — the terminator tests
    sample pure lit/dark colors, which only the procedural path pins."""
    import dataclasses

    marker = dataclasses.replace(defaults.DEFAULT_SKIN.year_marker, moon_asset=None)
    return dataclasses.replace(defaults.DEFAULT_SKIN, year_marker=marker)


def test_moon_terminator_quarters(app):
    """The procedural moon must show the lit half on the correct side at
    the quarter anchors and a full disc at full moon — never all-dark."""
    from types import SimpleNamespace

    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QImage, QPainter

    from render.layers import RenderContext, YearMarkerLayer

    skin = _procedural_moon_skin()
    layer = YearMarkerLayer(skin)

    def render_moon(fraction):
        image = QImage(100, 100, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(50, 50)
        ctx = RenderContext(
            skin=skin,
            day=SimpleNamespace(moon_fraction=fraction, southern_hemisphere=False),
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


def test_moon_transit_opacity(app):
    """The smaller Moon transits OVER the Earth at reduced opacity when
    they meet on the shared rim; apart (or without the Earth shown) it is
    fully opaque."""
    import dataclasses

    from render.layers import moon_transit_opacity

    base = dataclasses.replace(defaults.DEFAULT_SKIN.year_marker, mode="both")
    assert moon_transit_opacity(base, 100.0, 250.0) == 1.0        # far apart
    assert moon_transit_opacity(base, 100.0, 103.0) == defaults.MOON_TRANSIT_OPACITY
    assert moon_transit_opacity(base, 100.0, 460.0 + 3.0) == defaults.MOON_TRANSIT_OPACITY
    solo = dataclasses.replace(base, mode="moon")                 # no Earth, no transit
    assert moon_transit_opacity(solo, 100.0, 103.0) == 1.0


def test_moon_flips_on_southern_hemisphere(app):
    """Seen from the southern hemisphere the moon is upside down — at
    first quarter the lit half must appear on the LEFT (owner spec)."""
    from types import SimpleNamespace

    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QImage, QPainter

    from render.layers import RenderContext, YearMarkerLayer

    skin = _procedural_moon_skin()
    layer = YearMarkerLayer(skin)
    image = QImage(100, 100, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(50, 50)
    ctx = RenderContext(
        skin=skin,
        day=SimpleNamespace(moon_fraction=0.25, southern_hemisphere=True),
        tick=None, radius=50.0, cache=AssetCache(), dpr=1.0,
    )
    layer._draw_moon(painter, ctx, QPointF(0, 0), 80.0)
    painter.end()
    left, right = image.pixelColor(35, 50), image.pixelColor(65, 50)
    assert left.red() > 150          # lit side on the LEFT
    assert right.red() <= 150


def test_noon_sector_is_yellowish(frame):
    # At 12:00 in July the top sector (yellow) is in full daylight; sample
    # inside the background at dial angle ~16 deg — inside the (rotated)
    # yellow wedge but OFF the 12h axis, where all three hands stack at
    # noon sharp.
    color = frame.pixelColor(210, 75)
    assert color.alpha() > 200
    assert color.red() > 150 and color.green() > 120
    assert color.blue() < color.red()  # yellow/orange family, not blue
