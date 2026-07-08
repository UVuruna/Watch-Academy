# app/

The Qt application shell: window, input, tray, timing and persistence.
Knows nothing about astronomy (`core/`) or skin internals (`skins/`) — it
consumes their outputs through the render compositor.

## Files

### `widget.py` — Clock Widget
The frameless, per-pixel-transparent, always-at-bottom dial window;
painting is delegated to the compositor. See [Clock Widget](widget.md).

### `controller.py` — App Controller
Composition root: owns settings, window, tray, menu, repositories,
compositor, scheduler and the tick/quit flows.
See [App Controller](controller.md).

### `settings_store.py` — Settings Store
Atomic JSON persistence of user runtime state in `%APPDATA%/DOMY Watch/`.
See [Settings Store](settings_store.md).

### `tray.py` — Tray Controller
System tray icon with the shared context menu. See [Tray Controller](tray.md).

### `scheduler.py` — Minute Scheduler
Minute- or second-aligned self-rescheduling timer with clock-jump
detection. See [Minute Scheduler](scheduler.md).

### `native.py` — Win32 Integration
Single-instance mutex, click-through toggle, circular hit-test helper,
power/clock wake filter. See [Native](native.md).

### `time_travel.py` — Time Travel
Scenario-tester dialog: any moment + position rendered for a minute,
then auto-reset. See [Time Travel](time_travel.md).

Planned (M6): `settings_dialog.py`, `location_picker.py`. Deferred:
optional WorkerW "glue to wallpaper" mode (fragile on Win11 24H2 —
revisit on demand).

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
