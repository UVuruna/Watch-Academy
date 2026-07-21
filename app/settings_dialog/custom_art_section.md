# Custom Art Section

**Script:** [Custom Art Section (script)](custom_art_section.py)

## Purpose

`_CustomArtSectionMixin` — the **Custom art** nav section: the Custom
ring and Custom hands builders. Plain-Python mixin (no base class);
composed onto [Settings Dialog](dialog.md)'s `QDialog` shell.

## The groups

- **Custom ring** — the ring card builder: a layout (Flame /
  Chalice / Seal), a library letter per position and a unique name;
  the per-position dropdown is GROUPED (owner spec 2026-07-11) into
  Latin (the full A–Z), Greek, Numbers (1–10, 20 — growing) and
  Symbols sections with unselectable headers
  (`constants.RING_LETTER_GROUPS`) — a NUMBER only fits its own hour
  (owner rule 2026-07-12), so the Numbers section offers at most the
  position's own number. Add validates the card
  (`data.rings.validate_preset`) and OK persists it (it appears under
  Theme ▸ Ring).
- **Custom hands** (owner spec 2026-07-12) — the hand-pack builder:
  three PNGs pointing UP, a pivot per hand (x from the left, 'center'
  by default; y in pixels from the bottom), a bottom-up z-order and a
  unique name. Add writes the pack folder immediately (files, not
  settings, via `data.hands.user_hands_dir`) — it appears under Design
  ▸ Hands.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.
  RING_LAYOUTS`/`RING_LETTER_GROUPS`, `defaults` (`defaults.paths.
  assets_dir()` for the bundled-vs-user hand-pack count)
- `data.rings` — `ring_presets`, `validate_preset` (deferred import in
  `_add_custom_ring`)
- [Hands](../../data/hands.md) — `HAND_NAMES`, `hand_packs`,
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
- `_rebuild_ring_slots()`: rebuilds the per-position letter combos when
  the layout changes
- `_letter_combo(position) -> QComboBox`: one grouped letter-library
  dropdown for a ring position
- `_add_custom_ring()`: validates and appends a new ring card
- `_build_custom_hands_group() -> QGroupBox`: the hand-pack builder
- `_pick_hand(hand)`: browses for one hand's PNG
- `_add_custom_hands()`: validates, copies the three PNGs and writes
  `hands.json` for a new pack
