# Custom Art Section

**Script:** [Custom Art Section (script)](../custom_art_section.py) · **Flow:** [diagram](../__flow/custom_art_section.md)

## Purpose

`_CustomArtSectionMixin` — the Custom ring and Custom hands builders.
Plain-Python mixin (no base class); composed onto [Settings Dialog]
(dialog.md)'s `QDialog` shell. Since Phase 6 FINAL cleanup this is no longer
a visible sidebar row — it is reached only through the dialog's hidden
`initial_section="Custom art"` construction mode (dialog.md's Design
Decisions), opened by the Watch Face Ring section's "Custom ring…" button.

- **Custom ring** — THE COMPOSITIONAL RING MODEL (owner decree
  2026-08-05): the ring card builder picks an OUTER
  (`constants.RING_OUTERS` — any outer is legal, not just the five
  presets' locked ones), a library jewel per empty field and a unique
  name; the per-position dropdown is GROUPED (owner spec 2026-07-11)
  into Latin (the full A–Z), Greek, Numbers (1–10, 20 — growing) and
  Symbols sections with unselectable headers
  (`constants.RING_JEWEL_GROUPS`) — a NUMBER only fits its own hour
  (owner rule 2026-07-12), so the Numbers section offers at most the
  position's own number. A "Thematic color" combo (CUSTOM-THEMATIC
  widening, owner 2026-07-27) picks what the card's jewels wear under the
  Thematic ring finish — ANY transformer ramp, the five theme colors and
  every metal — stored on the card as the optional `thematic` field; "Auto"
  leaves it absent (moon indigo fallback). Add validates the card
  (`data.rings.validate_preset`) and OK persists it (it appears in the Watch
  Face window's Ring gallery). The INNER band and any CROWN TEXT are NOT
  part of this builder — they are Settings-level choices, set afterward
  in the Watch Face Ring section (`app.watch_face.ring`).
- **Custom hands** (owner spec 2026-07-12) — the hand-pack builder: three
  PNGs pointing UP, a pivot per hand (x from the left, 'center' by default;
  y in pixels from the bottom), a bottom-up z-order and a unique name. Add
  writes the pack folder immediately (files, not settings, via
  `data.hands.user_hands_dir`) — it appears in the Watch Face window's Hands
  gallery.

## Connections

### Uses
- [Config (folder)](../../../config/___config.md) — `constants.RING_OUTERS`/
  `RING_JEWEL_GROUPS`/`METAL_SHADE_NAMES`/`METAL_SHADE_TITLES`, `defaults`
  (`defaults.paths.assets_dir()` for the bundled-vs-user hand-pack count)
- [Rings](../../../data/__about/rings.md) — `ring_presets`, `validate_preset`
  (deferred import in `_add_custom_ring`)
- [Hands](../../../data/__about/hands.md) — `HAND_NAMES`, `hand_packs`,
  `user_hands_dir` (deferred imports)
- `PySide6.QtWidgets.QFileDialog` (deferred import in `_pick_hand`)

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_custom_ring_group()`, `_build_custom_hands_group()`;
  `result_settings()` reads `self._custom_rings` (mutated by
  `_add_custom_ring`)

## Classes

### _CustomArtSectionMixin
- `_build_custom_ring_group() -> QGroupBox`: the ring card builder
- `_rebuild_ring_slots()`: rebuilds the per-position jewel combos when the
  layout changes
- `_jewel_combo(position) -> QComboBox`: one grouped jewel-library
  dropdown for a ring position
- `_add_custom_ring()`: validates and appends a new ring card
- `_build_custom_hands_group() -> QGroupBox`: the hand-pack builder
- `_pick_hand(hand)`: browses for one hand's PNG
- `_add_custom_hands()`: validates, copies the three PNGs and writes
  `hands.json` for a new pack
