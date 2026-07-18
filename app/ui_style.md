# UI Style

**Script:** [UI Style (script)](ui_style.py)

## Purpose

Shared MODERN button styling for the reader dialogs (owner 2026-07-14:
"veći, upečatljiviji, življih boja — ne kao app iz 1990-e"): vivid
vertical-gradient pills with bold white text and rounded corners.
Every color pair, font size and padding is a `config/defaults.py`
knob; hover lightens and pressed darkens the same pair, computed —
never hardcoded per dialog.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `UI_BUTTON_COLORS` role pairs,
  font/radius/padding knobs.

### Used by
- [Encyclopedia Dialog](encyclopedia.md) — Home / Download / Previous
  / Next and the look arrows.
- [Guide Dialog](guide.md) — Previous / Next pager.

## Functions

### `style_button(button, role, small=False)`
Applies the role's gradient QSS to a `QPushButton`/`QToolButton` and
sets the pointing-hand cursor. `small=True` uses the compact font and
padding (the per-entry look arrows).

### `_qss(role, small)`
Builds the stylesheet string: normal / hover (lighter) / pressed
(darker) states from the role's `(top, bottom)` gradient pair.
