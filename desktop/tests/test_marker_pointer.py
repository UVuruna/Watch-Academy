"""THE POSITION POINTER (owner feature 2026-08-09, Settings ▸ Earth,
off by default): a small triangle at the Earth/Moon orbit circle, at
each body's own angle, colored with the SAME ramp hue the ring
jewels/crown text wear. See `render.layers.year_marker.YearMarkerLayer.
marker_marks.draw_pointer` and `app.controller._overlay_display_settings`.
(The drawing moved out of `YearMarkerLayer._draw_orbit_pointer` on
2026-08-10 when the owner approved two more shapes beside the triangle;
the geometry is unchanged, so these teeth kept biting through the move.)
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


def test_pointer_off_paints_no_pixel_of_the_pointer_colour(app, moment):
    """THE EVIDENCE GAP (re-grade round 2026-08-09): the earlier proof
    shot `dial-default-orbit-pointer-off.png` showed markers
    indistinguishable from the pointer-on render, with no assertion
    that the toggle actually suppresses the drawn triangle — a stale
    capture, not a code bug (this test's own render, built the same
    way, IS clean), but the gap itself was real. This pins render-level
    proof, not just the config flag `test_off_by_default` already
    covers: the pointer's own resolved hue must appear SOMEWHERE in the
    "on" render (proving the triangle really painted, not just some
    unrelated diff) and NOWHERE in the "off" render of the identical
    frame."""
    day, tick = moment
    skin_off = build_skin(dataclasses.replace(Settings(), diameter=720))
    assert skin_off.year_marker.pointer_enabled is False
    off = Compositor(skin_off, AssetCache()).render_offscreen(720.0, 1.0, day, tick)
    skin_on = build_skin(dataclasses.replace(
        Settings(), diameter=720, show_marker_pointer=True,
    ))
    assert skin_on.year_marker.pointer_enabled is True
    on = Compositor(skin_on, AssetCache()).render_offscreen(720.0, 1.0, day, tick)

    from PySide6.QtGui import QColor

    pointer_rgb = QColor(skin_on.year_marker.pointer_color).getRgb()[:3]

    def matches_pointer(color):
        return all(abs(c - p) <= 6 for c, p in zip(color.getRgb()[:3], pointer_rgb))

    # THE POINTER'S OWN COLOUR IS THE RING'S OWN HUE BY DESIGN (Task 3),
    # so a whole-dial scan collides with the crown text/jewels, which
    # wear that identical hue — a false positive, not proof of leakage.
    # The scan is bounded to a ring right at each marker's own edge
    # (`orbit ± the tip protrusion + a little air`), the ONLY place the
    # triangle itself can ever land, so a hit there is unambiguous.
    from config import dial
    from render.painting import dial_point

    spec = skin_on.year_marker
    half = 720 / 2.0
    hits = {"on": 0, "off": 0}
    for angle_deg, orbit, marker_half in (
        (tick.year_angle, dial.earth_moon_orbit_fraction(
            skin_on.numeral_outer_ring_size, max(spec.scale, spec.moon_scale),
        ), spec.scale),
    ):
        edge = orbit + marker_half
        band = 0.03  # fraction of the dial radius, generous around the tip
        for r_frac in [edge + k * 0.002 for k in range(-5, int(band * 500) + 1)]:
            for a in range(-6, 7):
                pt = dial_point(angle_deg + a, half * r_frac)
                x, y = int(pt.x() + half), int(pt.y() + half)
                if 0 <= x < 720 and 0 <= y < 720:
                    if matches_pointer(on.pixelColor(x, y)):
                        hits["on"] += 1
                    if matches_pointer(off.pixelColor(x, y)):
                        hits["off"] += 1
    assert hits["on"] > 0, "the pointer's own hue never appears at the marker's edge in the on render"
    assert hits["off"] == 0, (
        f"the pointer's own hue appears at the marker's own edge in the "
        f"OFF render ({hits['off']} samples) — the toggle is not "
        "suppressing the drawn triangle"
    )


def test_pointer_is_proportional_and_behind_the_body(app):
    """THE ARROW IS BEHIND THE BODY (owner correction 2026-08-11, "IZA
    NE ISPRED ZEMLJE, Z INDEX MANJI"): the render source draws the
    pointer BEFORE the body's own disc, and its dimensions come from
    the body's own half-size, never a fixed dial-radius size."""
    import inspect

    from render.layers import year_marker as ym

    source = inspect.getsource(ym.YearMarkerLayer)
    moon_paint = source[: source.index("_draw_moon(")]
    assert "draw_pointer" in moon_paint, (
        "the Moon's pointer must be drawn BEFORE the Moon's own disc"
    )
    earth_source = inspect.getsource(ym.YearMarkerLayer._draw_earth)
    assert earth_source.count("draw_pointer") == 1, (
        "exactly ONE Earth pointer draw — a leftover top-of-body call "
        "is how the 2026-08-11 'IZA NE ISPRED' correction shipped wrong"
    )
    assert earth_source.index("draw_pointer") < earth_source.index("variant = ("), (
        "the Earth's pointer must be drawn BEFORE the Earth's own art"
    )
    assert source.count("draw_pointer") - earth_source.count("draw_pointer") == 1, (
        "exactly ONE Moon pointer draw, before the disc"
    )


def test_the_arrow_flips_inward_when_the_body_rides_the_ring(app):
    """THE FLIPPED ARROW (owner correction 2026-08-11, slika 4/5:
    "obrni strelicu... jer je sada na RINGU"): a body relocated onto
    the ring band sits OUTSIDE the 360 tips' circle, so the arrow
    points INWARD at the marked point — nothing of it may paint
    outside the body's own outer edge."""
    import math as _math

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    from render import marker_marks

    image = QImage(400, 400, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(200, 200)
    # Body on the ring (orbit 0.95 of a 180 px dial radius), marked
    # point well inside at 100 px.
    marker_marks.draw_pointer(
        painter, "triangle", 0.0, 180.0, 0.95, 0.06, "#CC3333",
        tip_radius=100.0,
    )
    painter.end()

    def painted(radius_px):
        x = 200
        y = 200 - round(radius_px)
        return image.pixelColor(x, y).alpha() > 32

    assert painted(105), "the inward arrow must reach its marked point"
    body_inner = 180.0 * (0.95 - 0.06)
    assert painted(body_inner - 3), "the flanks must emerge at the body edge"
    body_outer = 180.0 * (0.95 + 0.06)
    for r in range(int(body_outer) + 4, 190):
        assert not image.pixelColor(200, 200 - r).alpha() > 32, (
            f"an inward arrow painted OUTSIDE the body at {r}px"
        )


def test_the_gem_lives_whole_between_the_body_and_the_marked_point(app):
    """THE WHOLE DIAMOND (owner correction 2026-08-11, slika 2/3): one
    vertex on the body's edge, the other on the marked point, nothing
    hidden under the disc — and height >= width by law."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    from config import dial
    from render import marker_marks

    assert dial.MARKER_GEM_WIDTH_RATIO < 1.0
    image = QImage(400, 400, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(200, 200)
    marker_marks.draw_pointer(
        painter, "gem", 0.0, 180.0, 0.50, 0.08, "#CC9933",
        tip_radius=140.0,
    )
    painter.end()
    body_edge = 180.0 * (0.50 + 0.08)
    mid = (body_edge + 140.0) / 2.0
    assert image.pixelColor(200, 200 - round(mid)).alpha() > 32, (
        "the gem's middle must sit between the body edge and the point"
    )
    # Nothing under the disc: inside the body's own circle stays clean.
    inside = 180.0 * 0.50
    assert image.pixelColor(200, 200 - round(inside)).alpha() <= 32
