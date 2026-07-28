"""THE ROSE — the seventh pointer (owner seal 2026-07-27, CUBE.md §The
Rose of the Twenty-Four).

Every sealed behavior pinned golden: the three-star geometry and its
z-order on both wheels, the palette that is also the year, the weekday
color law with its dual Sunday, the daylight switch — and the
REGRESSION PIN that the Rose never comes back as a ring preset.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings
from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from core.year_wheel import year_marker_angle
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    arm_half_deg,
    daylight_active,
    dial_point,
    palette_for,
    rose_star_offsets,
    rose_star_set,
    ruler_seat_angle,
    servant_seat_angle,
    sunday_dual_face,
    weekday_body_orbit,
    weekday_slots,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _skin(wheel="paint", **overrides):
    return build_skin(
        dataclasses.replace(
            Settings(), pointer="rose", palette_style=wheel, **overrides
        )
    )


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


# --- The Rose is a POINTER, and never again a ring ---------------------------------


def test_the_rose_ring_preset_is_gone_for_good():
    """REGRESSION PIN (owner correction 2026-07-27). Session 20 built
    the Rose as a RING PRESET because CUBE.md had mis-transcribed the
    owner's POINTER spec and stamped it SEALED. Every trace of that is
    deleted — no card, no `rose` flag on the card or the RingSpec, no
    ray geometry. If any of this reappears, the wrong thing is being
    rebuilt."""
    assert "Rose" not in ring_presets()
    for card in ring_presets().values():
        assert "rose" not in card
    assert not hasattr(defaults.DEFAULT_SKIN.ring, "rose")
    assert not hasattr(defaults, "ROSE_RAY_HALF_DEG")
    assert not hasattr(defaults, "ROSE_RAY_BORDER")


def test_the_rose_is_the_seventh_pointer_with_two_wheels():
    assert constants.POINTER_POINTS["rose"] == 8
    assert len(constants.POINTER_POINTS) == 7
    assert constants.POINTER_DISPLAY_NAMES["rose"] == "Rose"
    # Two wheels, not three — the Rose is not a Cube-wheel pointer.
    assert constants.palette_styles_for("rose") == ("paint", "light")
    assert constants.POINTER_PALETTE_LABELS["rose"] == ("Legacy", "Prophecy")
    assert "rose" not in constants.CUBE_WHEEL_POINTERS


# --- The three stars ----------------------------------------------------------------


@pytest.mark.parametrize(
    "wheel,expected",
    [("paint", (-30.0, -15.0, 0.0)), ("light", (-15.0, 15.0, 0.0))],
)
def test_star_offsets_and_draw_order(app, wheel, expected):
    """CUBE.md §The Rose: three octa stars 15° apart, listed in DRAW
    order (bottom of the z-stack first)."""
    assert rose_star_offsets(_skin(wheel)) == expected


@pytest.mark.parametrize("wheel", ["paint", "light"])
def test_the_zero_star_is_always_topmost(app, wheel):
    """The dominant, fully visible arm must point at true 12h on BOTH
    wheels — the dial keeps its own axis (owner 2026-07-27: "prvobitni
    offset u krupnom kadru otpada — idemo na simetriju")."""
    assert rose_star_offsets(_skin(wheel))[-1] == 0.0


def test_prophecy_rides_the_future_over_the_past(app):
    """Owner: on the symmetric wheel the PAST lies deepest, the FUTURE
    rides over it, the present covers both."""
    bottom, middle, top = rose_star_offsets(_skin("light"))
    assert rose_star_set(bottom) == "historical"
    assert rose_star_set(middle) == "archetypal"   # +15° — the future
    assert rose_star_set(top) == "modern"
    assert middle == 15.0


def test_legacy_leans_wholly_behind_the_hour(app):
    """Legacy's myth is the DEEPEST past and lies lowest."""
    bottom, middle, top = rose_star_offsets(_skin("paint"))
    assert (bottom, middle, top) == (-30.0, -15.0, 0.0)
    assert rose_star_set(bottom) == "archetypal"
    assert rose_star_set(middle) == "historical"
    assert rose_star_set(top) == "modern"


def test_both_wheels_share_the_two_anchors(app):
    """Only the MYTH star moves between the wheels — Modern stays on
    the true hours, Historical one ray back."""
    for wheel in ("paint", "light"):
        offsets = rose_star_offsets(_skin(wheel))
        assert rose_star_set(0.0) == "modern"
        assert -15.0 in offsets and rose_star_set(-15.0) == "historical"


def test_the_arms_keep_the_octa_shape(app):
    """Three OCTA stars: 45°-wide arms on a 15° pitch, so neighbors
    OVERLAP exactly as the owner draws them."""
    assert arm_half_deg(_skin()) == 22.5
    assert 2 * arm_half_deg(_skin()) > 15.0


# --- The palette IS the year --------------------------------------------------------


@pytest.mark.parametrize("wheel", ["paint", "light"])
def test_both_wheels_wear_the_one_rose_palette(app, wheel):
    """The wheel turns geometry and figures, never colors (Rule #5 —
    ONE tuple, shared with the Character wheel)."""
    assert palette_for(_skin(wheel)) is defaults.ROSE_PALETTE
    assert defaults.PALETTE_PRESETS[("octa", "cube")] is defaults.ROSE_PALETTE
    assert len(defaults.ROSE_PALETTE) == 8


def test_the_cardinals_are_the_turning_points_the_year_wheel_computes():
    """CUBE.md §The Sunday axis: the Rose's four cardinals land
    exactly where `core.year_wheel` puts the sun's turning points —
    summer solstice yellow up, autumn equinox red right, winter
    solstice purple down, spring equinox blue left."""
    anchors = SeasonsRepository().year_anchors(2026)
    # instants: [Dec solstice before, spring eq, June solstice,
    #            autumn eq, Dec solstice, spring eq after]
    for instant, angle in (
        (anchors.instants[2], 0.0),      # June solstice   — 12h yellow
        (anchors.instants[3], 90.0),     # autumn equinox  — 18h red
        (anchors.instants[4], 180.0),    # Dec solstice    — 24h purple
        (anchors.instants[1], 270.0),    # spring equinox  — 06h blue
    ):
        assert year_marker_angle(instant, anchors) == pytest.approx(angle)
    labels = constants.POINTER_ARM_LABELS["rose"]
    assert labels[0] == "Summer Solstice"      # 0°   — yellow
    assert labels[2] == "Autumn Equinox"       # 90°  — red
    assert labels[4] == "Winter Solstice"      # 180° — purple
    assert labels[6] == "Spring Equinox"       # 270° — blue


def test_the_sabbath_axis_keeps_the_cube_pole_partners():
    """Blue and red are the only hues that are not a season — they are
    Sunday's. On the Rose the Cube's axes keep their exact pole
    PARTNERS; blue simply wears cyan and red wears rose, the SAME shift
    the weekday law makes (CUBE.md §The Sunday axis)."""
    yellow, orange, red, rose, purple, cyan, blue, green = defaults.ROSE_PALETTE
    # Y is untouched: yellow ↔ purple-gray, still opposite (12h ↔ 24h).
    assert purple == defaults.MOON_GRAY_VIOLET
    # Every axis is a DIAGONAL — opposite arms, 180° apart.
    for a, b in ((yellow, purple), (orange, cyan), (rose, green), (red, blue)):
        index_a = defaults.ROSE_PALETTE.index(a)
        index_b = defaults.ROSE_PALETTE.index(b)
        assert abs(index_a - index_b) == 4


# --- The weekday color law ----------------------------------------------------------


def test_the_weekday_seats_follow_the_colour_law(app):
    """CUBE.md §The weekday law: the seat is the HUE. Prism paint's
    canon with the two Sunday hues lightened, because Sunday needs
    blue and red for its own two faces."""
    hues = defaults.ROSE_PALETTE
    expected = {
        0.0: ("jupiter", hues[0]),      # 12h yellow — Thursday
        45.0: ("mars", hues[1]),        # 15h orange — Tuesday
        90.0: ("sun", hues[2]),         # 18h red    — Sunday, the Ruler
        135.0: ("venus", hues[3]),      # 21h rose   — Friday
        180.0: ("mercury", hues[4]),    # 24h purple — Wednesday
        225.0: ("moon", hues[5]),       # 03h cyan   — Monday
        315.0: ("saturn", hues[7]),     # 09h green  — Saturday
    }
    seats = dict(weekday_slots(_skin()))
    assert set(seats) == set(expected)
    for angle, (body, _hue) in expected.items():
        assert seats[angle] == (body,)


def test_thursday_and_wednesday_keep_their_canonical_colour_seats(app):
    """The whole reason Sunday moved to 06h/18h (owner 2026-07-27)."""
    seats = dict(weekday_slots(_skin()))
    assert seats[0.0] == ("jupiter",)      # THU on the yellow 12h arm
    assert seats[180.0] == ("mercury",)    # WED on the purple 24h arm


def test_sunday_holds_two_seats_on_the_blue_red_axis(app):
    """The Ruler on red at 18h, the Servant on blue at 06h — 6+6+6.
    The Servant's seat is absent from the slot table exactly as 24h is
    on the Compass: it is his alone."""
    skin = _skin()
    assert servant_seat_angle(skin) == 270.0            # 06h, blue
    assert 270.0 not in dict(weekday_slots(skin))
    assert dict(weekday_slots(skin))[90.0] == ("sun",)  # 18h, red
    # The two seats are opposite each other, like every other axis.
    assert abs(270.0 - 90.0) == 180.0


def test_the_compass_servant_seat_is_untouched(app):
    """The Rose moved its OWN servant only — the Compass and the
    Seasons keep 24h (Rule #6: one reader, no behavior drift)."""
    for pointer in ("octa", "cross"):
        skin = build_skin(dataclasses.replace(Settings(), pointer=pointer))
        assert servant_seat_angle(skin) == constants.SOUTH_SLOT_ANGLE


def test_the_rose_carries_the_dual_sunday_face(app):
    assert sunday_dual_face(_skin()) is True


def test_rose_sunday_hover_fires_on_the_sabbath_seat_not_the_legacy_bottom(app):
    """REGRESSION (owner screenshot 2026-07-28): the two Sunday faces
    DRAW on the Sunday axis (Servant blue 06h/270°, Ruler red 18h/90°),
    but `Compositor._element_at`/`_weekday_body_at` used to hardcode
    `constants.SOUTH_SLOT_ANGLE` (24h/180°, the Compass/Seasons seat)
    for the Servant hit-test instead of calling `servant_seat_angle` —
    so the Rose's hover fired at the legacy bottom instead of its own
    drawn blue arm, and blanked Wednesday's real 24h/purple seat on
    Sundays in the process."""
    skin = _skin()
    compositor = Compositor(skin, AssetCache())
    radius = 180.0
    orbit = radius * weekday_body_orbit(skin)

    # The legacy bottom seat (24h/180°) must NOT answer as the Servant —
    # on the Rose that arm is Wednesday's own purple seat, undisturbed.
    legacy_point = dial_point(constants.SOUTH_SLOT_ANGLE, orbit)
    assert compositor._element_at(legacy_point, radius, 0.0, "sun") != (
        "sun_servant"
    )
    assert compositor._element_at(
        legacy_point, radius, 0.0, "sun"
    ) == "body:mercury"

    # The Rose's OWN seat — the blue 06h/270° Sunday arm — must answer.
    sabbath_point = dial_point(servant_seat_angle(skin), orbit)
    assert compositor._element_at(
        sabbath_point, radius, 0.0, "sun"
    ) == "sun_servant"


# --- The Duality-Axes config (owner decree 2026-07-28) ------------------------------


def test_the_blind_default_carries_over_for_every_undeclared_theme(app):
    """`config.constants.DUALITY_RULER_ON_COLD_POLE` lists only the
    Sacred-Axis proof case — every OTHER dual theme keeps the Rose's
    plain default: Ruler on red (18h), Servant on blue (06h)."""
    for theme in ("greek", "norse", "profession", "wolf", "bible_dark"):
        skin = _skin(weekday_theme=theme)
        assert ruler_seat_angle(skin) == 90.0
        assert servant_seat_angle(skin) == 270.0


def test_creeds_flips_to_the_sacred_axis_colours(app):
    """The proof case (CUBE.md §The Thirteen Axes — the Duality-Axes
    config): Christianity is the Sacred Axis's LUMINOUS COLD member and
    must pull to blue; Satanism the FALLEN WARM one and must pull to
    red — the reverse of the blind default, and of what the Rose drew
    before this config existed."""
    skin = _skin(weekday_theme="religion")
    assert "religion" in constants.DUALITY_RULER_ON_COLD_POLE
    assert ruler_seat_angle(skin) == 270.0     # Christianity — blue, 06h
    assert servant_seat_angle(skin) == 90.0    # Satanism — red, 18h
    # The Ruler's own drawn/hovered slot in the weekday table moves
    # with him — only the Servant's, drawn separately, never lived
    # there at all.
    assert dict(weekday_slots(skin))[270.0] == ("sun",)
    assert 90.0 not in dict(weekday_slots(skin))


def test_the_vertical_axis_never_flips(app):
    """CUBE.md: only the horizontal (Rose) axis is per-theme — the
    Compass/Seasons' vertical Ruler-at-top default is unconditional,
    even for creeds (owner decree 2026-07-28)."""
    for pointer in ("octa", "cross"):
        skin = build_skin(
            dataclasses.replace(
                Settings(), pointer=pointer, weekday_theme="religion",
            )
        )
        assert servant_seat_angle(skin) == constants.SOUTH_SLOT_ANGLE


def test_creeds_flip_carries_no_art_or_name_swap(app):
    """The flip moves ARMS, never identities: Christianity stays the
    RULER (its own name, plate and hover text), Satanism stays the
    SERVANT — only which arm each rides changes."""
    assert defaults.WEEKDAY_DUAL_NAMES["religion"] == (
        "Christianity", "Satanism",
    )
    assert defaults.WEEKDAY_THEME_FILES["religion"]["sun"] == "Christianity"


# --- The daylight switch ------------------------------------------------------------


def test_only_the_rose_and_the_calendar_carry_the_daylight_switch(app):
    """Owner 2026-07-27: those two are read as a WHEEL first and a
    clock second. Every other pointer always runs day/night, and the
    stored setting is ignored — never rewritten — on them, so the
    choice survives a pointer switch."""
    assert constants.DAYLIGHT_SWITCH_POINTERS == ("calendar", "rose")
    for pointer in constants.POINTER_POINTS:
        skin = build_skin(
            dataclasses.replace(Settings(), pointer=pointer, daylight=False)
        )
        expected = pointer not in constants.DAYLIGHT_SWITCH_POINTERS
        assert daylight_active(skin) is expected
        assert skin.daylight is False           # the setting survives


def test_daylight_off_paints_the_whole_star(app):
    """With the switch off the night half stands in full color instead
    of falling back to borders alone."""
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))

    def night_pixels(daylight: bool) -> int:
        skin = _skin("light", solar_rotation=False, daylight=daylight)
        image = Compositor(skin, AssetCache()).render_offscreen(
            600.0, 1.0, day, tick
        )
        purple = defaults.MOON_GRAY_VIOLET.upper()
        return sum(
            1
            for x in range(image.width())
            for y in range(image.height())
            if image.pixelColor(x, y).name().upper() == purple
        )

    assert night_pixels(False) > night_pixels(True)


# --- The drawn star -----------------------------------------------------------------


@pytest.mark.parametrize("wheel", ["paint", "light"])
def test_every_hue_of_every_star_reaches_the_dial(app, wheel):
    """Offscreen pin: the three stars really paint — all eight hues
    show, on both wheels, with the daylight law off so the night half
    cannot hide any of them."""
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    skin = _skin(wheel, solar_rotation=False, daylight=False)
    image = Compositor(skin, AssetCache()).render_offscreen(720.0, 1.0, day, tick)
    found = {
        image.pixelColor(x, y).name().upper()
        for x in range(image.width())
        for y in range(image.height())
        if image.pixelColor(x, y).alpha() > 200
    }
    for hue in defaults.ROSE_PALETTE:
        assert hue.upper() in found, f"{wheel}: {hue} never painted"
