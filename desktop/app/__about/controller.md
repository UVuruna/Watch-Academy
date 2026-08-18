# Watch Controller

**Script:** [Watch Controller (script)](../controller.py) · **Flow:** [diagram](../__flow/controller.md)

## Purpose
Composition root for ONE watch — the only object that knows everyone
else inside it. Owns the settings store, the clock window, the tray,
the shared right-click menu, the data repositories, the compositor and
the minute scheduler.

**ADD WATCH round** (owner INSTRUCTION.txt item 2, sealed 2026-07-21): a
process can hold several `WatchController` instances, one per watch,
each fully self-contained. [Watch Manager](watch_manager.md) is the thin
process-wide owner that builds/tears down the roster; a
`WatchController` reaches it only through the constructor callbacks
(`watch_count`, `on_add_watch`, `on_remove_watch`, `on_exit`) — it still
knows nothing about its siblings.

## THE SPLIT LANDED — one class, six modules
`controller.py` was a documented god-file carrying entries in both
`tests/test_structure_law.py` and `tests/structure_ratchet.json`. It
carries neither now.

**R10 (2026-08-18)** lifted skin building — the module-level
`build_skin`/`_compose_skin`/`apply_display_settings`/`display_for`/
`watch_title` and their pure helpers — into
[Skin Builder](skin_builder.md). Those were free functions over plain
data with no `self` and no window, and 28 test files already imported
them directly.

**WA-R14 (2026-08-19)** cut the class itself, along the five seams the
[OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md) had mapped. Each is a
MIXIN, not a collaborator: every one of these methods READS and WRITES
`self._settings`, `self._skin` and the timers, so a collaborator would
need a back-channel to all three while a mixin keeps `self` and changes
no call site at all.

| Mixin | Responsibility |
|-------|----------------|
| [Controller Shortcuts](controller_shortcuts.md) | every keyboard shortcut, and the flashes they raise |
| [Controller Menu](controller_menu.md) | the right-click / tray menu and its gating |
| [Controller Display](controller_display.md) | one visual choice in, a rebuilt skin out |
| [Controller Dialogs](controller_dialogs.md) | the watch's own windows and the payload each is handed |
| [Controller Simulation](controller_simulation.md) | the moment the watch shows when it is not now |

`WatchController` inherits all five, in that order, ahead of `QObject`.
What is LEFT here — 899 logic lines — is the composition root itself:
construction and wiring, the settings load/recover/save, the tick and
wake plumbing, the hover warm, the translation overlay, the window
position and the click-through poller.

## Connections

### Uses
- [Clock Widget](widget.md) — creates and positions the window; listens
  to `shortcut_triggered`/`open_encyclopedia`/`typed`/`moved`
- [Tray Controller](tray.md) — the tray icon; `logo_icon(watch_index)`
  picks this watch's own identity
- [Settings Store](settings_store.md) — load/recover/save, from this
  watch's own `settings_path`
- [Minute Scheduler](scheduler.md) — one tick source per watch
- [Native](native.md) — `PowerEventFilter`, click-through, single-instance
- [Legend Popup](legend_popup.md), [Fast Travel Flash](fast_travel_flash.md) —
  one instance each, owned here
- [Time Travel](time_travel.md), [Report](report.md),
  [Observatory](../observatory/___observatory.md) — opens/owns the one live instance of each
- [Watch Face (subfolder)](../watch_face/___watch_face.md) —
  `WatchFaceDialog`, opened/owned the SAME way (the owner-approved Watch
  Face & Settings UI rework — Phase 6 FINAL cleanup deleted the
  Design/Pointer Theme/Slot Theme windows this window replaces)
- [Settings Dialog (subfolder)](../settings_dialog/___settings_dialog.md),
  [Encyclopedia (subfolder)](../encyclopedia/___encyclopedia.md) — opens
  them; applies their results
- [Core (folder)](../../core/___core.md) — `build_day_context`,
  `build_tick_state`, `core.deep_time.*`
- [Data (folder)](../../data/___data.md) — the PROCESS-WIDE accessors
  `shared_deep_time`, `shared_moon_phases`, `shared_seasons`,
  `shared_symbolism`, `shared_encyclopedia` (never the repository
  classes directly — see THE ONE COPY RULE below); `TranslationStore`
- [Compositor](../../render/__about/compositor.md), [Assets](../../render/__about/assets.md) — rendering
- [Skins Manifest](../../skins/__about/manifest.md) — `missing_assets`
- [Config (folder)](../../config/___config.md) — defaults, paths, shortcuts

### Used by
- [Watch Manager](watch_manager.md) — builds and tears down the roster;
  `main.py` goes through the manager, never this class directly

## Classes

### WatchController(QObject)

#### Constructor
`__init__(app, watch_index=1, settings_path=None, watch_count=lambda: 1,
on_add_watch=lambda: None, on_remove_watch=lambda watch: None,
on_exit=None)` — every ADD WATCH parameter defaults to reproducing the
pre-ADD-WATCH single-watch behavior exactly, so a bare `WatchController(app)`
still constructs and behaves as before that round.

#### Properties
- `watch_index` — this watch's own 1-based slot number, fixed for its
  whole lifetime
- `settings_path` — this watch's own settings file

#### Selected methods (what stayed in the composition root)
- `run()`: delivers the first tick BEFORE `show()` (the compositor needs
  a day context for the first paint), positions the widget, shows
  widget+tray, starts the scheduler; connects `first_painted` so [Watch
  Manager](watch_manager.md) can arm the shared warm once every watch
  has painted
- `discard()` / `_prepare_quit()` / `_teardown_windows()` / `quit()`:
  `discard()` (Remove Watch) closes and deletes the dial window itself
  (root cause of a 2026-07-29 ghost-dial bug, Rule #25 — see the
  commit-history record); `_prepare_quit()` (Exit) saves first
- `_on_tick(clock_jumped)`: rebuilds the day context on a cache-key
  change or a reported clock jump; unreadable/out-of-coverage
  astronomical data dies VISIBLY (a dialog, then exit) — never a
  silently wrong dial. **A clock jump is NOT a new day** (owner bug
  2026-08-06): both rebuild the context, but only a changed `cache_key`
  starts the hover-article sweep — an NTP correction of a few seconds
  speaks no new text, and the sweep is the most expensive work the app
  owns (7,201 probes, measured at 58.2 s)
- `_on_wake()` / `_refresh_after_jump()`: the WM_TIMECHANGE /
  resume-from-sleep path. `_on_wake` runs inside the native event filter
  and does the cheapest possible thing — it re-aims `_wake_timer`, a
  restartable single-shot. Windows BROADCASTS the message to every
  top-level window and Qt runs it through EVERY installed filter, so
  with N watches one SYNC used to fire N^2 refreshes; the coalescer
  collapses the burst into one. `_teardown_windows` uninstalls the
  filter — it is installed on the APPLICATION and outlived its watch
  (640 zombie tracebacks in the owner's crash.log, 2026-08-06)
- `_symbolism()` / `_encyclopedia_repository()`: THE ONE COPY RULE. Both
  return the PROCESS-WIDE repository for the active language, never a
  fresh one. `_install_skin` calls them, so a private instance meant a
  1.12 MB + 439 KB reparse on every settings change, on every watch. A
  landed retranslation calls `reset_shared_symbolism()` /
  `reset_shared_encyclopedia()`
- `_start_hover_warm()` / `hover_warm_signature()`: hands the sweep to
  [Watch Manager](watch_manager.md)'s queue when one is attached, so at
  most ONE sweep runs in the process; a stand-alone watch (tests) still
  uses its own thread. The SIGNATURE is what the sweep would BUILD —
  skin, day cache key, daylight state and diameter — so watches that
  would produce identical work sweep once between them. It folds the
  skin in through its `repr`, not `hash` (several specs hold dicts, so
  the object is genuinely unhashable, and hashing a hand-picked subset
  would stop noticing whichever field someone adds next). **None means
  SWEEP** — an uncomputable signature is never treated as a match
- `_apply_language()`: takes the PROCESS-WIDE translation claim
  (`data.translations.claim_translation`) before building the corpus.
  The per-watch `_translation_thread` guard let five watches on one
  language start five workers on the same corpus, all writing one cache
  file
- `apply_pending_art()` / `_apply_art_now()`: the debounced repaint a
  landed background build rides — a Qt signal (`art_ready`) queued
  cross-thread onto the GUI thread, restarting a single-shot timer
  (`ART_REPAINT_DEBOUNCE_MS`) so a burst of landings repaints ONCE, not
  once per file. `_apply_art_now` also clears the asset cache's PENDING
  working-set markers (`self._compositor._cache.clear_pending()`, owner
  bar 2026-08-09, MIGRATE-GUI Phase 1) before rebuilding composites — a
  working-set miss that stood in blank the previous frame gets one more
  chance to resolve on exactly the same signal a landed metal recolor
  already rides. Reached through the compositor's own `_cache` rather
  than a new `Compositor` method deliberately: `render/compositor.py`
  is out of this round's scope (owned by a concurrent celestial-geometry
  round)

The menu tree, the jump arithmetic and the simulation lifecycle moved
out in WA-R14 — see [Controller Menu](controller_menu.md) and
[Controller Simulation](controller_simulation.md).

## Module-level functions
`_location_flash_text` is the only one left, and it moved to
[Controller Shortcuts](controller_shortcuts.md) with the flash it
formats. Everything this section used to describe — `build_skin`,
`display_for`, `apply_display_settings`, `watch_title` and their pure
helpers, together with THE LOCATION CROWN and THE RULED LOCATION ARC —
is [Skin Builder](skin_builder.md)'s, and its prose moved there in the
same commit that noticed the doc had outlived the code (WA-R14).

## Classes (menu plumbing)
`_StayOpenMenu(QMenu)` and `_guard_exclusive_choice` moved to
[Controller Menu](controller_menu.md) with `_build_menu`.

## Design Decisions
- **A shared `MinuteScheduler` across watches was considered and
  declined** — see [Watch Manager](watch_manager.md)'s own Design
  Decisions.
- **Non-modal Encyclopedia/Guide/Observatory** (`.show()` not `.exec()`,
  ITEM 1, R4 owner batch 2026-07-20): `exec()` forces application
  modality — blocking the dial too — for as long as the dialog stays
  open; `.show()` never does. A second open request raises the one live
  instance; Settings and Time Travel stay modal (they mutate state
  transactionally and must not be left half-applied by a stray close).
- **The split is done.** This god-file predated THE STRUCTURE LAW
  (owner decree 2026-07-29). R10 took skin building out on 2026-08-18
  and WA-R14 took the five remaining responsibilities out on
  2026-08-19; the file left both ratchets in that commit. What is here
  now is the composition root and nothing else.
