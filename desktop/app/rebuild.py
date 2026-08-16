"""The one door through which a live rebuild throws a widget away.

See [Rebuild](__about/rebuild.md) for the measured root cause. In one
sentence: an orphan QWidget IS a top-level window, so a VISIBLE child
handed `setParent(None)` becomes a real native window at the default
screen-centre spot and stays there until `deleteLater()` is reached a
repaint later — which is the flash the owner reported twice.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLayout, QWidget


def discard(widget: QWidget) -> None:
    """Throw `widget` away without ever letting it be a window.

    The order is the whole point and may not be rearranged:

    1. `hide()` — a hidden widget gets no native surface and no `Show`
       when it is orphaned one line later. WITHOUT THIS CALL the widget
       flashes open in the middle of the screen (owner bug 2026-08-15,
       reported again 2026-08-16; measured with a global
       `Show`/`PlatformSurface` spy, silent with it).
    2. `setParent(None)` — not optional either, and the reason is older
       than this module (Themes & Slots, live-profile audit shot
       2026-08-14): `deleteLater` alone leaves the widget a visible
       child until the event loop gets round to it, and a widget no
       layout owns keeps its old geometry, so the rebuilt rows painted
       ON TOP of the ones they replaced.
    3. `deleteLater()` — destruction belongs to the event loop; deleting
       a widget inside its own signal handler is how a rebuild crashes.
    """
    widget.hide()
    widget.setParent(None)
    widget.deleteLater()


def clear_layout(layout: QLayout) -> None:
    """Empty `layout` of everything it owns, ready to be refilled.

    Widgets go through `discard`; a nested layout is emptied by
    recursion and then dropped with its item. `takeAt(0)` rather than
    `itemAt` so the layout is genuinely empty when this returns."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            discard(widget)
            continue
        nested = item.layout()
        if nested is not None:
            clear_layout(nested)
