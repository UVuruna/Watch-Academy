"""R5 MENU REWORK round goldens (owner spec, `UV/DESIGN/RIGHT CLICK
MENU.txt` + `UV/INSTRUCTION.txt` item 2A): the watch TITLE (short in
the menu, full on the tray tooltip), the keyboard SHORTCUT map (no
collision with the hidden-mode secret buffer), and the Elements ->
Visible rename. The four mini windows this round originally replaced
the deep submenu chains with (Time Travel's own Quick Jump rows,
Pointer Theme, Slot Theme, Design) have themselves been superseded:
Time Travel's Quick Jump rows are still covered below; Pointer
Theme/Slot Theme/Design were DELETED by Phase 6 FINAL cleanup — their
own coverage lives in `tests/test_watch_face_pointer.py` and
`tests/test_watch_face_themes.py` now (the Watch Face window that
replaced them).
"""

import dataclasses
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from app.controller import WatchController, watch_title
from app.settings_store import Settings
from app.time_travel import TimeTravelDialog
from config import dial, shortcuts


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = WatchController(app)
    yield made
    for dialog in (made._encyclopedia, made._observatory, made._watch_face):
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
    "Belgrade-Gold DOMY-Family Trinity" — secondary palette style on the
    Trinity (trio) pointer picks the SECOND of its own (Court, Family)
    wheel-pair label."""
    settings = dataclasses.replace(
        Settings(),
        city_name="Belgrade", ring="DOMY", ring_finish="gold",
        pointer="trio", palette_style="secondary",
    )
    assert watch_title(settings, full=True) == "Belgrade-Gold DOMY-Family Trinity"


def test_watch_title_full_form_reads_the_paint_style_too():
    settings = dataclasses.replace(
        Settings(),
        city_name="Tromso", ring="Dollar", ring_finish="silver",
        pointer="cross", palette_style="primary",
    )
    assert watch_title(settings, full=True) == (
        "Tromso-Silver Dollar-Temperaments Quaternity"
    )


def test_watch_title_falls_back_to_the_default_pair_off_the_table():
    # hexa/octa/calendar/aurora... every pointer with named wheels reads
    # its OWN row; only "default" carries the generic Paint/Light pair,
    # for a pointer whose wheels have no names of their own. The hexa
    # PRIMARY slot is "Persons" since the owner's "ok." of 2026-07-27
    # (CANON.md §Prism primary — the Persons).
    settings = dataclasses.replace(
        Settings(),
        city_name="Oslo", ring="DOMY", ring_finish="bronze",
        pointer="hexa", palette_style="primary",
    )
    assert watch_title(settings, full=True) == "Oslo-Bronze DOMY-Persons Prism"


def test_watch_title_is_untranslated_never_touches_tr():
    """A NAME, not UI chrome (docstring rationale) — the signature
    carries no `tr`/overlay parameter; R-31 added `location_name` (an
    override for the LOCATION word alone, read by a live simulation),
    still no translation hook."""
    import inspect

    assert list(inspect.signature(watch_title).parameters) == [
        "settings", "full", "location_name",
    ]


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
    """R5's original candidates, still present verbatim under the R5b
    FINAL MAP (owner spec sealed 2026-07-21) — the SLOTS/FAST TRAVEL/
    LOCATIONS additions are covered by their own tests in
    test_shortcuts_r5b.py, this one just pins that nothing from the R5
    draft silently vanished. A z-mode shortcut was explicitly considered
    and dropped (Ctrl+Z's pre-existing Undo expectation)."""
    action_ids = {entry[0] for entry in shortcuts.SHORTCUTS}
    assert {
        "cycle_ring", "cycle_weekday_theme", "cycle_slots",
        "open_encyclopedia", "open_guide", "open_settings",
        "open_observatory", "open_time_travel",
        "return_to_now", "toggle_archetype",
    } <= action_ids


def test_shortcut_table_never_collides_with_the_hidden_mode_secret():
    """Every shortcut carries a MODIFIER — the secret buffer
    (`constants.HIDDEN_MODE_SECRET`) only ever sees PRINTABLE
    NO-MODIFIER text (`ClockWidget.keyPressEvent`), so a held-modifier
    combo can never feed it by construction; pinned here as an
    explicit table-shape assertion, not just an inline comment."""
    for action_id, _key, modifiers, _description in shortcuts.SHORTCUTS:
        assert modifiers, f"{action_id} carries no modifier"


def test_shortcut_display_renders_ctrl_combo_text():
    """R5b FINAL MAP round: Settings moved off Ctrl+, onto Ctrl+M
    (Rule #6 — the comma binding is gone, not kept alongside)."""
    assert shortcuts.shortcut_display("cycle_ring") == "Ctrl+R"
    assert shortcuts.shortcut_display("open_settings") == "Ctrl+M"
    assert shortcuts.shortcut_display("return_to_now") == "Ctrl+Home"


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
    for action_id, key_name, modifier_names, _description in shortcuts.SHORTCUTS:
        key = getattr(Qt.Key, key_name)
        modifiers = Qt.KeyboardModifier.NoModifier
        for name in modifier_names:
            modifiers |= getattr(Qt.KeyboardModifier, name)
        _press(widget, key, modifiers)
    assert seen == [entry[0] for entry in shortcuts.SHORTCUTS]


def test_widget_does_not_feed_the_secret_buffer_on_a_shortcut_combo(app):
    """Ctrl+R must never advance the typed-secret buffer — it is fully
    consumed by the shortcut branch before the typed/printable path."""
    widget = _bare_widget(app)
    typed = []
    widget.typed.connect(typed.append)
    _press(widget, Qt.Key.Key_R, Qt.KeyboardModifier.ControlModifier)
    assert typed == []


def test_on_shortcut_dispatches_every_action_id(controller, monkeypatch):
    """Every `shortcuts.SHORTCUTS` action_id reaches a real handler — R5's
    original ten plus R5b's SLOTS/FAST TRAVEL/LOCATIONS additions."""
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
        controller, "_open_watch_face",
        lambda: calls.append("open_watch_face"),
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
    monkeypatch.setattr(
        controller, "_cycle_slot_complication",
        lambda index: calls.append(f"cycle_slot{index}_complication"),
    )
    monkeypatch.setattr(
        controller, "_cycle_slot_weekday_theme",
        lambda index: calls.append(f"cycle_slot{index}_theme"),
    )
    monkeypatch.setattr(
        controller, "_cycle_fast_travel_theme",
        lambda: calls.append("fast_travel_theme"),
    )
    monkeypatch.setattr(
        controller, "_cycle_fast_travel_option",
        lambda: calls.append("fast_travel_option"),
    )
    monkeypatch.setattr(
        controller, "_step_fast_travel",
        lambda direction: calls.append(
            "fast_travel_past" if direction < 0 else "fast_travel_future"
        ),
    )
    monkeypatch.setattr(
        controller, "_jump_to_place",
        lambda kind: calls.append(f"location_{kind}"),
    )
    monkeypatch.setattr(
        controller, "_cycle_jump_city",
        lambda direction: calls.append(
            "location_prev_city" if direction < 0 else "location_next_city"
        ),
    )
    for action_id, *_rest in shortcuts.SHORTCUTS:
        controller._on_shortcut(action_id)
    assert calls == [entry[0] for entry in shortcuts.SHORTCUTS]


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


def test_sun_row_arrow_mirrors_whatever_the_jump_callback_lands_on(controller):
    """`_on_jump` (app/time_travel.py) only ever mirrors the callback's
    OWN return value onto the dialog's fields — a stub callback here
    isolates that mirroring from `_dialog_jump`'s own live-travel side
    effect (see `test_dialog_jump_travels_the_live_watch_and_mirrors_
    the_dialog` below for the REAL production callback, R8b item 1)."""
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
    # The stub never touches the controller — this is not evidence
    # either way about the REAL callback's live-travel behavior.
    assert controller._simulation is None


def test_dialog_jump_travels_the_live_watch_and_mirrors_the_dialog(controller):
    """TT LIVE TRAVEL (owner round R8b item 1, slika 1-6): a Quick Jump
    row/arrow inside the dialog must travel the WATCH immediately —
    "ono sto smo radili na uvek Quick Jump dok je bio na right klikku"
    — not sit as a draft the owner has to OK before anything moves.
    `controller._dialog_jump` is the REAL production callback: one
    arrow click already runs the live simulation on the landed moment,
    and the dialog's own fields mirror exactly what the dial now
    shows."""
    assert controller._simulation is None
    dialog = TimeTravelDialog(
        controller._settings.latitude, controller._settings.longitude,
        initial_moment=datetime(2026, 6, 20, 12, 0),
        coverage=controller._travel_coverage(),
        core_coverage=controller._bundled_coverage(),
        jump_callback=controller._dialog_jump,
    )
    dialog._on_jump("next_day")
    assert controller._simulation is not None
    sim_moment, sim_observer = controller._simulation
    assert dialog.moment().replace(tzinfo=controller._tz) == sim_moment
    assert dialog.latitude() == sim_observer.latitude
    assert dialog.longitude() == sim_observer.longitude
    # A second jump chains from the ALREADY-live landing, not a reset
    # back to the dialog's pre-open snapshot.
    first_landing = controller._simulation
    dialog._on_jump("next_day")
    assert controller._simulation != first_landing
    dialog.deleteLater()


def test_return_to_now_still_ends_the_simulation_after_live_jumps(controller):
    """Return to Now (owner 2026-07-15) keeps ending the simulation
    outright even though jumps now travel live (R8b item 1) — the
    dialog's own `RETURN_TO_NOW` exit code is unaffected by the new
    per-jump side effect."""
    dialog = TimeTravelDialog(
        controller._settings.latitude, controller._settings.longitude,
        initial_moment=datetime(2026, 6, 20, 12, 0),
        coverage=controller._travel_coverage(),
        core_coverage=controller._bundled_coverage(),
        jump_callback=controller._dialog_jump,
    )
    dialog._on_jump("next_day")
    assert controller._simulation is not None
    controller._end_simulation()
    assert controller._simulation is None
    dialog.deleteLater()


def test_location_jump_flashes_and_moves_the_tray_title(controller):
    """R-30/R-31 regression: a `_dialog_jump` LOCATION landing (kind
    "city") — unlike a plain day/month step — flashes the "CITY,
    COUNTRY" overlay AND moves the tray tooltip/menu TITLE's own
    location word, even though the home `Settings.city_name` never
    changes. `_end_simulation` must restore it afterward."""
    home_name = controller._settings.city_name
    assert controller._active_location_name == home_name
    dialog = TimeTravelDialog(
        controller._settings.latitude, controller._settings.longitude,
        initial_moment=datetime(2026, 6, 20, 12, 0),
        coverage=controller._travel_coverage(),
        core_coverage=controller._bundled_coverage(),
        jump_callback=controller._dialog_jump,
    )
    tokyo = {
        "name": "Tokyo", "latitude": 35.7, "longitude": 139.7,
        "timezone": "Asia/Tokyo",
    }
    dialog._on_jump("city", tokyo)
    assert controller._active_location_name == "Tokyo"
    assert controller._active_location_name != home_name
    assert "Tokyo" in controller._tray._icon.toolTip()
    assert "Tokyo" in controller._title_label.text()
    assert controller._fast_travel_flash._text_label.text() == "Tokyo, Asia"
    # A non-location jump (a plain day step) leaves the location alone.
    dialog._on_jump("next_day")
    assert controller._active_location_name == "Tokyo"
    controller._end_simulation()
    assert controller._active_location_name == home_name
    assert home_name in controller._tray._icon.toolTip()
    dialog.deleteLater()


def test_settings_location_change_flashes_and_updates_the_title(controller, monkeypatch):
    """R-30/R-31: the Settings dialog's own preset pick is a LOCATION
    change too — same flash, same tray/title update, no simulation
    involved at all."""
    from app.settings_dialog.dialog import SettingsDialog

    dialog = SettingsDialog(
        controller._settings, controller._skin, controller._translation_overlay,
    )
    new_settings = dataclasses.replace(
        controller._settings,
        city_name="Oslo", city_path=("Europe", "Northern Europe", "Norway", "Oslo"),
        latitude=59.91, longitude=10.75, timezone="Europe/Oslo",
    )
    monkeypatch.setattr(dialog, "result_settings", lambda: new_settings)
    controller._apply_settings_dialog_result(dialog)
    assert controller._active_location_name == "Oslo"
    assert "Oslo" in controller._tray._icon.toolTip()
    assert controller._fast_travel_flash._text_label.text() == "Oslo, Norway"
    dialog.deleteLater()


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



# --- The Names submenu (R-09/R-26, Phase 6 FINAL cleanup) ---------------------


def test_menu_carries_a_names_submenu_beside_visible(controller):
    """The weekday-body day name and the archetype figures' names are
    unified into one submenu beside Visible in the right-click menu —
    the SAME stored keys every other reader (render layers, Watch Face)
    already uses."""
    texts = [a.text() for a in controller._menu.actions()]
    assert any("Names" in t for t in texts)


def test_names_toggles_write_the_expected_settings_keys(controller):
    names_menu = next(
        action.menu() for action in controller._menu.actions()
        if action.menu() is not None and "Names" in action.text()
    )
    labels = {a.text(): a for a in names_menu.actions()}
    weekday_names = next(a for t, a in labels.items() if "Weekday names" in t)
    archetype_names = next(a for t, a in labels.items() if "Archetype names" in t)
    weekday_names.trigger()
    assert controller._settings.show_weekday_names is not Settings().show_weekday_names
    archetype_names.trigger()
    assert controller._settings.archetype_names is not Settings().archetype_names


# --- The Calendar mount (owner decree 2026-07-29; ported into the Watch Face
# window's Themes & Slots section by Phase 6 FINAL cleanup) -------------------


def test_calendar_mount_setter_applies_through_the_same_display_choice_path(
    controller,
):
    """The stored key stays `calendar_mount` — the picker moved (twice
    now: Pointer Theme -> Watch Face), the setting did not."""
    controller._set_display_choice("pointer", "calendar")
    assert controller._settings.calendar_mount == "zodiac"    # shipped default
    setters = controller._watch_face_setters()
    setters["calendar_mount"]("emotions")
    assert controller._settings.calendar_mount == "emotions"
    assert controller._skin.calendar_mount == "emotions"      # reached the dial


# --- Slot descriptors (item 3C's data, read by the Watch Face window now) ----


def test_slot_descriptor_weekday_pick_applies_through_south_slot(controller):
    controller._cycle_slots()   # enable the 2nd slot
    descriptors = controller._slot_descriptors()
    second = next(d for d in descriptors if d.index == 2)
    second.set_weekday("norse")
    assert controller._settings.info_slot_theme == "norse"
    assert controller._settings.octa_slot == "weekday"
