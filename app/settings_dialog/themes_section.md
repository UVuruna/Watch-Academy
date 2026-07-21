# Themes Section

**Script:** [Themes Section (script)](themes_section.py)

## Purpose

`_ThemesSectionMixin` — the **Themes** nav section: Theme rotation,
Artwork, Subdial plate and Metal shades groups. Plain-Python mixin (no
base class); composed onto [Settings Dialog](dialog.md)'s `QDialog`
shell.

## The groups

- **Theme rotation** (owner spec 2026-07-12) — cycle the CHECKED
  weekday themes on a timer: a GROUP dropdown (owner 2026-07-14) picks
  None (the canon — no rotation), one kinship family from the Weekday
  menu grouping, or Custom (the checkbox grid) — no separate Enabled
  checkbox, None IS off. Plus the per-theme METAL each bronze-plate
  theme wears (owner 2026-07-12; colored is the canon default
  2026-07-14) — per theme, or one "Follow ring color" checkbox; only
  the metal themes INSIDE the current rotation selection show their
  combos (owner 2026-07-14).
- **Artwork** (owner 2026-07-14) — the ART SOURCE pick (Gemini vs
  ChatGPT generations): one combo switches every plate, emblem and
  badge; files missing in the chosen source fall back to the other.
- **Subdial plate** (owner decree 2026-07-21, Rsub round — sits right
  beside Artwork, though it is deliberately INDEPENDENT of the art
  source pick: `assets/subdial/` is not a Gemini/ChatGPT family) — one
  combo, five entries labeled "1"/"2"/"3"/"4"/"Solo"
  (`constants.SUBDIAL_SET_TITLES`) over `constants.SUBDIAL_SETS`,
  restored from `Settings.subdial_set` (default "set1") and applied via
  `config.paths.set_subdial_set` in `app.controller.
  apply_display_settings` — mirrors the Artwork combo's own plumbing
  exactly. The active letter finish (Design ▸ tray menu, `ring_finish`)
  still decides which color draws within the chosen set; sets 1-4 carry
  three hand-drawn finishes each, "solo" carries one hand-drawn silver
  with gold/bronze derived live ([Asset Variants]
  (../../render/asset_variants.md)`.subdial_plate_file`).
- **Metal shades** (R8a round, owner spec 2026-07-21 night — the redo
  after the adaptive-percentile attempt was reverted for flattening
  relief) — three combos, one per metal (gold five shades, bronze
  three, silver three; `constants.METAL_SHADE_NAMES`/
  `METAL_SHADE_TITLES`), restored from `Settings.metal_shade_gold/
  _bronze/_silver` and applied via `config.paths.set_metal_shade` in
  `app.controller.apply_display_settings` — same plumbing pattern as
  Subdial plate. The picked shade recolors ring letters everywhere
  ([Asset Recolor](../../render/asset_recolor.md)`.letter_metal_file`)
  and badge medallions wherever gold/silver is chosen
  (`AssetCache._metal_swapped`) — bronze medallions stay the art as
  drawn regardless of the bronze shade pick (out of this round's
  scope; the owner's two complaints were badge GOLD and letter
  BRONZE, never badge bronze).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `defaults.
  WEEKDAY_MENU_GROUPS`/`WEEKDAY_THEME_TITLES`, `constants.
  METAL_THEMES`/`theme_metals`/`ART_SOURCES`/`ART_SOURCE_TITLES`/
  `SUBDIAL_SETS`/`SUBDIAL_SET_TITLES`/`METAL_SHADE_NAMES`/
  `METAL_SHADE_TITLES`
- [Asset Variants](../../render/asset_variants.md),
  [Asset Recolor](../../render/asset_recolor.md) — the derivation the
  Subdial plate / Metal shades pickers feed (applied by the controller,
  not called directly here)

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_theme_rotation_group()`, `_build_artwork_group()`,
  `_build_subdial_set_group()`, `_build_metal_shade_group()`;
  `result_settings()` reads `self._rotation_group`/`_metal_combos`/
  `_metal_follow_ring`/`_art_source_combo`/`_subdial_set_combo`/
  `_metal_shade_combos`

## Classes

### _ThemesSectionMixin
- `_build_theme_rotation_group() -> QGroupBox`: the rotation group
  dropdown/checkbox grid + per-theme metal row
- `_rotation_selection() -> tuple[str, ...]`: the themes the CURRENT
  dialog state would rotate
- `_refresh_rotation_ui()`: shows the checkbox grid only for Custom,
  each metal combo only while its theme is in the selection
- `_build_artwork_group() -> QGroupBox`: the art-source combo
- `_build_subdial_set_group() -> QGroupBox`: the subdial-set combo
- `_build_metal_shade_group() -> QGroupBox`: the three metal-shade combos
