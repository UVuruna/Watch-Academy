# Native

**Script:** [Native (script)](native.py)

## Purpose
The only module that talks to user32/kernel32 — what Qt cannot do:
single-instance detection, flicker-free click-through, the physical
window rect for the circular hit test, the power/clock native events
that must refresh the dial immediately, and the low-level keyboard HOOK
that delivers Spacebar to the UNFOCUSED dial (Session 21).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `winapi.py` literals

### Used by
- `main.py` — single-instance gate, AppUserModelID (called BEFORE
  `QApplication` exists — the very first thing `main()` does)
- [Clock Widget](widget.md) — WM_NCHITTEST circular pass-through
- [Watch Controller](controller.md) — click-through toggle, wake filter

## Functions

- `acquire_single_instance(name)`: named kernel mutex; the handle
  deliberately lives as long as the process
- `set_app_user_model_id(app_id)` (owner screenshot 2026-07-20):
  `shell32.SetCurrentProcessExplicitAppUserModelID` — gives the process
  its OWN taskbar identity so Windows stops grouping every window this
  interpreter opens under python.exe's identity (which could fall back
  to ITS icon for the taskbar button regardless of what
  `QApplication.setWindowIcon` set). Needs no QApplication/HWND; raises
  `OSError` on a non-S_OK HRESULT (Rule #1 — practically never fails on
  a supported Windows version, so a failure is let through loud rather
  than guarded, Rule #7).
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
  resizes and focus are all left untouched. The [Legend Popup](legend_popup.md)
  reuses it too (Session 21): the hover legend must ride ABOVE the dial
  in the "top" z-mode, where the dial is native-topmost AND focused.

## Classes

### KeyboardHook
A GLOBAL low-level keyboard hook (`SetWindowsHookEx(WH_KEYBOARD_LL)`)
that makes Spacebar open the Encyclopedia WHENEVER the hover works —
without the dial ever stealing keyboard focus from the app the user is
typing in (owner law 2026-07-18: "SPACE treba uvek kao i HOVER"). The
[Clock Widget](widget.md) owns one and installs it ONLY while the cursor
sits on an encyclopedia-capable element, uninstalling it on
hover-leave / hide / click-through toggle / quit — so SPACE is consumed
only during a deliberate hover over a page-bearing element, never at any
other time.

- **This is a HOOK.** A low-level keyboard hook is a SYSTEM-WIDE
  interception. The build pipeline's Defender-exclusion note (root
  CLAUDE.md, NSIS step) becomes relevant at M7 — see the ROADMAP M7
  section. Some AV heuristics flag `SetWindowsHookEx`; code-signing plus
  the exclusion cover it.
- The hook runs on the GUI thread and needs a running message loop —
  Qt's own suffices. Its callback MUST stay trivial (Windows silently
  evicts a slow low-level hook): on a SPACE keydown it fires `on_space`
  (which posts a QUEUED hop to the GUI event loop — the modal article is
  NEVER opened from inside the hook proc) and CONSUMES the key; every
  other key passes straight through. Because the consumed SPACE never
  reaches the focused window, the widget's own `keyPressEvent` cannot
  also fire — no double jump.
- `install()` / `uninstall()` are idempotent; a NULL install result
  raises `OSError` (an OS API failure stays visible, Rule #1). The
  ctypes trampoline is kept alive for the hook's lifetime. `installed`
  reports the current state. Auto-repeat keydowns are de-duped (fire
  once per physical press) so a held key cannot stack modals.

### PowerEventFilter
`QAbstractNativeEventFilter` firing the callback on
`WM_POWERBROADCAST` resume events and `WM_TIMECHANGE` — the dial
refreshes immediately instead of waiting for a tick that never fired
during sleep.
