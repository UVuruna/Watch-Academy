"""Encyclopedia — the article browser (owner spec 2026-07-12).

Screen 1 is a gallery of TOPICS (the eight weekday themes, Astrology,
the Chinese zodiac, the Trinity), each card wearing its symbol image;
screen 2 lists every article of the chosen topic — entity image, bold
name, full base text — translated through the active overlay and with
the canon terms highlighted exactly like the dial legends. Resizable
like the Guide: images rescale live with the window width.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from config import constants, defaults
from config.ui_text import ui
from data.symbolism import SymbolismRepository
from render.compositor import _article_body_html

_TOPIC_ICON_PX = 96


def _weekday_topic(theme: str):
    """(icon path, entries) for one weekday theme: seven bodies in
    week order with their themed art, display names and article set."""
    article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
    if theme == "planets":
        directory = defaults.WEEKDAY_ART_DIR / "planets"
        files = {body: body for body in constants.WEEKDAY_BODIES}
        names = defaults.DEFAULT_SKIN.weekday_set.body_names
    else:
        directory = (
            defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        )
        files = defaults.WEEKDAY_THEME_FILES[theme]
        names = defaults.WEEKDAY_THEME_NAMES[theme]
    week_order = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
    entries = [
        {
            "image": directory / f"{files[body]}.png",
            "name": names[body],
            "article": ("article", article_set, body),
            "accents": defaults.BODY_ACCENT_HUES[body],
        }
        for body in week_order
    ]
    return entries[0]["image"], entries


def _topics() -> dict:
    """topic key -> {title, icon, entries}; article refs resolve lazily
    against the repository so the overlay always applies."""
    topics: dict = {}
    theme_titles = {
        "planets": "Planets", "planet_signs": "Planet signs",
        "greek": "Greek gods", "norse": "Norse gods",
        "egypt": "Egyptian gods", "religion": "Religions",
        "religion_alt": "Religions II", "profession": "Professions",
    }
    for theme, title in theme_titles.items():
        icon, entries = _weekday_topic(theme)
        topics[theme] = {"title": title, "icon": icon, "entries": entries}
    topics["astrology"] = {
        "title": "Astrology",
        "icon": defaults.ZODIAC_ART_DIR / "sign" / "Leo.png",
        "entries": [
            {
                "image": defaults.ZODIAC_ART_DIR / "sign" / f"{sign}.png",
                "name": sign,
                "article": ("zodiac", sign),
                "accents": defaults.SIGN_ACCENT_HUES[sign],
            }
            for sign in (
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn",
                "Aquarius", "Pisces",
            )
        ],
    }
    topics["chinese"] = {
        "title": "Chinese zodiac",
        "icon": defaults.ZODIAC_ART_DIR / "chinese" / "Dragon.png",
        "entries": [
            {
                "image": defaults.ZODIAC_ART_DIR / "chinese" / f"{animal}.png",
                "name": animal,
                "article": ("chinese", animal),
                "accents": (),
            }
            for animal in constants.CHINESE_ANIMALS
        ] + [
            {
                "image": None,
                "name": element,
                "article": ("element", element),
                "accents": (),
            }
            for element in constants.CHINESE_ELEMENTS
        ],
    }
    topics["trinity"] = {
        "title": "Trinity",
        "icon": None,
        "entries": [
            {
                "image": None,
                "name": virtue,
                "article": ("trio", virtue),
                "accents": defaults.TRIO_ACCENT_HUES[virtue],
            }
            for virtue in ("Faith", "Hope", "Love")
        ],
    }
    return topics


class EncyclopediaDialog(QDialog):
    def __init__(self, translations: dict | None = None):
        super().__init__()
        self._overlay = translations or {}
        self._tr = lambda text: ui(self._overlay, text)
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Encyclopedia')}"
        )
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._symbolism = SymbolismRepository(overlay=self._overlay)
        self._topics = _topics()
        self._cells: list[tuple[QLabel, QPixmap]] = []

        self._title = QLabel()
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: {defaults.GUIDE_TITLE_PX}px; font-weight: bold;"
            f"margin: {defaults.GUIDE_SPACING_PX}px;"
        )
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._back = QPushButton(self._tr("← Back"))
        self._back.clicked.connect(self._show_topics)
        row = QHBoxLayout()
        row.addWidget(self._back)
        row.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._scroll, stretch=1)
        layout.addLayout(row)
        self.resize(
            defaults.GUIDE_INITIAL_IMAGE_PX + 90,
            defaults.GUIDE_INITIAL_IMAGE_PX + 220,
        )
        self._show_topics()

    def _article_text(self, ref: tuple) -> str:
        kind = ref[0]
        if kind == "article":
            return self._symbolism.article(ref[1], ref[2])["base"]
        if kind == "zodiac":
            return self._symbolism.zodiac_article(ref[1])["base"]
        if kind == "chinese":
            return self._symbolism.chinese_article(ref[1])["base"]
        if kind == "element":
            return self._symbolism.chinese_element(ref[1])["base"]
        return self._symbolism.trio_article(ref[1])["base"]

    def _show_topics(self) -> None:
        """Screen 1 — the topic gallery (owner spec: grouped by symbol)."""
        self._title.setText(self._tr("Encyclopedia"))
        self._back.hide()
        self._cells = []
        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(defaults.GUIDE_SPACING_PX * 2)
        for index, (key, topic) in enumerate(self._topics.items()):
            card = QToolButton()
            card.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextUnderIcon
            )
            card.setText(self._tr(topic["title"]))
            if topic["icon"] is not None and Path(topic["icon"]).exists():
                pixmap = QPixmap(str(topic["icon"])).scaledToHeight(
                    _TOPIC_ICON_PX,
                    Qt.TransformationMode.SmoothTransformation,
                )
                card.setIcon(QIcon(pixmap))
                card.setIconSize(pixmap.size())
            card.setMinimumSize(_TOPIC_ICON_PX + 60, _TOPIC_ICON_PX + 50)
            card.clicked.connect(
                lambda checked=False, chosen=key: self._show_topic(chosen)
            )
            grid.addWidget(card, index // 3, index % 3)
        self._scroll.setWidget(content)

    def _show_topic(self, key: str) -> None:
        """Screen 2 — every article of the topic, image + name + text."""
        topic = self._topics[key]
        self._title.setText(self._tr(topic["title"]))
        self._back.show()
        self._cells = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX * 3)
        for entry in topic["entries"]:
            cell = QVBoxLayout()
            cell.setSpacing(defaults.GUIDE_SPACING_PX)
            if entry["image"] is not None and Path(entry["image"]).exists():
                image = QLabel()
                image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                art = QPixmap(str(entry["image"]))
                self._cells.append((image, art))
                cell.addWidget(image)
            name = QLabel(
                f"<div style='font-size: {defaults.GUIDE_SUBTITLE_PX}px'>"
                f"<b>{self._tr(entry['name'])}</b></div>"
            )
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(name)
            text = QLabel(
                _article_body_html(
                    self._article_text(entry["article"]),
                    accents=entry["accents"],
                )
            )
            text.setWordWrap(True)
            text.setTextFormat(Qt.TextFormat.RichText)
            cell.addWidget(text)
            column.addLayout(cell)
        self._scroll.setWidget(content)
        self._scroll.verticalScrollBar().setValue(0)
        self._rescale()

    def _rescale(self) -> None:
        """Entry images follow the window width (Guide pattern)."""
        available = max(
            200,
            self._scroll.viewport().width() - 4 * defaults.GUIDE_SPACING_PX,
        )
        for image, art in self._cells:
            width = min(available // 2, art.width())
            image.setPixmap(
                art.scaledToWidth(
                    max(160, width),
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rescale()
