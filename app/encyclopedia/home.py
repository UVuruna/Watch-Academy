"""The Encyclopedia's HOME screen — level one, the nine wholes.

Owner law (Session 27, 2026-07-28): **this screen never scrolls.** It
carries no scroll area at all — a 3x3 grid (nine wholes, Session 35)
measured from the widget's own width AND height, so the cards shrink
with the window instead of spilling out of it. The dialog's minimum
size is the owner's own 1280x720 opening screen, which is what makes
"never scrolls" a geometric fact rather than a hope.

Each card wears its whole's Rose accent, a COMPUTED 2x2 mosaic of that
whole's own theme plates (root Rule #19 — never a generated category
image; a hand-drawn plate under `ENCYCLOPEDIA_WHOLE_ART_DIR` wins when
one lands), the whole's title, its one-line about and a live count of
what waits inside.

Layer: app. Documentation: home.md.
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from app.encyclopedia.cards import CardGrid, mosaic_pixmap
from config import encyclopedia_ui, paths
from config import encyclopedia_tree as tree


class HomeScreen(QWidget):
    """The nine wholes, 3x3, no scroll ever."""

    opened = Signal(str)

    def __init__(self, topics: dict, encyclopedia, tr):
        super().__init__()
        self._topics = topics
        self._encyclopedia = encyclopedia
        self._tr = tr
        self._zoom = 1.0
        self._grid = CardGrid(encyclopedia_ui.ENCYCLOPEDIA_HOME_COLUMNS)
        self._grid.opened.connect(self.opened)
        # THE GRID NEVER DICTATES A MINIMUM (owner bug 2026-07-29, the
        # one-way resize). `fit()` measures the cards FROM the viewport
        # and pins them with setFixedWidth/Height — which is also Qt's
        # way of declaring a minimum. So every enlargement raised the
        # window's own minimum to the new size and the window could
        # never be dragged back down: growth was a ratchet. The grid's
        # size hints are meaningless BY DESIGN here (the viewport is the
        # input, not the output), so they are declared Ignored, and the
        # only floor left is the dialog's own 1280x720.
        self._grid.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(self._grid)
        self._grid.set_cards([self._spec(whole) for whole in tree.WHOLES])

    def _plate(self, whole: tree.Whole) -> QPixmap:
        """The whole's tile: the owner's own plate when he has drawn
        one, otherwise the mosaic computed from the whole's own theme
        plates."""
        drawn = paths.art_file(
            encyclopedia_ui.ENCYCLOPEDIA_WHOLE_ART_DIR / f"{whole.key}.png"
        )
        if drawn.exists():
            return QPixmap(str(drawn))
        return mosaic_pixmap([
            self._topics[theme]["icon"]
            for theme in whole.themes if theme in self._topics
        ])

    def _spec(self, whole: tree.Whole) -> dict:
        pages = sum(
            len(self._topics[theme]["entries"])
            for theme in whole.themes if theme in self._topics
        )
        cards = sum(1 for theme in whole.themes if theme in self._topics)
        theme_word = self._tr("theme" if cards == 1 else "themes")
        page_word = self._tr("page" if pages == 1 else "pages")
        return {
            "key": whole.key,
            "title": self._tr(whole.title),
            "about": self._encyclopedia.whole(whole.key)["base"],
            "plate": self._plate(whole),
            "footer": f"{cards} {theme_word} · {pages} {page_word}",
            "accent": whole.accent,
        }

    def fit(self, zoom: float | None = None) -> None:
        if zoom is not None:
            self._zoom = zoom
        self._grid.fit(self.width(), self.height(), self._zoom)

    def resizeEvent(self, event) -> None:      # noqa: N802 — Qt override
        super().resizeEvent(event)
        self.fit()
