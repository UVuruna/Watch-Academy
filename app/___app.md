# app/

The Qt application shell: window, input, tray and persistence. Knows nothing
about astronomy (`core/`) or skin internals (`skins/`) — from M3 it consumes
their outputs through the compositor.

## Files

### `widget.py` — Clock Widget
The frameless, per-pixel-transparent, always-at-bottom dial window.
See [Clock Widget](widget.md).

### `controller.py` — App Controller
Composition root: owns settings, window, tray, menu and the quit flow.
See [App Controller](controller.md).

### `settings_store.py` — Settings Store
Atomic JSON persistence of user runtime state in `%APPDATA%/DOMY Watch/`.
See [Settings Store](settings_store.md).

### `tray.py` — Tray Controller
System tray icon with the shared context menu. See [Tray Controller](tray.md).

Planned (M4+): `scheduler.py` (minute-aligned timer), `native.py` (ctypes
click-through, power/clock-change events, optional WorkerW glue),
single-instance guard (second launch must not spawn a second widget),
`settings_dialog.py`, `location_picker.py` (M6).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — constants, defaults, paths

### Used by
- `main.py` — creates the controller and runs the Qt event loop

## Design Decisions
- All window flags are set before the first `show()` — changing them later
  re-parents and hides the window on Windows.
- Win+D on Windows 11 24H2 (verified empirically): the window receives NO
  events — the OS raises the desktop layer above everything (even TOPMOST
  cannot pierce it) and un-covers the widget when Show Desktop mode ends.
  The spontaneous-hide watchdog covers other shell actions; staying visible
  DURING Show Desktop requires the optional WorkerW glue mode (M4).
- One `QMenu` is shared by the tray icon and the widget's right-click.
