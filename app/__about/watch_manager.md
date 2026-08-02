# Watch Manager

**Script:** [Watch Manager (script)](../watch_manager.py)

## Purpose
The process-wide composition root (ADD WATCH round, owner
INSTRUCTION.txt item 2, sealed 2026-07-21). One `QApplication` holds an
independent roster of [Watch Controller](controller.md) instances — each
fully self-contained (its own settings file, dial widget, tray icon,
menu, skin, compositor, scheduler). `AppController` is the ONLY object
that knows the full roster; a `WatchController` reaches it only through
the callbacks its own constructor takes (`watch_count`, `on_add_watch`,
`on_remove_watch`, `on_exit`) — it still knows nothing about its
siblings.

## Connections

### Uses
- [Watch Controller](controller.md) — builds/tears down one instance per
  roster slot; calls its `run()` / `discard()` / `_prepare_quit()` /
  `refresh_title()`
- [Settings Store](settings_store.md) — seeds a new watch's settings
  file directly (`SettingsStore(path).save(seed)`) before constructing it
- [Warm](warm.md) — owns the one background warm thread, armed once
  every watch's first frame has painted
- [Config (folder)](../../config/___config.md) — `paths.settings_path(index)`,
  `paths.discover_watch_indices()`

### Used by
- `main.py` — builds `AppController(app)`, then `controller.run()`

## Classes

### AppController
Owns the watch roster and the app-wide window icon.

#### Roster
Watch 1 keeps the pre-multi-watch `settings.json`; watch N (2+) gets its
own `settings.<N>.json`. A removed watch's own number is never reused
while a higher-numbered watch survives (`_next_index`), so a watch's
tray color (derived from its index) never drifts onto a different watch
later in the session.

#### Methods
- `__init__(app)`: `paths.discover_watch_indices()` rebuilds the roster
  from whatever settings files exist on disk; one `_refresh_all_titles()`
  pass at the end lands every title/tooltip correctly regardless of
  build order (each watch's own `_build_menu()` runs during its own
  construction, before its siblings have joined the roster, so
  `watch_count()` under-reports mid-loop)
- `_build_watch(index)`: constructs one `WatchController` wired to this
  manager's `remove_watch`/`quit_all`; `on_add_watch` is assigned right
  after construction returns (it needs the watch itself as its seed)
- `_next_index()`: one past the highest `watch_index` any live watch
  currently holds
- `add_watch(seed_watch)`: a new watch seeded from `seed_watch`'s
  CURRENT settings, with `window_x`/`window_y` cleared so the new dial
  re-centers on the primary screen instead of landing on top of its seed
- `remove_watch(watch)`: watch-index-1 guarded (the anchor is
  un-removable); calls `watch.discard()` (closes the dial window AND the
  tray, never saves), deletes its settings file, drops it from the
  roster and from the warm `_armed` set
- `run()`: `run()` on every watch, then arms the shared warm for the
  whole startup roster
- `_arm_warm(watches)` / `_watch_painted(watch, pending)` / `_run_warm(watches)`:
  waits for every watch's `first_painted` signal before starting the ONE
  background warm thread (see [Warm](warm.md)) — called for the startup
  roster and again, for a single watch only, after a mid-session
  `add_watch`
- `kick_art_warm()` / `_drain_art()` / `_emit_art_ready()`: the ON-DEMAND
  art drain (owner bug 2026-08-02 — a finish/shade/theme switch after
  the startup warm finished recorded recipes nobody ever built, and the
  dial stayed gold until restart). Installed as [Asset
  Recolor](../../render/__about/asset_recolor.md)'s stale notifier: a
  paint that observes a missing finish rings it, one lock + one rerun
  flag keep at most ONE drain thread alive, and every live watch
  repaints per built finish. Stands down until the startup warm has
  started — that first drain belongs to `run_warm`, after the first
  frames
- `quit_all()`: the Exit action on ANY watch closes the WHOLE process —
  every watch's own `_prepare_quit()` runs before the one shared
  `app.quit()`

## Design Decisions
- **A shared `MinuteScheduler` across watches was considered and
  declined** (constructive disagreement, Rule #8): each scheduler is one
  lightweight self-rescheduling `QTimer` — a handful of them costs
  nothing measurable on Windows, while a shared one would force every
  watch to repaint at the fastest cadence any sibling needs.
- **`art_source`/`subdial_set` stay per-process globals** — a documented
  limit, not solved by this round. With several watches, whichever watch
  last touched Settings/Design wins those two globals for every other
  watch's next repaint too; making them genuinely per-watch would mean
  threading a parameter through every asset-cache call site in `render/`.
- **The app-wide window icon** (`app.tray.window_icon()`) is set inside
  every `WatchController.__init__` rather than hoisted here — redundant
  past the first watch, but harmless (idempotent, one process-wide
  identity), and every dialog across every watch shares one taskbar
  identity anyway.
