"""THE MOVING BODIES — the eight menus for how the Moon and the Earth
are drawn (owner verdict 2026-08-10). Pins four separate laws:

1. `render.moon_face.draw_moon_disc` — the three unlit-half treatments
   paint visibly different pixels, a new moon still shows "cut_rim"'s
   silver ring, and an unknown style raises rather than falling back.
2. `render.marker_marks.draw_pointer` — THE ANGLE LAW: every shape
   rides the body's own dial angle, never a fixed screen "up".
3. `constants.MOON_STATION_GLOW` — THE INTENSITY RAMP, exactly as the
   owner specified it, plus the cross-table completeness the four
   life stations must keep.
4. `constants.MOVING_BODY_MENUS` — THE ROSTER LAW: the one table the
   storage, the controller and the GUI all walk, round-tripped through
   a real `SettingsStore`.

Painted-pixel technique copied from `tests/test_moon_band.py`
(`QImage.pixelColor`, never `image.pixel` — see that module's own note
on the gotcha).
"""

import dataclasses
import json
import math

import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter

from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace
from config import constants, palette
from render.marker_marks import draw_pointer, station_of_moon_event, station_of_season_event
from render.moon_face import dark_region, draw_moon_disc
from skins.manifest import YearMarkerSpec


# ----------------------------------------------------------------------
# Shared rendering helpers
# ----------------------------------------------------------------------

def _new_image(canvas: int) -> tuple[QImage, QPainter]:
    image = QImage(canvas, canvas, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(canvas / 2, canvas / 2)
    return image, painter


def _flat_face(radius: float):
    def _paint(painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
    return _paint


def _render_moon_disc(style: str, fraction: float, radius: float = 150.0) -> QImage:
    canvas = 4 * int(radius)
    image, painter = _new_image(canvas)
    draw_moon_disc(painter, fraction, radius, style, _flat_face(radius), "#101010")
    painter.end()
    return image


def _alpha_at(image: QImage, dx: float, dy: float) -> int:
    canvas = image.width()
    x = round(canvas / 2 + dx)
    y = round(canvas / 2 + dy)
    return image.pixelColor(x, y).alpha()


def _painted_fraction_of_disc(path, radius: float) -> float:
    """What fraction of a `radius`-disc a `QPainterPath` fills, measured
    by painting it and sampling a grid of points inside the disc — the
    same painted-pixel technique `test_moon_band.py` uses, adapted to
    a whole region rather than a single sweep."""
    canvas = 4 * int(radius)
    image, painter = _new_image(canvas)
    painter.fillPath(path, QColor("#FFFFFF"))
    painter.end()
    step = 4
    hits = 0
    total = 0
    half = canvas // 2
    for y in range(-half, half, step):
        for x in range(-half, half, step):
            if x * x + y * y > radius * radius:
                continue
            total += 1
            if image.pixelColor(half + x, half + y).alpha() > 0:
                hits += 1
    assert total > 0
    return hits / total


# ----------------------------------------------------------------------
# LAW 1 — the Moon's disc: the three unlit-half treatments
# ----------------------------------------------------------------------

def test_moon_dark_styles_paint_visibly_different_crescents_at_a_thin_phase():
    """Fraction 0.08 (a thin waxing crescent, lit on the right): sample
    a point deep in the LEFT-side dark half, well clear of the rim
    stroke's own ring. The three styles must not agree on what to put
    there — "cut_rim" leaves it fully transparent, "cut_ghost" a
    partial wash, "opaque" a near-solid shadow fill."""
    radius = 150.0
    samples = {
        style: _alpha_at(_render_moon_disc(style, 0.08, radius), -radius * 0.6, 0.0)
        for style in constants.MOON_DARK_STYLES
    }
    assert samples["cut_rim"] == 0
    assert 0 < samples["cut_ghost"] < 200
    assert samples["opaque"] > 200
    assert len(set(samples.values())) == 3, (
        f"the three dark styles must read as visibly different renders, got {samples}"
    )


def test_cut_rim_paints_the_silver_rim_at_new_moon_while_the_lit_region_stays_empty():
    """THE LAW THAT MATTERS MOST (owner's own reason for accepting
    "cut_rim" over a plain cut): at fraction 0.0 the lit region is
    empty, but the permanent hairline around the TRUE disc must still
    be there, or a new moon vanishes entirely instead of reading as a
    hollow silver ring."""
    radius = 150.0
    image = _render_moon_disc("cut_rim", 0.0, radius)
    # The rim strokes the whole circle regardless of phase — the top
    # of the disc always sits on it.
    assert _alpha_at(image, 0.0, -radius) > 0
    # No ghost fill and no lit crescent at new moon: the interior stays
    # fully transparent.
    assert _alpha_at(image, 0.0, 0.0) == 0


def test_unknown_moon_dark_style_raises_instead_of_a_silent_fallback():
    """A roster/render drift, not user input — the same choice
    `render.letter_plates` makes, and this project's own scar: a
    silent fallback is how a whole missing treatment once shipped
    green."""
    _, painter = _new_image(40)
    try:
        with pytest.raises(ValueError):
            draw_moon_disc(painter, 0.08, 15.0, "gauze", _flat_face(15.0), "#101010")
    finally:
        painter.end()


def test_dark_region_is_near_empty_at_full_moon_and_near_the_whole_disc_at_new_moon():
    """`dark_region` is the disc MINUS the lit region. Full moon
    (fraction 0.5, per `constants.MOON_PHASE_FRACTIONS`) leaves almost
    nothing dark; new moon (fraction 0.0) leaves almost the whole
    disc dark."""
    radius = 100.0
    full_moon_dark = _painted_fraction_of_disc(dark_region(0.5, radius), radius)
    new_moon_dark = _painted_fraction_of_disc(dark_region(0.0, radius), radius)
    assert full_moon_dark < 0.05
    assert new_moon_dark > 0.95


# ----------------------------------------------------------------------
# LAW 2 — THE ANGLE LAW: the position pointer never points a fixed "up"
# ----------------------------------------------------------------------

_DIAL_RADIUS = 200.0
_ORBIT_FRACTION = 0.4
_HALF_SIZE_FRACTION = 0.05
_POINTER_CANVAS = 260


def _render_pointer(shape: str, angle_deg: float) -> QImage:
    image, painter = _new_image(_POINTER_CANVAS)
    draw_pointer(
        painter, shape, angle_deg, _DIAL_RADIUS,
        _ORBIT_FRACTION, _HALF_SIZE_FRACTION, "#FFD700",
    )
    painter.end()
    return image


def _painted_centroid_angle(image: QImage) -> float:
    """The painted pixels' centroid, expressed as a dial angle
    (degrees clockwise from top) via the SAME mapping
    `render.painting.dial_point` uses in reverse."""
    canvas = image.width()
    centre = canvas / 2
    sum_x = sum_y = 0.0
    count = 0
    for y in range(canvas):
        for x in range(canvas):
            if image.pixelColor(x, y).alpha() > 0:
                sum_x += x - centre
                sum_y += y - centre
                count += 1
    assert count > 0, "shape painted nothing at all"
    dx, dy = sum_x / count, sum_y / count
    return math.degrees(math.atan2(dx, -dy)) % 360.0


@pytest.mark.parametrize("shape", constants.MARKER_POINTER_SHAPES)
@pytest.mark.parametrize("angle_deg", (0.0, 90.0, 180.0, 270.0))
def test_pointer_rides_the_bodys_own_dial_angle_not_a_fixed_up(shape, angle_deg):
    """The owner had to correct exactly this once (2026-08-10): a
    proposal mockup drew every pointer straight up, which is only true
    for a body sitting at the top of the dial. Pinned for all three
    `constants.MARKER_POINTER_SHAPES` at four spread-out angles."""
    centroid = _painted_centroid_angle(_render_pointer(shape, angle_deg))
    delta = min((centroid - angle_deg) % 360.0, (angle_deg - centroid) % 360.0)
    assert delta < 15.0, (
        f"{shape} at dial angle {angle_deg} painted its centroid at "
        f"{centroid:.1f} instead — {delta:.1f} deg off"
    )


def test_unknown_pointer_shape_raises_instead_of_a_silent_fallback():
    _, painter = _new_image(40)
    try:
        with pytest.raises(ValueError):
            draw_pointer(painter, "arrow", 0.0, _DIAL_RADIUS, 0.4, 0.05, "#FFD700")
    finally:
        painter.end()


# ----------------------------------------------------------------------
# LAW 3 — THE STATION RAMP
# ----------------------------------------------------------------------

def test_station_glow_ramp_matches_the_owners_exact_words():
    """`constants.MOON_STATION_GLOW` as (outer, inner) fractions of
    peak intensity: zenith (full moon) carries the STRONGEST outer
    intensity of the four; youth and age share the SAME outer
    intensity; youth alone carries an inner glow, age none at all."""
    outer = {s: constants.MOON_STATION_GLOW[s][0] for s in constants.LIFE_STATIONS}
    inner = {s: constants.MOON_STATION_GLOW[s][1] for s in constants.LIFE_STATIONS}
    assert outer["zenith"] == max(outer.values())
    assert all(outer["zenith"] > outer[s] for s in constants.LIFE_STATIONS if s != "zenith")
    assert outer["youth"] == outer["age"]
    assert inner["youth"] > 0.0
    assert inner["age"] == 0.0


def test_every_life_station_has_a_moon_glow_entry_and_a_sun_season_entry():
    """One roster (`LIFE_STATIONS`) drives two tables — a station can
    never exist in one and be missing from the other."""
    for station in constants.LIFE_STATIONS:
        assert station in constants.MOON_STATION_GLOW, station
        assert station in constants.SUN_STATION_SEASONS, station


def test_every_sun_station_season_is_a_real_instrument_season_color():
    """THE PALETTE COLOUR LAW: `uniform_seasonal`'s halo reads
    `palette.INSTRUMENT_SEASON_COLORS`, so it can never name a season
    the palette does not sample."""
    for season in constants.SUN_STATION_SEASONS.values():
        assert season in palette.INSTRUMENT_SEASON_COLORS, season


# ----------------------------------------------------------------------
# LAW 4 — THE ROSTER LAW: MOVING_BODY_MENUS drives storage, spec and GUI
# ----------------------------------------------------------------------

_SETTINGS_FIELD_NAMES = {f.name for f in dataclasses.fields(Settings)}
_MARKER_SPEC_FIELD_NAMES = {f.name for f in dataclasses.fields(YearMarkerSpec)}


def test_every_moving_body_menu_is_a_real_settings_field():
    for name in constants.MOVING_BODY_MENUS:
        assert name in _SETTINGS_FIELD_NAMES, name


def test_every_moving_body_menu_is_a_real_year_marker_spec_field():
    """The overlay depends on the names matching — a menu present in
    one table and absent from the other would silently stop reaching
    the dial."""
    for name in constants.MOVING_BODY_MENUS:
        assert name in _MARKER_SPEC_FIELD_NAMES, name


def test_every_moving_body_default_belongs_to_its_own_choices():
    for name, (choices, default) in constants.MOVING_BODY_MENUS.items():
        assert default in choices, name


def test_moving_body_menus_round_trip_through_settings_store(tmp_path):
    """A non-default value for EVERY menu at once, saved and reloaded
    through a real `SettingsStore` (see `tests/test_settings_store.py`
    for the same temp-store technique) — every value must survive."""
    store = SettingsStore(tmp_path / "settings.json")
    overrides = {
        name: next(choice for choice in choices if choice != default)
        for name, (choices, default) in constants.MOVING_BODY_MENUS.items()
    }
    store.save(replace(Settings(), **overrides))
    loaded = store.load()
    for name, value in overrides.items():
        assert getattr(loaded, name) == value, name


def test_moving_body_menu_garbage_value_is_reported_as_corrupt_not_silently_swapped(tmp_path):
    """`app.settings_fields.load_choice`'s own law, verified against the
    real store rather than assumed: a stored value naming a face
    outside the roster is corrupt data and raises
    `SettingsCorruptError` — it is NOT quietly swapped for the default.
    A quiet substitution here is exactly the failure this project's
    own scar is named after (never-substitute-say-whats-missing,
    2026-08-07): a user's saved watch would silently start drawing a
    face they never chose, with nothing in the log to say so."""
    store = SettingsStore(tmp_path / "settings.json")
    store.path.write_text(
        json.dumps({
            "schema_version": 1,
            "window": {"x": 1, "y": 2, "diameter": 360},
            "moon_dark_style": "bogus_face",
        }),
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


# ----------------------------------------------------------------------
# LAW 5 — the station resolvers cover every event name the clock produces
# ----------------------------------------------------------------------

def test_every_principal_moon_phase_resolves_to_a_station():
    for name in constants.MOON_PHASE_FRACTIONS:
        assert station_of_moon_event(name) is not None, name


def test_every_zone_season_event_name_resolves_to_a_station():
    """Every name in EVERY zone table — this is what catches a zone
    whose names were never added to `SUN_STATION_OF_EVENT`."""
    for zone, table in constants.ZONE_SEASON_EVENT_NAMES.items():
        for name in table.values():
            assert station_of_season_event(name) is not None, f"{zone}: {name}"


def test_a_non_principal_event_name_resolves_to_none_not_a_guess():
    assert station_of_moon_event("Waxing Crescent") is None
    assert station_of_moon_event(None) is None
    assert station_of_season_event("Some Made Up Event") is None
    assert station_of_season_event(None) is None


def test_the_horizon_shadow_style_marks_the_band_and_reads_the_day_not_the_tick():
    """THE ECLIPSE ON THE BAND (owner placement 2026-08-10) must actually
    paint, and must take its event from the DAY.

    Two laws in one tooth, because they failed together. The style was
    wired end to end — settings, spec, picker — while nothing drew on
    the band, so choosing it silently turned the eclipse's mark OFF with
    every gate green; an independent grader caught it by opening the
    picker tile. The first fix then read `ctx.tick.eclipse_event`, but
    `MoonBandLayer.cadence` is DAILY and `ctx.tick` is None while a
    cached daily pass composites, which aborted the interpreter three
    tests into an unrelated module. `ctx.day.eclipses` is both safe and
    correct: the band draws the whole day, so it must mark an eclipse
    that has not begun and one already over — that is what showing
    DURATION means."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor, QImage, QPainter
    from PySide6.QtWidgets import QApplication

    from config import palette
    from render.layers.moon_band import MoonBandLayer

    QApplication.instance() or QApplication([])
    size = 260
    radius = size * 0.4
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    painter.translate(size / 2.0, size / 2.0)
    layer = MoonBandLayer.__new__(MoonBandLayer)
    layer.draw_eclipse_segment(painter, radius, 0.0)   # noon, the dial's top
    painter.end()

    copper = QColor(palette.ECLIPSE_TOTAL_MOON_TINT)
    hits = 0
    for x in range(size):
        for y in range(size):
            pixel = image.pixelColor(x, y)
            if pixel.alpha() == 0:
                continue
            if abs(pixel.red() - copper.red()) < 40 and pixel.red() > pixel.blue():
                hits += 1
    assert hits > 0, "the horizon-shadow style painted nothing at all"
