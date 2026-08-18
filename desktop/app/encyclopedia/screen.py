"""One SCREEN of the Encyclopedia — the three things all of them are.

The dialog is a stack of three screens: the nine wholes, one whole's
theme cards, and the article reader. They are the same KIND — each is
built from `(topics, encyclopedia, tr)`, each holds a zoom factor, and
each re-lays itself out when that factor changes — and until the [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s R8 they were three
unrelated `QWidget` subclasses that each wrote those three things again.

Worse, the zoom protocol had FORKED into two spellings: `fit(zoom=None)`
on the two grid screens, `set_zoom(zoom)` on the reader. Nothing made
them agree, so the dialog branched on which screen was showing —
`if screen == _HOME: ... elif _THEMES: ... else: ...` — in three places.
One protocol, `apply_zoom(zoom=None)`, deletes all three branches.

Layer: app. Documentation: __about/screen.md.
"""

from PySide6.QtWidgets import QWidget


class EncyclopediaScreen(QWidget):
    """A screen of the Encyclopedia stack.

    Subclasses build their own content and implement `_relayout()` —
    "lay yourself out at the zoom you are holding". They never touch
    `_zoom` themselves; `apply_zoom` owns it."""

    def __init__(self, topics: dict, encyclopedia, tr):
        super().__init__()
        self._topics = topics
        self._encyclopedia = encyclopedia
        self._tr = tr
        self._zoom = 1.0

    def apply_zoom(self, zoom: float | None = None) -> None:
        """THE ONE ZOOM PROTOCOL. `zoom=None` means "same factor, lay
        out again" — what a resize asks for; a number means the user
        turned Ctrl+wheel and every screen must remember it, whether it
        is showing or not (the dialog zooms the WHOLE encyclopedia, so
        the screen behind must already be right when it comes forward)."""
        if zoom is not None:
            self._zoom = zoom
        self._relayout()

    def _relayout(self) -> None:
        """Lay the screen out at `self._zoom`. Every screen has one."""
        raise NotImplementedError
