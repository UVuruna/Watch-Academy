# Themes & Slots Section

**Script:** [Themes & Slots Section (script)](../themes.py) · **Flow:** [diagram](../__flow/themes.md)

## Purpose
The Watch Face window's Themes & Slots page (Phase ③, R-17/R-18/R-19/
R-20) — replaces the placeholder. Top to bottom:

1. **FACE LAYOUT row (R-17):** four pills — Full face / 1 subdial /
   2 subdials / 3 subdials — the SAME state `Ctrl+N`'s `_cycle_slots`
   steps through, picked directly here instead of incrementally
   (`app.settings_store.slot_layout_target` reads the current one;
   `Settings["slot_layout"]` applies a target at once).
2. **SLOT PICKER row:** medal buttons (🥇🥈🥉) choosing which slot is
   being edited, disabled when that slot is off — plus the "Names"
   checkbox — built from the EXACT `SlotDescriptor` triple
   `app.controller._slot_descriptors()` already builds for the
   (retired-later) Slot Theme window (Rule #5, no second copy).
3. **The content tree** ([theme_tree.py](theme_tree.md)) — delegated
   whole; this module only decides WHICH descriptor is active and
   whether the layout is FULL FACE (no slot enabled) or a real subdial.
4. **Calendar mount gallery** (Phase 6 FINAL cleanup, owner decree
   2026-07-29): shown ONLY while the Calendar pointer is active — WHICH
   roster rides its twelve wedges, ported from the retired Pointer
   Theme window's second tab (`build_calendar_mount_grid`, Rule #5, no
   second copy of the gallery itself).
5. **Subdial plate pills** (Theme background / Classic black,
   `settings.subdial_style`) — moved from the retired
   `design_window.DesignDialog._complications_tab`.
6. **Artwork combo** (Phase 6 FINAL cleanup): the Gemini/ChatGPT ART
   SOURCE pick, ported verbatim from the retired
   `app.settings_dialog.themes_section._build_artwork_group`
   (`settings.art_source`) — LIVE-APPLY here instead of that copy's
   on-OK commit.
7. **Subdial plate SET combo** (Phase 6 FINAL cleanup): WHICH of the
   five hand-picked plate looks draws (`settings.subdial_set` — NOT the
   same setting as the Subdial plate pills above), ported verbatim from
   the retired `app.settings_dialog.themes_section.
   _build_subdial_set_group`.
8. **Theme rotation controls** — R-20 shipped the interval amount+unit
   and "Follow ring color" pair alone, moved from
   `app.settings_dialog.themes_section._build_theme_rotation_group`
   and narrowing it to ONLY that pair (the rotation GROUP picker — None
   / one kinship family / Custom — and the per-theme metal combos were
   deliberately deferred: "the old Settings copy until Phase 6"). Phase
   6 FINAL cleanup now PORTS those two remaining pieces here too,
   verbatim, before deleting `themes_section.py` outright — an R-20
   debt closed, not silently dropped.

## Connections

### Uses
- [Content Tree](theme_tree.md) — the Level 1/2/3 breadcrumb picker
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Weekday Theme Grid](../../__about/weekday_theme_grid.md) —
  `build_calendar_mount_grid` (the Calendar mount gallery)
- [Config (folder)](../../../config/___config.md) —
  `constants.watch_face_kinds`, `constants.ART_SOURCES`/
  `ART_SOURCE_TITLES`, `constants.SUBDIAL_SETS`/`SUBDIAL_SET_TITLES`,
  `constants.METAL_THEMES`/`theme_metals`, `pantheon.WEEKDAY_MENU_GROUPS`/
  `WEEKDAY_THEME_TITLES`
- [Watch Controller](../../__about/controller.md) —
  `setters["slot_layout"]`, `setters["slot_descriptors"]`,
  `setters["calendar_mount"]`, `setters["subdial_style"]`,
  `setters["art_source"]`, `setters["subdial_set"]`,
  `setters["theme_rotation_minutes"]`, `setters["theme_rotation_group"]`,
  `setters["theme_rotation_themes"]`, `setters["theme_metal"]`,
  `setters["theme_metal_follow_ring"]`

### Used by
- `app.watch_face.window` — registered as the Themes & Slots section's
  builder

## Design Decisions

- **THE VARIANT PANEL took the Artwork group's seat** (ballot verdicts
  3A + 8A, 2026-08-15). Artwork was only ever ONE of the four scattered
  mechanisms the owner reported as "variant of a theme"; the panel
  (`theme_variants.py`) gathers all four — style, metal, source, roster
  — under the content tree, beside the theme the tree just picked, and
  prints only the rows that theme can offer. `_artwork_group` is DELETED
  rather than deprecated in place (Rule "No Backward Compatibility");
  the panel's Source row draws the same base-plus-Sunday-dual composite
  it drew.
- **The Roster row left this module's tree too.** It spent one round
  seated inside the Theme families card (a runtime ALG-7 fix) on its way
  to where it belongs. Two seats for one control would be a Rule #5
  violation, so `theme_tree._add_roster_row` is gone.
- **VERDICT 5E: the per-theme METAL combos are gone from Theme
  rotation.** They never belonged there — a setting reachable only while
  its theme happened to be in the rotation is a setting hidden behind an
  unrelated choice, which is exactly what the owner reported. Rotation
  now carries only what rotation is: which themes rotate, how often, and
  whether the ring colour drives the metal.


- **Full face has no enabled slot** (owner architecture: `show_weekday
  = False` skips the weekday render layer entirely — confirmed in
  `render/compositor.py`'s `skipped["weekday_set"]`). Rather than a
  blank page, this section still binds the content tree to slot 1's
  OWN `weekday_theme`/`weekday_roster`/`show_weekday_names` — the exact
  values that take effect the moment a subdial turns back on — filtered
  through `constants.watch_face_kinds(pointer, pointer_shape)` so a
  pointer with no full-face "week" content (Calendar, Aurora, the Rose
  in polygon shape) shows an explanatory note instead of a picker that
  would apply invisibly. This is a Phase ③ judgment call, not an owner
  transcript — see the Phase ③ session report for the reasoning and
  the recorded debt (the "dozen"/"cube"/"wheel" kinds have no slot-
  content rendering path at all today).
- **Module-level navigation state** (`_active_slot`, see the file):
  `WatchFaceDialog._build()` tears down and reconstructs EVERY
  section's page on ANY live-apply pick anywhere in the window (see
  window.md) — so which slot medal is selected must survive a pick
  made elsewhere. A plain click on a medal button changes no setting
  (pure navigation) and therefore never triggers that outer rebuild;
  the state only needs to survive an unrelated refresh, which module
  scope does for free — the same reason `SlotThemeDialog` keeps
  `self._active_index` as a plain attribute (that dialog is simply
  never torn down).
