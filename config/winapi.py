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

# Undocumented Progman message that spawns the WorkerW wallpaper host
# (optional "glue to wallpaper" mode, best-effort on Windows 11 24H2)
WM_SPAWN_WORKERW = 0x052C

# Kernel error codes
ERROR_ALREADY_EXISTS = 183
