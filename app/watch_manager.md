# Watch Manager

**Script:** [Watch Manager (script)](watch_manager.py)

## Purpose
The ADD WATCH round's process-wide composition root (owner
INSTRUCTION.txt item 2, sealed 2026-07-21). ONE `QApplication` holds an
independent roster of [Watch Controller](controller.md) instances — each
fully self-contained (its own settings file, dial widget, tray icon,
menu, skin, compositor, scheduler, dialogs). `AppController` is the ONLY
object that knows the FULL roster; a `WatchController` reaches it only
through the constructor callbacks it is handed (`watch_count`,
`on_add_watch`, `on_remove_watch`, `on_exit`) — it still knows nothing
about its siblings. `main.py` now builds one of these instead of a bare
`WatchController`; everything else (`run()`/single-instance mutex) reads
the same as before.

## Connections

### Uses
- [Watch Controller](controller.md) — builds/tears down one per roster
  slot; reads its `watch_index`/`settings_path`/`_settings` and calls its
  `run()`/`discard()`/`_prepare_quit()`/`refresh_title()`
- [Settings Store](settings_store.md) — seeds a new watch's settings file
  directly (`SettingsStore(path).save(seed)`) before constructing it, so
  the ordinary `_load_settings_or_recover()` load path picks it up with
  no separate seeding parameter needed on `WatchController` itself
- [Config (folder)](../config/___config.md) — `paths.settings_path(index)`
  (the per-watch file scheme) and `paths.discover_watch_indices()` (the
  startup roster scan)

### Used by
- `main.py` — `AppController(app)` then `controller.run()`, same shape as
  the pre-ADD-WATCH `WatchController(app)` call it replaced

## Classes

### AppController

#### Roster (per-watch settings files — see [Settings Store](settings_store.md))
Watch 1 keeps the pre-multi-watch `settings.json` (existing installs keep
working untouched); watch N (2+) gets its own `settings.<N>.json`. A
REMOVED watch's own number is never reused while a higher-numbered watch
survives (`_next_index()`), so a watch's tray color (derived straight
from its index, [Tray Controller](tray.md)) never jumps onto a DIFFERENT
watch later in the session — simpler and more predictable than
compacting the roster after every removal.

#### Methods
- `__init__(app)`: `paths.discover_watch_indices()` rebuilds the roster
  from whatever settings files already exist on disk (a fresh install
  yields `[1]`, seeding just the anchor) — every watch's OWN
  `_build_menu()` runs DURING its own construction, before its siblings
  have joined `self._watches`, so `watch_count()` under-reports mid-loop;
  one `_refresh_all_titles()` pass at the very end lands every title/
  tooltip correctly regardless of build order
- `_build_watch(index)`: constructs one `WatchController` wired to this
  manager's `remove_watch`/`quit_all`; `on_add_watch` needs the WATCH
  ITSELF as its seed, not available until construction returns, so it is
  assigned right after (`watch._on_add_watch = lambda: self.add_watch(
  watch)`) — `WatchController._build_menu` reads `self._on_add_watch`
  fresh on every click (a lambda, never a value captured at connect
  time), so this late assignment is never a stale target
- `_next_index()`: one past the highest `watch_index` any LIVE watch
  currently holds (see Roster above)
- `_refresh_all_titles()`: `refresh_title()` on every watch — called
  after `__init__`'s discovery loop, `add_watch()` and `remove_watch()`,
  the three moments the roster SIZE can change
- `add_watch(seed_watch)` (owner INSTRUCTION.txt item 2): a new watch
  seeded from `seed_watch`'s CURRENT settings — the user diverges from
  there through the usual controls. `window_x`/`window_y` are cleared
  before saving the seed, so the new dial re-centers on the primary
  screen (`WatchController._position_widget`'s existing first-run
  behavior, reused for free) instead of landing exactly on top of its
  seed, invisible until dragged apart. Calls the new watch's `run()` —
  it must actually show/tray/tick, the same as every OTHER watch got at
  startup, just later
- `remove_watch(watch)`: the Remove/Close entry's callback (watches 2+
  only — `WatchController` itself never BUILDS the entry on watch 1; the
  `watch_index == 1` guard here is the belt to that suspender against a
  stale double-click race). `watch.discard()` tears it down WITHOUT
  saving, then its settings file is deleted and it drops out of the
  roster — no further confirmation here, `WatchController.
  _confirm_remove_watch` already asked
- `run()`: `run()` on every watch in the roster — unchanged per-watch
  behavior, just looped
- `quit_all()`: the Exit menu action on ANY watch closes the WHOLE
  process (architecture decision: Exit is process-wide; the per-watch
  Remove entry is the surgical one-watch-only teardown) — every watch's
  own `_prepare_quit()` runs before the ONE shared `app.quit()`

## Design Decisions

- **A shared `MinuteScheduler` across watches was considered and
  DECLINED (constructive disagreement, Rule #8).** ARCHITECTURE
  GUIDANCE for this round suggested reusing one tick source across
  watches instead of N timers, "if the current design allows it
  cheaply." Each `MinuteScheduler` is one lightweight self-rescheduling
  `QTimer`; N of them (a handful of watches in realistic use) cost
  nothing measurable on Windows. A SHARED scheduler would instead force
  EVERY watch to repaint at the fastest cadence any SIBLING's seconds
  hand/small-seconds slot needs (wasted redraws for a watch that wants
  minute-only ticks), or need its own per-watch cadence bookkeeping
  bolted onto the shared timer for no measured gain (Priorities: an
  optimization with no measurable gain is a net loss). Kept per-watch;
  flagged for the owner to confirm or override.
- **`art_source`/`subdial_set` stay PER-PROCESS globals — a documented
  limit, not solved this round.** `config.paths` holds both as module
  globals (`render.assets.subdial_plate_file`'s only reader for the
  second one), set by `app.controller.apply_display_settings` on every
  skin install. With several watches this means whichever watch last
  touched Settings/Design wins the ART SOURCE and SUBDIAL SET for every
  OTHER watch's next repaint too. Making these genuinely per-watch would
  mean threading a parameter through every asset-cache call site that
  reaches `art_file`/`subdial_plate_file` — dozens of call sites across
  render/ — a much larger change than this round's scope.
- **The app-wide window icon (`app.tray.window_icon()`,
  `QApplication.setWindowIcon`) stays untouched inside
  `WatchController.__init__`,** called once per watch construction
  (redundant past the first, harmless — it is idempotent and process-
  wide) rather than hoisted into the manager. Every dialog across every
  watch shares ONE taskbar identity anyway (one process, one
  AppUserModelID), so a per-watch window icon would be inconsistent
  with the OS-level grouping, not an improvement.
