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
   (`_letter_metal`, `_ring_two_metals`, `_ring_eye_shine`, `_theme_metal`,
   `_earth_continent`, `_resolve_hands`, `_themed_weekday_set`,
   `_pantheon_weekday_set`, `_classic_slot_theme`) — turning a `Settings`
   into a `SkinDefinition`. Pure, testable, no `QObject` involved.
2. **The Qt window/tray/menu shell** — `__init__`'s wiring, `run()`,
   `_build_menu()` (255 lines alone), `_teardown_windows()`, `discard()`,
   `_prepare_quit()`, `quit()`, `_position_widget()`, the debounced-save
   pair (`_on_widget_moved`/`_flush_position`), `refresh_title()`.
3. **Dialog opening/lifecycle** — the non-modal one-live-instance dance
   for Design/Pointer Theme/Slot Theme/Encyclopedia/Observatory/Guide,
   plus the modal Settings/Time Travel/Report openers
   (`_open_design`, `_open_pointer_theme`, `_open_slot_theme`,
   `_open_encyclopedia_at`, `_open_observatory`, `_open_guide`,
   `_open_settings`, `_open_report`) and their `_design_setters`/
   `_slot_descriptors` callable bundles.
4. **Keyboard shortcuts** — `_on_shortcut` and its ~20 per-family
   handlers (ring/weekday cycling, slot cycling, Fast Travel stepping,
   Location jumps, the hidden-mode secret buffer).
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
- [Design Window](design_window.md), [Pointer Theme](pointer_theme.md),
  [Slot Theme](slot_theme.md), [Time Travel](time_travel.md), [Report](report.md),
  [Observatory](observatory.md) — opens/owns the one live instance of each
- [Settings Dialog (subfolder)](../settings_dialog/___settings_dialog.md),
  [Encyclopedia (subfolder)](../encyclopedia/___encyclopedia.md) — opens
  them; applies their results
- [Core (folder)](../../core/___core.md) — `build_day_context`,
  `build_tick_state`, `core.deep_time.*`
- [Data (folder)](../../data/___data.md) — `DeepTimeRepository`,
  `MoonPhaseRepository`, `SeasonsRepository`, `SymbolismRepository`,
  `TranslationStore`
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
  silently wrong dial
- `_build_menu()`: the shared tray/right-click `_StayOpenMenu` — TITLE
  row, Add/Remove Watch, Show (tray-only), Design…/Pointer Theme…/Slot
  Theme… (the R5 mini windows), Visible dropdown, Legend/Solar
  rotation/Archetype/Click-through toggles, Settings…/Encyclopedia…/
  Observatory…/Guide…/Time Travel…, the hidden Report, Exit
- `_compute_jump(base_moment, base_observer, base_cycles, kind, city)`:
  the pure jump arithmetic (places, turning points, calendar unit
  jumps, the optional phase filter) shared by every travel entry point;
  returns the landed `(moment, observer, cycles)` or `None` on an edge
  clamp
- `_start_simulation(moment, observer, cycles=0)` / `_end_simulation()`:
  freezes/unfreezes the rendered moment for `TIME_TRAVEL_DURATION_S`

## Module-level functions (skin-building responsibility)

### `build_skin(settings) -> SkinDefinition`
The ONE render config: `DEFAULT_SKIN` with the chosen ring preset card,
the chosen finish's letter art, the chosen hand pack and the user's
display choices overlaid — built inside this watch's own display
context (`paths.display(display_for(settings))`, owner bug fix
2026-07-28: building watch 2's skin must never see watch 1's art
source/subdial set).

### `display_for(settings) -> paths.DisplayContext`
The per-watch art-source/subdial-set/metal-shade triple, read once and
carried on the skin — replaces what used to be process-wide globals.

### `apply_display_settings(skin, settings)`
Pure, testable overlay of the display choices (opacity overrides,
element visibility, saturation, custom palette, archetype mode, earth
label) onto an already-built skin — called by `_install_skin` after the
PRISTINE `build_skin` so cleared overrides really clear.

### `watch_title(settings, full=False) -> str`
The watch's own display NAME — `full=False` is just `settings.city_name`;
`full=True` is `f"{location}-{ring_finish} {ring}-{palette_label} {pointer}"`,
deliberately UNTRANSLATED (a name, not chrome). The tray hover tooltip
always passes `True`; the menu TITLE row passes `watch_count() >= 2`.

### Small pure helpers
`_letter_metal`, `_ring_two_metals`, `_ring_eye_shine`, `_theme_metal`,
`_earth_continent`, `_resolve_hands`, `_next_rotation_theme`,
`_filtered_sun_anchors`, `_filtered_moon_events`, `_slot_seconds`,
`_effective_weekday_slot`, `_classic_slot_theme`, `_themed_weekday_set`,
`_pantheon_weekday_set` — each a small, independently testable piece of
the skin-building responsibility.

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
