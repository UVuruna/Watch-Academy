# Native

**Script:** [Native (script)](native.py)

## Purpose
The only module that talks to user32/kernel32 — what Qt cannot do:
single-instance detection, flicker-free click-through, the physical
window rect for the circular hit test, and the power/clock native events
that must refresh the dial immediately.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `winapi.py` literals

### Used by
- `main.py` — single-instance gate
- [Clock Widget](widget.md) — WM_NCHITTEST circular pass-through
- [App Controller](controller.md) — click-through toggle, wake filter

## Functions

- `acquire_single_instance(name)`: named kernel mutex; the handle
  deliberately lives as long as the process
- `set_click_through(hwnd, enabled)`: TRUE click-through via
  `WS_EX_TRANSPARENT` — the window takes no mouse input at all; hover
  info survives through the controller's cursor poller
- `nchittest_falls_outside(message_ptr)`: is the WM_NCHITTEST point
  outside the window's inscribed circle? Uses the HWND from the message
  itself — calling `winId()` here would force window creation from
  inside window creation and loop forever (learned the hard way)
- `assert_topmost(hwnd)` (owner 2026-07-17, ROADMAP 15e): forces the
  window to TRUE topmost via `SetWindowPos(HWND_TOPMOST,
  SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)`. Qt's `WindowStaysOnTopHint`
  degrades to ordinary stacking once a `setWindowFlags()` call recreates
  the native window, so the "top" z-mode re-asserts topmost natively after
  every flag swap and every show/reshow (the widget calls it). Moves,
  resizes and focus are all left untouched.

## Classes

### PowerEventFilter
`QAbstractNativeEventFilter` firing the callback on
`WM_POWERBROADCAST` resume events and `WM_TIMECHANGE` — the dial
refreshes immediately instead of waiting for a tick that never fired
during sleep.
