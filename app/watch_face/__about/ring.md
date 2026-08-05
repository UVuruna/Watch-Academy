# Ring Section

**Script:** [Ring Section (script)](../ring.py) · **Flow:** [diagram](../__flow/ring.md)

## Purpose
The Watch Face window's Ring page (R-10), rebuilt for THE
COMPOSITIONAL RING MODEL (owner decree 2026-08-05): preset gallery
(thumbnail tiles of each preset's LOCKED outer, tooltip stating the
lock), the finish pills, the Two-metals/Shine checkboxes (unchanged),
an INNER gallery (eight tiles — user-changeable independent of the
locked outer) and a Crown Text group (read-only preset text, or a
custom ring's own typed text + top/bottom orientation) — plus R-13's
"Custom ring…" button.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `art_thumbnail`
- [Watch Face Shared Widgets](widgets.md) — `pill`, `tile`
- [Rings (data)](../../../data/__about/rings.md) — `ring_presets`
- [Config (folder)](../../../config/___config.md) — `RING_OUTERS`,
  `RING_OUTER_LOCK`, `RING_INNERS`, `RING_INNER_PRESET_DEFAULT`,
  `RING_INNER_DEFAULT`, `RING_FINISHES`, `RING_EYE_GLYPH`,
  `RING_TWO_METALS_DEFAULT`, `RING_EYE_SHINE_DEFAULT`

### Used by
- `app.watch_face.window` — registered as the Ring section's builder

## Design Decisions
- **R-13 honesty note:** `app/settings_dialog/custom_art_section.py`'s
  custom-ring flow is a plain-Python mixin baked directly onto
  `SettingsDialog` — there is no standalone custom-ring editor `QDialog`
  to embed. Rather than duplicate its inline widgets (a name field, a
  layout combo, a per-position letter-combo row, thematic color, "Add
  ring"), the "Custom ring…" button opens the EXISTING Settings dialog
  through `setters["open_custom_ring"]`, navigated straight to its
  Custom art section via the new `dialog.SettingsDialog(...,
  initial_section="Custom art")` parameter — honest reuse, not a second
  editor to keep in sync.
