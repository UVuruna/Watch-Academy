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
4. **Subdial plate pills** (Theme background / Classic black,
   `settings.subdial_style`) — moved from
   `design_window.DesignDialog._complications_tab`.
5. **Theme rotation controls** (interval amount+unit, "Follow ring
   color") — moved from
   `app.settings_dialog.themes_section._build_theme_rotation_group`,
   narrowed to ONLY the interval + follow-ring pair (the rotation GROUP
   picker and the per-theme metal combos stay in the old Settings copy
   until Phase 6 — R-20 asked for the interval alone).

## Connections

### Uses
- [Content Tree](theme_tree.md) — the Level 1/2/3 breadcrumb picker
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) —
  `constants.watch_face_kinds`
- [Watch Controller](../../__about/controller.md) —
  `setters["slot_layout"]`, `setters["slot_descriptors"]`,
  `setters["subdial_style"]`, `setters["theme_rotation_minutes"]`,
  `setters["theme_metal_follow_ring"]`

### Used by
- `app.watch_face.window` — registered as the Themes & Slots section's
  builder

## Design Decisions
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
