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
  this page calls (`ring_tint`, `ring_tint_inner`, `palettes`,
  `umbra_tint_mode`, `umbra_tint`, `aura_off_tint_mode`, `aura_off_tint`,
  `hands_tint`, `letter_tint`, `motto_tint`,
  `metal_shade_gold`/`bronze`/`silver`, `pointer_saturation`,
  `ring_saturation`, `hands_saturation`, `umbra_saturation`) is wired in
  `_watch_face_setters()`, plus the two data PROVIDERS
  `ring_has_motto`/`ring_has_split_art` the Crown Text/Inner-tint rows
  read to grey themselves out; `test_watch_face_colors.py`'s static
  check pins it

## Design Decisions
- **CORRECTION (owner 2026-08-05, LOUD): the two items below were
  WRONGLY declared impossible — the owner's own art and words proved
  it.** R-21's Outer/Inner ring-tint split IS built: the owner's split
  ring art (`assets/instrument/ring/outter/`+`inner/`, untracked) is
  composed by `render.layers.ring.RingLayer._draw_split_plate`, each
  band with its OWN tint (`ring_tint`/`ring_tint_inner`); the "Inner
  (Minute track)" row below greys out with a tooltip whenever the
  active preset hasn't opted in or the art isn't on disk
  (`setters["ring_has_split_art"]`) — no bundled preset opts in yet
  (`RingSpec.use_split_art` defaults False), so today's rendering is
  unchanged until the owner reviews and flips a preset. R-24's Crown
  Text color IS built too: the outer arc IS the Great Seal motto
  inscription (`RingSpec.motto`) — it always had a seat, just no
  control; `motto_tint` (this section) and `motto_scale`/`motto_alpha`
  (Size/Opacity sections) now read it independently of
  `letter_tint`/`ring_letter_scale`. See `skins.manifest.
  SkinDefinition`'s Crown Text fields for the full design note.
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
