# App Controller

**Script:** [App Controller (script)](controller.py)

## Purpose
Composition root — the only object that knows everyone. Owns the settings
store, the clock widget, the tray, the shared menu, the data repositories,
the compositor and the minute scheduler. Tick flow: read the wall clock
fresh → rebuild the day context when `(local date, UTC offset)` changed
(or after a clock jump) → build the tick state → repaint.

## Connections

### Uses
- [Clock Widget](widget.md) — creates and positions the window
- [Tray Controller](tray.md) — shows the tray icon
- [Settings Store](settings_store.md) — load/recover/save
- [Minute Scheduler](scheduler.md) — tick source
- [Clock State](../core/clock_state.md) — day/tick builds
- [Seasons](../data/seasons.md), [Moon Phases](../data/moon_phases.md) — anchors and windows
- [Compositor](../render/compositor.md), [Assets](../render/assets.md) — rendering
- [Config (folder)](../config/___config.md) — defaults (DEFAULT_CITY, DEFAULT_SKIN) and paths

### Used by
- `main.py`

## Classes

### AppController

#### Methods
- `run()`: delivers the first tick BEFORE `show()` (the compositor must
  have a day context when the first paint arrives), positions the widget,
  shows widget and tray, starts the scheduler, connects `screenChanged`
  (DPI/monitor moves flush every rasterized cache). The remembered
  position is kept if ANY attached screen shows part of the dial
  (multi-monitor safe); otherwise — first run or monitors rearranged —
  the widget centers on the primary screen
- `_on_tick(clock_jumped)`: day-context rebuild on cache-key change or
  clock jump; unreadable/out-of-coverage astronomical data dies VISIBLY
  (dialog, then exit) — never a silently wrong dial
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
- `_build_menu()`: the shared tray/right-click menu — Size submenu
  (360/540/720 presets, exclusive check group), Click-through toggle
  (turn back off via the TRAY — the dial itself no longer takes clicks),
  Exit; settings dialog arrives in M6
- `_set_diameter()`: resizes the widget, invalidates the compositor
  caches and persists the choice
- `_set_click_through()`: TRUE pass-through (window takes no mouse input;
  tray-only recovery) + starts `_poll_hover()` — a cursor poller that
  keeps ALL five hover tooltips (weekday, date, moon, dawn, dusk) alive
  by asking the compositor about the cursor position a few times a second
- `_on_wake()`: resume-from-sleep / clock change → immediate full refresh
  (wired to the native PowerEventFilter)
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
