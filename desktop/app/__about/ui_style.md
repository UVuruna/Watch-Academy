# UI Style

**Script:** [UI Style (script)](../ui_style.py)

## Purpose
Shared modern gradient-pill button styling for the reader dialogs and
the Encyclopedia's look/finish switcher caption — vivid vertical
gradients, bold white text, rounded corners. Every color pair, font size
and padding comes from `config/defaults.py`/`config/palette.py`; hover
lightens and pressed darkens the same pair, computed rather than
hand-tuned per dialog.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `palette.UI_BUTTON_COLORS`
  role pairs, `encyclopedia_ui` font/radius/padding knobs,
  `palette.ENCYCLOPEDIA_FINISH_BORDER_COLORS` / `_GRADIENT`,
  `palette.LOOK_FILL_*`, `palette.THEME_COLORS`

### Used by
- [Encyclopedia Dialog](../encyclopedia/__about/dialog.md) — Home /
  Download / Previous / Next, the look arrows (`style_button`), the
  persistent look caption (`style_look_chip`)
- Every reader dialog in `app/` that carries a vivid button ([Time
  Travel](time_travel.md), [Report](report.md), the R5 mini windows)

## Functions

### `tooltip_wrap(text)`
ALG-3 HOVER GEOMETRY (Zubi fix round 2026-08-09): plain-text Qt
tooltips never wrap on their own — every tooltip longer than a line
routes through this hard-wrap (≤ 72 chars per line, paragraph breaks
kept). Callers: the Watch Face sections' tooltips (ring presets,
numerals combos, colors groups, opacity crown, themes slots).

### `uniform_width(buttons)`
ALG-5 UNIFORM SIBLINGS (same round): same-kind controls in one row
share the widest content's minimum width — 'OK' never shrinks beside
'Cancel'. Central call: `app.theme.style_dialog_buttons` (every
QDialogButtonBox); row-level calls in the reader pager, Report,
TimeTravel and the Observatory chart-pane pair.

### `style_button(button, role, small=False)`
Applies the role's gradient QSS to a `QPushButton`/`QToolButton` and
sets the pointing-hand cursor. `small=True` uses the compact
font/padding and its own smaller radius
(`UI_BUTTON_SMALL_RADIUS_PX` — ALG-6: a near-square small button may
carry only 15% of its shorter side). The role pairs were darkened in
the same round so bold white text holds ≥ 4.5:1 on every pair's
lightest stop (`palette.UI_BUTTON_COLORS`).

### `_qss(role, small)` / `_stops(top, bottom, factor=100)`
Build the stylesheet string — normal / hover (lighter) / pressed
(darker) states derived from the role's `(top, bottom)` gradient pair.

### `style_look_chip(label, look_label)`
The Encyclopedia's persistent look-caption FILL: looks up `look_label`
in `_LOOK_FILLS` (a solid hex for the metal finishes, a two-stop
`qlineargradient` for Colored/Atmosphere/Atmosphere · Night) and falls
back to a neutral dark chip for every kinship-group switcher the table
does not name. Text color is never hand-picked.

### `_LOOK_FILLS`
The fill palette table: `label -> hex | (hex, hex)`.

### `_yiq(hex_color)` / `_readable_text(fill)`
The standard YIQ perceived-brightness estimate, checked per gradient
stop — white text only when EVERY stop of a fill is dark enough to
carry it.
