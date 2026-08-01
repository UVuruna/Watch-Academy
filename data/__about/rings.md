# Ring Presets

**Script:** [Ring Presets (script)](../rings.py) ·
**Flow:** [diagram](../__flow/rings.md)

## Purpose

Loads the ring preset "cards" — bundled ones from
`Database/ring_presets.json` plus the user's CUSTOM cards from
settings. One card = one dial styling: `{name, positions, letters}`,
plus the optional fields below. The card's `positions` signature
(as a frozenset) resolves the LAYOUT from `constants.RING_LAYOUTS` —
the ring face with matching gaps and the metal rules. Validation is
loud (Rule #1): an unknown position set, an unknown glyph, a count
mismatch or a duplicate name raises naming the offending card.

### Optional card fields (all validated by `validate_preset`)

- **`thematic`** — the card's own color under the Thematic ring finish;
  must be one of `constants.METAL_SHADE_NAMES["thematic"]`.
- **`triangle`** — a 3-position override of the seal layout's metal
  triangle (splits a 6-letter preset into two 3-letter metal groups);
  only valid when the resolved layout is `"seal"`.
- **`legend`** — `position → {name, reading}`, the per-letter hover
  legend text.
- **`motto`** — a list of Great Seal motto entries; see
  [flow](../__flow/rings.md) for the two mutually exclusive forms
  (pinned / centered) and their angle-solving.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `constants.RING_LAYOUTS`, `constants.RING_LETTER_FILES`,
  `constants.METAL_SHADE_NAMES`, `paths.database_dir()`
- [Motto](../../core/__about/motto.md) — `motto_glyph_angles`,
  `centered_word_angles`, `_occurrence_index` — the per-glyph angle
  solve for the optional `motto` field

### Used by
- [Watch Controller](../../app/__about/controller.md) — `build_skin` resolves
  the active preset
- [Settings Store](../../app/__about/settings_store.md) — imports
  `ring_presets` and `validate_preset` to check a stored custom card
- [Design Window](../../app/__about/design_window.md) — lists loaded preset
  names
- [Custom Art Section](../../app/settings_dialog/__about/custom_art_section.md)
  — `validate_preset` checks the custom-ring builder's input

## Functions

- `ring_presets(custom=())`: `name → validated card` for every bundled
  + custom preset (`{name, positions, letters, layout, triangle,
  legend, motto, thematic}`); a duplicated name raises.
- `validate_preset(entry)`: the shared card validator — see
  [flow](../__flow/rings.md).
- `_validate_motto(name, raw, positions)` (private): the `motto`
  field's own validator and angle solver.
