"""ADD WATCH round (owner INSTRUCTION.txt item 2, sealed 2026-07-21):
the process-wide `AppController` (app/watch_manager.py) builds and
tears down the watch roster — seeding a new watch from the current
one's settings, deleting a removed watch's settings file, the anchor
(watch 1) refusing removal, and the menu TITLE row switching short/full
as the roster grows and shrinks.

Headless (QT_QPA_PLATFORM=offscreen), built exactly like main.py minus
the single-instance mutex — the same pattern test_controller_dialogs.py
and test_menu_rework.py already use for a single WatchController.
"""

import dataclasses
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from app.controller import WatchController, watch_title
from app.watch_manager import AppController
from config import paths


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _no_background_warmup(monkeypatch):
    """`add_watch()` calls the new watch's real `run()` (production
    needs it — a watch added mid-session must actually show/tray/tick),
    which spawns a background thread pre-building the disk raster
    cache. That thread's own cost is legitimately real work (~90s cold,
    per controller.md's own measurement) that every OTHER test in this
    suite avoids entirely by never calling `run()` — this file is the
    first to need `run()` at all, so it neutralizes just that one
    thread (a no-op stand-in) rather than paying the full warm-up on
    every fresh `tmp_path` this file's tests hand it."""
    monkeypatch.setattr(WatchController, "_warm_caches", lambda self: None)


@pytest.fixture
def manager(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    made = AppController(app)
    yield made
    for watch in made._watches:
        for dialog in (
            watch._encyclopedia, watch._observatory, watch._guide,
            watch._design, watch._pointer_theme, watch._slot_theme,
        ):
            if dialog is not None:
                dialog.close()
        watch._scheduler.stop()
        watch._tray.hide()


def _accept_removal(monkeypatch):
    monkeypatch.setattr(
        QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Yes
    )


# --- startup: one anchor watch ----------------------------------------------------


def test_starts_with_exactly_one_anchor_watch(manager):
    assert len(manager._watches) == 1
    assert manager._watches[0].watch_index == 1
    assert manager._watches[0].settings_path == paths.settings_path(1)


def test_anchor_watch_title_is_short_form_alone(manager):
    watch = manager._watches[0]
    assert watch._title_label.text() == watch_title(watch._settings, full=False)


# --- add watch ----------------------------------------------------------------


def test_add_watch_creates_a_second_watch_with_its_own_settings_file(manager):
    manager.add_watch(manager._watches[0])
    assert len(manager._watches) == 2
    second = manager._watches[1]
    assert second.watch_index == 2
    assert second.settings_path == paths.settings_path(2)
    assert second.settings_path.exists()


def test_added_watch_seeds_from_the_current_watch_settings(manager):
    first = manager._watches[0]
    first._settings = dataclasses.replace(first._settings, ring="Morph", diameter=480)
    manager.add_watch(first)
    second = manager._watches[1]
    assert second._settings.ring == "Morph"
    assert second._settings.diameter == 480


def test_added_watch_position_is_cleared_so_it_does_not_overlap_its_seed(manager):
    first = manager._watches[0]
    first._settings = dataclasses.replace(first._settings, window_x=100, window_y=100)
    manager.add_watch(first)
    second = manager._watches[1]
    # None,None re-centers on the primary screen — WatchController's own
    # existing first-run behavior, reused rather than reinvented.
    assert second._settings.window_x is None
    assert second._settings.window_y is None


def test_third_watch_gets_index_three(manager):
    manager.add_watch(manager._watches[0])
    manager.add_watch(manager._watches[0])
    assert [w.watch_index for w in manager._watches] == [1, 2, 3]


# --- title short/full switching by watch count ------------------------------------


def test_titles_switch_to_full_form_once_a_second_watch_exists(manager):
    first = manager._watches[0]
    assert first._title_label.text() == watch_title(first._settings, full=False)
    manager.add_watch(first)
    second = manager._watches[1]
    assert first._title_label.text() == watch_title(first._settings, full=True)
    assert second._title_label.text() == watch_title(second._settings, full=True)


def test_tray_tooltip_is_always_full_regardless_of_count(manager):
    """Unchanged sealed behavior: the tray HOVER stays full even with
    only one watch — only the menu TITLE row depends on the count."""
    watch = manager._watches[0]
    assert watch._tray._icon.toolTip() == watch_title(watch._settings, full=True)


# --- remove watch -------------------------------------------------------------


def test_watch_one_cannot_be_removed(manager, monkeypatch):
    _accept_removal(monkeypatch)
    manager.remove_watch(manager._watches[0])
    assert len(manager._watches) == 1


def test_watch_one_never_offers_the_remove_menu_entry(manager):
    texts = [a.text() for a in manager._watches[0]._menu.actions()]
    assert not any("Remove this Watch" in t for t in texts)


def test_second_watch_offers_the_remove_menu_entry(manager):
    manager.add_watch(manager._watches[0])
    texts = [a.text() for a in manager._watches[1]._menu.actions()]
    assert any("Remove this Watch" in t for t in texts)


def test_remove_confirms_before_deleting(manager, monkeypatch):
    manager.add_watch(manager._watches[0])
    second = manager._watches[1]
    monkeypatch.setattr(
        QMessageBox, "exec", lambda self: QMessageBox.StandardButton.No
    )
    second._confirm_remove_watch()
    assert len(manager._watches) == 2         # declined: nothing removed
    assert second.settings_path.exists()


def test_remove_deletes_the_watch_and_its_settings_file(manager, monkeypatch):
    manager.add_watch(manager._watches[0])
    second = manager._watches[1]
    second_path = second.settings_path
    _accept_removal(monkeypatch)
    second._confirm_remove_watch()
    assert len(manager._watches) == 1
    assert second not in manager._watches
    assert not second_path.exists()


def test_removed_watch_index_is_never_reused_while_a_higher_one_survives(
    manager, monkeypatch,
):
    """1, 2, 3 exist; removing 2 leaves [1, 3] — the next Add Watch
    continues past the highest surviving index (4), never refilling
    the gap left at 2 (so a later watch never inherits a color/identity
    that used to belong to a different, already-removed watch)."""
    first = manager._watches[0]
    manager.add_watch(first)
    manager.add_watch(first)
    second = next(w for w in manager._watches if w.watch_index == 2)
    _accept_removal(monkeypatch)
    second._confirm_remove_watch()
    assert [w.watch_index for w in manager._watches] == [1, 3]
    manager.add_watch(first)
    assert [w.watch_index for w in manager._watches] == [1, 3, 4]


def test_removing_the_only_extra_watch_frees_its_index_for_reuse(manager, monkeypatch):
    """The common case: add watch 2, remove it, add again — nothing
    else occupies a higher index, so watch 2's own slot (and its
    rose-gold tray identity) comes right back."""
    first = manager._watches[0]
    manager.add_watch(first)
    second = manager._watches[1]
    _accept_removal(monkeypatch)
    second._confirm_remove_watch()
    assert [w.watch_index for w in manager._watches] == [1]
    manager.add_watch(first)
    assert [w.watch_index for w in manager._watches] == [1, 2]


def test_removing_back_to_one_watch_restores_the_short_title(manager, monkeypatch):
    first = manager._watches[0]
    manager.add_watch(first)
    second = manager._watches[1]
    _accept_removal(monkeypatch)
    second._confirm_remove_watch()
    assert first._title_label.text() == watch_title(first._settings, full=False)


# --- exit is process-wide, remove is per-watch -------------------------------------


def test_exit_action_on_any_watch_is_wired_to_quit_all(manager):
    manager.add_watch(manager._watches[0])
    for watch in manager._watches:
        assert watch._on_exit == manager.quit_all


def test_quit_all_tears_down_every_watch_and_quits_once(manager, monkeypatch):
    manager.add_watch(manager._watches[0])
    calls = []
    for watch in manager._watches:
        monkeypatch.setattr(
            watch, "_prepare_quit", lambda w=watch: calls.append(w.watch_index)
        )
    monkeypatch.setattr(manager._app, "quit", lambda: calls.append("app.quit"))
    manager.quit_all()
    assert calls == [1, 2, "app.quit"]


# --- persistence across a restart --------------------------------------------------


def test_restart_rediscovers_every_watch_on_disk(app, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    first_run = AppController(app)
    first_run.add_watch(first_run._watches[0])
    first_run.add_watch(first_run._watches[0])
    assert [w.watch_index for w in first_run._watches] == [1, 2, 3]
    first_run.quit_all()

    second_run = AppController(app)
    try:
        assert [w.watch_index for w in second_run._watches] == [1, 2, 3]
    finally:
        for watch in second_run._watches:
            watch._scheduler.stop()
            watch._tray.hide()
