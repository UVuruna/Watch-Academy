"""Pointer variants (hexa/cross/octa): slot layouts, shared-slot
priority, palette presets, the octa bottom slot, the Umbra and the
solar-rotation toggle."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.layers import (
    HandLayer,
    SlotLayer,
    dial_point,
    palette_for,
    slot_layout,
    slot_seat_orbit,
    slot_seat_rotation,
    slot_seat_scale,
    today_slot_theta,
    weekday_body_orbit,
    umbra_ladder,
    visible_occupant,
    weekday_classic_slot,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def july_wednesday(app):
    """2026-07-08 (a Wednesday) at noon in Belgrade."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# --- Slot layouts ---------------------------------------------------------------


def test_every_layout_seats_the_whole_week():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        seated = [body for _, occupants in slots for body in occupants]
        if pointer in ("hexa", "trio"):
            seated.append("sun")     # hexa and trio center the Sun
        assert sorted(seated) == sorted(constants.WEEKDAY_BODIES), pointer


def test_slot_angles_sit_on_the_pointer_arms():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        if pointer == "aurora":
            # No arms exist — the single slot is pinned to the dial
            # bottom, above the Omega (owner spec 2026-07-12).
            assert slots == ((180.0, constants.WEEKDAY_BODIES),) or [
                angle for angle, _ in slots
            ] == [180.0]
            continue
        arm_step = 360.0 / constants.POINTER_POINTS[pointer]
        for angle, _ in slots:
            assert angle % arm_step == 0.0, (pointer, angle)


def test_octa_reserves_the_bottom_arm_for_the_info_slot():
    occupied = [angle for angle, _ in constants.POINTER_WEEKDAY_SLOTS["octa"]]
    assert constants.SOUTH_SLOT_ANGLE not in occupied


def test_slot_layout_matrix():
    """The owner's SLOT POSITION MATRIX (2026-07-14), pinned case by
    case: one slot (classic weekday / 24h on the Trinity / the center
    elsewhere), two slots (weekday priority on the Seasons and the
    Compass, arm seats on the Trinity and the Prism, 3h+21h flanks),
    three slots (top + right + left; the Seasons lock the 1st on the
    classic unit), the pinned layouts, and the 1 → 2 → 3 enable
    order."""
    import dataclasses

    TOP = constants.SLOT_SEAT_TOP_ANGLE
    RIGHT_ARM = constants.SLOT_SEAT_RIGHT_ARM_ANGLE
    LEFT_ARM = constants.SLOT_SEAT_LEFT_ARM_ANGLE
    H3 = constants.AURORA_DUAL_WEEKDAY_ANGLE
    H21 = constants.AURORA_DUAL_SLOT_ANGLE
    SOUTH = constants.SOUTH_SLOT_ANGLE

    def skin(**kw):
        kw.setdefault("show_octa_slot", False)
        return dataclasses.replace(defaults.DEFAULT_SKIN, **kw)

    # ONE slot: weekday -> the classic unit; anything else 24h on the
    # Trinity, the CENTER on the Seasons/Prism/Compass.
    for pointer in ("trio", "cross", "hexa", "octa"):
        assert slot_layout(skin(pointer=pointer)) == {1: "classic"}, pointer
    assert slot_layout(skin(pointer="trio", weekday_slot="time")) == {1: SOUTH}
    for pointer in ("cross", "hexa", "octa"):
        assert slot_layout(
            skin(pointer=pointer, weekday_slot="zodiac")
        ) == {1: "center"}, pointer
    # TWO slots: the Trinity and the Prism seat the pair on the arms.
    for pointer in ("trio", "hexa"):
        assert slot_layout(
            skin(pointer=pointer, show_octa_slot=True)
        ) == {1: LEFT_ARM, 2: RIGHT_ARM}, pointer
    # The Seasons and the Compass: whichever slot is weekday rides the
    # classic unit, the other takes the center; both weekday -> the
    # 1st; neither -> the 3h/21h flanks.
    for pointer in ("cross", "octa"):
        assert slot_layout(
            skin(pointer=pointer, show_octa_slot=True, octa_slot="date")
        ) == {1: "classic", 2: "center"}, pointer
        assert slot_layout(skin(
            pointer=pointer, show_octa_slot=True,
            weekday_slot="date", octa_slot="weekday",
        )) == {1: "center", 2: "classic"}, pointer
        assert slot_layout(skin(
            pointer=pointer, show_octa_slot=True, octa_slot="weekday",
        )) == {1: "classic", 2: "center"}, pointer
        assert slot_layout(skin(
            pointer=pointer, show_octa_slot=True,
            weekday_slot="time", octa_slot="date",
        )) == {1: H3, 2: H21}, pointer
    # THREE slots: top + right + left — the Seasons lock the 1st on
    # the classic unit and flank the rest.
    assert slot_layout(skin(
        pointer="octa", show_octa_slot=True, show_third_slot=True,
    )) == {1: TOP, 2: H21, 3: H3}
    for pointer in ("trio", "hexa"):
        assert slot_layout(skin(
            pointer=pointer, show_octa_slot=True, show_third_slot=True,
        )) == {1: TOP, 2: RIGHT_ARM, 3: LEFT_ARM}, pointer
    assert slot_layout(skin(
        pointer="cross", show_octa_slot=True, show_third_slot=True,
    )) == {1: "classic", 2: H21, 3: H3}
    # PINNED (Aurora, or the pointer off): 24h alone, the 3h/21h pair,
    # the top+arms trio — the weekday mode sits in a SEAT (today
    # alone), never the classic unit.
    for pinned in (
        skin(pointer="aurora"),
        skin(pointer="hexa", show_pointer=False),
    ):
        assert slot_layout(pinned) == {1: SOUTH}
        assert weekday_classic_slot(pinned) is None
    assert slot_layout(
        skin(pointer="aurora", show_octa_slot=True)
    ) == {1: H3, 2: H21}
    assert slot_layout(skin(
        pointer="aurora", show_octa_slot=True, show_third_slot=True,
    )) == {1: TOP, 2: RIGHT_ARM, 3: LEFT_ARM}
    # The enable ORDER (owner: ne može samo third): without the 1st
    # nothing draws, without the 2nd the 3rd stays dark.
    assert slot_layout(skin(show_weekday=False, show_octa_slot=True)) == {}
    assert slot_layout(skin(
        pointer="octa", show_octa_slot=False, show_third_slot=True,
    )) == {1: "classic"}


def test_slot_seat_geometry_follows_the_pointer():
    """Owner 2026-07-15, pinned: (1) seats ride the star's rotation
    ONLY while a pointer with arms is drawn — Aurora and pointer-off
    stay on natural round angles; (2) slot size is 125% on the
    slim-armed Seasons/Compass, 150% everywhere else including the
    pinned layouts; (3) on the slim-armed pointers an ANGLE seat
    shifts outward to the diamond's widest point, arms at 3h/6h stay
    (trio/hexa untouched, center/classic untouched)."""

    def skin(**kw):
        return dataclasses.replace(defaults.DEFAULT_SKIN, **kw)

    # (1) Rotation reaches the seats only under an armed pointer.
    for pointer in ("trio", "cross", "hexa", "octa"):
        assert slot_seat_rotation(skin(pointer=pointer), 10.76) == 10.76
    assert slot_seat_rotation(skin(pointer="aurora"), 10.76) == 0.0
    assert slot_seat_rotation(
        skin(pointer="hexa", show_pointer=False), 10.76
    ) == 0.0
    # (2) Per-pointer sizes: 125% slim-armed, 150% elsewhere + pinned.
    for pointer in ("cross", "octa"):
        assert slot_seat_scale(skin(pointer=pointer)) == 1.25, pointer
    for pointer in ("trio", "hexa", "aurora"):
        assert slot_seat_scale(skin(pointer=pointer)) == 1.50, pointer
    assert slot_seat_scale(
        skin(pointer="octa", show_pointer=False)
    ) == defaults.SLOT_SIZE_PINNED == 1.50
    # (3) The outward shift: angle seats on cross/octa only.
    H3 = constants.AURORA_DUAL_WEEKDAY_ANGLE
    for pointer in ("cross", "octa"):
        assert slot_seat_orbit(skin(pointer=pointer), H3) == \
            defaults.SLOT_SEAT_OUTWARD[pointer], pointer
        assert slot_seat_orbit(skin(pointer=pointer), "center") == 1.0
        assert slot_seat_orbit(skin(pointer=pointer), "classic") == 1.0
    assert slot_seat_orbit(skin(pointer="hexa"), H3) == 1.0
    assert slot_seat_orbit(
        skin(pointer="octa", show_pointer=False), H3
    ) == 1.0


def test_classic_weekday_unit_carries_the_pointer_scale():
    """The per-pointer slot size (0.14.229) reaches the CLASSIC weekday
    unit — the today badge and its ghosts — not only the seated slots:
    a probe beyond the UNSCALED body edge still lands on the body
    because the hit radius carries slot_seat_scale. Regression guard —
    the factor was once wired into SlotLayer alone, so the badge stayed
    one size on every pointer (owner: Prism i Kompas identični)."""
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())  # hexa → 1.5×
    spec = defaults.DEFAULT_SKIN.weekday_set
    R = 180.0
    angle = constants.POINTER_WEEKDAY_SLOTS["hexa"][1][0]  # a non-south seat
    center = dial_point(angle, R * weekday_body_orbit(defaults.DEFAULT_SKIN))
    unscaled_half = R * spec.diamond_scale
    norm = math.hypot(center.x(), center.y())
    # 1.35× the unscaled half-size out from the body center: inside the
    # 1.5× body, OUTSIDE the 1.0× body — so the hit proves the scaling.
    probe = QPointF(
        center.x() + center.x() / norm * unscaled_half * 1.35,
        center.y() + center.y() / norm * unscaled_half * 1.35,
    )
    assert comp._weekday_body_at(probe, R, 0.0, "mercury") is not None


def test_weekday_body_sits_at_the_romb_center_on_every_pointer():
    """The weekday-by-colors body rides the ROMB CENTER — half the star
    tip — identically on every pointer (owner 2026-07-15: this one slot
    always centers in its diamond, whatever the pointer). Pinned against
    the geometry: a diamond's diagonals cross at tip/2, and the body must
    sit farther out than the legacy 0.38 orbit (it was stuck inside)."""
    for pointer in ("hexa", "trio", "cross", "octa"):
        s = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
        expected = s.star.radius_fraction / 2.0
        assert weekday_body_orbit(s) == pytest.approx(expected), pointer
        # Farther out than the legacy 0.38 orbit it was stuck inside.
        assert weekday_body_orbit(s) > s.weekday_set.orbit_fraction, pointer


def test_classic_unit_wears_the_driving_slots_theme():
    """Owner 2026-07-15 (his 'ne razumem' point, pinned plainly): on
    the Seasons/Compass with TWO slots where the 1st chose another
    mode and the 2ND is weekday, the classic rotating unit is DRIVEN
    by the 2nd slot — so it wears the 2nd slot's own theme, not the
    1st's. Every other case keeps the weekday theme."""
    from app.controller import _classic_slot_theme
    from app.settings_store import Settings, replace

    base = replace(
        Settings(), weekday_theme="planets", info_slot_theme="greek",
    )
    # The 2nd slot drives the classic unit -> ITS theme dresses it.
    for pointer in ("cross", "octa"):
        driven = replace(
            base, pointer=pointer, show_octa_slot=True,
            weekday_slot="time", octa_slot="weekday",
        )
        assert _classic_slot_theme(driven)[0] == "greek", pointer
    # The 1st slot is weekday itself -> the weekday theme stays.
    plain = replace(
        base, pointer="octa", show_octa_slot=True, octa_slot="weekday",
    )
    assert _classic_slot_theme(plain)[0] == "planets"
    # Three slots: the Seasons lock the 1st on the classic unit ->
    # the weekday theme stays even with a weekday 2nd.
    third = replace(
        base, pointer="cross", show_octa_slot=True, show_third_slot=True,
        weekday_slot="time", octa_slot="weekday",
    )
    assert _classic_slot_theme(third)[0] == "planets"


def test_subdial_plate_recolors_to_every_finish(app):
    """Owner 2026-07-15 ('ti si taj koji treba da renderuješ zlatnu i
    bronzanu boju'), pinned: his ONE silver master serves every letter
    finish — silver returns the master as drawn, gold and bronze
    return disk-cached recolors of it; a seat with no plate of its
    own borrows the center plate."""
    from config import paths as _paths
    from render.assets import subdial_plate_file

    master = _paths.art_file(
        defaults.SUBDIAL_ART_DIR / "silver" / "center.png"
    )
    assert master.exists()
    assert subdial_plate_file("silver", "center") == master
    assert subdial_plate_file("silver", "h3") == master   # seat borrow
    version = defaults.SUBDIAL_RECOLOR_VERSION
    for finish in ("gold", "bronze"):
        plate = subdial_plate_file(finish, "center")
        assert plate is not None and plate != master, finish
        assert plate.name.endswith(
            f"_subdial{version}_{finish}.png"
        ), finish
        assert plate.exists(), finish
    # The "theme" plate style (owner A/B spec 2026-07-15): a clock
    # TINT recolors the tapisserie field — that pass runs even on the
    # exact finish, into its own cache entry.
    tinted = subdial_plate_file("silver", "center", tint="#5A3FA0")
    assert tinted is not None and tinted != master
    assert tinted.name.endswith(f"_subdial{version}_silver_5a3fa0.png")
    assert tinted.exists()
    # The metal stays INSIDE the radial bezel band (owner correction
    # 2026-07-15: his three side-by-side grabs showed the field
    # drinking bronze/gold) — the recolored interior must match the
    # master's interior exactly.
    import numpy as _np
    from PySide6.QtGui import QImage as _QImage

    def interior(path):
        image = _QImage(str(path)).convertToFormat(
            _QImage.Format.Format_RGBA8888
        )
        w, h = image.width(), image.height()
        stride = image.bytesPerLine() // 4
        data = _np.frombuffer(image.constBits(), dtype=_np.uint8)
        data = data.reshape(h, stride, 4)[:, :w, :]
        ys, xs = _np.mgrid[0:h, 0:w]
        r = _np.hypot(xs - (w - 1) / 2, ys - (h - 1) / 2) / (w / 2)
        return data[r < defaults.SUBDIAL_RECOLOR_RIM_RADIUS[0]]

    gold = subdial_plate_file("gold", "center")
    assert _np.array_equal(interior(gold), interior(master))


def test_dual_sunday_two_faces_on_compass_and_seasons(app, july_wednesday):
    """Owner corrections 2026-07-13: the SERVANT face is NOT
    Sunday-only — it stands at 24h all week like every other body
    (ghosted; opaque on Sunday) and speaks ITS OWN face text with its
    own name; the north sun speaks the RULER face; on the Seasons the
    Servant shares mercury's 180 seat by the standard priority; the
    Trinity/Prism single image carries BOTH plates in its legend.
    Every theme's dual art is ON DISK, colored variants too."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from render.layers import servant_holds_the_seat, sunday_dual_face

    # The art table is complete: all twelve themes + colored variants.
    # Canonical paths resolve through the ART SOURCE (owner 2026-07-14).
    from config import paths as _paths

    for theme in constants.WEEKDAY_THEMES:
        rel = defaults.WEEKDAY_DUAL_FILES[theme]
        if not _paths.art_file(
            defaults.WEEKDAY_ART_DIR / f"{rel}.png"
        ).exists():
            # ONLY the reworked Creeds may run dual-less: its Satanism
            # plate is pending owner art (2026-07-15) — the theme runs
            # single-faced until it lands.
            assert theme == "religion", theme
            continue
        assert theme in defaults.WEEKDAY_DUAL_NAMES
    for theme in constants.METAL_THEMES:
        # The colored dual is the SIBLING variant (owner restructure
        # 2026-07-14): the variant segment swaps to colored/.
        rel = defaults.WEEKDAY_DUAL_FILES[theme].replace(
            "/primary/", "/colored/"
        )
        assert _paths.art_file(
            defaults.WEEKDAY_ART_DIR / f"{rel}.png"
        ).exists(), theme
    # ...and so are the SPLIT FACE TEXTS (owner: no identical text on
    # the two faces) — every article set's sun carries distinct
    # ruler/servant prose.
    import json as _json

    from config import paths
    data = _json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    for article_set in set(constants.WEEKDAY_THEME_ARTICLES.values()):
        faces = data["articles"][article_set]["sun"].get("faces")
        assert faces is not None, article_set
        assert set(faces) == {"ruler", "servant"}, article_set
        assert faces["ruler"] != faces["servant"], article_set

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 12, 12, 0, tzinfo=tz)          # a Sunday
    day = build_day_context(
        now,
        astral.Observer(
            latitude=city["latitude"], longitude=city["longitude"]
        ),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    for pointer in ("octa", "cross"):
        skin = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer=pointer, solar_rotation=False),
        )
        assert skin.weekday_set.dual_asset is not None
        assert sunday_dual_face(skin)
        assert servant_holds_the_seat(skin, "sun"), pointer
        compositor = Compositor(skin, AssetCache())
        compositor.render_offscreen(360.0, 1.0, day, tick)
        orbit = 180.0 * skin.weekday_set.orbit_fraction
        south = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
        north = compositor.tooltip_at(180.0, 180.0 - orbit, 360.0)
        # Each face speaks its OWN name and text (owner: no more
        # identical Ruler text on the Servant).
        assert south is not None and "Eclipsed Sun" in south, pointer
        assert north is not None and "Eclipsed Sun" not in north, pointer
        # The hover embeds the SCALED cache copy of the servant plate
        # (performance round 2026-07-13) — pin the exact resolved uri.
        from render.assets import scaled_variant_file

        eclipse_uri = scaled_variant_file(
            defaults.WEEKDAY_ART_DIR
            / f"{defaults.WEEKDAY_DUAL_FILES['planets']}.png",
            2 * defaults.ARTICLE_IMAGE_WIDTH_PX,
        ).as_uri()
        assert eclipse_uri in south and eclipse_uri not in north
    # The SERVANT stands as a ghost on ORDINARY days too (a Wednesday):
    # on the Compass the free 24h seat is his; on the Seasons mercury
    # is TODAY on Wednesday and keeps his own seat.
    wed_day, wed_tick = july_wednesday
    octa = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="octa", solar_rotation=False),
    )
    assert servant_holds_the_seat(octa, "mercury")
    ghost = Compositor(octa, AssetCache())
    ghost.render_offscreen(360.0, 1.0, wed_day, wed_tick)
    orbit = 180.0 * octa.weekday_set.orbit_fraction
    tip = ghost.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert tip is not None and "Eclipsed Sun" in tip
    cross = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(Settings(), pointer="cross")
    )
    assert not servant_holds_the_seat(cross, "mercury")   # Wednesday: his seat
    # On a Friday Sunday is nearer than Wednesday — the Servant wins.
    assert servant_holds_the_seat(cross, "venus")
    # The Prism keeps one image — but its legend carries BOTH plates.
    hexa = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="hexa", solar_rotation=False),
    )
    assert not sunday_dual_face(hexa)
    prism = Compositor(hexa, AssetCache())
    prism.render_offscreen(360.0, 1.0, day, tick)
    center = prism.tooltip_at(180.0, 180.0, 360.0)
    assert center is not None and center.count("<img") == 2
    # center_only keeps the center for the body — no dual face.
    center_only = dataclasses.replace(
        octa,
        weekday_set=dataclasses.replace(
            octa.weekday_set, display_mode="center_only"
        ),
    )
    assert not sunday_dual_face(center_only)


# --- Shared-slot priority (owner rule) --------------------------------------------


def test_shared_slot_shows_the_next_upcoming_day():
    """Owner's example, Wednesday: of the pairs {Mon|Sat}, {Thu|Sun},
    {Tue|Fri} the visible bodies are Sat, Thu, Fri — the smaller forward
    distance from today wins."""
    assert visible_occupant(("moon", "saturn"), "mercury") == "saturn"
    assert visible_occupant(("jupiter", "sun"), "mercury") == "jupiter"
    assert visible_occupant(("mars", "venus"), "mercury") == "venus"


def test_today_always_wins_its_shared_slot():
    assert visible_occupant(("jupiter", "sun"), "sun") == "sun"
    assert visible_occupant(("jupiter", "sun"), "jupiter") == "jupiter"
    assert visible_occupant(("moon", "saturn"), "saturn") == "saturn"


def test_today_slot_positions():
    assert today_slot_theta("hexa", "sun") is None       # center, not an arm
    assert today_slot_theta("hexa", "mercury") == 180.0
    assert today_slot_theta("cross", "sun") == 0.0       # shares the top arm
    assert today_slot_theta("cross", "mercury") == 180.0  # Wednesday alone at the bottom
    assert today_slot_theta("octa", "sun") == 0.0
    assert today_slot_theta("octa", "mercury") == 135.0


# --- Star geometry -----------------------------------------------------------------


def test_cross_arms_borrow_the_octa_shape():
    """Owner spec (cross.png): the cross is the octa star WITHOUT the
    four diagonal arms — slim diamonds with gaps, not a fat 4-star."""
    half_angles = constants.POINTER_ARM_HALF_ANGLE_DEG
    assert half_angles["cross"] == half_angles["octa"]
    for pointer in ("hexa", "octa"):
        assert half_angles[pointer] == 180.0 / constants.POINTER_POINTS[pointer]


# --- Palette presets (owner: 5 — hexa/octa paint+light, cross seasons) -------------


def test_palette_presets_cover_every_pointer_and_style():
    for pointer, arms in constants.POINTER_POINTS.items():
        for style in constants.PALETTE_STYLES:
            palette = defaults.PALETTE_PRESETS[(pointer, style)]
            assert len(palette) == arms, (pointer, style)


def test_cross_wheels_are_seasons_paint_and_elements_light():
    """Owner 2026-07-17 (CANON §Seasons light): the cross PAINT stays the
    seasons temperaments palette; the cross LIGHT is now the FOUR ELEMENTS
    wheel, seating the Tetramorph — the two wheels DIFFER, and each hue
    lands on its canonical season arm (fire summer-top, earth autumn-right,
    water winter-bottom, air spring-left)."""
    assert defaults.PALETTE_PRESETS[("cross", "paint")] == (
        "#D9D900", "#D4330F", "#0A70D8", "#129412",
    )
    assert defaults.PALETTE_PRESETS[("cross", "light")] == (
        "#E8391E", "#6B8E3A", "#1E74D0", "#EFE9B0",
    )
    assert (
        defaults.PALETTE_PRESETS[("cross", "paint")]
        != defaults.PALETTE_PRESETS[("cross", "light")]
    )


def test_compass_octa_presets_are_the_approved_walks_and_ages():
    """Owner rework 2026-07-16: PAINT wears the Walks' materials, LIGHT
    wears the Eight Ages — the two presets must be the exact approved
    hex tuples (CANON.md) and must no longer be near-identical."""
    assert defaults.PALETTE_PRESETS[("octa", "paint")] == (
        "#F0C420", "#C87533", "#A02020", "#7A2E8E",
        "#262636", "#1F5FA8", "#3E8914", "#EDEDE0",
    )
    # Owner shift 2026-07-16: Death at midnight wears pure WHITE (in
    # the light register death goes INTO the light), the moonlight
    # silver moved to the Unborn, the mist to Birth; the rose retired.
    assert defaults.PALETTE_PRESETS[("octa", "light")] == (
        "#FFE800", "#FFB400", "#FF6A3C", "#9C6BD4",
        "#FFFFFF", "#C8D7F0", "#8FA8C8", "#7CE577",
    )
    assert (
        defaults.PALETTE_PRESETS[("octa", "paint")]
        != defaults.PALETTE_PRESETS[("octa", "light")]
    )


def test_palette_for_selects_the_skin_choice():
    paint = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    light = dataclasses.replace(paint, palette_style="light")
    assert palette_for(paint) == defaults.PALETTE_PRESETS[("octa", "paint")]
    assert palette_for(light) == defaults.PALETTE_PRESETS[("octa", "light")]


# --- Aurora (owner spec 2026-07-12) -------------------------------------------------


def test_slot_modes_are_real_everywhere():
    """The slot matrix (owner 2026-07-14): every 1st-slot mode is
    EFFECTIVE under every pointer — the matrix seats it — with ONE
    exception: the Seasons with all three slots lock the 1st on the
    weekday unit. The Chinese styles keep carrying their art folder
    and selective-swap metal."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    for pointer in ("hexa", "octa", "cross", "trio", "aurora"):
        for mode in ("ascendant", "zodiac", "chinese", "time", "seconds"):
            skin = apply_display_settings(
                defaults.DEFAULT_SKIN,
                replace(Settings(), pointer=pointer, weekday_slot=mode),
            )
            assert skin.weekday_slot == mode, (pointer, mode)
    locked = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), pointer="cross", weekday_slot="ascendant",
            show_octa_slot=True, show_third_slot=True,
        ),
    )
    assert locked.weekday_slot == "weekday"          # the Seasons lock
    # The Chinese styles resolve art folders + swap metals (Rule #5:
    # one mapping shared by every slot).
    assert constants.CHINESE_STYLE_ART_DIRS["gold"] == "chinese/primary"
    assert constants.CHINESE_STYLE_ART_DIRS["colored"] == "chinese/colored"
    assert "gold" in defaults.METAL_SWAP_TARGETS
    assert constants.ZODIAC_STYLE_ART_DIRS["colored"] == "astrology/colored"


def test_ring_tick_hover_reads_all_three_wheels(july_wednesday):
    """Owner spec 2026-07-12: hovering the ring tick band answers with
    the angle on every wheel — the 24h time, the year-wheel date (with
    the season, and the event on an anchor day) and the moon-cycle
    reading (new at the top, exactly as the Moon marker rides)."""
    import math as m

    from core.year_wheel import instant_at_marker_angle, year_marker_angle

    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    band = 180.0 * (
        defaults.TICK_HOVER_INNER_FRACTION
        + defaults.TICK_HOVER_OUTER_FRACTION
    ) / 2
    top = compositor.tooltip_at(180.0, 180.0 - band, 360.0)     # theta 0
    # Formatting round 2026-07-12: bold labels, the exact dial degree
    # and the day-period word on the time line; blank rows between the
    # D/Y/M sections.
    assert "12:00" in top and "Time:" in top
    assert "Angle:" in top and "0.0°" in top
    assert "&nbsp;" in top                     # the section separators
    # The top of the year wheel IS the summer solstice anchor.
    assert "Summer Solstice" in top and "Summer" in top
    assert "Date:" in top and "Season:" in top
    assert "June" in top and "2026" in top
    # Moon wheel: new at the top — 0% illumination, day 0 of the cycle.
    assert "0.0%" in top and "New Moon" in top
    theta = 250.0                              # ((250-180)/15)h = 04:40
    rad = m.radians(theta)
    side = compositor.tooltip_at(
        180.0 + band * m.sin(rad), 180.0 - band * m.cos(rad), 360.0
    )
    assert "04:40" in side and "250.0°" in side
    assert "February" in side and "Winter" in side   # 250 deg on the year wheel
    assert "Waning Gibbous" in side                  # 250/360 of the moon cycle
    # Inverse golden: the ANGLE round-trips exactly (the December
    # solstice angle legitimately has two dates a year apart — the
    # inverse picks the span's earlier one, so compare angles).
    for when, name in day.season_events:
        angle = year_marker_angle(when, day.year_anchors)
        back = instant_at_marker_angle(day.year_anchors, angle)
        assert abs(
            year_marker_angle(back, day.year_anchors) - angle
        ) % 360.0 < 0.01, name
    # Southern mirror: the same angle un-mirrors +180.
    south = instant_at_marker_angle(day.year_anchors, 0.0, southern=True)
    north_bottom = instant_at_marker_angle(day.year_anchors, 180.0)
    assert south == north_bottom


def test_aurora_bands_spread_the_day_hues_evenly():
    """The five DAY hues split the actual sunrise-sunset arc into equal
    bands — ALL of them visible on the shortest and the longest day
    alike — dawn wears the palette's first hue (blue), dusk its last
    (brown); the weekday slot is pinned to the dial bottom and the
    pointer is always solar-rotated."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral

    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from core.clock_state import build_day_context
    from core import angles
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.layers import aurora_bands, today_slot_theta

    palette = defaults.PALETTE_PRESETS[("aurora", "paint")]
    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    seasons = SeasonsRepository()
    moons = MoonPhaseRepository()
    for date in (datetime(2026, 6, 21, 12, 0, tzinfo=tz),      # longest day
                 datetime(2026, 12, 21, 12, 0, tzinfo=tz)):    # shortest day
        day = build_day_context(
            date, observer,
            seasons.year_anchors(date.year), moons.moon_window(date.year),
        )
        bands, solar_frame = aurora_bands(day.sun, palette, 0.55)
        assert solar_frame is False
        assert len(bands) == 7, date                 # dawn + 5 day + dusk
        assert bands[0][2] == palette[0]             # dawn blue
        assert bands[-1][2] == palette[-1]           # dusk brown
        # No separate twilight opacity under Aurora (owner: the color
        # carries the meaning) — the whole arc wears the day alpha.
        assert bands[0][3] == bands[-1][3] == 0.55
        day_bands = bands[1:-1]
        assert [hue for _, _, hue, _ in day_bands] == list(palette[1:-1])
        rise = angles.time_to_dial_angle(day.sun.sunrise)
        sets = angles.time_to_dial_angle(day.sun.sunset)
        span = (sets - rise) % 360.0
        widths = [end - start for start, end, _, alpha in day_bands]
        assert all(abs(w - span / 5) < 1e-9 for w in widths), date
        assert abs(day_bands[0][0] - rise) < 1e-9
        assert all(alpha == 0.55 for _, _, _, alpha in day_bands)
    # The weekday slot never rotates: pinned at the bottom, above Omega.
    for body in constants.WEEKDAY_BODIES:
        assert today_slot_theta("aurora", body) == 180.0
    # Aurora is ALWAYS solar-rotated, whatever the toggle says.
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="aurora", solar_rotation=False),
    )
    assert skin.solar_rotation is True
    assert skin.pointer == "aurora"


# --- Octa bottom slot ----------------------------------------------------------------


def test_bottom_slot_layer_stack_positions():
    """Owner dual-Sunday round 2026-07-12: on the Compass/Seasons the
    info slot is CENTERED and rides ABOVE the hands (the center
    occludes them — his accepted cost); in the pinned layouts it sits
    at the bottom BELOW the hands (the old bug report: the seconds
    hand passed behind the zodiac art); the Prism has none at all."""
    octa = _build_layers(dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa", show_octa_slot=True,
    ))
    lone = _build_layers(defaults.DEFAULT_SKIN)
    assert any(isinstance(layer, SlotLayer) for layer in octa)
    # One classic slot alone (the canon) builds NO seat layer at all.
    assert not any(isinstance(layer, SlotLayer) for layer in lone)
    slot_index = next(
        i for i, layer in enumerate(octa) if isinstance(layer, SlotLayer)
    )
    last_hand = max(
        i for i, layer in enumerate(octa) if isinstance(layer, HandLayer)
    )
    assert slot_index > last_hand            # centered -> above the hands
    pinned = _build_layers(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", show_pointer=False,
        )
    )
    slot_index = next(
        i for i, layer in enumerate(pinned) if isinstance(layer, SlotLayer)
    )
    first_hand = min(
        i for i, layer in enumerate(pinned) if isinstance(layer, HandLayer)
    )
    assert slot_index < first_hand           # bottom -> below the hands


@pytest.mark.parametrize("mode", constants.OCTA_SLOT_MODES)
def test_octa_slot_modes_render(july_wednesday, mode):
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa", octa_slot=mode,
        show_octa_slot=True,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash


@pytest.mark.parametrize("style", constants.ZODIAC_SLOT_STYLES)
def test_zodiac_slot_styles_render(july_wednesday, style):
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa",
        octa_slot="zodiac", info_slot_style=style, show_octa_slot=True,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200


@pytest.mark.parametrize("style", constants.CHINESE_SLOT_STYLES)
def test_chinese_slot_styles_render(july_wednesday, style):
    """Every Chinese dropdown style paints (owner 2026-07-12): text in
    two lines, colored from its own folder, gold/silver through the
    selective swap, bronze as drawn."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa",
        octa_slot="chinese", info_slot_style=style, show_octa_slot=True,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200


def test_seated_digital_slot_enlarges_but_stays_silent(july_wednesday):
    """The digital slot modes (owner 2026-07-14): a seated slot IS a
    hover target (the enlarge is an inherited trait) but keeps no
    tooltip of its own — and it paints without a crash."""
    from PySide6.QtCore import QPointF

    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_pointer=False, weekday_slot="time", show_octa_slot=False,
        ),
        AssetCache(),
    )
    image = compositor.render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    assert compositor._element_at(
        QPointF(0.0, orbit), 180.0, 0.0, "mercury"
    ) == "slot:1"
    tip = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert tip is None or "Time" not in str(tip)


def test_info_slot_weekday_wears_its_theme_metal(july_wednesday):
    """Owner 2026-07-12 (identical Weekday submenus): the info slot's
    second body carries ITS OWN theme's metal — resolved from
    theme_metals in apply_display_settings, run through the selective
    swap (or the colored/ art) on the info body alone."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), pointer="octa", octa_slot="weekday",
            info_slot_theme="greek", theme_metals={"greek": "gold"},
        ),
    )
    assert skin.info_slot_metal == "gold"
    assert skin.weekday_theme == "planets"       # the day slot untouched
    day, tick = july_wednesday
    image = Compositor(skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    assert image.pixelColor(180, 8).alpha() > 200


def test_seated_slot_wears_its_own_roster():
    """Owner 2026-07-15 ('u 1 slot grcki planetary u 2 slot grcki
    panteon'): the FIGURE roster is each slot's OWN pick, made in the
    theme dropdown beside the metals — the same theme can sit twice
    with two casts. Pinned: the built skin carries the per-slot
    rosters, the seats resolve through the shared pantheon_seat
    safety law (identity and plate travel together or not at all),
    and the seated hover speaks the seated figure even when both
    slots share the theme."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from config import paths as _paths
    from render.layers import slot_view

    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), pointer="octa", octa_slot="weekday",
            weekday_theme="greek", weekday_roster="planetary",
            info_slot_theme="greek", info_slot_roster="pantheon",
        ),
    )
    # Slot 1 stays the PLANETARY cast (no pantheon identities on the
    # weekday set) while slot 2 carries its own pantheon pick.
    assert skin.weekday_set.body_articles is None
    assert slot_view(skin, 1)[4] == "planetary"
    assert skin.info_slot_roster == "pantheon"
    assert slot_view(skin, 2)[4] == "pantheon"
    # The throne the 2nd slot draws on Sunday: Zeus, the pantheon
    # article, an existing plate (fame first — the reused primary
    # serves until the pantheon plate lands).
    seat = defaults.pantheon_seat("greek", "sun")
    assert seat is not None
    assert seat[1].startswith("Zeus")
    assert seat[2] == ("greek_pantheon", "sun")
    assert _paths.art_file(seat[0]).exists()
    # The safety law on every seat: a pantheon identity only ever
    # rides an existing pantheon plate — no seat may pair the
    # pantheon name with missing art.
    for body in constants.WEEKDAY_BODIES:
        resolved = defaults.pantheon_seat("greek", body)
        if resolved is not None:
            assert _paths.art_file(resolved[0]).exists(), body
    # The seated hover speaks the seated figure — same theme on both
    # slots, two casts (the same_unit shortcut must compare rosters).
    comp = Compositor(skin, AssetCache())
    pantheon_tip = comp._weekday_tooltip(
        "sun", active=False, theme="greek",
        slot_metal="bronze", roster="pantheon",
    )
    planetary_tip = comp._weekday_tooltip(
        "sun", active=False, theme="greek",
        slot_metal="bronze", roster="planetary",
    )
    assert "Zeus" in pantheon_tip and "Helios" not in pantheon_tip
    assert "Helios" in planetary_tip


# --- Render smoke -------------------------------------------------------------------


@pytest.mark.parametrize("pointer", ["cross", "octa", "trio"])
def test_pointer_variants_render(july_wednesday, pointer):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(2, 2).alpha() == 0           # corners stay transparent
    assert image.pixelColor(180, 8).alpha() > 200        # ring painted
    assert image.pixelColor(333, 180).alpha() > 200      # disc touches the ring


def test_trio_centers_the_sun_and_pairs_the_week():
    """Owner-approved trio pairing: Faith 12h = Jupiter+Saturn, Love 20h
    = Venus+Mars, Hope 4h = Moon+Mercury; Sunday's Sun in the center."""
    from render.layers import today_slot_theta

    assert today_slot_theta("trio", "sun") is None
    slots = dict(constants.POINTER_WEEKDAY_SLOTS["trio"])
    assert slots[0.0] == ("jupiter", "saturn")
    assert slots[120.0] == ("venus", "mars")
    assert slots[240.0] == ("moon", "mercury")


def test_trio_aura_thirds_center_on_the_arms(july_wednesday):
    """The trio's hues center on the arms like every pointer (owner
    correction 2026-07-10): upright, yellow spans 8h-16h, red 16h-24h,
    blue 0h-8h. Probed at 14h (yellow), 18h (red) and 6h (blue), away
    from the diamonds (arms sit at 0/120/240 deg)."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
        show_weekday=False, show_earth=False, show_moon=False,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    at_14h = image.pixelColor(234, 87)          # dial 30 deg, radius 0.6R
    assert at_14h.red() > at_14h.blue() + 30             # Faith yellow
    at_18h = image.pixelColor(288, 180)         # dial 90 deg
    assert at_18h.red() > at_18h.green() + 30            # Love red
    assert at_18h.red() > at_18h.blue() + 30
    at_6h = image.pixelColor(72, 180)           # dial 270 deg
    assert at_6h.blue() > at_6h.red() + 30               # Hope blue


def test_hover_rework_moon_and_earth_formats(july_wednesday):
    """Owner hover rework: raised ordinal suffixes, illumination to one
    decimal, the moonrise-moonset span and the season row (Belgrade,
    8 July 2026 = 189th day, 18th day of a 94-day summer)."""
    day, tick = july_wednesday
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    moon = compositor._moon_text()
    # Formatting round 2026-07-13: the phase NAME is the title — no
    # "Phase:" label anywhere, the name rides the bigger bold line.
    assert "Phase:</b>" not in moon
    assert "font-weight:bold" in moon
    assert "Waning" in moon or "Waxing" in moon or "Moon" in moon
    # The TRUE analytic illumination since Session 16 (the linear
    # interpolation read 42.8% here — up to 3 p.p. off mid-phase).
    assert "Illumination:</b> 43.3%" in moon   # one decimal (owner spec)
    assert "of 29.53" in moon and "&nbsp;" in moon
    # 8 Jul 2026 is a SKIP day in Belgrade — the moon sets at 13:53 but
    # does not rise (rises again just after midnight on the 9th); the
    # hover shows the side that exists.
    assert "Moonset:</b> 13:53" in moon
    earth = compositor._earth_text()
    assert "Date:</b> 8<sup>th</sup> July 2026" in earth
    assert "Season:</b>" in earth and "Sign:</b>" in earth
    assert "189<sup>th</sup> Day - 28<sup>th</sup> Week" in earth
    assert "Summer 18<sup>th</sup> of 94 Days" in earth
    assert "Cancer (21<sup>st</sup> June - 21<sup>st</sup> July)" in earth
    # A PRINCIPAL-phase day dates its instant like the weekday tooltip
    # and the <sup> markup must render, never print literally (owner
    # bug 2026-07-14).
    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    new_moon = datetime(2026, 7, 14, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    nm_day = build_day_context(
        new_moon, observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    nm_tick = build_tick_state(new_moon, nm_day)
    principal = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    principal.render_offscreen(360.0, 1.0, nm_day, nm_tick)
    title = principal._moon_text()
    assert "14<sup>th</sup> July - 11:43" in title
    assert "&lt;sup&gt;" not in title


def test_greetings_ride_the_top_ring_letter_only_when_unlocked(july_wednesday):
    """The hidden mode (owner 2026-07-14, placement round two; TOP-ONLY
    round 2026-07-16): unlocked, hovering the 12h ring LETTER — the band
    OUTSIDE the tick scale — opens the Four Greetings (verses + reading
    + the watchmaker's commentary, Serbian in every language); the TICKS
    at that angle keep their own day/year/moon reading, locked the
    letter stays silent, and the 24h (Omega) letter no longer answers
    this hover at all — that spot now belongs to the reveal-week
    double-click."""
    from PySide6.QtCore import QPointF

    day, tick = july_wednesday
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    letters = (
        defaults.TICK_HOVER_OUTER_FRACTION
        + defaults.GREETINGS_LETTER_OUTER_FRACTION
    ) / 2
    top = QPointF(0.0, -180.0 * letters)
    bottom = QPointF(0.0, 180.0 * letters)
    assert compositor._tick_tooltip(top, 180.0) is None      # locked
    compositor.set_hidden_unlocked(True)
    assert compositor._tick_tooltip(bottom, 180.0) is None   # Omega: silent
    poem = compositor._tick_tooltip(top, 180.0)
    assert "Četiri pozdrava" in poem
    assert "Dobar dan" in poem and "ponovi sve ovo" in poem
    assert "Komentar časovničara" in poem
    # The closing line maps the greetings to the dial: noon FAITH,
    # dawn HOPE (owner correction 2026-07-14) — the words wear the
    # legend highlight, so match around the markup.
    assert "podne" in poem and "vere" in poem
    assert "zora" in poem and "nade" in poem
    assert "zora povratka" not in poem


def test_omega_double_click_reveals_the_week(july_wednesday):
    """Omega double-click, REPURPOSED (owner seal 2026-07-16,
    superseding the same-day restart semantics): the hit region sits
    at the 24h letter band; the first double-click starts the
    REVEAL_WEEK_DURATION_S window (hands hidden, ghosts full), the
    NEXT one TOGGLES IT OFF — never a restart — and a fresh click
    afterwards starts a new window that expires on its own."""
    day, tick = july_wednesday
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)

    # The hit region is the FULL ROUND AREA centered on the Omega letter
    # (owner 2026-07-17, slika 9): the letter CENTER point lands (the old
    # annular wedge MISSED it — it sat just inside the ring band).
    # hit_omega takes WIDGET-LOCAL coordinates (the dial center sits at
    # (radius, radius), same convention as set_hover/tooltip_at).
    letter = defaults.RING_LETTER_RADIUS_FRACTION
    x, y = 180.0, 180.0 + 180.0 * letter        # bottom = 24h/Omega center
    assert compositor.hit_omega(x, y, 360.0)
    assert not compositor.hit_omega(180.0, 180.0 - 180.0 * letter, 360.0)  # top: not Omega

    assert not compositor.reveal_active()
    assert compositor.trigger_reveal_week(now=1000.0) is True   # started
    assert compositor.reveal_active(now=1000.0)
    assert compositor.reveal_active(now=1000.0 + defaults.REVEAL_WEEK_DURATION_S - 1)
    assert not compositor.reveal_active(now=1000.0 + defaults.REVEAL_WEEK_DURATION_S)

    # A second double-click INSIDE the window ends it (toggle-off).
    assert compositor.trigger_reveal_week(now=1100.0) is True
    assert compositor.trigger_reveal_week(now=1110.0) is False  # ended
    assert not compositor.reveal_active(now=1110.0)

    # And a fresh click after a toggle-off starts a NEW window that
    # expires by the timer again.
    assert compositor.trigger_reveal_week(now=1200.0) is True
    assert compositor.reveal_active(now=1200.0 + defaults.REVEAL_WEEK_DURATION_S - 1)
    assert not compositor.reveal_active(now=1200.0 + defaults.REVEAL_WEEK_DURATION_S)


def test_omega_hit_is_the_full_letter_circle(july_wednesday):
    """Owner slika 9 (2026-07-17): the Omega double-click hit is the FULL
    ROUND AREA at the 24h seat — a circle on the letter cell. The letter
    CENTER and points in the GAP between its strokes all land now; the OLD
    narrow annulus sat just OUTSIDE the ring band (>0.945R) and missed
    them. Points well outside the circle still do not answer."""
    day, tick = july_wednesday
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    radius = 180.0
    letter_r = radius * defaults.RING_LETTER_RADIUS_FRACTION
    # The letter centre lands — and it sits BELOW the old annulus's inner
    # bound (the exact spot the owner's screenshot kept missing).
    assert comp.hit_omega(180.0, 180.0 + letter_r, 360.0)
    assert defaults.RING_LETTER_RADIUS_FRACTION < defaults.TICK_HOVER_OUTER_FRACTION
    # A point ABOVE the centre (the gap between the strokes) lands too.
    inset = radius * defaults.OMEGA_HIT_RADIUS_FRACTION * 0.5
    assert comp.hit_omega(180.0, 180.0 + letter_r - inset, 360.0)
    # Well outside the circle — radially and laterally — does not.
    assert not comp.hit_omega(180.0, 180.0 + letter_r + radius * 0.3, 360.0)
    assert not comp.hit_omega(180.0 + radius * 0.3, 180.0 + letter_r, 360.0)
    # The TOP (12h) letter is never the Omega.
    assert not comp.hit_omega(180.0, 180.0 - letter_r, 360.0)


def test_reveal_week_raises_ghost_opacity_and_lifts_the_center_body(july_wednesday):
    """The reveal window (owner 2026-07-16) raises every non-active
    weekday body — the arm ghosts AND, on Trinity/Prism, the ghost
    center Sun — to full opacity, and the center Sun moves from
    WeekdayLayer (below the hands) to CenterBodyLayer (above them)."""
    import dataclasses as dc

    from PySide6.QtGui import QImage, QPainter

    from render.layers import CenterBodyLayer, RenderContext, WeekdayLayer

    day, tick = july_wednesday
    skin = dc.replace(defaults.DEFAULT_SKIN, pointer="trio")
    today = constants.WEEKDAY_BODIES[day.weekday_index]
    assert today != "sun"                       # Wednesday: Sun is a ghost

    cache = AssetCache()
    weekday_layer = WeekdayLayer(skin)
    center_layer = CenterBodyLayer(skin)

    def render(reveal_active: bool) -> tuple[float, float]:
        """Returns (weekday-layer alpha, center-layer alpha) sampled at
        the dial center, where only the ghost/reveal Sun can land."""
        image = QImage(361, 361, QImage.Format.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        painter.translate(180.5, 180.5)
        ctx = RenderContext(
            skin=skin, day=day, tick=None, radius=180.0, cache=cache,
            dpr=1.0, reveal_active=reveal_active,
        )
        weekday_layer.paint(painter, ctx)
        weekday_alpha = image.pixelColor(180, 180).alphaF()
        image.fill(0)
        center_layer.paint(painter, ctx)
        center_alpha = image.pixelColor(180, 180).alphaF()
        painter.end()
        return weekday_alpha, center_alpha

    weekday_alpha, center_alpha = render(reveal_active=False)
    assert weekday_alpha > 0.0                  # the ghost Sun, below hands
    assert center_alpha == 0.0                  # CenterBodyLayer skips it

    weekday_alpha, center_alpha = render(reveal_active=True)
    assert weekday_alpha == 0.0                 # WeekdayLayer steps aside
    assert center_alpha > 0.0                   # ...CenterBodyLayer lifts it


def test_every_pointer_wheel_pair_differs(app):
    """The wheel-pair is NEVER grayed now (owner 2026-07-17): EVERY armed
    pointer carries TWO DISTINCT wheels — the Seasons gained the Elements
    wheel, so the cross no longer collapses. The `_add_choice_group`
    primitive still honors an explicit `disabled` set (its contract)."""
    from app.controller import AppController
    from PySide6.QtWidgets import QMenu

    for pointer in ("trio", "cross", "hexa", "octa", "aurora", "calendar"):
        assert (
            defaults.PALETTE_PRESETS[(pointer, "paint")]
            != defaults.PALETTE_PRESETS[(pointer, "light")]
        )
    # The primitive still grays when asked (used nowhere for the palette
    # pair now, but the contract stands).
    menu, submenu = QMenu(), QMenu()
    actions = AppController._add_choice_group(
        None, menu, submenu,
        [(style, style) for style in constants.PALETTE_STYLES],
        constants.PALETTE_STYLES[0], lambda value: None,
        disabled=constants.PALETTE_STYLES,
    )
    assert all(not a.isEnabled() for a in actions)


def test_lunation_before_the_years_first_new_moon(app, july_wednesday):
    """Owner correction 2026-07-12: the year's 1st Moon = the first New
    Moon on/after Jan 1, so the early-January days still riding the
    December lunation read as the PREVIOUS year's LAST — 2025 began 12
    lunations (Dec 20 was its 12th), and 5 Jan 2026 is inside it. Only
    roughly one year in three reaches 13."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 1, 5, 12, 0, tzinfo=tz)
    day = build_day_context(
        now,
        astral.Observer(
            latitude=city["latitude"], longitude=city["longitude"]
        ),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    january = compositor._lunation_ordinal()
    assert "12" in january and "2025" in january
    # ...and a mid-year date counts within its own year (first 2026
    # New Moon 18 Jan; by 8 July SIX lunations have started — July's
    # own new moon has not fallen yet).
    july_day, july_tick = july_wednesday
    compositor.render_offscreen(360.0, 1.0, july_day, july_tick)
    july = compositor._lunation_ordinal()
    assert "6" in july and "2026" in july


def test_lunation_ordinal_reads_the_ring_side(app):
    """Owner logic 2026-07-13 (his 11 July screenshot): with the Moon
    on the dial's LEFT — second half of its cycle — the ring past 12h
    already belongs to the NEXT moon (hovering right of the top must
    read the 7th, not the running 6th); and December wraps into the
    new year's 1st."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )

    def ordinals(now):
        day = build_day_context(
            now, observer,
            SeasonsRepository().year_anchors(now.year),
            MoonPhaseRepository().moon_window(now.year),
        )
        tick = build_tick_state(now, day)
        assert tick.moon_fraction > 0.5     # premise: Moon on the LEFT
        compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        compositor.render_offscreen(360.0, 1.0, day, tick)
        return (
            compositor._lunation_ordinal(),
            compositor._lunation_ordinal(next_cycle=True),
        )

    current, following = ordinals(datetime(2026, 7, 11, 12, 0, tzinfo=tz))
    assert "6" in current and "2026" in current
    assert "7" in following and "2026" in following
    december, january = ordinals(datetime(2026, 12, 28, 12, 0, tzinfo=tz))
    assert "12" in december and "2026" in december
    assert "1<sup>st</sup>" in january and "2027" in january


def test_upright_mode_disarms_the_rotation(july_wednesday):
    """With solar rotation OFF the Star/Aura/Umbra stand upright — the
    render differs from the solar one (Belgrade July tilts ~+14 deg) and
    the today-slot hover sits at the exact unrotated angle."""
    day, tick = july_wednesday
    solar = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    upright_skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    upright_compositor = Compositor(upright_skin, AssetCache())
    upright = upright_compositor.render_offscreen(360.0, 1.0, day, tick)
    assert solar != upright
    # Wednesday=mercury sits at exactly 180 deg when upright: hover at the
    # unrotated slot center must hit it (orbit 0.38 * 180 px below center).
    # Hover rework: the ACTIVE body leads with the date and carries its
    # JUSTIFIED article (base + the active combination's paragraph).
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright_compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Wednesday, 8<sup>th</sup> July 2026" in tip
    assert "align='justify'" in tip
    assert "Mercury" in tip                    # the planets article text
    assert "align='center'" in tip           # hover text is centered (owner spec)


def _day_and_tick(latitude, longitude, tz_name):
    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    tz = ZoneInfo(tz_name)
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    day = build_day_context(
        now,
        astral.Observer(latitude=latitude, longitude=longitude),
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    return day, build_tick_state(now, day)


def test_southern_hemisphere_mirrors_the_arm_anchors(app):
    """Owner bug 2026-07-12 (Sydney screenshots): the year wheel runs
    MIRRORED in the south, so the TOP cardinal arm must read the
    DECEMBER solstice — their Summer Solstice — and the diagonals the
    mirrored quarters; the north keeps June at the top."""
    import dataclasses

    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    upright = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False
        ),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, sydney, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)
    assert "Summer Solstice" in top                  # the south's own name
    assert "December" in top                         # at the DECEMBER instant
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)
    assert "Winter Solstice" in bottom and "June" in bottom
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm
    assert "December" in diagonal or "January" in diagonal or "February" in diagonal


def test_southern_hemisphere_mirrors_the_diamond_signs(app):
    """Owner spec 2026-07-12: in the south the Earth passes the TOP
    diamond in December — its hover must name Sagittarius/Capricorn
    (with their universal dates) and highlight in the arm it actually
    occupies; the north keeps Gemini/Cancer at the top."""
    import dataclasses

    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, sydney, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond
    assert "Sagittarius" in top and "Capricorn" in top
    assert "December" in top                              # universal dates
    assert "Gemini" not in top


def test_climate_zones_name_the_events_and_seasons(app):
    """Owner decision: the south flips the seasonal event names (their
    Summer Solstice is the December one), the tropics use the neutral
    month names and read their WET/DRY halves instead of seasons."""
    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    assert sydney.zone == "south"
    names = [name for _, name in sydney.season_events]
    assert "Winter Solstice" in names and "Summer Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, sydney, tick)
    earth = compositor._earth_text()
    assert "Winter 18<sup>th</sup> of 94 Days" in earth   # July = their winter

    singapore, tick = _day_and_tick(1.3521, 103.8198, "Asia/Singapore")
    assert singapore.zone == "tropics"
    names = [name for _, name in singapore.season_events]
    assert "June Solstice" in names and "December Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, singapore, tick)
    earth = compositor._earth_text()
    assert "Wet season 111<sup>th</sup> of 186 Days" in earth


def test_trio_arm_hover_carries_the_virtue_article(july_wednesday):
    """The Trinity arm hover: theme, third, pair — then the virtue's
    article (owner request): Faith's speaks of the vertical line."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
            show_weekday=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    tip = compositor.tooltip_at(180.0, 72.0, 360.0)       # top arm = Faith
    assert "Faith" in tip and "08:00 - 16:00" in tip
    assert "Thursday" in tip and "Saturday" in tip
    assert "align='justify'" in tip and "vertical line" in tip


def test_day_and_night_period_hovers(july_wednesday):
    """Hover rework 5 & 6 + formatting round 2026-07-12: the sunlit arc
    answers with a bold Day title, labeled sun span and the twilight
    span under its With Twilight title — plus a mini Earth of the
    active region (day art on the day side, night art on the night
    side); the dark of the wheel mirrors it as Night / Complete Dark."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
            show_pointer=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    at_day = compositor.tooltip_at(234.0, 87.0, 360.0)     # dial 30 deg = 14h
    assert "<b>Day</b> 15h" in at_day
    assert "Sunrise:" in at_day and "Dusk:" in at_day
    assert "With Twilight" in at_day
    assert "<img" in at_day and "_day" in at_day           # the region's day face
    at_night = compositor.tooltip_at(162.0, 285.0, 360.0)  # near the bottom
    assert "<b>Night</b> 8h" in at_night
    assert "Sunset:" in at_night and "Dawn:" in at_night
    assert "Complete Dark" in at_night
    assert "<img" in at_night and "_night" in at_night


def test_twilight_band_format_and_tick_priority(july_wednesday):
    """Owner formatting round 2026-07-12: the twilight hover carries a
    bold Morning/Evening Twilight title, the labeled bounds and the
    band's span in minutes AND dial degrees (15°/h); where the ring
    tick band overlaps the twilight wedge (0.86–0.90 R), the CIRCLE
    outranks the wedge."""
    from core import angles

    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
            show_pointer=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    sun = day.sun
    theta = math.radians(
        (angles.time_to_dial_angle(sun.dawn)
         + angles.time_to_dial_angle(sun.sunrise)) / 2
    )

    def probe(fraction):
        return compositor.tooltip_at(
            180.0 + 180.0 * fraction * math.sin(theta),
            180.0 - 180.0 * fraction * math.cos(theta),
            360.0,
        )

    below_band = probe((defaults.TICK_HOVER_INNER_FRACTION - 0.02))
    assert "Morning Twilight" in below_band
    assert "Dawn:" in below_band and "Sunrise:" in below_band
    span = round((sun.sunrise - sun.dawn).total_seconds() / 60)
    assert f"{span} min - {span / 4:.2f}°" in below_band
    # The band names its astronomical definition (owner 2026-07-12).
    assert "Civil twilight" in below_band
    # Same wedge angle, but INSIDE the tick annulus (which overlaps the
    # aura up to 0.90 R): the circle answers, not the wedge.
    aura = compositor._skin.background.aura_radius_fraction
    in_band = probe((defaults.TICK_HOVER_INNER_FRACTION + aura) / 2)
    assert "Time:" in in_band and "Date:" in in_band


def test_arm_hover_only_inside_the_diamond(july_wednesday):
    """Owner bug report: the diamond hover must not swallow the wheel —
    BETWEEN the arms the Aura/Umbra day-night hover answers; the arm
    text appears only inside the drawn diamond polygon."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    on_arm = compositor.tooltip_at(180.0, 72.0, 360.0)     # top arm axis, 0.6R
    assert "Gemini" in on_arm                              # diamond answers
    # Dial 30 deg (between the 0 and 60 arms) at 0.7R: the gap — the
    # day hover answers there (14h is deep in the July daylight arc).
    between = compositor.tooltip_at(243.0, 70.9, 360.0)
    assert between is not None and "<b>Day</b> 15h" in between
    assert "Gemini" not in between and "Leo" not in between


def test_ghost_body_hover_shows_the_article_alone(july_wednesday):
    """Hover rework: ghost (non-current) bodies are hover targets too,
    showing their article WITHOUT the date line (owner spec) — probed on
    Jupiter's top slot on a Wednesday."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright.tooltip_at(180.0, 180.0 - orbit, 360.0)   # top slot = jupiter
    assert tip is not None and "align='justify'" in tip
    assert "Jupiter" in tip                    # its planets article
    assert "July 2026" not in tip              # no date line on ghosts


# --- Arm hovers (owner spec) -----------------------------------------------------------


def test_hexa_arm_hover_names_its_two_signs(july_wednesday):
    """Each hexa diamond spans exactly TWO zodiac signs (the owner's
    proposed list had Aquarius doubled on the bottom arm — corrected:
    bottom = Sagittarius + Capricorn), side by side as two COLUMNS
    (owner 2026-07-13): bold title with the date span, no glyph.
    Upright → no asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond, 0.6R up
    assert "Gemini" in top and "Cancer" in top and "*" not in top
    assert top.count("<td width=") == 2                   # two sign columns
    assert "♊" not in top and "♋" not in top              # titles wear no glyph
    assert "May" in top and "Jun" in top                  # each with its dates
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)      # below mercury's slot
    assert "Sagittarius" in bottom and "Capricorn" in bottom
    assert "Nov" in bottom and "Dec" in bottom


def test_octa_arm_hovers_events_and_seasons(july_wednesday):
    """Octa cardinals give the exact event instant; diagonals describe
    their season with dates, duration and the middle date. Solar
    rotation ON adds the imprecision asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False
        ),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    cardinal = upright.tooltip_at(180.0, 72.0, 360.0)     # top arm
    assert "Summer Solstice" in cardinal
    assert "2026" in cardinal and ":" in cardinal         # exact date + minutes
    assert "*" not in cardinal
    assert "h " in cardinal and "min" in cardinal         # day length line
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm, 0.6R
    assert "Summer" in diagonal and "Days)" in diagonal and "Heart" in diagonal
    assert "<sup>" in diagonal                            # raised ordinals
    solar = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"), AssetCache()
    )
    solar.render_offscreen(360.0, 1.0, day, tick)
    rotation = day.star_rotation
    theta = math.radians(45.0 + rotation)
    tilted = solar.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tilted is not None and "*" in tilted


def test_chinese_slot_hover(july_wednesday):
    """The info slot lives in the CENTER on the Compass (owner
    dual-Sunday round 2026-07-12) — the hover answers at (0,0)."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN,
            pointer="octa",
            solar_rotation=False,
            octa_slot="chinese",
            info_slot_style="text",
            show_octa_slot=True,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    tip = compositor.tooltip_at(180.0, 180.0, 360.0)      # dial center
    assert "Fire Horse" in tip and "2026" in tip and "2027" in tip
    assert "<br/>" in tip                     # name / span on separate lines


def test_twilight_band_beats_the_arm_hover(july_wednesday):
    """Owner: dawn/dusk info must never be shadowed by the star-arm
    hovers — the band keeps priority inside the star region."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    # Mid-dusk angle (sunset 20:25 → dusk 21:02), probe at 0.6R.
    sunset_angle = (
        (day.sun.sunset.hour * 3600 + day.sun.sunset.minute * 60) / 86400 * 360 + 180
    ) % 360
    dusk_angle = (
        (day.sun.dusk.hour * 3600 + day.sun.dusk.minute * 60) / 86400 * 360 + 180
    ) % 360
    theta = math.radians((sunset_angle + dusk_angle) / 2)
    tip = compositor.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tip is not None and "Sunset" in tip and "Dusk" in tip


# --- Umbra ----------------------------------------------------------------------------


def test_umbra_forms_structure():
    """Sectioned forms (owner spec): fine 30 sections/16 shades (his
    measured art), coarse 24/13 — single lightest/darkest + mirror
    pairs; the gradient form has no sections at all."""
    assert constants.UMBRA_SECTION_COUNTS == {"fine": 30, "coarse": 24}
    for form, sections in constants.UMBRA_SECTION_COUNTS.items():
        shades = sections // 2 + 1
        assert 1 + 2 * (shades - 2) + 1 == sections, form
    assert "gradient" in constants.UMBRA_FORMS
    assert "gradient" not in constants.UMBRA_SECTION_COUNTS


def test_umbra_ladders_hit_the_owner_values():
    """full = endpoint-inclusive over 0..255 (16 shades -> step 17);
    half = bin centers of the middle half 64..192 (16 -> 188..68 step 8,
    every value + its mirror = 256)."""
    full16 = umbra_ladder(16, "full")
    assert full16 == tuple(255 - 17 * k for k in range(16))
    half16 = umbra_ladder(16, "half")
    assert half16 == tuple(188 - 8 * k for k in range(16))
    assert all(a + b == 256 for a, b in zip(half16, reversed(half16)))
    # Owner spec: light = the bright half (128-255), dark = the dark
    # half (0-127) — bin centers, exact step 8 like "half".
    light16 = umbra_ladder(16, "light")
    assert light16 == tuple(252 - 8 * k for k in range(16))
    assert light16[-1] == 132 and all(0 <= v <= 255 for v in light16)
    dark16 = umbra_ladder(16, "dark")
    assert dark16 == tuple(124 - 8 * k for k in range(16))
    assert dark16[-1] == 4
    full13 = umbra_ladder(13, "full")
    assert full13[0] == 255 and full13[-1] == 0 and full13[6] == 128
    half13 = umbra_ladder(13, "half")
    assert half13[0] == 187 and half13[-1] == 69 and half13[6] == 128
    for ladder in (full16, half16, full13, half13):
        assert list(ladder) == sorted(ladder, reverse=True)
        assert len(set(ladder)) == len(ladder)


def test_event_glow_is_visible_even_over_the_yellow_wedge(app):
    """Owner report: no glow on the summer solstice. The solstice Earth
    always sits in the bright yellow wedge — the halo must remain
    visible there (white core). A/B: the same moment with and without
    the event window must differ around the marker."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        solstice_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    glowing = build_tick_state(solstice_noon, day)
    assert glowing.season_event == "Summer Solstice"
    # Clear BOTH events: on this date the moon's first quarter is also
    # within its window and its halo would contaminate the comparison.
    quiet = dc.replace(glowing, season_event=None, moon_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # Upright + solstice noon: the Earth RELOCATES to the ring band
    # centerline at the dial top (owner rework 2026-07-16). Probe
    # DIAGONALLY below-right of the relocated marker: inside the halo,
    # outside the disc, off the noon hand shafts on the vertical.
    marker_y = 270 - round(270 * defaults.GLOW_RING_RADIUS_FRACTION)
    lit = with_glow.pixelColor(289, marker_y + 33)
    plain = without.pixelColor(289, marker_y + 33)
    # The GOLDEN core lifts red and green over the background.
    assert lit.red() - plain.red() >= 8 or lit.green() - plain.green() >= 8


def test_window_margin_is_tight_and_never_clips():
    """MARGIN GAP diagnosis (owner slika 4, ROADMAP 15e). The reserved
    window half-extent must COVER the glowing hovered marker's full reach
    (never clips) and exceed it by ONLY the tiny anti-aliasing epsilon
    (tight — the old fixed 0.01 slab, ~7 px at a 720 dial, was the gap).
    Pinned at default AND at max-everything settings."""
    import dataclasses as dc

    from app.controller import apply_display_settings
    from app.settings_store import Settings

    for earth_scale, hover, letters in ((1.0, 1.2, 1.0), (2.0, 2.0, 2.0)):
        settings = dc.replace(
            Settings(), earth_scale=earth_scale, moon_scale=earth_scale,
            hover_enlarge=hover, ring_letter_scale=letters,
        )
        skin = apply_display_settings(defaults.DEFAULT_SKIN, settings)
        margin = defaults.dial_window_margin_fraction(skin)
        # The window half-extent as a fraction of the dial RADIUS.
        window_half = 1.0 + 2.0 * margin
        marker = max(skin.year_marker.scale, skin.year_marker.moon_scale)
        glow_reach = (
            defaults.GLOW_RING_RADIUS_FRACTION
            + marker * defaults.GLOW_RADIUS_SCALE * skin.hover_enlarge
        )
        letter_reach = (
            defaults.RING_LETTER_RADIUS_FRACTION
            + defaults.RING_LETTER_ART_SCALE * skin.ring_letter_scale
            * (1.0 + 2.0 * defaults.RING_LETTER_SHADOW_RADIUS)
        )
        reach = max(glow_reach, letter_reach)
        # Lower bound — never clips the drawn extent.
        assert window_half >= reach
        # Upper bound — the ONLY slack is 2·epsilon (tight, no waste).
        assert window_half - reach == pytest.approx(
            2.0 * defaults.DIAL_WINDOW_MARGIN_EPSILON
        )
        # That slack is ~2 px at a 720 dial (radius 360), not the old ~7.
        assert (window_half - reach) * 360.0 < 3.0


def test_window_margin_renders_glow_without_clipping(app):
    """The pixel side of the margin fix (owner slika 4): a glowing Earth
    rendered into the LIVE margin-sized window reaches near the edge but
    the outer frame stays fully transparent (never clipped). Hover is
    baked into the marker scale (hover_enlarge 1.0), so the drawn extent
    equals the margin's scale × glow reservation."""
    import dataclasses as dc

    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QImage, QPainter

    from app.controller import apply_display_settings
    from app.settings_store import Settings

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    solstice = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        solstice, observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    tick = build_tick_state(solstice, day)
    assert tick.season_event == "Summer Solstice"
    tick = dc.replace(tick, moon_event=None)     # only the Earth glows

    settings = dc.replace(
        Settings(), earth_scale=2.0, hover_enlarge=1.0,
        solar_rotation=False, show_moon=False,
    )
    skin = apply_display_settings(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        settings,
    )
    diameter = 720
    margin_px = round(diameter * defaults.dial_window_margin_fraction(skin))
    window = diameter + 2 * margin_px

    comp = Compositor(skin, AssetCache())
    comp.set_day(day)
    image = QImage(window, window, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(_Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(margin_px, margin_px)     # the widget's own offset
    comp.paint(painter, float(diameter), 1.0, tick)
    painter.end()

    # NEVER CLIPPED — the outermost 1-px frame is fully transparent.
    border_alpha = max(
        max(
            image.pixelColor(i, 0).alpha(),
            image.pixelColor(i, window - 1).alpha(),
            image.pixelColor(0, i).alpha(),
            image.pixelColor(window - 1, i).alpha(),
        )
        for i in range(window)
    )
    assert border_alpha == 0
    # TIGHT — the solstice Earth glow (at the top) reaches near the edge.
    top_row = next(
        y for y in range(window)
        if any(image.pixelColor(x, y).alpha() > 30 for x in range(window))
    )
    assert top_row <= 15


def test_moon_event_glow_renders(app):
    """Owner report: the moon glow "doesn't work" — pin that the halo
    really draws at a principal instant (it only shows within ±6 h of
    one; his Time Travel likely landed outside a window)."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    seasons = SeasonsRepository().year_anchors(2026)
    window = MoonPhaseRepository().moon_window(2026)
    reference = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    scout = build_day_context(reference, observer, seasons, window)
    instant, name = min(
        scout.moon_events, key=lambda event: abs(event[0] - reference)
    )
    local = instant.astimezone(tz)
    day = build_day_context(local, observer, seasons, window)
    glowing = build_tick_state(local, day)
    assert glowing.moon_event == name
    quiet = dc.replace(glowing, moon_event=None, season_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # At the instant the moon sits exactly on its cycle angle and
    # RELOCATES to the ring band centerline (owner rework 2026-07-16);
    # probe 30 px above the relocated marker center, off the disc.
    moon_angle = math.radians(glowing.moon_fraction * 360.0)
    orbit = 270 * defaults.GLOW_RING_RADIUS_FRACTION
    moon_x = 270 + orbit * math.sin(moon_angle)
    moon_y = 270 - orbit * math.cos(moon_angle)
    lit = with_glow.pixelColor(round(moon_x), round(moon_y) - 30)
    plain = without.pixelColor(round(moon_x), round(moon_y) - 30)
    assert (
        lit.red() - plain.red() >= 8
        or lit.green() - plain.green() >= 8
        or lit.blue() - plain.blue() >= 8
    )


def test_season_glow_relocates_to_ring_band_and_is_golden(app):
    """Turning-point rework (owner 2026-07-16): at a solstice the Earth
    marker relocates radially to the ring band centerline at its year
    angle, and its glow is GOLDEN (red/green lifted, blue barely). The
    OLD orbit (0.75R) carries no glow anymore."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        solstice_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    glowing = build_tick_state(solstice_noon, day)
    assert glowing.season_event == "Summer Solstice"
    quiet = dc.replace(glowing, season_event=None, moon_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # Summer solstice: year_angle 0 -> the top. Relocated to the ring
    # band centerline; probe 40 px above center (inside the halo, clear
    # of the ~30 px marker disc).
    band_y = 270 - round(270 * defaults.GLOW_RING_RADIUS_FRACTION)
    lit = with_glow.pixelColor(289, band_y + 33)
    plain = without.pixelColor(289, band_y + 33)
    dr = lit.red() - plain.red()
    dg = lit.green() - plain.green()
    db = lit.blue() - plain.blue()
    assert dr >= 8 and dg >= 8       # golden: red & green lift
    assert dr - db >= 8              # ... and clearly more than blue
    # The OLD orbit is now quiet: no glow relocation leaves it behind.
    old_y = 270 - round(270 * defaults.DEFAULT_SKIN.year_marker.orbit_fraction)
    old_lit = with_glow.pixelColor(289, old_y + 33)
    old_plain = without.pixelColor(289, old_y + 33)
    assert abs(old_lit.red() - old_plain.red()) <= 4


def test_moon_glow_relocates_to_ring_band_and_is_silver(app):
    """The Moon's phase glow relocates to the ring band centerline too,
    and its color is SILVER — all three channels lift together (blue is
    NOT suppressed the way the golden sun glow suppresses it)."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    seasons = SeasonsRepository().year_anchors(2026)
    window = MoonPhaseRepository().moon_window(2026)
    reference = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    scout = build_day_context(reference, observer, seasons, window)
    instant, name = min(
        scout.moon_events, key=lambda event: abs(event[0] - reference)
    )
    local = instant.astimezone(tz)
    day = build_day_context(local, observer, seasons, window)
    glowing = build_tick_state(local, day)
    assert glowing.moon_event == name
    quiet = dc.replace(glowing, moon_event=None, season_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    moon_angle = math.radians(glowing.moon_fraction * 360.0)
    orbit = 270 * defaults.GLOW_RING_RADIUS_FRACTION
    moon_x = 270 + orbit * math.sin(moon_angle)
    moon_y = 270 - orbit * math.cos(moon_angle)
    lit = with_glow.pixelColor(round(moon_x), round(moon_y) - 30)
    plain = without.pixelColor(round(moon_x), round(moon_y) - 30)
    dr = lit.red() - plain.red()
    dg = lit.green() - plain.green()
    db = lit.blue() - plain.blue()
    assert dr >= 8 and dg >= 8 and db >= 8      # silver: all channels lift
    # Silver keeps blue with the rest — unlike the golden sun glow which
    # suppresses blue by a wide margin.
    assert dr - db <= 6


def _render_window_frame(compositor, day, tick, dial_diameter):
    """Render the compositor at the WIDGET's full window size — the dial
    plus its transparent margin on every side — exactly like
    ClockWidget.paintEvent (translate by the margin, then paint the dial).
    An offscreen the size of the dial ALONE would clip the ring-band glow
    at the image edge and hide the very bug under test (owner 2026-07-16).
    """
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QPainter

    margin = round(
        dial_diameter * defaults.dial_window_margin_fraction(compositor._skin)
    )
    window = dial_diameter + 2 * margin
    compositor.set_day(day)
    image = QImage(window, window, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(margin, margin)
    compositor.paint(painter, float(dial_diameter), 1.0, tick)
    painter.end()
    return image, window, margin


def _max_border_alpha(image, window):
    """The largest alpha on the outermost ring of pixels — 0 means nothing
    reaches the window edge (no hard square cut)."""
    peak = 0
    for i in range(window):
        for x, y in ((i, 0), (i, window - 1), (0, i), (window - 1, i)):
            peak = max(peak, image.pixelColor(x, y).alpha())
    return peak


def test_full_moon_glow_never_clipped_at_window_edge(app):
    """Owner bug 2026-07-16: a full-moon glow at the BOTTOM of the ring
    was square-cut by the window edge. At the WIDGET's full window size the
    silver halo must fade to nothing INSIDE the window — no glow pixel may
    touch the outermost row/column — while still clearly rendering."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    seasons = SeasonsRepository().year_anchors(2026)
    moon = MoonPhaseRepository().moon_window(2026)
    reference = datetime(2026, 6, 15, 12, 0, tzinfo=tz)
    scout = build_day_context(reference, observer, seasons, moon)
    instant, _ = min(
        (event for event in scout.moon_events if event[1] == "Full Moon"),
        key=lambda event: abs(event[0] - reference),
    )
    local = instant.astimezone(tz)
    day = build_day_context(local, observer, seasons, moon)
    tick = build_tick_state(local, day)
    assert tick.moon_event == "Full Moon"          # fraction 0.5 -> the bottom
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    frame, window, margin = _render_window_frame(
        Compositor(skin, AssetCache()), day, tick, 540
    )
    assert _max_border_alpha(frame, window) <= 6   # halo faded; nothing clipped
    # ... and the halo really drew at the relocated ring-band bottom.
    radius = 270.0
    marker_y = radius + radius * defaults.GLOW_RING_RADIUS_FRACTION
    glow_probe_y = marker_y + radius * defaults.DEFAULT_SKIN.year_marker.moon_scale
    lit = frame.pixelColor(
        round(radius + margin + 12), round(glow_probe_y + margin)
    )
    assert lit.alpha() > 30


def test_earth_solstice_glow_never_clipped_even_when_hovered(app):
    """The worst case the window margin is DERIVED for (owner 2026-07-16):
    the larger Earth marker at a solstice, at the bottom of the ring, AND
    hover-enlarged to the slider maximum. Its golden halo reaches furthest
    of any glow yet must still fade inside the window edge."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    anchors = SeasonsRepository().year_anchors(2026)
    moon = MoonPhaseRepository().moon_window(2026)
    # anchors.instants[4] = the December solstice of 2026 -> Earth at the
    # bottom (year_angle 180).
    local = anchors.instants[4].astimezone(tz)
    day = build_day_context(local, observer, anchors, moon)
    tick = build_tick_state(local, day)
    assert tick.season_event == "Winter Solstice"
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, solar_rotation=False,
        hover_enlarge=constants.HOVER_ENLARGE_RANGE[1],
    )
    compositor = Compositor(skin, AssetCache())
    compositor._hovered = "earth"                  # force the enlarge factor
    frame, window, _ = _render_window_frame(compositor, day, tick, 540)
    assert _max_border_alpha(frame, window) <= 6


def test_window_margin_is_live_from_the_settings(app):
    """Owner slike 1–3 (2026-07-17): the transparent margin is COMPUTED
    from the user's ACTUAL settings, not a fixed max constant. At DEFAULT
    settings it shrinks below the old fixed 0.1465; at MAX-everything it
    grows past it — and the worst-case glow still fits at BOTH extremes."""
    from app.controller import build_skin
    from app.settings_store import Settings, replace

    default_margin = defaults.dial_window_margin_fraction(build_skin(Settings()))
    assert default_margin < 0.1465                 # the old fixed value
    max_skin = build_skin(
        replace(
            Settings(), earth_scale=2.0, moon_scale=2.0,
            hover_enlarge=2.0, ring_letter_scale=2.0,
        )
    )
    assert defaults.dial_window_margin_fraction(max_skin) > 0.1465
    # The boundary pixel test at the MAX extreme: the biggest possible
    # glow (Earth ×2 at a solstice, hover ×2, at the ring bottom) must
    # still fade INSIDE the window edge at the live (larger) margin.
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    anchors = SeasonsRepository().year_anchors(2026)
    moon = MoonPhaseRepository().moon_window(2026)
    local = anchors.instants[4].astimezone(tz)     # December solstice
    day = build_day_context(local, observer, anchors, moon)
    tick = build_tick_state(local, day)
    assert tick.season_event == "Winter Solstice"
    compositor = Compositor(
        dataclasses.replace(max_skin, solar_rotation=False), AssetCache()
    )
    compositor._hovered = "earth"                  # force the enlarge factor
    frame, window, _ = _render_window_frame(compositor, day, tick, 540)
    assert _max_border_alpha(frame, window) <= 6


def test_widget_z_mode_swaps_the_window_flags(app):
    """Owner 2026-07-17 (ROADMAP 15d): set_z_mode swaps the always-on-
    bottom / always-on-top hint in place, keeping the frameless-tool base;
    unchanged is a no-op."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMenu

    from app.widget import ClockWidget

    widget = ClockWidget(360, QMenu(), None)
    try:
        flags = widget.windowFlags()
        assert flags & Qt.WindowType.WindowStaysOnBottomHint     # default
        widget.set_z_mode("top")
        flags = widget.windowFlags()
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        assert not (flags & Qt.WindowType.WindowStaysOnBottomHint)
        assert flags & Qt.WindowType.FramelessWindowHint         # base kept
        assert flags & Qt.WindowType.Tool
        widget.set_z_mode("bottom")
        assert widget.windowFlags() & Qt.WindowType.WindowStaysOnBottomHint
    finally:
        widget.close()


def test_half_contrast_renders_a_gentler_night(july_wednesday):
    """The bottom of the dial (solar midnight, no hue overlay in July) is
    near-black on full contrast and clearly lifted on half."""
    day, tick = july_wednesday
    full = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    half_skin = dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="half")
    half = Compositor(half_skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    # 104 px below center: inside the darkest sections (plus the star's
    # slight solar rotation), BELOW the enlarged south body slot and away
    # from diamond borders.
    full_pixel = full.pixelColor(180, 284)
    half_pixel = half.pixelColor(180, 284)
    assert full_pixel.alpha() > 200 and half_pixel.alpha() > 200
    assert full_pixel.red() < 50
    assert half_pixel.red() >= 55
    # Light contrast lifts the night far higher (window 128-255); dark
    # keeps it near-black (window 0-127).
    light = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="light"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    dark = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="dark"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    assert light.pixelColor(180, 284).red() >= 120
    assert dark.pixelColor(180, 284).red() < 50


@pytest.mark.parametrize("form", ["coarse", "gradient"])
def test_umbra_forms_render(july_wednesday, form):
    day, tick = july_wednesday
    upright = dataclasses.replace(
        defaults.DEFAULT_SKIN, umbra_form=form, solar_rotation=False
    )
    image = Compositor(upright, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    assert image.pixelColor(180, 8).alpha() > 200
    if form == "gradient":
        # Upright: lightest straight up, darkest straight down; the
        # sweep must be mirror-symmetric. Probes at 0.62R: top/bottom on
        # the vertical, the mirror pair at dial angles 150/210 deg —
        # night side in July, so pure Umbra with no Aura wedge over it.
        top = image.pixelColor(180, 68).red()
        bottom = image.pixelColor(180, 292).red()
        night_right = image.pixelColor(236, 277).red()
        night_left = image.pixelColor(124, 277).red()
        assert bottom < 40 < top                 # dark bottom, light top...
        assert abs(night_left - night_right) <= 2    # ...mirrored sides


def test_weekday_center_body_matches_the_diamond_bodies(app, july_wednesday, monkeypatch):
    """Owner 2026-07-18 (his two screenshots): the hexa/trio CENTER body
    is the SAME size as the diamond bodies — in the normal state AND
    during the Omega reveal. Normal drew center_scale x the seat factor
    (~170 px against 144 px diamonds on his dial); the reveal center
    dropped the seat factor and SHRANK (~114 px). One formula now:
    `weekday_body_size`, shared by the slots, the ghost center and the
    above-the-hands center pass."""
    import render.layers as layers
    from render.layers import CenterBodyLayer, RenderContext, WeekdayLayer

    day, tick = july_wednesday
    calls = []
    monkeypatch.setattr(
        layers, "draw_weekday_body",
        lambda painter, ctx, body, pos, size, opacity: calls.append(
            ((pos.x(), pos.y()), size)
        ),
    )
    for pointer in ("hexa", "trio"):
        skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
        for reveal in (False, True):
            calls.clear()
            ctx = RenderContext(
                skin=skin, day=day, tick=tick, radius=180.0,
                cache=AssetCache(), dpr=1.0, reveal_active=reveal,
            )
            WeekdayLayer(skin).paint(None, ctx)
            CenterBodyLayer(skin).paint(None, ctx)
            centers = {size for pos, size in calls if pos == (0.0, 0.0)}
            slots = {size for pos, size in calls if pos != (0.0, 0.0)}
            assert len(centers) == 1, (pointer, reveal)   # the center drew
            assert len(slots) == 1, (pointer, reveal)     # diamonds uniform
            assert centers == slots, (pointer, reveal)    # center == diamonds


def test_hover_warm_sweep_speaks_through_the_real_dispatch(app, july_wednesday, monkeypatch):
    """Owner 2026-07-18 (asked twice): the background sweep pre-builds
    the hover articles through the REAL tooltip dispatch. On a reduced
    grid most probes speak (the day/night period answers everywhere),
    a second sweep is a warm no-op with the same coverage, and
    `should_stop` aborts the rings immediately."""
    day, tick = july_wednesday
    monkeypatch.setattr(defaults, "HOVER_WARM_ANGLE_STEPS", 24)
    monkeypatch.setattr(defaults, "HOVER_WARM_RADIAL_STEPS", 6)
    monkeypatch.setattr(defaults, "HOVER_WARM_RING_PAUSE_S", 0.0)
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)      # day + tick installed
    spoken = comp.warm_hover_articles(360.0)
    assert spoken > 24                    # the sweep reached real articles
    assert comp.warm_hover_articles(360.0) == spoken  # warm re-run, same coverage
    assert comp.warm_hover_articles(360.0, should_stop=lambda: True) <= 1
