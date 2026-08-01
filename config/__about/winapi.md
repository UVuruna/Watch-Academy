# Win32 API Literals

**Script:** [Win32 API Literals (script)](../winapi.py)

## Purpose

The only sanctioned home for Win32 API constants in this project — a
documented enum-exception to monorepo Rule #4 (no hardcoded values):
the literals are defined by the Windows SDK and never change, so they
are named here once instead of being re-derived at each call site.

Consumed by `app/native.py` (M4) for flicker-free click-through
toggling, power/clock-change notifications, the optional WorkerW glue
mode, and the low-level keyboard hook that delivers Spacebar to the
unfocused dial (Session 21).

## Contents

- **Window style/message literals** — `GWL_EXSTYLE`, `WS_EX_LAYERED`,
  `WS_EX_TRANSPARENT`, `WM_TIMECHANGE`, `WM_POWERBROADCAST`,
  `WM_NCHITTEST`, `HTTRANSPARENT`, the `PBT_APM*` resume codes.
- **Topmost re-assertion** — `HWND_TOPMOST`, `SWP_NOSIZE`,
  `SWP_NOMOVE`, `SWP_NOACTIVATE` (the "top" z-mode's native
  `SetWindowPos` call, since Qt's `WindowStaysOnTopHint` degrades to
  normal stacking after a flag swap recreates the native window).
- **WorkerW glue** — `WM_SPAWN_WORKERW` (the undocumented Progman
  message, best-effort on Windows 11 24H2).
- **Single-instance** — `ERROR_ALREADY_EXISTS`.
- **The low-level keyboard hook** (Session 21) — `WH_KEYBOARD_LL`,
  `HC_ACTION`, the `WM_KEY*`/`WM_SYSKEY*` message codes, `VK_SPACE`,
  plus the two ctypes ABI definitions the hook's callback rides on:
  `KBDLLHOOKSTRUCT` (the struct the hook's `lParam` points at — only
  `vkCode` is read) and `LL_KEYBOARD_PROC` (the `WINFUNCTYPE` for
  `LowLevelKeyboardProc`'s `__stdcall` signature).

## Connections

### Used by
- [App (folder)](../../app/___app.md) — `app/native.py` reads every
  constant above for click-through, power/clock-change handling, the
  "top" z-mode's topmost re-assertion, the WorkerW glue and the
  Spacebar keyboard hook

## Design Decisions

- **Constants ride beside the ABI they serve.** The two ctypes
  definitions (`KBDLLHOOKSTRUCT`, `LL_KEYBOARD_PROC`) are not
  constants, but they describe the exact memory/callback layout the
  `WH_KEYBOARD_LL` literals above address — keeping them in the same
  file means the hook's whole contract (values + shapes) is verifiable
  in one place.
