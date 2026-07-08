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
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.layers import (
    BottomSlotLayer,
    HandLayer,
    palette_for,
    today_slot_theta,
    umbra_ladder,
    visible_occupant,
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
        if pointer == "hexa":
            seated.append("sun")             # the hexa layout centers the Sun
        assert sorted(seated) == sorted(constants.WEEKDAY_BODIES), pointer


def test_slot_angles_sit_on_the_pointer_arms():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        arm_step = 360.0 / constants.POINTER_POINTS[pointer]
        for angle, _ in slots:
            assert angle % arm_step == 0.0, (pointer, angle)


def test_octa_reserves_the_bottom_arm_for_the_info_slot():
    occupied = [angle for angle, _ in constants.POINTER_WEEKDAY_SLOTS["octa"]]
    assert constants.OCTA_TIME_SLOT_ANGLE not in occupied


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


def test_cross_serves_one_seasons_palette_under_both_styles():
    assert (
        defaults.PALETTE_PRESETS[("cross", "paint")]
        == defaults.PALETTE_PRESETS[("cross", "light")]
    )


def test_palette_for_selects_the_skin_choice():
    paint = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    light = dataclasses.replace(paint, palette_style="light")
    assert palette_for(paint) == defaults.PALETTE_PRESETS[("octa", "paint")]
    assert palette_for(light) == defaults.PALETTE_PRESETS[("octa", "light")]


# --- Octa bottom slot ----------------------------------------------------------------


def test_bottom_slot_layer_rides_only_the_octa_stack():
    octa = _build_layers(dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"))
    hexa = _build_layers(defaults.DEFAULT_SKIN)
    assert any(isinstance(layer, BottomSlotLayer) for layer in octa)
    assert not any(isinstance(layer, BottomSlotLayer) for layer in hexa)
    # The slot text draws OVER the hands (owner spec), like the center body.
    slot_index = next(
        i for i, layer in enumerate(octa) if isinstance(layer, BottomSlotLayer)
    )
    last_hand = max(
        i for i, layer in enumerate(octa) if isinstance(layer, HandLayer)
    )
    assert slot_index > last_hand


@pytest.mark.parametrize("mode", constants.OCTA_SLOT_MODES)
def test_octa_slot_modes_render(july_wednesday, mode):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa", octa_slot=mode)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash


# --- Render smoke -------------------------------------------------------------------


@pytest.mark.parametrize("pointer", ["cross", "octa"])
def test_pointer_variants_render(july_wednesday, pointer):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(2, 2).alpha() == 0           # corners stay transparent
    assert image.pixelColor(180, 8).alpha() > 200        # ring painted
    assert image.pixelColor(333, 180).alpha() > 200      # disc touches the ring


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
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright_compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Wednesday, Mercury" in tip
    assert "align='center'" in tip           # hover text is centered (owner spec)


# --- Arm hovers (owner spec) -----------------------------------------------------------


def test_hexa_arm_hover_names_its_two_signs(july_wednesday):
    """Each hexa diamond spans exactly TWO zodiac signs (the owner's
    proposed list had Aquarius doubled on the bottom arm — corrected:
    bottom = Sagittarius + Capricorn). Upright → no asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond, 0.6R up
    assert "Gemini" in top and "Cancer" in top and "*" not in top
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)      # below mercury's slot
    assert "Sagittarius" in bottom and "Capricorn" in bottom


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
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm, 0.6R
    assert "Summer" in diagonal and "days" in diagonal and "Middle" in diagonal
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
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN,
            pointer="octa",
            solar_rotation=False,
            octa_slot="chinese_text",
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
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
    # Upright + solstice noon: the Earth rides at the dial top, orbit
    # 0.75R. Probe DIAGONALLY below-right of the marker: inside the 2x
    # halo, outside the disc, off the noon hand shafts on the vertical
    # and BELOW the marker's date-text line (which renders as wide tofu
    # boxes under the offscreen platform and would mask the comparison).
    # The white core lifts the blue channel over the blue-free yellow.
    marker_y = 270 - round(270 * defaults.DEFAULT_SKIN.year_marker.orbit_fraction)
    lit = with_glow.pixelColor(300, marker_y + 30)
    plain = without.pixelColor(300, marker_y + 30)
    assert lit.blue() - plain.blue() >= 8


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
    # At the instant the moon sits exactly on its cycle angle; probe
    # 30 px above the marker center — inside the 2x halo, off the disc.
    moon_angle = math.radians(day.moon_fraction * 360.0)
    orbit = 270 * defaults.DEFAULT_SKIN.year_marker.moon_orbit_fraction
    moon_x = 270 + orbit * math.sin(moon_angle)
    moon_y = 270 - orbit * math.cos(moon_angle)
    lit = with_glow.pixelColor(round(moon_x), round(moon_y) - 30)
    plain = without.pixelColor(round(moon_x), round(moon_y) - 30)
    assert (
        lit.red() - plain.red() >= 8
        or lit.green() - plain.green() >= 8
        or lit.blue() - plain.blue() >= 8
    )


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
    # 90 px below center: inside the darkest sections (plus the star's
    # slight solar rotation), away from body slots and diamond borders.
    full_pixel = full.pixelColor(180, 270)
    half_pixel = half.pixelColor(180, 270)
    assert full_pixel.alpha() > 200 and half_pixel.alpha() > 200
    assert full_pixel.red() < 50
    assert half_pixel.red() >= 55


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
