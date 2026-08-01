# Home Screen

**Script:** [Home Screen (script)](../home.py) · **Flow:** [diagram](../__flow/home.md)

## Purpose
Level one — the NINE WHOLES (Session 35, 2026-07-29, regrouped from the
original six) in a 3x3 grid. The owner's law is absolute (*"Prvi ekran
nema scroll. uvek sve staje u window"*), so this screen owns **no scroll
area at all** and measures its cards from the widget's own width AND
height.

Each card carries its whole's Rose (or, for the ninth, Moon-silver)
accent, a plate, the whole's about line and a live count, properly
pluralized (`5 themes · 52 pages`, `1 theme · 1 page`).

## Connections

### Uses
- [Card](cards.md) — `CardGrid` and `mosaic_pixmap`
- [Encyclopedia Repository](../../../data/__about/encyclopedia.md) — `whole(key)`, the about text
- [Encyclopedia Tree (config)](../../../config/__about/encyclopedia_tree.md) — `WHOLES`, the nine wholes and their accents

### Used by
- [Encyclopedia Dialog](dialog.md) — the first of the three stacked screens

## Classes

### HomeScreen
`QWidget`, `opened = Signal(str)`.

- `__init__(topics, encyclopedia, tr)`: builds one `CardGrid` sized
  `encyclopedia_ui.ENCYCLOPEDIA_HOME_COLUMNS` and fills it once from
  `tree.WHOLES`; both the grid and this widget declare
  `QSizePolicy.Ignored` on purpose (see Design Decisions)
- `_plate(whole)`: the owner's own hand-drawn plate at
  `ENCYCLOPEDIA_WHOLE_ART_DIR/<key>.png` when it exists, else
  `mosaic_pixmap` of the whole's own theme icons
- `_spec(whole)`: the card spec dict (`key`, `title`, `about`, `plate`,
  `footer`, `accent`) — `footer` is the pluralized theme/page count
- `fit(zoom=None)`: re-measures the grid from `self.width()` /
  `self.height()`
- `resizeEvent(event)`: calls `fit()` on every resize

## Design Decisions

**The grid never dictates a minimum** (root cause fixed 2026-07-29,
owner bug, Rule #25). `fit()` measures the cards FROM the viewport and
pins them with `setFixedWidth`/`setFixedHeight` — which is also how Qt
declares a MINIMUM. Because this screen owns no scroll area, that
minimum would go straight up into the dialog: every enlargement would
stick and the window could never be dragged back down. The grid's own
size hints are meaningless BY DESIGN here — the viewport is the INPUT,
not the output — so `_grid` and `HomeScreen` both declare
`QSizePolicy.Ignored`, and the only floor left is the dialog's own
`ENCYCLOPEDIA_MIN_WIDTH_PX` x `ENCYCLOPEDIA_MIN_HEIGHT_PX` (the owner's
1280x720 opening screen). Pinned by
`tests/test_encyclopedia_tree.py::test_growing_the_window_never_raises_its_own_minimum`.

**The plate is computed, not generated** (root Rule #19): a category
image is derivable, so it is never generated — a hand-drawn plate always
wins, the mosaic is the floor, not a ceiling.
