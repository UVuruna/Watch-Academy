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
from datetime import datetime
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


def test_grid_covers_the_seven_archetypes():
    """CANON: SEVEN archetypes over 4 pointers × 2 wheels — the
    Seasons serve ONE under both; Aurora and the Calendar have none."""
    assert set(archetypes.ARCHETYPE_GRID.values()) == {
        "trinity_paint", "trinity_light", "seasons",
        "prism_paint", "prism_light", "compass_paint", "compass_light",
    }
    assert archetypes.grid_key("cross", "paint") == "seasons"
    assert archetypes.grid_key("cross", "light") == "seasons"
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
    assert archetypes.center("seasons")["file"].name == "Throne.png"
    assert archetypes.center("compass_paint") is None
    assert archetypes.center("compass_light") is None


def test_reused_scale_glass_is_real_art(app):
    """Prism paint's Lucifer and Judas REUSE the owner's Scale glass
    (canon: no new art for those two seats) — the files are on disk
    and pass the readiness check, unlike the 1×1 placeholders."""
    figs = archetypes.figures("prism_paint")
    lucifer, judas = figs[2], figs[4]
    assert lucifer["file"].name == "Lucifer_Triangle.png"
    assert judas["file"].name == "Judas_Triangle.png"
    assert archetype_art_ready(lucifer["file"])
    assert archetype_art_ready(judas["file"])
    # The freshly committed placeholders are NOT ready — the renderer
    # falls back to the name for them.
    assert not archetype_art_ready(figs[0]["file"])          # One_Love 1×1


def test_family_and_temperament_seatings():
    """CANON seatings: the Family triangle (Child top, Mother 20h,
    Father 4h) and the color-fixed temperaments (Choleric summer
    yellow top, Sanguine spring green left)."""
    family = archetypes.figures("trinity_light")
    assert [fig["name"] for fig in family] == [
        "The Child", "The Mother", "The Father",
    ]
    seasons = archetypes.figures("seasons")
    assert [fig["name"] for fig in seasons] == [
        "Choleric", "Melancholic", "Phlegmatic", "Sanguine",
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
            painter, ctx, fig, QPointF(0, 0), 80.0, 1.0, named=False,
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


def test_reveal_hides_the_hands(app):
    """The repurposed Omega double-click (owner seal 2026-07-16): while
    the reveal runs the HANDS are not drawn — at noon sharp all hands
    stack straight up, so the probe band above the center reads pure
    arm fill with the reveal on and a hand shaft without it."""
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    skin = _archetype_skin("trio", show_weekday_names=False)
    comp = Compositor(skin, AssetCache())
    base = comp.render_offscreen(360.0, 1.0, day, tick)
    assert comp.trigger_reveal_week() is True
    revealed = comp.render_offscreen(360.0, 1.0, day, tick)

    def non_fill(image):
        """Pixels in the probe band that are NOT the lit yellow arm
        fill (the placeholder name text sits higher, ~y 92–115)."""
        return sum(
            1
            for x in range(174, 187)
            for y in range(125, 146)
            if not (
                image.pixelColor(x, y).red() > 180
                and image.pixelColor(x, y).blue() < 120
            )
        )

    assert non_fill(base) > 0        # a hand shaft crosses the band
    assert non_fill(revealed) == 0   # hands hidden — clean theme


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


def test_earth_day_label_joins_the_date(app):
    """archetype_earth_day (owner 2026-07-16, default OFF): with the
    option on IN the mode, the Earth marker's label block changes (the
    date shifts up, the abbreviated day joins); off the mode the flag
    is inert."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))     # a Thursday
    plain = Compositor(_archetype_skin("octa"), AssetCache())
    labeled = Compositor(
        _archetype_skin("octa", archetype_earth_day=True), AssetCache()
    )
    size = 720.0                     # the date label draws from 540 up
    base = plain.render_offscreen(size, 1.0, day, tick)
    dated = labeled.render_offscreen(size, 1.0, day, tick)
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

    assert differing(base, dated) > 0
    # Off the mode the flag does nothing.
    off_a = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False
        ), AssetCache()
    ).render_offscreen(size, 1.0, day, tick)
    off_b = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            archetype_earth_day=True,
        ), AssetCache()
    ).render_offscreen(size, 1.0, day, tick)
    assert differing(off_a, off_b) == 0


# --- The menu gating ----------------------------------------------------------------


def test_menu_gating(app, tmp_path, monkeypatch):
    """The Archetype toggle grays on the archetype-less Aurora/Calendar
    (and with the Pointer element off); while the mode is ON the three
    slot submenus gray IN PLACE and the Earth-weekday sub-toggle goes
    live — the full controller wiring, against a TEMP settings home."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from app.controller import AppController

    controller = AppController(app)
    try:
        assert controller._archetype_action.isEnabled()      # hexa default
        assert not controller._archetype_earth_action.isEnabled()
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
        assert controller._archetype_earth_action.isEnabled()
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
        # Paint/Light stays LIVE on the Trinity (the Family wheel) and
        # grays only on the Seasons.
        assert all(
            a.isEnabled() for a in controller._menu_gates["palette_style"]
        )
        controller._set_display_choice("pointer", "cross")
        assert not any(
            a.isEnabled() for a in controller._menu_gates["palette_style"]
        )
    finally:
        controller._profiling_timer.stop()
        controller._tray.hide()
