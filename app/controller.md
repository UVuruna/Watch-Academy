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
  📜 Legend, 🔆 Solar rotation, 🎭 Archetype (+ its 🌍 Earth weekday
  sub-toggle), 🖱️ Click-through | ⚙️ Settings…,
  🏛️ Encyclopedia…, 📖 Guide…, 🕰️ Time Travel… | 🚪 Exit. The three
  slot submenus are THE SAME SHAPE (`build_slot_menu` builds each):
  a Weekday submenu in KINSHIP GROUPS (`WEEKDAY_MENU_GROUPS`: Ancient
  Gods / Society — Professions, Creeds, Mysteries — / Animals /
  Arcana, where Planets nests its Image and Sign looks; the metal
  themes open a Gold/Bronze/Silver/Colored metal dropdown whose pick
  activates theme AND metal, releasing follow-the-ring; the pantheon
  themes carry a Planetary/Pantheon roster pair in the same dropdown
  — below the metals on Greek/Norse, the whole dropdown on Egyptian/
  Slavic — writing that slot's OWN `*_roster` key, owner 2026-07-15:
  slot 1 Greek Planetary can sit beside slot 2 Greek Pantheon) — plus the
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
  wears the theme AND roster of the slot that DRIVES it
  (`_classic_slot_theme` + `_themed_weekday_set` /
  `_pantheon_weekday_set`, owner 2026-07-15): on the Seasons/Compass
  with two slots where only the 2nd is weekday, that slot rides the
  rotation in ITS OWN theme. The pantheon set resolves every seat
  through `defaults.pantheon_seat` — the safety law: the first
  EXISTING candidate plate wins with the pantheon identity (name +
  article), a seat whose art has not landed keeps the PLANETARY
  bundle whole, and a missing pantheon dual pulls the WHOLE Sunday
  pair (plate, names, face texts) back to planetary. Theme ROTATION
  cycles inside a kinship group picked in Settings
  (`rotation_themes`).
  Then Ring (DOMY/MORPH presets + the Gold/Silver/Bronze
  letter-finish group; the tint color picker lives in Settings), Pointer
  (three groups: Trinity/Seasons/Prism/Compass/Aurora/Calendar variant —
  the owner's display names for trio/cross/hexa/octa/aurora/calendar;
  Aurora and Calendar have no arm count, and Aurora forces solar
  rotation (its toggle grays out) — the Paint/Light palette group, and
  the Calendar lighting group (Hour/Year)) and Umbra
  (two groups: Fine/Coarse/Gradient form + Full/Half/Light/Dark
  contrast); the Paint/Light group is GRAYED in place only while the
  SEASONS drive the pointer now (owner 2026-07-16, revised the same
  day with the CANON Family wheel: the Trinity carries TWO wheels —
  Court paint / Family light, `PALETTE_PRESETS[("trio", "light")]` —
  so the pair is LIVE there; `_menu_gates["palette_style"]`,
  `_add_choice_group` returns its actions so `_refresh_menu_gating`
  re-grays them in place). On the
  Calendar pointer Paint/Light instead PICK THE WHEEL — paint = Zodiac,
  light = Almanac (the labels stay, the equivalence is documented) — so
  the group stays live there; the Calendar lighting group is grayed off
  the Calendar pointer (`_menu_gates["calendar_lighting"]`). Then
  Size (360…1440),
  Elements (the FINAL.txt #5 on/off switches, via the shared
  `_add_toggle()` helper: Earth — with its Clean/Atmosphere style
  group nested — Moon, Weekday, Pointer, Colorful — off draws the
  day/twilight arcs as plain white transparency — and Seconds, which
  also switches the tick cadence through
  `MinuteScheduler.set_per_second`), the Legend toggle (off = no
  hovers at all; with click-through the dial has zero interaction),
  the Solar rotation toggle (off = upright Star/Aura/Umbra), the
  ARCHETYPE toggle pair (owner sealed package 2026-07-16): 🎭
  Archetype — the stay-open checkable that turns the mode on (the
  render-level override; the slot settings stay untouched) — with 🌍
  Earth weekday beneath it (`archetype_earth_day`, live only while
  the mode runs); `_refresh_menu_gating` grays the Archetype toggle
  where no archetype exists (Aurora, Calendar, Pointer element off)
  and, WHILE THE MODE IS ON, grays the three slot submenus and their
  enables IN PLACE and releases the big-seconds gate (a seated
  small-seconds slot cannot silence the hidden big hand); the
  gating call now also closes `_build_menu` itself, so a fresh menu
  and an in-place refresh share the ONE implementation. Then Time
  Travel…, Click-through toggle (turn back off via the TRAY — the
  dial itself no longer takes clicks), Exit
- `_set_ring()` / `_set_display_choice(key, value)`: rebuild via the
  module-level `build_skin(settings)` — DEFAULT_SKIN + the chosen RING
  PRESET (DOMY and MORPH are ring preset names, nothing more) — or a
  targeted `dataclasses.replace`, install through the shared
  `_install_skin()` (fresh compositor, day context kept) and persist;
  `apply_display_settings(skin, settings)` (pure, testable) overlays
  the display choices, opacity overrides and the custom palette —
  including `archetype_mode`/`archetype_earth_day` (owner 2026-07-16;
  while the mode is active a seated small-seconds slot no longer
  silences the big hand, since the slots are overridden off)
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
  `TIME_TRAVEL_DURATION_S`, then the tick flow snaps back. Deep travel
  (Session 16) carries the moment in the 400-year PROXY frame with
  `_sim_cycles` beside it; `_on_tick` asks the repositories for the
  REAL astronomical year, stamps `deep_cycles` on the built context
  and renames the Chinese year from the real year (a 400-year shift
  moves the sexagenary cycle by 40). The QUICK JUMP submenu (owner
  2026-07-14; Session 16 rework per slika 12) leads with NOW, then:
  **🌞 Sun** (next/prev turning point + next/prev SOLAR eclipse — 🌑
  stand-in icon), **🌙 Moon** (next/prev phase + next/prev LUNAR
  eclipse — 🌘), **📅 Year · Month · Day** (six unit jumps), **🏛
  Century · Millennium** (four — 🏛 the agent's pick from the owner's
  "🏛 or ⏳"), **📍 Location** (poles, Greenwich + the user's
  `jump_cities` from Settings — a place jump moves the OBSERVER, the
  moment stays). Eclipse entries need the pack and GRAY without it
  (tooltip names the full installation); eclipse picks land on the
  catalog instant via `julian_day_of` next/prev queries; unit jumps
  are calendar arithmetic on the real astronomical date
  (`shift_calendar` — Feb 29 clamps, era edges are plain arithmetic);
  event instants from differently-canonicalized years are REBASED into
  the sim frame before comparing (whole Gregorian cycles — exact).
  Jumps CHAIN off the running simulation, every jump entry keeps the
  menu OPEN (`stay_open`), all jumps clamp to the active coverage (an
  edge step is a no-op), and the dialog seeds from the simulation; the
  dialog's blue Now button ends the simulation through `RETURN_TO_NOW`
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
- `_open_report()`: the hidden [Report](report.md) — the
  [Profiling](../config/profiling.md) statistics (`@timed` on the
  tick, day rebuild, skin build, paint, composite rebuild, hit test,
  hover text, subdial recolor, working-set warmup and translation
  chunks), flushed once per minute and at quit
- `_critical_box()`: shared stay-on-top critical dialog (errors must be
  seen even when other windows cover the screen)
