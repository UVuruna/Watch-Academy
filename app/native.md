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
- `set_click_through(hwnd, enabled)`: toggles `WS_EX_TRANSPARENT`
  directly — `setWindowFlag()` would re-parent and hide the window
- `nchittest_falls_outside(message_ptr)`: is the WM_NCHITTEST point
  outside the window's inscribed circle? Uses the HWND from the message
  itself — calling `winId()` here would force window creation from
  inside window creation and loop forever (learned the hard way)

## Classes

### PowerEventFilter
`QAbstractNativeEventFilter` firing the callback on
`WM_POWERBROADCAST` resume events and `WM_TIMECHANGE` — the dial
refreshes immediately instead of waiting for a tick that never fired
during sleep.
