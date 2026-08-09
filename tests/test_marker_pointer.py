"""THE POSITION POINTER (owner feature 2026-08-09, Settings ▸ Earth,
off by default): a small triangle at the Earth/Moon orbit circle, at
each body's own angle, colored with the SAME ramp hue the ring
jewels/crown text wear. See `render.layers.year_marker.YearMarkerLayer.
_draw_orbit_pointer` and `app.controller._overlay_display_settings`.
"""

import dataclasses
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings
from app.watch_face import thumbs
from config import defaults, palette
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def moment():
    now = datetime(2026, 7, 7, 12, 0, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.8, longitude=20.5)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def test_off_by_default(app):
    assert Settings().show_marker_pointer is False
    skin = build_skin(Settings())
    assert skin.year_marker.pointer_enabled is False


def test_setting_flips_the_skin_flag(app):
    skin = build_skin(dataclasses.replace(Settings(), show_marker_pointer=True))
    assert skin.year_marker.pointer_enabled is True


def test_default_color_is_the_ring_finish_hue(app):
    """The default gold "classic" ring finish resolves to the SAME hue
    `thumbs.shade_hue` reads for the Settings dialog's own metal-shade
    swatches — never a hardcoded hex (THE PALETTE COLOUR LAW)."""
    skin = build_skin(Settings())
    expected = thumbs.shade_hue("gold", "classic")
    assert expected is not None
    assert skin.year_marker.pointer_color == expected


def test_color_follows_the_ring_finish(app):
    """A silver ring finish resolves to the silver ramp's own hue —
    the pointer wears whatever the ring jewels/crown text wear, not a
    fixed color."""
    skin = build_skin(dataclasses.replace(Settings(), ring_finish="silver"))
    expected = thumbs.shade_hue("silver", Settings().metal_shade_silver)
    assert expected is not None
    assert skin.year_marker.pointer_color == expected
    assert skin.year_marker.pointer_color != build_skin(Settings()).year_marker.pointer_color


def test_fallback_is_the_palette_law_color(app):
    """A metal `thumbs.shade_hue` cannot resolve falls back to
    `palette.MARKER_POINTER_FALLBACK_COLOR` — never a bare hex inline."""
    assert thumbs.shade_hue("nonexistent-metal", "nonexistent-shade") is None
    assert palette.MARKER_POINTER_FALLBACK_COLOR.startswith("#")


def test_pointer_on_changes_the_render_near_the_markers(app, moment):
    """A real render diff: turning the pointer on paints NEW pixels
    right at the Earth/Moon markers' own edge that the pointer-off
    render does not have."""
    day, tick = moment
    off = Compositor(
        build_skin(dataclasses.replace(Settings(), diameter=720)), AssetCache(),
    ).render_offscreen(720.0, 1.0, day, tick)
    on = Compositor(
        build_skin(dataclasses.replace(
            Settings(), diameter=720, show_marker_pointer=True,
        )), AssetCache(),
    ).render_offscreen(720.0, 1.0, day, tick)
    differing = sum(
        1
        for x in range(0, 720, 3)
        for y in range(0, 720, 3)
        if off.pixelColor(x, y) != on.pixelColor(x, y)
    )
    assert differing > 0


def test_pointer_never_reaches_the_minute_band_or_the_outer_ring(app):
    """The pointer's own tip protrusion stays inside THE CLEAR ORBIT
    LANE's own clearance margin — it never re-opens the gap Task 1
    closed."""
    from config import dial

    assert (
        dial.MARKER_POINTER_PROTRUSION_FRACTION
        < dial.EARTH_MOON_ORBIT_CLEARANCE_FRACTION
    )
