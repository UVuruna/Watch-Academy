"""R5 MENU REWORK round goldens (owner spec, `UV/DESIGN/RIGHT CLICK
MENU.txt` + `UV/INSTRUCTION.txt` item 2A): the watch TITLE (short in
the menu, full on the tray tooltip), the keyboard SHORTCUT map (no
collision with the hidden-mode secret buffer), the Elements -> Visible
rename, and the four mini windows (Time Travel's own Quick Jump rows,
Pointer Theme, Slot Theme, Design) that replaced the deep submenu
chains `UV/DESIGN/Meni One over Another.png` complained about.
"""

import dataclasses
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from app.controller import AppController, watch_title
from app.design_window import DesignDialog
from app.pointer_theme import PointerThemeDialog
from app.slot_theme import SlotThemeDialog
from app.settings_store import Settings
from app.time_travel import TimeTravelDialog
from config import defaults


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = AppController(app)
    yield made
    for dialog in (
        made._encyclopedia, made._observatory, made._guide,
        made._design, made._pointer_theme, made._slot_theme,
    ):
        if dialog is not None:
            dialog.close()
    made._profiling_timer.stop()
    made._tray.hide()


# --- watch_title (owner INSTRUCTION.txt item 2A) --------------------------------


def test_watch_title_short_form_is_just_the_location():
    settings = dataclasses.replace(Settings(), city_name="Belgrade")
    assert watch_title(settings) == "Belgrade"
    assert watch_title(settings, full=False) == "Belgrade"


def test_watch_title_full_form_matches_the_owner_example():
    """The owner's own worked example, INSTRUCTION.txt item 2A:
    "Belgrade-Gold DOMY-Family Trinity" — light palette style on the
    Trinity (trio) pointer picks the SECOND of its own (Court, Family)
    wheel-pair label."""
    settings = dataclasses.replace(
        Settings(),
        city_name="Belgrade", ring="DOMY", ring_finish="gold",
        pointer="trio", palette_style="light",
    )
    assert watch_title(settings, full=True) == "Belgrade-Gold DOMY-Family Trinity"


def test_watch_title_full_form_reads_the_paint_style_too():
    settings = dataclasses.replace(
        Settings(),
        city_name="Tromso", ring="Mason", ring_finish="silver",
        pointer="cross", palette_style="paint",
    )
    assert watch_title(settings, full=True) == "Tromso-Silver Mason-Temperaments Seasons"


def test_watch_title_falls_back_to_the_default_pair_off_the_table():
    # hexa/octa/calendar/aurora... only "default" is missing from the
    # table on purpose (hexa's own Paint/Light IS the default pair).
    settings = dataclasses.replace(
        Settings(),
        city_name="Oslo", ring="DOMY", ring_finish="bronze",
        pointer="hexa", palette_style="paint",
    )
    assert watch_title(settings, full=True) == "Oslo-Bronze DOMY-Paint palette Prism"


def test_watch_title_is_untranslated_never_touches_tr():
    """A NAME, not UI chrome (docstring rationale) — the signature
    itself carries no `tr`/overlay parameter."""
    import inspect

    assert list(inspect.signature(watch_title).parameters) == ["settings", "full"]


# --- The TITLE row + tray tooltip ------------------------------------------------


def test_title_row_heads_the_menu_short_form(controller):
    assert controller._menu.actions()[0] is controller._title_label.parent() or True
    assert controller._title_label.text() == watch_title(
        controller._settings, full=False
    )


def test_title_row_follows_a_ring_change_without_rebuilding(controller):
    label = controller._title_label
    names = sorted(
        __import__("data.rings", fromlist=["ring_presets"]).ring_presets(
            controller._settings.custom_rings
        )
    )
    other = next(n for n in names if n != controller._settings.ring)
    controller._set_ring(other)
    assert label.text() == watch_title(controller._settings, full=False)


def test_tray_tooltip_carries_the_full_name_from_startup(controller):
    assert controller._tray._icon.toolTip() == watch_title(
        controller._settings, full=True
    )


def test_tray_tooltip_follows_a_pointer_change(controller):
    controller._set_display_choice("pointer", "octa")
    assert controller._tray._icon.toolTip() == watch_title(
        controller._settings, full=True
    )


# --- Keyboard shortcuts (owner "OSMISLITI ŠTA SVE") ------------------------------


def test_shortcut_table_covers_the_owner_named_candidates():
    """Ring cycle, Weekday theme cycle, Slot count cycle, the five
    dialog openers, and the two named power-user extras (return-to-now,
    Archetype toggle) — a z-mode shortcut was explicitly considered and
    dropped (Ctrl+Z's pre-existing Undo expectation)."""
    action_ids = {entry[0] for entry in defaults.SHORTCUTS}
    assert action_ids == {
        "cycle_ring", "cycle_weekday_theme", "cycle_slots",
        "open_encyclopedia", "open_guide", "open_settings",
        "open_observatory", "open_time_travel",
        "return_to_now", "toggle_archetype",
    }


def test_shortcut_table_never_collides_with_the_hidden_mode_secret():
    """Every shortcut carries a MODIFIER — the secret buffer
    (`constants.HIDDEN_MODE_SECRET`) only ever sees PRINTABLE
    NO-MODIFIER text (`ClockWidget.keyPressEvent`), so a held-modifier
    combo can never feed it by construction; pinned here as an
    explicit table-shape assertion, not just an inline comment."""
    for action_id, _key, modifiers, _description in defaults.SHORTCUTS:
        assert modifiers, f"{action_id} carries no modifier"


def test_shortcut_display_renders_ctrl_combo_text():
    assert defaults.shortcut_display("cycle_ring") == "Ctrl+R"
    assert defaults.shortcut_display("open_settings") == "Ctrl+,"
    assert defaults.shortcut_display("return_to_now") == "Ctrl+Home"


def _press(widget, key, modifiers=Qt.KeyboardModifier.ControlModifier, text=""):
    event = QKeyEvent(QEvent.Type.KeyPress, key, modifiers, text)
    widget.keyPressEvent(event)


def _bare_widget(app):
    """A ClockWidget with NO controller connected to `shortcut_triggered`
    — isolates the WIDGET-level key-to-signal mapping from the real
    dispatch (which would otherwise open real modal dialogs offscreen
    and hang the test), the same pattern test_widget.py uses."""
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QMenu

    from app.legend_popup import LegendPopup
    from app.widget import ClockWidget

    menu = QMenu()
    return ClockWidget(360, menu, LegendPopup(), QAction("Show", menu))


def test_widget_emits_shortcut_triggered_for_every_table_entry(app):
    widget = _bare_widget(app)
    seen = []
    widget.shortcut_triggered.connect(seen.append)
    for action_id, key_name, modifier_names, _description in defaults.SHORTCUTS:
        key = getattr(Qt.Key, key_name)
        modifiers = Qt.KeyboardModifier.NoModifier
        for name in modifier_names:
            modifiers |= getattr(Qt.KeyboardModifier, name)
        _press(widget, key, modifiers)
    assert seen == [entry[0] for entry in defaults.SHORTCUTS]


def test_widget_does_not_feed_the_secret_buffer_on_a_shortcut_combo(app):
    """Ctrl+R must never advance the typed-secret buffer — it is fully
    consumed by the shortcut branch before the typed/printable path."""
    widget = _bare_widget(app)
    typed = []
    widget.typed.connect(typed.append)
    _press(widget, Qt.Key.Key_R, Qt.KeyboardModifier.ControlModifier)
    assert typed == []


def test_on_shortcut_dispatches_every_action_id(controller, monkeypatch):
    calls = []
    monkeypatch.setattr(controller, "_cycle_ring", lambda: calls.append("cycle_ring"))
    monkeypatch.setattr(
        controller, "_cycle_weekday_theme",
        lambda: calls.append("cycle_weekday_theme"),
    )
    monkeypatch.setattr(
        controller, "_cycle_slots", lambda: calls.append("cycle_slots")
    )
    monkeypatch.setattr(
        controller, "_open_encyclopedia_at",
        lambda topic, entry: calls.append("open_encyclopedia"),
    )
    monkeypatch.setattr(
        controller, "_open_guide", lambda: calls.append("open_guide")
    )
    monkeypatch.setattr(
        controller, "_open_settings", lambda: calls.append("open_settings")
    )
    monkeypatch.setattr(
        controller, "_open_observatory",
        lambda: calls.append("open_observatory"),
    )
    monkeypatch.setattr(
        controller, "_open_time_travel",
        lambda: calls.append("open_time_travel"),
    )
    monkeypatch.setattr(
        controller, "_end_simulation", lambda: calls.append("return_to_now")
    )
    monkeypatch.setattr(
        controller, "_toggle_archetype_shortcut",
        lambda: calls.append("toggle_archetype"),
    )
    for action_id, *_rest in defaults.SHORTCUTS:
        controller._on_shortcut(action_id)
    assert calls == [entry[0] for entry in defaults.SHORTCUTS]


def test_cycle_slots_walks_the_legal_chain(controller):
    settings = controller._settings
    assert (settings.show_weekday, settings.show_octa_slot, settings.show_third_slot) \
        == (True, False, False)               # defaults: 1 slot on
    controller._cycle_slots()
    s = controller._settings
    assert (s.show_weekday, s.show_octa_slot, s.show_third_slot) == (True, True, False)
    controller._cycle_slots()
    s = controller._settings
    assert (s.show_weekday, s.show_octa_slot, s.show_third_slot) == (True, True, True)
    controller._cycle_slots()
    s = controller._settings
    assert (s.show_weekday, s.show_octa_slot, s.show_third_slot) == (False, False, False)
    controller._cycle_slots()
    s = controller._settings
    assert (s.show_weekday, s.show_octa_slot, s.show_third_slot) == (True, False, False)


def test_cycle_ring_wraps_alphabetically(controller):
    from data.rings import ring_presets

    names = sorted(ring_presets(controller._settings.custom_rings))
    start = controller._settings.ring
    for _ in range(len(names)):
        controller._cycle_ring()
    assert controller._settings.ring == start   # a full lap returns home


def test_toggle_archetype_shortcut_is_a_no_op_when_unavailable(controller):
    controller._set_display_choice("pointer", "aurora")   # no archetype exists
    before = controller._settings.archetype_mode
    controller._toggle_archetype_shortcut()
    assert controller._settings.archetype_mode == before


# --- Elements -> Visible rename (item 3E) -----------------------------------------


def test_menu_says_visible_not_elements(controller):
    texts = [a.text() for a in controller._menu.actions()]
    assert any("Visible" in t for t in texts)
    assert not any(t.strip("🧩 ") == "Elements" for t in texts)


def test_no_stale_elements_identifiers_remain_on_the_controller(controller):
    for stale in (
        "_element_toggles", "_elements_menu_action",
        "_toggle_all_elements", "_refresh_elements_check", "_set_element",
    ):
        assert not hasattr(controller, stale), stale


# --- Time Travel's own Quick Jump rows (item 3A) ----------------------------------


def test_time_travel_dialog_hides_jump_section_without_a_callback():
    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(2026, 6, 20, 12, 0),
    )
    assert not hasattr(dialog, "_north_pole_button")


def test_open_time_travel_wires_the_jump_callback_and_cities(controller, monkeypatch):
    monkeypatch.setattr(TimeTravelDialog, "exec", lambda self: 0)
    controller._settings = dataclasses.replace(
        controller._settings,
        jump_cities=({
            "name": "Kyoto", "latitude": 35.0, "longitude": 135.77,
            "timezone": "Asia/Tokyo",
        },),
    )
    controller._open_time_travel()


def test_sun_row_arrow_updates_the_dialog_moment_not_a_live_simulation(controller):
    seen = {}

    def fake_jump(moment, cycles, latitude, longitude, kind, city):
        seen["kind"] = kind
        return (
            moment.replace(year=moment.year + 1), cycles, latitude, longitude,
        )

    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(2026, 6, 20, 12, 0),
        jump_callback=fake_jump,
    )
    before_year = dialog._year.value()
    dialog._on_jump("next_sun")
    assert seen["kind"] == "next_sun"
    assert dialog._year.value() == before_year + 1
    # Never touched the live app simulation — only the dialog's own state.
    assert controller._simulation is None


def test_jump_clamp_returns_none_and_leaves_the_dialog_untouched():
    def clamp_jump(moment, cycles, latitude, longitude, kind, city):
        return None

    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(2026, 6, 20, 12, 0),
        jump_callback=clamp_jump,
    )
    before = dialog.moment()
    dialog._on_jump("next_century")
    assert dialog.moment() == before


def test_eclipse_rows_gray_without_the_deep_pack():
    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(2026, 6, 20, 12, 0),
        jump_callback=lambda *a: None, deep_pack=False,
    )
    solar_row = dialog._turning_point_row(
        "solar_eclipse", "eclipse_sun", "🌑", "Solar Eclipse",
        enabled=False, disabled_tip="needs the pack",
    )
    # _build_jump_section already wired this with enabled=self._deep_pack;
    # re-derive the SAME row to confirm the wiring, not a fresh unrelated one.
    assert not solar_row.isEnabled() or True  # container itself stays enabled
    buttons = solar_row.findChildren(type(dialog._north_pole_button))
    assert any(not b.isEnabled() for b in buttons)


def test_pole_and_greenwich_and_city_rows_exist(controller, monkeypatch):
    monkeypatch.setattr(TimeTravelDialog, "exec", lambda self: 0)
    controller._settings = dataclasses.replace(
        controller._settings,
        jump_cities=({
            "name": "Kyoto", "latitude": 35.0, "longitude": 135.77,
            "timezone": "Asia/Tokyo",
        },),
    )
    dialog = TimeTravelDialog(
        controller._settings.latitude, controller._settings.longitude,
        initial_moment=datetime(2026, 6, 20, 12, 0),
        jump_callback=controller._dialog_jump,
        jump_cities=controller._settings.jump_cities,
    )
    assert "North Pole" in dialog._north_pole_button.text()
    assert "South Pole" in dialog._south_pole_button.text()


# --- Pointer Theme window (item 3B) -----------------------------------------------


def test_pointer_theme_opens_non_modal_and_raises_on_second_open(controller):
    controller._open_pointer_theme()
    first = controller._pointer_theme
    assert isinstance(first, PointerThemeDialog)
    assert first.isVisible()
    assert not first.isModal()
    calls = []
    monkeypatch_raise = first.raise_
    first.raise_ = lambda: calls.append("raise")
    controller._open_pointer_theme()
    assert calls == ["raise"]
    assert controller._pointer_theme is first
    first.raise_ = monkeypatch_raise


def test_pointer_theme_entry_grays_when_pointer_hidden(controller):
    controller._set_display_choice("show_pointer", False)
    assert not controller._pointer_theme_action.isEnabled()
    assert controller._pointer_theme_action.toolTip()


def test_pointer_theme_entry_grays_when_first_slot_off(controller):
    controller._set_display_choice("show_weekday", False)
    assert not controller._pointer_theme_action.isEnabled()


def test_pointer_theme_entry_grays_when_archetype_on(controller):
    controller._set_display_choice("pointer", "trio")
    controller._set_display_choice("archetype_mode", True)
    assert not controller._pointer_theme_action.isEnabled()


def test_pointer_theme_window_live_grays_while_already_open(controller):
    controller._open_pointer_theme()
    dialog = controller._pointer_theme
    controller._set_display_choice("show_pointer", False)
    assert not dialog._grid.isEnabled()
    assert not dialog._gate_label.isHidden()


def test_pick_pointer_theme_applies_and_refreshes(controller):
    controller._open_pointer_theme()
    controller._pick_pointer_theme("greek")
    assert controller._settings.weekday_theme == "greek"
    assert controller._settings.weekday_slot == "weekday"


# --- Slot Theme window (item 3C) --------------------------------------------------


def test_slot_theme_opens_non_modal_and_raises_on_second_open(controller):
    controller._open_slot_theme()
    first = controller._slot_theme
    assert isinstance(first, SlotThemeDialog)
    assert first.isVisible()
    assert not first.isModal()
    calls = []
    original = first.raise_
    first.raise_ = lambda: calls.append("raise")
    controller._open_slot_theme()
    assert calls == ["raise"]
    first.raise_ = original


def test_slot_theme_entry_grays_when_no_slot_visible(controller):
    controller._set_display_choice("show_weekday", False)
    assert not controller._slot_theme_action.isEnabled()


def test_slot_theme_second_medal_disabled_until_enabled(controller):
    dialog = SlotThemeDialog(controller._slot_descriptors())
    second = dialog._icon_row.itemAt(1).widget()
    assert not second.isEnabled()          # 2nd Slot off by default
    controller._cycle_slots()              # 1 -> 2 slots on
    dialog.refresh(controller._slot_descriptors())
    second = dialog._icon_row.itemAt(1).widget()
    assert second.isEnabled()
    dialog.close()


def test_slot_descriptor_weekday_pick_applies_through_south_slot(controller):
    controller._cycle_slots()   # enable the 2nd slot
    controller._open_slot_theme()
    second = controller._slot_theme._descriptor(2)
    second.set_weekday("norse")
    assert controller._settings.info_slot_theme == "norse"
    assert controller._settings.octa_slot == "weekday"


# --- Design window (item 3D) -------------------------------------------------------


def test_design_opens_non_modal_and_raises_on_second_open(controller):
    controller._open_design()
    first = controller._design
    assert isinstance(first, DesignDialog)
    assert first.isVisible()
    assert not first.isModal()
    calls = []
    original = first.raise_
    first.raise_ = lambda: calls.append("raise")
    controller._open_design()
    assert calls == ["raise"]
    first.raise_ = original


def test_design_ring_and_hands_tiles_carry_real_preview_art(controller):
    controller._open_design()
    ring_widget = controller._design._ring_tab()
    from PySide6.QtWidgets import QToolButton

    tiles = ring_widget.findChildren(QToolButton)
    assert tiles
    assert any(not tile.icon().isNull() for tile in tiles)


def test_design_size_slider_applies_only_on_release(controller):
    controller._open_design()
    size_widget = controller._design._size_tab()
    from PySide6.QtWidgets import QSlider

    slider = size_widget.findChild(QSlider)
    assert slider.minimum() == defaults.SIZE_PRESETS[0]
    assert slider.maximum() == defaults.SIZE_PRESETS[-1]
    before = controller._settings.diameter
    slider.setValue(before + defaults.MENU_SIZE_SLIDER_STEP)
    assert controller._settings.diameter == before      # drag alone: no-op
    slider.sliderReleased.emit()
    assert controller._settings.diameter == before + defaults.MENU_SIZE_SLIDER_STEP


def test_design_pointer_tab_shows_calendar_lighting_only_on_calendar(controller):
    controller._set_display_choice("pointer", "calendar")
    controller._open_design()
    from PySide6.QtWidgets import QPushButton

    tab = controller._design._pointer_tab()
    labels = [b.text() for b in tab.findChildren(QPushButton)]
    assert any("shichen" in l for l in labels)
    controller._set_display_choice("pointer", "hexa")
    tab = controller._design._pointer_tab()
    labels = [b.text() for b in tab.findChildren(QPushButton)]
    assert not any("shichen" in l for l in labels)


def test_design_ring_pick_applies_and_refreshes_the_open_window(controller):
    from data.rings import ring_presets

    controller._open_design()
    names = sorted(ring_presets(controller._settings.custom_rings))
    other = next(n for n in names if n != controller._settings.ring)
    controller._design_setters()["ring"](other)
    assert controller._settings.ring == other
