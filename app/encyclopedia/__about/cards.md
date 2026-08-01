# Card

**Script:** [Card (script)](../cards.py) · **Flow:** [diagram](../__flow/cards.md)

## Purpose
ONE card component for both gallery levels — plate, title, about line,
footer stat, and the whole's accent on its edge — plus the `CardGrid`
that lays cards in centered, wrapping rows, and the free functions that
make the no-X-scroll law and the whole-plate mosaic arithmetic instead
of guesswork.

## Connections

### Uses
- [Asset Variants](../../../render/__about/asset_variants.md) — `scaled_variant_file`, the pre-warmed downscale a card icon decodes from

### Used by
- [Home Screen](home.md), [Theme Screen](themes.md) — both galleries share this one card language (Rule #5)

## Functions

- `row_content_width(card_width, columns) -> int`: the pixel width one
  full row of `columns` cards needs (cards + gaps + grid margins)
- `card_width_for(viewport_width, columns) -> int`: the exact inverse —
  the widest card `columns` of which still fit inside `viewport_width`,
  floored at `ENCYCLOPEDIA_CARD_MIN_WIDTH_PX`
- `card_pixmap(icon) -> QPixmap`: one plate, decoded from the pre-warmed
  downscale (`build=False` — never builds one on the GUI thread); a
  missing or `None` icon returns a null pixmap (graceful-absent)
- `mosaic_pixmap(icons) -> QPixmap`: a whole's tile COMPUTED from up to
  four of its own theme plates, 2x2 (root Rule #19 — never a generated
  category image)

## Classes

### Card
`QFrame`, `clicked = Signal(str)`. One clickable tile: plate, title,
about, footer — the whole's accent hue tints the hover wash and border.

- `__init__(key, title, about, plate, footer, accent)`
- `fit(width, height, font_px)`: sizes the card; `height=None` lets it
  keep its natural height (the theme grid, which scrolls), a given
  height pins it (the home grid, which may not)
- `enterEvent` / `leaveEvent`: swap the hover paint
- `mouseReleaseEvent`: emits `clicked(key)` on a left click inside the frame

### CardGrid
`QWidget`, `opened = Signal(str)`. Rows of cards, each row centered as
its own block, wrapping into the next row instead of spilling sideways.

- `__init__(columns)`
- `cards` (property): the live `Card` list
- `set_cards(specs)`: tears down and rebuilds every row from a list of
  spec dicts (`key`, `title`, `about`, `plate`, `footer`, `accent`)
- `fit(viewport_width, viewport_height, zoom=1.0)`: re-measures every
  card; `viewport_height` given (home) pins the row height so the grid
  never scrolls, `None` (themes) lets rows take their natural height

## Design Decisions
- **The width pair is one formula, two directions** (Rule #5):
  `row_content_width` and `card_width_for` are exact inverses so the
  dialog's minimum width and the live per-resize card size can never
  drift apart — the old gallery grew a horizontal scrollbar twice
  because the two directions used to be computed separately.
- **Rows center as blocks** — a stretch on both sides of every row, so
  a short trailing row centers exactly like a full one.
- **A missing plate is not an error** — the card shows its title alone,
  the graceful-absent contract every gallery tile has always had.
- **The no-X-scroll law is enforced twice on purpose**: the geometry
  here can never produce a row wider than its viewport, AND the screens
  that own a scroll area (themes) switch its horizontal bar off too.
