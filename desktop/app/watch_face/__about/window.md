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
- `_SECTIONS` is a flat `(title, builder)` tuple, `builder` a
  `(settings, setters, tr) -> QWidget` function or `None` for a
  not-yet-built placeholder — a later phase turns a `None` into a real
  module by matching the SAME shape, no registry redesign needed.
- Sidebar selection persistence mirrors `design_window.py`'s tab
  persistence exactly, for the same reason: every pick routes through
  `refresh()`, which rebuilds the whole sidebar+stack pair.
- **One scrolling content column per section (layout law, 2026-08-06).**
  Bare pages in the stack made the window's minimum the TALLEST section
  (Colors — 2090px, taller than any screen) while a maximized window
  stretched every row across the whole 4K width — the owner's
  screenshots. Each page now sits top-packed inside a `QScrollArea`,
  capped at a content-column width COMPUTED as the widest section's own
  polished hint (`ensurePolished` first — QSS paddings are part of the
  real size), and `_declare_minimum` declares the window minimum from
  that column: sidebar + column + scrollbar across, the tallest section
  up to the 1280x720 screen floor down — past the floor the scrollbar
  lawfully takes over. Verified by `tests/test_layout_audit.py`, which
  walks all nine sections at the declared minimum and +50%.
- **The holder wears the same collar (2026-08-13).** The cap above was
  put on the PAGE alone, while the `FlowContent` holder around it kept
  the scroll area's full width — and it measures its content at its own
  width. Four pixels of difference is enough to fit one more tile per
  gallery row, so the height the holder published was a full row short
  of what the page then needed: on the owner's live profile the Ring
  page's "Inner (minute track)" group was handed 375px against its own
  388px minimum and lost its bottom margin. Both now wear the same
  `column_width`, so the measured width and the drawn width are one
  number. Tooth:
  `tests/test_watch_face.py::test_every_scroll_holder_is_capped_to_the_same_column_as_its_page`
  (counter-proved: it fails on the un-capped holder).
