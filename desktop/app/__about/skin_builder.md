# Skin Builder

**Script:** [Skin Builder (script)](../skin_builder.py) · **Flow:**
[diagram](../__flow/skin_builder.md)

## Purpose
THE SKIN BUILDER — settings in, a `SkinDefinition` out.

One question, asked on every launch and after every pick the owner
makes: given these `Settings` and this location, what exactly does the
dial look like? Ring preset and finish, pointer and its palette, hands,
the weekday cast and its metal, the slots' content and seating, crown
text, numerals, opacity — resolved into the ONE typed record
([Manifest](../../skins/__about/manifest.md)'s `SkinDefinition`) the
render layer paints from.

It lived at the top of [Watch Controller](controller.md): a thousand
module-level lines in front of a 3,000-line class that only CALLS them.
The [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md) measured that
file at 4,483 lines carrying seven responsibilities and named this the
first cut (**R10**), because these are free functions over plain data —
they read no `self`, own no window, and 28 test files already imported
them directly, as if the module they wanted had always existed.

## Connections

### Uses
- [Settings Store](settings_store.md) — `Settings`, the input
- [Manifest](../../skins/__about/manifest.md) — `SkinDefinition` and its
  eight specs, the output
- [Config (folder)](../../config/___config.md) — `archetypes`,
  `constants`, `defaults`, `dial`, `palette`, `pantheon`, `paths`,
  `profiling`
- [Rings](../../data/__about/rings.md) · [Hands](../../data/__about/hands.md)
  — the presets and the hand packs
- [Letter Plates](../../render/__about/letter_plates.md) — crown-text
  glyph resolution
- [Crown Text](../../core/__about/crown_text.md) ·
  [World](../../core/__about/world.md) — the arc geometry
- [Thumbs](../watch_face/__about/thumbs.md) — a preset's own preview art

### Used by
- [Watch Controller](controller.md) — `build_skin` on every settings
  change, `watch_title` for the window title, `effective_weekday_slot`
  and `slot_seconds` for the tick and menu gating
- 28 test files — `build_skin` (29 imports), `apply_display_settings`
  (16), `watch_title`, `_location_crown_text`, `_classic_slot_theme`

## Functions

- `build_skin(settings, location_display)`: the door. Resolves the ring
  preset, composes the skin, applies the display settings.
- `_compose_skin(...)`: the long one — every spec of the record, from
  ring and pointer to hands, slots, numerals and crown text.
- `display_for(settings)` / `apply_display_settings(skin, settings)` /
  `_overlay_display_settings(...)`: the display OVERLAY — the picks that
  change what a built skin SHOWS without rebuilding what it is.
- `watch_title(settings, index, count)`: the window/tray title.
- `effective_weekday_slot(settings)` / `slot_seconds(settings)`: two
  questions about the slots that the controller and the overlay both
  ask; public because they cross the module boundary.
- The pure helpers: `_jewel_metal`, `_ring_eye_shine`, `_theme_metal`,
  `_resolve_hands`, `_resolve_ring_inner`, `_location_crown_text`,
  `_crown_arc_glyphs`, `_classic_slot_theme`, `_themed_weekday_set`,
  `_pantheon_weekday_set`.

## Design Decisions
- **What did NOT come along, and why.** The anchor filters
  (`_filtered_sun_anchors`, `_filtered_moon_events` and their index
  tables) belong to Time Travel's jump keys, `_next_rotation_theme` to
  the rotation cycler, `_StayOpenMenu` and `_guard_exclusive_choice` to
  the menu, `_location_flash_text` to the on-screen flash. None of them
  builds a skin, so none of them moved — the cut is by responsibility,
  not by line range.
- **Free functions, not a class.** There is no state between calls: a
  skin is computed from its arguments every time. Wrapping them in a
  `SkinBuilder` object would add a `self` that holds nothing and force
  28 test files to construct one.
- **`effective_weekday_slot` and `slot_seconds` became PUBLIC** in the
  move. The controller reads both, and a private name imported across a
  module boundary is exactly the defect finding L1 recorded elsewhere in
  the same audit.
- **The module is still large** (~890 logic lines) and that is the
  subject's size, not a second responsibility hiding: `_compose_skin`
  alone answers for every visible part of one dial. It sits under the
  wall with room, and it is one thing.
