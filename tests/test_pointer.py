"""Pointer variants (hexa/cross/octa): slot layouts, shared-slot
priority, the octa digital-time slot and the pointer/contrast-driven
gray wheel."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
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
    HandLayer,
    TimeTextLayer,
    today_slot_theta,
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


def test_octa_reserves_the_bottom_arm_for_the_time():
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


# --- Octa time slot ----------------------------------------------------------------


def test_time_text_layer_rides_only_the_octa_stack():
    octa = _build_layers(dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"))
    hexa = _build_layers(defaults.DEFAULT_SKIN)
    assert any(isinstance(layer, TimeTextLayer) for layer in octa)
    assert not any(isinstance(layer, TimeTextLayer) for layer in hexa)
    # The time text draws OVER the hands (owner spec), like the center body.
    time_index = next(
        i for i, layer in enumerate(octa) if isinstance(layer, TimeTextLayer)
    )
    last_hand = max(
        i for i, layer in enumerate(octa) if isinstance(layer, HandLayer)
    )
    assert time_index > last_hand


# --- Render smoke -------------------------------------------------------------------


@pytest.mark.parametrize("pointer", ["cross", "octa"])
def test_pointer_variants_render(july_wednesday, pointer):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(2, 2).alpha() == 0           # corners stay transparent
    assert image.pixelColor(180, 8).alpha() > 200        # ring painted
    assert image.pixelColor(333, 180).alpha() > 200      # disc touches the ring


# --- Gray wheel ----------------------------------------------------------------------


def test_gray_wheel_structure():
    """Measured from the owner's art (gray.png: 30 sections of 12 deg,
    shades 0..255 step 17): single lightest/darkest sections centered on
    noon/midnight + 14 mirror pairs = 16 shades. Soft contrast is the
    middle half of the scale, values at the centers of 16 bins of 8 —
    188..68, symmetric about 128."""
    assert constants.GRAY_WHEEL_SECTIONS == 30
    shades = constants.GRAY_WHEEL_SECTIONS // 2 + 1
    assert shades == 16
    assert 1 + 2 * (shades - 2) + 1 == constants.GRAY_WHEEL_SECTIONS
    assert defaults.GRAY_WHEEL_SCALES["full"] == (255, 17)
    assert defaults.GRAY_WHEEL_SCALES["soft"] == (188, 8)
    for contrast in constants.GRAY_CONTRAST_VARIANTS:
        lightest, step = defaults.GRAY_WHEEL_SCALES[contrast]
        values = [lightest - k * step for k in range(shades)]
        assert all(0 <= value <= 255 for value in values)
    full = [255 - k * 17 for k in range(shades)]
    assert full[-1] == 0                                   # spans the whole range
    soft = [188 - k * 8 for k in range(shades)]
    assert soft[-1] == 68
    assert all(value + mirror == 256 for value, mirror in zip(soft, reversed(soft)))


def test_cross_arms_borrow_the_octa_shape():
    """Owner spec (cross.png): the cross is the octa star WITHOUT the
    four diagonal arms — slim diamonds with gaps, not a fat 4-star."""
    half_angles = constants.POINTER_ARM_HALF_ANGLE_DEG
    assert half_angles["cross"] == half_angles["octa"]
    for pointer in ("hexa", "octa"):
        assert half_angles[pointer] == 180.0 / constants.POINTER_POINTS[pointer]


def test_soft_contrast_renders_a_gentler_night(july_wednesday):
    """The bottom of the dial (solar midnight, no hue overlay in July) is
    near-black on full contrast and clearly lifted on soft."""
    day, tick = july_wednesday
    full = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    soft_skin = dataclasses.replace(defaults.DEFAULT_SKIN, gray_contrast="soft")
    soft = Compositor(soft_skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    # 90 px below center: inside the darkest pair (plus the star's slight
    # solar rotation), away from body slots and diamond borders.
    full_pixel = full.pixelColor(180, 270)
    soft_pixel = soft.pixelColor(180, 270)
    assert full_pixel.alpha() > 200 and soft_pixel.alpha() > 200
    assert full_pixel.red() < 50
    assert soft_pixel.red() >= 55
