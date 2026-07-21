"""R5b FINAL MAP round goldens (owner spec sealed 2026-07-21): the
sealed shortcut map (Ctrl+, dies, Ctrl+M takes Settings; Ctrl+W gains a
diamonds-only guard), the new SLOTS (Ctrl+1/2/3, Ctrl+Alt+1/2/3), FAST
TRAVEL (Ctrl+[/]/minus/plus) and LOCATIONS (Ctrl+Up/Down/Space/Left/
Right) families, the Fast Travel flash overlay, and the two real
`app.widget.ClockWidget.keyPressEvent` fixes this round required
(bare-Space-only, KeypadModifier masking).
"""

import dataclasses
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.fast_travel_flash import FastTravelFlash
from app.settings_store import Settings, replace
from config import constants, defaults
from core.deep_time import real_year


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = WatchController(app)
    yield made
    for dialog in (
        made._encyclopedia, made._observatory, made._guide,
        made._design, made._pointer_theme, made._slot_theme,
    ):
        if dialog is not None:
            dialog.close()
    made._fast_travel_flash.close()
    made._profiling_timer.stop()
    made._tray.hide()


# --- The final map table (owner's sealed list) ------------------------------


_OWNER_SEALED_COMBOS = {
    ("cycle_ring", "Key_R", ("ControlModifier",)),
    ("cycle_weekday_theme", "Key_W", ("ControlModifier",)),
    ("cycle_slots", "Key_N", ("ControlModifier",)),
    ("open_encyclopedia", "Key_E", ("ControlModifier",)),
    ("open_guide", "Key_G", ("ControlModifier",)),
    ("open_settings", "Key_M", ("ControlModifier",)),
    ("open_observatory", "Key_O", ("ControlModifier",)),
    ("open_time_travel", "Key_T", ("ControlModifier",)),
    ("return_to_now", "Key_Home", ("ControlModifier",)),
    ("toggle_archetype", "Key_A", ("ControlModifier",)),
    ("cycle_slot1_complication", "Key_1", ("ControlModifier",)),
    ("cycle_slot2_complication", "Key_2", ("ControlModifier",)),
    ("cycle_slot3_complication", "Key_3", ("ControlModifier",)),
    ("cycle_slot1_theme", "Key_1", ("ControlModifier", "AltModifier")),
    ("cycle_slot2_theme", "Key_2", ("ControlModifier", "AltModifier")),
    ("cycle_slot3_theme", "Key_3", ("ControlModifier", "AltModifier")),
    ("fast_travel_theme", "Key_BracketLeft", ("ControlModifier",)),
    ("fast_travel_option", "Key_BracketRight", ("ControlModifier",)),
    ("fast_travel_past", "Key_Minus", ("ControlModifier",)),
    ("fast_travel_future", "Key_Equal", ("ControlModifier",)),
    ("fast_travel_future", "Key_Plus", ("ControlModifier",)),
    ("location_north_pole", "Key_Up", ("ControlModifier",)),
    ("location_south_pole", "Key_Down", ("ControlModifier",)),
    ("location_greenwich", "Key_Space", ("ControlModifier",)),
    ("location_prev_city", "Key_Left", ("ControlModifier",)),
    ("location_next_city", "Key_Right", ("ControlModifier",)),
}


def test_final_map_contains_every_owner_combo():
    table = {entry[:3] for entry in defaults.SHORTCUTS}
    assert _OWNER_SEALED_COMBOS <= table


def test_final_map_has_exactly_the_owner_sealed_combos():
    table = {entry[:3] for entry in defaults.SHORTCUTS}
    assert table == _OWNER_SEALED_COMBOS


def test_ctrl_comma_is_fully_retired():
    assert not any(entry[1] == "Key_Comma" for entry in defaults.SHORTCUTS)
    assert "Key_Comma" not in defaults._SHORTCUT_KEY_DISPLAY_OVERRIDES


def test_only_one_ctrl_home_entry_survives_the_full_reset():
    home_entries = [entry for entry in defaults.SHORTCUTS if entry[1] == "Key_Home"]
    assert len(home_entries) == 1
    assert home_entries[0][0] == "return_to_now"


def test_settings_shortcut_display_is_ctrl_m():
    assert defaults.shortcut_display("open_settings") == "Ctrl+M"


def test_fast_travel_future_both_bindings_share_one_action_id():
    matches = [entry for entry in defaults.SHORTCUTS if entry[0] == "fast_travel_future"]
    assert {entry[1] for entry in matches} == {"Key_Equal", "Key_Plus"}


# --- Ctrl+W: the diamonds-only guard (CHANGED, owner spec) ------------------


def test_cycle_weekday_theme_still_cycles_on_the_default_hexa(controller):
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_weekday_theme")
    assert controller._settings.weekday_theme != before


def test_cycle_weekday_theme_is_noop_when_first_slot_shows_a_complication(controller):
    controller._set_display_choice("weekday_slot", "time")
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_weekday_theme")
    assert controller._settings.weekday_theme == before


def test_cycle_weekday_theme_is_noop_when_first_slot_is_hidden(controller):
    controller._set_display_choice("show_weekday", False)
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_weekday_theme")
    assert controller._settings.weekday_theme == before


def test_cycle_weekday_theme_is_noop_when_pointer_hidden(controller):
    controller._set_display_choice("show_pointer", False)
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_weekday_theme")
    assert controller._settings.weekday_theme == before


def test_cycle_weekday_theme_is_noop_on_aurora_which_has_no_diamonds(controller):
    controller._set_display_choice("pointer", "aurora")
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_weekday_theme")
    assert controller._settings.weekday_theme == before


# --- SLOTS: Ctrl+1/2/3 (Complication) and Ctrl+Alt+1/2/3 (Weekday theme) ----


def test_slot1_complication_cycle_starts_at_the_top_and_advances(controller):
    assert controller._settings.weekday_slot == "weekday"   # not a complication
    controller._on_shortcut("cycle_slot1_complication")
    assert controller._settings.weekday_slot == "time"
    controller._on_shortcut("cycle_slot1_complication")
    assert controller._settings.weekday_slot == "date"
    controller._on_shortcut("cycle_slot1_complication")
    assert controller._settings.weekday_slot == "day_length"
    controller._on_shortcut("cycle_slot1_complication")
    assert controller._settings.weekday_slot == "seconds"
    controller._on_shortcut("cycle_slot1_complication")
    assert controller._settings.weekday_slot == "time"       # wraps


def test_slot2_complication_cycle_is_noop_when_2nd_slot_inactive(controller):
    assert not controller._settings.show_octa_slot
    before = controller._settings.octa_slot
    controller._on_shortcut("cycle_slot2_complication")
    assert controller._settings.octa_slot == before


def test_slot3_complication_cycle_requires_the_2nd_slot_too(controller):
    controller._cycle_slots()   # 1 -> 2 slots
    controller._cycle_slots()   # 2 -> 3 slots
    assert controller._settings.show_third_slot
    controller._set_display_choice("show_octa_slot", False)   # breaks the chain
    before = controller._settings.third_slot
    controller._on_shortcut("cycle_slot3_complication")
    assert controller._settings.third_slot == before


def test_slot1_theme_cycle_is_noop_when_1st_slot_hidden(controller):
    controller._set_display_choice("show_weekday", False)
    before = controller._settings.weekday_theme
    controller._on_shortcut("cycle_slot1_theme")
    assert controller._settings.weekday_theme == before


def test_slot2_theme_cycle_switches_that_slot_into_weekday_mode(controller):
    controller._cycle_slots()   # enable the 2nd slot
    controller._settings = replace(controller._settings, octa_slot="date")
    controller._on_shortcut("cycle_slot2_theme")
    assert controller._settings.octa_slot == "weekday"


def test_slot2_theme_cycle_advances_the_theme(controller):
    controller._cycle_slots()
    before = controller._settings.info_slot_theme
    controller._on_shortcut("cycle_slot2_theme")
    assert controller._settings.info_slot_theme != before


def test_slot3_theme_cycle_is_noop_without_the_2nd_slot(controller):
    before = controller._settings.third_slot_theme
    controller._on_shortcut("cycle_slot3_theme")
    assert controller._settings.third_slot_theme == before


# --- FAST TRAVEL: theme/option cycling order --------------------------------


def test_fast_travel_theme_cycles_in_order_and_wraps(controller):
    themes = defaults.FAST_TRAVEL_THEMES
    assert controller._fast_travel_theme_index == 0
    for expected in range(1, len(themes) + 1):
        controller._on_shortcut("fast_travel_theme")
        assert controller._fast_travel_theme_index == expected % len(themes)


def test_fast_travel_option_cycles_within_theme_and_remembers_per_theme(controller):
    assert controller._fast_travel_theme_index == 0   # "sun"
    assert controller._fast_travel_option_index("sun") == 0
    controller._on_shortcut("fast_travel_option")
    assert controller._fast_travel_option_index("sun") == 1
    controller._on_shortcut("fast_travel_theme")       # -> "moon"
    assert controller._fast_travel_option_index("moon") == 0
    controller._on_shortcut("fast_travel_option")
    assert controller._fast_travel_option_index("moon") == 1
    # sun's own cursor survives untouched while moon's advances
    assert controller._fast_travel_option_index("sun") == 1


def test_fast_travel_option_wraps_within_its_own_theme(controller):
    sun_options = defaults.FAST_TRAVEL_THEMES[0]["options"]
    for expected in range(1, len(sun_options) + 1):
        controller._on_shortcut("fast_travel_option")
        assert controller._fast_travel_option_index("sun") == expected % len(sun_options)


def test_fast_travel_theme_and_option_change_each_trigger_one_flash(controller, monkeypatch):
    calls = []
    monkeypatch.setattr(
        controller._fast_travel_flash, "flash",
        lambda *args, **kwargs: calls.append(args),
    )
    controller._on_shortcut("fast_travel_theme")
    assert len(calls) == 1
    controller._on_shortcut("fast_travel_option")
    assert len(calls) == 2


def test_fast_travel_step_never_flashes(controller, monkeypatch):
    calls = []
    monkeypatch.setattr(
        controller._fast_travel_flash, "flash",
        lambda *args, **kwargs: calls.append(args),
    )
    controller._on_shortcut("fast_travel_past")
    controller._on_shortcut("fast_travel_future")
    assert calls == []


def test_fast_travel_flash_carries_the_active_theme_icon_and_option_text(
    controller, monkeypatch
):
    calls = []
    monkeypatch.setattr(
        controller._fast_travel_flash, "flash",
        lambda dial, icon_path, emoji, text: calls.append((icon_path, emoji, text)),
    )
    controller._on_shortcut("fast_travel_theme")   # -> "moon"
    icon_path, emoji, text = calls[0]
    assert emoji == "🌙"
    assert text == "Full"                          # moon's own first option


# --- FAST TRAVEL: the jump-step math (golden) --------------------------------


def test_fast_travel_past_on_calendar_year_steps_exactly_minus_one_year(controller):
    calendar_index = next(
        i for i, theme in enumerate(defaults.FAST_TRAVEL_THEMES)
        if theme["id"] == "calendar"
    )
    year_option_index = next(
        i for i, option in enumerate(
            defaults.FAST_TRAVEL_THEMES[calendar_index]["options"]
        )
        if option["id"] == "year"
    )
    controller._fast_travel_theme_index = calendar_index
    controller._fast_travel_option_indices["calendar"] = year_option_index

    known = datetime(2026, 6, 20, 12, 0, tzinfo=controller._tz)
    controller._start_simulation(known, controller._observer, 0)
    before_moment, _before_observer = controller._simulation
    before_year = real_year(before_moment.year, controller._sim_cycles)

    controller._on_shortcut("fast_travel_past")

    after_moment, _after_observer = controller._simulation
    after_year = real_year(after_moment.year, controller._sim_cycles)
    assert after_year == before_year - 1
    assert (after_moment.month, after_moment.day) == (
        before_moment.month, before_moment.day,
    )
    assert (after_moment.hour, after_moment.minute) == (
        before_moment.hour, before_moment.minute,
    )


def test_fast_travel_future_on_calendar_year_steps_exactly_plus_one_year(controller):
    calendar_index = next(
        i for i, theme in enumerate(defaults.FAST_TRAVEL_THEMES)
        if theme["id"] == "calendar"
    )
    year_option_index = next(
        i for i, option in enumerate(
            defaults.FAST_TRAVEL_THEMES[calendar_index]["options"]
        )
        if option["id"] == "year"
    )
    controller._fast_travel_theme_index = calendar_index
    controller._fast_travel_option_indices["calendar"] = year_option_index

    known = datetime(2026, 6, 20, 12, 0, tzinfo=controller._tz)
    controller._start_simulation(known, controller._observer, 0)
    before_moment, _ = controller._simulation
    before_year = real_year(before_moment.year, controller._sim_cycles)

    controller._on_shortcut("fast_travel_future")

    after_moment, _ = controller._simulation
    after_year = real_year(after_moment.year, controller._sim_cycles)
    assert after_year == before_year + 1


def test_fast_travel_step_chains_from_the_active_simulation(controller):
    """Owner chaining law: "each jump starts from the active
    simulation" — a SECOND step continues from the FIRST landing, not
    from real "now" again."""
    calendar_index = next(
        i for i, theme in enumerate(defaults.FAST_TRAVEL_THEMES)
        if theme["id"] == "calendar"
    )
    year_option_index = next(
        i for i, option in enumerate(
            defaults.FAST_TRAVEL_THEMES[calendar_index]["options"]
        )
        if option["id"] == "year"
    )
    controller._fast_travel_theme_index = calendar_index
    controller._fast_travel_option_indices["calendar"] = year_option_index
    known = datetime(2026, 6, 20, 12, 0, tzinfo=controller._tz)
    controller._start_simulation(known, controller._observer, 0)
    start_moment, _ = controller._simulation
    start_year = real_year(start_moment.year, controller._sim_cycles)

    controller._on_shortcut("fast_travel_past")
    controller._on_shortcut("fast_travel_past")

    end_moment, _ = controller._simulation
    end_year = real_year(end_moment.year, controller._sim_cycles)
    assert end_year == start_year - 2


# --- The Sun/Moon phase-filter extension to _compute_jump (pure + integration) --


def test_filtered_sun_anchors_none_keeps_all_six():
    from app.controller import _filtered_sun_anchors

    instants = tuple(range(6))   # stand-ins; the function never inspects values
    assert _filtered_sun_anchors(instants, None) == instants


def test_filtered_sun_anchors_solstice_keeps_the_even_indices():
    from app.controller import _filtered_sun_anchors

    instants = ("dec0", "mar", "jun", "sep", "dec1", "mar2")
    assert _filtered_sun_anchors(instants, "solstice") == ("dec0", "jun", "dec1")


def test_filtered_sun_anchors_equinox_keeps_the_odd_indices():
    from app.controller import _filtered_sun_anchors

    instants = ("dec0", "mar", "jun", "sep", "dec1", "mar2")
    assert _filtered_sun_anchors(instants, "equinox") == ("mar", "sep", "mar2")


def test_filtered_moon_events_new_full_quarter():
    from app.controller import _filtered_moon_events

    events = (
        ("new1", 0.0), ("fq1", 0.25), ("full1", 0.5), ("tq1", 0.75),
    )
    assert _filtered_moon_events(events, "new") == ("new1",)
    assert _filtered_moon_events(events, "full") == ("full1",)
    assert _filtered_moon_events(events, "quarter") == ("fq1", "tq1")
    assert _filtered_moon_events(events, None) == ("new1", "fq1", "full1", "tq1")


def test_sun_moon_jump_pattern_parses_every_fast_travel_stem():
    from app.controller import _SUN_MOON_JUMP_PATTERN

    for stem in (
        "sun", "sun_solstice", "sun_equinox",
        "moon_full", "moon_new", "moon_quarter",
    ):
        for direction in ("next", "prev"):
            assert _SUN_MOON_JUMP_PATTERN.match(f"{direction}_{stem}")


def test_compute_jump_next_sun_solstice_never_lands_on_an_equinox_month(controller):
    """Integration-level pin against the REAL bundled seasons data: a
    solstice-filtered jump from a known moment must land in June or
    December, never March/September."""
    import astral

    observer = astral.Observer(latitude=44.8, longitude=20.5)
    moment = datetime(2026, 1, 1, tzinfo=controller._tz)
    for _ in range(6):
        result = controller._compute_jump(moment, observer, 0, "next_sun_solstice")
        assert result is not None
        moment, observer, _cycles = result
        assert moment.month in (6, 12), moment


def test_compute_jump_next_sun_equinox_never_lands_on_a_solstice_month(controller):
    import astral

    observer = astral.Observer(latitude=44.8, longitude=20.5)
    moment = datetime(2026, 1, 1, tzinfo=controller._tz)
    for _ in range(6):
        result = controller._compute_jump(moment, observer, 0, "next_sun_equinox")
        assert result is not None
        moment, observer, _cycles = result
        assert moment.month in (3, 9), moment


def test_compute_jump_next_moon_new_lands_on_a_catalogued_new_moon(controller):
    import astral

    from core.deep_time import real_year

    observer = astral.Observer(latitude=44.8, longitude=20.5)
    moment = datetime(2026, 1, 1, tzinfo=controller._tz)
    result = controller._compute_jump(moment, observer, 0, "next_moon_new")
    assert result is not None
    landed, _observer, cycles = result
    year = real_year(landed.year, cycles)
    catalogued = {
        when for when, fraction in controller._moon_phases.moon_window(year).events
        if fraction == 0.0
    }
    assert any(abs((landed - when.astimezone(landed.tzinfo)).total_seconds()) < 60
               for when in catalogued)


# --- LOCATIONS ---------------------------------------------------------------


def test_location_pole_jumps_set_the_expected_latitude(controller):
    controller._on_shortcut("location_north_pole")
    assert controller._simulation is not None
    _, observer = controller._simulation
    assert observer.latitude == pytest.approx(defaults.QUICK_JUMP_POLE_LATITUDE)
    controller._on_shortcut("location_south_pole")
    _, observer = controller._simulation
    assert observer.latitude == pytest.approx(-defaults.QUICK_JUMP_POLE_LATITUDE)


def test_location_greenwich_sets_the_expected_coordinates(controller):
    controller._on_shortcut("location_greenwich")
    _, observer = controller._simulation
    assert observer.latitude == pytest.approx(defaults.GREENWICH_LATITUDE)
    assert observer.longitude == pytest.approx(defaults.GREENWICH_LONGITUDE)


def test_location_city_cycle_is_a_strict_noop_with_none_defined(controller):
    assert controller._settings.jump_cities == ()
    controller._on_shortcut("location_next_city")
    assert controller._simulation is None
    assert controller._jump_city_index == 0
    controller._on_shortcut("location_prev_city")
    assert controller._simulation is None


def test_location_city_cycle_wraps_forward_through_the_list(controller):
    cities = (
        {"name": "A", "latitude": 10.0, "longitude": 10.0, "timezone": "UTC"},
        {"name": "B", "latitude": 20.0, "longitude": 20.0, "timezone": "UTC"},
        {"name": "C", "latitude": 30.0, "longitude": 30.0, "timezone": "UTC"},
    )
    controller._settings = replace(controller._settings, jump_cities=cities)
    seen = []
    for _ in range(4):
        controller._on_shortcut("location_next_city")
        _, observer = controller._simulation
        seen.append(observer.latitude)
    assert seen == [10.0, 20.0, 30.0, 10.0]


def test_location_city_cycle_wraps_backward_through_the_list(controller):
    cities = (
        {"name": "A", "latitude": 10.0, "longitude": 10.0, "timezone": "UTC"},
        {"name": "B", "latitude": 20.0, "longitude": 20.0, "timezone": "UTC"},
        {"name": "C", "latitude": 30.0, "longitude": 30.0, "timezone": "UTC"},
    )
    controller._settings = replace(controller._settings, jump_cities=cities)
    seen = []
    for _ in range(4):
        controller._on_shortcut("location_prev_city")
        _, observer = controller._simulation
        seen.append(observer.latitude)
    assert seen == [10.0, 30.0, 20.0, 10.0]


# --- Menu labels (R5 doubt 4 FOLLOW-UP) --------------------------------------


def test_the_six_direct_shortcut_actions_carry_their_combo_in_the_menu(controller):
    texts = [a.text() for a in controller._menu.actions()]
    for action_id, expected_suffix in (
        ("open_encyclopedia", "Ctrl+E"),
        ("open_guide", "Ctrl+G"),
        ("open_settings", "Ctrl+M"),
        ("open_observatory", "Ctrl+O"),
        ("open_time_travel", "Ctrl+T"),
        ("toggle_archetype", "Ctrl+A"),
    ):
        assert defaults.shortcut_display(action_id) == expected_suffix
        assert any(t.endswith(f"\t{expected_suffix}") for t in texts), action_id


# --- FastTravelFlash widget-level tests ---------------------------------------


def _make_dial_stub(app):
    from PySide6.QtWidgets import QWidget

    widget = QWidget()
    widget.resize(400, 400)
    widget.move(200, 200)
    widget.show()
    return widget


def test_flash_shows_above_the_dial_when_there_is_room(app, monkeypatch):
    from app import fast_travel_flash as flash_mod

    monkeypatch.setattr(flash_mod.native, "assert_topmost", lambda hwnd: None)
    dial = _make_dial_stub(app)
    flash = FastTravelFlash()
    try:
        flash.flash(dial, None, "☀️", "Solstices only")
        assert flash.isVisible()
        dial_geo = dial.frameGeometry()
        assert flash.geometry().bottom() <= dial_geo.top()
    finally:
        flash.close()
        dial.close()


def test_flash_falls_below_when_the_dial_hugs_the_screen_top(app, monkeypatch):
    from app import fast_travel_flash as flash_mod

    monkeypatch.setattr(flash_mod.native, "assert_topmost", lambda hwnd: None)
    dial = _make_dial_stub(app)
    dial.move(200, 0)                # hugging the top edge
    flash = FastTravelFlash()
    try:
        flash.flash(dial, None, "☀️", "Solstices only")
        dial_geo = dial.frameGeometry()
        assert flash.geometry().top() >= dial_geo.bottom()
    finally:
        flash.close()
        dial.close()


def test_flash_auto_hides_when_its_fade_completes(app, monkeypatch):
    from app import fast_travel_flash as flash_mod

    monkeypatch.setattr(flash_mod.native, "assert_topmost", lambda hwnd: None)
    dial = _make_dial_stub(app)
    flash = FastTravelFlash()
    try:
        flash.flash(dial, None, "🌙", "Full")
        assert flash.isVisible()
        assert flash._hold_timer.isActive()
        # Simulate the hold timer firing and the fade completing —
        # offscreen tests never sleep for the real ~1.2s.
        flash._hold_timer.timeout.emit()
        flash._fade.finished.emit()
        assert not flash.isVisible()
    finally:
        flash.close()
        dial.close()


def test_flash_restarts_cleanly_on_a_rapid_second_call(app, monkeypatch):
    from app import fast_travel_flash as flash_mod

    monkeypatch.setattr(flash_mod.native, "assert_topmost", lambda hwnd: None)
    dial = _make_dial_stub(app)
    flash = FastTravelFlash()
    try:
        flash.flash(dial, None, "☀️", "Any turning point")
        flash._hold_timer.timeout.emit()   # start fading
        flash.flash(dial, None, "🌙", "Full")   # a second press mid-fade
        assert flash._opacity.opacity() == 1.0
        assert flash._text_label.text() == "Full"
    finally:
        flash.close()
        dial.close()


# --- widget.py fixes (Ctrl+Space bare-modifier guard, KeypadModifier mask) --


def _press(widget, key, modifiers=Qt.KeyboardModifier.ControlModifier, text=""):
    event = QKeyEvent(QEvent.Type.KeyPress, key, modifiers, text)
    widget.keyPressEvent(event)


def _bare_widget(app):
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QMenu

    from app.legend_popup import LegendPopup
    from app.widget import ClockWidget

    menu = QMenu()
    return ClockWidget(360, menu, LegendPopup(), QAction("Show", menu))


def test_bare_space_still_triggers_the_encyclopedia_jump(app, monkeypatch):
    widget = _bare_widget(app)
    calls = []
    monkeypatch.setattr(widget, "_trigger_space_jump", lambda: calls.append(1))
    _press(widget, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
    assert calls == [1]


def test_ctrl_space_reaches_the_shortcut_table_not_the_encyclopedia_jump(app, monkeypatch):
    widget = _bare_widget(app)
    space_calls = []
    monkeypatch.setattr(widget, "_trigger_space_jump", lambda: space_calls.append(1))
    seen = []
    widget.shortcut_triggered.connect(seen.append)
    _press(widget, Qt.Key.Key_Space, Qt.KeyboardModifier.ControlModifier)
    assert space_calls == []
    assert seen == ["location_greenwich"]


def test_ctrl_numpad_plus_still_matches_fast_travel_future(app):
    widget = _bare_widget(app)
    seen = []
    widget.shortcut_triggered.connect(seen.append)
    numpad_modifiers = (
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.KeypadModifier
    )
    _press(widget, Qt.Key.Key_Plus, numpad_modifiers)
    assert seen == ["fast_travel_future"]
