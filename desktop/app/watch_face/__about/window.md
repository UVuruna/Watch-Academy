# Watch Face Window

**Script:** [Watch Face Window (script)](../window.py) · **Flow:** [diagram](../__flow/window.md)

## Purpose
The new consolidated visual-customization window (Phase ①+②, R-01):
a left `QListWidget` sidebar of eight sections beside a right
`QStackedWidget` page per section — replacing, over several phases, the
Design / Pointer Theme / Slot Theme windows and the Settings dialog's
Display/Colors groups. THIS PHASE wires five real sections (Pointer,
Ring, Hands, Umbra & Aura, Size) plus three placeholder pages (Themes &
Slots, Colors, Opacity) that simply read "Arrives in a later phase".

## Connections

### Uses
- [Rebuild](../../__about/rebuild.md) — `clear_layout`/`discard`, the ONE door a live rebuild throws widgets away through: `hide()` BEFORE `setParent(None)`, because an orphan QWidget IS a top-level window and a visible one flashes open at the centre of the screen (owner bug 2026-08-15, reported again 2026-08-16 because only half of it was fixed the first time)
- [Theme](../../__about/theme.md) — `apply_theme`, `size_to_screen`
- `app.watch_face.pointer` / `.ring` / `.hands` / `.umbra_aura` / `.size`
  — one builder module per real section
- [Config (folder)](../../../config/___config.md) — `constants.APP_NAME`,
  `defaults.DIALOG_SQUARE_HEIGHT_FRACTION`, `defaults.SETTINGS_NAV_WIDTH_PX`

### Used by
- [Watch Controller](../../__about/controller.md) — `_open_watch_face`
  (non-modal, one live instance, raised on a second open);
  `_watch_face_setters()` wraps every setter so a pick both applies AND
  refreshes the open window

## Classes

### WatchFaceDialog(QDialog)
Non-modal, LIVE-APPLY — every section's pick calls its setter
immediately; there is nothing to commit, no OK/Cancel.

#### Methods
- `refresh(settings, setters)`: re-supplies the live settings after a
  pick applies, then rebuilds — called by the controller
- `_build()`: rebuilds the sidebar + stack from the `_SECTIONS` registry
  on every pick, KEEPING the previously selected row (the SAME
  "a fresh container reopens at row 0" fix `design_window.DesignDialog
  ._build` already carries for its `QTabWidget`)
- `_capture_scrolls()` / `_restore_scrolls(offsets)`: the per-page scroll
  offsets carried across that rebuild

## THE NO-MOVEMENT DECREE (owner 2026-08-10, third report)
**A settings pick — here or in the Settings dialog — may change the WATCH
and nothing else.** Not the section, not the scroll position, not which
side of the window holds the caret. The live-apply rebuild broke all
three at once, because it destroys the very widget the owner clicked:
the fresh `QListWidget` reopened at row 0 (fixed earlier), every fresh
`QScrollArea` reopened at the top, and the rebuilt sidebar's default
StrongFocus took the caret. So `_build` now carries the row, restores
every page's scroll offset TWICE (once inline, once queued — a
scrollbar's range is still 0 before the layout pass, so the inline call
alone would clamp to the top), and gives the sidebar `TabFocus` so it is
reachable but never grabs. Teeth: `test_refresh_keeps_the_scroll_offset_
of_every_page` and `test_refresh_never_hands_focus_to_the_sidebar` in
`tests/test_watch_face.py`. The Settings dialog builds its pages ONCE
and is not affected.

## Design Decisions
- **NOTHING `_build` MAKES IS EVER BORN PARENTLESS** (owner bug
  2026-08-15 — a window flashed open in the middle of the screen and
  shut again on EVERY live pick). A parentless `QWidget` *is* a
  top-level window, and the sidebar/stack pair used to be built bare
  and adopted only by the closing `addWidget` calls. In that span
  `setCurrentRow`/`setCurrentIndex` makes a window VISIBLE, so Windows
  gave each one a real native window at its default (screen-centre)
  spot; the reparent hid it a repaint later. Measured on the running
  app with a global Show/PlatformSurface spy — `PlatformSurface →
  WinIdChange → Show` at (1451,600) and (1216,600), then `Hide`; the
  same spy is silent after the fix. Both are constructed
  `QListWidget(self)` / `QStackedWidget(self)` now. The tooth
  (`tests/test_watch_face.py::test_the_rebuild_never_creates_a_top_
  level_window`) watches CONSTRUCTION, not the end state — by the time
  `_build` returns, `addWidget` has adopted both either way, so an
  after-the-fact `parent()` check passes on the broken code too
  (verified).
- `_SECTIONS` is a flat `(title, builder)` tuple, `builder` a
  `(settings, setters, tr) -> QWidget` function or `None` for a
  not-yet-built placeholder — a later phase turns a `None` into a real
  module by matching the SAME shape, no registry redesign needed.
- Sidebar selection persistence mirrors `design_window.py`'s tab
  persistence exactly, for the same reason: every pick routes through
  `refresh()`, which rebuilds the whole sidebar+stack pair.
- **No pinned width (owner decree 2026-08-14, superseding the fixed
  column of 2026-08-06).** The one-readable-column fix capped every page
  (and, since 2026-08-13, its holder) with `setMaximumWidth` to the
  widest section's MINIMUM hint — so an ultra-wide window still drew
  every gallery in the same narrow column, wrapping the eclipse tiles
  into two rows beside a screen of empty space (the owner's
  screenshot). His ruling: minimums that keep text legible are lawful,
  a hard-coded width never is. The caps are gone; content follows the
  real viewport width and the flow galleries absorb it by refilling
  their rows. `column_width` survives only as the MINIMUM the window
  must offer (`_declare_minimum`: sidebar + column + scrollbar across,
  the tallest section up to the 1280x720 screen floor down — past the
  floor the scrollbar lawfully takes over; measured from polished hints,
  since QSS paddings are part of the real size). Teeth:
  `tests/test_watch_face.py::test_no_page_carries_a_pinned_maximum_width`
  (the new law) and
  `…::test_every_scroll_holder_is_capped_to_the_same_column_as_its_page`
  (kept: holder and page must always wear the SAME width — the
  2026-08-13 row-wrap drift between the two is still a bug, cap or no
  cap). Runtime coverage: `tests/test_layout_audit.py` walks all nine
  sections at the declared minimum and +50%.
- **The nav pill fits its own row (2026-08-13, Space & Legibility law).**
  `app/theme.py`'s `QListWidget::item:selected` pill is painted from QSS
  padding (10px vertical) + margin (2px vertical); left to `QListWidget`'s
  own row layout, the reserved row was narrower than the painted pill, so
  the SELECTED entry's pill overlapped the row above and below and
  clipped their text (owner-reported: "Ring" / "Hands & Bodies" sliced
  around a selected "Numerals"). `_build` now stamps every nav item's
  `setSizeHint` from `config.encyclopedia_ui.THEME_NAV_ITEM_PADDING_V_PX`
  / `THEME_NAV_ITEM_MARGIN_V_PX` — the SAME constants the QSS pill reads
  — so the reserved row and the painted pill are one number and can never
  drift apart. Tooth:
  `tests/test_watch_face.py::test_nav_sidebar_selection_never_overlaps_a_neighbour_row`
  (counter-proved: it fails when the `setSizeHint` call is skipped, with
  the real theme applied).
