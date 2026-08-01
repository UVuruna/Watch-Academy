# Native

**Script:** [Native (script)](../native.py) · **Flow:** [diagram](../__flow/native.md)

## Purpose
The only module that talks to `user32`/`kernel32`/`shell32` — everything
Qt cannot do: single-instance detection, the app's own taskbar identity,
flicker-free click-through toggling (`setWindowFlag` would re-parent and
hide the window), the physical window rect for the circular hit test,
the power/clock native events that must refresh the dial immediately,
and the low-level keyboard HOOK that delivers Spacebar to the dial even
when it is unfocused. All Win32 literals (`GWL_EXSTYLE`, `WM_NCHITTEST`,
`LL_KEYBOARD_PROC`, …) live in `config/winapi.py` — this module only
calls the APIs.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `winapi.py`'s ctypes
  structures and constants

### Used by
- `main.py` — `acquire_single_instance` / `set_app_user_model_id`,
  called BEFORE `QApplication` exists
- [Clock Widget](widget.md) — `KeyboardHook`, `nchittest_falls_outside`,
  `set_click_through`, `assert_topmost`
- [Watch Controller](controller.md) — click-through toggle, `PowerEventFilter`
- [Legend Popup](legend_popup.md), [Fast Travel Flash](fast_travel_flash.md) —
  `assert_topmost`, to ride above the natively-topmost "top" z-mode dial

## Functions

- `acquire_single_instance(name) -> bool`: named kernel mutex; the
  handle deliberately lives as long as the process (module-level
  `_instance_mutex`, never closed)
- `set_app_user_model_id(app_id)`: `SetCurrentProcessExplicitAppUserModelID`
  — gives the process its own taskbar identity so Windows stops grouping
  every window under python.exe's icon; raises `OSError` on a non-`S_OK`
  HRESULT (an OS failure here is real and must be seen, Rule #1 — it
  practically never fails on a supported Windows version, so the failure
  path is left loud rather than guarded, Rule #7)
- `autostart_enabled()` / `set_autostart(enabled)`: the HKCU Run entry
  is the store — no duplicate flag in `Settings`
- `set_click_through(hwnd, enabled)`: TRUE click-through via
  `WS_EX_LAYERED | WS_EX_TRANSPARENT` — the window takes no mouse input
  at all; hover survives through the controller's cursor poller
- `assert_topmost(hwnd)`: `SetWindowPos(HWND_TOPMOST, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)`
  — re-asserts TRUE topmost natively, since Qt's `WindowStaysOnTopHint`
  degrades to ordinary stacking once `setWindowFlags()` recreates the
  native window
- `nchittest_falls_outside(message_ptr) -> bool`: True when a
  `WM_NCHITTEST` message's point lies outside the window's inscribed
  circle — reads the HWND from the message itself (`winId()` here would
  force window creation from inside window creation and loop forever)

## Classes

### KeyboardHook
A global low-level keyboard hook (`SetWindowsHookExW(WH_KEYBOARD_LL)`)
that lets Spacebar open the Encyclopedia whenever the cursor hovers a
page-bearing dial element — without the dial ever stealing keyboard
focus from whatever app the user is typing in. [Clock Widget](widget.md)
owns one instance and installs it only while the cursor sits on an
encyclopedia-capable target.

#### Methods
- `install()` / `uninstall()`: idempotent; `install()` raises `OSError`
  on a NULL hook handle (Rule #1)
- `installed` (property): current install state
- `_callback(n_code, w_param, l_param)`: on a SPACE keydown, fires
  `on_space` once per physical press (de-duped against auto-repeat) and
  CONSUMES the key (returns `1`, no `CallNextHookEx`); every other key
  passes through untouched. The callback must stay trivial — Windows
  silently evicts a slow low-level hook — so `on_space` only ever posts
  a queued hop back to the Qt event loop, never opens the modal article
  from inside the hook proc itself.

### PowerEventFilter(QAbstractNativeEventFilter)
Fires `on_wake` on `WM_TIMECHANGE` and on `WM_POWERBROADCAST` resume
events (`PBT_APMRESUMEAUTOMATIC`/`PBT_APMRESUMESUSPEND`) — the dial
refreshes immediately instead of waiting for a scheduled tick that never
fired while the machine slept.

## Design Decisions
- A low-level hook is a system-wide interception; some AV heuristics
  flag `SetWindowsHookEx` — code-signing plus a documented Defender
  exclusion (see the monorepo build pipeline) cover it at release time.
