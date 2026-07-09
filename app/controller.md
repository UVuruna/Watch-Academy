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
- `_build_menu()`: the shared tray/right-click menu, built from the
  `_add_choice_submenu()` helper (one exclusive check-group per
  submenu) — THEME as the first-level dropdown (owner spec, FINAL.txt
  #6) nesting Octa slot (nine modes; grayed out unless the octa
  pointer is active — `_set_display_choice` flips it on pointer
  change), Weekday (Planets / Planet signs / Greek gods / Norse gods /
  Religions / Professions), Ring (DOMY/MORPH presets), Pointer (two
  groups: Trinity/Seasons/Prism/Compass variant — the owner's display
  names for trio/cross/hexa/octa — + Paint/Light palette) and Umbra
  (two groups: Fine/Coarse/Gradient form + Full/Half/Light/Dark
  contrast); then Size (360…1440),
  Elements (the FINAL.txt #5 on/off switches, via the shared
  `_add_toggle()` helper: Earth — with its Clean/Atmosphere style
  group nested — Moon, Weekday, Pointer, Colorful — off draws the
  day/twilight arcs as plain white transparency — and Seconds, which
  also switches the tick cadence through
  `MinuteScheduler.set_per_second`), the Legend toggle (off = no
  hovers at all; with click-through the dial has zero interaction),
  the Solar rotation toggle (off = upright Star/Aura/Umbra), Time
  Travel…, Click-through toggle (turn back off via the TRAY — the
  dial itself no longer takes clicks), Exit
- `_set_ring()` / `_set_display_choice(key, value)`: rebuild via the
  module-level `build_skin(settings)` — DEFAULT_SKIN + the chosen RING
  PRESET (DOMY and MORPH are ring preset names, nothing more) — or a
  targeted `dataclasses.replace`, install through the shared
  `_install_skin()` (fresh compositor, day context kept) and persist;
  `apply_display_settings(skin, settings)` (pure, testable) overlays
  the display choices, opacity overrides and the custom palette
- `_open_settings()`: the M6 dialog — location (new observer/timezone →
  full day-context rebuild), opacity and palette results applied by
  reinstalling the PRISTINE pack (so cleared overrides really clear)
- `_set_diameter()`: resizes the widget, invalidates the compositor
  caches and persists the choice
- `_set_click_through()`: TRUE pass-through (window takes no mouse input;
  tray-only recovery) + starts `_poll_hover()` — a cursor poller that
  keeps ALL five hover tooltips (weekday, date, moon, dawn, dusk) alive
  by asking the compositor about the cursor position a few times a second
- `_on_wake()`: resume-from-sleep / clock change → immediate full refresh
  (wired to the native PowerEventFilter)
- `_open_time_travel()`: frozen (moment, observer) rendered instead of
  the present for `TIME_TRAVEL_DURATION_S`, then the tick flow snaps back
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
