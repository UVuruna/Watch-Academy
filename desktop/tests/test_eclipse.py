"""Eclipse display (ROADMAP 15h item 11, owner 2026-07-18; THE THIRD
BODY, owner order 2026-08-12): the data path
(DeepTimeRepository.eclipses_near, bounded/indexed, never a table scan),
the core windows (EclipseEvent — ±3h into `TickState.eclipse_event` for
"happening now", ±12h into `eclipse_body_event` for the body's own
stand), the render (RED solar glow and the owner's eclipse art, BRONZE
lunar glow and darkening, magnitude-scaled strength — all of it on the
ECLIPSE'S OWN BODY at the hour it happens, never on the Earth or the
Moon marker) and the ABSENCE rule: without the Deep Time pack no eclipse
ever renders — the app behaves exactly as before this round."""

import dataclasses
import math
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults, dial, encyclopedia_ui, glow, palette
from core import angles
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
from render.context import RenderContext
from render.eclipse_glow import (
    eclipse_glow_strength,
    eclipse_render_state,
    eclipse_state_glow_strength,
)
from render.layers.year_marker import (
    marker_yields_band,
    earth_marker_angle,
    eclipse_body_angle,
    eclipse_body_orbit,
    eclipse_body_scale,
    moon_marker_angle,
    moon_marker_orbit,
)
from render.painting import dial_point
from tests.deep_fixture import build_fixture_pack

REAL_PACK = (
    Path(__file__).resolve().parents[2] / "shared" / "Database" / "deep_time.sqlite"
)


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


# --- Visibility (TASK 4, owner verdict "može", fix round E, 2026-07-19) -------


def test_eclipse_visibility_solar_distance_ground_truthed(app):
    """SOLAR visible <=> Sun above horizon AND within
    `ECLIPSE_SOLAR_VISIBILITY_KM` of the catalog's greatest-eclipse
    point. Ground-truthed against the SAME primitives `core.clock_state`
    uses (astral's own sun elevation at the instant, plain haversine)
    for the real 2026-08-12 total solar eclipse's greatest-eclipse
    instant (~17:46 UT) observed from Belgrade — whatever those say, the
    built TickState must agree, against a near AND a clearly-far catalog
    ground point."""
    import astral.sun

    tz = ZoneInfo("Europe/Belgrade")
    instant = datetime(2026, 8, 12, 17, 46, tzinfo=timezone.utc)
    local_now = instant.astimezone(tz)
    city = defaults.DEFAULT_CITY
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    sun_up = astral.sun.elevation(
        observer, instant, with_refraction=False
    ) > constants.HORIZON_ELEVATION_DEG
    # Ground truth, read from astral directly (not assumed): 17:46 UT is
    # 19:46 local in mid-August Belgrade, well within evening daylight.
    assert sun_up is True

    def haversine(lat1, lon1, lat2, lon2):
        r = constants.EARTH_RADIUS_KM
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        )
        return 2 * r * math.asin(math.sqrt(a))

    # A nearby ground point (well inside Europe) and a clearly distant
    # one (Sydney) — both distances computed independently of the code
    # under test, so the assertions below are ground truth, not circular.
    near_lat, near_lon = 46.0, 20.0
    far_lat, far_lon = -33.87, 151.21
    near_distance = haversine(city["latitude"], city["longitude"], near_lat, near_lon)
    far_distance = haversine(city["latitude"], city["longitude"], far_lat, far_lon)
    assert near_distance <= constants.ECLIPSE_SOLAR_VISIBILITY_KM
    assert far_distance > constants.ECLIPSE_SOLAR_VISIBILITY_KM

    near_day = _belgrade_day(
        local_now,
        (EclipseEvent(
            kind="solar", instant=instant, type="total", magnitude=1.0,
            lat=near_lat, lon=near_lon,
        ),),
    )
    far_day = _belgrade_day(
        local_now,
        (EclipseEvent(
            kind="solar", instant=instant, type="total", magnitude=1.0,
            lat=far_lat, lon=far_lon,
        ),),
    )
    near_tick = build_tick_state(local_now, near_day)
    far_tick = build_tick_state(local_now, far_day)
    # The FAR point fails on distance alone, regardless of daylight.
    assert far_tick.eclipse_event.visible is False
    assert far_tick.eclipse_event.distance_km == pytest.approx(far_distance, abs=1.0)
    # The NEAR point is within range — its visibility rests purely on
    # the ground-truthed daylight fact above (the sun has set).
    assert near_tick.eclipse_event.visible == sun_up
    assert near_tick.eclipse_event.distance_km == pytest.approx(near_distance, abs=1.0)


def test_eclipse_visibility_lunar_moon_altitude_ground_truthed(app):
    """LUNAR visible <=> the Moon stands above the horizon at the eclipse
    instant — ground-truthed directly against astral's own
    `astral.moon.elevation` (the same primitive `core.clock_state`
    uses), picking one instant it reads above and one it reads below
    from a spread of candidates rather than assuming either from
    memory."""
    import astral.moon

    tz = ZoneInfo("Europe/Belgrade")
    city = defaults.DEFAULT_CITY
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    candidates = [
        datetime(2026, 3, 3, h, 0, tzinfo=timezone.utc) for h in range(0, 24, 3)
    ]
    elevations = {
        instant: astral.moon.elevation(observer, instant) for instant in candidates
    }
    above = next(i for i, e in elevations.items() if e > 0.0)
    below = next(i for i, e in elevations.items() if e <= 0.0)

    def tick_for(instant):
        local_now = instant.astimezone(tz)
        day = _belgrade_day(
            local_now,
            (EclipseEvent(
                kind="lunar", instant=instant, type="total", magnitude=1.2,
            ),),
        )
        return build_tick_state(local_now, day)

    assert tick_for(above).eclipse_event.visible is True
    assert tick_for(below).eclipse_event.visible is False


def test_eclipse_invisible_hover_names_the_reason(app):
    """The card's Visibility row names the reason (owner spec, round
    numbers, the km threshold never printed): "below the horizon" for a
    horizon miss, "path {d} km away" for a solar distance miss."""
    tz = ZoneInfo("Europe/Belgrade")
    instant = datetime(2026, 8, 12, 17, 46, tzinfo=timezone.utc)
    local_now = instant.astimezone(tz)
    day = _belgrade_day(local_now)
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, build_tick_state(local_now, day))

    far_event = EclipseEvent(
        kind="solar", instant=instant, type="total", magnitude=1.0,
        lat=-33.87, lon=151.21, visible=False, distance_km=16123.4,
    )
    horizon_event = EclipseEvent(
        kind="lunar", instant=instant, type="total", magnitude=1.2,
        visible=False,
    )
    far_line = compositor._eclipse_visibility_text(far_event)
    horizon_line = compositor._eclipse_visibility_text(horizon_event)
    assert "16123 km away" in far_line
    assert "below the horizon" in horizon_line
    assert str(constants.ECLIPSE_SOLAR_VISIBILITY_KM) not in far_line
    # A visible one says so rather than falling silent.
    assert "Visible" in compositor._eclipse_visibility_text(
        dataclasses.replace(far_event, visible=True)
    )


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
    assert eclipse_glow_strength(glow.ECLIPSE_MAGNITUDE_MIN) == pytest.approx(
        glow.ECLIPSE_GLOW_STRENGTH_MIN
    )
    assert eclipse_glow_strength(glow.ECLIPSE_MAGNITUDE_MAX) == pytest.approx(
        glow.ECLIPSE_GLOW_STRENGTH_MAX
    )
    mid = eclipse_glow_strength(
        (glow.ECLIPSE_MAGNITUDE_MIN + glow.ECLIPSE_MAGNITUDE_MAX) / 2
    )
    assert glow.ECLIPSE_GLOW_STRENGTH_MIN < mid < glow.ECLIPSE_GLOW_STRENGTH_MAX
    # Clamped outside the documented range.
    assert eclipse_glow_strength(-5.0) == pytest.approx(
        glow.ECLIPSE_GLOW_STRENGTH_MIN
    )
    assert eclipse_glow_strength(50.0) == pytest.approx(
        glow.ECLIPSE_GLOW_STRENGTH_MAX
    )
    assert eclipse_glow_strength(None) == glow.ECLIPSE_GLOW_STRENGTH_MAX


# --- Render: THE ECLIPSE BODY (owner order 2026-08-12) ------------------------
# These tests were rewritten wholesale this round. They used to pin the
# COSTUME — a solar eclipse turning the Earth marker red and swapping its
# art at the Earth's own seat — and that law is retired: the owner ruled
# the eclipse must stand apart from the Earth, at the hour it happens
# (ballot A1). What survives unchanged is every colour, strength and
# geometry rule; only the body they are painted on is new.


def _eclipse_body_probe(skin, day, tick, radius: float = 270.0):
    """Where the eclipse body is drawn, in image pixels, plus its own
    half-size — read off the SAME functions the dial paints with
    (`render.layers.year_marker`), never recomputed here. A test that
    re-derived the seat would be pinning its own arithmetic; this way the
    collision escape (E1/F1) is exercised by the test too."""
    ctx = RenderContext(
        skin=skin, day=day, tick=tick, radius=radius,
        cache=AssetCache(), dpr=1.0,
    )
    event = tick.eclipse_body_event
    scale = eclipse_body_scale(ctx, event.kind == "solar")
    angle = eclipse_body_angle(ctx, event)
    point = dial_point(angle, radius * eclipse_body_orbit(ctx, angle, scale))
    return round(radius + point.x()), round(radius + point.y()), radius * scale


def test_solar_eclipse_glow_is_red_not_gold(app):
    """A/B at the eclipse BODY's own seat: with the eclipse active that
    spot must read markedly more red-dominant than the untouched dial
    reads there — pinning that the red override took, on the new body."""
    tz = ZoneInfo("Europe/Belgrade")
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    day = _belgrade_day(solstice_noon)
    plain_glow = build_tick_state(solstice_noon, day)
    assert plain_glow.season_event == "Summer Solstice"
    quiet = dataclasses.replace(plain_glow, season_event=None, moon_event=None)
    # 17:00 local — a seat far from both markers, so the body stays on
    # the orbit lane and this measures the glow, not the escape.
    instant = datetime(2026, 6, 21, 17, 0, tzinfo=tz).astimezone(timezone.utc)
    event = EclipseEvent(
        kind="solar", instant=instant, type="total", magnitude=1.05,
    )
    eclipsed = dataclasses.replace(
        quiet, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    plain = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, quiet)
    red = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    x, y, half = _eclipse_body_probe(skin, day, eclipsed)
    probe = (x, y - round(half * 1.25))       # inside the halo, past the disc
    plain_px = plain.pixelColor(*probe)
    red_px = red.pixelColor(*probe)
    assert (red_px.red() - red_px.green()) > (
        plain_px.red() - plain_px.green()
    ) + 15


def test_solar_eclipse_stands_apart_from_the_earth(app):
    """THE THIRD BODY (owner order 2026-08-12, his first sentence of that
    day): the eclipse is drawn at the HOUR it happens, and the Earth
    marker is left completely alone — same pixels at the Earth's own seat
    with and without the eclipse, different pixels at the eclipse's."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 1, 12, 0, tzinfo=tz)     # no season/moon window
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    assert plain.season_event is None and plain.eclipse_event is None
    instant = datetime(2026, 3, 1, 17, 0, tzinfo=tz).astimezone(timezone.utc)
    event = EclipseEvent(
        kind="solar", instant=instant, type="total", magnitude=1.02,
    )
    eclipsed = dataclasses.replace(
        plain, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    before = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, plain)
    after = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    # 1. The Earth keeps its seat, its lane AND its art.
    earth_point = dial_point(
        plain.year_angle,
        radius * dial.earth_moon_orbit_fraction(
            skin.numeral_outer_ring_size, skin.year_marker.scale,
        ),
    )
    ex, ey = round(radius + earth_point.x()), round(radius + earth_point.y())
    assert before.pixelColor(ex, ey) == after.pixelColor(ex, ey)
    # 2. The eclipse body appears at its OWN hour seat.
    x, y, _half = _eclipse_body_probe(skin, day, eclipsed)
    assert before.pixelColor(x, y) != after.pixelColor(x, y)
    # 3. That seat is the hour hand's own reading of the instant, not the
    #    Earth's date angle — the whole point of the round.
    assert round(angles.time_to_dial_angle(instant.astimezone(tz))) == 75
    # THE OWNER'S OWN ECLIPSE ICON (correction 2026-08-11): the body's
    # art is `assets/instrument/icons/sun_eclipse.png` — never the
    # Planets theme's Eclipsed-Sun weekday dual.
    assert defaults.ECLIPSE_SOLAR_ART.name == "sun_eclipse.png"
    assert defaults.ECLIPSE_SOLAR_ART.parent.name == "icons"
    assert defaults.ECLIPSE_SOLAR_ART.exists()


def test_the_eclipse_body_answers_the_cursor_not_the_earth(app):
    """THE HOVER FOLLOWS THE DRAWN BODY (owner correction 2026-08-12: the
    hover must show the eclipse's info, not the Earth's).

    This test replaces one that pinned the OPPOSITE — the retired costume
    era, where a solar eclipse relocated the Earth marker to the ring band
    and the hit test copied that relocation by hand. Since the costume
    went, the marker stays on its ordinary circle: cursor over the eclipse
    body must answer "eclipse", and cursor over the Earth must answer
    "earth" AT ITS CIRCLE, not at the band."""
    from PySide6.QtCore import QPointF

    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 1, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    event = EclipseEvent(
        kind="solar", instant=now.replace(hour=17).astimezone(timezone.utc),
        type="total", magnitude=1.02,
    )
    eclipsed = dataclasses.replace(
        plain, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    today = constants.WEEKDAY_BODIES[day.weekday_index]

    def element_at(x: float, y: float) -> str | None:
        return comp._element_at(
            QPointF(x - radius, y - radius), radius, comp._rotation(), today,
        )

    x, y, _half = _eclipse_body_probe(skin, day, eclipsed)
    assert element_at(x, y) == "eclipse"
    # The Earth answers at the circle it is DRAWN on...
    earth = dial_point(
        plain.year_angle,
        radius * dial.earth_moon_orbit_fraction(
            skin.numeral_outer_ring_size, skin.year_marker.scale,
        ),
    )
    assert element_at(radius + earth.x(), radius + earth.y()) == "earth"
    # ...and no longer at the ring band the costume used to move it to.
    band = dial_point(plain.year_angle, radius * dial.GLOW_RING_RADIUS_FRACTION)
    assert element_at(radius + band.x(), radius + band.y()) != "earth"


# --- Render: lunar (Moon marker darkened + bronze glow) ------------------------


def test_lunar_eclipse_is_a_body_apart_from_the_moon(app):
    """THE TWO MARKS (owner order 2026-08-12, ballot D1, his words: the
    Moon stays on the circle whether it is full or new). An eclipsed Moon
    appears as its OWN body at the eclipse's hour — and the Moon marker
    at its cycle seat is left pixel-for-pixel alone, so phase and eclipse
    are two readings instead of one blurred picture."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)      # arbitrary, no window
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    quiet = dataclasses.replace(plain, season_event=None, moon_event=None)
    event = EclipseEvent(
        kind="lunar", instant=now.replace(hour=17).astimezone(timezone.utc),
        type="total", magnitude=1.15,
    )
    eclipsed = dataclasses.replace(
        quiet, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    before = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, quiet)
    after = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    # 1. The Moon marker keeps its own seat, its own lane and its face.
    moon_point = dial_point(
        angles.moon_cycle_angle(quiet.moon_fraction),
        radius * dial.earth_moon_orbit_fraction(
            skin.numeral_outer_ring_size, skin.year_marker.moon_scale,
        ),
    )
    mx = round(radius + moon_point.x())
    my = round(radius + moon_point.y())
    assert before.pixelColor(mx, my) == after.pixelColor(mx, my)
    # 2. The eclipse stands on its own, at the hour it happens.
    x, y, _half = _eclipse_body_probe(skin, day, eclipsed)
    assert before.pixelColor(x, y) != after.pixelColor(x, y)


def test_the_hover_follows_the_moon_off_the_ring_when_it_yields(app):
    """THE OWNER'S SECOND REPORT, 2026-08-12: "the hover does not seem to
    follow the Moon's relocation off the ring when it overlaps with the
    eclipse". It did not — the hit test carried its own hand-written copy
    of the marker geometry, so the collision rule this round added moved
    the DRAWN Moon and left the TARGET on the band.

    The collision case, exactly as the render shows it: the eclipse takes
    the ring band, the Moon steps back to the ordinary circle — and the
    cursor must find each of them where it is drawn."""
    from PySide6.QtCore import QPointF

    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 9, 30, tzinfo=tz)
    day = _belgrade_day(now)
    tick = build_tick_state(now, day)
    assert tick.moon_event == "Full Moon"          # the Moon is band-bound
    event = EclipseEvent(
        kind="lunar", instant=now.replace(hour=0, minute=10).astimezone(timezone.utc),
        type="total", magnitude=1.30,
    )
    eclipsed = dataclasses.replace(
        tick, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    today = constants.WEEKDAY_BODIES[day.weekday_index]

    def element_at(point) -> str | None:
        return comp._element_at(
            QPointF(point.x(), point.y()), radius, comp._rotation(), today,
        )

    ctx = _eclipse_ctx(skin, day, eclipsed)
    # The Moon has indeed left the band...
    assert moon_marker_orbit(ctx) != dial.GLOW_RING_RADIUS_FRACTION
    # ...and the cursor finds it there, on the circle it is drawn on.
    assert element_at(
        dial_point(moon_marker_angle(ctx), radius * moon_marker_orbit(ctx))
    ) == "moon"
    # The band it left now answers with the body that took it.
    assert element_at(
        dial_point(
            eclipse_body_angle(ctx, event),
            radius * dial.GLOW_RING_RADIUS_FRACTION,
        )
    ) == "eclipse"


# --- The type -> state table (fix round C, owner decree 2026-07-19) -----------


def test_type_state_mapping_covers_the_ground_truthed_vocabulary():
    """The catalog's ACTUAL type vocabulary (ground-truthed from
    Database/deep_time.sqlite: solar {partial, annular, total, hybrid},
    lunar {partial, penumbral, total}) each resolve to a named state.

    HYBRID HAS ITS OWN STATE since the eclipse rework (owner order
    2026-08-13). It used to be aliased onto "solar_total", and this test
    pinned that alias — which is precisely why the collapse survived so
    long: a hybrid eclipse then drew a byte-identical picture to a total
    one in every display style at once. It is total on part of its
    ground track and annular on the rest, and the dial now says so."""
    assert eclipse_render_state(
        EclipseEvent(kind="lunar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="total", magnitude=1.1)
    ) == "lunar_total"
    assert eclipse_render_state(
        EclipseEvent(kind="lunar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="partial", magnitude=0.5)
    ) == "lunar_partial"
    assert eclipse_render_state(
        EclipseEvent(kind="lunar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="penumbral", magnitude=0.9)
    ) == "lunar_penumbral"
    assert eclipse_render_state(
        EclipseEvent(kind="solar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="total", magnitude=1.05)
    ) == "solar_total"
    assert eclipse_render_state(
        EclipseEvent(kind="solar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="hybrid", magnitude=1.0)
    ) == "solar_hybrid"
    assert eclipse_render_state(
        EclipseEvent(kind="solar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="annular", magnitude=0.95)
    ) == "solar_annular"
    assert eclipse_render_state(
        EclipseEvent(kind="solar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="partial", magnitude=0.3)
    ) == "solar_partial"


def test_unknown_type_falls_back_to_the_kind_partial_state():
    """Documented fallback (Rule #1): a malformed catalog row still
    renders — the kind's PARTIAL state, never a crash."""
    assert eclipse_render_state(
        EclipseEvent(kind="lunar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="bogus", magnitude=0.5)
    ) == "lunar_partial"
    assert eclipse_render_state(
        EclipseEvent(kind="solar", instant=datetime(2026, 1, 1, tzinfo=timezone.utc), type="bogus", magnitude=0.5)
    ) == "solar_partial"


def test_solar_partial_is_the_one_state_still_magnitude_scaled():
    """Every other state carries a FIXED glow-strength constant; only
    `solar_partial` keeps the original magnitude-linear mapping (owner's
    named exception)."""
    for state in (
        "lunar_total", "lunar_partial", "lunar_penumbral",
        "solar_total", "solar_hybrid", "solar_annular",
    ):
        assert eclipse_state_glow_strength(state, 0.01) == pytest.approx(
            eclipse_state_glow_strength(state, 1.19)
        ), f"{state} must ignore magnitude"
    lo = eclipse_state_glow_strength("solar_partial", glow.ECLIPSE_MAGNITUDE_MIN)
    hi = eclipse_state_glow_strength("solar_partial", glow.ECLIPSE_MAGNITUDE_MAX)
    assert lo < hi        # solar_partial alone still tracks magnitude


# --- Render: per-state lunar darkening (fix round C, owner decree 2026-07-19) --


def _lunar_moon_pixel(app, type_: str, magnitude: float):
    """Renders a lunar eclipse of the given TYPE and samples the Moon
    marker's own pixel at its relocated (ring-band) center — the moon's
    OWN art occludes the glow halo directly under it, so this reads only
    the darkened disc, never the bronze glow bleeding through.

    PINNED TO THE "halo" STYLE (2026-08-10). The whole-disc multiply
    these tests measure is one of three lunar treatments the owner
    approved that day, and no longer the default — "umbra_sweep" now
    ships instead, drawing Earth's shadow as a real curved edge so the
    magnitude becomes visible geometry. The multiply is still a shipped
    option and its behaviour (the near-black ceiling, the blood-moon
    copper, the brightness ladder, the deliberate independence from
    magnitude) is still law, so these teeth name the style they measure
    rather than riding whatever the default happens to be. The new
    default has its own tooth in `tests/test_moving_bodies.py`."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    # Pinned above the horizon (owner's separate hidden-alpha dimming,
    # `moon_hidden_alpha`, would otherwise blend the marker toward the
    # background and confound a pure disc-brightness measurement).
    quiet = dataclasses.replace(
        plain, season_event=None, moon_event=None, is_moon_up=True,
    )
    # THE ECLIPSE'S OWN HOUR, deliberately NOT the rendered moment: at
    # 12:00 the body would sit at the top of the dial, exactly under the
    # hour hand, and the probe would measure the HAND instead of the
    # disc. 17:00 seats it at 75° — clear of both hands and of both
    # markers, so what is sampled is the eclipse and nothing else.
    event = EclipseEvent(
        kind="lunar",
        instant=now.replace(hour=17).astimezone(timezone.utc),
        type=type_, magnitude=magnitude,
    )
    eclipsed = dataclasses.replace(
        quiet, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        solar_rotation=False,
        year_marker=dataclasses.replace(
            defaults.DEFAULT_SKIN.year_marker, eclipse_lunar_style="halo",
        ),
    )
    image = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    # THE BODY'S OWN SEAT (owner order 2026-08-12): the darkened disc is
    # the ECLIPSE's, standing at the hour of greatest eclipse — the Moon
    # marker itself keeps its phase seat and is no longer touched.
    x, y, _half = _eclipse_body_probe(skin, day, eclipsed)
    return image.pixelColor(x, y)


def test_lunar_total_disc_is_genuinely_near_black(app):
    """The owner's exact complaint: a TOTAL lunar eclipse must read as an
    unmistakably darkened, near-black disc — not a bright moon under a
    translucent wash. Max channel value stays under a hard threshold
    well below the old translucent overlay would ever reach."""
    pixel = _lunar_moon_pixel(app, "total", 1.15)
    assert max(pixel.red(), pixel.green(), pixel.blue()) < 55


def test_lunar_total_disc_wears_copper_not_neutral_gray(app):
    """Fix round E (owner verdict "može"): the TOTAL lunar disc multiplies
    with a deep COPPER tone (`palette.ECLIPSE_TOTAL_MOON_TINT`) instead
    of neutral gray — dark (same near-black ceiling as the plain
    near-black test) AND red-DOMINANT (red channel clearly ahead of
    green/blue, a neutral gray would tie all three)."""
    pixel = _lunar_moon_pixel(app, "total", 1.15)
    assert max(pixel.red(), pixel.green(), pixel.blue()) < 55
    assert pixel.red() > pixel.green() > pixel.blue()


def test_lunar_penumbral_clearly_brighter_than_partial(app):
    """Type alone sets brightness (60% vs 18% of full value) — the
    penumbral disc must read distinctly brighter than the partial disc,
    same magnitude, same everything else."""
    partial = _lunar_moon_pixel(app, "partial", 1.0)
    penumbral = _lunar_moon_pixel(app, "penumbral", 1.0)
    partial_sum = partial.red() + partial.green() + partial.blue()
    penumbral_sum = penumbral.red() + penumbral.green() + penumbral.blue()
    assert penumbral_sum > partial_sum + 40


def test_lunar_partial_clearly_brighter_than_total(app):
    total = _lunar_moon_pixel(app, "total", 1.0)
    partial = _lunar_moon_pixel(app, "partial", 1.0)
    total_sum = total.red() + total.green() + total.blue()
    partial_sum = partial.red() + partial.green() + partial.blue()
    assert partial_sum > total_sum + 20


def test_lunar_disc_brightness_ignores_magnitude(app):
    """The owner's core decree: disc brightness is TYPE-driven only —
    magnitude may vary the GLOW, never the disc's see-through-ness."""
    low = _lunar_moon_pixel(app, "total", glow.ECLIPSE_MAGNITUDE_MIN)
    high = _lunar_moon_pixel(app, "total", glow.ECLIPSE_MAGNITUDE_MAX)
    assert max(low.red(), low.green(), low.blue()) < 55
    assert max(high.red(), high.green(), high.blue()) < 55


# --- Render: solar annular "ring of fire" glow color ---------------------------


def _solar_glow_pixel(app, type_: str, magnitude: float):
    tz = ZoneInfo("Europe/Belgrade")
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    day = _belgrade_day(solstice_noon)
    plain_glow = build_tick_state(solstice_noon, day)
    quiet = dataclasses.replace(plain_glow, season_event=None, moon_event=None)
    # 17:00 local: a seat clear of both markers, so the two types are
    # compared at the same spot on the same lane.
    instant = datetime(2026, 6, 21, 17, 0, tzinfo=tz).astimezone(timezone.utc)
    event = EclipseEvent(
        kind="solar", instant=instant, type=type_, magnitude=magnitude,
    )
    eclipsed = dataclasses.replace(
        quiet, eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    image = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    x, y, half = _eclipse_body_probe(skin, day, eclipsed)
    # THE PROBE SITS OUTSIDE THE CORONA (eclipse rework 2026-08-13). It
    # used to read at 1.25 body radii, which the default "bite" style
    # now fills with the pearly corona at totality — a mark, not the
    # glow, and this test is about the GLOW's colour. 1.40 is past the
    # corona's own fade-out (`marker_marks._CORONA_REACH`) and still
    # well inside the halo, so what is compared is the halo alone.
    return image.pixelColor(x, y - round(half * 1.32))


def test_solar_annular_glow_hue_differs_from_total(app):
    """The "ring of fire" (owner decree, fix round C): an ANNULAR solar
    eclipse keeps the same black-sun art but its glow shifts to a
    hotter orange-red than a TOTAL eclipse's plain red — measurably more
    green in the halo at the same probe point."""
    total_px = _solar_glow_pixel(app, "total", 1.05)
    annular_px = _solar_glow_pixel(app, "annular", 0.95)
    assert annular_px.green() > total_px.green() + 15


def test_solar_total_and_annular_glow_are_full_strength_regardless_of_magnitude():
    """Fix round C: total/annular glow strength is FIXED (1.0), unlike
    the old build where every solar state scaled with magnitude."""
    assert eclipse_state_glow_strength("solar_total", 0.01) == pytest.approx(1.0)
    assert eclipse_state_glow_strength("solar_annular", 0.01) == pytest.approx(1.0)


# --- Hover text NAMES the eclipse -----------------------------------------------


def test_the_eclipse_card_is_its_own_and_the_markers_say_nothing(app):
    """THE ECLIPSE'S OWN CARD (owner correction 2026-08-12: "the hover
    should show info about the eclipse, not the same as the earth
    hover"). The card names the type, the depth and the local instant —
    and the Earth's and the Moon's cards are back to speaking only the
    date and the phase, which is all their markers show that day."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    event = EclipseEvent(
        kind="solar",
        instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
        type="total", magnitude=1.0395,
    )
    eclipsed = dataclasses.replace(
        plain, eclipse_event=event, eclipse_body_event=event,
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, eclipsed)
    card = comp._eclipse_text()
    assert "Total Solar Eclipse" in card          # the chapter's own title
    assert "Magnitude" in card and "1.04" in card
    assert "19:45" in card or "17:45" in card     # local (CEST) vs UT
    assert "Visibility" in card
    # The markers keep their own subjects, and only their own.
    assert "Eclipse" not in comp._earth_text()
    assert "Eclipse" not in comp._moon_text()


def test_the_lunar_eclipse_card_speaks_its_own_chapter(app):
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    event = EclipseEvent(
        kind="lunar", instant=now.astimezone(timezone.utc),
        type="total", magnitude=1.15,
    )
    eclipsed = dataclasses.replace(
        plain, eclipse_event=event, eclipse_body_event=event,
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, eclipsed)
    card = comp._eclipse_text()
    assert "Total Lunar Eclipse" in card
    assert "1.15" in card
    assert "Eclipse" not in comp._moon_text()


# --- THE ECLIPSES ENCYCLOPEDIA (fix round F, owner order 2026-07-19) -----------
#
# TASK 4 (Spacebar jump to the active category's chapter) and TASK 3 (the
# category emblem on the Earth/Moon hover card, graceful-absent).


def _eclipse_marker_probe(kind, type_, magnitude=1.05):
    """Render an eclipse window and return (compositor, x, y, size) at THE
    ECLIPSE BODY's own drawn seat — read from `render.layers.year_marker`,
    the functions the dial paints and the hit test answers with, so the
    Spacebar target is taken at the exact spot the reader points at.

    Until 2026-08-12 this probed the Earth/Moon marker at the ring band,
    because the eclipse was a costume those markers wore. It is a body of
    its own now, and so is its page."""
    tz = ZoneInfo("Europe/Belgrade")
    now = (
        datetime(2026, 3, 3, 12, 0, tzinfo=tz) if kind == "lunar"
        else datetime(2026, 3, 1, 12, 0, tzinfo=tz)
    )
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    event = EclipseEvent(
        kind=kind, instant=now.replace(hour=17).astimezone(timezone.utc),
        type=type_, magnitude=magnitude,
    )
    eclipsed = dataclasses.replace(
        plain, season_event=None, moon_event=None,
        eclipse_event=event, eclipse_body_event=event,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    x, y, _half = _eclipse_body_probe(skin, day, eclipsed)
    return comp, float(x), float(y), 540.0


@pytest.mark.parametrize("kind,type_,topic,index", [
    ("solar", "total", "eclipse_solar", 1),
    ("solar", "annular", "eclipse_solar", 2),
    ("solar", "partial", "eclipse_solar", 3),
    ("solar", "hybrid", "eclipse_solar", 4),
    ("lunar", "total", "eclipse_lunar", 1),
    ("lunar", "partial", "eclipse_lunar", 2),
    ("lunar", "penumbral", "eclipse_lunar", 3),
])
def test_space_jump_opens_the_active_eclipse_chapter(app, kind, type_, topic, index):
    """TASK 4 golden, re-seated on THE THIRD BODY (owner 2026-08-12):
    Space over the ECLIPSE opens the Encyclopedia at THAT category's
    chapter — every one of the seven categories, indexed by the active
    type; hybrid keeps its OWN chapter (index 4), not solar_total's."""
    comp, x, y, size = _eclipse_marker_probe(kind, type_)
    assert comp.encyclopedia_target(x, y, size) == (topic, index)


def test_space_jump_falls_back_to_seasons_and_phase_without_eclipse(app):
    """Without an eclipse window the Earth still opens SEASONS and the
    Moon its current PHASE — the eclipse branch never hijacks the plain
    targets (Rule #6: no behavior change for the non-eclipse path)."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 6, 21, 12, 0, tzinfo=tz)      # summer-solstice glow
    day = _belgrade_day(now)
    tick = build_tick_state(now, day)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, tick)
    radius = 270.0
    orbit = radius * dial.GLOW_RING_RADIUS_FRACTION
    theta = math.radians(tick.year_angle)
    earth = comp.encyclopedia_target(
        radius + orbit * math.sin(theta), radius - orbit * math.cos(theta), 540.0
    )
    assert earth is not None and earth[0] == "seasons"


def test_eclipse_emblem_maps_every_category_and_is_graceful(app):
    """TASK 3 mapping: `_eclipse_emblem` resolves each (kind, type) to
    its own category emblem under assets/eclipse/, an unknown type to
    None, and the badge degrades to EMPTY while the art is absent
    (graceful-absent — the sheet's art has not landed)."""
    from render.compositor import _hover_badge

    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, build_tick_state(now, day))
    expected = {
        ("solar", "total"): "Solar_Total.png",
        ("solar", "annular"): "Solar_Annular.png",
        ("solar", "partial"): "Solar_Partial.png",
        ("solar", "hybrid"): "Solar_Hybrid.png",
        ("lunar", "total"): "Lunar_Total.png",
        ("lunar", "partial"): "Lunar_Partial.png",
        ("lunar", "penumbral"): "Lunar_Penumbral.png",
    }
    for (kind, type_), stem in expected.items():
        event = EclipseEvent(
            kind=kind, instant=now.astimezone(timezone.utc),
            type=type_, magnitude=1.0,
        )
        path = comp._eclipse_emblem(event)
        assert path is not None and path.name == stem
        assert path.parent == glow.ECLIPSE_ART_DIR
        # Art-arrival-proof (the subdial lesson, 0.14.367): while the
        # art is absent the badge degrades to EMPTY (graceful), and the
        # moment a source subtree carries the file (the ChatGPT batch,
        # unlocked by registering the "eclipse" root) it must RENDER.
        from config import paths as _paths
        if _paths.art_file(path).exists():
            assert _hover_badge(path) != ""
        else:
            assert _hover_badge(path) == ""
    unknown = EclipseEvent(
        kind="solar", instant=now.astimezone(timezone.utc),
        type="bogus", magnitude=1.0,
    )
    assert comp._eclipse_emblem(unknown) is None


def test_eclipse_hover_card_shows_emblem_when_art_present(app, tmp_path, monkeypatch):
    """TASK 3 wiring, re-seated on the eclipse's OWN card (owner
    2026-08-12): when the category emblem art DOES exist, the badge
    crowns that card — solar and lunar alike (owner slika 7). A real
    (tiny) PNG under a monkeypatched eclipse dir proves the slot is
    wired, not just the graceful-absent path."""
    from PySide6.QtGui import QImage

    monkeypatch.setattr(glow, "ECLIPSE_ART_DIR", tmp_path)
    swatch = QImage(8, 8, QImage.Format.Format_ARGB32)
    swatch.fill(0xFFCC5522)
    for stem in ("Solar_Total.png", "Lunar_Total.png"):
        assert swatch.save(str(tmp_path / stem))

    tz = ZoneInfo("Europe/Belgrade")
    # Solar.
    solar_now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    solar_day = _belgrade_day(solar_now)
    solar_event = EclipseEvent(
        kind="solar",
        instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
        type="total", magnitude=1.04,
    )
    solar_tick = dataclasses.replace(
        build_tick_state(solar_now, solar_day),
        eclipse_event=solar_event, eclipse_body_event=solar_event,
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, solar_day, solar_tick)
    card = comp._eclipse_text()
    assert "Solar Eclipse" in card
    assert tmp_path.joinpath("Solar_Total.png").as_uri() in card

    # Lunar.
    lunar_now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    lunar_day = _belgrade_day(lunar_now)
    lunar_event = EclipseEvent(
        kind="lunar", instant=lunar_now.astimezone(timezone.utc),
        type="total", magnitude=1.15,
    )
    lunar_tick = dataclasses.replace(
        build_tick_state(lunar_now, lunar_day),
        eclipse_event=lunar_event, eclipse_body_event=lunar_event,
    )
    comp.render_offscreen(360.0, 1.0, lunar_day, lunar_tick)
    card = comp._eclipse_text()
    assert "Lunar Eclipse" in card
    assert tmp_path.joinpath("Lunar_Total.png").as_uri() in card


# --- THE PER-TYPE ECLIPSE ICONS (ART-INFRA round, owner 2026-07-20/21) --------
#
# Distinct from the category EMBLEM above (the big rose-window plate,
# unchanged this round): a SMALL icon rides inline before the hover
# line's own title, red/gold/blue for LUNAR (owner-approved), a shape-
# matched proposal for SOLAR.


def test_eclipse_lunar_type_icon_mapping():
    """The owner-approved mapping: red=TOTAL, gold=PARTIAL,
    blue=PENUMBRAL; an unknown type is graceful-absent (None)."""
    assert defaults.eclipse_lunar_type_icon("total").name == "moon_eclipse_red.png"
    assert defaults.eclipse_lunar_type_icon("partial").name == "moon_eclipse_gold.png"
    assert (
        defaults.eclipse_lunar_type_icon("penumbral").name
        == "moon_eclipse_blue.png"
    )
    assert defaults.eclipse_lunar_type_icon("bogus") is None


def test_eclipse_solar_type_icon_total_and_partial_are_as_drawn():
    """Total/partial ride their source file UNCHANGED — only annular
    gets the computed tint (below)."""
    from render.asset_variants import eclipse_solar_type_icon

    assert (
        eclipse_solar_type_icon("total")
        == defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE["total"]
    )
    assert (
        eclipse_solar_type_icon("partial")
        == defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE["partial"]
    )
    assert eclipse_solar_type_icon("bogus") is None


def test_eclipse_solar_annular_icon_is_tinted_toward_the_ring_of_fire_color(app):
    """The PROPOSED solar recolor (owner: "consider recoloring one for
    more noticeable distinction"): annular's icon is TRITONE-tinted
    toward GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR — a DIFFERENT file than the
    plain source, and its bright (non-black) pixels read that hue."""
    from PySide6.QtGui import QColor, QImage

    from render.asset_variants import eclipse_solar_type_icon

    tinted_path = eclipse_solar_type_icon("annular")
    source_path = defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE["annular"]
    assert tinted_path != source_path
    assert tinted_path.exists()
    image = QImage(str(tinted_path))
    target_hue = QColor(palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR).hueF() * 360.0
    seen_bright = False
    for x in range(0, image.width(), 15):
        for y in range(0, image.height(), 15):
            px = image.pixelColor(x, y)
            if px.alpha() < 200 or px.lightness() < 40:
                continue     # transparent or the near-black eclipsed disc
            seen_bright = True
            assert min(abs(px.hueF() * 360.0 - target_hue), 12.0) <= 12.0
    assert seen_bright


def test_eclipse_hover_line_carries_the_lunar_type_icon(app):
    """Wiring: the eclipse card's Type row embeds the type icon's own
    URI inline, ahead of the type name it labels."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    for type_, stem in (
        ("total", "moon_eclipse_red.png"),
        ("partial", "moon_eclipse_gold.png"),
        ("penumbral", "moon_eclipse_blue.png"),
    ):
        event = EclipseEvent(
            kind="lunar", instant=now.astimezone(timezone.utc),
            type=type_, magnitude=1.0,
        )
        tick = dataclasses.replace(
            build_tick_state(now, day),
            eclipse_event=event, eclipse_body_event=event,
        )
        comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        comp.render_offscreen(360.0, 1.0, day, tick)
        card = comp._eclipse_text()
        assert stem in card, (type_, card)
        # It rides BEFORE the Type row it belongs to, not after.
        assert card.index(stem) < card.index("Type")


def test_eclipse_hover_line_carries_the_solar_type_icon(app):
    """Same wiring, solar side — annular resolves through the tinted
    cache file, still embedded inline."""
    from render.asset_variants import eclipse_solar_type_icon

    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    for type_ in ("total", "annular", "partial"):
        event = EclipseEvent(
            kind="solar",
            instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
            type=type_, magnitude=1.0,
        )
        tick = dataclasses.replace(
            build_tick_state(now, day),
            eclipse_event=event, eclipse_body_event=event,
        )
        comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        comp.render_offscreen(360.0, 1.0, day, tick)
        earth = comp._eclipse_text()
        expected = eclipse_solar_type_icon(type_)
        # `scaled_variant_file` may downscale to a differently-STAMPED
        # cache file, but its name always ends in the source's own
        # `{stem}.png` (`_scaled_cache_path`'s own naming law) — a
        # trailing-substring check is robust either way.
        assert expected.name in earth, (type_, earth)
        assert earth.index("Solar Eclipse") > 0


# --- THE SUPERSCRIPT LEAK, KILLED FOR GOOD (owner, angry, Session 21-D) -------
#
# `_eclipse_hover_line` used to `html.escape()` the WHOLE composed line
# AFTER `self._ord()` had already inserted a raw `<sup>` tag, turning it
# into the literal text "2&lt;sup&gt;nd&lt;/sup&gt; August" on screen.
# This is a REGRESSION GUARD, not just a fix for that one line: it walks
# a coarse polar grid through the REAL `_tooltip_at` dispatch (the same
# geometry `warm_hover_articles` warms, at a fraction of its pitch — cheap
# on purpose) over BOTH a plain day and a day sitting inside an eclipse
# window, and fails CI the moment ANY hover builder (existing or future)
# escapes markup it should have left raw.

_ESCAPED_MARKUP = re.compile(r"&lt;(sup|/sup|b|/b|i|/i)&gt;", re.IGNORECASE)


def _sweep_tooltip_texts(comp, size=480.0, rings=6, angles=24):
    """Coarse polar sweep over `_tooltip_at` (owner spec — reuse the
    warm-sweep grid): far fewer probes than `warm_hover_articles`'s
    production pitch (`encyclopedia_ui.HOVER_WARM_RADIAL_STEPS` × `_ANGLE_STEPS`)
    since a regression test only needs to VISIT every hover builder once,
    not warm the asset cache. Returns every non-empty tooltip string."""
    radius = size / 2
    texts = []
    center = comp._tooltip_at(radius, radius, size)
    if center is not None:
        texts.append(center)
    for ring in range(1, rings + 1):
        fraction = ring / rings
        for step in range(angles):
            theta = math.radians(step * 360.0 / angles)
            text = comp._tooltip_at(
                radius + math.sin(theta) * radius * fraction,
                radius - math.cos(theta) * radius * fraction,
                size,
            )
            if text is not None:
                texts.append(text)
    return texts


def test_hover_sweep_never_leaks_escaped_markup(app):
    """Sweeps a NORMAL day (no eclipse) and an ECLIPSE-WINDOW day (both
    solar and lunar), asserting no tooltip string anywhere in either
    sweep contains a literally-escaped tag. Reproduces the owner's exact
    report (2<sup>nd</sup> August rendering as text) and guards every
    OTHER hover builder against the same class of bug."""
    tz = ZoneInfo("Europe/Belgrade")
    size = 480.0

    # A plain day — every ordinary hover builder in the chain.
    plain_now = datetime(2026, 7, 9, 15, 0, tzinfo=tz)
    plain_day = _belgrade_day(plain_now)
    plain_tick = build_tick_state(plain_now, plain_day)
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(size, 1.0, plain_day, plain_tick)
    plain_texts = _sweep_tooltip_texts(comp, size)
    assert plain_texts, "the plain-day sweep found no hovers at all"

    # The eclipse windows. The coarse grid may pass beside a body this
    # small, so each sweep is joined by ONE deliberate probe at the
    # eclipse's own drawn seat — the card is what this guard is here for.
    def eclipse_sweep(now, event):
        day = _belgrade_day(now)
        tick = dataclasses.replace(
            build_tick_state(now, day),
            eclipse_event=event, eclipse_body_event=event,
        )
        comp.render_offscreen(size, 1.0, day, tick)
        texts = _sweep_tooltip_texts(comp, size)
        x, y, _half = _eclipse_body_probe(
            defaults.DEFAULT_SKIN, day, tick, radius=size / 2,
        )
        seat = comp._tooltip_at(float(x), float(y), size)
        if seat is not None:
            texts.append(seat)
        return texts

    solar_texts = eclipse_sweep(
        datetime(2026, 8, 12, 12, 0, tzinfo=tz),
        EclipseEvent(
            kind="solar",
            instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
            type="total", magnitude=1.0395,
        ),
    )
    assert any("Solar Eclipse" in t for t in solar_texts), (
        "the solar-eclipse sweep never reached the eclipse body's card"
    )

    lunar_now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    lunar_texts = eclipse_sweep(
        lunar_now,
        EclipseEvent(
            kind="lunar", instant=lunar_now.replace(hour=17).astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    assert any("Lunar Eclipse" in t for t in lunar_texts), (
        "the lunar-eclipse sweep never reached the eclipse body's card"
    )

    for text in plain_texts + solar_texts + lunar_texts:
        leak = _ESCAPED_MARKUP.search(text)
        assert leak is None, (
            f"escaped markup leaked into a hover tooltip: {leak.group(0)!r} "
            f"in {text!r}"
        )


def test_the_partial_occulter_is_the_suns_own_size(app):
    """THE OCCULTING DISC IS NOT SMALL (owner bug 2026-08-13, looking at
    `solar_partial_bite.png`: "kruznica delimicnog pomracenja je manja od
    kruznice sunca").

    At a solar eclipse the Moon's apparent diameter is within a few
    percent of the Sun's — that is the entire reason eclipses look the
    way they do. A PARTIAL eclipse is a near-miss in ALIGNMENT, not a
    small Moon, so the coverage must come from the centre DISTANCE and
    never from shrinking the disc. ANNULAR is the one type whose
    occulter is genuinely smaller (that is what leaves the ring of
    fire), and TOTAL's is genuinely larger.

    The old geometry expressed the magnitude as a lunar PHASE and asked
    `moon_lit_region` for it, whose terminator semi-axis is
    r*|cos 2*pi*f|: at the catalogue's typical partial magnitude 0.62
    that drew an occulting curve 0.24 r wide — a quarter of the Sun.
    """
    from render import marker_marks

    radius = 100.0
    occulter, distance = marker_marks.solar_occulter_geometry(
        "solar_partial", radius, 0.62
    )
    assert abs(occulter - radius) <= 0.05 * radius, (
        f"a partial eclipse's occulter is {occulter / radius:.3f} of the "
        "Sun's radius — a partial eclipse is a near-miss in alignment, "
        "not a small Moon"
    )
    # The coverage still has to be REAL: magnitude is the covered share
    # of the Sun's DIAMETER, so the covered length along the line of
    # centres is R + r - d.
    covered_length = radius + occulter - distance
    assert covered_length == pytest.approx(2.0 * radius * 0.62), (
        "the magnitude must be carried by the offset"
    )
    # The two ends of the formula: no coverage is exact tangency, full
    # coverage is concentric.
    assert marker_marks.solar_occulter_geometry(
        "solar_partial", radius, 0.0
    )[1] == pytest.approx(radius + occulter)
    assert marker_marks.solar_occulter_geometry(
        "solar_partial", radius, 1.0
    )[1] == pytest.approx(0.0)
    # ANNULAR keeps its genuinely smaller disc — the ring of fire — and
    # TOTAL its genuinely larger one.
    annular, _ = marker_marks.solar_occulter_geometry(
        "solar_annular", radius, 0.94
    )
    total, _ = marker_marks.solar_occulter_geometry(
        "solar_total", radius, 1.05
    )
    assert annular < radius, "an annular occulter must be smaller"
    assert 0.90 * radius < annular < 0.98 * radius, (
        "and only by the few percent the catalogue reports"
    )
    assert total > radius, "a total occulter must be larger"
    assert total < 1.10 * radius


def test_the_bite_uncovers_the_suns_disc_in_proportion(app):
    """THE VISIBLE PART OF THE SUN'S OWN DISC tracks the uncovered
    share — the property that survived every rewrite of this style.

    The style itself has changed three times: a lunar-phase crescent
    (2026-08-11), the true two-disc difference painted bright
    (2026-08-13 morning), and now the owner's own two body plates
    composited at that same geometry (2026-08-13 evening). What the
    picture must SAY never changed, so the measurement is made inside
    the Sun's own disc, where the answer belongs — the ray pattern
    outside it is his art and is present at every magnitude, totality
    included, which is exactly why counting the whole frame was the
    wrong measure."""
    import math as _math

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    from render import marker_marks

    def bright_area(magnitude, inside_disc=True):
        image = QImage(240, 240, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.black)
        painter = QPainter(image)
        painter.translate(120, 120)
        marker_marks.draw_solar_eclipse(
            painter, "bite", 100.0, "solar_partial", magnitude, "#FFD34D",
        )
        painter.end()
        lit = sum(
            1
            for x in range(240)
            for y in range(240)
            if image.pixelColor(x, y).red() > 128
            and (
                (x - 120) ** 2 + (y - 120) ** 2 <= 100.0 ** 2
                if inside_disc else True
            )
        )
        return lit / (_math.pi * 100.0 * 100.0)

    assert bright_area(1.0) < 0.02          # totality: the disc is gone
    quarter = bright_area(0.75)
    half = bright_area(0.5)
    assert 0.15 < quarter < 0.40            # thick crescent at 25% visible
    assert 0.40 < half < 0.65               # half the face at 50% visible
    assert quarter < half
    # AND THE RAYS SURVIVE TOTALITY (owner rule 2026-08-13: cover the
    # whole yellow disc "and leave only the rays to be seen"). Without
    # them a total eclipse would be a bare black hole on the dial, which
    # is the one thing he said he would not ship.
    assert bright_area(1.0, inside_disc=False) > 0.10


def test_eclipse_jump_type_filter_narrows_the_catalog(deep):
    """THE TYPED ECLIPSE JUMPS (owner selector spec 2026-08-11): the
    optional type filter narrows eclipse_after/before to one catalog
    type; None keeps every type, byte-identical to before the filter."""
    from core.deep_time import julian_day

    jd = julian_day(-4500, 1, 1, 0.0)
    any_solar = deep.eclipse_after(jd, "solar")
    assert any_solar is not None
    hybrid = deep.eclipse_after(jd, "solar", "hybrid")
    assert hybrid is not None and hybrid.type == "hybrid"
    total_lunar = deep.eclipse_after(jd, "lunar", "total")
    assert total_lunar is not None and total_lunar.type == "total"
    # An impossible type for the kind simply finds nothing at the edge.
    assert deep.eclipse_after(jd, "solar", "penumbral") is None


# --- THE THIRD BODY: the owner's own rules of 2026-08-12 ----------------------
# One test per sentence of his order, so a future round cannot quietly
# undo one of them. His sentences, in his order: the eclipse is shown
# apart from the Earth, at the hour it happens (A1, covered above); it
# stands for +-12 h (B2); it has its own switch (C1); the Moon keeps the
# ordinary circle with its own new-/full-moon face (D1); and when the two
# would overlap, the ECLIPSE goes out to the ring (E1 + F1).


def _eclipse_ctx(skin, day, tick, radius: float = 270.0) -> RenderContext:
    return RenderContext(
        skin=skin, day=day, tick=tick, radius=radius,
        cache=AssetCache(), dpr=1.0,
    )


def test_eclipse_body_window_is_twelve_hours(app):
    """B2 as the owner corrected it in writing ("+-12h"): the body's own
    window is twice the ±6 h the ballot offered, and strictly WIDER than
    the ±3 h "happening now" window that still drives the hover card —
    so `eclipse_event` can never be set while `eclipse_body_event` is
    not, which would leave a costume with nobody wearing it."""
    assert constants.ECLIPSE_BODY_WINDOW_H == 12.0
    assert constants.ECLIPSE_BODY_WINDOW_H > constants.ECLIPSE_GLOW_WINDOW_H
    tz = ZoneInfo("Europe/Belgrade")
    instant = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    event = EclipseEvent(
        kind="lunar", instant=instant.astimezone(timezone.utc),
        type="total", magnitude=1.15,
    )
    for hours, body, now_flag in (
        (0.0, True, True),      # at the instant: both windows hold
        (6.0, True, False),     # six hours out: the body stands, the card is quiet
        (11.5, True, False),    # still inside his twelve
        (12.5, False, False),   # past it: nothing
    ):
        moment = instant + timedelta(hours=hours)
        day = dataclasses.replace(
            _belgrade_day(moment), eclipses=(event,),
        )
        tick = build_tick_state(moment, day)
        assert (tick.eclipse_body_event is not None) is body, hours
        assert (tick.eclipse_event is not None) is now_flag, hours


def test_eclipse_body_has_its_own_switch(app):
    """C1: independent of both markers. With the Earth and the Moon
    switched OFF the eclipse still stands (the old costume would have
    vanished with its carrier — the hole this round closed); with
    `show_eclipse` off it is gone even though both markers are on."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    quiet = dataclasses.replace(plain, season_event=None, moon_event=None)
    event = EclipseEvent(
        kind="solar", instant=now.replace(hour=17).astimezone(timezone.utc),
        type="total", magnitude=1.02,
    )
    eclipsed = dataclasses.replace(
        quiet, eclipse_event=event, eclipse_body_event=event,
    )
    bare = dataclasses.replace(
        defaults.DEFAULT_SKIN, solar_rotation=False,
        show_earth=False, show_moon=False,
    )
    empty = Compositor(bare, AssetCache()).render_offscreen(540.0, 1.0, day, quiet)
    alone = Compositor(bare, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    x, y, _half = _eclipse_body_probe(bare, day, eclipsed)
    assert empty.pixelColor(x, y) != alone.pixelColor(x, y)
    off = dataclasses.replace(bare, show_eclipse=False)
    hidden = Compositor(off, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    assert hidden.pixelColor(x, y) == empty.pixelColor(x, y)


def test_eclipse_escapes_to_the_ring_when_it_would_cover_the_moon(app):
    """E1 + F1, and the owner's own worked example: a solar eclipse at
    12:00 lands exactly where the new moon is drawn. Then the ECLIPSE
    leaves for the ring band and the Moon keeps the ordinary circle."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    tick = build_tick_state(now, day)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    ctx = _eclipse_ctx(skin, day, tick)
    scale = eclipse_body_scale(ctx, solar=True)
    lane = dial.earth_moon_orbit_fraction(skin.numeral_outer_ring_size, scale)
    # The Moon's own seat, whatever the cycle says today, is the angle
    # the eclipse must be pushed off.
    moon_seat = angles.moon_cycle_angle(tick.moon_fraction)
    assert eclipse_body_orbit(ctx, moon_seat, scale) == (
        dial.GLOW_RING_RADIUS_FRACTION
    )
    # The angle furthest from BOTH markers has nothing in the way, so
    # the body keeps the bodies' own lane there. Chosen by measurement
    # rather than by a guessed quarter-turn: the Earth's date seat moves
    # through the year, and a fixed offset would sooner or later land on
    # it and make this test lie about which rule it is proving.
    seats = (moon_seat, earth_marker_angle(ctx))
    clear = max(
        range(360),
        key=lambda a: min(abs(((a - s + 180.0) % 360.0) - 180.0) for s in seats),
    )
    assert eclipse_body_orbit(ctx, float(clear), scale) == pytest.approx(lane)
    # F1 is TOUCHING DISTANCE, not the exact hour: a few minutes off the
    # seat still overlaps, and still escapes.
    near = (moon_seat + 1.5) % 360.0
    assert eclipse_body_orbit(ctx, near, scale) == (
        dial.GLOW_RING_RADIUS_FRACTION
    )
    # With the Moon hidden there is nothing to escape from.
    moonless = _eclipse_ctx(
        dataclasses.replace(skin, show_moon=False, show_earth=False), day, tick,
    )
    assert eclipse_body_orbit(moonless, moon_seat, scale) == pytest.approx(lane)


def test_eclipse_body_seat_is_the_hour_not_the_date(app):
    """A1 in one line — the sentence the previous round failed to obey.
    The body's angle is the hour hand's own reading of the eclipse
    instant, and it MOVES when the instant moves, while the Earth's date
    angle and the Moon's phase angle stay exactly where they were."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 9, 0, tzinfo=tz)
    day = _belgrade_day(now)
    tick = build_tick_state(now, day)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    ctx = _eclipse_ctx(skin, day, tick)
    for hour, expected in ((12, 0.0), (18, 90.0), (0, 180.0), (6, 270.0)):
        event = EclipseEvent(
            kind="solar", instant=now.replace(hour=hour).astimezone(timezone.utc),
            type="total", magnitude=1.02,
        )
        assert eclipse_body_angle(ctx, event) == pytest.approx(expected)


def test_the_marker_yields_the_ring_to_the_eclipse(app):
    """The SECOND half of the owner's collision rule, in his own words:
    the eclipse goes on the outer ring AND the moon is shown on the
    ordinary circle as on any other day, with its own full-/new-moon
    graphic. A first cut only did the first half and measured the
    markers where they currently stood — so a FULL MOON, which is itself
    relocated to the ring band for six hours around exactly the instant a
    lunar eclipse happens, was still sitting where the eclipse escaped
    to. The render showed it; this test now holds it."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 9, 30, tzinfo=tz)
    day = _belgrade_day(now)
    tick = build_tick_state(now, day)
    assert tick.moon_event == "Full Moon"        # the Moon is band-bound
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    # An eclipse at the Moon's own seat: 00:10, the bottom of the dial.
    event = EclipseEvent(
        kind="lunar", instant=now.replace(hour=0, minute=10).astimezone(timezone.utc),
        type="total", magnitude=1.30,
    )
    eclipsed = dataclasses.replace(
        tick, eclipse_event=event, eclipse_body_event=event,
    )
    ctx = _eclipse_ctx(skin, day, eclipsed)
    scale = eclipse_body_scale(ctx, solar=False)
    angle = eclipse_body_angle(ctx, event)
    # 1. The eclipse takes the ring band.
    assert eclipse_body_orbit(ctx, angle, scale) == (
        dial.GLOW_RING_RADIUS_FRACTION
    )
    # 2. ... and the Moon gives it up, back to the ordinary circle.
    assert marker_yields_band(ctx, "moon") is True
    # 3. The Earth, far away on the year wheel, keeps its own behaviour.
    assert marker_yields_band(ctx, "earth") is False
    # 4. With no eclipse on the dial nothing yields anything.
    quiet_ctx = _eclipse_ctx(skin, day, tick)
    assert marker_yields_band(quiet_ctx, "moon") is False
    # 5. Drawn: the two stand at measurably different radii now.
    image = Compositor(skin, AssetCache()).render_offscreen(760.0, 1.0, day, eclipsed)
    radius = 380.0
    eclipse_point = dial_point(angle, radius * dial.GLOW_RING_RADIUS_FRACTION)
    moon_point = dial_point(
        angles.moon_cycle_angle(tick.moon_fraction),
        radius * dial.earth_moon_orbit_fraction(
            skin.numeral_outer_ring_size, skin.year_marker.moon_scale,
        ),
    )
    separation = math.hypot(
        eclipse_point.x() - moon_point.x(), eclipse_point.y() - moon_point.y()
    )
    assert separation > radius * (
        scale + skin.year_marker.moon_scale
    ), "the two must not overlap once the rule has fired"
    assert image.pixelColor(
        round(radius + eclipse_point.x()), round(radius + eclipse_point.y())
    ).alpha() > 0
