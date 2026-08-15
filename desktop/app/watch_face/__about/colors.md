# Watch Face Colors Section

**Script:** [Colors Section (script)](../colors.py)

## Purpose
Phase ④ (R-21..R-25): the Watch Face window's real Colors page,
replacing the placeholder — Ring tint, the Pointer palette chips, Umbra
coloring, Aura coloring (Colorful-off only), Hands/Jewels free color,
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
  this page calls (`ring_tint`, `ring_tint_inner`, `palettes`,
  `umbra_tint_mode`, `umbra_tint`, `aura_off_tint_mode`, `aura_off_tint`,
  `hands_tint`, `jewels_tint`, `crown_text_tint`,
  `metal_shade_gold`/`bronze`/`silver`, `pointer_saturation`,
  `ring_saturation`, `hands_saturation`, `umbra_saturation`) is wired in
  `_watch_face_setters()`, plus the data PROVIDER `ring_has_crown_text` the
  Crown Text row reads to grey itself out (the Inner-tint row is always
  live now — THE COMPOSITIONAL RING MODEL, owner decree 2026-08-05);
  `test_watch_face_colors.py`'s static check pins it

## Design Decisions

- **METAL SHADES ARE ROUNDELS** (owner order 2026-08-15). The group
  used to be three `QComboBox` rows — a dropdown can name a shade but
  never show it, and he asked for "a roundel that simulates a metal
  plate with its sheen and shows how each option looks". It is three
  card groups now, Gold / Silver / Bronze in his order side by side in
  one row, each holding its shades as `OptionCard`s under the ordinary
  card grammar (image, text, hover blurb, resize).
  - Everything the roundel draws is READ from that shade's own ramp in
    `recolor/presets/metals.json` (`thumbs.metal_roundel_icon` →
    `_shade_ramp`): a corner-to-corner sweep through the real stops,
    the rim in the darkest stop, the specular crescent in the lightest.
    So two shades differ on this tile exactly as much as they differ on
    the dial. A shade with no ramp draws no tile rather than a
    stand-in, and a tooth fails if any registered shade loses its ramp.
  - THREE groups, not one of eleven cards: the shades of a metal are
    alternatives to each other and not to the other metals' — which is
    what the three separate settings (`metal_shade_gold` /
    `_silver` / `_bronze`) already say. One flat group would read as
    eleven mutually exclusive picks.
  - The row aligns its three boxes to a common TOP and lets them share
    a height. A `Maximum` vertical policy was tried and reverted the
    same day (proof shots): it does end each column at its content, but
    with the row's AlignTop it dropped the two short columns below
    Gold's top edge — worse than the even bottoms it was meant to fix.


- **CORRECTION (owner 2026-08-05, LOUD): the two items below were
  WRONGLY declared impossible — the owner's own art and words proved
  it.** R-21's Outer/Inner ring-tint split IS built, and THE
  COMPOSITIONAL RING MODEL (same decree) made it the ONLY ring render
  path: `render.layers.ring.RingLayer._draw_bands` composes the owner's
  outer/inner art (`assets/instrument/ring/outter/`+`inner/`)
  UNCONDITIONALLY, each band with its OWN tint
  (`ring_tint`/`ring_tint_inner`) — the "Inner (Minute track)" row
  below is always live now, no more disk-presence gate. R-24's Crown
  Text color IS built too: the outer arc IS the Great Seal crown text
  inscription (`RingSpec.crown_text`) — it always had a seat, just no
  control; `crown_text_tint` (this section) and `crown_text_scale`/`crown_text_alpha`
  (Size/Opacity sections) now read it independently of
  `jewels_tint`/`ring_jewels_scale`. See `skins.manifest.
  SkinDefinition`'s Crown Text fields for the full design note.
- **R-25's Jewels saturation as a separate slider**: `ring_saturation`
  already scales the ring plate AND its jewels together, a UNIFIED
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
