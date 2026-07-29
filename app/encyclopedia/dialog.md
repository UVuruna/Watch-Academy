# Encyclopedia Dialog

**Script:** [Encyclopedia Dialog (script)](dialog.py)

## Purpose
The WINDOW — the shell that holds the three levels and everything shared
between them: the ONE header row (Home, the breadcrumb, the titled
VARIANT switcher and Download), the session zoom and the
`QStackedWidget` that shows one screen at a time.

It owns navigation, never layout: `show_home` / `show_whole` /
`show_topic` and `navigate_to` (the dial's Spacebar jump and the tray
menu both land here).

## Connections

### Uses
- [Home Screen](home.md), [Theme Screen](themes.md), [Reader Screen](reader.md) — the three levels it stacks
- [Topic Tree](tree.md) — the table it opens, and `resolve_target` for every jump addressed the dial's way
- [Encyclopedia Tree](../../config/encyclopedia_tree.md) — the wholes, their accents and the breadcrumb's names

### Used by
- [App Controller](../controller.md) — one live instance, raised or navigated on a second open request

## The header

```
 Home  > The Divine        <   Creeds - Creeds   >        Download
```

ONE row, three groups (owner 2026-07-29: *"Home, Title sa switcherom i
Download treba da budu u istom redu"*). The breadcrumb names the WHOLE,
the title the theme and its register — never the same name twice on one
screen (the owner's round R8b complaint). The switcher shows only when
the theme has more than one register; Download only on the article
screen, since the galleries have no page to save.

The two flanking groups carry **stretch 1 each and the middle group
none**, so Qt hands the flanks the same width and the title lands on the
window's own centre however long the breadcrumb or the Download caption
grows. This is the one strip the no-X-scroll law cannot delegate to a
scroll area — it has none — so a test measures the row's minimum against
the owner's 1280.

## Design Decisions
- **`is_daylight` (owner decree 2026-07-29, THE DOUBLE NINTH LAW).** The
  constructor takes it as a plain bool (default True) and hands it
  straight to `topic_tree.topics` — the controller resolves it from its
  OWN live tick (`WatchController._effective_is_daylight`, `core.
  clock_state.build_tick_state` against the already-built `DayContext`)
  and passes it in; the dialog itself never touches a wall clock or
  recomputes sunrise/sunset.
- **The window's minimum is the owner's opening screen** (1280x720). The
  home grid is measured from the viewport, so this is what makes "the
  first screen never scrolls" geometric rather than hopeful.
- **The zoom is module-level** (`_session_zoom`): it survives a
  close-reopen within one app run, and is never written to settings.
- **The reader owns the reading position**; the dialog exposes it
  read-only as `topic_key` / `entry_index`.
