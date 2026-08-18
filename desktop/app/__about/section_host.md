# Section Host

**Script:** [Section Host (script)](../section_host.py) · **Flow:**
[diagram](../__flow/section_host.md)

## Purpose
ONE nav-list-beside-a-page-stack, for every window built that way.

A left `QListWidget` of section titles, a right `QStackedWidget` holding
one `QScrollArea` per section, the sidebar's width MEASURED from the
longest title, and the window minimum computed from the pages' own
hints. The [Watch Face window](../watch_face/__about/window.md) and the
[Settings dialog](../settings_dialog/__about/dialog.md) had written that
out twice; the [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md) named
it R16 (section 1 COPY) and this module is the answer (WA-R16,
2026-08-19).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `SETTINGS_NAV_WIDTH_PX`, `SETTINGS_NAV_CHROME_PX`,
  `SETTINGS_NAV_ITEM_CHROME_PX`

### Used by
- [Watch Face (subfolder)](../watch_face/___watch_face.md) — nine
  sections, rebuilt on every live pick
- [Settings Dialog (subfolder)](../settings_dialog/___settings_dialog.md)
  — three sections, built once (its sidebar-less "Custom art" mode has
  no section list, so it builds no host)

## The interface
- `SectionHost(sections, *, parent, measure_minimum, row_height,
  page_holder, horizontal_scroll)` — `sections` is a sequence of
  `(label, page)`, the label exactly as it should read in the sidebar
  and the page already built.
- `nav_list` / `stack` / `pages` / `nav_width` / `spacing` — the parts a
  window still speaks about itself.
- `current_row()` / `set_current_row(row)` — the selection, clamped.
- `polish_pages()` then `content_width()` / `tallest()` /
  `measured_minimum(extra_width, extra_height, floor)` — the measuring
  half. The host answers for the sidebar, the widest page and the
  scrollbar; the window adds its OWN chrome (its margins, and for the
  Settings dialog its button row).
- `capture_scrolls()` / `restore_scrolls(offsets)` — for a window that
  rebuilds live.
- `stretched_holder(factory)` — a ready-made `page_holder` that packs
  the page to the TOP and leaves the leftover height empty below.

## Design Decisions
- **The host takes BUILT PAGES, never builders.** That is the seam that
  removes the duplication without moving anyone's `self`. The Settings
  dialog's three section mixins keep every widget handle on the dialog,
  because `result_settings()` reads them back when OK is pressed; a host
  that built pages would have to be handed the dialog's state and hand
  its widgets back — the back-channel a mixin exists to avoid. The same
  reasoning kept the controller's five pieces as mixins in
  [WA-R14](controller.md).
- **Every difference between the two windows is a NAMED argument**, with
  its reason written beside it, so a third window that wants a section
  list gets one line instead of a third copy:
  `measure_minimum` (minimum vs preferred hints — the flow galleries
  reflow, the settings panels do not), `row_height` (the nav pill row
  fix the Watch Face window measured; a window that never saw that
  overlap does not inherit a fix for a bug it does not have),
  `page_holder` (a flow gallery only knows its height once it has a
  width) and `horizontal_scroll` (a scroll area rebuilt inside an
  already-visible window grows an empty bar).
- **The screen floor lives here now.** Both windows quoted `1280, 720`
  separately; `SCREEN_FLOOR` is the one copy.
- **Nothing here changed a pixel.** The declared minimums measured
  before and after the move are identical — `WatchFaceDialog` 785×720
  and `SettingsDialog` 714×720 on both device profiles.
