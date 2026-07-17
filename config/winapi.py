"""Win32 API literals — the ONLY sanctioned home for them in this project
(documented enum-exception to monorepo Rule #4).

Used by app/native.py (M4) for flicker-free click-through toggling,
power/clock-change notifications and the optional WorkerW glue mode.
Values are defined by the Windows SDK and never change.
"""

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
