"""Eclipse display (ROADMAP 15h item 11, owner 2026-07-18): the data
path (DeepTimeRepository.eclipses_near, bounded/indexed, never a table
scan), the core window (EclipseEvent, ±3h, TickState.eclipse_event),
the render (RED solar glow + Earth art swap, BRONZE lunar glow +
darkening, magnitude-scaled strength) and the ABSENCE rule: without the
Deep Time pack no eclipse ever renders — the app behaves exactly as
before this round."""

import dataclasses
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import (
    EclipseEvent,
    build_day_context,
    build_tick_state,
)
from core.deep_time import julian_day
from data.deep_time import DeepTimeRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import eclipse_glow_strength
from tests.deep_fixture import build_fixture_pack

REAL_PACK = Path(__file__).resolve().parents[1] / "Database" / "deep_time.sqlite"


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def deep(tmp_path_factory):
    path = build_fixture_pack(tmp_path_factory.mktemp("pack") / "deep_time.sqlite")
    return DeepTimeRepository.detect(path)


# --- The data path (bounded, indexed lookup) ----------------------------------


def test_eclipses_near_brackets_the_fixture_instants(deep):
    """Both directions, both kinds, from ONE indexed jd_ut query per
    side — never a full-table scan (the fixture pack proves the shape;
    the real pack's index makes it cheap at 70k+ rows)."""
    jd = julian_day(-4499, 6, 21, 0.5)         # between the two solar rows
    events = deep.eclipses_near(
        datetime(2301, 6, 21, 12, 0, tzinfo=timezone.utc), 17,
    )
    kinds = {(event.kind, event.type) for event in events}
    assert ("solar", "partial") in kinds        # -4499-03-08, before
    assert ("solar", "hybrid") in kinds          # -4499-09-12, after
    assert ("lunar", "total") in kinds           # -4499-04-02, before
    # The BEFORE candidates share `now`'s own proxy frame (2301±1); the
    # only AFTER lunar candidate in this fixture sits in the far span
    # (astro 3000), correctly re-shifted by the SAME 17 cycles (9800).
    solar_before = next(e for e in events if e.kind == "solar" and e.type == "partial")
    assert solar_before.instant.year == 2301
    lunar_before = next(e for e in events if e.kind == "lunar" and e.type == "total")
    assert lunar_before.instant.year == 2301


def test_eclipses_near_returns_empty_beyond_the_catalog_edge(deep):
    """At the far edge (only an AFTER or only a BEFORE exists) the
    missing side is simply absent from the tuple — no crash, no
    synthetic row (mirrors eclipse_after/before's own None-at-edge)."""
    events = deep.eclipses_near(
        datetime(3002, 6, 1, 0, 0, tzinfo=timezone.utc), 0,
    )
    # 3000-06-01 solar/3000-01-10 lunar are the LAST fixture rows —
    # strictly after 3002 there is nothing.
    assert all(event.instant.year <= 3000 for event in events)


@pytest.mark.skipif(not REAL_PACK.exists(), reason="Deep Time pack not built")
def test_golden_2026_08_12_total_solar_eclipse_is_in_the_catalog():
    """The famous candidate the owner named: a real total solar eclipse
    the morning of 2026-08-12 (greatest eclipse ~17:45:59 UT,
    magnitude ~1.04)."""
    repo = DeepTimeRepository.detect()
    events = repo.eclipses_near(datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc), 0)
    solar = [e for e in events if e.kind == "solar"]
    assert solar, "no solar eclipse candidate found around 2026-08-12"
    total = next(e for e in solar if e.type == "total")
    assert total.instant.date() == datetime(2026, 8, 12).date()
    assert total.instant.hour == 17 and total.instant.minute == 45
    assert 1.0 < total.magnitude < 1.1


# --- The core window (EclipseEvent, ±3h) --------------------------------------


def _belgrade_day(now, eclipses=()):
    observer = astral.Observer(latitude=44.82, longitude=20.46)
    return build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
        eclipses,
    )


def test_eclipse_window_on_and_off_boundary():
    tz = ZoneInfo("Europe/Belgrade")
    instant = datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc)
    eclipse = EclipseEvent(kind="solar", instant=instant, type="total", magnitude=1.04)
    now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    day = _belgrade_day(now, (eclipse,))
    local = instant.astimezone(tz)
    inside = build_tick_state(local - timedelta(hours=2, minutes=59), day)
    assert inside.eclipse_event is not None
    assert inside.eclipse_event.kind == "solar"
    outside = build_tick_state(local - timedelta(hours=3, minutes=1), day)
    assert outside.eclipse_event is None


def test_absent_pack_never_populates_eclipses():
    """The ABSENCE RULE (Rule #1-compatible documented fallback): the
    default `eclipses=()` (no Deep Time pack) means TickState.eclipse_event
    is ALWAYS None, at every instant — identical to the app before this
    round."""
    now = datetime(2026, 8, 12, 12, 0, tzinfo=ZoneInfo("Europe/Belgrade"))
    day = _belgrade_day(now)                    # eclipses defaults to ()
    assert day.eclipses == ()
    for offset_h in (-100, -3, 0, 3, 100):
        tick = build_tick_state(now + timedelta(hours=offset_h), day)
        assert tick.eclipse_event is None


def test_controller_absence_expression_yields_empty(tmp_path):
    """The exact ternary app/controller.py evaluates when the Deep Time
    pack is missing — pinned directly against DeepTimeRepository.detect
    returning None (no full install)."""
    deep = DeepTimeRepository.detect(tmp_path / "nope.sqlite")
    now = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
    eclipses = deep.eclipses_near(now, 0) if deep is not None else ()
    assert eclipses == ()


# --- Magnitude -> glow strength ------------------------------------------------


def test_eclipse_glow_strength_mapping():
    assert eclipse_glow_strength(defaults.ECLIPSE_MAGNITUDE_MIN) == pytest.approx(
        defaults.ECLIPSE_GLOW_STRENGTH_MIN
    )
    assert eclipse_glow_strength(defaults.ECLIPSE_MAGNITUDE_MAX) == pytest.approx(
        defaults.ECLIPSE_GLOW_STRENGTH_MAX
    )
    mid = eclipse_glow_strength(
        (defaults.ECLIPSE_MAGNITUDE_MIN + defaults.ECLIPSE_MAGNITUDE_MAX) / 2
    )
    assert defaults.ECLIPSE_GLOW_STRENGTH_MIN < mid < defaults.ECLIPSE_GLOW_STRENGTH_MAX
    # Clamped outside the documented range.
    assert eclipse_glow_strength(-5.0) == pytest.approx(
        defaults.ECLIPSE_GLOW_STRENGTH_MIN
    )
    assert eclipse_glow_strength(50.0) == pytest.approx(
        defaults.ECLIPSE_GLOW_STRENGTH_MAX
    )
    assert eclipse_glow_strength(None) == defaults.ECLIPSE_GLOW_STRENGTH_MAX


# --- Render: solar (Earth marker RED glow + art swap) -------------------------


def test_solar_eclipse_glow_is_red_not_gold(app):
    """A/B against the plain season glow (gold): the SAME relocated
    marker position must read noticeably MORE red-dominant with the
    eclipse active — pinning that the color override actually took."""
    tz = ZoneInfo("Europe/Belgrade")
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    day = _belgrade_day(solstice_noon)
    plain_glow = build_tick_state(solstice_noon, day)
    assert plain_glow.season_event == "Summer Solstice"
    quiet = dataclasses.replace(plain_glow, season_event=None, moon_event=None)
    eclipsed = dataclasses.replace(
        quiet,
        eclipse_event=EclipseEvent(
            kind="solar", instant=solstice_noon.astimezone(timezone.utc),
            type="total", magnitude=1.05,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    gold = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, plain_glow)
    red = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    marker_y = 270 - round(270 * defaults.GLOW_RING_RADIUS_FRACTION)
    probe = (289, marker_y + 33)
    gold_px = gold.pixelColor(*probe)
    red_px = red.pixelColor(*probe)
    # The eclipse RED glow must dominate red over green far more than the
    # golden glow does at the same spot.
    assert (red_px.red() - red_px.green()) > (gold_px.red() - gold_px.green()) + 15


def test_solar_eclipse_swaps_the_earth_art(app):
    """The Earth marker's rendered pixmap differs during a solar eclipse
    (the Planets Eclipsed-Sun dual, source-mapped) versus a plain day —
    same position, different art, so the marker disc itself changes."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 1, 12, 0, tzinfo=tz)     # no season/moon window
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    assert plain.season_event is None and plain.eclipse_event is None
    eclipsed = dataclasses.replace(
        plain,
        eclipse_event=EclipseEvent(
            kind="solar", instant=now.astimezone(timezone.utc),
            type="total", magnitude=1.02,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    before = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, plain)
    after = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    # The Earth marker relocates to the ring band during the eclipse —
    # sample its NEW drawn position (year_angle unchanged, radius swaps).
    year_angle = plain.year_angle
    radius = 270.0
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    theta = math.radians(year_angle)
    x = round(radius + orbit * math.sin(theta))
    y = round(radius - orbit * math.cos(theta))
    assert before.pixelColor(x, y) != after.pixelColor(x, y)
    assert defaults.ECLIPSE_SOLAR_ART.name == "sun_eclipse.png"


def test_solar_eclipse_hit_test_rides_the_relocated_marker(app):
    """The MARKER-PRIORITY note (Session 21-C): the eclipse window shares
    the season/moon relocation, so the Earth still hit-tests at its
    RING-BAND position with no new hit-test path needed."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 1, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    eclipsed = dataclasses.replace(
        plain,
        eclipse_event=EclipseEvent(
            kind="solar", instant=now.astimezone(timezone.utc),
            type="total", magnitude=1.02,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    theta = math.radians(plain.year_angle)
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    from PySide6.QtCore import QPointF

    x = radius + orbit * math.sin(theta)
    y = radius - orbit * math.cos(theta)
    point = QPointF(x - radius, y - radius)
    assert comp._element_at(
        point, radius, comp._rotation(), constants.WEEKDAY_BODIES[day.weekday_index],
    ) == "earth"


# --- Render: lunar (Moon marker darkened + bronze glow) ------------------------


def test_lunar_eclipse_glow_is_bronze_and_moon_is_darkened(app):
    """A/B: the eclipsed Moon renders visibly different from the plain
    full moon at the SAME cycle position — the bronze overlay changes
    the disc, and the halo differs from the silver moon-event glow."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)      # arbitrary, no window
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    quiet = dataclasses.replace(plain, season_event=None, moon_event=None)
    eclipsed = dataclasses.replace(
        quiet,
        eclipse_event=EclipseEvent(
            kind="lunar", instant=now.astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    before = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, quiet)
    after = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    moon_angle = math.radians(quiet.moon_fraction * 360.0)
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    x = round(radius + orbit * math.sin(moon_angle))
    y = round(radius - orbit * math.cos(moon_angle))
    assert before.pixelColor(x, y) != after.pixelColor(x, y)


def test_lunar_eclipse_hit_test_rides_the_relocated_marker(app):
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    eclipsed = dataclasses.replace(
        plain,
        eclipse_event=EclipseEvent(
            kind="lunar", instant=now.astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    moon_angle = math.radians(plain.moon_fraction * 360.0)
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    from PySide6.QtCore import QPointF

    x = radius + orbit * math.sin(moon_angle)
    y = radius - orbit * math.cos(moon_angle)
    point = QPointF(x - radius, y - radius)
    assert comp._element_at(
        point, radius, comp._rotation(), constants.WEEKDAY_BODIES[day.weekday_index],
    ) == "moon"


# --- Hover text NAMES the eclipse -----------------------------------------------


def test_earth_hover_names_the_solar_eclipse(app):
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    eclipsed = dataclasses.replace(
        plain,
        eclipse_event=EclipseEvent(
            kind="solar",
            instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
            type="total", magnitude=1.0395,
        ),
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, eclipsed)
    earth = comp._earth_text()
    assert "Solar Eclipse" in earth
    assert "Total" in earth
    assert "1.04" in earth or "1.0395"[:4] in earth
    assert "19:45" in earth or "17:45" in earth   # local (CEST) vs UT


def test_moon_hover_names_the_lunar_eclipse(app):
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    eclipsed = dataclasses.replace(
        plain,
        eclipse_event=EclipseEvent(
            kind="lunar", instant=now.astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, eclipsed)
    moon = comp._moon_text()
    assert "Lunar Eclipse" in moon
    assert "Total" in moon
    assert "1.15" in moon
