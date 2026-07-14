"""Elements switches (owner spec, FINAL.txt #5): each switch removes one
dial element — Earth, Moon, Weekday, Pointer, Colorful (white Aura),
Seconds — while the day/twilight indication always stays."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
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
from render.compositor import Compositor, _build_layers
from render.layers import (
    BottomSlotLayer,
    CenterBodyLayer,
    HandLayer,
    StarLayer,
    WeekdayLayer,
    YearMarkerLayer,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def july_wednesday(app):
    """2026-07-08 (a Wednesday) at noon in Belgrade."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def test_pointer_off_drops_the_star_but_keeps_the_octa_slot():
    """Owner correction: hiding the Pointer element removes the
    diamonds, but the octa info slot keeps showing its selection."""
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa", show_pointer=False
    )
    layers = _build_layers(skin)
    assert not any(isinstance(layer, StarLayer) for layer in layers)
    assert any(isinstance(layer, BottomSlotLayer) for layer in layers)


def test_weekday_off_drops_the_bodies_and_the_center():
    layers = _build_layers(
        dataclasses.replace(defaults.DEFAULT_SKIN, show_weekday=False)
    )
    assert not any(isinstance(layer, WeekdayLayer) for layer in layers)
    assert not any(isinstance(layer, CenterBodyLayer) for layer in layers)


def test_markers_off_drop_the_year_marker_layer():
    layers = _build_layers(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, show_earth=False, show_moon=False
        )
    )
    assert not any(isinstance(layer, YearMarkerLayer) for layer in layers)
    # One marker still on keeps the layer (it gates internally).
    layers = _build_layers(
        dataclasses.replace(defaults.DEFAULT_SKIN, show_earth=False)
    )
    assert any(isinstance(layer, YearMarkerLayer) for layer in layers)


def test_compass_slot_has_its_own_switch():
    """Owner spec: the Compass info slot is an Element of its own — it
    survives Pointer-off but disappears with its own switch."""
    kept = _build_layers(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", show_pointer=False
        )
    )
    assert any(isinstance(layer, BottomSlotLayer) for layer in kept)
    dropped = _build_layers(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", show_octa_slot=False
        )
    )
    assert not any(isinstance(layer, BottomSlotLayer) for layer in dropped)


def test_earth_date_switch_gates_the_label(july_wednesday):
    """Owner spec: the date ON the Earth marker has its own switch —
    render differs at 720 px when toggled, and stays identical at
    360 px where the label never draws anyway."""
    day, tick = july_wednesday
    with_date = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        720.0, 1.0, day, tick
    )
    without = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, show_earth_date=False),
        AssetCache(),
    ).render_offscreen(720.0, 1.0, day, tick)
    assert with_date != without
    small_on = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    small_off = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, show_earth_date=False),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    assert small_on == small_off


def test_seconds_off_drops_the_third_hand():
    on = _build_layers(defaults.DEFAULT_SKIN)
    off = _build_layers(
        dataclasses.replace(defaults.DEFAULT_SKIN, show_seconds=False)
    )
    count = lambda layers: sum(isinstance(layer, HandLayer) for layer in layers)
    assert count(on) == 3
    assert count(off) == 2


def test_colorful_off_paints_the_aura_white(july_wednesday):
    """Colorful off keeps the day arc visible but drains its hue: a lit
    pixel over the gray Umbra reads neutral (R=G=B) instead of a
    saturated palette wedge. Other elements are switched off so the
    probe cannot land on a marker or the star."""
    day, tick = july_wednesday
    bare = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        show_pointer=False, show_weekday=False,
        show_earth=False, show_moon=False,
    )
    probe = (250, 110)                          # 45 deg, 0.55R — mid-afternoon arc
    colored = Compositor(bare, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    pixel = colored.pixelColor(*probe)
    assert max(pixel.red(), pixel.green(), pixel.blue()) - min(
        pixel.red(), pixel.green(), pixel.blue()
    ) > 40                                      # palette hue is saturated
    white = Compositor(
        dataclasses.replace(bare, colorful=False), AssetCache()
    ).render_offscreen(360.0, 1.0, day, tick)
    pixel = white.pixelColor(*probe)
    assert max(pixel.red(), pixel.green(), pixel.blue()) - min(
        pixel.red(), pixel.green(), pixel.blue()
    ) < 12                                      # white transparency stays neutral


def test_element_scales_flow_into_the_specs():
    """Owner EXTRAS: the Settings size multipliers scale the spec values
    (so the render AND the hover hit regions follow), and the octa slot
    and hover-enlarge factors ride the skin fields."""
    from app.controller import build_skin
    from app.settings_store import Settings, replace

    base = build_skin(Settings())
    scaled = build_skin(
        replace(
            Settings(),
            earth_scale=2.0, moon_scale=0.5,
            slot_scale=1.5, hover_enlarge=1.4,
        )
    )
    assert scaled.year_marker.scale == base.year_marker.scale * 2.0
    assert scaled.year_marker.moon_scale == base.year_marker.moon_scale * 0.5
    # ONE slot size (owner 2026-07-14): the merged slider drives the
    # bodies AND every subdial through diamond_scale.
    assert scaled.weekday_set.diamond_scale == base.weekday_set.diamond_scale * 1.5
    assert scaled.weekday_set.center_scale == base.weekday_set.center_scale * 1.5
    assert scaled.hover_enlarge == 1.4


def test_hover_enlarge_grows_the_hovered_body(july_wednesday):
    """Hovering a weekday body draws IT larger (one shared factor,
    owner EXTRAS): with the cursor parked on Jupiter's top slot the
    body's pixels reach beyond its normal radius."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, solar_rotation=False,
        show_earth=False, show_moon=False, hover_enlarge=1.6,
    )
    compositor = Compositor(skin, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    spec = defaults.DEFAULT_SKIN.weekday_set
    orbit = 180.0 * spec.orbit_fraction
    body_edge_px = 180.0 * spec.diamond_scale        # normal half-size
    # A probe just OUTSIDE the normal body edge, above the center but
    # OFF the exact vertical — the noon-pointing hands cover the
    # center strip and would eat the pixel difference.
    probe = (170, round(180.0 - orbit - body_edge_px - 4))
    plain = compositor.render_offscreen(360.0, 1.0, day, tick)
    assert compositor.set_hover(180.0, 180.0 - orbit, 360.0)
    hovered = compositor.render_offscreen(360.0, 1.0, day, tick)
    # Just outside the body's normal edge: only the ENLARGED render
    # reaches the probe, so the pixel changes under the hover.
    assert hovered.pixelColor(*probe) != plain.pixelColor(*probe)
    assert compositor.set_hover(-1.0e9, -1.0e9, 360.0)   # leave clears it
    cleared = compositor.render_offscreen(360.0, 1.0, day, tick)
    assert cleared.pixelColor(*probe) == plain.pixelColor(*probe)


def test_hidden_elements_take_no_hovers(july_wednesday):
    """A switched-off element must not answer hovers: the Wednesday body
    slot (weekday off) and the arm regions (pointer off) go silent —
    the spot falls through to the wheel itself, which reads the NIGHT
    there (midnight region, hover rework 5)."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        solar_rotation=False,
        show_weekday=False, show_pointer=False,
        show_earth=False, show_moon=False,
    )
    compositor = Compositor(skin, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    # Wednesday=mercury sits at exactly 180 deg when upright; with the
    # weekday element off (and the arms off) no body or arm answers —
    # only the wheel's own night hover.
    tip = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Night" in tip and "Mercury" not in tip and "align='justify'" not in tip
