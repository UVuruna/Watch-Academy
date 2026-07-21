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
import math
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


def test_prism_poles_wear_their_own_lancets(app, tmp_path):
    """ONE IMAGE, ONE PLACE (owner law 2026-07-19): the Scale-glass
    reuse for the prism poles is REVOKED — the triangles belong to the
    Scale badge alone (in four rotating versions), and Lucifer/Judas
    point at their OWN persons lancets (prompts sheeted; the name
    fallback carries the seats until the art lands). The placeholder
    rejection is pinned on a SYNTHETIC 1×1 so it never depends on which
    real art has arrived."""
    figs = archetypes.figures("prism_paint")
    lucifer, judas = figs[2], figs[4]
    assert lucifer["file"].name == "Lucifer_Pride.png"
    assert judas["file"].name == "Judas_Fear.png"
    for fig in figs:
        assert "badge" not in fig["file"].parts     # nothing borrows the Scale
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


def test_tetramorph_figures_declare_rotation():
    """THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20): the
    Tetramorph is the first ArchetypeLayer consumer to opt in — every
    other archetype figure and every center stays a fixed master, so
    `ArchetypeLayer.paint()`'s rotation branch never fires for them."""
    tetramorph = archetypes.figures("seasons_light")
    assert all(fig["rotates"] for fig in tetramorph)
    for key in archetypes.ARCHETYPE_GRID.values():
        if key == "seasons_light":
            continue
        assert not any(fig["rotates"] for fig in archetypes.figures(key)), key
        center = archetypes.center(key)
        if center is not None:
            assert not center.get("rotates")
    assert not archetypes.center("seasons_light").get("rotates")


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
            painter, ctx, fig, QPointF(0, 0), 80.0, 1.0,
            named=False, label_px=32.0,
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


# --- Name label fitting: the shared MAX-PX cap, and the SET-UNIFORM law -----------
# (ROADMAP 15h item 4, owner verdict 2026-07-18: the two-line wrap is REVOKED —
# every name is one line again; a set of names sharing a ring wears the size
# of its SMALLEST fitted member.)


def test_short_name_is_capped_at_name_label_max_px(app):
    """4b: a SHORT name with ample room must not inflate past
    `defaults.NAME_LABEL_MAX_PX` — the flat ceiling reasoned from the
    720-dial short-weekday "TUE" look, shared by the weekday body label
    and the archetype figure label (Rule #5, ONE fitting helper)."""
    import render.layers as layers_mod

    assert (
        layers_mod.name_label_px("Ox", target_width=10_000.0)
        == defaults.NAME_LABEL_MAX_PX
    )


def test_long_name_still_shrinks_to_fit(app):
    """4b: the cap is a ceiling, not a floor — a LONG name in a narrow
    space still measures DOWN to fit, and grows again with more room."""
    import render.layers as layers_mod

    narrow = layers_mod.name_label_px("The Eye of Providence", target_width=80.0)
    wide = layers_mod.name_label_px("The Eye of Providence", target_width=800.0)
    assert defaults.BODY_LABEL_MIN_PX <= narrow < wide <= defaults.NAME_LABEL_MAX_PX


def test_draw_name_label_draws_exactly_one_line(app, monkeypatch):
    """Owner verdict 2026-07-18: the two-line wrap is GONE — every name,
    long or short, draws as exactly ONE outlined line at the given
    pixel size (no more measuring/splitting inside the draw call)."""
    import render.layers as layers_mod

    calls = []
    monkeypatch.setattr(
        layers_mod, "draw_outlined_text",
        lambda painter, pos, text, font:
            calls.append((text, pos.y(), font.pixelSize())),
    )
    image = QImage(200, 200, QImage.Format.Format_ARGB32_Premultiplied)
    painter = QPainter(image)
    layers_mod.draw_name_label(painter, "Compass Walks", QPointF(0, 0), 42.0)
    painter.end()
    assert calls == [("Compass Walks", 0.0, 42)]


def test_weekday_label_set_uses_the_smallest_fitted_member(app):
    """21-C owner verdict: ALL names of one weekday ring wear the size
    of the SMALLEST fitted member — a set containing one long name
    drags every member down to its size, the cap/floor still hold."""
    import render.layers as layers_mod

    skin = _archetype_skin("hexa", show_weekday_names=True)
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    ctx = RenderContext(
        skin=dataclasses.replace(skin, archetype_mode=False),
        day=day, tick=tick, radius=200.0, cache=AssetCache(), dpr=1.0,
    )
    set_px = layers_mod.weekday_label_set_px(ctx)
    # Every individual body's OWN fit is >= the set answer (the set
    # picks the narrowest-fitting member, never inflates past it).
    slot_size = layers_mod.weekday_body_size(ctx.skin, ctx.radius)
    target = slot_size * defaults.NAME_LABEL_WIDTH_FRACTION
    own_fits = [
        layers_mod.name_label_px(layers_mod.weekday_label_text(ctx, body), target)
        for body in constants.WEEKDAY_BODIES
    ]
    assert set_px == min(own_fits)
    assert defaults.BODY_LABEL_MIN_PX <= set_px <= defaults.NAME_LABEL_MAX_PX


def test_archetype_label_set_uses_the_smallest_fitted_member(app):
    """21-C owner verdict: the archetype figures AND the center share
    ONE set — a long figure/center name drags every label in the
    layout down to its own smaller fitted size."""
    import render.layers as layers_mod

    skin = _archetype_skin("trio")
    ctx = RenderContext(
        skin=skin, day=SimpleNamespace(), tick=None,
        radius=200.0, cache=AssetCache(), dpr=1.0,
    )
    key = layers_mod.archetype_key(skin)
    arm_width = (
        ctx.radius * skin.star.radius_fraction
        * math.tan(
            math.radians(constants.POINTER_ARM_HALF_ANGLE_DEG[skin.pointer])
        )
    )
    set_px = layers_mod.archetype_label_set_px(ctx, key, arm_width)
    target = arm_width * defaults.NAME_LABEL_WIDTH_FRACTION
    fits = [
        layers_mod.name_label_px(fig["name"], target)
        for fig in archetypes.figures(key)
    ]
    center = archetypes.center(key)
    if center is not None:
        center_height = layers_mod.archetype_figure_size(
            skin, ctx.radius, center["file"]
        )
        fits.append(
            layers_mod.name_label_px(
                center["name"], center_height * defaults.NAME_LABEL_WIDTH_FRACTION,
            )
        )
    assert set_px == min(fits)
    assert defaults.BODY_LABEL_MIN_PX <= set_px <= defaults.NAME_LABEL_MAX_PX


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


def test_arm_hover_speaks_the_two_row_article(app):
    """Hovering an arm in the mode answers the archetype's TWO-ROW
    legend (Session 6 wrote the sets): the figure's name, the second-row
    name, and both rows of real prose — no longer the pending line."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    comp = Compositor(_archetype_skin("trio"), AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    tooltip = comp.tooltip_at(*_arm_px(180.0, 0.0), 360.0)
    assert tooltip is not None
    assert "The One" in tooltip and "Judge" in tooltip
    assert archetypes.ARCHETYPE_PENDING_LINE not in tooltip
    assert "Alpha and the Omega" in tooltip     # row-1 prose landed
    # The hexa two-sign columns are REPLACED by the archetype reading.
    soul = Compositor(_archetype_skin("hexa", "light"), AssetCache())
    soul.render_offscreen(360.0, 1.0, day, tick)
    tooltip = soul.tooltip_at(*_arm_px(180.0, 0.0), 360.0)
    assert "Gratitude" in tooltip and "Taking for Granted" in tooltip
    assert archetypes.ARCHETYPE_PENDING_LINE not in tooltip


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
    bodies; PORTRAIT art (the tall lancets) wears the STANDARD-aspect
    inscribed height, `archetype_portrait_height`."""
    from render.layers import (
        archetype_figure_size, archetype_portrait_height, weekday_body_size,
    )

    skin = _archetype_skin("trio")
    radius = 180.0
    circle_size = weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    half = constants.POINTER_ARM_HALF_ANGLE_DEG["trio"]
    tan_half = math.tan(math.radians(half))
    portrait_size = archetype_portrait_height(tip, tan_half)
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
    `ARCHETYPE_PORTRAIT_ASPECT_MAX` (fix round A 2026-07-19: 0.70, not
    the old 0.85): aspect AT the threshold reads CIRCLE (>=), just
    below it reads PORTRAIT."""
    from render.layers import (
        archetype_figure_size, archetype_portrait_height, weekday_body_size,
    )

    skin = _archetype_skin("trio")
    radius = 180.0
    threshold = archetypes.ARCHETYPE_PORTRAIT_ASPECT_MAX
    assert threshold == pytest.approx(0.70)
    height = 1000
    at_threshold = _rect_png(
        tmp_path, "at_threshold.png", round(height * threshold), height
    )
    just_below = _rect_png(
        tmp_path, "just_below.png", round(height * threshold) - 1, height
    )
    circle_size = weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    half = constants.POINTER_ARM_HALF_ANGLE_DEG["trio"]
    tan_half = math.tan(math.radians(half))
    portrait_size = archetype_portrait_height(tip, tan_half)
    assert archetype_figure_size(skin, radius, at_threshold) == pytest.approx(circle_size)
    assert archetype_figure_size(skin, radius, just_below) == pytest.approx(portrait_size)


def test_archetype_figure_size_providence_eye_aspect_classifies_circle(tmp_path):
    """Owner fix round A 2026-07-19: the ChatGPT-set Providence_Eye
    center (measured aspect 0.842) is a ROUND rondel that wrongly
    classified as PORTRAIT under the old 0.85 threshold and drew at the
    tall lancet height (the "Trinity ogroman centar" bug). At 0.70 it
    classifies CIRCLE and wears the slot size."""
    from render.layers import archetype_figure_size, weekday_body_size

    skin = _archetype_skin("trio")
    radius = 180.0
    height = 1000
    providence_eye_like = _rect_png(
        tmp_path, "providence_eye.png", round(height * 0.842), height
    )
    assert archetype_figure_size(skin, radius, providence_eye_like) == pytest.approx(
        weekday_body_size(skin, radius)
    )


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
            layers_mod, "draw_name_label",
            lambda painter, name, pos, target_width:
                captured.append(target_width),
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
    half = constants.POINTER_ARM_HALF_ANGLE_DEG["trio"]
    tan_half = math.tan(math.radians(half))
    from render.layers import archetype_portrait_height
    assert rendered_height(portrait_center) == pytest.approx(
        archetype_portrait_height(tip, tan_half)
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
    # The evangelist and element columns now carry their OWN prose
    # (Tetramorph completion round 2026-07-18), not just the names.
    assert "crying in the wilderness" in tip                # Mark's article
    assert "yellow bile" in tip                             # Fire's article
    # The bottom arm creature is the Eagle → John → Water.
    bottom = tetra.tooltip_at(*_arm_px(180.0, 180.0), 360.0)
    assert "The Eagle" in bottom and "John" in bottom and "Water" in bottom
    assert "In the beginning was the Word" in bottom        # John's article
    assert "humor of phlegm" in bottom                      # Water's article


def test_tetramorph_three_side_survives_absent_evangelist_art(app):
    """The evangelist rondels may not exist on disk yet (a
    1x1-placeholder-free path): the three-side must still render the
    evangelist column from text alone — the name and its article, no
    crash, no stretched pixel."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    tetra = Compositor(_archetype_skin("cross", "light"), AssetCache())
    tetra.render_offscreen(360.0, 1.0, day, tick)
    # The config path table maps each arm index to its evangelist rondel.
    for index, name in enumerate(("Mark", "Luke", "John", "Matthew")):
        assert (
            archetypes.tetramorph_evangelist_file(index).name == f"{name}.png"
        )
    # With no evangelist art landed, the column carries the name and its
    # article prose and does not crash on any of the four arms.
    for arm, name in ((0.0, "Mark"), (90.0, "Luke"),
                      (180.0, "John"), (270.0, "Matthew")):
        tip = tetra.tooltip_at(*_arm_px(180.0, arm), 360.0)
        assert tip is not None and name in tip


def test_archetype_article_resolution_is_graceful(app):
    """SymbolismRepository.archetype_article: an unknown set and an
    unknown entity still answer None (the graceful path stands); the
    Compass has no center, so its "center" entity stays None even now
    that Session 6 wrote the sets."""
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    assert repo.archetype_article("archetype_trinity_paint", "nobody") is None
    assert repo.archetype_article("no_such_set", "one") is None
    # The two Compass wheels are centerless (the rose is the wheel).
    assert repo.archetype_article("archetype_compass_paint", "center") is None
    assert repo.archetype_article("archetype_compass_light", "center") is None
    # Every archetype declares its documented set name.
    for key, spec in archetypes.ARCHETYPES.items():
        assert spec["articles"] == f"archetype_{key}"


def test_every_archetype_set_position_and_center_is_written(app):
    """Session 6 coverage law: every archetype's every FIGURE position
    (both life registers included) and every CENTER that exists resolves
    to a non-pending {"rows": [...]} node with non-empty prose — so no
    hover in the mode ever falls back to the pending line."""
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    checked = 0
    for key, spec in archetypes.ARCHETYPES.items():
        set_name = spec["articles"]
        figs = []
        if "registers" in spec:
            for register in spec["registers"].values():
                figs.extend(register)
        else:
            figs = list(spec["figures"])
        entities = {fig["entity"] for fig in figs}
        if spec["center"] is not None:
            entities.add("center")
        for entity in entities:
            node = repo.archetype_article(set_name, entity)
            assert node is not None, f"{set_name}.{entity} is pending"
            rows = node.get("rows")
            assert rows and all(
                isinstance(r, str) and r.strip() for r in rows
            ), f"{set_name}.{entity} has empty rows"
            checked += 1
    assert checked == 48        # 6 two-row sets + 2 three-side wheels


def test_tetramorph_columns_carry_creature_evangelist_element_prose(app):
    """Tetramorph completion round 2026-07-18: each seasons_light
    creature node carries THREE non-pending rows — the creature (rows[0]),
    the evangelist it became (rows[1]), the element its arm holds
    (rows[2]) — so all three columns of the three-side speak, never a
    bare title. The four evangelist names and the four element humors are
    named in their rows."""
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    expect = {
        "lion": ("Mark", "yellow bile"),
        "ox": ("Luke", "black bile"),
        "eagle": ("John", "phlegm"),
        "man": ("Matthew", "blood"),
    }
    for entity, (evangelist, humor) in expect.items():
        node = repo.archetype_article("archetype_seasons_light", entity)
        rows = node["rows"]
        assert len(rows) == 3, f"{entity} needs creature+evangelist+element"
        assert all(isinstance(r, str) and r.strip() for r in rows)
        assert evangelist in rows[1], f"{entity} evangelist row"
        assert humor in rows[2], f"{entity} element humor row"


def test_octa_variants_wear_the_sealed_walks_and_ages_hues(app):
    """Session 6 MANDATORY: the octa_paint/octa_light variant paragraphs
    were rewritten off the OLD compass day-arc onto the sealed Walks
    (paint) and Eight Ages (light) wheels — each weekday body carries its
    fixed arm's NEW hue and no foreign arm hue leaks in."""
    from data.symbolism import SymbolismRepository

    # body -> (octa paint hue, octa light hue) at its fixed octa arm.
    hues = {
        "sun": ("#F0C420", "#FFE800"), "mars": ("#C87533", "#FFB400"),
        "venus": ("#A02020", "#FF6A3C"), "mercury": ("#7A2E8E", "#9C6BD4"),
        "moon": ("#1F5FA8", "#C8D7F0"), "saturn": ("#3E8914", "#8FA8C8"),
        "jupiter": ("#EDEDE0", "#7CE577"),
    }
    all_hues = {h for pair in hues.values() for h in pair}
    repo = SymbolismRepository()
    data = repo._load()["articles"]
    seen = 0
    for set_name, entities in data.items():
        for body, node in entities.items():
            variants = node.get("variants", {})
            if "octa_paint" not in variants:
                continue
            paint, light = variants["octa_paint"], variants["octa_light"]
            own_paint, own_light = hues[body]
            assert own_paint.lower() in paint.lower()
            assert own_light.lower() in light.lower()
            for hue in all_hues:
                if hue != own_paint:
                    assert hue.lower() not in paint.lower()
                if hue != own_light:
                    assert hue.lower() not in light.lower()
            seen += 1
    assert seen == 163


# --- The Earth day label -----------------------------------------------------------


def test_earth_weekday_label_joins_the_date(app):
    """earth_label="weekday" (owner 2026-07-18, ROADMAP 15h — the
    four-mode enum, replacing the old earth_weekday bool): the
    abbreviated weekday on the Earth marker — a GENERAL Earth option, so
    it changes the render in BOTH archetype AND normal mode."""
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
        _archetype_skin("octa", earth_label="weekday"), AssetCache()
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
            defaults.DEFAULT_SKIN, solar_rotation=False, earth_label="weekday"
        ),
        AssetCache(),
    ).render_offscreen(size, 1.0, day, tick)
    assert differing(normal_off, normal_on) > 0


def test_earth_label_four_modes_render_distinctly(app):
    """THE EARTH LABEL QUARTET (owner 2026-07-18, ROADMAP 15h, Session
    21-E): the single `earth_label` enum drives FOUR exclusive on-dial
    forms plus off — weekday alone draws (must work without the date),
    date alone draws with different glyphs than the weekday,
    "date_weekday" stacks the date over the weekday (more pixels than
    the date alone), and "full" stacks the date over the YEAR (also
    more than the date alone, and different from "date_weekday" since
    the second row reads a year, not a weekday)."""
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

    def differing(a, b):
        return sum(
            1
            for x in range(int(cx) - box, int(cx) + box)
            for y in range(int(cy) - box, int(cy) + box)
            if a.pixelColor(x, y) != b.pixelColor(x, y)
        )

    off = render(earth_label="off")
    date_only = render(earth_label="date")
    weekday_only = render(earth_label="weekday")

    # Weekday ALONE actually draws (owner: "FRI must work without Date").
    assert differing(weekday_only, off) > 0
    # Date alone draws, and differs from the weekday (different glyphs).
    assert differing(date_only, off) > 0
    assert differing(date_only, weekday_only) > 0
    # DATE & WEEKDAY (the old combined "Full Date" meaning): the date
    # WITH the weekday row — more than the date alone.
    date_weekday = render(earth_label="date_weekday")
    assert differing(date_weekday, date_only) > 0
    assert differing(date_weekday, off) > 0
    # FULL DATE (owner 2026-07-18, the TRUE Full Date): the date WITH
    # the year row — also more than the date alone, and a distinct
    # render from Date & Weekday (a year reads differently than "THU").
    full = render(earth_label="full")
    assert differing(full, date_only) > 0
    assert differing(full, off) > 0
    assert differing(full, date_weekday) > 0


# --- The menu gating ----------------------------------------------------------------


def test_menu_gating(app, tmp_path, monkeypatch):
    """The Archetype toggle grays on the archetype-less Aurora/Calendar
    (and with the Pointer element off). R5 MENU REWORK shrank the rest
    of this to the two window-opening entries: Pointer Theme / Slot
    Theme gray while the mode is ON (the Design/Earth controls moved
    into their own window, see tests/test_menu_rework.py for its own
    gating coverage). The full controller wiring, TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    controller = AppController(app)
    try:
        assert controller._archetype_action.isEnabled()      # hexa default
        controller._set_display_choice("pointer", "aurora")
        assert not controller._archetype_action.isEnabled()
        controller._set_display_choice("pointer", "calendar")
        assert not controller._archetype_action.isEnabled()
        controller._set_display_choice("pointer", "trio")
        assert controller._archetype_action.isEnabled()
        assert controller._pointer_theme_action.isEnabled()
        assert controller._slot_theme_action.isEnabled()
        controller._set_display_choice("archetype_mode", True)
        assert not controller._pointer_theme_action.isEnabled()
        assert not controller._slot_theme_action.isEnabled()
        # The settings underneath stay the user's own.
        assert controller._settings.show_weekday
        controller._set_display_choice("archetype_mode", False)
        assert controller._pointer_theme_action.isEnabled()
        assert controller._slot_theme_action.isEnabled()
    finally:
        controller._profiling_timer.stop()
        controller._tray.hide()


def test_archetype_names_is_its_own_settings_switch(app, tmp_path, monkeypatch):
    """Owner 2026-07-18, Session 21-C ('nemoj ispod nego u Settings —
    ON/OFF'): the menu twin the previous round added is GONE — there is
    no `_archetype_names_action` on the controller any more — and the
    figures' names are governed by their OWN INDEPENDENT setting,
    `archetype_names`, entirely separate from the weekday bodies'
    `show_weekday_names`."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        assert not hasattr(c, "_archetype_names_action")
        assert c._settings.archetype_names is True     # default: names on
        # Toggling the weekday Names switch must NOT move archetype_names.
        c._set_display_choice("show_weekday_names", False)
        assert c._settings.archetype_names is True
        c._set_display_choice("archetype_names", False)
        assert c._settings.show_weekday_names is False
        assert c._settings.archetype_names is False
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


def test_archetype_names_gates_the_render(app, monkeypatch):
    """`ArchetypeLayer` reads `archetype_names` — NOT
    `show_weekday_names` — for the figures' names: with real art, the
    LIT figure's name draws when `archetype_names` is on and is
    SKIPPED when off, regardless of the weekday bodies' own switch."""
    import render.layers as layers_mod

    monkeypatch.setattr(layers_mod, "archetype_art_ready", lambda path: True)
    monkeypatch.setattr(layers_mod, "draw_pixmap_centered", lambda *a, **kw: None)
    calls = []
    monkeypatch.setattr(
        layers_mod, "draw_name_label",
        lambda painter, name, pos, label_px: calls.append(name),
    )
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))

    def render(archetype_names):
        skin = _archetype_skin(
            "trio", show_weekday_names=False, archetype_names=archetype_names,
        )
        comp = Compositor(skin, AssetCache())
        comp.render_offscreen(360.0, 1.0, day, tick)

    calls.clear()
    render(False)
    assert calls == []                # names OFF — nothing drawn
    calls.clear()
    render(True)
    assert calls != []                # names ON — the lit figure speaks


def test_visible_top_level_toggles_all_on_off(app, tmp_path, monkeypatch):
    """Visible top-level CLICK = all on / all off (owner 2026-07-17,
    ROADMAP 15e; renamed from Elements, R5 MENU REWORK item E): the
    ordinal check shows ONLY when every entry is on; clicking while
    all-on turns them all off, otherwise turns them all on; turning ONE
    off unchecks the ordinal. TEMP home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        keys = [k for _, k in c._visible_toggles]
        # Defaults: every entry on → the ordinal is checked.
        assert all(getattr(c._settings, k) for k in keys)
        assert c._visible_menu_action.isChecked()
        # Click Visible → all off, ordinal unchecks, children mirror off.
        c._toggle_all_visible()
        assert not any(getattr(c._settings, k) for k in keys)
        assert not c._visible_menu_action.isChecked()
        assert all(not a.isChecked() for a, _ in c._visible_toggles)
        # Click again → all on.
        c._toggle_all_visible()
        assert all(getattr(c._settings, k) for k in keys)
        assert c._visible_menu_action.isChecked()
        # Turning a SINGLE entry off unchecks the ordinal.
        c._set_visible(keys[0], False)
        assert not c._visible_menu_action.isChecked()
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


# --- THE "SHOW" AFFORDANCE for "normal" z-mode (ROADMAP 15h, owner 2026-07-18) ----


def test_show_action_visible_only_in_normal_z_mode(app, tmp_path, monkeypatch):
    """The Show entry sits right below the TITLE row (owner
    INSTRUCTION.txt item 2A, R5 MENU REWORK — the title heads the whole
    menu now), HIDDEN (not grayed) outside "normal" z-mode —
    meaningless in "bottom" (never above anything) and "top" (already
    always above)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        assert c._menu.actions()[2] is c._show_action   # TITLE, separator, Show
        assert c._settings.z_mode == "bottom"           # default
        assert not c._show_action.isVisible()
        c._settings = dataclasses.replace(c._settings, z_mode="normal")
        c._refresh_menu_gating()
        assert c._show_action.isVisible()
        c._settings = dataclasses.replace(c._settings, z_mode="top")
        c._refresh_menu_gating()
        assert not c._show_action.isVisible()
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


def test_show_action_and_tray_double_click_raise_only_in_normal_mode(
    app, tmp_path, monkeypatch,
):
    """Triggering Show (menu or tray double-click) raises the dial only
    while z_mode == "normal" — a no-op in "bottom"/"top" (defense in
    depth beyond the menu's own visibility gate)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        calls = []
        monkeypatch.setattr(c._widget, "raise_and_focus", lambda: calls.append(1))
        assert c._settings.z_mode == "bottom"
        c._show_if_normal_z_mode()
        assert calls == []                              # no-op outside normal
        c._settings = dataclasses.replace(c._settings, z_mode="normal")
        c._show_if_normal_z_mode()
        assert calls == [1]
    finally:
        c._profiling_timer.stop()
        c._tray.hide()


def test_show_action_hidden_only_in_the_dial_context_menu(
    app, tmp_path, monkeypatch,
):
    """Show only in the TRAY (owner 2026-07-18, Session 21-D: "ako smo
    kliknuli znači da ga vidim") — the entry must NOT appear in the
    dial's right-click context menu, even while z_mode == "normal" makes
    it meaningful for the tray. The SAME shared QMenu is popped from two
    call sites: `ClockWidget.contextMenuEvent` hides `_show_action`
    before its own `exec()` and restores the z_mode-gated state right
    after; the tray's native popup (QSystemTrayIcon.setContextMenu)
    never runs this code at all, so it always sees the gated state
    undisturbed. `exec()` is stubbed here — a real popup would block the
    test waiting for a user."""
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QContextMenuEvent

    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    c = AppController(app)
    try:
        c._settings = dataclasses.replace(c._settings, z_mode="normal")
        c._refresh_menu_gating()
        c._widget.set_z_mode("normal")
        # The TRAY sees the gated state: visible in "normal".
        assert c._show_action.isVisible()

        visible_during_popup = []

        def fake_exec(pos):
            visible_during_popup.append(c._show_action.isVisible())

        monkeypatch.setattr(c._menu, "exec", fake_exec)
        event = QContextMenuEvent(
            QContextMenuEvent.Reason.Mouse, QPoint(0, 0), QPoint(0, 0)
        )
        c._widget.contextMenuEvent(event)

        assert visible_during_popup == [False]      # hidden for the DIAL's own popup
        assert c._show_action.isVisible()           # restored for the tray afterward
    finally:
        c._profiling_timer.stop()
        c._tray.hide()
