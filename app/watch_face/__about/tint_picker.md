# Tint Picker (shared)

**Script:** [Tint Picker (script)](../tint_picker.py)

## Purpose
Shared tint-picker widgets — the round swatch, the titled preset grids
(`palette.RING_TINT_GROUPS`'s Lighter/Darker shape) and the "Custom…"
hue picker — extracted from `app.settings_dialog.colors_section` (Rule
#5, Watch Face Phase 4) so every color control that recolors through a
`#RRGGBB` hue (Ring tint, Umbra tint, Aura-off tint, Hands tint, Indices
tint) draws the SAME picker instead of five near-identical copies.

Stateless: every builder takes the CURRENT value and reads it fresh.
The live-apply `colors.py` needs nothing more — the Watch Face window
rebuilds the whole page on every pick. The OK/Cancel
`app.settings_dialog.colors_section` mixin keeps its own buffered
state and calls `repaint_selection` after a pick instead of rebuilding.

## Connections

### Uses
- [Config (folder)](../../../config/___config.md) — `dial.RING_TINT_SWATCH_PX`,
  `dial.RING_TINT_SWATCHES_PER_ROW`

### Used by
- [Watch Face Colors Section](colors.md) — every tint control on the
  Colors page
- [Colors Section](../../settings_dialog/__about/colors_section.md) —
  the Ring tint group's grids/custom row/label, refactored to delegate
  here instead of duplicating the logic

## Functions
- `round_swatch(chip, hue, size, selected)`: the Paint-style filled
  circle, ringed white when selected
- `preset_name(hue, groups)` / `tint_label_text(tr, hue, groups,
  none_label)`: the hover-matching label — preset name + hex, bare hex
  for a custom pick, or the "none" label
- `build_preset_grids(tr, groups, current, on_pick, none_swatch_hue)`:
  the titled grids; returns the layout plus the swatch list for
  `repaint_selection`
- `repaint_selection(swatches, current, none_swatch_hue)`: re-rings the
  active swatch in place (OK/Cancel callers only)
- `build_custom_row(tr, current, seed, on_pick, dialog_title)`: the
  "Custom…" button opening `QColorDialog`
