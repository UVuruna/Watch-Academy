"""Session 21 — the SYSTEM TRIO (owner round 2026-07-18, ROADMAP 15h).

Pins what is verifiable offscreen for the three owner-reported problems:

- TASK 1 — the native low-level keyboard hook that opens the Encyclopedia
  on SPACE WITHOUT keyboard focus: its bookkeeping (idempotent
  install/uninstall, install-failure surfaces) and its callback contract
  (consume SPACE, fire ONCE per physical press, pass every other key
  through), plus the widget arming/disarming it on the hover boundary.
- TASK 2B — SPACE off the themed elements does nothing: `_last_hover` is
  cleared on leave so a stale on-target position can no longer answer.
- TASK 3 — permanent crash logging: the log file is created and a
  synthetic unhandled exception leaves a trace.

The real z-order stacking (TASK 2A) and the hook's live global key
interception need a real desktop and are NOT exercised here — see the
session report for the owner's real-machine checklist. The native Win32
entry points are stubbed; no real hook is ever installed in the suite.
"""

import ctypes
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QMenu

from app import native
from config import winapi


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class _FakeRenderer:
    """Answers the widget's hover queries from a single switch: `target`
    stands in for both a tooltip and an encyclopedia page."""

    def __init__(self):
        self.target = None               # (topic, index) or None

    def set_hover(self, x, y, size):
        return False

    def tooltip_at(self, x, y, size):
        return "an article" if self.target is not None else None

    def encyclopedia_target(self, x, y, size):
        return self.target


def _make_widget(monkeypatch, hook):
    """A ClockWidget wired to a fake renderer and a stubbed keyboard hook,
    with the native topmost assert (legend popup) neutralised."""
    from app.legend_popup import LegendPopup
    from app.widget import ClockWidget
    from app import widget as widget_mod

    monkeypatch.setattr(widget_mod.native, "KeyboardHook", lambda on_space: hook)
    monkeypatch.setattr(native, "assert_topmost", lambda hwnd: None)
    widget = ClockWidget(360, QMenu(), LegendPopup())
    renderer = _FakeRenderer()
    widget.set_renderer(renderer)
    widget.set_tick(object())            # mouseMoveEvent needs a tick
    return widget, renderer


class _RecordingHook:
    def __init__(self):
        self.installed = False
        self.log = []

    def install(self):
        self.installed = True
        self.log.append("install")

    def uninstall(self):
        self.installed = False
        self.log.append("uninstall")


# --- TASK 1: the native hook bookkeeping -------------------------------------

def _stub_win32(monkeypatch, *, hook_handle=0xABCD):
    installs, unhooks, next_hook = [], [], []
    monkeypatch.setattr(native._kernel32, "GetModuleHandleW", lambda name: 0x1000)
    monkeypatch.setattr(
        native._user32, "SetWindowsHookExW",
        lambda wh, proc, hmod, tid: installs.append((wh, hmod, tid)) or hook_handle,
    )
    monkeypatch.setattr(
        native._user32, "UnhookWindowsHookEx",
        lambda handle: unhooks.append(handle) or True,
    )
    monkeypatch.setattr(
        native._user32, "CallNextHookEx",
        lambda *a: next_hook.append(a) or 4242,
    )
    return installs, unhooks, next_hook


def test_keyboard_hook_install_is_idempotent(monkeypatch):
    installs, unhooks, _ = _stub_win32(monkeypatch)
    hook = native.KeyboardHook(lambda: None)

    assert hook.installed is False
    hook.install()
    hook.install()                        # idempotent — one real install
    assert hook.installed is True
    assert len(installs) == 1
    assert installs[0][0] == winapi.WH_KEYBOARD_LL

    hook.uninstall()
    hook.uninstall()                      # idempotent — one real unhook
    assert hook.installed is False
    assert unhooks == [0xABCD]


def test_keyboard_hook_install_failure_is_visible(monkeypatch):
    _stub_win32(monkeypatch, hook_handle=0)   # NULL == failure
    hook = native.KeyboardHook(lambda: None)
    with pytest.raises(OSError):
        hook.install()
    assert hook.installed is False


def _space_event(vk=winapi.VK_SPACE):
    kb = winapi.KBDLLHOOKSTRUCT()
    kb.vkCode = vk
    return kb, ctypes.addressof(kb)


def test_hook_consumes_space_and_fires_once_per_press(monkeypatch):
    _stub_win32(monkeypatch)
    fired = []
    hook = native.KeyboardHook(lambda: fired.append(1))
    _kb, addr = _space_event()

    # keydown: fires the jump AND consumes the key (return 1).
    assert hook._callback(winapi.HC_ACTION, winapi.WM_KEYDOWN, addr) == 1
    assert fired == [1]
    # auto-repeat keydown: still consumed, must NOT re-fire.
    assert hook._callback(winapi.HC_ACTION, winapi.WM_KEYDOWN, addr) == 1
    assert fired == [1]
    # keyup: consumed, resets the latch.
    assert hook._callback(winapi.HC_ACTION, winapi.WM_KEYUP, addr) == 1
    # a fresh press fires again.
    assert hook._callback(winapi.HC_ACTION, winapi.WM_KEYDOWN, addr) == 1
    assert fired == [1, 1]


def test_hook_passes_other_keys_through(monkeypatch):
    _, _, next_hook = _stub_win32(monkeypatch)
    fired = []
    hook = native.KeyboardHook(lambda: fired.append(1))
    _kb, addr = _space_event(vk=0x41)     # 'A'

    result = hook._callback(winapi.HC_ACTION, winapi.WM_KEYDOWN, addr)
    assert result == 4242                 # CallNextHookEx sentinel
    assert fired == []                    # never triggered
    assert len(next_hook) == 1

    # nCode < 0 must also defer to the next hook untouched.
    _kb2, addr2 = _space_event()
    assert hook._callback(-1, winapi.WM_KEYDOWN, addr2) == 4242
    assert fired == []


# --- TASK 1: the widget arms/disarms the hook on the hover boundary ---------

def test_widget_arms_hook_only_over_a_target(app, monkeypatch):
    hook = _RecordingHook()
    widget, renderer = _make_widget(monkeypatch, hook)
    try:
        size = float(widget.dial_diameter)
        margin = widget.margin_px

        def move_to(local):
            ev = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(local, local), QPointF(local, local),
                Qt.MouseButton.NoButton, Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )
            widget.mouseMoveEvent(ev)

        # Over a target (renderer speaks a page) → the hook arms.
        renderer.target = ("weekday", 0)
        move_to(margin + size / 2)
        assert hook.installed is True

        # Off any target → the hook disarms.
        renderer.target = None
        move_to(margin + size / 2)
        assert hook.installed is False
    finally:
        widget.close()


def test_leave_clears_last_hover_and_disarms_hook(app, monkeypatch):
    hook = _RecordingHook()
    widget, renderer = _make_widget(monkeypatch, hook)
    try:
        # Pretend the cursor sat on a target: a live hover and an armed hook.
        widget._last_hover = (10.0, 20.0)
        widget._update_space_hook(("weekday", 0))
        assert hook.installed is True

        widget.leaveEvent(QEvent(QEvent.Type.Leave))
        assert widget._last_hover is None      # owner 15h item 3B
        assert hook.installed is False
    finally:
        widget.close()


def test_bypass_key_disarms_hook_and_clears_hover(app, monkeypatch):
    hook = _RecordingHook()
    widget, renderer = _make_widget(monkeypatch, hook)
    try:
        widget._last_hover = (10.0, 20.0)
        widget._update_space_hook(("weekday", 0))
        assert hook.installed is True

        from config import defaults
        bypass = getattr(Qt.KeyboardModifier, defaults.HOVER_BYPASS_MODIFIER)
        ev = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(50, 50), QPointF(50, 50),
            Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, bypass,
        )
        widget.mouseMoveEvent(ev)
        assert widget._last_hover is None
        assert hook.installed is False
    finally:
        widget.close()


# --- TASK 2B: SPACE only fires on a live target ------------------------------

def test_space_jump_noop_without_a_live_hover(app, monkeypatch):
    hook = _RecordingHook()
    widget, renderer = _make_widget(monkeypatch, hook)
    try:
        emitted = []
        widget.open_encyclopedia.connect(lambda t, i: emitted.append((t, i)))

        widget._last_hover = None
        widget._trigger_space_jump()
        assert emitted == []              # cleared hover → nothing

        # A live on-target hover DOES open the page.
        renderer.target = ("seasons", 2)
        widget._last_hover = (30.0, 40.0)
        widget._trigger_space_jump()
        assert emitted == [("seasons", 2)]

        # A live hover OFF any target stays inert (owner 15h item 3B).
        emitted.clear()
        renderer.target = None
        widget._trigger_space_jump()
        assert emitted == []
    finally:
        widget.close()


# --- TASK 2A: the legend popup rides topmost ---------------------------------

def test_legend_popup_is_topmost_and_asserts_native(app, monkeypatch):
    from app.legend_popup import LegendPopup

    asserted = []
    monkeypatch.setattr(native, "assert_topmost", lambda hwnd: asserted.append(hwnd))
    popup = LegendPopup()
    try:
        assert bool(popup.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        from PySide6.QtCore import QPoint

        popup.show_html("<b>hello</b>", QPoint(100, 100))
        assert asserted, "show_html must re-assert native topmost"
    finally:
        popup.close()


# --- TASK 3: crash logging ---------------------------------------------------

def test_crash_log_records_a_synthetic_exception(tmp_path, monkeypatch):
    import faulthandler

    import main as main_mod

    user_dir = tmp_path / "DOMY Watch"
    monkeypatch.setattr(main_mod.paths, "user_dir", lambda: user_dir)
    # A known, harmless previous hook so delegation is a no-op.
    monkeypatch.setattr(sys, "excepthook", lambda *a: None)
    try:
        main_mod._install_crash_logging()
        log = user_dir / "crash.log"
        assert log.exists()
        assert "session" in log.read_text(encoding="utf-8")

        try:
            raise ValueError("synthetic boom")
        except ValueError:
            sys.excepthook(*sys.exc_info())

        text = log.read_text(encoding="utf-8")
        assert "synthetic boom" in text
        assert "ValueError" in text
    finally:
        faulthandler.disable()
        if main_mod._crash_log is not None:
            main_mod._crash_log.close()
            main_mod._crash_log = None
