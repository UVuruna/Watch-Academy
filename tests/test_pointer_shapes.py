"""THE POINTERS REWORK — phase 1 (owner sheet UV/Pointers.png, sealed
2026-07-29).

Every sealed behavior pinned golden: the two SHAPES and their geometry
(the plain polygon really being the plain polygon, the CUBE standing in
for the Trinity's triangle, the Calendar's two hexagrams, the Rose's
twenty-four rays), the CURVATURE slider with its two edge forms, the
OFFSET WHEELS (Seasons boundaries on the cardinal hours, Prophecy rays
on the half hours), the AURA wedges that follow the star's ray groups,
the night-border option, and the settings round-trip of the four new
keys.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from app.controller import WatchController, build_skin
from app.settings_store import (
    Settings,
    SettingsCorruptError,
    SettingsStore,
    replace,
)
from config import constants
from config import defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    RenderContext,
    StarLayer,
    arm_half_deg,
    arm_offset_deg,
    arm_shape_path,
    aura_group_offset_deg,
    aura_wedge_bounds,
    border_clips,
    dial_point,
    drawn_arm_count,
    drawn_arms,
    lit_regions,
    palette_for,
    polygon_boundary_radius,
    polygon_curvature,
    polygon_faces,
    rose_assembly_offset_deg,
    star_inner_radius,
    wheel_offset_deg,
    wheel_rotation,
)

TIP = 100.0                      # a round star tip for the geometry math
HOUR_DEG = 360.0 / 24.0          # the dial's own scale: 15° = one hour
# QPainterPath.contains() answers on Qt's own float32 geometry, so a
# measured silhouette radius is exact to about 1e-3 of the tip. Every
# geometric claim below is asserted well inside that.
EDGE_TOL = 0.01


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _skin(pointer="hexa", **overrides):
    return build_skin(
        dataclasses.replace(Settings(), pointer=pointer, **overrides)
    )


def _arm_angles(skin) -> list[list[float]]:
    """The drawn passes as plain angle lists, normalized to 0..360."""
    return [
        [angle % 360.0 for angle, _hue in arms]
        for arms in drawn_arms(skin, palette_for(skin))
    ]


def _silhouette_radius(skin, angle: float) -> float:
    """How far the DRAWN figure reaches along a dial angle — bisection
    over the union of the arm paths, the honest measure of the outline
    (the polygon's own edge, curved or not)."""
    paths = [
        arm_shape_path(skin, TIP, theta)
        for arms in drawn_arms(skin, palette_for(skin))
        for theta, _hue in arms
    ]
    low, high = 0.0, TIP * 1.5
    for _ in range(60):
        middle = (low + high) / 2.0
        if any(path.contains(dial_point(angle, middle)) for path in paths):
            low = middle
        else:
            high = middle
    return low


def _edge_midpoint_deg(skin) -> float:
    """Where the polygon's OUTER edge is halfway between its corners —
    the angle the curvature bites deepest at. On the N-gons that is the
    color boundary itself (`arm_half_deg` off the arm); on the TRINITY's
    cube the boundary is a hexagon vertex, so the edge midpoint sits
    half as far off the arm."""
    half = arm_half_deg(skin)
    return half / 2.0 if skin.pointer == "trio" else half


def _dt(when: datetime):
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


# --- The shape choice itself --------------------------------------------------------


def test_the_shape_is_a_global_two_way_choice_defaulting_to_the_star():
    assert constants.POINTER_SHAPES == ("star", "polygon")
    assert constants.POINTER_SHAPE_DEFAULT == "star"
    assert Settings().pointer_shape == "star"


def test_only_the_four_true_polygons_take_a_polygon_face(app):
    """The Calendar's twelve-point and the Rose's twenty-four-point
    "polygons" are STARS with touching arms — they keep the star
    construction (owner sheet), and with it no curvature."""
    assert constants.POLYGON_POINTERS == ("trio", "cross", "hexa", "octa")
    for pointer in constants.POINTER_POINTS:
        skin = _skin(pointer, pointer_shape="polygon")
        assert polygon_faces(skin) is (pointer in constants.POLYGON_POINTERS)
        # The star shape never draws a polygon face on anything.
        assert polygon_faces(_skin(pointer)) is False


def test_the_armless_aurora_ignores_the_shape(app):
    """Aurora draws no pointer at all, so the choice is inert there —
    and the stored value survives untouched, never rewritten."""
    skin = _skin("aurora", pointer_shape="polygon")
    assert skin.pointer_shape == "polygon"
    assert polygon_faces(skin) is False


# --- One vertex per arm tip ---------------------------------------------------------


@pytest.mark.parametrize(
    "pointer,expected",
    [
        ("trio", [0.0, 120.0, 240.0]),
        ("cross", [0.0, 90.0, 180.0, 270.0]),
        ("hexa", [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]),
        ("octa", [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]),
    ],
)
def test_the_polygon_keeps_a_vertex_on_every_arm_tip(app, pointer, expected):
    """Owner spec: one VERTEX at each arm-tip direction of that
    pointer's star — the polygon is the star's own arms, fattened."""
    polygon = _skin(pointer, pointer_shape="polygon")
    assert _arm_angles(polygon) == [expected]
    assert _arm_angles(_skin(pointer)) == [expected]     # same arms as the star
    for angle in expected:
        assert _silhouette_radius(polygon, angle) == pytest.approx(
            TIP, abs=EDGE_TOL
        )


@pytest.mark.parametrize(
    "pointer,sides", [("cross", 4), ("hexa", 6), ("octa", 8)]
)
def test_the_plain_polygon_is_literally_the_plain_polygon(app, pointer, sides):
    """Curvature 0: vertices on the tip circle, edge midpoints on the
    apothem, and every point BETWEEN them exactly on the straight chord
    (`apothem / cos(angle off the midpoint)`) — a square, a hexagon and
    an octagon, nothing cleverer."""
    skin = _skin(pointer, pointer_shape="polygon")
    half = 180.0 / sides
    assert arm_half_deg(skin) == pytest.approx(half)
    apothem = TIP * math.cos(math.radians(half))
    for step in (0.0, 0.25, 0.5, 0.75, 1.0):
        # Sweep from an arm tip to the middle of the edge beside it.
        off = step * half
        assert _silhouette_radius(skin, off) == pytest.approx(
            apothem / math.cos(math.radians(half - off)), abs=EDGE_TOL
        )


def test_the_trinity_polygon_is_the_cube_not_a_triangle(app):
    """Owner exception: the Trinity draws the CUBE — the hexagon of
    three rhombi the Cube look already builds — with a rhombus tip on
    each of the trio's three arms. Same construction, reused (Rule #5):
    the polygon's arm path is IDENTICAL to the Cube look's own."""
    polygon = _skin("trio", pointer_shape="polygon")
    cube = _skin("trio", cube_look=True)
    assert arm_half_deg(polygon) == arm_half_deg(cube) == 60.0
    assert polygon_curvature(polygon) == 0.0
    # The very same figure: the drawn silhouette matches the Cube
    # look's own all the way round (the polygon path merely names the
    # colour boundaries as corners, which the Cube look leaves implicit).
    for angle in range(0, 360, 5):
        assert _silhouette_radius(polygon, float(angle)) == pytest.approx(
            _silhouette_radius(cube, float(angle)), abs=EDGE_TOL
        )
    # Six hexagon vertices at the tip: the three arms and the three
    # colour boundaries between them.
    for angle in range(0, 360, 60):
        assert _silhouette_radius(polygon, float(angle)) == pytest.approx(
            TIP, abs=EDGE_TOL
        )
    assert polygon_boundary_radius(polygon, TIP) == pytest.approx(TIP)


def test_the_star_shape_is_untouched_by_the_rework(app):
    """REGRESSION PIN: with the default settings every drawn arm is the
    diamond it always was — center, two side vertices at
    `tip / 2cos(half)`, the tip. (The Rose's three stars overlap, so
    only its half-angle and inner radius are pinned here; its own
    geometry lives in tests/test_rose_pointer.py.)"""
    for pointer in ("trio", "cross", "hexa", "octa", "rose"):
        skin = _skin(pointer)
        half = constants.POINTER_ARM_HALF_ANGLE_DEG[pointer]
        assert arm_half_deg(skin) == half
        inner = TIP / (2.0 * math.cos(math.radians(half)))
        assert star_inner_radius(skin, TIP) == pytest.approx(inner)
        assert _silhouette_radius(skin, 0.0) == pytest.approx(
            TIP, abs=EDGE_TOL
        )
        # The four corners themselves, in the path's own order.
        path = arm_shape_path(skin, TIP, 0.0)
        assert path.elementCount() == 5          # centre, 3 corners, close
        corners = [
            dial_point(-half, inner), dial_point(0.0, TIP),
            dial_point(half, inner),
        ]
        for index, corner in enumerate(corners, start=1):
            assert path.elementAt(index).x == pytest.approx(corner.x())
            assert path.elementAt(index).y == pytest.approx(corner.y())


# --- The curvature slider -----------------------------------------------------------


def test_the_curvature_range_and_the_two_edge_forms():
    assert constants.POLYGON_CURVATURE_RANGE == (0.0, 1.0)
    assert constants.POLYGON_CURVATURE_DEFAULT == 0.0
    assert constants.POLYGON_EDGE_MODES == ("smooth", "notched")
    assert constants.POLYGON_EDGE_DEFAULT == "smooth"
    assert Settings().polygon_curvature == 0.0
    assert Settings().polygon_edge == "smooth"


@pytest.mark.parametrize("pointer", ["trio", "cross", "hexa", "octa"])
@pytest.mark.parametrize("edge", ["smooth", "notched"])
def test_curvature_pulls_the_edge_inward_monotonically(app, pointer, edge):
    """0 leaves the plain polygon; every step inward is strictly
    smaller; 1.0 lands the edge midpoint exactly where the pointer's own
    star seats its inner vertex."""
    def midpoint_radius(curvature):
        skin = _skin(
            pointer, pointer_shape="polygon",
            polygon_curvature=curvature, polygon_edge=edge,
        )
        return _silhouette_radius(skin, _edge_midpoint_deg(skin))

    straight = _skin(pointer, pointer_shape="polygon")
    apothem = TIP * math.cos(math.radians(_edge_midpoint_deg(straight)))
    radii = [midpoint_radius(c) for c in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert radii[0] == pytest.approx(apothem, abs=EDGE_TOL)
    assert all(a > b for a, b in zip(radii, radii[1:]))
    assert radii[-1] == pytest.approx(
        star_inner_radius(straight, TIP), abs=EDGE_TOL
    )


@pytest.mark.parametrize("pointer", ["trio", "cross", "hexa", "octa"])
def test_the_two_edge_forms_agree_only_at_zero_curvature(app, pointer):
    """Both forms pass through the SAME pulled midpoint, so they can
    only differ between it and the vertices: at curvature 0 that
    difference is nothing (both draw the straight edge), above it the
    concave arc bites deeper than the V-notch's straight segments."""
    def quarter_radius(curvature, edge):
        skin = _skin(
            pointer, pointer_shape="polygon",
            polygon_curvature=curvature, polygon_edge=edge,
        )
        return _silhouette_radius(skin, _edge_midpoint_deg(skin) / 2.0)

    assert quarter_radius(0.0, "smooth") == pytest.approx(
        quarter_radius(0.0, "notched"), abs=EDGE_TOL
    )
    assert quarter_radius(1.0, "smooth") < quarter_radius(1.0, "notched")


def test_no_curvature_on_the_calendar_and_the_rose(app):
    """Owner spec: their polygons are stars, and a star never curves —
    the stored slider value is IGNORED there, never rewritten."""
    for pointer in ("calendar", "rose"):
        skin = _skin(pointer, pointer_shape="polygon", polygon_curvature=1.0)
        assert skin.polygon_curvature == 1.0
        assert polygon_curvature(skin) == 0.0
        # The rays still reach the tip: a star, untouched by the slider.
        for arms in drawn_arms(skin, palette_for(skin)):
            for theta, _hue in arms:
                assert _silhouette_radius(skin, theta) == pytest.approx(
                    TIP, abs=EDGE_TOL
                )


# --- The offset wheels --------------------------------------------------------------


def test_the_seasons_wheel_puts_its_boundaries_on_the_cardinal_hours(app):
    """Owner spec 2026-07-29: the cross's TERTIARY wheel — the Seasons —
    turns 45°, so a season BEGINS at 12h/3h/6h/9h (astronomical). Its
    other two wheels stay centered on the cardinals (meteorological)."""
    assert constants.SEASONS_ARM_OFFSET_DEG == 45.0
    seasons = _skin("cross", palette_style="tertiary")
    assert arm_offset_deg(seasons) == 45.0
    assert _arm_angles(seasons) == [[45.0, 135.0, 225.0, 315.0]]
    for wheel in ("primary", "secondary"):
        assert arm_offset_deg(_skin("cross", palette_style=wheel)) == 0.0
        assert _arm_angles(_skin("cross", palette_style=wheel)) == [
            [0.0, 90.0, 180.0, 270.0]
        ]
    # The BOUNDARIES — halfway between adjacent arms — land on 12h and
    # its cardinal partners, in BOTH shapes (the polygon's vertices
    # follow the arms).
    for shape in ("star", "polygon"):
        arms = _arm_angles(
            _skin("cross", palette_style="tertiary", pointer_shape=shape)
        )[0]
        boundaries = sorted(
            (arms[i] + 45.0) % 360.0 for i in range(len(arms))
        )
        assert boundaries == [0.0, 90.0, 180.0, 270.0]


def test_prophecy_stands_on_the_half_hours_while_legacy_keeps_the_hours(app):
    """Owner spec 2026-07-29: the Rose's SECONDARY wheel shifts its
    WHOLE assembly half a ray (+7.5°), so every ray CENTER lands on
    HH:30 and each hue covers its hours from :00 to :59. Legacy's rays
    stay on the full hours."""
    assert constants.ROSE_WHEEL_ASSEMBLY_OFFSET_DEG["primary"] == 0.0
    assert constants.ROSE_WHEEL_ASSEMBLY_OFFSET_DEG["secondary"] == 7.5
    legacy = _skin("rose", palette_style="primary")
    prophecy = _skin("rose", palette_style="secondary")
    assert rose_assembly_offset_deg(legacy) == 0.0
    assert rose_assembly_offset_deg(prophecy) == 7.5

    def rays(skin):
        return sorted(
            angle for arms in _arm_angles(skin) for angle in arms
        )

    for skin in (legacy, prophecy):
        assert len(rays(skin)) == 24       # three stars, eight arms each
    assert rays(legacy) == [k * HOUR_DEG for k in range(24)]
    assert rays(prophecy) == [(k + 0.5) * HOUR_DEG for k in range(24)]
    # The twenty-four-ray POLYGON carries the same shift.
    assert rays(
        _skin("rose", palette_style="secondary", pointer_shape="polygon")
    ) == [(k + 0.5) * HOUR_DEG for k in range(24)]


def test_the_prophecy_shift_moves_no_hue_off_its_own_ray(app):
    """Owner spec: "do NOT re-anchor which hue sits where — only the
    +7.5° shift"."""
    palette = defaults.ROSE_PALETTE
    unshifted = {
        (angle - 7.5) % 360.0: hue
        for arms in drawn_arms(
            _skin("rose", palette_style="secondary"), palette
        )
        for angle, hue in arms
    }
    plain = {
        angle % 360.0: hue
        for offset in constants.ROSE_STAR_OFFSETS["secondary"]
        for angle, hue in (
            (offset + index * 45.0, hue) for index, hue in enumerate(palette)
        )
    }
    assert unshifted == plain


# --- The Aura wedges follow the star ------------------------------------------------


def test_the_aura_wedge_of_a_one_star_pointer_is_unchanged(app):
    """Every pointer but the Rose wears one hue per arm, so the wedge
    still centers on the arm itself."""
    for pointer in ("trio", "cross", "hexa", "octa"):
        skin = _skin(pointer)
        assert aura_group_offset_deg(skin) == 0.0
        palette = palette_for(skin)
        span = 360.0 / len(palette)
        assert aura_wedge_bounds(skin, palette) == [
            (index * span - span / 2.0, index * span + span / 2.0)
            for index in range(len(palette))
        ]


def test_the_genesis_and_seasons_wedges_ride_their_own_arms(app):
    """The Aura reads the SAME `wheel_offset_deg` the arms do, so an
    offset wheel can never leave its background behind."""
    for pointer, offset in (("trio", 180.0), ("cross", 45.0)):
        skin = _skin(pointer, palette_style="tertiary")
        palette = palette_for(skin)
        span = 360.0 / len(palette)
        assert wheel_offset_deg(skin) == offset
        assert aura_wedge_bounds(skin, palette)[0] == pytest.approx(
            (offset - span / 2.0, offset + span / 2.0)
        )


def test_the_aura_wedges_cover_the_rose_ray_groups(app):
    """THE OWNER'S TOP-PRIORITY FIX (2026-07-29): the Rose wears each
    hue on THREE rays, and the background wedge must span exactly that
    group. Golden angles for both wheels — Legacy's boundaries on the
    HH:30 marks, Prophecy's on the full hours."""
    legacy = _skin("rose", palette_style="primary")
    prophecy = _skin("rose", palette_style="secondary")
    assert aura_group_offset_deg(legacy) == -15.0
    assert aura_group_offset_deg(prophecy) == 0.0

    legacy_wedges = aura_wedge_bounds(legacy, palette_for(legacy))
    prophecy_wedges = aura_wedge_bounds(prophecy, palette_for(prophecy))
    assert legacy_wedges[0] == pytest.approx((-37.5, 7.5))
    assert prophecy_wedges[0] == pytest.approx((-15.0, 30.0))
    assert [start for start, _end in legacy_wedges] == pytest.approx(
        [-37.5 + index * 45.0 for index in range(8)]
    )
    assert [start for start, _end in prophecy_wedges] == pytest.approx(
        [-15.0 + index * 45.0 for index in range(8)]
    )
    # Legacy cuts on the half hours, Prophecy on the whole ones.
    for start, _end in legacy_wedges:
        assert (start / HOUR_DEG) % 1.0 == pytest.approx(0.5)
    for start, _end in prophecy_wedges:
        assert (start / HOUR_DEG) % 1.0 == pytest.approx(0.0)


@pytest.mark.parametrize("wheel", ["primary", "secondary"])
def test_every_rose_wedge_stands_behind_its_own_hue_group(app, wheel):
    """The law itself: each ray wearing hue k must fall inside the
    wedge drawn in hue k — on BOTH wheels and in BOTH shapes."""
    for shape in ("star", "polygon"):
        skin = _skin("rose", palette_style=wheel, pointer_shape=shape)
        palette = palette_for(skin)
        wedges = aura_wedge_bounds(skin, palette)
        for arms in drawn_arms(skin, palette):
            for angle, hue in arms:
                start, end = wedges[palette.index(hue)]
                assert start < angle < end, f"{hue} ray {angle} outside {wedges}"


# --- The Calendar's two figures -----------------------------------------------------


def test_the_calendar_star_is_two_hexagrams_the_even_one_on_top(app):
    """Owner sheet: STAR = two 6-arm stars 30° apart, z-stacked, wearing
    the twelve wedge hues between them — the star on the EVEN wedge
    centers painted last (the Rose's z-stack pattern)."""
    skin = _skin("calendar")
    assert constants.CALENDAR_STAR_ARMS == 6
    assert drawn_arm_count(skin) == 6
    assert arm_half_deg(skin) == 30.0
    passes = _arm_angles(skin)
    assert len(passes) == 2
    assert passes[0] == [45.0, 105.0, 165.0, 225.0, 285.0, 345.0]   # odd
    assert passes[1] == [15.0, 75.0, 135.0, 195.0, 255.0, 315.0]    # even, top
    # Together they wear all twelve hues, one per wedge, on the wedge
    # centers of the ACTIVE wheel.
    palette = palette_for(skin)
    drawn = {
        angle % 360.0: hue
        for arms in drawn_arms(skin, palette) for angle, hue in arms
    }
    assert len(drawn) == 12
    assert set(drawn.values()) == set(palette)


def test_the_calendar_polygon_is_one_twelve_point_star(app):
    """Owner sheet: POLYGON = one 12-arm star, adjacent arms touching
    (half 15°), one hue per 2h wedge, tips on the wedge centers."""
    skin = _skin("calendar", pointer_shape="polygon")
    assert drawn_arm_count(skin) == 12
    assert arm_half_deg(skin) == 15.0
    passes = _arm_angles(skin)
    assert len(passes) == 1
    assert passes[0] == [15.0 + index * 30.0 for index in range(12)]


def test_the_calendar_figure_rides_its_active_wheel(app):
    """Zodiac wedges START on the cardinal axes, Almanac wedges are
    CENTERED on them — the drawn tips follow, so a hue always stands on
    the wedge it colors."""
    zodiac = _skin("calendar", palette_style="primary", pointer_shape="polygon")
    almanac = _skin(
        "calendar", palette_style="secondary", pointer_shape="polygon"
    )
    assert _arm_angles(zodiac)[0][0] == 15.0
    assert _arm_angles(almanac)[0][0] == 0.0


def test_the_calendar_figure_is_calendar_fixed(app):
    """Like the wedges it stands on, it never takes the solar
    rotation — every other pointer does."""
    assert wheel_rotation(_skin("calendar"), 12.5) == 0.0
    for pointer in ("trio", "cross", "hexa", "octa", "rose"):
        assert wheel_rotation(_skin(pointer), 12.5) == 12.5


def test_the_calendar_draws_nothing_with_the_pointer_switched_off(app):
    """Owner sheet, "Old - empty": the empty calendar is the POINTER
    element switched off — not a third shape."""
    skin = _skin("calendar", show_pointer=False)
    layers = Compositor(skin, AssetCache())._layers
    assert not any(type(layer).__name__ == "StarLayer" for layer in layers)


def test_the_arm_hover_follows_the_drawn_shape(app):
    """Rule #5: `Compositor._arm_angle_at` hit-tests the very path the
    layer paints (`arm_shape_path`), so a point inside the drawn HEXAGON
    but outside the star diamond it replaced still answers with its
    arm."""
    radius = 200.0
    for pointer in ("hexa", "octa"):
        star = _skin(pointer, solar_rotation=False)
        polygon = _skin(pointer, pointer_shape="polygon", solar_rotation=False)
        tip = radius * star.star.radius_fraction
        # Halfway between the two silhouettes, off the shared boundary
        # ray: inside the fattened polygon face, outside the diamond.
        angle = arm_half_deg(polygon) * 0.8
        star_reach = _silhouette_radius(star, angle) * tip / TIP
        polygon_reach = _silhouette_radius(polygon, angle) * tip / TIP
        assert polygon_reach > star_reach
        point = dial_point(angle, (star_reach + polygon_reach) / 2.0)
        assert Compositor(polygon, AssetCache())._arm_angle_at(
            point, radius, 0.0
        ) is not None
        assert Compositor(star, AssetCache())._arm_angle_at(
            point, radius, 0.0
        ) is None


# --- Hide night borders -------------------------------------------------------------


def test_border_clips_default_to_the_whole_circle(app):
    """The setting off: today's law — borders run the full circle so the
    night arms stay recognizable."""
    day, _tick = _dt(datetime(2026, 7, 16, 12, 0))
    for pointer in constants.POINTER_POINTS:
        assert border_clips(_skin(pointer), day.sun) == (None,)


def test_hide_night_borders_strokes_only_the_sunlit_arcs(app):
    """The setting on: the outline strokes are clipped to exactly the
    `lit_regions` arcs — the night keeps its fills and loses the border
    mesh."""
    day, _tick = _dt(datetime(2026, 7, 16, 12, 0))
    skin = _skin("rose", hide_night_borders=True)
    expected = [
        (start, end) for start, end, _alpha in lit_regions(day.sun, skin.star)
    ]
    assert list(border_clips(skin, day.sun)) == expected
    assert expected                                   # Belgrade in July


def test_hide_night_borders_is_inert_while_the_daylight_law_is_off(app):
    """With the Calendar's/Rose's daylight switch off the wheel stands
    in flat full colour — everything counts as lit, so the borders run
    the whole circle again."""
    day, _tick = _dt(datetime(2026, 7, 16, 12, 0))
    for pointer in constants.DAYLIGHT_SWITCH_POINTERS:
        skin = _skin(pointer, hide_night_borders=True, daylight=False)
        assert border_clips(skin, day.sun) == (None,)


@pytest.mark.parametrize("pointer", ["rose", "hexa"])
def test_hide_night_borders_leaves_the_night_bare(app, pointer):
    """THE PIXEL PIN (Rule #25). The wheel is painted ALONE, so nothing
    else can stand in for it: with the option on, the night keeps no
    star ink at all, while the sunlit half is byte-for-byte the drawing
    it always was.

    REGRESSION: the first implementation of this option looked complete
    and changed NOTHING on the glass — the per-arm border clip called
    `setClipPath` without `IntersectClip`, which REPLACES the painter's
    clip, so each arm threw the pass's sunlit-arc clip away and stroked
    the whole circle anyway. Only a pixel count over the night sector
    catches that; `border_clips` returning the right arcs does not."""
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    lit = [
        (start % 360.0, end % 360.0)
        for start, end, _alpha in lit_regions(day.sun, _skin(pointer).star)
    ]

    def is_lit(theta):
        return any(
            (start <= theta <= end) if start <= end
            else (theta >= start or theta <= end)
            for start, end in lit
        )

    def ink(hide, want_lit):
        """Painted pixels of the star alone, in the deep night or the
        deep day (5° clear of every boundary, so the anti-aliased seams
        of the clip itself never count)."""
        skin = _skin(
            pointer, solar_rotation=False, hide_night_borders=hide
        )
        size = 400
        image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(size / 2.0, size / 2.0)
        StarLayer(skin).paint(
            painter,
            RenderContext(
                skin=skin, day=day, tick=tick, radius=size / 2.0,
                cache=AssetCache(), dpr=1.0, rotation=0.0,
            ),
        )
        painter.end()
        center = size / 2.0
        found = 0
        for x in range(size):
            for y in range(size):
                if image.pixelColor(x, y).alpha() < 20:
                    continue
                theta = math.degrees(
                    math.atan2(x - center, -(y - center))
                ) % 360.0
                if any(
                    is_lit((theta + margin) % 360.0) != want_lit
                    for margin in (-5.0, 0.0, 5.0)
                ):
                    continue
                found += 1
        return found

    night_before = ink(False, want_lit=False)
    assert night_before > 500                # the border mesh IS there
    assert ink(True, want_lit=False) < night_before / 50
    assert ink(True, want_lit=True) == ink(False, want_lit=True)


# --- Settings persistence -----------------------------------------------------------


@pytest.fixture
def store(tmp_path):
    return SettingsStore(tmp_path / "settings.json")


def test_the_four_new_keys_round_trip(store):
    saved = replace(
        Settings(),
        pointer_shape="polygon",
        polygon_curvature=0.65,
        polygon_edge="notched",
        hide_night_borders=True,
    )
    store.save(saved)
    loaded = store.load()
    assert loaded.pointer_shape == "polygon"
    assert loaded.polygon_curvature == pytest.approx(0.65)
    assert loaded.polygon_edge == "notched"
    assert loaded.hide_night_borders is True


def test_a_file_written_before_the_rework_gets_the_defaults(store):
    """Additive keys: a settings file from yesterday simply reads as the
    star shape, no curvature, today's borders — never a corrupt file."""
    store.save(Settings())
    raw = json.loads(store.path.read_text(encoding="utf-8"))
    for key in (
        "pointer_shape", "polygon_curvature", "polygon_edge",
        "hide_night_borders",
    ):
        assert key in raw                      # the writer emits all four
        del raw[key]
    store.path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = store.load()
    assert loaded.pointer_shape == constants.POINTER_SHAPE_DEFAULT
    assert loaded.polygon_curvature == constants.POLYGON_CURVATURE_DEFAULT
    assert loaded.polygon_edge == constants.POLYGON_EDGE_DEFAULT
    assert loaded.hide_night_borders is False


@pytest.mark.parametrize(
    "key,value",
    [
        ("pointer_shape", "hexagon"),
        ("polygon_edge", "rounded"),
        ("polygon_curvature", 1.5),
        ("hide_night_borders", "yes"),
    ],
)
def test_a_hand_edited_value_out_of_range_is_corrupt_not_silent(
    store, key, value
):
    """Rule #1: a bad value must fail HERE, never deep inside a paint
    pass where Qt swallows the exception."""
    store.save(Settings())
    raw = json.loads(store.path.read_text(encoding="utf-8"))
    raw[key] = value
    store.path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_the_settings_reach_the_skin(app):
    """The whole chain: Settings → build_skin → the render helpers."""
    skin = build_skin(
        replace(
            Settings(),
            pointer="octa",
            pointer_shape="polygon",
            polygon_curvature=0.4,
            polygon_edge="notched",
            hide_night_borders=True,
        )
    )
    assert skin.pointer_shape == "polygon"
    assert skin.polygon_curvature == pytest.approx(0.4)
    assert skin.polygon_edge == "notched"
    assert skin.hide_night_borders is True
    assert polygon_faces(skin) is True
    assert polygon_curvature(skin) == pytest.approx(0.4)


# --- The Design window's wiring reaches the live controller (phase 3) ---------------


@pytest.fixture
def controller(app, tmp_path, monkeypatch):
    """A REAL WatchController — the exact object whose `_design_setters()`
    the Design window's Pointer tab calls through, so this is the
    faithful proof that a row's pick both PERSISTS to `Settings` and
    reaches the INSTALLED skin, not a re-test of `build_skin` alone
    (already golden-tested above)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = WatchController(app)
    yield made
    made._teardown_windows()
    made._profiling_timer.stop()


def test_the_four_design_rows_persist_and_reach_the_live_skin(controller):
    """Rule #25 pin: every new Design ▸ Pointer row writes through the
    SAME `_set_display_choice` mechanism the neighboring rows use
    (Rule #5, no new mechanism) — `_design_setters()` is the exact dict
    `_open_design()` hands the window, so calling through it here is
    the real wiring, not a stand-in."""
    setters = controller._design_setters()
    setters["pointer"]("octa")
    setters["pointer_shape"]("polygon")
    assert controller._settings.pointer_shape == "polygon"
    assert controller._skin.pointer_shape == "polygon"
    assert polygon_faces(controller._skin) is True

    setters["polygon_curvature"](0.5)
    assert controller._settings.polygon_curvature == pytest.approx(0.5)
    assert controller._skin.polygon_curvature == pytest.approx(0.5)
    assert polygon_curvature(controller._skin) == pytest.approx(0.5)

    setters["polygon_edge"]("notched")
    assert controller._settings.polygon_edge == "notched"
    assert controller._skin.polygon_edge == "notched"

    setters["hide_night_borders"](True)
    assert controller._settings.hide_night_borders is True
    assert controller._skin.hide_night_borders is True
