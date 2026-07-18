"""The clock window's Z-order modes (owner 2026-07-17, ROADMAP 15e).

Pins the three-way z_mode swap and the TRUE always-on-top enforcement:
Qt's StaysOnTop hint degrades after a flag swap recreates the native
window, so "top" re-asserts topmost NATIVELY after the swap and after
every show/reshow. The native call is stubbed and its invocations are
counted — no real Win32 side effects in the test.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _make_widget():
    from app.legend_popup import LegendPopup
    from app.widget import ClockWidget

    menu = QMenu()
    return ClockWidget(360, menu, LegendPopup(), QAction("Show", menu))


def test_three_z_modes_swap_and_top_asserts_native_topmost(app, monkeypatch):
    from app import widget as widget_mod

    calls: list = []
    monkeypatch.setattr(
        widget_mod.native, "assert_topmost", lambda hwnd: calls.append(hwnd)
    )
    widget = _make_widget()
    try:
        def has(flag):
            return bool(widget.windowFlags() & flag)

        top = Qt.WindowType.WindowStaysOnTopHint
        bottom = Qt.WindowType.WindowStaysOnBottomHint

        # The three modes carry three distinct Z hints.
        assert widget.set_z_mode("bottom") is False   # already bottom
        assert has(bottom) and not has(top)
        assert widget.set_z_mode("normal") is True     # a real flag swap
        assert not has(bottom) and not has(top)        # a plain window
        assert widget.set_z_mode("top") is True
        assert has(top) and not has(bottom)
        assert widget.set_z_mode("top") is False       # no-op when unchanged

        # Native topmost is asserted only while VISIBLE in the "top" mode.
        calls.clear()
        widget.show()
        widget.reassert_z_order()
        assert calls, "top mode must re-assert native topmost after show"

        # Leaving "top" never asserts; returning to it (a visible swap) does.
        calls.clear()
        widget.set_z_mode("bottom")
        assert calls == []
        widget.set_z_mode("top")
        assert calls, "a visible swap back to top must re-assert topmost"
    finally:
        widget.close()


def test_raise_and_focus_raises_and_activates(app, monkeypatch):
    """The "Show" affordance (owner 2026-07-18, ROADMAP 15h, Session
    21-C): raise_() + activateWindow(), the Qt path for bringing the
    dial above other windows on demand in "normal" z-mode."""
    widget = _make_widget()
    try:
        calls = []
        monkeypatch.setattr(widget, "raise_", lambda: calls.append("raise"))
        monkeypatch.setattr(
            widget, "activateWindow", lambda: calls.append("activate")
        )
        widget.raise_and_focus()
        assert calls == ["raise", "activate"]
    finally:
        widget.close()


def test_reshow_reasserts_topmost_in_top_mode(app, monkeypatch):
    """The spontaneous-hide watchdog's reshow path re-asserts native
    topmost too (owner 2026-07-17) — a reshow behind the stack must ride
    back above."""
    from app import widget as widget_mod

    calls: list = []
    monkeypatch.setattr(
        widget_mod.native, "assert_topmost", lambda hwnd: calls.append(hwnd)
    )
    widget = _make_widget()
    try:
        widget.set_z_mode("top")
        widget.show()
        calls.clear()
        widget._reshow()
        assert calls, "reshow in top mode must re-assert topmost"
    finally:
        widget.close()
