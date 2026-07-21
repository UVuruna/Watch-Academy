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
- [Clock Widget](widget.md) — creates and positions the window; fires
  `shortcut_triggered` (R5 MENU REWORK) for `_on_shortcut`
- [Tray Controller](tray.md) — shows the tray icon; `set_tooltip` carries
  the full `watch_title`
- [Settings Store](settings_store.md) — load/recover/save
- [Minute Scheduler](scheduler.md) — tick source
- [Clock State](../core/clock_state.md) — day/tick builds
- [Seasons](../data/seasons.md), [Moon Phases](../data/moon_phases.md) — anchors and windows
- [Compositor](../render/compositor.md), [Assets](../render/assets.md) — rendering
- [Design Window](design_window.md), [Pointer Theme](pointer_theme.md),
  [Slot Theme](slot_theme.md) — the three R5 mini windows
- [Time Travel](time_travel.md) — now hosts its own Quick Jump rows
  (item 3A), fed by `_dialog_jump`/`_compute_jump`
- [Config (folder)](../config/___config.md) — defaults (DEFAULT_CITY, DEFAULT_SKIN,
  SHORTCUTS) and paths

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
- `_build_menu()`: the shared tray/right-click menu, every level a
  `_StayOpenMenu` — CHECKABLE picks keep the menu open for several
  settings in one visit; plain actions close as usual (a rebuild while
  open closes and RETAINS the old menu so Qt never deletes a visible
  popup). **R5 MENU REWORK (owner spec 2026-07-20,
  `UV/DESIGN/RIGHT CLICK MENU.txt` — the exact "4-5 branching levels
  stack one over another in a screen corner" complaint,
  `UV/DESIGN/Meni One over Another.png`):** the menu is FLAT now.
  Top-to-bottom: the TITLE row (a `QWidgetAction`-hosted `QLabel`,
  `watch_title(settings, full=False)` — a single watch shows just its
  location; the FULL multi-attribute name backs the tray hover tooltip
  via `_refresh_watch_title`, called from `_install_skin`); 👁️ Show
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
  own Quick Jump rows — see below); 📊 Report (hidden), 🚪 Exit. The
  QUICK JUMP submenu (the OTHER half of the "4-5 levels" complaint) is
  GONE — absorbed into the Time Travel dialog itself (item 3A).
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
  item 2A): the watch's own display NAME — `full=False` (the menu
  TITLE row) is just `settings.city_name`; `full=True` (the tray hover
  tooltip, `_refresh_watch_title`) is
  f"{location}-{ring_finish} {ring}-{palette label} {pointer}", e.g.
  "Belgrade-Gold DOMY-Family Trinity" — UNTRANSLATED on purpose (a
  NAME, not chrome, the same treatment `POINTER_DISPLAY_NAMES` and a
  ring preset's own name already get). Kept as ONE function so ADD
  WATCH (the next round, multi-watch names) only has to loop it.
- `_on_shortcut(action_id)` (R5 MENU REWORK item 2, `defaults.
  SHORTCUTS`): dispatches one keyboard shortcut, fired by the focused
  [Clock Widget](widget.md)'s `keyPressEvent` →
  `shortcut_triggered` signal (every combo needs the dial to hold
  keyboard focus — no new global hook this round beyond the existing
  SPACE hook). `_cycle_ring`/`_cycle_weekday_theme` (Ctrl+R/Ctrl+W)
  walk `sorted(ring_presets(...))`/`_WEEKDAY_THEME_ORDER` and delegate
  to `_set_ring`/`_set_weekday_theme`, which already refresh any open
  mini window through `_install_skin`. `_cycle_slots` (Ctrl+N) walks
  the 1 → 2 → 3 chain directly, 0→1→2→3→0 — the SAME chain the Slot
  Theme window's medals respect, and the bootstrap out of "no slot
  visible" (Slot Theme's own gray condition). `_toggle_archetype_
  shortcut` (Ctrl+A) mirrors the menu's own Archetype toggle
  (including its checked-state QAction, bypassed by the shortcut
  path) — a no-op where the mode is unavailable. The five dialog-
  opener actions (Ctrl+E/G/,/O/T) and `return_to_now` (Ctrl+Home) call
  the existing `_open_*`/`_end_simulation` methods directly. A z-mode
  shortcut was considered and DROPPED (Ctrl+Z's pre-existing "Undo"
  expectation, which this app has nothing to honor).
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
  `TIME_TRAVEL_DURATION_S`, then the tick flow snaps back. Deep travel
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
  calendar arithmetic via `shift_calendar`). Nothing calls it to
  START a live simulation any more — `_dialog_jump` is its only
  caller now.
- `_dialog_jump(moment, cycles, latitude, longitude, kind, city)`: the
  Time Travel window's own Quick Jump row callback (item 3A) — wraps
  `_compute_jump` around the DIALOG'S current fields (never the live
  simulation) and hands the landed state back for the dialog to apply
  to ITS OWN widgets; OK still applies the final choice
  transactionally. Wired into `TimeTravelDialog(jump_callback=...)` in
  `_open_time_travel`.
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
