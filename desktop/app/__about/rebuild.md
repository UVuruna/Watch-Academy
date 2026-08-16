# Rebuild

**Script:** [Rebuild (script)](../rebuild.py)

## Purpose
The ONE door through which a live rebuild throws a widget away.

Every window in this program rebuilds itself on a live pick: the Watch
Face sidebar and page stack, its Themes & Slots rows, the content tree,
the Encyclopedia card grid and the Guide's look table. All of them tore
their old contents down by hand, and all of them made the same
top-level window the owner kept seeing flash open and shut in the middle
of the screen.

The mechanism, measured with a global `Show`/`PlatformSurface` event
filter on the running app (owner bug 2026-08-15, reported again
2026-08-16): **an orphan QWidget IS a top-level window.** A VISIBLE
child handed `setParent(None)` stops being a child and becomes a real
native window, which Windows places at its default screen-centre spot —
and `deleteLater()` only destroys it once the event loop comes round, a
repaint later. In that gap it is on screen.

`hide()` first, and the window can never exist: a hidden widget gets no
native surface and no `Show` when it is orphaned. That single call is
the whole fix, and it belongs in one place rather than at every one of
the seven sites that used to spell the teardown out.

The first round on this bug (0.15.045) fixed the OTHER half — a widget
built parentless and adopted later — and left this half standing six
lines above its own edit. Both halves are the same law: **nothing this
program builds or destroys is ever, for one instant, a window nobody
asked for.**

## Connections

### Uses
- `PySide6.QtWidgets.QLayout`, `QWidget` — types only, no project
  dependency; this module sits below every window

### Used by
- [Watch Face Window](../watch_face/__about/window.md) — `_build`
  discards the previous sidebar + page stack
- [Watch Face — Themes & Slots](../watch_face/__about/themes.md) and
  [Content Tree](../watch_face/__about/theme_tree.md) — their private
  `_clear` helpers were byte-identical twins and now both call
  `clear_layout` (Rule C, inheritance over duplication)
- [Encyclopedia Cards](../encyclopedia/__about/cards.md) — `set_cards`
  clears the card grid before refilling it
- [Encyclopedia Reader](../encyclopedia/__about/reader.md) — the look
  table is rebuilt cell by cell

## Functions

### discard(widget)
`hide()` → `setParent(None)` → `deleteLater()`, in that order and never
another. The `hide()` is the tooth of this module: without it the widget
flashes as a window. The `setParent(None)` is not optional either — the
reason is recorded at the Themes & Slots call site it came from:
`deleteLater` alone leaves the widget a visible child until the event
loop runs, and a widget no layout owns keeps its old geometry, so
rebuilt rows painted ON TOP of the ones they replaced.

### clear_layout(layout)
Empties a layout of everything it owns — widgets through `discard`,
nested layouts by recursion. Takes items out with `takeAt(0)` so the
layout is left genuinely empty and ready to be refilled.

## Enforcement
`desktop/tests/test_no_orphan_windows.py` holds both halves:

- the STATIC tooth — no module under `app/` may call `setParent(None)`
  on its own; the only spelling of a teardown is this module's;
- the RUNTIME tooth — a global `Show`/`PlatformSurface` spy over a real
  `WatchController`, driving every knob and every page of the Watch Face
  window and failing if ANY top-level window is shown. It watches the
  SYMPTOM, not a theory about a parent, which is exactly what the first
  round's tooth did not do.
