"""THE CALENDAR WHEELS DO NOT TURN (owner order 2026-08-13).

North is ALWAYS the summer solstice and ALWAYS the new moon. The world
offset moves what the CLOCK draws — the hour hand, the hour numbers, the
jewels, the eclipse body at its hour — because those are positions in
TIME. The year wheel and the moon cycle are positions in the CALENDAR,
and a calendar does not swing when the sky is redrawn.

Before this round the offset was added to both, so turning Solar Rotation
on swung the summer solstice off north — the owner's report: "POZICIJE
EARTH I MOON treba uvek da su ISTE ... to NE SME DA SE ROTIRA - kao sto
ni SEKUNDARA ni MINUTARA ne prate rotaciju".
"""

import types

import pytest
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings
from render.context import RenderContext
from render.layers.year_marker import earth_marker_angle, moon_marker_angle

# The offsets a real dial actually reaches: 0 in Geocentric, the night
# half-turn, and the solar rotation's measured extremes (Belgrade DST
# runs -4.17..+10.76, Tromso far wider).
OFFSETS = (0.0, 10.76, -4.17, 90.0, 180.0, 189.5, 359.0)


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def ctx_factory(app):
    """The two angles read only the skin, the tick and the offset — a
    real skin, a stand-in tick, and no day (the Almanac branch is off for
    every pointer but the Calendar, and this is the default one)."""
    skin = build_skin(Settings())

    def make(offset: float) -> RenderContext:
        tick = types.SimpleNamespace(
            year_angle=137.5, moon_fraction=0.31, hour_angle=42.0,
        )
        return RenderContext(
            skin=skin, day=None, tick=tick,
            radius=360.0, cache=None, dpr=1.0, world_offset=offset,
        )
    return make


def test_the_calendar_wheels_never_take_the_world_offset(ctx_factory):
    base_earth = earth_marker_angle(ctx_factory(0.0))
    base_moon = moon_marker_angle(ctx_factory(0.0))
    for offset in OFFSETS:
        ctx = ctx_factory(offset)
        assert earth_marker_angle(ctx) == pytest.approx(base_earth), (
            f"the Earth marker moved by world_offset={offset} — the year "
            "wheel is a CALENDAR position and north must stay the summer "
            "solstice in every world mode and at every solar rotation"
        )
        assert moon_marker_angle(ctx) == pytest.approx(base_moon), (
            f"the Moon marker moved by world_offset={offset} — the moon "
            "cycle is a CALENDAR position and north must stay the new moon"
        )


def test_the_earth_marker_still_reads_its_own_tick_angle(ctx_factory):
    """Not merely constant — constant AT THE RIGHT PLACE. A function that
    returned 0.0 would pass the test above and draw the Earth at north
    forever."""
    assert earth_marker_angle(ctx_factory(180.0)) == pytest.approx(137.5)
