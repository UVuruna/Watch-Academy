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


def test_encyclopedia_target_maps_body_and_ignores_untopiced(app):
    """The Spacebar jump's element→topic mapping (owner 2026-07-16,
    ROADMAP queue #8): the centered Sun body opens the active weekday
    theme's page at the Sun entry; a spot with no themed target opens
    nothing."""
    city = defaults.DEFAULT_CITY
    now = datetime(2026, 7, 7, 12, 0, tzinfo=ZoneInfo(city["timezone"]))
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    # The default hexa layout carries the Sun in the center.
    assert comp.encyclopedia_target(180.0, 180.0, 360.0) == (
        defaults.DEFAULT_SKIN.weekday_theme, 0,
    )
    # A transparent corner is over nothing themed.
    assert comp.encyclopedia_target(4.0, 4.0, 360.0) is None


def _dt(app, when):
    city = defaults.DEFAULT_CITY
    now = when.replace(tzinfo=ZoneInfo(city["timezone"]))
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _seat_px(skin, radius, seat_angle):
    """The widget pixel at a seated slot's centre — mirrors the
    compositor's `_element_at` seat geometry."""
    from render.layers import dial_point, slot_seat_orbit, slot_seat_rotation

    orbit = skin.weekday_set.orbit_fraction * slot_seat_orbit(skin, seat_angle)
    pos = dial_point(seat_angle + slot_seat_rotation(skin, 0.0), radius * orbit)
    return radius + pos.x(), radius + pos.y()


def _arm_px(radius, dial_angle, star_fraction):
    """A widget pixel well inside the star arm pointing at `dial_angle`
    (solar rotation off, so the drawn angle is the dial angle)."""
    from render.layers import dial_point

    pos = dial_point(dial_angle, radius * star_fraction * 0.82)
    return radius + pos.x(), radius + pos.y()


def test_spacebar_covers_calendar_pinned_body(app):
    """"sve znači SVE" (owner 2026-07-16): the Calendar pointer's pinned
    weekday seat opens its OWN theme's page at today's body — the owner's
    failing "Zeus on the Calendar pinned slot" (Thursday, Greek → Zeus =
    Jupiter, the 5th Week page)."""
    import dataclasses

    day, tick = _dt(app, datetime(2026, 7, 16, 12, 0))     # a Thursday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="calendar",
        weekday_theme="greek", solar_rotation=False,
    )
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    # The pinned seat sits at 24h (SOUTH_SLOT_ANGLE, the dial bottom).
    px, py = _seat_px(skin, 180.0, 180.0)
    assert comp.encyclopedia_target(px, py, 360.0) == ("greek", 4)


def test_spacebar_seated_slots_resolve_per_slot_theme(app):
    """Two seated weekday slots on the Prism, each in its OWN theme
    (owner failing case: Zeus and the Egyptian body on the 4h/20h arms) —
    the Spacebar jump opens each slot's own theme page at today's body,
    NOT the main theme's."""
    import dataclasses

    day, tick = _dt(app, datetime(2026, 7, 16, 12, 0))     # Thursday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="hexa", solar_rotation=False,
        weekday_theme="greek", weekday_slot="weekday",
        show_octa_slot=True, octa_slot="weekday", info_slot_theme="egypt",
    )
    from render.layers import slot_layout

    layout = slot_layout(skin)               # {1: 240°, 2: 120°}
    assert set(layout.values()) == {240.0, 120.0}
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    slot1 = next(a for i, a in layout.items() if i == 1)
    slot2 = next(a for i, a in layout.items() if i == 2)
    # Today is Thursday → Jupiter, the 5th Week page in both themes.
    assert comp.encyclopedia_target(
        *_seat_px(skin, 180.0, slot1), 360.0
    ) == ("greek", 4)
    assert comp.encyclopedia_target(
        *_seat_px(skin, 180.0, slot2), 360.0
    ) == ("egypt", 4)


def test_spacebar_cross_equinox_arm_opens_the_sun(app):
    """The Seasons (cross) cardinal arms open the Sun topic (owner
    2026-07-16, "equinox on Compass") — a left/right arm points at an
    equinox, the shared Equinox page (Sun entry 2)."""
    import dataclasses

    day, tick = _dt(app, datetime(2026, 7, 16, 12, 0))
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="cross", solar_rotation=False,
    )
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    star_fraction = skin.star.radius_fraction
    # 90° (right, 18h) and 270° (left, 06h) are the equinox arms.
    for dial_angle in (90.0, 270.0):
        px, py = _arm_px(180.0, dial_angle, star_fraction)
        assert comp.encyclopedia_target(px, py, 360.0) == ("sun", 2)
    # A solstice cardinal (top/bottom) opens a solstice page instead.
    top = comp.encyclopedia_target(
        *_arm_px(180.0, 0.0, star_fraction), 360.0
    )
    assert top is not None and top[0] == "sun" and top[1] in (0, 1)


def test_spacebar_octa_season_arm_opens_the_seasons(app):
    """The Compass (octa) DIAGONAL arms open the Seasons topic (owner
    2026-07-16, "summer on Compass"): the diagonal whose tooltip names
    Summer maps to the Summer season page (entry 1)."""
    import dataclasses

    from render.compositor import _ENC_SEASON_ORDER

    day, tick = _dt(app, datetime(2026, 7, 16, 12, 0))
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False,
    )
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    star_fraction = skin.star.radius_fraction
    summer_index = _ENC_SEASON_ORDER.index("Summer")
    matched = False
    for dial_angle in (45.0, 135.0, 225.0, 315.0):
        px, py = _arm_px(180.0, dial_angle, star_fraction)
        target = comp.encyclopedia_target(px, py, 360.0)
        assert target is not None and target[0] == "seasons"
        tooltip = comp.tooltip_at(px, py, 360.0)
        if tooltip and "Summer" in tooltip:
            assert target == ("seasons", summer_index)
            matched = True
    assert matched, "no octa diagonal named Summer in July"


def test_spacebar_moon_marker_opens_the_current_phase(app):
    """The Moon marker opens the Moon topic at the CURRENT phase's page
    (owner 2026-07-16): the phase name indexes constants.MOON_PHASE_NAMES,
    the eight-page order of the topic (queue #8b)."""
    from config import constants
    from core.moon import phase_name
    from render.layers import dial_point
    from core import angles

    day, tick = _dt(app, datetime(2026, 7, 16, 12, 0))
    skin = defaults.DEFAULT_SKIN
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    marker = skin.year_marker
    pos = dial_point(
        angles.moon_cycle_angle(tick.moon_fraction),
        180.0 * marker.moon_orbit_fraction,
    )
    target = comp.encyclopedia_target(180.0 + pos.x(), 180.0 + pos.y(), 360.0)
    expected = constants.MOON_PHASE_NAMES.index(phase_name(tick.moon_fraction))
    assert target == ("moon", expected)


def _repaint(comp, size=360.0):
    from PySide6.QtGui import QImage, QPainter

    image = QImage(round(size), round(size), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    comp.paint(painter, size, 1.0, comp._last_tick)
    painter.end()
    return image


def test_hover_and_reveal_never_rebuild_the_composite(app):
    """Owner 2026-07-17, ROADMAP 15f: the hover-enlarge and the Omega
    reveal draw the weekday bodies LIVE, so a hover enter/leave or a reveal
    toggle rebuilds NONE of the cached composite segments — the exact same
    cached pixmaps survive (object-identity check, independent of the perf
    store)."""
    import dataclasses

    day, tick = _dt(app, datetime(2026, 7, 16, 14, 30))
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)        # builds the segments
    cached = list(comp._composites)
    assert len(cached) == 2 and all(px is not None for px in cached)

    def unchanged():
        return len(comp._composites) == len(cached) and all(
            a is b for a, b in zip(comp._composites, cached)
        )

    # Hover onto the centered Sun body, then leave — no segment rebuild.
    assert comp.set_hover(180.0, 180.0, 360.0)
    _repaint(comp)
    assert unchanged()
    assert comp.set_hover(-1.0e9, -1.0e9, 360.0)
    _repaint(comp)
    assert unchanged()
    # The Omega reveal toggle on and off — also no rebuild.
    comp.trigger_reveal_week()
    _repaint(comp)
    assert unchanged()
    comp.trigger_reveal_week()
    _repaint(comp)
    assert unchanged()


def test_composite_segments_split_around_the_live_bodies(app):
    """The z-ordered stack splits into TWO cached segments around the live
    WeekdayLayer (owner 2026-07-17, ROADMAP 15f): the default z_order seats
    the weekday_set BELOW the ring, so pulling it out leaves the base
    (background, star) below the bodies and the ring above them — the
    weekday/archetype layers paint LIVE between the two blits."""
    from render.layers import ArchetypeLayer, RingLayer, WeekdayLayer

    day, tick = _dt(app, datetime(2026, 7, 16, 14, 30))
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    kinds = [step[0] for step in comp._steps]
    live = [type(p).__name__ for k, p in comp._steps if k == "live"]
    assert kinds.count("cache") == 2                     # base + ring
    assert "WeekdayLayer" in live                         # bodies paint live
    # The ring is cached ABOVE the live bodies (z-order preserved).
    cache_groups = comp._cached_groups
    assert any(isinstance(l, RingLayer) for group in cache_groups for l in group)
    assert not any(
        isinstance(l, (WeekdayLayer, ArchetypeLayer))
        for group in cache_groups
        for l in group
    )


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
            day=SimpleNamespace(southern_hemisphere=False),
            tick=SimpleNamespace(moon_fraction=fraction),
            radius=50.0, cache=AssetCache(), dpr=1.0,
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
    they meet on the shared rim; apart it is fully opaque. (With the
    Earth element switched off the layer skips the transit entirely.)"""
    from render.layers import moon_transit_opacity

    spec = defaults.DEFAULT_SKIN.year_marker
    assert moon_transit_opacity(spec, 100.0, 250.0) == 1.0        # far apart
    assert moon_transit_opacity(spec, 100.0, 103.0) == defaults.MOON_TRANSIT_OPACITY
    assert moon_transit_opacity(spec, 100.0, 460.0 + 3.0) == defaults.MOON_TRANSIT_OPACITY


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
        day=SimpleNamespace(southern_hemisphere=True),
        tick=SimpleNamespace(moon_fraction=0.25),
        radius=50.0, cache=AssetCache(), dpr=1.0,
    )
    layer._draw_moon(painter, ctx, QPointF(0, 0), 80.0)
    painter.end()
    left, right = image.pixelColor(35, 50), image.pixelColor(65, 50)
    assert left.red() > 150          # lit side on the LEFT
    assert right.red() <= 150


def test_sunday_sun_covers_the_hands(app):
    """On Sundays the opaque Sun in the center draws ABOVE the hands —
    at noon sharp all hands point straight up, so a pixel just above the
    center must show the warm Sun, not the gray hand shaft."""
    from datetime import datetime

    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    sunday_noon = datetime(2026, 7, 12, 12, 0, tzinfo=tz)   # a Sunday
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    day = build_day_context(
        sunday_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    image = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, build_tick_state(sunday_noon, day)
    )
    color = image.pixelColor(180, 165)   # inside the Sun disc, on the hand axis
    assert color.red() > 140 and color.red() > color.blue()   # Sun, not gray shaft


def test_noon_sector_is_yellowish(frame):
    # At 12:00 in July the top sector (yellow) is in full daylight; sample
    # inside the background at dial angle ~16 deg — inside the (rotated)
    # yellow wedge but OFF the 12h axis, where all three hands stack at
    # noon sharp.
    color = frame.pixelColor(210, 75)
    assert color.alpha() > 200
    assert color.red() > 150 and color.green() > 120
    assert color.blue() < color.red()  # yellow/orange family, not blue


def test_pointer_saturation_grays_the_star_and_aura_hues(app):
    """The Pointer Saturation slider (owner 2026-07-18, Settings ▸
    Colors, renamed from "palette_saturation" in Session 21-D now that
    RING has its own independent slider) scales BOTH the pointer (Star)
    and the background (Aura) wedges through the ONE shared source,
    `render.layers.palette_for` — 0.0 grays every hue to its own
    brightness (HSV saturation zeroed, value/hue untouched); the
    ring/letters (a separate art path, never touching palette_for) are
    untouched."""
    import dataclasses

    from PySide6.QtGui import QColor

    from render.layers import palette_for

    full = dataclasses.replace(defaults.DEFAULT_SKIN, pointer_saturation=1.0)
    gray = dataclasses.replace(defaults.DEFAULT_SKIN, pointer_saturation=0.0)
    full_hues = palette_for(full)
    gray_hues = palette_for(gray)
    assert full_hues == defaults.PALETTE_PRESETS[(full.pointer, full.palette_style)]
    assert len(gray_hues) == len(full_hues)
    for original, grayed in zip(full_hues, gray_hues):
        color = QColor(grayed)
        h, s, v, a = color.getHsvF()
        assert s == pytest.approx(0.0, abs=1e-6)      # fully desaturated
        # Value (brightness) is untouched — the color grays to ITS OWN
        # brightness, not to a flat mid-gray.
        orig_v = QColor(original).getHsvF()[2]
        assert v == pytest.approx(orig_v, abs=1e-6)


def test_ring_saturation_grays_the_tinted_ring_plate_not_the_pointer(app):
    """The Ring Saturation slider (owner 2026-07-18, Settings ▸ Colors,
    Session 21-D — its OWN slider, independent of Pointer): scales the
    ring plate's (and letter overlay's) saturation at
    `render.assets.AssetCache._saturated`, applied AFTER the ring_tint
    recolor — so a colorful ring_tint grays out at ring_saturation=0.0
    while the Star/Aura palette (a completely different asset/path)
    stays exactly as saturated as ever, and vice versa."""
    import dataclasses

    from PySide6.QtGui import QColor

    from render.assets import AssetCache
    from render.compositor import Compositor

    now = datetime(2025, 6, 20, 12, 0, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.82, longitude=20.46)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)

    # A saturated ring tint so a gray-out is visible against it.
    tinted = dataclasses.replace(
        defaults.DEFAULT_SKIN, ring_tint="#3050E0", ring_saturation=1.0,
    )
    grayed_ring = dataclasses.replace(tinted, ring_saturation=0.0)
    grayed_pointer = dataclasses.replace(
        tinted, pointer_saturation=0.0, ring_saturation=1.0,
    )

    def ring_pixel(skin):
        image = Compositor(skin, AssetCache()).render_offscreen(
            480.0, 1.0, day, tick
        )
        # Inside the donut band, on the horizontal axis (18h side) —
        # away from any hand/star overlay; probed to land on a
        # colorful (not white/black-edge) pixel of the tinted plate.
        return image.pixelColor(470, 240)

    full_px = ring_pixel(tinted)
    grayed_px = ring_pixel(grayed_ring)
    pointer_grayed_px = ring_pixel(grayed_pointer)

    full_s = QColor(full_px).getHsvF()[1]
    grayed_s = QColor(grayed_px).getHsvF()[1]
    pointer_grayed_s = QColor(pointer_grayed_px).getHsvF()[1]

    # ring_saturation=0.0 measurably desaturates the ring pixel...
    assert grayed_s < full_s - 0.05
    # ...but pointer_saturation=0.0 (the OTHER slider) leaves it alone.
    assert pointer_grayed_s == pytest.approx(full_s, abs=1e-3)
