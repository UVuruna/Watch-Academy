# Theme

**Script:** [Theme (script)](theme.py)

## Purpose

The Rule #16 POLISH round's single QSS stylesheet for dialog chrome —
dark-first surfaces, rounded cards, and consistently restyled sliders /
spinboxes / combos / checkboxes / buttons — replacing the default gray
Qt widget look across the Settings dialog and (where it needs no
layout surgery) the reader dialogs. Every color and radius is a
`config/defaults.py` token (`THEME_COLORS`,
`THEME_RADIUS_CONTROL_PX/CARD_PX/PILL_PX`) — this module only builds
the QSS string and applies it; no hex literal lives here.

Palette follows monorepo [DESIGN.md](../../../DESIGN.md) (Rule #16): dark
surfaces stepped by elevation, one accent hue (the dial's own gold),
8–14px corner radii, borders as low-opacity white rather than a flat
gray line. `app/ui_style.py`'s vivid gradient buttons (Encyclopedia /
Guide) are UNCHANGED — this stylesheet governs the surfaces and form
controls those dialogs don't already own an opinion on, and the
Settings dialog's own buttons (OK/Cancel, "Default", "Skin default").

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `THEME_COLORS`, `THEME_RADIUS_*` in `defaults.py`.

### Used by
- [Settings Dialog](settings_dialog.md) — nav column, group-box cards,
  every slider/combo/spinbox/checkbox, OK/Cancel/Default buttons.
- [Encyclopedia Dialog](encyclopedia.md), [Guide Dialog](guide.md),
  [Time Travel Dialog](time_travel.md), [Report Dialog](report.md) —
  base surface + (Time Travel only) its QComboBox/QSpinBox controls;
  their own `ui_style.style_button` gradients and per-label accents
  are untouched.

## Functions

### `apply_theme(widget)`
Sets the module's QSS string as `widget`'s stylesheet. Qt cascades QSS
to every descendant, so calling this once in a dialog's `__init__`
covers the whole widget tree — no per-child styling needed for the
controls this theme covers.

### `style_dialog_buttons(box: QDialogButtonBox)`
Tags the box's OK button `objectName="primaryButton"` (solid accent
fill) and every other standard button `objectName="secondaryButton"`
(outline) so the shared stylesheet can tell them apart — `QSS` alone
cannot select "the OK button" out of a `QDialogButtonBox` by role.
