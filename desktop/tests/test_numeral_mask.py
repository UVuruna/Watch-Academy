"""THE NUMBER'S OWN RECTANGLE — the inner-band mask's two bounds
(owner corrections 2026-08-11, slika 1 and 8): the 360 hairlines are
the cutting limit, and the seat's own big stroke is removed WHOLE by a
narrow wedge that spares the neighbouring hairlines. Pins
`render.numeral_bands.inner_number_clear_regions`.
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from app.skin_builder import build_skin
from app.settings_store import Settings
from config import dial
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render import numeral_bands
from render.assets import AssetCache
from render.context import RenderContext
from render.layers.numerals import band_spec
from render.painting import dial_point


@pytest.fixture(scope="module")
def app():
    existing = QApplication.instance()
    if existing is not None:
        return existing
    try:
        return QApplication([])
    except Exception:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        return QApplication([])


@pytest.fixture(scope="module")
def frame_args():
    now = datetime(2026, 1, 1, 12, 35, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.8, longitude=20.5)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)



def test_clear_region_never_cuts_the_hairlines_and_takes_the_stroke_whole(
    app, frame_args
):
    """THE TWO BOUNDS ON THE CUT (owner corrections 2026-08-11, slika 1
    and 8): the numeral mask (a) never reaches the 360 hairlines — they
    are "the cutting limit" — and (b) removes the seat's own big stroke
    WHOLE via a narrow wedge, sparing the hairlines a degree to either
    side."""
    from PySide6.QtCore import QPointF

    from config import dial
    from render.layers.numerals import band_spec
    from render.painting import dial_point

    day, tick = frame_args
    skin = build_skin(Settings())
    ctx = RenderContext(
        skin=skin, day=day, tick=tick, radius=400.0, cache=AssetCache(), dpr=1.0,
    )
    spec = band_spec(skin, "inner", ctx)
    region = numeral_bands.inner_number_clear_regions(spec)
    if region.isEmpty():
        pytest.skip("variant with no composed numbers")
    seats = [angle for _l, angle, _c in numeral_bands._seats(spec)]
    shrink = numeral_bands.interior_scale(spec.ring_size)
    half = spec.pixels / 2.0 / spec.dpr
    tick_mid = half * shrink * (
        dial.RING_INNER_TICK_INNER_FRACTION + dial.RING_INNER_TICK_OUTER_FRACTION
    ) / 2.0
    stroke_mid = half * shrink * (
        dial.RING_INNER_CONTENT_INNER_FRACTION + dial.RING_INNER_TICK_INNER_FRACTION
    ) / 2.0
    for degree in range(360):
        near_seat = any(
            min(abs(degree - s % 360.0), 360.0 - abs(degree - s % 360.0)) <= 0.8
            for s in seats
        )
        inside = region.contains(dial_point(float(degree), tick_mid))
        if near_seat:
            continue                      # the wedge may take the seat degree
        assert not inside, f"hairline at {degree} deg is cut by the mask"
    for seat in seats:
        assert region.contains(dial_point(seat % 360.0, tick_mid)), (
            f"seat {seat}: the stroke's outer part must be masked (no stub)"
        )
        assert region.contains(dial_point(seat % 360.0, stroke_mid)), (
            f"seat {seat}: the stroke must go whole"
        )
