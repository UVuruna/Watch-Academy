# App Controller

**Script:** [App Controller (script)](controller.py)

## Purpose
Composition root — the only object that knows everyone. Owns the settings
store, the clock widget, the tray and the shared menu; runs the lifecycle
(startup positioning, debounced position saves, quit).

## Connections

### Uses
- [Clock Widget](widget.md) — creates and positions the window
- [Tray Controller](tray.md) — shows the tray icon
- [Settings Store](settings_store.md) — load/recover/save
- [Config (folder)](../config/___config.md) — defaults and paths

### Used by
- `main.py`

## Classes

### AppController

#### Methods
- `run()`: positions the widget and shows widget and tray. The remembered
  position is kept if ANY attached screen shows part of the dial
  (multi-monitor safe); otherwise — first run or monitors rearranged —
  the widget centers on the primary screen
- `quit()`: disarms the watchdog, saves the final position (a save failure
  shows a blocking stay-on-top dialog), hides tray, quits — the app always
  exits even when the save fails
- `_load_settings_or_recover()`: corrupt settings → visible dialog offering
  reset-with-backup or abort; unreadable file (locked/permissions) →
  visible dialog offering session defaults (file untouched) or abort —
  never a silent reset (Rule #1)
- `_on_widget_moved()` / `_flush_position()`: debounced position
  persistence; a mid-run save failure surfaces as a tray error balloon
  (once per failure streak) instead of dying silently
- `_build_menu()`: the shared tray/right-click menu (Exit; grows in M4/M6)
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
