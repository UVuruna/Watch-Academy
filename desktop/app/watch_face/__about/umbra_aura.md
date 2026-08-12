# Umbra & Aura Section

**Script:** [Umbra & Aura Section (script)](../umbra_aura.py) · **Flow:** [diagram](../__flow/umbra_aura.md)

## Purpose
The Watch Face window's Umbra & Aura page: the umbra FORM pills
(Fine/Coarse/Gradient) and the CONTRAST pills, moved verbatim from
`design_window.DesignDialog._umbra_tab`. Coloring lives in the Colors
section and opacity in the Opacity section — both later phases; this
page carries only the form/contrast choice, matching its narrower name.

## Connections

### Uses
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) —
  `constants.UMBRA_CONTRAST_VARIANTS`

### Used by
- `app.watch_face.window` — registered as the Umbra & Aura section's
  builder
