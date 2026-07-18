"""THE ARCHETYPE MODE golden tests (owner sealed package 2026-07-16).

Pins the sealed behaviors: the render-level override (slots and the
weekday model OFF without touching settings), the hour-space lighting
math per pointer, the center table, the placeholder fallback (the
figure's NAME while art is a 1×1 stand-in), the reveal gesture hiding
the hands, the graceful two-row article path, the encyclopedia
mapping, and the menu gating."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from config import archetypes, constants, defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    archetype_active,
    archetype_art_ready,
    archetype_center_lit,
    archetype_lit_index,
    dial_point,
    draw_archetype_figure,
    enabled_slots,
    slot_layout,
    weekday_classic_slot,
    RenderContext,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


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


def _archetype_skin(pointer: str, style: str = "paint", **kw):
    return dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer=pointer, palette_style=style,
        archetype_mode=True, solar_rotation=False, **kw,
    )


def _hour_angle(hours: int, minutes: int) -> float:
    """The hour hand's dial angle at a wall-clock time (noon = 0°)."""
    return ((hours * 60 + minutes) / (24 * 60) * 360.0 + 180.0) % 360.0


# --- The grid and the tables ---------------------------------------------------


def test_grid_covers_the_eight_archetypes():
    """CANON (owner 2026-07-17): EIGHT archetypes — the Seasons split
    into PAINT (the Four Temperaments) and LIGHT (the Tetramorph); Aurora
    and the Calendar have none."""
    assert set(archetypes.ARCHETYPE_GRID.values()) == {
        "trinity_paint", "trinity_light", "seasons_paint", "seasons_light",
        "prism_paint", "prism_light", "compass_paint", "compass_light",
    }
    assert archetypes.grid_key("cross", "paint") == "seasons_paint"
    assert archetypes.grid_key("cross", "light") == "seasons_light"
    assert archetypes.grid_key("aurora", "paint") is None
    assert archetypes.grid_key("calendar", "light") is None
    for pointer in ("trio", "cross", "hexa", "octa"):
        assert archetypes.has_archetype(pointer)
    for pointer in ("aurora", "calendar"):
        assert not archetypes.has_archetype(pointer)


def test_figure_order_matches_the_hour_spaces():
    """The figures tuple index IS the hour-space index: angles run
    k·(360/N) in order, and the entity keys are unique per set."""
    pointer_of = {key: pointer for (pointer, _), key
                  in archetypes.ARCHETYPE_GRID.items()}
    for key in set(archetypes.ARCHETYPE_GRID.values()):
        figs = archetypes.figures(key)
        arms = constants.POINTER_POINTS[pointer_of[key]]
        assert len(figs) == arms
        step = 360.0 / arms
        assert [fig["angle"] for fig in figs] == [
            k * step for k in range(arms)
        ]
        entities = [fig["entity"] for fig in figs]
        assert len(set(entities)) == len(entities)


def test_center_table_is_the_sealed_one():
    """Owner seal 2026-07-16: Eye (Trinity paint), Hearth (Trinity
    light), Seal (Prism paint), Union (Prism light), Throne (Seasons,
    both wheels), Compass — none."""
    assert archetypes.center("trinity_paint")["file"].name == "Providence_Eye.png"
    assert archetypes.center("trinity_light")["file"].name == "Hearth.png"
    assert archetypes.center("prism_paint")["file"].name == "Seal.png"
    assert archetypes.center("prism_light")["file"].name == "Union.png"
    assert archetypes.center("seasons_paint")["file"].name == "Throne.png"
    assert archetypes.center("seasons_light")["file"].name == "Throne.png"
    assert archetypes.center("compass_paint") is None
    assert archetypes.center("compass_light") is None


def test_reused_scale_glass_is_real_art(app, tmp_path):
    """Prism paint's Lucifer and Judas REUSE the owner's Scale glass
    (canon: no new art for those two seats) — the files are on disk and
    pass the readiness check. The placeholder rejection is pinned on a
    SYNTHETIC 1×1 (the shipping placeholders are being replaced by real
    art file by file — owner drop 2026-07-18 — so no asset stays a
    placeholder forever)."""
    figs = archetypes.figures("prism_paint")
    lucifer, judas = figs[2], figs[4]
    assert lucifer["file"].name == "Lucifer_Triangle.png"
    assert judas["file"].name == "Judas_Triangle.png"
    assert archetype_art_ready(lucifer["file"])
    assert archetype_art_ready(judas["file"])
    # A 1×1 stand-in is NOT ready — the renderer falls back to the name.
    placeholder = tmp_path / "stand_in.png"
    QImage(1, 1, QImage.Format.Format_ARGB32).save(str(placeholder))
    assert not archetype_art_ready(placeholder)


def test_family_and_temperament_seatings():
    """CANON seatings: the Family triangle (Child top, Mother 20h,
    Father 4h) and the color-fixed temperaments (Choleric summer
    yellow top, Sanguine spring green left)."""
    family = archetypes.figures("trinity_light")
    assert [fig["name"] for fig in family] == [
        "The Child", "The Mother", "The Father",
    ]
    seasons = archetypes.figures("seasons_paint")
    assert [fig["name"] for fig in seasons] == [
        "Choleric", "Melancholic", "Phlegmatic", "Sanguine",
    ]
    # The LIGHT wheel seats the Tetramorph on the same season arms.
    tetramorph = archetypes.figures("seasons_light")
    assert [fig["name"] for fig in tetramorph] == [
        "The Lion", "The Ox", "The Eagle", "The Man",
    ]


# --- The render-level override --------------------------------------------------


def test_mode_overrides_slots_without_mutating_settings():
    """The sealed package: when the mode is ON the weekday model and
    ALL THREE SLOTS are off for rendering and hit-testing — but the
    OVERRIDE lives at the render level (enabled_slots), so neither the
    settings nor the skin's own slot switches are mutated and toggling
    back restores everything."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    settings = replace(
        Settings(), pointer="hexa", show_weekday=True,
        show_octa_slot=True, octa_slot="zodiac", archetype_mode=True,
    )
    skin = apply_display_settings(defaults.DEFAULT_SKIN, settings)
    assert skin.archetype_mode and archetype_active(skin)
    assert enabled_slots(skin) == ()
    assert slot_layout(skin) == {}
    assert weekday_classic_slot(skin) is None
    # Nothing was mutated — the mode only OVERRIDES.
    assert settings.show_weekday and settings.show_octa_slot
    assert skin.show_weekday and skin.show_octa_slot
    # Toggling back restores the user's layout untouched — the hexa
    # two-slot case seats the pair on the 4h/20h arms.
    restored = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(settings, archetype_mode=False)
    )
    assert slot_layout(restored) == {
        1: constants.SLOT_SEAT_LEFT_ARM_ANGLE,
        2: constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
    }
    # Aurora has no archetype — the mode is inert there.
    aurora = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(settings, pointer="aurora")
    )
    assert not archetype_active(aurora)
    assert enabled_slots(aurora) != ()
    # No pointer element, no diamonds — no archetype either.
    bare = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(settings, show_pointer=False)
    )
    assert not archetype_active(bare)


def test_mode_returns_the_big_seconds_hand():
    """A seated small-seconds slot silences the big hand — but the
    mode overrides the slots, so the big hand returns while it runs."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    seated = replace(Settings(), weekday_slot="seconds")
    assert not apply_display_settings(
        defaults.DEFAULT_SKIN, seated
    ).show_seconds
    assert apply_display_settings(
        defaults.DEFAULT_SKIN, replace(seated, archetype_mode=True)
    ).show_seconds


# --- The hour-space lighting -----------------------------------------------------


def test_hour_space_lighting_boundaries():
    """The circle divides by arms — trio 3×8h, cross 4×6h, hexa 6×4h,
    octa 8×3h — every space CENTERED on its arm (the arm tip is the
    center of its hue). Pinned at the exact boundaries."""
    lit = archetype_lit_index
    # TRIO: The One 8–16h (top), the Devil 16–24h, Jesus 0–8h.
    assert lit("trio", _hour_angle(8, 1)) == 0
    assert lit("trio", _hour_angle(15, 59)) == 0
    assert lit("trio", _hour_angle(16, 1)) == 1
    assert lit("trio", _hour_angle(23, 59)) == 1
    assert lit("trio", _hour_angle(0, 1)) == 2
    assert lit("trio", _hour_angle(7, 59)) == 2
    assert lit("trio", _hour_angle(14, 30)) == 0
    # CROSS: Choleric 9–15h, Melancholic 15–21h, Phlegmatic 21–3h,
    # Sanguine 3–9h.
    assert lit("cross", _hour_angle(9, 1)) == 0
    assert lit("cross", _hour_angle(14, 59)) == 0
    assert lit("cross", _hour_angle(15, 1)) == 1
    assert lit("cross", _hour_angle(21, 1)) == 2
    assert lit("cross", _hour_angle(2, 59)) == 2
    assert lit("cross", _hour_angle(3, 1)) == 3
    # HEXA: 4h spaces — The One/Gratitude 10–14h, then clockwise.
    assert lit("hexa", _hour_angle(10, 1)) == 0
    assert lit("hexa", _hour_angle(13, 59)) == 0
    assert lit("hexa", _hour_angle(14, 1)) == 1
    assert lit("hexa", _hour_angle(9, 59)) == 5
    assert lit("hexa", _hour_angle(14, 30)) == 1
    # OCTA: 3h spaces — the King 10:30–13:30, then clockwise.
    assert lit("octa", _hour_angle(10, 31)) == 0
    assert lit("octa", _hour_angle(13, 29)) == 0
    assert lit("octa", _hour_angle(13, 31)) == 1
    assert lit("octa", _hour_angle(22, 29)) == 3
    assert lit("octa", _hour_angle(22, 31)) == 4
    assert lit("octa", _hour_angle(14, 30)) == 1
    # The spaces ride the DRAWN arms: under solar rotation a boundary
    # case shifts exactly with the diamonds — the 16:00 boundary moves
    # clockwise with a positive rotation, so 16:01 falls back to The
    # One; a negative rotation hands it to the Devil earlier.
    assert lit("trio", _hour_angle(16, 1), rotation=1.0) == 0
    assert lit("trio", _hour_angle(16, 1), rotation=-1.0) == 1


# --- The placeholder fallback ----------------------------------------------------


def _png(tmp_path, name: str, side: int, color=Qt.GlobalColor.red):
    image = QImage(side, side, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(color)
    path = tmp_path / name
    image.save(str(path))
    return path


def _rect_png(tmp_path, name: str, width: int, height: int):
    """A non-square synthetic PNG (art-arrival-proof) for the two-type
    classification tests — width/height picks CIRCLE (wide/square) vs
    PORTRAIT (tall) without depending on the owner's real art landing."""
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.red)
    path = tmp_path / name
    image.save(str(path))
    return path


def test_art_readiness_rejects_placeholders(app, tmp_path):
    """archetype_art_ready: a committed 1×1 placeholder (and a missing
    file) reads NOT ready; real art reads ready."""
    assert not archetype_art_ready(_png(tmp_path, "tiny.png", 1))
    assert archetype_art_ready(_png(tmp_path, "real.png", 64))
    assert not archetype_art_ready(tmp_path / "never_written.png")


def test_placeholder_falls_back_to_the_name(app, tmp_path):
    """The graceful fallback (WORKPLAN missing-art rule): a 1×1 figure
    draws the NAME in the outlined label style instead of a stretched
    pixel; real art draws the image."""
    skin = _archetype_skin("trio")
    ctx = RenderContext(
        skin=skin, day=SimpleNamespace(), tick=None,
        radius=100.0, cache=AssetCache(), dpr=1.0,
    )

    def render(path):
        image = QImage(200, 200, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(100, 100)
        fig = {"file": path, "name": "Testling", "row2": "-",
               "entity": "t", "enc": None}
        draw_archetype_figure(
            painter, ctx, fig, QPointF(0, 0), 80.0, 40.0, 1.0, named=False,
        )
        painter.end()
        return image

    def white_pixels(image):
        return sum(
            1
            for x in range(60, 140)
            for y in range(80, 120)
            if image.pixelColor(x, y).alpha() > 200
            and min(
                image.pixelColor(x, y).red(),
                image.pixelColor(x, y).green(),
                image.pixelColor(x, y).blue(),
            ) > 200
        )

    fallback = render(_png(tmp_path, "tiny.png", 1))
    assert white_pixels(fallback) > 0            # the NAME label
    real = render(_png(tmp_path, "real.png", 64))
    assert white_pixels(real) == 0               # the red art, no label
    assert real.pixelColor(100, 100).red() > 200


# --- The reveal gesture hides the hands -------------------------------------------


def test_reveal_hides_the_hands(app, monkeypatch):
    """The repurposed Omega double-click (owner seal 2026-07-16): while
    the reveal runs the HANDS are not drawn — the compositor SKIPS
    HandLayer entirely. Pinned semantically on the layer skip (the old
    pixel probe band broke the day the owner's real center glass landed
    over it, 2026-07-18): normal frame paints hands, reveal frame paints
    none, toggle-off paints them again."""
    from render.layers import HandLayer

    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    skin = _archetype_skin("trio", show_weekday_names=False)
    comp = Compositor(skin, AssetCache())
    painted = []
    monkeypatch.setattr(
        HandLayer, "paint",
        lambda self, painter, ctx: painted.append(type(self).__name__),
    )
    comp.render_offscreen(360.0, 1.0, day, tick)
    assert painted                            # hands drawn normally
    painted.clear()
    assert comp.trigger_reveal_week() is True
    comp.render_offscreen(360.0, 1.0, day, tick)
    assert not painted                        # reveal: HandLayer skipped
    assert comp.trigger_reveal_week() is False    # toggle-off
    comp.render_offscreen(360.0, 1.0, day, tick)
    assert painted                            # hands are back


# --- Hovers, articles and the encyclopedia -----------------------------------------


def _arm_px(radius, dial_angle, star_fraction=0.86):
    pos = dial_point(dial_angle, radius * star_fraction * 0.82)
    return radius + pos.x(), radius + pos.y()


def test_arm_hover_speaks_the_two_row_pending_article(app):
    """Hovering an arm in the mode answers the archetype's TWO-ROW
    legend; until Session 6 writes the sets it shows the figure's name,
    the second-row name and the pending line — never a KeyError."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    comp = Compositor(_archetype_skin("trio"), AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    tooltip = comp.tooltip_at(*_arm_px(180.0, 0.0), 360.0)
    assert tooltip is not None
    assert "The One" in tooltip and "Judge" in tooltip
    assert archetypes.ARCHETYPE_PENDING_LINE in tooltip
    # The hexa two-sign columns are REPLACED by the archetype reading.
    soul = Compositor(_archetype_skin("hexa", "light"), AssetCache())
    soul.render_offscreen(360.0, 1.0, day, tick)
    tooltip = soul.tooltip_at(*_arm_px(180.0, 0.0), 360.0)
    assert "Gratitude" in tooltip and "Taking for Granted" in tooltip


def test_center_hover_and_targets(app):
    """The center speaks its CANON figure the same graceful way; the
    Spacebar targets: centers → None, the Walks → the Professions
    pages, the persons → None (no topics yet)."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    trio = Compositor(_archetype_skin("trio"), AssetCache())
    trio.render_offscreen(360.0, 1.0, day, tick)
    tooltip = trio.tooltip_at(180.0, 180.0, 360.0)
    assert tooltip is not None and "The Eye of Providence" in tooltip
    assert trio.encyclopedia_target(180.0, 180.0, 360.0) is None
    # Trio arms carry persons — no encyclopedia topics yet.
    assert trio.encyclopedia_target(*_arm_px(180.0, 0.0), 360.0) is None
    # The Walks map onto the Professions topic where pages exist.
    walks = Compositor(_archetype_skin("octa"), AssetCache())
    walks.render_offscreen(360.0, 1.0, day, tick)
    assert walks.encyclopedia_target(
        *_arm_px(180.0, 0.0), 360.0
    ) == ("profession", 0)                        # the King → Ruler
    assert walks.encyclopedia_target(
        *_arm_px(180.0, 225.0), 360.0
    ) is None                                     # the Scholar — none yet
    # The Compass has NO center — the middle answers no archetype hover.
    center_tip = walks.tooltip_at(180.0, 180.0, 360.0)
    assert center_tip is None or "The Seal" not in center_tip


def test_archetype_figure_size_circle_and_portrait_types(app, tmp_path):
    """Owner decree 2026-07-18, round two (screenshots): the archetype
    art divides into TWO TYPES by its OWN aspect ratio — no per-art
    clamp. CIRCLE art (square, or WIDE like Saturn's rings, or missing/
    placeholder) wears `weekday_body_size` — IDENTICAL to the weekday
    bodies; PORTRAIT art (the tall lancets) wears the per-pointer
    fraction of the star tip, `ARCHETYPE_FIGURE_HEIGHT_OF_TIP`."""
    from render.layers import archetype_figure_size, weekday_body_size

    skin = _archetype_skin("trio")
    radius = 180.0
    circle_size = weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    portrait_size = tip * archetypes.ARCHETYPE_FIGURE_HEIGHT_OF_TIP["trio"]
    assert portrait_size != pytest.approx(circle_size)   # a real distinction

    # CIRCLE: a square medallion.
    square = _rect_png(tmp_path, "square.png", 200, 200)
    assert archetype_figure_size(skin, radius, square) == pytest.approx(circle_size)
    # CIRCLE: WIDE art (Saturn's rings) stays height-based ON PURPOSE
    # (owner: "planeta istih dimenzija kao ostale, prstenovi vire") —
    # no clamp shrinks it to fit its own width.
    wide = _rect_png(tmp_path, "wide.png", 400, 200)
    assert archetype_figure_size(skin, radius, wide) == pytest.approx(circle_size)
    # PORTRAIT: a tall lancet.
    tall = _rect_png(tmp_path, "tall.png", 400, 800)
    assert archetype_figure_size(skin, radius, tall) == pytest.approx(portrait_size)
    # Missing / placeholder art reads CIRCLE-sized — nothing to classify.
    placeholder = _png(tmp_path, "tiny.png", 1)
    assert archetype_figure_size(skin, radius, placeholder) == pytest.approx(circle_size)
    missing = tmp_path / "never_written.png"
    assert archetype_figure_size(skin, radius, missing) == pytest.approx(circle_size)


def test_archetype_figure_size_boundary_is_the_threshold(tmp_path):
    """The CIRCLE/PORTRAIT split sits exactly at
    `ARCHETYPE_PORTRAIT_ASPECT_MAX`: aspect AT the threshold reads
    CIRCLE (>=), just below it reads PORTRAIT."""
    from render.layers import archetype_figure_size, weekday_body_size

    skin = _archetype_skin("trio")
    radius = 180.0
    threshold = archetypes.ARCHETYPE_PORTRAIT_ASPECT_MAX
    height = 1000
    at_threshold = _rect_png(
        tmp_path, "at_threshold.png", round(height * threshold), height
    )
    just_below = _rect_png(
        tmp_path, "just_below.png", round(height * threshold) - 1, height
    )
    circle_size = weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    portrait_size = tip * archetypes.ARCHETYPE_FIGURE_HEIGHT_OF_TIP["trio"]
    assert archetype_figure_size(skin, radius, at_threshold) == pytest.approx(circle_size)
    assert archetype_figure_size(skin, radius, just_below) == pytest.approx(portrait_size)


def test_archetype_center_follows_its_own_art_type(app, monkeypatch, tmp_path):
    """The center is NOT special-cased — `ArchetypeCenterLayer` routes
    its own figure's art through the same `archetype_figure_size`
    classifier an arm figure uses (owner two-type law, 2026-07-18 round
    two): a circle center wears the slot size, a portrait center the
    lancet fraction, whichever art the archetype's center dict names."""
    import config.archetypes as archetypes_mod
    import render.layers as layers_mod
    from render.layers import ArchetypeCenterLayer, weekday_body_size

    skin = _archetype_skin("trio")
    radius = 180.0

    def rendered_height(art_path):
        monkeypatch.setattr(
            archetypes_mod, "center",
            lambda key: {"file": art_path, "name": "Testling", "entity": "center"},
        )
        captured = []
        monkeypatch.setattr(
            layers_mod, "draw_pixmap_centered",
            lambda painter, ctx, asset, pos, height, *a, **kw:
                captured.append(height),
        )
        monkeypatch.setattr(
            layers_mod, "_draw_archetype_name",
            lambda painter, name, pos, arm_width, figure_height:
                captured.append(figure_height),
        )
        image = QImage(400, 400, QImage.Format.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        painter.translate(200, 200)
        ctx = RenderContext(
            skin=skin, day=SimpleNamespace(star_rotation=0.0),
            tick=SimpleNamespace(hour_angle=0.0),
            radius=radius, cache=AssetCache(), dpr=1.0, archetype_lit=0,
        )
        ArchetypeCenterLayer(skin).paint(painter, ctx)
        painter.end()
        monkeypatch.undo()
        return captured[-1]

    circle_center = _rect_png(tmp_path, "circle_center.png", 200, 200)
    assert rendered_height(circle_center) == pytest.approx(
        weekday_body_size(skin, radius)
    )
    portrait_center = _rect_png(tmp_path, "portrait_center.png", 400, 800)
    tip = radius * skin.star.radius_fraction
    assert rendered_height(portrait_center) == pytest.approx(
        tip * archetypes.ARCHETYPE_FIGURE_HEIGHT_OF_TIP["trio"]
    )


def test_archetype_center_size_is_reveal_invariant(app):
    """Owner 2026-07-17, ROADMAP 15g: the Omega reveal must NOT resize any
    figure. The center figure draws IDENTICALLY with the reveal off and on
    — the sizing helper has no reveal term, so size(normal) == size(reveal)
    to the pixel. Both renders sit AT solar noon (hour_angle == star_rotation)
    so the 2026-07-18 center WINDOW also reads full in the non-reveal case —
    isolating the size comparison from the window's own opacity term (pinned
    separately by test_archetype_center_window_render)."""
    from render.layers import ArchetypeCenterLayer, RenderContext

    skin = _archetype_skin("trio")
    layer = ArchetypeCenterLayer(skin)

    def render(reveal):
        image = QImage(360, 360, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(180, 180)
        ctx = RenderContext(
            skin=skin, day=SimpleNamespace(star_rotation=0.0),
            tick=SimpleNamespace(hour_angle=0.0),
            radius=180.0, cache=AssetCache(), dpr=1.0,
            reveal_active=reveal, archetype_lit=0,
        )
        layer.paint(painter, ctx)
        painter.end()
        return image

    assert render(False) == render(True)     # reveal never resizes the center


def test_archetype_center_lit_window():
    """Owner seal 2026-07-18: the center burns FULL exactly at TRUE solar
    noon and at TRUE solar midnight, stays full within
    ARCHETYPE_CENTER_WINDOW_DEG (15deg == +-1h) of either, and turns
    ghost just past the boundary — on BOTH sides of each instant."""
    noon = 40.0                                   # an arbitrary noon angle
    midnight = (noon + 180.0) % 360.0
    window = archetypes.ARCHETYPE_CENTER_WINDOW_DEG
    assert archetype_center_lit(noon, noon)
    assert archetype_center_lit(midnight, noon)
    for sign in (+1.0, -1.0):
        just_inside_noon = (noon + sign * (window - 0.1)) % 360.0
        just_outside_noon = (noon + sign * (window + 0.1)) % 360.0
        just_inside_midnight = (midnight + sign * (window - 0.1)) % 360.0
        just_outside_midnight = (midnight + sign * (window + 0.1)) % 360.0
        assert archetype_center_lit(just_inside_noon, noon)          # 14.9 deg
        assert not archetype_center_lit(just_outside_noon, noon)     # 15.1 deg
        assert archetype_center_lit(just_inside_midnight, noon)      # 14.9 deg
        assert not archetype_center_lit(just_outside_midnight, noon)  # 15.1 deg


def test_archetype_center_window_render(app):
    """Owner seal 2026-07-18: the center draws differently in vs out of
    the noon/midnight window on the same skin/day, and the reveal
    gesture forces it full even OUT of the window."""
    from render.layers import ArchetypeCenterLayer

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    base = datetime(2026, 7, 16, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        base, observer,
        SeasonsRepository().year_anchors(base.year),
        MoonPhaseRepository().moon_window(base.year),
    )
    in_window = build_tick_state(day.sun.noon, day)             # TRUE solar noon
    out_window = build_tick_state(day.sun.noon + timedelta(hours=6), day)

    skin = _archetype_skin("trio")
    layer = ArchetypeCenterLayer(skin)

    def render(tick, reveal=False):
        image = QImage(360, 360, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.translate(180, 180)
        ctx = RenderContext(
            skin=skin, day=day, tick=tick, radius=180.0,
            cache=AssetCache(), dpr=1.0, reveal_active=reveal, archetype_lit=0,
        )
        layer.paint(painter, ctx)
        painter.end()
        return image

    lit = render(in_window)
    ghost = render(out_window)
    assert lit != ghost                       # the window changes the paint
    revealed = render(out_window, reveal=True)
    assert revealed == lit                    # reveal forces full, out-of-window


def test_archetype_arm_is_a_hover_target(app):
    """Owner slika 8: an archetype arm is a hover-enlarge target
    ("archetype:<index>") through the arm-diamond geometry — set_hover
    locks on and the enlarged figure redraws above (the HoverLift twin)."""
    from render.layers import archetype_lit_index

    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    skin = _archetype_skin("octa", hover_enlarge=1.8)   # solar rotation off
    comp = Compositor(skin, AssetCache())
    plain = comp.render_offscreen(360.0, 1.0, day, tick)
    lit = archetype_lit_index("octa", tick.hour_angle, 0.0)   # a full figure
    x, y = _arm_px(180.0, lit * 45.0)
    assert comp.set_hover(x, y, 360.0)              # the target changed
    assert comp._hovered == f"archetype:{lit}"
    hovered = comp.render_offscreen(360.0, 1.0, day, tick)
    assert hovered != plain                         # the figure grew above
    assert comp.set_hover(-1.0e9, -1.0e9, 360.0)    # leaving clears it
    assert comp.render_offscreen(360.0, 1.0, day, tick) == plain


def test_ages_arm_shows_the_three_side_layout(app):
    """Owner slika 6 ("oba odmah"): the Ages (compass light) arm hover is
    a THREE-COLUMN layout — the age's text plus BOTH life registers at
    once (the Tree and the Menagerie) — distinct from the two-row form,
    its total width the same as the two-side layout."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    ages = Compositor(_archetype_skin("octa", "light"), AssetCache())
    ages.render_offscreen(360.0, 1.0, day, tick)
    tip = ages.tooltip_at(*_arm_px(180.0, 0.0), 360.0)     # top arm = Youth
    assert tip is not None
    assert "The Tree" in tip and "The Menagerie" in tip    # both registers
    assert "The Blossoming Crown" in tip and "The Lion" in tip  # both beings
    assert tip.count("<td") == 3                            # three columns
    # Total width stays within the two-side width (owner).
    assert (
        3 * defaults.ARTICLE_THREE_COLUMN_WIDTH_PX
        <= 2 * defaults.ARTICLE_COLUMN_WIDTH_PX + 2
    )


def test_tetramorph_arm_shows_the_three_side_layout(app):
    """Owner 2026-07-17 ("sva 3 ako se podudaraju"): the Tetramorph
    (seasons light) arm hover is a THREE-COLUMN layout — the creature, the
    evangelist it became, and the element its season arm holds — the same
    machinery and total width as the Ages three-side."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    tetra = Compositor(_archetype_skin("cross", "light"), AssetCache())
    tetra.render_offscreen(360.0, 1.0, day, tick)
    tip = tetra.tooltip_at(*_arm_px(180.0, 0.0), 360.0)     # top arm = the Lion
    assert tip is not None
    assert tip.count("<td") == 3                            # three columns
    assert "The Lion" in tip                                # the creature
    assert "The Evangelist" in tip and "Mark" in tip        # the evangelist
    assert "The Element" in tip and "Fire" in tip           # the element
    # The bottom arm creature is the Eagle → John → Water.
    bottom = tetra.tooltip_at(*_arm_px(180.0, 180.0), 360.0)
    assert "The Eagle" in bottom and "John" in bottom and "Water" in bottom


def test_archetype_article_resolution_is_graceful(app):
    """SymbolismRepository.archetype_article: an unwritten set (and an
    unwritten entity) answer None — the resolution path Session 6
    fills with {"rows": [...]} nodes under the documented set names."""
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    assert repo.archetype_article("archetype_trinity_paint", "one") is None
    assert repo.archetype_article("archetype_compass_light", "center") is None
    # Every archetype declares its documented set name.
    for key, spec in archetypes.ARCHETYPES.items():
        assert spec["articles"] == f"archetype_{key}"


# --- The Earth day label -----------------------------------------------------------


def test_earth_weekday_label_joins_the_date(app):
    """earth_weekday (owner 2026-07-17, default OFF; renamed from
    archetype_earth_day): the abbreviated weekday on the Earth marker —
    a GENERAL Earth option now, so it changes the render in BOTH archetype
    AND normal mode (exclusive with the date since ROADMAP 15e: with it on
    the marker shows the weekday instead of the date)."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))     # a Thursday
    size = 720.0                     # the date label draws from 540 up
    marker = defaults.DEFAULT_SKIN.year_marker
    pos = dial_point(tick.year_angle, 360.0 * marker.orbit_fraction)
    cx, cy = 360 + pos.x(), 360 + pos.y()
    box = 50

    def differing(a, b):
        return sum(
            1
            for x in range(int(cx) - box, int(cx) + box)
            for y in range(int(cy) - box, int(cy) + box)
            if a.pixelColor(x, y) != b.pixelColor(x, y)
        )

    # In ARCHETYPE mode the label block changes when the option turns on.
    base = Compositor(
        _archetype_skin("octa"), AssetCache()
    ).render_offscreen(size, 1.0, day, tick)
    dated = Compositor(
        _archetype_skin("octa", earth_weekday=True), AssetCache()
    ).render_offscreen(size, 1.0, day, tick)
    assert differing(base, dated) > 0
    # And now ALSO in NORMAL mode (the general Earth option, no longer
    # gated by archetype mode).
    normal_off = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    ).render_offscreen(size, 1.0, day, tick)
    normal_on = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False, earth_weekday=True
        ),
        AssetCache(),
    ).render_offscreen(size, 1.0, day, tick)
    assert differing(normal_off, normal_on) > 0


def test_earth_label_date_and_weekday_are_exclusive_in_render(app):
    """EARTH LABEL EXCLUSIVITY (owner 2026-07-17, ROADMAP 15e): on the
    Earth marker the DATE and the WEEKDAY are mutually exclusive — weekday
    ALONE draws (it must work without the date), date alone draws, and the
    two produce DIFFERENT pixels (different glyphs). Both-off draws neither."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))     # a Thursday → THU
    size = 720.0
    marker = defaults.DEFAULT_SKIN.year_marker
    pos = dial_point(tick.year_angle, 360.0 * marker.orbit_fraction)
    cx, cy = 360 + pos.x(), 360 + pos.y()
    box = 55

    def skin(**kw):
        return dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False, **kw
        )

    def render(**kw):
        return Compositor(skin(**kw), AssetCache()).render_offscreen(
            size, 1.0, day, tick
        )

    def label_pixels(image):
        return sum(
            1
            for x in range(int(cx) - box, int(cx) + box)
            for y in range(int(cy) - box, int(cy) + box)
            if image.pixelColor(x, y).alpha() > 0
        )

    neither = render(show_earth_date=False, earth_weekday=False)
    date_only = render(show_earth_date=True, earth_weekday=False)
    weekday_only = render(show_earth_date=False, earth_weekday=True)

    def differing(a, b):
        return sum(
            1
            for x in range(int(cx) - box, int(cx) + box)
            for y in range(int(cy) - box, int(cy) + box)
            if a.pixelColor(x, y) != b.pixelColor(x, y)
        )

    # Weekday ALONE actually draws (owner: "FRI must work without Date").
    assert differing(weekday_only, neither) > 0
    # Date alone draws, and differs from the weekday (different glyphs).
    assert differing(date_only, neither) > 0
    assert differing(date_only, weekday_only) > 0
    # FULL DATE (owner 2026-07-18, the third mode): both bools on draws
    # the date WITH the weekday row — more than the date alone.
    full = render(show_earth_date=True, earth_weekday=True)
    assert differing(full, date_only) > 0
    assert differing(full, neither) > 0


# --- The menu gating ----------------------------------------------------------------


def test_menu_gating(app, tmp_path, monkeypatch):
    """The Archetype toggle grays on the archetype-less Aurora/Calendar
    (and with the Pointer element off); while the mode is ON the three
    slot submenus gray IN PLACE. The Earth-weekday toggle is a general
    Earth option now (owner 2026-07-17) — enabled at the default 720 px
    regardless of the mode. The full controller wiring, TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    controller = AppController(app)
    try:
        assert controller._archetype_action.isEnabled()      # hexa default
        # The Earth-weekday toggle lives in Design ▸ Earth now, gated by
        # the dial size (720 default), NOT the archetype mode.
        assert controller._earth_weekday_toggle.isEnabled()
        controller._set_display_choice("pointer", "aurora")
        assert not controller._archetype_action.isEnabled()
        controller._set_display_choice("pointer", "calendar")
        assert not controller._archetype_action.isEnabled()
        controller._set_display_choice("pointer", "trio")
        assert controller._archetype_action.isEnabled()
        assert all(
            action.isEnabled()
            for action, _ in controller._slot_menu_checks
        )
        controller._set_display_choice("archetype_mode", True)
        # Still enabled in the mode (general option, not gated by it).
        assert controller._earth_weekday_toggle.isEnabled()
        assert not any(
            action.isEnabled()
            for action, _ in controller._slot_menu_checks
        )
        # The settings underneath stay the user's own.
        assert controller._settings.show_weekday
        controller._set_display_choice("archetype_mode", False)
        assert all(
            action.isEnabled()
            for action, _ in controller._slot_menu_checks
        )
    finally:
        controller._profiling_timer.stop()
        controller._tray.hide()


def test_weekday_menu_planets_first_with_art_metals(app, tmp_path, monkeypatch):
    """Planets menu placement + Art metals (owner 2026-07-18): the
    Weekday submenu shows Planets FIRST, flat, above the kinship groups
    — Arcana no longer carries it, so Planets appears exactly once —
    and its Art option nests its OWN Gold/Bronze/Silver dropdown (no
    Colored: the planets/art/ plates have no colored/ folder), wired
    through the same on_theme(theme, metal) path as the METAL_THEMES
    entries. Image and Sign stay plain options. TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    def action(menu, text):
        return next(a for a in menu.actions() if a.text() == text)

    c = AppController(app)
    try:
        slot_menu = next(
            a for a in c._menu.actions() if "1ˢᵗ Slot" in a.text()
        ).menu()
        weekday_menu = action(slot_menu, "Weekday").menu()
        entries = [a.text() for a in weekday_menu.actions() if a.text()]
        # Planets leads, flat — the kinship groups (and Names) follow.
        assert entries[0] == "Planets"
        assert entries.index("Arcana") > entries.index("Planets")
        assert entries.count("Planets") == 1     # never inside Arcana too

        planets_menu = action(weekday_menu, "Planets").menu()
        assert [a.text() for a in planets_menu.actions()] == [
            "Image", "Sign", "Art",
        ]
        art_menu = action(planets_menu, "Art").menu()
        assert [a.text() for a in art_menu.actions()] == [
            "Gold", "Bronze", "Silver",
        ]

        arcana_menu = action(weekday_menu, "Arcana").menu()
        assert "Planets" not in [a.text() for a in arcana_menu.actions()]
        assert [a.text() for a in arcana_menu.actions()] == [
            "Alchemy", "Japanese week", "Cosmos",
        ]
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


def test_per_pointer_palette_labels_and_calendar_visibility(app, tmp_path, monkeypatch):
    """The wheel-pair labels follow the pointer (owner 2026-07-17,
    ROADMAP 11) and the pair is NEVER grayed — every pointer has two
    distinct wheels (the Seasons gained the Elements). The Calendar
    lighting entries are NON-VISIBLE off the Calendar, INLINE on it."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    controller = AppController(app)
    try:
        def labels():
            return [a.text() for a in controller._menu_gates["palette_style"]]

        def all_live():
            return all(
                a.isEnabled() for a in controller._menu_gates["palette_style"]
            )

        def lighting_visible():
            return any(
                a.isVisible()
                for a in controller._menu_gates["calendar_lighting"]
            )

        controller._set_display_choice("pointer", "trio")
        assert labels() == ["Court", "Family"] and all_live()
        assert not lighting_visible()
        # Naming refinements (owner 2026-07-17, ROADMAP 15e): the Seasons
        # pair is Temperaments/Elements now, and Aurora has its OWN pair
        # (Warm/Cool) instead of a second Paint/Light.
        controller._set_display_choice("pointer", "cross")
        assert labels() == ["Temperaments", "Elements"] and all_live()
        controller._set_display_choice("pointer", "octa")
        assert labels() == ["Walks", "Ages"] and all_live()
        controller._set_display_choice("pointer", "aurora")
        assert labels() == ["Warm", "Cool"] and all_live()
        controller._set_display_choice("pointer", "hexa")
        assert labels() == ["Paint palette", "Light palette"] and all_live()
        controller._set_display_choice("pointer", "calendar")
        assert labels() == ["Zodiac", "Almanac"] and all_live()
        assert lighting_visible()        # inline only on the Calendar
    finally:
        controller._profiling_timer.stop()
        controller._tray.hide()


def test_slot_ordinal_click_follows_the_enable_chain(app, tmp_path, monkeypatch):
    """Top-level slot ordinal CLICK = its dropdown Enable (owner
    2026-07-17, slika 3): clicking enables/disables the slot through the
    same key, gated by the same 1 → 2 → 3 chain — a forbidden enable is a
    no-op and the check restores. TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        info_action = next(
            a for a, k in c._slot_menu_checks if k == "show_octa_slot"
        )
        # Defaults: 1st on, 2nd & 3rd off.
        assert c._settings.show_weekday
        assert not c._settings.show_octa_slot
        # The chain ALLOWS enabling the 2nd (1st is on), then the 3rd.
        c._toggle_slot_ordinal("show_octa_slot", True)
        assert c._settings.show_octa_slot and info_action.isChecked()
        c._toggle_slot_ordinal("show_third_slot", True)
        assert c._settings.show_third_slot
        # Disabling the 1st is always allowed; the 2nd's ordinal check then
        # restores to unchecked (its EFFECTIVE state is off).
        c._toggle_slot_ordinal("show_weekday", False)
        assert not c._settings.show_weekday
        assert not info_action.isChecked()
        # A FORBIDDEN enable is a no-op: with the 1st off, re-enabling the
        # 2nd does nothing (same gate as its grayed dropdown Enable).
        c._toggle_slot_ordinal("show_octa_slot", False)
        assert not c._settings.show_octa_slot
        c._toggle_slot_ordinal("show_octa_slot", True)
        assert not c._settings.show_octa_slot          # forbidden — unchanged
        assert not info_action.isChecked()
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


def test_elements_top_level_toggles_all_on_off(app, tmp_path, monkeypatch):
    """Elements top-level CLICK = all on / all off (owner 2026-07-17,
    ROADMAP 15e): the ordinal check shows ONLY when every element is on;
    clicking while all-on turns them all off, otherwise turns them all on;
    turning ONE off unchecks the ordinal. TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        keys = [k for _, k in c._element_toggles]
        # Defaults: every element on → the ordinal is checked.
        assert all(getattr(c._settings, k) for k in keys)
        assert c._elements_menu_action.isChecked()
        # Click Elements → all off, ordinal unchecks, children mirror off.
        c._toggle_all_elements()
        assert not any(getattr(c._settings, k) for k in keys)
        assert not c._elements_menu_action.isChecked()
        assert all(not a.isChecked() for a, _ in c._element_toggles)
        # Click again → all on.
        c._toggle_all_elements()
        assert all(getattr(c._settings, k) for k in keys)
        assert c._elements_menu_action.isChecked()
        # Turning a SINGLE element off unchecks the ordinal.
        c._set_element(keys[0], False)
        assert not c._elements_menu_action.isChecked()
    finally:
        c._profiling_timer.stop()
        c._tray.hide()
