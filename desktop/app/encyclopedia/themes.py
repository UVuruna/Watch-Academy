"""The Encyclopedia's THEME screen — level two, one whole's cards.

The chosen whole's theme cards in the same card language as the home
screen (Rule #5, one `CardGrid`), up to
`ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` per row, wrapping into further rows.

Owner law: **vertical scroll is allowed here, horizontal never.** The
scroll area's horizontal bar is switched OFF outright, and the card
width is measured from the viewport so no row can want one in the first
place.

A card's footer names what waits inside — its page count, and for a
theme that carries several registers, how many the switcher walks.

Layer: app. Documentation: themes.md.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout

from app.encyclopedia.cards import CardGrid, card_pixmap
from app.encyclopedia.screen import EncyclopediaScreen
from config import encyclopedia_ui
from config import encyclopedia_tree as tree


class ThemeScreen(EncyclopediaScreen):
    """The theme cards of ONE whole."""

    opened = Signal(str)

    def __init__(self, topics: dict, encyclopedia, tr):
        super().__init__(topics, encyclopedia, tr)
        self._whole: tree.Whole | None = None
        self._grid = CardGrid(encyclopedia_ui.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS)
        self._grid.opened.connect(self.opened)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setWidget(self._grid)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(self._scroll)

    @property
    def whole(self) -> tree.Whole | None:
        return self._whole

    def show_whole(self, key: str) -> None:
        self._whole = tree.WHOLE_BY_KEY[key]
        self._grid.set_cards([
            self._spec(theme) for theme in self._whole.themes
            if theme in self._topics
        ])
        self.apply_zoom()
        self._scroll.verticalScrollBar().setValue(0)

    def _spec(self, theme: str) -> dict:
        topic = self._topics[theme]
        variants = len(topic["variants"])
        footer = f"{len(topic['entries'])} {self._tr('pages')}"
        if variants > 1:
            footer += f" · {variants} {self._tr('registers')}"
        return {
            "key": theme,
            "title": self._tr(topic.get("tile_title") or topic["title"]),
            "about": self._encyclopedia.about(theme)["base"],
            "plate": card_pixmap(topic["icon"]),
            "footer": footer,
            "accent": self._whole.accent,
        }

    def _relayout(self) -> None:
        """This gallery SCROLLS, so only the viewport's width is an
        input — the height is whatever the cards need."""
        self._grid.fit(self._scroll.viewport().width(), None, self._zoom)

    def resizeEvent(self, event) -> None:      # noqa: N802 — Qt override
        super().resizeEvent(event)
        self.apply_zoom()
