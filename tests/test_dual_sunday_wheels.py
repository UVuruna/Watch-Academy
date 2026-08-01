"""THE DUAL SUNDAY WHEEL MAP (owner seal 2026-07-29) — regression pins
for the Session-23 miss (root Rule #25: named after the failure): the
Duality-Axes decree was STARTED for the Compass's CHARACTER wheel, yet
that wheel never received its horizontal 06h/18h duality; and the
Quaternity's SEASONS wheel turned its arms onto the diagonals while the
two Sunday faces stayed stranded on seats that no longer exist. The
seal: duality is a property of the WHEEL — center on hexa/trio and the
Seasons wheel, vertical 12h/24h on Quaternity/Compass primary+secondary,
horizontal 06h/18h on the Rose and the Character wheel — plus the two
sealed per-theme flips (religion horizontal, continents vertical)."""

import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from render.skin_geometry import (
    center_duality,
    horizontal_duality,
    ruler_seat_angle,
    servant_seat_angle,
    weekday_slots,
)
from render.slot_layout import center_dual_face, center_seat_body_key, sunday_dual_face


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _skin(pointer: str, style: str = "primary", theme: str | None = None):
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    settings = replace(
        Settings(), pointer=pointer, palette_style=style,
        solar_rotation=False,
    )
    if theme is not None:
        settings = replace(settings, weekday_theme=theme)
    return apply_display_settings(defaults.DEFAULT_SKIN, settings)


def test_compass_character_wheel_rides_the_horizontal_axis(app):
    """The very seat the decree was started for: the Character wheel
    (octa tertiary) seats Sunday on the blue<->red axis — Ruler on red
    18h, Servant on blue 06h — and its bodies take the Rose's own hue
    seats, because the wheel wears the same ROSE_PALETTE hues."""
    skin = _skin("octa", "tertiary")
    assert horizontal_duality(skin)
    assert not center_duality(skin)
    assert sunday_dual_face(skin)
    assert ruler_seat_angle(skin) == 90.0       # 18h, red
    assert servant_seat_angle(skin) == 270.0    # 06h, blue
    slots = dict(weekday_slots(skin))
    assert slots == dict(constants.POINTER_WEEKDAY_SLOTS["rose"])
    assert 270.0 not in slots                   # the Servant's seat is his alone
    # The first two wheels keep the vertical axis untouched.
    for style in ("primary", "secondary"):
        vertical = _skin("octa", style)
        assert not horizontal_duality(vertical)
        assert ruler_seat_angle(vertical) == 0.0
        assert servant_seat_angle(vertical) == constants.SOUTH_SLOT_ANGLE


def test_character_wheel_honors_the_sacred_axis_flip(app):
    """The creeds flip (Christianity BLUE, Satanism RED) rides every
    horizontal wheel — the Character wheel exactly like the Rose."""
    for pointer, style in (("octa", "tertiary"), ("rose", "primary"),
                           ("rose", "secondary")):
        skin = _skin(pointer, style, theme="religion")
        assert ruler_seat_angle(skin) == 270.0   # Christianity — blue 06h
        assert servant_seat_angle(skin) == 90.0  # Satanism — red 18h


def test_quaternity_seasons_wheel_centers_the_sunday(app):
    """The Seasons wheel (cross tertiary) turns its arms onto the
    diagonals — no 12h/24h seat exists, so its Sunday lives in ONE
    CENTER image under the Trinity/Prism law (daylight Ruler, night
    Servant, the Ninth in the solar windows)."""
    skin = _skin("cross", "tertiary")
    assert center_duality(skin)
    assert not sunday_dual_face(skin)
    assert center_dual_face(skin)
    assert center_seat_body_key(skin, "mars") == "sun"
    slots = dict(weekday_slots(skin))
    # The Sun stands in the center — never on an arm — and Jupiter
    # keeps the shared arm alone, swung to the 45-degree diagonal.
    assert all(
        "sun" not in occupants for occupants in slots.values()
    )
    assert slots[45.0] == ("jupiter",)
    # The first two wheels keep the vertical two-seat Sunday.
    for style in ("primary", "secondary"):
        vertical = _skin("cross", style)
        assert not center_duality(vertical)
        assert sunday_dual_face(vertical)


def test_continents_geographic_vertical_flip(app):
    """Theme poll 23/23 (owner seal 2026-07-29): the Arctic IS the
    north, so on the VERTICAL wheels continents seats the Servant
    (Arctic) on top 12h and the Ruler (Antarctica) at 24h — Jupiter
    keeps his own arm when the Ruler moves down. The horizontal wheels
    stay standard (18h red Antarctica, 06h blue Arctic)."""
    for pointer in ("cross", "octa"):
        skin = _skin(pointer, "primary", theme="continents")
        assert ruler_seat_angle(skin) == constants.SOUTH_SLOT_ANGLE
        assert servant_seat_angle(skin) == 0.0
        slots = dict(weekday_slots(skin))
        assert "sun" in slots[180.0]
        assert all(
            "sun" not in occupants or angle == 180.0
            for angle, occupants in slots.items()
        )
    jupiter_kept = dict(weekday_slots(_skin("cross", "primary",
                                            theme="continents")))
    assert jupiter_kept[0.0] == ("jupiter",)
    for pointer, style in (("rose", "primary"), ("octa", "tertiary")):
        skin = _skin(pointer, style, theme="continents")
        assert ruler_seat_angle(skin) == 90.0
        assert servant_seat_angle(skin) == 270.0
