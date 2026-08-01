# Theme

**Script:** [Theme (script)](../theme.py) · **Flow:** [diagram](../__flow/theme.md)

## Purpose
The Rule #16 POLISH round's single QSS stylesheet for dialog chrome —
dark-first surfaces, rounded cards, consistently restyled sliders /
spinboxes / combos / checkboxes / buttons / tabs — replacing the default
gray Qt widget look across the Settings dialog and (where it needs no
layout surgery) the reader dialogs. Every color and radius is a
`config/defaults.py`/`config/palette.py` token — this module only builds
the QSS string and applies it. Also owns the ONE dialog-sizing routine
every top-level dialog in `app/` calls.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `palette.THEME_COLORS`,
  `encyclopedia_ui.THEME_RADIUS_CONTROL_PX/CARD_PX/PILL_PX`,
  `defaults.DIALOG_A4_ASPECT_W/H`, `DIALOG_A4_HEIGHT_FRACTION`,
  `DIALOG_SQUARE_HEIGHT_FRACTION`

### Used by
Every dialog in `app/` — [Settings Dialog](../settings_dialog/__about/dialog.md),
[Time Travel](time_travel.md), [Report](report.md), [Design
Window](design_window.md), [Pointer Theme](pointer_theme.md), [Slot
Theme](slot_theme.md), [Encyclopedia Dialog](../encyclopedia/__about/dialog.md),
[Observatory](observatory.md) — for `apply_theme`; the four A4/square
callers additionally use `size_to_screen`

## Functions

### `apply_theme(widget)`
Sets the module's QSS string as `widget`'s stylesheet; QSS cascades to
every descendant, so one call in a dialog's `__init__` covers the whole
widget tree.

### `size_to_screen(dialog, aspect_w, aspect_h, height_fraction, min_width=0)`
The OPENING SIZE routine every top-level dialog calls: resizes and
centers `dialog` to the `aspect_w:aspect_h` shape at `height_fraction`
of the active screen's available height. `min_width` is a per-dialog
content-width floor that wins over the aspect-derived width when it is
larger ("whichever is larger wins") — only the WIDTH grows to cover it,
the HEIGHT always stays the requested fraction exactly. The whole result
clamps to the screen. Reads the screen through the dialog's window
HANDLE rather than `QWidget.screen()` — pre-show there is none (falls
back to the primary screen, which is what `screen()` would have returned
anyway); post-show the handle's screen is the real, multi-monitor
correct one (`QWidget.screen()` intermittently walked a dead C++
`QScreen` under the offscreen test platform, a hard access violation no
`except` can catch).

### `style_dialog_buttons(box)`
Tags a `QDialogButtonBox`'s OK button `objectName="primaryButton"`
(solid accent fill) and every other standard button
`objectName="secondaryButton"` (outline) — QSS alone cannot select "the
OK button" out of the box by role.

## Design Decisions
- Palette follows the monorepo [DESIGN.md](../../../../DESIGN.md) (Rule
  #16): dark surfaces stepped by elevation, one accent hue (the dial's
  own gold), 8–14px corner radii, borders as low-opacity white rather
  than a flat gray line.
- [UI Style](ui_style.md)'s vivid gradient buttons (Encyclopedia,
  Time Travel, Report) are UNCHANGED by this stylesheet — it governs the
  surfaces and form controls those dialogs don't already own an opinion
  on, plus every dialog's own OK/Cancel/neutral buttons.
