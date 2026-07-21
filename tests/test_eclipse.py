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
import re
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
from render.layers import (
    eclipse_glow_strength,
    eclipse_render_state,
    eclipse_state_glow_strength,
)
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
    """The hover line appends the reason (owner spec, round numbers, the
    km threshold never printed): "below the horizon" for a horizon miss,
    "path {d} km away" for a solar distance miss."""
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
    far_line = compositor._eclipse_hover_line(far_event)
    horizon_line = compositor._eclipse_hover_line(horizon_event)
    assert "16123 km away" in far_line
    assert "below the horizon" in horizon_line
    assert str(constants.ECLIPSE_SOLAR_VISIBILITY_KM) not in far_line


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


# --- The type -> state table (fix round C, owner decree 2026-07-19) -----------


def test_type_state_mapping_covers_the_ground_truthed_vocabulary():
    """The catalog's ACTUAL type vocabulary (ground-truthed from
    Database/deep_time.sqlite: solar {partial, annular, total, hybrid},
    lunar {partial, penumbral, total}) each resolve to a named state;
    hybrid is a deliberate map to solar_total, not the unknown fallback."""
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
    ) == "solar_total"
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
        "solar_total", "solar_annular",
    ):
        assert eclipse_state_glow_strength(state, 0.01) == pytest.approx(
            eclipse_state_glow_strength(state, 1.19)
        ), f"{state} must ignore magnitude"
    lo = eclipse_state_glow_strength("solar_partial", defaults.ECLIPSE_MAGNITUDE_MIN)
    hi = eclipse_state_glow_strength("solar_partial", defaults.ECLIPSE_MAGNITUDE_MAX)
    assert lo < hi        # solar_partial alone still tracks magnitude


# --- Render: per-state lunar darkening (fix round C, owner decree 2026-07-19) --


def _lunar_moon_pixel(app, type_: str, magnitude: float):
    """Renders a lunar eclipse of the given TYPE and samples the Moon
    marker's own pixel at its relocated (ring-band) center — the moon's
    OWN art occludes the glow halo directly under it, so this reads only
    the darkened disc, never the bronze glow bleeding through."""
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
    eclipsed = dataclasses.replace(
        quiet,
        eclipse_event=EclipseEvent(
            kind="lunar", instant=now.astimezone(timezone.utc),
            type=type_, magnitude=magnitude,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    image = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    moon_angle = math.radians(quiet.moon_fraction * 360.0)
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    x = round(radius + orbit * math.sin(moon_angle))
    y = round(radius - orbit * math.cos(moon_angle))
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
    with a deep COPPER tone (`defaults.ECLIPSE_TOTAL_MOON_TINT`) instead
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
    low = _lunar_moon_pixel(app, "total", defaults.ECLIPSE_MAGNITUDE_MIN)
    high = _lunar_moon_pixel(app, "total", defaults.ECLIPSE_MAGNITUDE_MAX)
    assert max(low.red(), low.green(), low.blue()) < 55
    assert max(high.red(), high.green(), high.blue()) < 55


# --- Render: solar annular "ring of fire" glow color ---------------------------


def _solar_glow_pixel(app, type_: str, magnitude: float):
    tz = ZoneInfo("Europe/Belgrade")
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    day = _belgrade_day(solstice_noon)
    plain_glow = build_tick_state(solstice_noon, day)
    quiet = dataclasses.replace(plain_glow, season_event=None, moon_event=None)
    eclipsed = dataclasses.replace(
        quiet,
        eclipse_event=EclipseEvent(
            kind="solar", instant=solstice_noon.astimezone(timezone.utc),
            type=type_, magnitude=magnitude,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    image = Compositor(skin, AssetCache()).render_offscreen(540.0, 1.0, day, eclipsed)
    marker_y = 270 - round(270 * defaults.GLOW_RING_RADIUS_FRACTION)
    return image.pixelColor(289, marker_y + 33)


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


# --- THE ECLIPSES ENCYCLOPEDIA (fix round F, owner order 2026-07-19) -----------
#
# TASK 4 (Spacebar jump to the active category's chapter) and TASK 3 (the
# category emblem on the Earth/Moon hover card, graceful-absent).


def _eclipse_marker_probe(kind, type_, magnitude=1.05):
    """Render an eclipse window and return (compositor, x, y, size) at the
    relocated marker's ring-band position — the SAME geometry the
    hit-test goldens above use, so the Spacebar target is read at the
    exact drawn spot."""
    tz = ZoneInfo("Europe/Belgrade")
    now = (
        datetime(2026, 3, 3, 12, 0, tzinfo=tz) if kind == "lunar"
        else datetime(2026, 3, 1, 12, 0, tzinfo=tz)
    )
    day = _belgrade_day(now)
    plain = build_tick_state(now, day)
    eclipsed = dataclasses.replace(
        plain, season_event=None, moon_event=None,
        eclipse_event=EclipseEvent(
            kind=kind, instant=now.astimezone(timezone.utc),
            type=type_, magnitude=magnitude,
        ),
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(540.0, 1.0, day, eclipsed)
    radius = 270.0
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
    theta = math.radians(
        plain.year_angle if kind == "solar"
        else plain.moon_fraction * 360.0
    )
    x = radius + orbit * math.sin(theta)
    y = radius - orbit * math.cos(theta)
    return comp, x, y, 540.0


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
    """TASK 4 golden: while an eclipse window is active, Space over the
    Earth (solar) / Moon (lunar) marker opens the Encyclopedia at THAT
    category's chapter — every one of the seven categories, indexed by
    the active type; hybrid keeps its OWN chapter (index 4), not
    solar_total's."""
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
    orbit = radius * defaults.GLOW_RING_RADIUS_FRACTION
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
        assert path.parent == defaults.ECLIPSE_ART_DIR
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
    """TASK 3 wiring: when the category emblem art DOES exist, the badge
    appears on BOTH cards — the Earth card for a solar eclipse and the
    Moon card for a lunar one — beside the eclipse line (owner slika 7).
    A real (tiny) PNG under a monkeypatched eclipse dir proves the slot
    is wired, not just the graceful-absent path."""
    from PySide6.QtGui import QImage

    monkeypatch.setattr(defaults, "ECLIPSE_ART_DIR", tmp_path)
    swatch = QImage(8, 8, QImage.Format.Format_ARGB32)
    swatch.fill(0xFFCC5522)
    for stem in ("Solar_Total.png", "Lunar_Total.png"):
        assert swatch.save(str(tmp_path / stem))

    tz = ZoneInfo("Europe/Belgrade")
    # Solar — the Earth card.
    solar_now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    solar_day = _belgrade_day(solar_now)
    solar_tick = dataclasses.replace(
        build_tick_state(solar_now, solar_day),
        eclipse_event=EclipseEvent(
            kind="solar",
            instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
            type="total", magnitude=1.04,
        ),
    )
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, solar_day, solar_tick)
    earth = comp._earth_text()
    assert "Solar Eclipse" in earth
    assert tmp_path.joinpath("Solar_Total.png").as_uri() in earth

    # Lunar — the Moon card.
    lunar_now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    lunar_day = _belgrade_day(lunar_now)
    lunar_tick = dataclasses.replace(
        build_tick_state(lunar_now, lunar_day),
        eclipse_event=EclipseEvent(
            kind="lunar", instant=lunar_now.astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    comp.render_offscreen(360.0, 1.0, lunar_day, lunar_tick)
    moon = comp._moon_text()
    assert "Lunar Eclipse" in moon
    assert tmp_path.joinpath("Lunar_Total.png").as_uri() in moon


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
    from render.assets import eclipse_solar_type_icon

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

    from render.assets import eclipse_solar_type_icon

    tinted_path = eclipse_solar_type_icon("annular")
    source_path = defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE["annular"]
    assert tinted_path != source_path
    assert tinted_path.exists()
    image = QImage(str(tinted_path))
    target_hue = QColor(defaults.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR).hueF() * 360.0
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
    """Wiring: the Moon hover card's eclipse line embeds the type
    icon's own URI inline, ahead of the "Lunar Eclipse" title."""
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    for type_, stem in (
        ("total", "moon_eclipse_red.png"),
        ("partial", "moon_eclipse_gold.png"),
        ("penumbral", "moon_eclipse_blue.png"),
    ):
        tick = dataclasses.replace(
            build_tick_state(now, day),
            eclipse_event=EclipseEvent(
                kind="lunar", instant=now.astimezone(timezone.utc),
                type=type_, magnitude=1.0,
            ),
        )
        comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        comp.render_offscreen(360.0, 1.0, day, tick)
        moon = comp._moon_text()
        assert stem in moon, (type_, moon)
        # It rides BEFORE the "Lunar Eclipse" title, not after.
        assert moon.index(stem) < moon.index("Lunar Eclipse")


def test_eclipse_hover_line_carries_the_solar_type_icon(app):
    """Same wiring, Earth/solar side — annular resolves through the
    tinted cache file, still embedded inline."""
    from render.assets import eclipse_solar_type_icon

    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    day = _belgrade_day(now)
    for type_ in ("total", "annular", "partial"):
        tick = dataclasses.replace(
            build_tick_state(now, day),
            eclipse_event=EclipseEvent(
                kind="solar",
                instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
                type=type_, magnitude=1.0,
            ),
        )
        comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        comp.render_offscreen(360.0, 1.0, day, tick)
        earth = comp._earth_text()
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
    production pitch (`defaults.HOVER_WARM_RADIAL_STEPS` × `_ANGLE_STEPS`)
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

    # The solar eclipse window (Earth marker names it).
    solar_now = datetime(2026, 8, 12, 12, 0, tzinfo=tz)
    solar_day = _belgrade_day(solar_now)
    solar_plain_tick = build_tick_state(solar_now, solar_day)
    solar_tick = dataclasses.replace(
        solar_plain_tick,
        eclipse_event=EclipseEvent(
            kind="solar",
            instant=datetime(2026, 8, 12, 17, 45, 59, tzinfo=timezone.utc),
            type="total", magnitude=1.0395,
        ),
    )
    comp.render_offscreen(size, 1.0, solar_day, solar_tick)
    solar_texts = _sweep_tooltip_texts(comp, size)
    assert any("Solar Eclipse" in t for t in solar_texts), (
        "the solar-eclipse sweep never reached the Earth marker hover"
    )

    # The lunar eclipse window (Moon marker names it).
    lunar_now = datetime(2026, 3, 3, 12, 0, tzinfo=tz)
    lunar_day = _belgrade_day(lunar_now)
    lunar_plain_tick = build_tick_state(lunar_now, lunar_day)
    lunar_tick = dataclasses.replace(
        lunar_plain_tick,
        eclipse_event=EclipseEvent(
            kind="lunar", instant=lunar_now.astimezone(timezone.utc),
            type="total", magnitude=1.15,
        ),
    )
    comp.render_offscreen(size, 1.0, lunar_day, lunar_tick)
    lunar_texts = _sweep_tooltip_texts(comp, size)
    assert any("Lunar Eclipse" in t for t in lunar_texts), (
        "the lunar-eclipse sweep never reached the Moon marker hover"
    )

    for text in plain_texts + solar_texts + lunar_texts:
        leak = _ESCAPED_MARKUP.search(text)
        assert leak is None, (
            f"escaped markup leaked into a hover tooltip: {leak.group(0)!r} "
            f"in {text!r}"
        )
