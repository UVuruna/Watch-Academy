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

## THIS FILE IS A DOCUMENTED GOD-FILE (Rule #20 ratchet)
`controller.py` is 3,449 lines — well past the ~1,000-line Violation
threshold — and carries a `tests/test_structure_law.py` ratchet entry.
It currently holds SIX distinct responsibilities that a future session
owes a split (see [Refactor God-Files](../../../../REFACTOR-GODFILES.md)
for the procedure):

1. **Skin building from settings** — the module-level `build_skin`/
   `_compose_skin`/`apply_display_settings`/`display_for`/
   `_overlay_display_settings` functions and their small pure helpers
   (`_jewel_metal`, `_ring_two_metals`, `_ring_eye_shine`, `_theme_metal`,
   `_resolve_hands`, `_themed_weekday_set`,
   `_pantheon_weekday_set`, `_classic_slot_theme`) — turning a `Settings`
   into a `SkinDefinition`. Pure, testable, no `QObject` involved.
2. **The Qt window/tray/menu shell** — `__init__`'s wiring, `run()`,
   `_build_menu()` (255 lines alone), `_teardown_windows()`, `discard()`,
   `_prepare_quit()`, `quit()`, `_position_widget()`, the debounced-save
   pair (`_on_widget_moved`/`_flush_position`), `refresh_title()`.
3. **Dialog opening/lifecycle** — the non-modal one-live-instance dance
   for Watch Face/Encyclopedia/Observatory/Guide (Phase 6 FINAL cleanup
   retired the separate Design/Pointer Theme/Slot Theme mini windows —
   the Watch Face window is their sole survivor), plus the modal
   Settings/Time Travel/Report/Shortcuts openers (`_open_watch_face`,
   `_open_encyclopedia_at`, `_open_observatory`, `_open_guide`,
   `_open_settings`, `_open_report`, `_open_shortcuts` — R-37) and their
   `_watch_face_setters`/`_slot_descriptors` callable bundles.
   `_apply_settings_dialog_result` is the ONE apply path an
   accepted `SettingsDialog` takes, however it was reached — the plain
   menu opener (`_open_settings`) and the Watch Face Ring section's
   "Custom ring…" button (`_open_custom_ring_editor`, R-13, which opens
   the same dialog navigated to its Custom art section) both call it.
4. **Keyboard shortcuts** — `_on_shortcut` and its ~20 per-family
   handlers (ring/weekday cycling, slot cycling, Fast Travel stepping,
   Location jumps, the hidden-mode secret buffer). `_cycle_slots`
   (Ctrl+N) now shares its flag arithmetic with `_apply_slot_layout`/
   `_set_slot_layout`, which the Watch Face Themes & Slots section's
   FACE LAYOUT row picks directly instead of stepping (Phase ③, R-17).
5. **Time travel and simulation** — `_compute_jump` (the pure jump
   arithmetic), `_apply_jump`/`_dialog_jump`/`_start_simulation`/
   `_end_simulation`/`_active_simulation_or_now`, the coverage guards
   (`_bundled_coverage`/`_travel_coverage`).
6. **Tick plumbing** — `_on_tick`, `_on_wake`, `_on_screen_changed`,
   the translation-overlay background fetch (`_apply_language`/
   `_translate_worker`/`_poll_translation`), the click-through hover
   poller (`_set_click_through`/`_poll_hover`).

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
  [Observatory](observatory.md) — opens/owns the one live instance of each
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

#### Selected methods (grouped by responsibility 2–6 above)
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
- `_build_menu()`: the shared tray/right-click `_StayOpenMenu` — TITLE
  row, Add/Remove Watch, Show (tray-only), Watch Face… (the ONE flat
  entry that replaced the R5 Design…/Pointer Theme…/Slot Theme… mini
  windows, Phase 6 FINAL cleanup), Visible dropdown, Names dropdown
  (R-09/R-26 — weekday names + archetype names, unified beside
  Visible), Legend/Solar rotation/Archetype/Click-through toggles,
  Settings…/Encyclopedia…/Observatory…/Guide…/Time Travel…, the hidden
  Report, Exit
- `_compute_jump(base_moment, base_observer, base_cycles, kind, city)`:
  the pure jump arithmetic (places, turning points, calendar unit
  jumps, the optional phase filter) shared by every travel entry point;
  returns the landed `(moment, observer, cycles)` or `None` on an edge
  clamp
- `_start_simulation(moment, observer, cycles=0)` / `_end_simulation()`:
  freezes/unfreezes the rendered moment for `TIME_TRAVEL_DURATION_S`

## Module-level functions (skin-building responsibility)

### `build_skin(settings, location_display="") -> SkinDefinition`
The ONE render config: `DEFAULT_SKIN` with the chosen ring preset card,
the chosen finish's jewel art, the chosen hand pack and the user's
display choices overlaid — built inside this watch's own display
context (`paths.display(display_for(settings))`, owner bug fix
2026-07-28: building watch 2's skin must never see watch 1's art
source/subdial set). `location_display` (RING VERDICTS round, owner
decree 2026-08-05) is the active location's own "CITY, COUNTRY" text —
`WatchController` passes its live `_active_location_display`; every
other caller (tests, a direct build) leaves it "" and the Location
crown option simply draws nothing extra for that build.

### `display_for(settings) -> paths.DisplayContext`
The per-watch art-source/subdial-set/metal-shade triple, read once and
carried on the skin — replaces what used to be process-wide globals.

### `apply_display_settings(skin, settings)`
Pure, testable overlay of the display choices (opacity overrides,
element visibility, saturation, custom palette, archetype mode, earth
label) onto an already-built skin — called by `_install_skin` after the
PRISTINE `build_skin` so cleared overrides really clear.

**Watch Face Phase 4 additions:** the Umbra tint mode/tint/saturation/
alpha, the Aura-off tint mode/tint, the Hands tint/saturation and the
Indices (`jewels_tint`) fields are direct pass-throughs (each already
carries its own honest default, no override/None dance). Three fields
DO follow the None-override dance, mirroring `star_alpha`: `ghost_alpha`
(overrides `WeekdaySpec.ghost_opacity`, R-36 "Inactive icons"),
`moon_transit_alpha` (overrides `YearMarkerSpec.transit_alpha`, R-35
"Moon — hover over Earth" — the closest honest reading of that brief;
there is no mouse-hover state on this dial, only the Moon/Earth rim
transit `render.daylight.moon_transit_opacity` already computed) and
`umbra_alpha` is a DIRECT value (R-15, owner-requested, no skin default
to fall back to — the Umbra was always fully opaque before this Phase).

**Crown Text + Ring split additions (owner correction 2026-08-05):**
`crown_text_alpha`/`crown_text_scale`/`crown_text_tint` (the outer Great Seal/cross-
station crown text arc, `RingLayer._draw_crown_text`) and `ring_tint_inner` (the
split art's own inner-band tint, `RingLayer._draw_split_plate`) are
direct pass-throughs the same shape as the Phase 4 fields above — see
[Skins Manifest](../../skins/__about/manifest.md) and
[Ring (layer)](../../render/layers/__about/ring.md) for the render-side
design notes. The ROADMAP's earlier "no such element"/"one baked
plate" debts were both WRONG (Phase ④ never found the actual crown-text/
split-art mechanism); this round corrected them, not merely added new
controls.

### `watch_title(settings, full=False) -> str`
The watch's own display NAME — `full=False` is just `settings.city_name`;
`full=True` is `f"{location}-{ring_finish} {ring}-{palette_label} {pointer}"`,
deliberately UNTRANSLATED (a name, not chrome). The tray hover tooltip
always passes `True`; the menu TITLE row passes `watch_count() >= 2`.

### Small pure helpers
`_jewel_metal`, `_ring_two_metals`, `_ring_eye_shine`, `_theme_metal`,
`_location_flash_text` (R-30, the flash's own "CITY, COUNTRY" formatter),
`_location_crown_text` (RING VERDICTS round, owner decree 2026-08-05 —
uppercases and filters `_location_flash_text`'s own output down to
`constants.RING_CROWN_TEXT_CHARSET`, the exact set the crown-text renderer
can draw), `_resolve_hands`, `_next_rotation_theme`,
`_filtered_sun_anchors`, `_filtered_moon_events`, `_slot_seconds`,
`_effective_weekday_slot`, `_classic_slot_theme`, `_themed_weekday_set`,
`_pantheon_weekday_set` — each a small, independently testable piece of
the skin-building responsibility.

**THE LOCATION CROWN (RING VERDICTS round, owner decree 2026-08-05):**
a per-ring toggle (`Settings.ring_crown_location`, keyed by ring name
like `ring_two_metals`) that REPLACES whatever crown text the active
ring carries — a bundled preset's own crown text or a custom ring's typed
text — with the active location's "CITY, COUNTRY", available for
presets and custom rings alike (`_compose_skin`). `WatchController`
keeps a live `_active_location_display` string in lockstep with
`_active_location_name` (R-31) at every one of its update points
(`__init__`, `_flash_location`, `_end_simulation`) — `_flash_location`
(R-30's own flash/tray-title path, every location change funnels
through it: Settings dialog preset pick, Quick Jump, Time Travel,
Greenwich, the poles) ALSO recomposes the skin there, so the crown
follows a location change the same tick the flash/tray title do,
never lagging a tick behind. `_set_ring_crown_location` is the ONE
setter the Watch Face Ring section's "Location" checkbox calls.

**THE RULED LOCATION ARC (owner defect 2026-08-07):** the ledger rules
The One's BOTTOM crown arc to be "City, Country", and until this round
nothing drew it — the toggle above is OFF by default and, when ticked,
draws at the TOP, straight through the live time crown. A preset's ruled
arc is not a user pick, so it is declared in
`dial.RING_LIVE_CROWN[...]["location"]` (the orientation, or `None`) and
APPENDED by `_compose_skin` beside the preset's own crown text. The user
toggle still wins when ticked, so the two never draw together.

**The separator.** `constants.RING_JEWEL_FILES` has no COMMA plate (52
entries: uppercase Latin/Greek, digits, `$`, `&`, `✠`, the Eye, the
colon), so `_location_crown_text` drops the comma and collapses the gap
to ONE SPACE — "Belgrade, Serbia" reads "BELGRADE SERBIA". That is the
existing formatter reused, not a new rule: it is what the Location
toggle has drawn since the RING VERDICTS round.

`dial.RING_LIVE_CROWN_LOCATION_READING` holds the arc's hover text once
(it was a dict literal inlined in the toggle's branch), shared by both
paths.

## Classes (menu plumbing)

### `_StayOpenMenu(QMenu)`
A menu whose CHECKABLE items (and plain actions carrying the
`"stay_open"` property) do not close it — several settings changed in
one visit.

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
- **Split is owed, not yet done.** This god-file predates THE STRUCTURE
  LAW (Rule #20, owner decree 2026-07-29); the six responsibilities
  above are the seam a future split session should cut along — skin
  building is already the most pure/independent of the six and the
  natural first extraction.
