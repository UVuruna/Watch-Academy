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
_shell32 = ctypes.windll.shell32

_shell32.SetCurrentProcessExplicitAppUserModelID.restype = ctypes.c_long  # HRESULT
_shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = (wintypes.LPCWSTR,)

_user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.GetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int)
_user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.SetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)
_user32.SetWindowPos.restype = wintypes.BOOL
_user32.SetWindowPos.argtypes = (
    wintypes.HWND, wintypes.HWND,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint,
)
_user32.SetWindowsHookExW.restype = ctypes.c_void_p          # HHOOK
_user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int, winapi.LL_KEYBOARD_PROC, ctypes.c_void_p, wintypes.DWORD,
)
_user32.UnhookWindowsHookEx.restype = wintypes.BOOL
_user32.UnhookWindowsHookEx.argtypes = (ctypes.c_void_p,)
_user32.CallNextHookEx.restype = ctypes.c_ssize_t            # LRESULT
_user32.CallNextHookEx.argtypes = (
    ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t,
)
_kernel32.GetModuleHandleW.restype = ctypes.c_void_p         # HMODULE
_kernel32.GetModuleHandleW.argtypes = (ctypes.c_wchar_p,)

# Deliberately never closed: the mutex must live exactly as long as the
# process so a second launch can detect us.
_instance_mutex = None


def acquire_single_instance(name: str) -> bool:
    """True when this is the only running instance."""
    global _instance_mutex
    _instance_mutex = _kernel32.CreateMutexW(None, False, name)
    return _kernel32.GetLastError() != winapi.ERROR_ALREADY_EXISTS


def set_app_user_model_id(app_id: str) -> None:
    """Give the process its OWN taskbar identity (owner screenshot
    2026-07-20: Encyclopedia/Guide/Observatory showed python's own logo
    in the Windows taskbar). Without this, Windows groups every window
    an unfrozen interpreter opens under python.exe's identity, and can
    fall back to ITS icon resource for the taskbar button regardless of
    what `QApplication.setWindowIcon` set at the Qt level — the two are
    separate identities. MUST run before the first window is created;
    it needs no QApplication and no HWND, so main() calls it first
    thing. An OS API failure here is a real, visible bug (Rule #1) —
    the call practically never fails on a supported Windows version, so
    a failure is let through loud rather than guarded (Rule #7)."""
    hr = _shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    if hr != 0:                                              # S_OK
        raise OSError(
            "SetCurrentProcessExplicitAppUserModelID failed: "
            f"hr=0x{hr & 0xFFFFFFFF:08X}"
        )


_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_VALUE = "DOMY Watch"


def _autostart_command() -> str:
    """What HKCU Run should launch: the frozen EXE, or (in development)
    pythonw with the repo's main.py."""
    import sys
    from pathlib import Path

    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    main = Path(__file__).resolve().parents[1] / "main.py"
    return f'"{pythonw}" "{main}"'


def autostart_enabled() -> bool:
    """Whether the HKCU Run entry exists (the registry IS the store —
    no duplicate flag in settings.json)."""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.QueryValueEx(key, _RUN_VALUE)
        return True
    except OSError:
        return False


def set_autostart(enabled: bool) -> None:
    """Create or remove the HKCU Run entry (standard-user autostart —
    the app never elevates, per the build conventions)."""
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        if enabled:
            winreg.SetValueEx(
                key, _RUN_VALUE, 0, winreg.REG_SZ, _autostart_command()
            )
        else:
            try:
                winreg.DeleteValue(key, _RUN_VALUE)
            except FileNotFoundError:
                pass                    # already absent — nothing to remove


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


def assert_topmost(hwnd: int) -> None:
    """Force the window to the TRUE top of the Z-order (owner 2026-07-17,
    ROADMAP 15e). Qt's WindowStaysOnTopHint degrades to ordinary stacking
    after a setWindowFlags() call recreates the native window, so the
    "top" z-mode re-asserts HWND_TOPMOST natively after every flag swap
    and every show — without moving, resizing or activating the window."""
    _user32.SetWindowPos(
        wintypes.HWND(hwnd),
        wintypes.HWND(winapi.HWND_TOPMOST),
        0, 0, 0, 0,
        winapi.SWP_NOMOVE | winapi.SWP_NOSIZE | winapi.SWP_NOACTIVATE,
    )


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


class KeyboardHook:
    """A low-level (WH_KEYBOARD_LL) keyboard hook installed ONLY while the
    cursor hovers an encyclopedia-capable dial element, so Spacebar opens
    the article WHENEVER the hover works — WITHOUT the dial ever stealing
    keyboard focus from the app the user is typing in (owner law
    2026-07-18). Installed on hover-enter of a target, uninstalled on
    hover-leave / hide / click-through toggle / quit.

    A low-level hook is GLOBAL and runs on the thread that installed it
    (the GUI thread), which must pump a message loop — Qt's own does. Its
    callback MUST stay trivial and fast: Windows silently evicts a hook
    that dawdles. On a SPACE keydown it fires `on_space` (which posts a
    QUEUED hop back to the GUI event loop — never opening the modal
    article from inside the hook proc, or the proc would not return) and
    CONSUMES the key; every other key passes straight through untouched.
    Because the consumed SPACE never reaches the focused window, the
    widget's own keyPressEvent cannot also fire — no double jump."""

    def __init__(self, on_space: "Callable[[], None]"):
        self._on_space = on_space
        self._hook = None                # the HHOOK while installed
        self._space_down = False         # de-dupe auto-repeat keydowns
        # The ctypes trampoline must outlive the hook or the callback is
        # garbage-collected out from under Windows.
        self._proc = winapi.LL_KEYBOARD_PROC(self._callback)

    @property
    def installed(self) -> bool:
        return self._hook is not None

    def install(self) -> None:
        """Idempotent: a no-op when already installed."""
        if self._hook is not None:
            return
        self._space_down = False
        hook = _user32.SetWindowsHookExW(
            winapi.WH_KEYBOARD_LL,
            self._proc,
            _kernel32.GetModuleHandleW(None),
            0,
        )
        if not hook:
            # An OS API failure must be SEEN, not swallowed (Rule #1); a
            # low-level hook install effectively never fails for a normal
            # desktop process, so let it fail loudly (Rule #7).
            raise OSError("SetWindowsHookExW(WH_KEYBOARD_LL) failed")
        self._hook = hook

    def uninstall(self) -> None:
        """Idempotent: a no-op when not installed. Deterministic teardown
        is REQUIRED — a leaked low-level hook keeps eating SPACE globally."""
        if self._hook is None:
            return
        _user32.UnhookWindowsHookEx(self._hook)
        self._hook = None
        self._space_down = False

    def _callback(self, n_code, w_param, l_param):
        if n_code == winapi.HC_ACTION:
            vk = ctypes.cast(
                l_param, ctypes.POINTER(winapi.KBDLLHOOKSTRUCT)
            ).contents.vkCode
            if vk == winapi.VK_SPACE:
                if w_param in (winapi.WM_KEYDOWN, winapi.WM_SYSKEYDOWN):
                    if not self._space_down:
                        # Fire ONCE per physical press — auto-repeat sends
                        # a stream of keydowns and the modal article must
                        # not stack.
                        self._space_down = True
                        self._on_space()
                    return 1              # consume — no CallNextHookEx
                if w_param in (winapi.WM_KEYUP, winapi.WM_SYSKEYUP):
                    self._space_down = False
                    return 1              # swallow the matching keyup too
        return _user32.CallNextHookEx(None, n_code, w_param, l_param)


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
