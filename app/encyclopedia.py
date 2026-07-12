"""Encyclopedia — the article browser (owner spec 2026-07-12).

Screen 1 is a gallery of TOPICS in four GROUPS (owner UX round: Gods /
Zodiac — with the planets and their signs / Themes / Religions), each
card wearing its symbol image; screen 2 lists every article of the
chosen topic — entity image(s), bold name, full base text — translated
through the active overlay and with the canon terms highlighted exactly
like the dial legends. The whole article BLOCK is centered and spans a
fraction of the window width; the font grows gently with the window
(em-like coefficient). Astrology shows BOTH the sign logo and its
constellation side by side. Resizable: everything rescales live.
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

# The gallery groups (owner UX round 2026-07-12): gods together, the
# zodiac family with the planets and their signs, the remaining week
# themes with the Trinity, and the religions on their own ("2 members
# for now").
_TOPIC_GROUPS = (
    ("Gods", ("greek", "norse", "egypt", "slavic")),
    ("Zodiac", ("astrology", "chinese", "planets", "planet_signs")),
    ("Themes", ("alchemy", "japan", "profession", "trinity")),
    ("Religions", ("religion", "religion_alt")),
)


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
            "images": (directory / f"{files[body]}.png",),
            "name": names[body],
            "article": ("article", article_set, body),
            "accents": defaults.BODY_ACCENT_HUES[body],
        }
        for body in week_order
    ]
    return entries[0]["images"][0], entries


def _topics() -> dict:
    """topic key -> {title, icon, entries}; article refs resolve lazily
    against the repository so the overlay always applies. Every entry
    carries an `images` TUPLE — Astrology pairs the sign logo with its
    constellation (owner spec: both, side by side)."""
    topics: dict = {}
    for theme, title in defaults.WEEKDAY_THEME_TITLES.items():
        icon, entries = _weekday_topic(theme)
        topics[theme] = {"title": title, "icon": icon, "entries": entries}
    topics["astrology"] = {
        "title": "Astrology",
        "icon": defaults.ZODIAC_ART_DIR / "sign" / "Leo.png",
        "entries": [
            {
                "images": (
                    defaults.ZODIAC_ART_DIR / "logo" / f"{sign}.png",
                    defaults.ZODIAC_ART_DIR / "constellation" / f"{sign}.png",
                ),
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
                "images": (defaults.ZODIAC_ART_DIR / "chinese" / f"{animal}.png",),
                "name": animal,
                "article": ("chinese", animal),
                "accents": (),
            }
            for animal in constants.CHINESE_ANIMALS
        ] + [
            {
                "images": (),
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
                "images": (),
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
        self._cells: list[tuple[QLabel, QPixmap, int]] = []
        self._blocks: list[QWidget] = []
        self._text_labels: list[QLabel] = []
        self._name_labels: list[QLabel] = []

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
        """Screen 1 — the topic gallery in the owner's four groups,
        a bold group header above each card row."""
        self._title.setText(self._tr("Encyclopedia"))
        self._back.hide()
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX)
        for group_title, keys in _TOPIC_GROUPS:
            header = QLabel(self._tr(group_title))
            header.setStyleSheet(
                f"font-size: {defaults.GUIDE_SUBTITLE_PX + 2}px;"
                f"font-weight: bold;"
                f"margin-top: {defaults.GUIDE_SPACING_PX}px;"
            )
            column.addWidget(header)
            rule = QFrame()
            rule.setFrameShape(QFrame.Shape.HLine)
            rule.setFrameShadow(QFrame.Shadow.Sunken)
            column.addWidget(rule)
            grid = QGridLayout()
            grid.setSpacing(defaults.GUIDE_SPACING_PX * 2)
            for index, key in enumerate(keys):
                topic = self._topics[key]
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
                grid.addWidget(card, index // 4, index % 4)
            grid.setColumnStretch(4, 1)
            column.addLayout(grid)
        column.addStretch(1)
        self._scroll.setWidget(content)

    def _show_topic(self, key: str) -> None:
        """Screen 2 — every article of the topic: the images row (the
        Astrology pair sits side by side), the bold name and the text,
        all inside ONE centered block per entry (owner: center the
        whole object, never the text lines)."""
        topic = self._topics[key]
        self._title.setText(self._tr(topic["title"]))
        self._back.show()
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX * 3)
        for entry in topic["entries"]:
            block = QWidget()
            cell = QVBoxLayout(block)
            cell.setContentsMargins(0, 0, 0, 0)
            cell.setSpacing(defaults.GUIDE_SPACING_PX)
            images = [
                path for path in entry["images"]
                if path is not None and Path(path).exists()
            ]
            if images:
                images_row = QHBoxLayout()
                images_row.setSpacing(defaults.GUIDE_SPACING_PX * 2)
                images_row.addStretch(1)
                for path in images:
                    label = QLabel()
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self._cells.append(
                        (label, QPixmap(str(path)), len(images))
                    )
                    images_row.addWidget(label)
                images_row.addStretch(1)
                cell.addLayout(images_row)
            name = QLabel(f"<b>{self._tr(entry['name'])}</b>")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._name_labels.append(name)
            cell.addWidget(name)
            text = QLabel(
                _article_body_html(
                    self._article_text(entry["article"]),
                    accents=entry["accents"],
                )
            )
            text.setWordWrap(True)
            text.setTextFormat(Qt.TextFormat.RichText)
            self._text_labels.append(text)
            cell.addWidget(text)
            self._blocks.append(block)
            column.addWidget(block, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._scroll.setWidget(content)
        self._scroll.verticalScrollBar().setValue(0)
        self._rescale()

    def _rescale(self) -> None:
        """Everything follows the window: each entry BLOCK spans the
        configured width fraction (centered), the images share the
        block (the Astrology pair splits it), and the font grows with
        the width at the gentle em-like coefficient."""
        viewport = max(320, self._scroll.viewport().width())
        block_width = round(
            viewport * defaults.ENCYCLOPEDIA_TEXT_WIDTH_FRACTION
        )
        for block in self._blocks:
            block.setFixedWidth(block_width)
        font_px = min(
            defaults.ENCYCLOPEDIA_MAX_FONT_PX,
            max(
                defaults.ENCYCLOPEDIA_BASE_FONT_PX,
                round(
                    defaults.ENCYCLOPEDIA_BASE_FONT_PX
                    + (viewport - defaults.ENCYCLOPEDIA_FONT_BASE_WIDTH)
                    * defaults.ENCYCLOPEDIA_FONT_GROWTH
                ),
            ),
        )
        for label in self._text_labels:
            label.setStyleSheet(f"font-size: {font_px}px;")
        for label in self._name_labels:
            label.setStyleSheet(f"font-size: {font_px + 3}px;")
        for image, art, siblings in self._cells:
            share = block_width // siblings - defaults.GUIDE_SPACING_PX * 2
            width = min(max(160, share), art.width())
            image.setPixmap(
                art.scaledToWidth(
                    width, Qt.TransformationMode.SmoothTransformation
                )
            )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rescale()
