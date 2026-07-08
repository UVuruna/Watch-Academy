"""Win32 integration — the only module that talks to user32/kernel32.

Covers what Qt cannot: the single-instance mutex, flicker-free
click-through toggling (setWindowFlag would re-parent and hide the
window), the physical window rect for the circular hit test, and the
power/clock native events that must refresh the dial immediately.
All Win32 literals live in config/winapi.py.
"""

import ctypes
from ctypes import wintypes
from typing import Callable

from PySide6.QtCore import QAbstractNativeEventFilter

from config import winapi

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

_user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.GetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int)
_user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.SetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)

# Deliberately never closed: the mutex must live exactly as long as the
# process so a second launch can detect us.
_instance_mutex = None


def acquire_single_instance(name: str) -> bool:
    """True when this is the only running instance."""
    global _instance_mutex
    _instance_mutex = _kernel32.CreateMutexW(None, False, name)
    return _kernel32.GetLastError() != winapi.ERROR_ALREADY_EXISTS


def set_click_through(hwnd: int, enabled: bool) -> None:
    """True click-through: WS_EX_TRANSPARENT removes the window from mouse
    hit testing entirely (both buttons AND system hover pass to whatever
    lies beneath) — toggled directly because setWindowFlag() would
    re-parent and hide the window. Hover tooltips in this mode come from
    the controller's cursor poller instead."""
    style = _user32.GetWindowLongPtrW(wintypes.HWND(hwnd), winapi.GWL_EXSTYLE)
    if enabled:
        style |= winapi.WS_EX_LAYERED | winapi.WS_EX_TRANSPARENT
    else:
        style &= ~winapi.WS_EX_TRANSPARENT
    _user32.SetWindowLongPtrW(wintypes.HWND(hwnd), winapi.GWL_EXSTYLE, style)


def nchittest_falls_outside(message_ptr: int) -> bool:
    """True when the native message is a WM_NCHITTEST whose (physical,
    screen-space) point lies outside the window's inscribed circle.
    The window handle comes from the message itself — calling winId()
    here would force window creation from INSIDE window creation and
    CreateWindowEx would loop forever. Physical coordinates on both
    sides, so mixed-DPI multi-monitor setups need no conversion."""
    msg = ctypes.cast(message_ptr, ctypes.POINTER(wintypes.MSG)).contents
    if msg.message != winapi.WM_NCHITTEST:
        return False
    x = ctypes.c_short(msg.lParam & 0xFFFF).value
    y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
    rect = wintypes.RECT()
    _user32.GetWindowRect(msg.hWnd, ctypes.byref(rect))
    center_x = (rect.left + rect.right) / 2
    center_y = (rect.top + rect.bottom) / 2
    radius = min(rect.right - rect.left, rect.bottom - rect.top) / 2
    return (x - center_x) ** 2 + (y - center_y) ** 2 > radius * radius


class PowerEventFilter(QAbstractNativeEventFilter):
    """Fires the callback on resume-from-sleep and on system clock/zone
    changes — the dial must refresh immediately instead of waiting for
    the next scheduled tick (which never fired during sleep)."""

    def __init__(self, on_wake: Callable[[], None]):
        super().__init__()
        self._on_wake = on_wake

    def nativeEventFilter(self, event_type, message):
        if event_type == b"windows_generic_MSG":
            msg = ctypes.cast(int(message), ctypes.POINTER(wintypes.MSG)).contents
            if msg.message == winapi.WM_TIMECHANGE:
                self._on_wake()
            elif msg.message == winapi.WM_POWERBROADCAST and msg.wParam in (
                winapi.PBT_APMRESUMEAUTOMATIC,
                winapi.PBT_APMRESUMESUSPEND,
            ):
                self._on_wake()
        return False, 0
