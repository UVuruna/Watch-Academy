# Encyclopedia Dialog

**Script:** [Encyclopedia Dialog (script)](dialog.py)

## Purpose
The WINDOW — the shell that holds the three levels and everything shared
between them: the breadcrumb, the title row with its VARIANT switcher,
the Home button, the session zoom and the `QStackedWidget` that shows one
screen at a time.

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
 Encyclopedia   > The Divine
        <   Greek gods - Pantheon   >
```

The breadcrumb names the WHOLE, the title the theme and its register —
never the same name twice on one screen (the owner's round R8b
complaint). The switcher shows only when the theme has more than one
register.

## Design Decisions
- **The window's minimum is the owner's opening screen** (1280x720). The
  home grid is measured from the viewport, so this is what makes "the
  first screen never scrolls" geometric rather than hopeful.
- **The zoom is module-level** (`_session_zoom`): it survives a
  close-reopen within one app run, and is never written to settings.
- **The reader owns the reading position**; the dialog exposes it
  read-only as `topic_key` / `entry_index`.
