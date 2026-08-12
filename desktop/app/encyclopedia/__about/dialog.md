# Encyclopedia Dialog

**Script:** [Encyclopedia Dialog (script)](../dialog.py) · **Flow:** [diagram](../__flow/dialog.md)

## Purpose
The WINDOW — the shell that holds the three levels and everything
shared between them: the ONE header row (Home, the breadcrumb, the
titled VARIANT switcher and Download), the session zoom and the
`QStackedWidget` that shows one screen at a time.

It owns navigation, never layout: `show_home` / `show_whole` /
`show_topic` and `navigate_to` (the dial's Spacebar jump and the tray
menu both land here).

## Connections

### Uses
- [Home Screen](home.md), [Theme Screen](themes.md), [Reader Screen](reader.md) — the three stacked levels
- [Topic Tree](tree.md) — the table it opens (`topic_tree.topics`) and `resolve_target` for every jump addressed the dial's way
- [Card](cards.md) — `row_content_width`, for the minimum-width guard
- [Encyclopedia Tree (config)](../../../config/__about/encyclopedia_tree.md) — `whole_of`, the breadcrumb's names
- [Theme](../../__about/theme.md), [UI Style](../../__about/ui_style.md) — dialog theming and the chrome's gradient pills
- [Encyclopedia Repository](../../../data/__about/encyclopedia.md), [Symbolism Repository](../../../data/__about/symbolism.md) — built once here and threaded into all three screens

### Used by
- [App Controller](../../__about/controller.md) — keeps the ONE live instance
  (`self._encyclopedia`), raises it on a second open request instead of
  opening a duplicate, navigates it via `navigate_to`
- [Encyclopedia Warm](../../__about/encyclopedia_warm.md) — walks
  `app.encyclopedia.topics()` (this package's own re-export) as its
  single inventory of derived art to pre-build

## Classes

### EncyclopediaDialog
`QDialog`, non-modal (`.show()`d by the controller, `WA_DeleteOnClose`).

- `__init__(translations=None, hidden_unlocked=False, initial_topic=None, initial_entry=0, stay_on_top=False, travel_date=None, is_daylight=True)`:
  builds the topic table, the chrome, the three screens and the
  `QStackedWidget`; pins the window's minimum size; opens on Home, then
  applies `navigate_to(initial_topic, initial_entry)` (the Spacebar jump)
- `reader` / `home` / `themes` (properties): read-only handles for
  callers and tests
- `screen` (property): which level is showing — 0 home, 1 themes, 2 reader
- `topic_key` / `entry_index` (properties): proxy the reader's own
  reading position — the dialog never tracks it twice
- `show_home()` / `show_whole(key)` / `show_topic(key)`: switch the
  stack and refresh the header
- `navigate_to(topic, entry=0)`: resolves `(topic, entry)` through
  `topic_tree.resolve_target` and jumps this LIVE window there;
  `topic=None` or an unrecognized target is a no-op
- `_crumb_clicked(event)`: the breadcrumb's middle step returns to the
  whole; a no-op on the theme screen, where the whole IS the current page
- `_refresh_header()`: dresses the one header row (breadcrumb, title,
  variant switcher, Download) for whichever screen is showing
- `_step_variant(delta)`: forwards to `self._reader.switch_variant`
- `_apply_zoom_delta(angle_delta_y)` / `wheelEvent(event)`: Ctrl+wheel
  zoom, clamped to `constants.ENCYCLOPEDIA_ZOOM_RANGE`
- `_unlock_verses()`: appends the Four Greetings / Seasons poem entries
  (hidden-mode only)

## The header

```
 Home  ›  The Faith        ◀   Creeds — Creeds   ▶        Download
```

ONE row, three groups (owner 2026-07-29: *"Home, Title sa switcherom i
Download treba da budu u istom redu"*). The breadcrumb names the WHOLE,
the title the theme and its register — never the same name twice on one
screen. The variant switcher shows only when the theme has more than one
register; Download only on the article screen.

The two flanking groups (`crumbs_group`, `download_group`) carry stretch
1 each and the middle `title_group` none, so Qt hands the flanks the
same width and the title lands on the window's own centre however long
the breadcrumb or the Download caption grows.

## Design Decisions
- **`is_daylight` (owner decree 2026-07-29, THE DOUBLE NINTH LAW).** A
  plain bool (default `True`), handed straight to `topic_tree.topics` —
  the controller resolves it from its OWN live tick and passes it in;
  the dialog never touches a wall clock or recomputes sunrise/sunset.
- **The window's minimum is the owner's opening screen** (1280x720,
  `ENCYCLOPEDIA_MIN_WIDTH_PX`/`_HEIGHT_PX`, widened if a full theme-grid
  row would need more). The home grid is measured from the viewport, so
  this is what makes "the first screen never scrolls" geometric rather
  than hopeful.
- **The zoom is module-level** (`_session_zoom`): it survives a
  close-reopen within one app run, and is never written to settings.
- **The reader owns the reading position**; the dialog exposes it
  read-only as `topic_key` / `entry_index`.
- **Non-modal lifecycle**: the controller `.show()`s this dialog instead
  of `.exec()`ing it, so the dial stays interactive while it is open;
  `WA_DeleteOnClose` tears the C++ object down the moment the window closes.
