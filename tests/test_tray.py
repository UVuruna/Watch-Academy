"""ADD WATCH round tray icon identity (owner INSTRUCTION.txt item 2B,
sealed 2026-07-21): watch 1 keeps the gold master untouched, watch 2
wears the pre-existing rose-gold master, watch 3+ tint the gold master
along the CALENDAR MONTH color wheel (`UV/Color Wheels.png`) starting
PURPLE #8000FF (R:G:B 1:0:2, January) then BLUE #0000FF (R:G:B 0:0:1,
February) and onward, wrapping past December."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import tray
from config import defaults


def app():
    return QApplication.instance() or QApplication([])


# --- the recolor rule (pure functions, no Qt objects needed) --------------------


def test_watch_one_is_the_gold_master_untouched():
    assert tray._logo_asset(1) == defaults.LOGO_ASSET
    assert tray._tray_tint(1) is None


def test_watch_two_is_the_rose_gold_master_not_a_recolor():
    assert tray._logo_asset(2) == defaults.LOGO_SETUP_ASSET
    assert tray._tray_tint(2) is None


def test_watch_three_starts_the_wheel_at_purple_one_zero_two():
    """The owner's own worked example, INSTRUCTION.txt item 2B: PURPLE,
    R:G:B 1:0:2 — the CALENDAR month wheel's January (UV/Color
    Wheels.png)."""
    assert tray._logo_asset(3) == defaults.LOGO_ASSET
    assert tray._tray_tint(3) == "#8000FF"


def test_watch_four_is_blue_zero_zero_one():
    """R:G:B 0:0:1 — the CALENDAR wheel's February, right after purple."""
    assert tray._tray_tint(4) == "#0000FF"


def test_wheel_walks_all_twelve_months_in_order():
    colors = [tray._tray_tint(index) for index in range(3, 15)]
    assert colors == list(defaults.TRAY_COLOR_WHEEL)
    assert len(defaults.TRAY_COLOR_WHEEL) == 12


def test_wheel_wraps_forever_past_december():
    assert tray._tray_tint(15) == defaults.TRAY_COLOR_WHEEL[0]   # back to purple
    assert tray._tray_tint(16) == defaults.TRAY_COLOR_WHEEL[1]   # back to blue
    assert tray._tray_tint(27) == defaults.TRAY_COLOR_WHEEL[0]   # a second lap


def test_tray_color_table_for_watches_one_through_eight():
    """The full golden table (owner deliverable): golden, rose gold,
    then the wheel from purple."""
    expected = {
        1: None, 2: None,
        3: "#8000FF", 4: "#0000FF", 5: "#0080FF", 6: "#00FFFF",
        7: "#00FF80", 8: "#00FF00",
    }
    for index, hue in expected.items():
        assert tray._tray_tint(index) == hue


# --- the rasterized icon itself --------------------------------------------------


def test_logo_icon_returns_a_non_null_icon_for_every_watch_index():
    application = app()
    for index in range(1, 9):
        icon = tray.logo_icon(index)
        assert not icon.isNull()


def test_logo_icon_defaults_to_watch_one():
    application = app()
    assert not tray.logo_icon().isNull()
