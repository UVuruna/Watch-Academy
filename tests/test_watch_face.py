"""WatchFaceDialog (Phase ①+②) regressions — the window frame, the
sidebar-selection persistence across a live-apply rebuild (the SAME
"a fresh container reopens at row 0" fix `design_window.DesignDialog`
carries for its `QTabWidget`), and that the real sections list the same
variants `design_window.py`'s tabs already do (so nothing was dropped in
the split into `app/watch_face/`).
"""

from collections import defaultdict

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QToolButton

from app.settings_store import Settings
from app.watch_face.window import WatchFaceDialog, _SECTIONS
from config import constants, shortcuts
from data.hands import hand_packs
from data.rings import ring_presets


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _setters() -> dict:
    """Every key answers a no-op — the real dialog wires live setters
    through the controller (see `_RecordingSetters` in
    test_design_window.py for the analogous stub)."""
    return defaultdict(lambda: (lambda *_args, **_kwargs: None))


def _dialog(settings: Settings | None = None) -> WatchFaceDialog:
    return WatchFaceDialog(
        settings if settings is not None else Settings(), _setters()
    )


# --- R-01: the frame ---------------------------------------------------------


def test_window_builds_with_all_eight_sidebar_entries(app):
    dialog = _dialog()
    assert dialog._nav_list.count() == 8
    titles = [dialog._nav_list.item(i).text() for i in range(8)]
    assert titles == [
        "Pointer", "Ring", "Hands", "Umbra & Aura", "Opacity",
        "Themes & Slots", "Colors", "Size",
    ]
    assert dialog._stack.count() == 8
    dialog.deleteLater()


def test_placeholder_pages_read_arrives_in_a_later_phase(app):
    dialog = _dialog()
    for title, builder in _SECTIONS:
        if builder is not None:
            continue
        index = [t for t, _b in _SECTIONS].index(title)
        page = dialog._stack.widget(index)
        labels = [w.text() for w in page.findChildren(QLabel)]
        assert any("Arrives in a later phase" in text for text in labels)
    dialog.deleteLater()


def test_refresh_keeps_the_selected_sidebar_row(app):
    dialog = _dialog()
    assert dialog._nav_list.currentRow() == 0
    dialog._nav_list.setCurrentRow(5)          # the owner browses Colors
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._nav_list                 # the REBUILT widget, not the corpse
    assert isinstance(rebuilt, QListWidget)
    assert rebuilt.currentRow() == 5
    dialog.deleteLater()


def test_refresh_clamps_a_stale_row_index(app):
    dialog = _dialog()
    dialog._nav_list.setCurrentRow(dialog._nav_list.count() - 1)
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._nav_list
    assert rebuilt.currentRow() == rebuilt.count() - 1
    dialog.deleteLater()


# --- R-04/R-10/R-14: the real sections list the same variants ---------------


def test_pointer_section_lists_every_pointer_variant(app):
    dialog = _dialog()
    page = dialog._stack.widget(0)              # Pointer is index 0
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = {
        f"{constants.POINTER_DISPLAY_NAMES[variant]} ({count})"
        for variant, count in constants.POINTER_DIAL_COUNTS.items()
    }
    assert expected <= names
    dialog.deleteLater()


def test_ring_section_lists_every_ring_preset(app):
    settings = Settings()
    dialog = _dialog(settings)
    page = dialog._stack.widget(1)               # Ring is index 1
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = set(ring_presets(settings.custom_rings))
    assert expected <= names
    dialog.deleteLater()


def test_hands_section_lists_every_hand_pack(app):
    dialog = _dialog()
    page = dialog._stack.widget(2)                # Hands is index 2
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = set(hand_packs())
    assert expected <= names
    dialog.deleteLater()


# --- Wiring: the Ctrl+F shortcut exists and is dispatched --------------------


def test_open_watch_face_shortcut_is_registered():
    action_ids = {entry[0] for entry in shortcuts.SHORTCUTS}
    assert "open_watch_face" in action_ids
    assert shortcuts.shortcut_display("open_watch_face") == "Ctrl+F"


def test_open_watch_face_shortcut_never_collides_with_an_existing_combo():
    combos = [
        (key, tuple(sorted(modifiers)))
        for _action_id, key, modifiers, _description in shortcuts.SHORTCUTS
    ]
    assert len(combos) == len(set(combos)), (
        "two SHORTCUTS entries bind the same physical combo"
    )
