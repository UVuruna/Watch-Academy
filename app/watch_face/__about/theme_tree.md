# Content Tree

**Script:** [Content Tree (script)](../theme_tree.py) · **Flow:** [diagram](../__flow/theme_tree.md)

## Purpose
The Watch Face window's CONTENT DECISION TREE (R-17/R-18) — never a
flat dump of every theme. A breadcrumb-navigated hierarchy:

- **Level 1 — content kind:** Weekday themes / Complications /
  Astrology / Ascendant / Chinese zodiac. On a SUBDIAL (a real,
  enabled slot) every kind is offered (owner verdict P-4). At FULL
  FACE the active pointer's carried kinds
  (`constants.watch_face_kinds`) gate this list down to "Weekday
  themes" alone or nothing (see themes.md's Design Decisions for why
  weekday is the only kind wired here at all).
- **Level 2 (Weekday only) — kinship group:** Planets plus the
  existing groups (`app.weekday_theme_grid.weekday_group_titles`).
- **Level 3 (Weekday only) — the group's own theme tiles,** the
  pointer's default theme starred.

Complications' Level 2 is `constants.SLOT_COMPLICATION_TITLES`'
entries; Astrology/Ascendant/Chinese zodiac's Level 2 is their style
pills (`constants.ZODIAC_SLOT_STYLES`/`CHINESE_SLOT_STYLES`) — all
three ported verbatim from `app.slot_theme.SlotThemeDialog._style_tab`.

## Connections

### Uses
- [Weekday Theme Grid](../../__about/weekday_theme_grid.md) —
  `weekday_group_titles`, `build_weekday_group_grid`,
  `build_weekday_theme_tiles`
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) —
  `constants.SLOT_COMPLICATION_TITLES`, `ZODIAC_SLOT_STYLES`,
  `CHINESE_SLOT_STYLES`, `watch_face_kinds`
- [Slot Theme](../../__about/slot_theme.md) — `SlotDescriptor` (the
  data shape both windows read; imported, never redefined)

### Used by
- [Themes & Slots Section](themes.md) — the whole tree, for whichever
  descriptor is active

## Functions

### `build(descriptor, full_face, pointer, pointer_shape, tr) -> QWidget`
The tree's entry point. `full_face=True` filters Level 1 through
`constants.watch_face_kinds(pointer, pointer_shape)`; `False` (a real
subdial) offers every kind unfiltered.

### `reset_navigation()`
Clears the module-level breadcrumb state — test-only; production code
never calls it (state is meant to survive across the window's live-
apply rebuilds, see Design Decisions).

## Design Decisions
- **Breadcrumb state is module-level** (`_nav`), for the identical
  reason `themes.py` keeps its active-slot index at module level: the
  window recreates this page's whole widget tree on every unrelated
  live-apply pick, so surviving that (but not needing to survive an
  app restart — this is pure UI navigation, never saved to disk) means
  living above the widget instance. A drill-down click never touches a
  setting, so it never triggers that outer rebuild by itself — the
  in-widget `_build()` call it fires handles its own redraw.
- **No second theme list.** Level 2/3 read
  `weekday_group_titles`/`build_weekday_group_grid`/
  `build_weekday_theme_tiles` — new SHAPES over `pantheon.
  WEEKDAY_MENU_TOP`/`WEEKDAY_MENU_GROUPS`, the same data
  `build_weekday_theme_grid`'s flat gallery already reads.
