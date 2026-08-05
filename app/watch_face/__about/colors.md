# Watch Face Colors Section

**Script:** [Colors Section (script)](../colors.py)

## Purpose
Phase ④ (R-21..R-25): the Watch Face window's real Colors page,
replacing the placeholder — Ring tint, the Pointer palette chips, Umbra
coloring, Aura coloring (Colorful-off only), Hands/Indices free color,
Metal shades, and the Saturation sliders. LIVE-APPLY like every other
Watch Face section — no OK/Cancel buffer, the window rebuilds this page
fresh on every pick.

## Connections

### Uses
- [Tint Picker](tint_picker.md) — every color group's grids/custom
  row/label
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) —
  `palette.RING_TINT_GROUPS`/`PALETTE_PRESETS`/`pointer_arm_labels`/
  `effective_palette_style`, `constants.METAL_SHADE_NAMES`/
  `METAL_SHADE_TITLES`, the four Saturation range/step pairs

### Used by
- `app.watch_face.window` — registered as the Colors section's builder
- [Watch Controller](../../__about/controller.md) — every setter key
  this page calls (`ring_tint`, `palettes`, `umbra_tint_mode`,
  `umbra_tint`, `aura_off_tint_mode`, `aura_off_tint`, `hands_tint`,
  `letter_tint`, `metal_shade_gold`/`bronze`/`silver`,
  `pointer_saturation`, `ring_saturation`, `hands_saturation`,
  `umbra_saturation`) is wired in `_watch_face_setters()`,
  `test_watch_face_colors.py`'s static check pins it

## Design Decisions — DEBT recorded here, not shipped as a dead control
- **R-21's Outer/Inner ring-tint split** (hour markers vs minute
  track): the ring band is ONE baked plate
  (`render.layers.ring.RingLayer.paint`'s `spec.asset`) with no
  separable layer per element — the split needs new ring ART, not a
  UI hook.
- **R-24's Crown Text color** (and Phase 6's proposed Size slider for
  it): no "Crown Text" element exists anywhere in the render stack —
  `render/skin_geometry.py`, `render/layers/ring.py` and
  `skins/manifest.py` carry no such seat. The outer arc IS the Great
  Seal motto inscription, already wired through `letter_tint`/
  `ring_finish`.
- **R-25's Indices saturation as a separate slider**: `ring_saturation`
  already scales the ring plate AND its letters together, a UNIFIED
  target sealed by owner decree (Session 21-D, fix round E,
  2026-07-19) — splitting it apart reverses that decision without the
  owner asking.
- **R-25's Pointer (star-diamond) saturation**: fix round E
  (2026-07-19) explicitly REMOVED saturation scaling from the star
  diamonds by owner request (`render.skin_geometry.aura_palette_for`'s
  own docstring) — reintroducing it under a new name would be the same
  reversal.
- **R-23 naming note**: the task brief's "Elements ▸ Colorless" is not
  literal — the Visible menu carries a "Colorful" toggle instead
  (`settings.colorful`). The Aura group here gates on `not
  settings.colorful`, grayed out (never hidden) otherwise.
