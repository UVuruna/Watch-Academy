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
- `_build_menu()`: the shared tray/right-click menu (owner rework
  2026-07-13), every level a `_StayOpenMenu` — CHECKABLE picks keep
  the menu open for several settings in one visit; plain actions
  close as usual (a rebuild while open closes and RETAINS the old
  menu so Qt never deletes a visible popup). Emoji-fronted top level:
  🎨 Design (Pointer, Ring, Umbra, Complications — the subdial plate
  style, Theme background / Classic black (owner A/B spec 2026-07-15)
  — | Hands, Earth — with the Date switch — | Size), 🥇 1ˢᵗ Slot,
  🥈 2ⁿᵈ Slot, 🥉 3ʳᵈ Slot, 🧩 Elements |
  📜 Legend, 🔆 Solar rotation, 🖱️ Click-through | ⚙️ Settings…,
  🏛️ Encyclopedia…, 📖 Guide…, 🕰️ Time Travel… | 🚪 Exit. The three
  slot submenus are THE SAME SHAPE (`build_slot_menu` builds each):
  a Weekday submenu in KINSHIP GROUPS (`WEEKDAY_MENU_GROUPS`: Ancient
  Gods / Society — Professions, Creeds, Mysteries — / Animals /
  Arcana, where Planets nests its Image and Sign looks; the metal
  themes open a Gold/Bronze/Silver/Colored metal dropdown whose pick
  activates theme AND metal, releasing follow-the-ring) — plus the
  slot's OWN Names switch — the COMPLICATIONS submenu (Digital time /
  Date / Day length / Seconds — the seated small seconds silences the
  big hand and its Elements toggle), and the Astrology / Ascendant /
  Chinese-zodiac families with their own STYLE dropdowns. Below a
  separator each slot carries its ENABLE switch: slots enable
  strictly 1 → 2 → 3 (`enable2`/`enable3` gates gray the jumps); the
  Seasons three-slot case locks the 1st on the classic weekday unit
  (`first_lock`). Each slot's top-level entry carries a CHECK MARK
  beside its ordinal while the slot is enabled (owner 2026-07-15),
  refreshed in place with the gating. Since the ROUNDEL round (owner
  2026-07-14) TEXT is
  real under EVERY pointer — text and the flat astrology art draw on
  the watch-face subdial. Pointer, show_weekday and show_pointer
  changes re-gray the gated entries IN PLACE (`_refresh_menu_gating`
  over the `_menu_gates` buckets — owner 2026-07-13: those switches
  must not close the open menu; no rebuild). The classic weekday unit
  wears the theme of the slot that DRIVES it (`_classic_slot_theme` +
  `_themed_weekday_set`, owner 2026-07-15): on the Seasons/Compass
  with two slots where only the 2nd is weekday, that slot rides the
  rotation in ITS OWN theme. Theme ROTATION cycles inside a kinship
  group picked in Settings (`rotation_themes`).
  Then Ring (DOMY/MORPH presets + the Gold/Silver/Bronze
  letter-finish group; the tint color picker lives in Settings), Pointer (two
  groups: Trinity/Seasons/Prism/Aurora/Compass variant — the owner's
  display names for trio/cross/hexa/aurora/octa; Aurora has no arm
  count and forces solar rotation (its toggle grays out) — + Paint/
  Light palette) and Umbra
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
- `_open_time_travel()` / `_quick_jump()` / `_end_simulation()`:
  frozen (moment, observer) rendered instead of the present for
  `TIME_TRAVEL_DURATION_S`, then the tick flow snaps back; the QUICK
  JUMP submenu (owner 2026-07-14) leads with NOW (back to the present
  immediately) and offers the next/previous sun and moon turning
  points (big ➜/⬅ arrows — forward reads logo-text-arrow, backward
  arrow-logo-text, owner 2026-07-15), the two poles and Greenwich —
  jumps CHAIN off the running simulation (time keeps its place when
  the place changes and vice versa), every jump entry keeps the menu
  OPEN (the `stay_open` action property on the `_StayOpenMenu`), and
  the dialog seeds from the simulation; the dialog's blue Now button
  (left of OK/Cancel) ends the simulation through `RETURN_TO_NOW`
- `_collect_secret(char)`: the HIDDEN MODE unlock — printable keys on
  the focused dial roll through a buffer; matching
  `constants.HIDDEN_MODE_SECRET` flips the RUNTIME
  `_hidden_unlocked` flag (owner 2026-07-15: per SESSION, never
  persisted — the code must be re-entered on every launch) and the
  Four Greetings appear on the ring letters and in the Encyclopedia
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
