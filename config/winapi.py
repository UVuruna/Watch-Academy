"""Win32 API literals — the ONLY sanctioned home for them in this project
(documented enum-exception to monorepo Rule #4).

Used by app/native.py (M4) for flicker-free click-through toggling,
power/clock-change notifications, the optional WorkerW glue mode, and
the low-level keyboard hook that delivers Spacebar to the unfocused dial
(Session 21). The literals are defined by the Windows SDK and never
change; the two ctypes definitions (the KBDLLHOOKSTRUCT layout and the
hook-callback prototype) are the ABI those literals ride on, so they
live here with them.
"""

import ctypes
from ctypes import wintypes

# SetWindowLongPtrW index
GWL_EXSTYLE = -20

# Extended window styles
WS_EX_LAYERED = 0x0008_0000
WS_EX_TRANSPARENT = 0x0000_0020

# Window messages
WM_TIMECHANGE = 0x001E
WM_POWERBROADCAST = 0x0218
WM_NCHITTEST = 0x0084

# WM_POWERBROADCAST wParam values
PBT_APMRESUMESUSPEND = 0x0007
PBT_APMRESUMEAUTOMATIC = 0x0012

# WM_NCHITTEST return value: "this point is not mine, pass it through"
HTTRANSPARENT = -1

# SetWindowPos: the TRUE always-on-top assertion (owner 2026-07-17,
# ROADMAP 15e). Qt's WindowStaysOnTopHint degrades to normal stacking
# after a flag swap recreates the native window, so the "top" z-mode
# re-asserts topmost natively after every flag swap and every show.
HWND_TOPMOST = -1                        # place above all non-topmost windows
SWP_NOSIZE = 0x0001                      # keep the current size
SWP_NOMOVE = 0x0002                      # keep the current position
SWP_NOACTIVATE = 0x0010                  # do not steal focus

# Undocumented Progman message that spawns the WorkerW wallpaper host
# (optional "glue to wallpaper" mode, best-effort on Windows 11 24H2)
WM_SPAWN_WORKERW = 0x052C

# Kernel error codes
ERROR_ALREADY_EXISTS = 183

# --- Low-level keyboard hook (Session 21) -----------------------------------
# SetWindowsHookEx(WH_KEYBOARD_LL) lets Spacebar open the Encyclopedia
# WHENEVER the hover works, without the dial ever taking keyboard focus
# from the app the user is typing in (owner law 2026-07-18). The hook is
# installed ONLY while the cursor sits on an encyclopedia-capable element
# and consumes SPACE; every other key passes through. See app/native.py.

WH_KEYBOARD_LL = 13                      # global low-level keyboard hook
HC_ACTION = 0                            # the nCode worth acting on

# Key messages the hook's wParam carries
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104                   # a key pressed with ALT held
WM_SYSKEYUP = 0x0105

# Virtual-key code
VK_SPACE = 0x20


class KBDLLHOOKSTRUCT(ctypes.Structure):
    """The struct the low-level keyboard hook's lParam points at — only
    `vkCode` is read (which key), the rest complete the SDK layout."""

    _fields_ = (
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),   # ULONG_PTR
    )


# LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam,
#                                       LPARAM lParam). The pointer-wide
# integer types: LRESULT/LPARAM = LONG_PTR (c_ssize_t), WPARAM = UINT_PTR
# (c_size_t). WINFUNCTYPE gives the __stdcall trampoline Windows calls.
LL_KEYBOARD_PROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,   # LRESULT
    ctypes.c_int,       # nCode
    ctypes.c_size_t,    # WPARAM — the key message
    ctypes.c_ssize_t,   # LPARAM — a KBDLLHOOKSTRUCT pointer
)
