# Watch Controller

**Script:** [Watch Controller (script)](controller.py)

## Purpose
Composition root for ONE WATCH — the only object that knows everyone ELSE
inside it. Owns the settings store, the clock widget, the tray, the shared
menu, the data repositories, the compositor and the minute scheduler. Tick
flow: read the wall clock fresh → rebuild the day context when `(local
date, UTC offset)` changed (or after a clock jump) → build the tick state
→ repaint.

**ADD WATCH round (owner INSTRUCTION.txt item 2, sealed 2026-07-21):** a
process can hold SEVERAL `WatchController` instances, one per watch, each
fully self-contained (its own settings file, widget, tray icon, menu,
skin, compositor, scheduler, dialogs). [Watch Manager](watch_manager.md)
(`app/watch_manager.py`) is the thin process-wide owner that builds and
tears down the roster; a `WatchController` reaches it only through the
constructor callbacks below — it still knows nothing about its siblings.
See [Watch Manager](watch_manager.md) for the roster-level mechanics
(seeding, settings-file numbering, title refresh) and this doc's own
"ADD WATCH additions" section below for what changed INSIDE one watch.

## Connections

### Uses
- [Clock Widget](widget.md) — creates and positions the window; fires
  `shortcut_triggered` (R5 MENU REWORK) for `_on_shortcut`
- [Tray Controller](tray.md) — shows the tray icon; `set_tooltip` carries
  the full `watch_title`; `logo_icon(watch_index)` picks this watch's own
  golden/rose-gold/wheel-tinted identity (ADD WATCH round)
- [Settings Store](settings_store.md) — load/recover/save, from THIS
  watch's own `settings_path` (`config.paths.settings_path(watch_index)`
  by default)
- [Minute Scheduler](scheduler.md) — tick source, one per watch (kept
  per-watch rather than shared — see [Watch Manager](watch_manager.md)'s
  `quit_all` docstring for the reasoning)
- [Clock State](../core/clock_state.md) — day/tick builds
- [Seasons](../data/seasons.md), [Moon Phases](../data/moon_phases.md) — anchors and windows
- [Compositor](../render/compositor.md), [Assets](../render/assets.md) — rendering
- [Design Window](design_window.md), [Pointer Theme](pointer_theme.md),
  [Slot Theme](slot_theme.md) — the three R5 mini windows
- [Fast Travel Flash](fast_travel_flash.md) — one instance per watch
  (R5b round); `_flash_fast_travel()` shows it on every Ctrl+[/Ctrl+]
- [Time Travel](time_travel.md) — now hosts its own Quick Jump rows
  (item 3A), fed by `_dialog_jump`/`_compute_jump`
- [Config (folder)](../config/___config.md) — defaults (DEFAULT_CITY, DEFAULT_SKIN,
  SHORTCUTS) and paths

### Used by
- [Watch Manager](watch_manager.md) (`app/watch_manager.py`) — builds and
  tears down the roster; `main.py` itself now goes through the manager,
  never this class directly

## Classes

### WatchController

#### Constructor (ADD WATCH round)
`__init__(app, watch_index=1, settings_path=None, watch_count=lambda: 1,
on_add_watch=lambda: None, on_remove_watch=lambda watch: None,
on_exit=None)` — every new parameter DEFAULTS to reproducing the
pre-ADD-WATCH single-watch behavior exactly (watch 1, its own
`settings.json`, a title that never goes full, Add Watch a no-op, Exit
quits just this instance), so a bare `WatchController(app)` still
constructs and behaves precisely as before the round — every test in
this suite predating it needed no changes beyond the class rename.
[Watch Manager](watch_manager.md) supplies real callbacks for all six.

#### Properties (ADD WATCH round)
- `watch_index`: this watch's own 1-based slot number — fixed for its
  whole lifetime, drives its tray color/settings-file name and whether
  it is the un-removable anchor (1)
- `settings_path`: this watch's own settings file (`self._store.path`)
  — the manager deletes it on Remove Watch

#### Methods
- `run()`: delivers the first tick BEFORE `show()` (the compositor must
  have a day context when the first paint arrives), positions the widget,
  shows widget and tray, starts the scheduler, connects `screenChanged`
  (DPI/monitor moves flush every rasterized cache). The remembered
  position is kept if ANY attached screen shows part of the dial
  (multi-monitor safe); otherwise — first run or monitors rearranged —
  the widget centers on the primary screen. One background thread
  (`_warm_caches`) then chains the working-set warmup and the HOVER
  ARTICLE sweep (owner 2026-07-18, asked twice: the user never hovers
  in the first seconds — pre-build every article the dial can speak
  today, so the FIRST hover is instant)
- `_start_hover_warm()` / `_warm_hover_articles()`: re-run the sweep
  (`compositor.warm_hover_articles`) on skin install and day change —
  the generation counter (`_hover_warm_generation`) obsoletes a sweep
  whose skin/day was replaced mid-run; a warm re-run costs header
  reads only

**ITEM 2 audit (R4 owner instruction batch 2026-07-20 — "sporedne niti
... nikako ne smije da blokira glavnu nit... preko threadinga nećeš
moći da dobiješ pravi paralelizam"):** measured offscreen
(`AppController` built exactly like `main.py`, minus the mutex and
`run()`'s tray/scheduler/thread side effects — see
`tests/test_controller_dialogs.py`'s fixture for the same safe
pattern) rather than guessed:
  - `AppController(app)` construction (settings load, `build_skin`,
    `Compositor`, the whole right-click/tray menu): ~235 ms, entirely
    before `show()` — unavoidably on the GUI thread (Qt widgets/menus
    can only be built there), but the window is not on screen yet at
    this point, so nothing the user can see is stalled.
  - First real paint after `show()`: ~235 ms on a machine whose
    raster cache already has SOME entries (this dev box, from the test
    suite's own runs) — genuinely cold (`raster_cache` deleted first),
    a single hover-sized probe ranged 0.6–100 ms depending on how many
    images that ONE probe's article still needed to decode; the SAME
    probe replayed immediately after (now cached) cost 2–3 ms total —
    an 85× speedup, confirming the disk-cache-then-OS-file-cache
    design (`render/assets.md`) already does its job once warm.
  - The GUI thread's OWN steady-state cost is trivial: 300
    `tooltip_at()` + `widget.update()` calls back-to-back cost 117 ms
    alone (0.39 ms/call) — nowhere near anything a human would call
    "lag".
  - **The owner's GIL doubt, answered empirically:** running the two
    heaviest documented background operations (`_metal_swapped`'s
    numpy hue-swap, `scaled_variant_file`'s PNG decode/scale/save) in
    an UNTHROTTLED loop on a second thread while the SAME 300-probe
    GUI-thread test ran concurrently cost 150 ms instead of 117 ms — a
    1.28× slowdown, not the "still only 1 CPU active" full
    serialization the owner expected. This is the concrete answer:
    Qt's own image codecs and numpy's C-level array ops both RELEASE
    the GIL for the duration of their C code (the same way file I/O
    does), so the interpreter is free to run the GUI thread's Python
    bytecode (event dispatch, `tooltip_at`, `paintEvent`) during that
    window — genuine, if imperfect, parallelism, exactly as
    `render/assets.py`'s existing "QImage in, QImage out... QPixmap
    must never be touched off the GUI thread" comments already assume.
  - A genuinely COLD full warm-up (`warm_working_set()` +
    `warm_hover_articles()` with `raster_cache` empty) measured ~84 s
    + ~6.5 s ≈ 90 s of real background CPU work (417 downscaled
    copies, 6,661 spoken hover probes) — slower than the `_warm_
    hover_articles` docstring's "the user never hovers in the first
    SECONDS" assumption on a truly fresh install, but this is
    BACKGROUND-thread time, already off the GUI thread by design, and
    the 1.28× figure above shows it does not meaningfully starve
    interaction while it runs. **Conclusion: no code change made for
    ITEM 2** — the GUI thread was already clean (Rule #8: report
    honestly instead of adding machinery the measurements don't
    justify); a process pool would trade this modest, already-
    overlapping cost for IPC/pickling overhead with no measured upside.
- `_on_tick(clock_jumped)`: day-context rebuild on cache-key change or
  clock jump; unreadable/out-of-coverage astronomical data dies VISIBLY
  (dialog, then exit) — never a silently wrong dial
- `quit()`: `_prepare_quit()` then `app.quit()` — standalone Exit (no
  manager attached; every test predating ADD WATCH, and the default
  `on_exit` a bare `WatchController` falls back to)
- `_prepare_quit()` (ADD WATCH round, split out of the old `quit()`):
  disarms the watchdog, saves the final position (a save failure shows a
  blocking stay-on-top dialog), flushes profiling — everything Exit needs
  from THIS watch except the final shared `app.quit()`, so
  [Watch Manager](watch_manager.md)`.quit_all()` can run it for every
  watch before quitting the process exactly once
- `_teardown_windows()` (ADD WATCH round): closes every open dialog, stops
  the scheduler and the debounced save timer, hides the tray — the shared
  first half of `_prepare_quit()` (Exit: also saves) and `discard()`
  (Remove Watch: never saves, the file is about to be deleted)
- `discard()` (ADD WATCH round): Remove Watch's own teardown —
  `_teardown_windows()` without a save, called by the manager right
  before it deletes this watch's settings file
- `refresh_title()` (ADD WATCH round): public hook for the manager —
  re-renders the TITLE row and tray tooltip after the roster changes
  (`watch_count()` just moved for every SURVIVING watch, not only the one
  that was added/removed)
- `_load_settings_or_recover()`: corrupt settings → visible dialog offering
  reset-with-backup or abort; unreadable file (locked/permissions) →
  visible dialog offering session defaults (file untouched) or abort —
  never a silent reset (Rule #1)
- `_on_widget_moved()` / `_flush_position()`: debounced position
  persistence; a mid-run save failure surfaces as a tray error balloon
  (once per failure streak) instead of dying silently
- `_build_menu()`: the shared tray/right-click menu, every level a
  `_StayOpenMenu` — CHECKABLE picks keep the menu open for several
  settings in one visit; plain actions close as usual (a rebuild while
  open closes and RETAINS the old menu so Qt never deletes a visible
  popup). **R5 MENU REWORK (owner spec 2026-07-20,
  `UV/DESIGN/RIGHT CLICK MENU.txt` — the exact "4-5 branching levels
  stack one over another in a screen corner" complaint,
  `UV/DESIGN/Meni One over Another.png`):** the menu is FLAT now.
  Top-to-bottom: the TITLE row (a `QWidgetAction`-hosted `QLabel`,
  `watch_title(settings, full=self._watch_count() >= 2)` — a single
  watch shows just its location; 2+ watches (ADD WATCH round) switch it
  to the FULL multi-attribute form too, matching the tray hover tooltip,
  which stays full always; both refresh via `_refresh_watch_title` /
  the public `refresh_title()`, called from `_install_skin` and by the
  manager after the roster changes); ➕ Add Watch (ADD WATCH round, owner
  INSTRUCTION.txt item 2 — "na vrhu... ispod TITLE info", on EVERY
  watch, `self._on_add_watch()` — a no-op default for standalone/test
  use, reassigned by [Watch Manager](watch_manager.md) right after
  construction) and, on watches 2+ only, ➖ Remove this Watch
  (`_confirm_remove_watch()` — one Yes/No box, then the manager's
  `remove_watch(self)`; watch 1 is the anchor and never builds this
  action at all — no gating needed, the entry simply does not exist for
  it); 👁️ Show
  (owner 2026-07-18, ROADMAP 15h, Session 21-C — visible only in
  `z_mode == "normal"`, TRAY-ONLY per Session 21-D, see below); 🎨
  Design…, ✨ Pointer Theme…, 🥇 Slot Theme… — ONE flat entry each,
  opening its own mini WINDOW instead of the old deep submenu chains
  (Rule #6, no both-paths) — see [Design Window](design_window.md),
  [Pointer Theme](pointer_theme.md), [Slot Theme](slot_theme.md) for
  what each absorbed and why each is non-modal + LIVE-APPLY; 🧩
  Visible (renamed from Elements, item 3E — STAYS a dropdown: Pointer,
  Colorful, Earth, Moon, Seconds, `_set_visible`/`_toggle_all_visible`/
  `_refresh_visible_check`, unchanged in shape from the old Elements
  mechanic beyond the rename); 📜 Legend, 🔆 Solar rotation, 🎭
  Archetype, 🖱️ Click-through; ⚙️ Settings…, 🏛️ Encyclopedia…, 🔭
  Observatory…, 📖 Guide…, 🕰️ Time Travel… (now GROWN DOWN with its
  own Quick Jump rows — see below); 📊 Report (hidden), 🚪 Exit — wired
  to `self._on_exit` (ADD WATCH round: defaults to this watch's own
  `quit()` standalone; the manager passes its OWN `quit_all()` instead,
  so Exit on ANY watch closes the WHOLE process — Remove Watch above is
  the one-watch-only teardown, Exit is deliberately process-wide). The
  QUICK JUMP submenu (the OTHER half of the "4-5 levels" complaint) is
  GONE — absorbed into the Time Travel dialog itself (item 3A).
  **R5 doubt 4 FOLLOW-UP (R5b round):** the six flat entries with a
  DIRECT 1:1 keyboard shortcut (Encyclopedia, Guide, Settings,
  Observatory, Time Travel, Archetype) carry the combo appended via
  `_labeled(text, action_id)` — a tab character plus
  `defaults.shortcut_display(action_id)`, Qt's own convention for a
  right-aligned accelerator hint in a `QMenu` row, deliberately WITHOUT
  a real `QAction.setShortcut` (every shortcut already dispatches
  through `ClockWidget.keyPressEvent` → `shortcut_triggered`; a second
  Qt-level shortcut on the same key would double-fire). The
  cycling/Fast-Travel/Location shortcuts have no single corresponding
  flat entry (they live inside a mini window, or have no menu surface
  at all) and are left unlabeled.
  **TRAY-ONLY Show (owner correction, Session 21-D — "ako smo kliknuli
  znači da ga vidim"):** the SAME shared `QMenu` pops from TWO call
  sites — the tray's native popup
  (`TrayController`/`QSystemTrayIcon.setContextMenu`) and the dial's
  own right-click ([Clock Widget](widget.md)'s `contextMenuEvent`) —
  but Show is meaningless on the second: you already see the dial,
  that is how you right-clicked it. `ClockWidget` owns the visibility
  split (constructor param `_show_action`, kept current via
  `set_show_action()` on every menu rebuild), and `contextMenuEvent`
  hides the action right before its OWN `exec()` and restores it
  after; the tray's popup never runs this code, so it always sees the
  `_refresh_menu_gating`-controlled state undisturbed.
- `watch_title(settings, full=False)` (module-level, R5 MENU REWORK
  item 2A): the watch's own display NAME — `full=False` is just
  `settings.city_name`; `full=True` is
  f"{location}-{ring_finish} {ring}-{palette label} {pointer}", e.g.
  "Belgrade-Gold DOMY-Family Trinity" — UNTRANSLATED on purpose (a
  NAME, not chrome, the same treatment `POINTER_DISPLAY_NAMES` and a
  ring preset's own name already get). The CALLER decides `full`: the
  tray hover tooltip always passes `True`; the menu TITLE row passes
  `self._watch_count() >= 2` (ADD WATCH round — a single watch keeps
  the short form, 2+ switch it to full too, owner: "Title ne treba pun
  naziv ako nema potrebe"). Kept as ONE function so that round only had
  to loop it, never reinvent it.
- `_on_shortcut(action_id)` (R5 MENU REWORK item 2, `defaults.
  SHORTCUTS`; extended R5b FINAL MAP round, owner spec sealed
  2026-07-21): dispatches one keyboard shortcut, fired by the focused
  [Clock Widget](widget.md)'s `keyPressEvent` →
  `shortcut_triggered` signal (every combo needs the dial to hold
  keyboard focus — no new global hook this round beyond the existing
  SPACE hook). `_cycle_ring`/`_cycle_weekday_theme` (Ctrl+R/Ctrl+W)
  walk `sorted(ring_presets(...))`/`_WEEKDAY_THEME_ORDER` and delegate
  to `_set_ring`/`_set_weekday_theme`, which already refresh any open
  mini window through `_install_skin`. `_cycle_weekday_theme` gained a
  STRICT no-op guard this round (`_weekday_theme_on_diamonds()`): the
  Pointer visible, the pointer variant actually HAS diamonds
  (`constants.POINTER_ARM_HALF_ANGLE_DEG` excludes Aurora/Calendar),
  the 1st Slot visible, and its effective mode is "weekday" — under
  that last condition `_classic_slot_theme` is PROVABLY always reading
  `weekday_theme` (its own Seasons/Compass redirect only fires when the
  effective mode is NOT "weekday"), so the guard is exactly "would this
  cycle be visible". `_cycle_slots` (Ctrl+N) walks the 1 → 2 → 3 chain
  directly, 0→1→2→3→0 — the SAME chain the Slot Theme window's medals
  respect, and the bootstrap out of "no slot visible" (Slot Theme's own
  gray condition). `_toggle_archetype_shortcut` (Ctrl+A) mirrors the
  menu's own Archetype toggle (including its checked-state QAction,
  bypassed by the shortcut path) — a no-op where the mode is
  unavailable. The five dialog-opener actions (now Ctrl+E/G/M/O/T — the
  R5b map moved Settings off Ctrl+, Rule #6, no leftover binding) and
  `return_to_now` (Ctrl+Home, now the FULL reset — now AND the home
  location, since `self._observer`/the home coordinates were never
  mutated by a simulation to begin with) call the existing
  `_open_*`/`_end_simulation` methods directly. A z-mode shortcut was
  considered and DROPPED (Ctrl+Z's pre-existing "Undo" expectation,
  which this app has nothing to honor).
  **R5b's three new families** (also dispatched here):
  - **SLOTS** (Ctrl+1/2/3 Complication, Ctrl+Alt+1/2/3 Weekday theme,
    per slot): `_slot_active(index)` is the shared strict no-op guard
    (the "slots enable IN ORDER" rule — slot 3 also needs slot 2 on).
    `_cycle_slot_complication` walks `_SLOT_COMPLICATION_ORDER`
    (`tuple(constants.SLOT_COMPLICATION_TITLES)`) via the SAME
    `_next_rotation_theme` helper the weekday-theme rotation timer
    already uses (Rule #5) — a slot currently on a NON-complication
    (Weekday/Zodiac/...) starts the cycle from the top.
    `_cycle_slot_weekday_theme` walks `_WEEKDAY_THEME_ORDER` the same
    way, but its OWN setter (`_slot_theme_state`) ALSO switches that
    slot's mode to "weekday" as a side effect — the direct one-press
    route into weekday-display mode, since slots 2/3 have no dedicated
    toggle for it beyond picking a theme.
  - **FAST TRAVEL** (Ctrl+[ theme, Ctrl+] option, Ctrl+minus/plus
    step): `_fast_travel_theme_index`/`_fast_travel_option_indices`
    (session-only state, like the hidden-mode unlock) walk
    `defaults.FAST_TRAVEL_THEMES` — EACH theme remembers its own
    option cursor across Ctrl+[ switches. `_step_fast_travel` builds a
    `_compute_jump` kind as `f"{'next'/'prev'}_{option['jump_stem']}"`
    from `_active_simulation_or_now()` (the chaining law: "each jump
    starts from the active simulation") through the shared
    `_apply_jump` tail (`_compute_jump` then, on a landing,
    `_start_simulation`). `_flash_fast_travel` fires ONLY from the
    theme/option pickers (owner spec scopes the flash to Ctrl+[/Ctrl+]
    — a step carries no flash) — see [Fast Travel Flash](fast_travel_flash.md).
  - **LOCATIONS** (Ctrl+Up/Down poles, Ctrl+Space Greenwich,
    Ctrl+Left/Right custom cities): `_jump_to_place(kind)` and
    `_cycle_jump_city(direction)` both chain from
    `_active_simulation_or_now()` through the SAME `_apply_jump` tail —
    the poles/Greenwich kinds never clamp; the city cycle is a strict
    no-op with `settings.jump_cities` empty, otherwise it walks its own
    session-only `_jump_city_index` cursor (wrapping) and jumps to the
    landed city via `_compute_jump`'s existing `"city"` kind.
  `_active_simulation_or_now()` (factored out this round, Rule #5) is
  the ONE (moment, observer, cycles) every LIVE travel shortcut AND
  `_open_time_travel`'s own dialog-seeding both read: the running
  simulation while one is live, else the real wall clock at the home
  observer.
- `_open_design()` / `_open_pointer_theme()` / `_open_slot_theme()`:
  open (or raise the live) [Design Window](design_window.md) /
  [Pointer Theme](pointer_theme.md) / [Slot Theme](slot_theme.md) — the
  SAME non-modal, one-live-instance shape ITEM 1's trio uses, but
  LIVE-APPLY (see each module's own docstring for why — every option
  they absorbed already applied on click in the old menu chain).
  `_design_setters()`/`_slot_descriptors()` build the callable bundles
  each window's picks call THROUGH (Rule #5 — the SAME `_set_*`
  methods the old menu chains used), each wrapped so a pick both
  applies and re-supplies the open window with fresh state.
  `_refresh_pointer_theme_gate()`/`_refresh_slot_theme_gate()` (called
  from `_refresh_menu_gating`) gray the top-level entry AND push a
  live gate into an already-open window: Pointer Theme grays on
  Archetype-on, the Pointer element hidden, or the 1st Slot off
  (agent interpretation, flagged in pointer_theme.md); Slot Theme
  grays on Archetype-on or no Slot visible at all.
- `_set_ring()` / `_set_ring_two_metals()` / `_set_display_choice(key,
  value)`: rebuild via the module-level `build_skin(settings)` —
  DEFAULT_SKIN + the chosen RING PRESET (DOMY/Morph/Omega/Templar/Mason
  are ring preset names, nothing more) — or a targeted
  `dataclasses.replace`, install through the shared
  `_install_skin()` (fresh compositor, day context kept) and persist;
  `apply_display_settings(skin, settings)` (pure, testable) overlays
  the display choices, opacity overrides and the custom palette —
  including `archetype_mode`/`earth_label` (owner 2026-07-16/18;
  while the mode is active a seated small-seconds slot no longer
  silences the big hand, since the slots are overridden off).
  `_install_skin()` also re-reserves the window margin from the LIVE
  settings (`defaults.dial_window_margin_fraction(skin)`, owner slike
  1–3 2026-07-17) so a size/hover/letter slider re-sizes the window
  exactly, and `run()`/`_open_settings()` apply the `z_mode` window-flag
  swap (ROADMAP 15e — three modes bottom/normal/top; `run()` re-asserts
  native topmost after the first show, and `_open_settings()` reconnects
  `screenChanged` when the swap recreated the native window — the S18
  caveat). **DIALOG Z-ORDER over the topmost dial (fix round A, owner
  verdict 2026-07-19 — screenshots showed Guide/Settings/Time Travel
  opening OVER the dial in "top" z-mode but Encyclopedia/Observatory
  opening UNDER it):** the root cause was `WindowStaysOnTopHint` itself
  — `SettingsDialog`/`TimeTravelDialog`/`GuideDialog` set it
  unconditionally in `__init__`, but `EncyclopediaDialog`/
  `ObservatoryDialog` were built as deliberately NORMAL windows (owner
  2026-07-13: "must yield to whatever has focus, like any other
  application") — harmless in every OTHER z-mode, but in "top" the dial
  is natively `HWND_TOPMOST` (`native.assert_topmost`, the LegendPopup
  precedent) and an ordinary window then opens underneath it. Both
  dialogs gained an optional `stay_on_top` constructor parameter
  (default False, preserving the 2026-07-13 intent everywhere else);
  `_open_observatory()`/`_open_encyclopedia_at()` pass
  `stay_on_top=(z_mode == "top")` so only THIS z-mode flips the flag —
  no `native.assert_topmost` call needed, `WindowStaysOnTopHint` alone
  is what already clears the dial for the other three dialogs. The
  wheel-pair labels are per pointer (`constants.POINTER_PALETTE_LABELS`,
  owner 2026-07-17 ROADMAP 15e: Court/Family, Temperaments/Elements,
  Walks/Ages, Warm/Cool for Aurora, Zodiac/Almanac, else Paint/Light —
  R5 MENU REWORK moved the picker itself into the
  [Design Window](design_window.md)'s Pointer tab, which reads this
  SAME raw-English table directly, translated at build time; `watch_
  title` reads it too, UNTRANSLATED — Rule #5, one source) and the
  pair is never grayed; the Calendar lighting row is visible only on
  the Calendar pointer.
  `_install_skin()` ALSO refreshes the TITLE row/tray tooltip
  (`_refresh_watch_title`) and any OPEN Design/Pointer Theme/Slot Theme
  window in place (`_refresh_open_mini_windows`, R5 MENU REWORK) — the
  ONE choke point every ring/pointer/palette/diameter change already
  runs through, so a change made through ANY path (a shortcut, a pick
  inside a DIFFERENT mini window) never leaves another open window
  stale.
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
- `_open_time_travel()` / `_end_simulation()`: frozen (moment,
  observer) rendered instead of the present for
  `TIME_TRAVEL_DURATION_S`, then the tick flow snaps back.
  `_open_time_travel` now seeds the dialog's fields FROM
  `_active_simulation_or_now()` (R5b round, Rule #5 — factored out
  rather than duplicated once the Fast Travel/Location shortcuts
  needed the SAME "what does 'right now' mean while travelling" rule). Deep travel
  (Session 16) carries the moment in the 400-year PROXY frame with
  `_sim_cycles` beside it; `_on_tick` asks the repositories for the
  REAL astronomical year, stamps `deep_cycles` on the built context
  and renames the Chinese year from the real year (a 400-year shift
  moves the sexagenary cycle by 40). **R5 MENU REWORK item 3A
  RETIRED the old Quick Jump SUBMENU** (owner 2026-07-14; Session 16
  rework per slika 12; the 4-5-level chain
  `UV/DESIGN/Meni One over Another.png` complained about) — every
  motion it held (Sun/Moon turning points + their eclipses, Day/Month/
  Year/Century/Millennium, North/South Pole, Greenwich, the user's
  `jump_cities`) is now a ROW inside the Time Travel dialog itself, see
  [Time Travel](time_travel.md#quick-jump-rows-item-3a) for the row
  shapes and icons.
- `_compute_jump(base_moment, base_observer, base_cycles, kind, city)`:
  the PURE computation EXTRACTED from the old immediate-jump
  `_quick_jump` (R5 MENU REWORK) — returns the landed `(moment,
  observer, cycles)` or `None` on an edge clamp; every rule from the
  old submenu survives verbatim (places are REAL coordinates with
  their REAL clocks, deep-travel event instants are REBASED into the
  caller's frame via `julian_day_of` before comparing, unit jumps are
  calendar arithmetic via `shift_calendar`). `_dialog_jump` is its
  dialog-facing caller; R5b's `_apply_jump` (below) is its LIVE-dial
  caller — nothing calls it to start a simulation directly any more.
  **R5b PHASE FILTER extension:** the "next_sun"/"prev_sun"/
  "next_moon"/"prev_moon" branch (module-level `_SUN_MOON_JUMP_PATTERN`)
  now also matches an optional `_solstice`/`_equinox` (Sun) or
  `_new`/`_full`/`_quarter` (Moon) suffix — `defaults.
  FAST_TRAVEL_THEMES`' own `jump_stem`s build these — narrowing the
  candidate turning-point set via `_filtered_sun_anchors`/
  `_filtered_moon_events` (module-level, pure) BEFORE the SAME
  compare-on-Julian-Day/land/re-canonicalize logic runs; the plain
  (no-suffix) kinds the Time Travel dialog's own rows use are
  UNCHANGED (the filter is `None`, both helpers pass every candidate
  through). The Moon theme's "eclipse" option and every CALENDAR
  option reuse the EXISTING `_ECLIPSE_JUMPS`/`_UNIT_JUMPS` kinds
  verbatim — no `_compute_jump` change needed for those two.
- `_apply_jump(moment, observer, cycles, kind, city=None)` (R5b round):
  one `_compute_jump` step applied straight to the LIVE dial
  (`_start_simulation` on a landing, a silent no-op on a clamp) — the
  shared tail `_jump_to_place`/`_cycle_jump_city`/`_step_fast_travel`
  all use.
- `_dialog_jump(moment, cycles, latitude, longitude, kind, city)`: the
  Time Travel window's own Quick Jump row callback (item 3A) — wraps
  `_compute_jump` around the DIALOG'S current fields and hands the
  landed state back for the dialog to mirror onto ITS OWN widgets.
  **TT LIVE TRAVEL (owner round R8b item 1):** it now ALSO calls
  `_start_simulation` on the landing as a side effect — "ono sto smo
  radili na uvek Quick Jump dok je bio na right klikku" — so the watch
  travels immediately on every row/arrow click, exactly like
  `_apply_jump` does for every keyboard shortcut; the dialog stays
  open and its own fields just mirror whatever the dial now shows. OK
  (`_open_time_travel`) simply re-asserts the fields' current state —
  a no-op after a pure jump chain. Wired into
  `TimeTravelDialog(jump_callback=...)` in `_open_time_travel`.
- `_bundled_coverage()` / `_travel_coverage()`: the minute-exact core
  tier (the INTERSECTION of the two bundled databases' `coverage()`)
  and the ACTIVE span — the core widened to the Deep Time pack's own
  coverage when the pack is present (`DeepTimeRepository.detect()`
  runs ONCE in the constructor, before the menu build, and the
  instance is injected into both repositories — the one resolution
  point). The dialog validates against the active span BEFORE
  travelling (inline refusal, owner 2026-07-16), the quick jumps clamp
  their searches to it, and `_start_simulation()` re-checks it as a
  final backstop — after FIRST re-canonicalizing the proxy frame (a
  jump or timezone conversion may drift the proxy year across a
  canonical window edge; one enforcement point keeps every path
  consistent with the repositories) — so no travel path can reach the
  day build's die-visibly SystemExit box; the REAL current-day
  protection in `_on_tick` is untouched
- `_collect_secret(char)`: the HIDDEN MODE unlock — printable keys on
  the focused dial roll through a buffer; matching
  `constants.HIDDEN_MODE_SECRET` flips the RUNTIME
  `_hidden_unlocked` flag (owner 2026-07-15: per SESSION, never
  persisted — the code must be re-entered on every launch), the
  Four Greetings appear on the ring letters and in the Encyclopedia
  — the Trinity topic's own reading AND, bound to their CANONICAL
  home (ROADMAP queue #6, owner 2026-07-16), a second reading in the
  Seasons topic, the CANON's three-line quote with an English framing
  of the four faces — and 📊 Report reveals itself above Exit
**ITEM 1 — NON-MODAL Encyclopedia/Guide/Observatory (R4 owner
instruction batch 2026-07-20 — "kada su otvoreni Sat treba da ostane
MOGUC ZA INTERAKCIJU"):** these three now `.show()` instead of
`.exec()` — `exec()` forces APPLICATION modality for its duration
regardless of the dialog's own `windowModality` (Qt: "blocking input
to any other application window"), which is exactly what was locking
the dial out; `.show()` never does. Each dialog's LIVE instance (or
`None`) lives on the controller as `self._encyclopedia` /
`self._observatory` / `self._guide` — a second open request RAISES the
one already open (`raise_()` + `activateWindow()`) instead of stacking
a duplicate; closing it (`finished` signal, fired by both Accept/Close
and the window's X button) clears the attribute back to `None`, and
each dialog carries `WA_DeleteOnClose` so Qt tears down the C++ object
the moment it closes (`quit()` also closes any still-open one
explicitly, so Exit never leaves a stray window mid-teardown). Settings
and Time Travel are UNCHANGED (still `.exec()` — Rule: they mutate
state transactionally and must not be left half-applied by a stray
close). Verified in
[tests/test_controller_dialogs.py](../tests/test_controller_dialogs.py)
(non-modal `isVisible()`/`not isModal()`, second-open-raises identity,
size math) — headless, built exactly like `main.py` minus the mutex.

- `_open_observatory()`: opens (or raises the live) [Observatory](observatory.md)
  (owner 2026-07-16) with the EFFECTIVE `(moment, observer, tz, cycles)`
  — the frozen Time Travel simulation tuple when active, else the live
  present — and the optional Deep Time pack (exact nearest-eclipse
  instants for the eclipse timeline when installed). Passes
  `stay_on_top=z_mode == "top"` (fix round A, owner verdict 2026-07-19
  — see the Z-ORDER note below). Its own internal Enlarge flow
  (`ObservatoryDialog._open_enlarged`) is non-modal too now, for the
  same ITEM 1 reason — see [Observatory](observatory.md)
- `_open_guide()`: opens (or raises the live) [Guide](guide.md) — the
  menu used to build-and-`.exec()` a fresh `GuideDialog` inline in
  `_build_menu`'s lambda; ITEM 1 gave it the same live-instance-
  tracking shape as the other two, so it earned its own method
- `_open_report()`: the hidden [Report](report.md) — the
  [Profiling](../config/profiling.md) statistics (`@timed` on the
  tick, day rebuild, skin build, paint, composite rebuild, hit test,
  hover text, hover warmup, subdial recolor, working-set warmup and
  translation chunks), flushed once per minute and at quit. Stays
  MODAL — an admin snapshot, outside ITEM 1's non-modal trio
- `_open_encyclopedia_at(topic, entry)`: opens (or navigates the live)
  [Encyclopedia](encyclopedia.md) — from the menu (topic None = the
  gallery) or on a Spacebar jump to a hovered topic's entry (the
  widget's `open_encyclopedia` signal). Passes
  `stay_on_top=z_mode == "top"` (fix round A, owner verdict 2026-07-19 —
  see the Z-ORDER note below) and `travel_date=_effective_travel_date()`
  (owner decree 2026-07-19/20) so the Scale badge's Judas/Lucifer
  rotation reads the SAME displayed moment as the poles' light/dark
  glyph — the Time Travel traveled date while a simulation runs, else
  today. The old re-entrancy guard (owner 15h item 3C, Session 21 —
  back when the dialog was MODAL and a second SPACE jump dispatched
  inside `exec()`'s nested loop would have stacked a second modal on
  the first) is now ITEM 1's live-instance dance: a THEMED second jump
  (a real topic) calls `EncyclopediaDialog.navigate_to(topic, entry)`
  on the SAME live window — a strict improvement over the old no-op,
  since the window genuinely moves to the new target instead of
  swallowing the jump; the menu's plain "Encyclopedia…" re-open
  (topic=None) just raises it, leaving whatever page the user is
  already browsing untouched
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
- `_show_if_normal_z_mode()`: the "Show" gesture's shared guard (owner
  2026-07-18, ROADMAP 15h) — a no-op outside `z_mode == "normal"` (in
  "bottom"/"top" raising the dial means nothing), otherwise calls
  `ClockWidget.raise_and_focus`. Wired to BOTH triggers: the menu's
  `_show_action` (see `_build_menu`) and a [Tray Controller](tray.md)
  `on_double_click` callback registered right after the tray icon is
  built — a tray icon DOUBLE-CLICK (`QSystemTrayIcon.ActivationReason.
  DoubleClick`) does the same thing.
