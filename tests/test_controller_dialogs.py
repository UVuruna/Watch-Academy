"""ITEM 1/3, R4 owner instruction batch 2026-07-20: Encyclopedia, Guide
and Observatory open NON-MODAL (`.show()`, not `.exec()`) so the dial
stays fully interactive while any of them is open; a second open
request RAISES the ONE live instance instead of stacking a duplicate
(the Encyclopedia additionally NAVIGATES a live window to a new
SPACE-jump target — a strict improvement over the old modal no-op).
Settings and Time Travel are UNCHANGED (still `.exec()` — they mutate
state transactionally). Their OPENING SIZE follows DESIGN #1: A4
portrait at 80% of the screen's available height for Encyclopedia/
Observatory, square (1:1) at 50% for Settings/Guide, both clamped to
the screen and both still respecting any existing per-dialog width
floor (the Encyclopedia's 4-gallery-tile law, Settings' own content
minimum).

Headless (QT_QPA_PLATFORM=offscreen) — builds a REAL WatchController
(standalone, as every test predating the ADD WATCH round did — main.py
itself now goes through app.watch_manager.AppController, the thin
multi-watch owner, but a bare WatchController still constructs and
behaves exactly as before), minus the single-instance mutex and
`run()`'s tray-show/scheduler-start/background-warm-thread side
effects (this module never calls `run()`, only the dialog-opening
methods, which need nothing `run()` sets up)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.encyclopedia import EncyclopediaDialog
from app.observatory import ObservatoryDialog
from app.settings_dialog.dialog import SettingsDialog
from app.settings_store import Settings
from config import defaults, encyclopedia_ui


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(app):
    made = WatchController(app)
    yield made
    # Every non-modal dialog this file opens is closed here even when a
    # test fails partway through — a stray offscreen QDialog left alive
    # cannot leak onto anyone's real screen, but closing it deterministically
    # keeps one test's window from bleeding into the next test's assertions.
    for dialog in (made._encyclopedia, made._observatory, made._watch_face):
        if dialog is not None:
            dialog.close()


def _available(dialog):
    screen = dialog.screen() or QGuiApplication.primaryScreen()
    return screen.availableGeometry()


# --- non-modal lifecycle -------------------------------------------------------

def test_encyclopedia_opens_non_modal_and_dial_stays_interactive(controller):
    controller._open_encyclopedia_at(None, 0)
    dialog = controller._encyclopedia
    assert isinstance(dialog, EncyclopediaDialog)
    assert dialog.isVisible()
    assert not dialog.isModal()      # exec() is what used to force this True
    # The dial itself keeps processing ordinary events while the dialog
    # is open — a right-click menu popup and a hover repaint are both
    # just regular Qt widget calls; exec() used to block the WHOLE
    # application's event queue (not just this dialog's), which is
    # exactly what .show() no longer does.
    controller._widget.set_tick(controller._widget._tick)
    controller._widget.update()


def test_observatory_opens_non_modal(controller):
    controller._open_observatory()
    dialog = controller._observatory
    assert isinstance(dialog, ObservatoryDialog)
    assert dialog.isVisible()
    assert not dialog.isModal()


def test_guide_opens_the_encyclopedia_on_its_card(controller):
    """SESSION 27 (owner 2026-07-28): the standalone Guide window is
    retired — the help book is a card in The Instrument, and the menu
    entry is the shortcut that opens the Encyclopedia straight on it."""
    controller._open_guide()
    dialog = controller._encyclopedia
    assert isinstance(dialog, EncyclopediaDialog)
    assert dialog.isVisible()
    assert not dialog.isModal()
    assert dialog._reader.topic_key == "guide"


# --- second open raises, never stacks -------------------------------------------

def test_encyclopedia_second_menu_open_raises_the_live_window(controller, monkeypatch):
    controller._open_encyclopedia_at("week", 0)
    first = controller._encyclopedia
    calls = []
    monkeypatch.setattr(first, "raise_", lambda: calls.append("raise"))
    monkeypatch.setattr(first, "activateWindow", lambda: calls.append("activate"))

    controller._open_encyclopedia_at(None, 0)   # the menu's plain re-open

    assert controller._encyclopedia is first    # no second instance
    assert calls == ["raise", "activate"]
    assert first.topic_key == "week"           # untouched by a topic=None reopen


def test_observatory_second_open_raises_the_live_window(controller, monkeypatch):
    controller._open_observatory()
    first = controller._observatory
    calls = []
    monkeypatch.setattr(first, "raise_", lambda: calls.append("raise"))
    monkeypatch.setattr(first, "activateWindow", lambda: calls.append("activate"))

    controller._open_observatory()

    assert controller._observatory is first
    assert calls == ["raise", "activate"]


def test_guide_second_open_raises_the_live_encyclopedia(controller, monkeypatch):
    """The Guide entry opens the Encyclopedia (Session 27), so a second
    press obeys the SAME one-live-window rule as every other opener."""
    controller._open_guide()
    first = controller._encyclopedia
    calls = []
    monkeypatch.setattr(first, "raise_", lambda: calls.append("raise"))
    monkeypatch.setattr(first, "activateWindow", lambda: calls.append("activate"))

    controller._open_guide()

    assert controller._encyclopedia is first
    assert calls == ["raise", "activate"]


# --- SPACE-jump-while-open navigates the live Encyclopedia ---------------------

def test_second_space_jump_navigates_the_live_encyclopedia(controller):
    """The strict improvement over the old modal no-op (ITEM 1, R4): a
    SPACE jump to a DIFFERENT topic while the Encyclopedia is already
    open moves the SAME live window instead of being swallowed."""
    controller._open_encyclopedia_at("week", 0)
    dialog = controller._encyclopedia
    assert dialog.topic_key == "week"

    controller._open_encyclopedia_at("moon", 2)

    assert controller._encyclopedia is dialog   # the SAME instance
    assert dialog.topic_key == "moon"
    assert dialog.entry_index == 2


def test_navigate_to_ignores_an_unknown_topic() -> None:
    dialog = EncyclopediaDialog(initial_topic="week", initial_entry=0)
    try:
        assert dialog.topic_key == "week"
        dialog.navigate_to("this_topic_does_not_exist", 0)
        assert dialog.topic_key == "week"   # untouched
    finally:
        dialog.close()


# --- closing clears the controller's reference ----------------------------------

def test_closing_the_encyclopedia_clears_the_controller_reference(controller):
    controller._open_encyclopedia_at(None, 0)
    dialog = controller._encyclopedia
    dialog.close()
    assert controller._encyclopedia is None


def test_closing_the_observatory_clears_the_controller_reference(controller):
    controller._open_observatory()
    dialog = controller._observatory
    dialog.close()
    assert controller._observatory is None


def test_closing_the_guide_clears_the_controller_reference(controller):
    controller._open_guide()
    dialog = controller._encyclopedia
    dialog.close()
    assert controller._encyclopedia is None


def test_quit_closes_every_open_non_modal_dialog(controller, monkeypatch):
    """`quit()` itself is not exercised end to end here (it saves
    settings and calls app.quit()) — only the ITEM-1-specific piece
    (widened to the Watch Face window too, the sole survivor of R5's
    three mini windows after Phase 6 FINAL cleanup): every live
    non-modal dialog is closed before teardown."""
    controller._open_encyclopedia_at(None, 0)
    controller._open_observatory()
    controller._open_watch_face()

    # Stub out everything quit() does beyond the dialog-closing loop —
    # this test's only concern is ITEM 1's addition.
    monkeypatch.setattr(controller._widget, "mark_closing", lambda: None)
    monkeypatch.setattr(controller._scheduler, "stop", lambda: None)
    monkeypatch.setattr(controller, "_capture_position", lambda: None)
    monkeypatch.setattr(controller._store, "save", lambda settings: None)
    monkeypatch.setattr(controller, "_save_timer", type(
        "S", (), {"isActive": lambda self: False}
    )())
    monkeypatch.setattr(controller._tray, "hide", lambda: None)
    monkeypatch.setattr(controller._app, "quit", lambda: None)
    import config.profiling as profiling_module
    monkeypatch.setattr(profiling_module, "flush", lambda: None)

    controller.quit()

    assert controller._encyclopedia is None
    assert controller._observatory is None
    assert controller._watch_face is None


# --- opening sizes (DESIGN #1) ---------------------------------------------------

def test_encyclopedia_opens_at_the_owners_own_opening_screen(controller):
    """SESSION 27 (owner spec 2026-07-28): the Encyclopedia opens — and
    can never be dragged below — the owner's own 1280x720 opening
    screen. The old A4-portrait opening size retired with the two-screen
    browser: the home screen's 3x3 grid is measured from the viewport,
    so this minimum is what makes "the first screen never scrolls" a
    geometric fact rather than a hope."""
    controller._open_encyclopedia_at(None, 0)
    dialog = controller._encyclopedia

    assert dialog.minimumWidth() >= encyclopedia_ui.ENCYCLOPEDIA_MIN_WIDTH_PX
    assert dialog.minimumHeight() == encyclopedia_ui.ENCYCLOPEDIA_MIN_HEIGHT_PX
    assert dialog.width() >= dialog.minimumWidth()
    assert dialog.height() >= dialog.minimumHeight()


def test_observatory_opens_a4_portrait_at_80pct_height(controller):
    controller._open_observatory()
    dialog = controller._observatory
    available = _available(dialog)
    expected_height = min(
        round(available.height() * defaults.DIALOG_A4_HEIGHT_FRACTION),
        available.height(),
    )
    expected_width = min(
        round(
            expected_height * defaults.DIALOG_A4_ASPECT_W
            / defaults.DIALOG_A4_ASPECT_H
        ),
        available.width(),
    )
    assert dialog.height() == expected_height
    assert dialog.width() == expected_width


def test_guide_opens_the_encyclopedia_at_its_card(controller):
    """The Guide has no window of its own since Session 27 — it opens
    the Encyclopedia on the guide card, at the Encyclopedia's own
    opening size."""
    controller._open_guide()
    dialog = controller._encyclopedia

    assert dialog.topic_key == "guide"
    assert dialog.height() >= encyclopedia_ui.ENCYCLOPEDIA_MIN_HEIGHT_PX


def test_settings_opens_square_at_50pct_height_or_wider(app):
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    try:
        available = _available(dialog)
        expected_height = min(
            round(available.height() * defaults.DIALOG_SQUARE_HEIGHT_FRACTION),
            available.height(),
        )
        assert dialog.height() == expected_height
        # The content-driven floor (nav column + widest panel) may make
        # this wider than a true square — "whichever is larger wins"
        # (`app.theme.size_to_screen`'s documented resolution) — but it
        # can never be NARROWER than the square target itself.
        assert dialog.width() >= min(expected_height, available.width())
    finally:
        dialog.done(0)


# ═══════════════════════ THE DEAD REFERENCE ═══════════════════════
# Owner bug 2026-08-07: "od 6 otvorenih satova CHI neće da mi otvori
# Watch Face, ostali hoće". A single-instance handler that trusts its
# own `is not None` and calls `raise_()` alone fails in two ways that
# look identical to the user — a menu item that does nothing, on one
# watch, forever. `WatchController._reopen_live` is the shared answer;
# these are its teeth, one per way of dying.

def test_a_window_hidden_without_done_opens_again(controller):
    """`finished` never fires for a window that was HIDDEN rather than
    closed, so the controller's reference stays set — and `raise_()` on
    a hidden window puts nothing back on screen. The handler must SHOW
    it again."""
    controller._open_watch_face()
    dialog = controller._watch_face
    assert dialog is not None and dialog.isVisible()

    dialog.hide()                       # no done(), so no `finished`
    assert controller._watch_face is dialog, "the reference should still be set"

    controller._open_watch_face()
    assert controller._watch_face is dialog, "it must not stack a duplicate"
    assert dialog.isVisible(), "the hidden window never came back"
    dialog.done(0)


def test_a_window_whose_c_object_died_is_replaced_not_lost(controller):
    """The other death: the Qt object is gone while the Python wrapper
    lives on, so every call on it raises `RuntimeError` inside a Qt slot
    — where it is swallowed, and the menu goes silent for good. The
    handler must drop the corpse and build a fresh window."""
    controller._open_watch_face()
    dead = controller._watch_face
    assert dead is not None

    class _Dead:
        """A wrapper whose C++ object is gone — exactly what PySide6
        raises after the real object is destroyed."""

        def show(self):
            raise RuntimeError("Internal C++ object (WatchFaceDialog) already deleted.")

        raise_ = activateWindow = show

    controller._watch_face = _Dead()
    controller._open_watch_face()

    assert isinstance(controller._watch_face, type(dead)), (
        "a dead reference must be replaced by a real window, not kept"
    )
    assert controller._watch_face.isVisible()
    controller._watch_face.done(0)
    dead.done(0)


def test_every_single_instance_window_goes_through_one_door(controller):
    """Rule #5: the Encyclopedia and the Observatory carry the same
    pattern and the same two deaths, so they share the same door. A new
    handler that hand-rolls `raise_()` again would drift straight back
    into this bug."""
    import inspect

    from app.controller import WatchController

    for name in ("_open_watch_face", "_open_observatory", "_open_encyclopedia_at"):
        source = inspect.getsource(getattr(WatchController, name))
        assert "_reopen_live" in source, name
        assert ".raise_()" not in source, f"{name} still raises by hand"
