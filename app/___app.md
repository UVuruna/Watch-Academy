# app/

The Qt application shell: window, input, tray, timing and persistence.
Knows nothing about astronomy (`core/`) or skin internals (`skins/`) — it
consumes their outputs through the render compositor.

## Files

### `widget.py` — Clock Widget
The frameless, per-pixel-transparent, always-at-bottom dial window;
painting is delegated to the compositor. See [Clock Widget](widget.md).

### `watch_manager.py` — Watch Manager
ADD WATCH round (owner INSTRUCTION.txt item 2, sealed 2026-07-21): the
process-wide composition root — builds and tears down the roster of
`WatchController` instances, one per watch, from whatever settings files
already exist on disk. See [Watch Manager](watch_manager.md).

### `controller.py` — Watch Controller
Composition root for ONE watch: owns its own settings, window, tray,
menu, repositories, compositor, scheduler and the tick/quit flows —
several can coexist in one process under [Watch Manager](watch_manager.md).
See [Watch Controller](controller.md).

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
then auto-reset (prefilled with the configured location). Since
Session 16 (owner 2026-07-17) the moment editor spans the whole Deep
Time coverage INCLUDING BCE (spinbox + era combo over the 400-year
proxy frame), with the dual-calendar header and the in-app precision
tier lines. R5 MENU REWORK (item 3A): grows DOWN with its own Quick
Jump rows, absorbing the old right-click menu's deep Quick Jump
submenu chain whole. See [Time Travel](time_travel.md).

### `weekday_theme_grid.py` — Weekday Theme Grid
A reusable image+name gallery of the weekday body themes (Planets
flat, then the kinship groups), shared by Pointer Theme and Slot
Theme. See [Weekday Theme Grid](weekday_theme_grid.md).

### `pointer_theme.py` — Pointer Theme
R5 MENU REWORK mini window: picks the 1st Slot's own weekday-body
theme — the old deeply-nested Weekday submenu, now an image+name
gallery. See [Pointer Theme](pointer_theme.md).

### `slot_theme.py` — Slot Theme
R5 MENU REWORK mini window: three medal icons pick which of the
1st/2nd/3rd Slots is being edited; tabs hold that slot's full option
set (Weekday / Complications / Astrology / Ascendant / Chinese
Zodiac). See [Slot Theme](slot_theme.md).

### `design_window.py` — Design Window
R5 MENU REWORK mini window: the old Design submenu's whole chain
(Pointer, Ring, Umbra, Complications, Hands, Earth, Size) as one
tabbed window, images where real preview art exists. See
[Design Window](design_window.md).

### `settings_dialog.py` — Settings Dialog
The M6 window: cascading location picker over the bundled city
database with lat/lng fine-tune, Star/Aura opacity sliders and the
palette chip editor. See [Settings Dialog](settings_dialog.md).

### `legend_popup.py` — Legend Popup
The scrollable hover window replacing QToolTip: capped to screen
fractions, taller articles scroll, stays open while the cursor is over
it. See [Legend Popup](legend_popup.md).

### `encyclopedia.py` — Encyclopedia Dialog
The article browser: a grouped topic gallery, then a SLIDER paging one
entry at a time with Home / Download and the look arrows.
See [Encyclopedia Dialog](encyclopedia.md).

### `guide.py` — Guide Dialog
The paged, resizable help book over `assets/guide/` pages and
captions. See [Guide Dialog](guide.md).

### `ui_style.py` — UI Style
Shared modern gradient-pill button styling for the reader dialogs —
roles, sizes and colors all from defaults. See [UI Style](ui_style.md).

### `theme.py` — Theme
The Rule #16 POLISH round's dark QSS theme for dialog chrome — surfaces,
group-box cards, sliders/combos/spinboxes/checkboxes/tables, applied to
the Settings dialog and the reader dialogs. See [Theme](theme.md).

### `report.py` — Report
The hidden efficiency report (owner 2026-07-15): the session unlock
reveals 📊 Report above Exit — sortable function statistics, a
top-total bar chart and a recent-durations sparkline.
See [Report](report.md).

### `observatory.py` — Observatory
The statistics sibling of the Encyclopedia (owner 2026-07-16; menu 🔭
Observatory… beside 🏛️ Encyclopedia…): dark, QPainter-drawn interactive
charts over the long ephemeris data — the season-duration oscillations
(per-series checkboxes), the light−dark envelope with the eras marked,
the eclipse timeline and the location's day-length curve; reads only the
committed series bundles (never needs deep_time.sqlite). See
[Observatory](observatory.md).

Deferred: optional WorkerW "glue to wallpaper" mode (fragile on Win11
24H2 — revisit on demand).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — constants, defaults, paths

### Used by
- `main.py` — creates the [Watch Manager](watch_manager.md) and runs the
  Qt event loop

## Design Decisions
- **Crash forensics (owner 15h item 3C, Session 21):** `main.py`
  installs permanent crash logging at startup — `faulthandler` (native
  fatal-error dumps) plus a `sys.excepthook` (unhandled Python
  tracebacks) BOTH appending to **`%APPDATA%/DOMY Watch/crash.log`**
  under a timestamped session header. It only ADDS a trace; the original
  excepthook still runs (nothing swallowed). After a crash the owner
  sends that file. The occasional-SPACE crash is also hardened directly:
  the Encyclopedia open is re-entrancy-guarded (no stacked modals) and
  the SPACE hook de-dupes auto-repeat.
- All window flags are set before the first `show()` — changing them later
  re-parents and hides the window on Windows.
- Win+D on Windows 11 24H2 (verified empirically): the window receives NO
  events — the OS raises the desktop layer above everything (even TOPMOST
  cannot pierce it) and un-covers the widget when Show Desktop mode ends.
  The spontaneous-hide watchdog covers other shell actions; staying visible
  DURING Show Desktop requires the optional WorkerW glue mode (M4).
- One `QMenu` is shared by the tray icon and the widget's right-click.
