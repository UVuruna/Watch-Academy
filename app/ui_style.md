# UI Style

**Script:** [UI Style (script)](ui_style.py)

## Purpose

Shared MODERN button styling for the reader dialogs (owner 2026-07-14:
"veći, upečatljiviji, življih boja — ne kao app iz 1990-e"): vivid
vertical-gradient pills with bold white text and rounded corners.
Every color pair, font size and padding is a `config/defaults.py`
knob; hover lightens and pressed darkens the same pair, computed —
never hardcoded per dialog.

A second recipe, `style_look_chip` (owner round R8b item 4: "jel me
stvarno zezas da ne mozes da napravis gradient button" — the R3
border-only frame this replaces never rendered as a real gradient; QSS
has no `border-color` gradient primitive, only a `background` one),
dresses the Encyclopedia's look/finish switcher CAPTION with a FILLED
pill instead — metal finishes, the continents globe looks and every
kinship-group switcher all read through this ONE function.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `UI_BUTTON_COLORS` role pairs,
  font/radius/padding knobs, `ENCYCLOPEDIA_FINISH_BORDER_COLORS` /
  `ENCYCLOPEDIA_FINISH_GRADIENT` (the metal/Colored fills), `THEME_COLORS`
  (the neutral chip and the two text-contrast anchors).

### Used by
- [Encyclopedia Dialog](encyclopedia.md) — Home / Download / Previous
  / Next, the look arrows (`style_button`), and the persistent look
  caption (`style_look_chip`).
- [Guide Dialog](guide.md) — Previous / Next pager.

## Functions

### `style_button(button, role, small=False)`
Applies the role's gradient QSS to a `QPushButton`/`QToolButton` and
sets the pointing-hand cursor. `small=True` uses the compact font and
padding (the per-entry look arrows).

### `_qss(role, small)`
Builds the stylesheet string: normal / hover (lighter) / pressed
(darker) states from the role's `(top, bottom)` gradient pair.

### `style_look_chip(label, look_label)`
The Encyclopedia's persistent look-caption FILL (owner round R8b item
4, supersedes the retired `style_finish_frame` border-only chip):
looks up `look_label` in `_LOOK_FILLS` — a solid hex for Bronze/Gold/
Silver/Clean/Clean · Night, a two-stop horizontal `qlineargradient` for
Colored/Atmosphere/Atmosphere · Night — and falls back to a neutral
dark chip (`THEME_COLORS["surface_3"]`) for every kinship-group
switcher the table doesn't name (Planets/Signs/Art, the Week's Canon/
Gods/Religions/Themes/Animals, Astrology's Logo & Constellation/
Colored/Sign). Text color is never hand-picked.

### `_LOOK_FILLS`
The fill palette table: `label -> hex | (hex, hex)`. Bronze/Gold/
Silver reuse `defaults.ENCYCLOPEDIA_FINISH_BORDER_COLORS`; Colored
reuses `defaults.ENCYCLOPEDIA_FINISH_GRADIENT` (Rule #5 — the SAME
blue→red sweep, now filling instead of framing). The four continents
globe looks are new this round, realizing the owner's own four
suggested words as one coherent family: Atmosphere leads sky-blue and
ends warm gold (the DAY pairing, `#4FC3F7` → `#FFB74D`); Atmosphere ·
Night leads navy and ends the SAME blue Colored uses (`#0B1F3A` →
`#3B5FE0`, family cohesion); Clean is a solid ocean teal by day
(`#0E6B8C`) and the SAME navy by night (`#0B1F3A`).

### `_yiq(hex_color)`
The standard YIQ perceived-brightness estimate (0–255) for one hex
color — the ONE formula every fill's text-contrast decision reads.

### `_readable_text(fill)`
White text (`THEME_COLORS["text_primary"]`) when EVERY stop of `fill`
is dark enough by YIQ; the dark anchor (`THEME_COLORS["surface_0"]`)
otherwise — checked per-stop so a two-tone gradient only gets white
text when both ends can actually carry it.
