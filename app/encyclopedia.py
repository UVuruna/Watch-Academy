"""Encyclopedia — the article browser (owner spec 2026-07-12; expansion
2026-07-13).

Screen 1 is a gallery of TOPICS in GROUPS — THE CLOCK first (the Week
day pages and the Instrument functionality articles), then Gods /
Zodiac / Themes / Religions, and THE INNER WHEEL last (Virtues, Sins,
Moods with their emblem logos); screen 2 lists every article of the
chosen topic — entity image(s), bold name, full base text — translated
through the active overlay and with the canon terms highlighted exactly
like the dial legends. The whole article BLOCK is centered and spans a
fraction of the window width; the font grows gently with the window
(em-like coefficient). Astrology shows BOTH the sign logo and its
constellation side by side; the SUN entries pair the Ruler plate with
the Servant face. Metal themes (and the Chinese animals) carry LOOK
ARROWS — Bronze / Gold / Silver / Colored cycled per entry (owner
2026-07-13: "sve slike od te teme, može skrol levo desno strelice").
Resizable: everything rescales live.
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
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository
from render.assets import metal_variant_file
from render.compositor import _article_body_html

_TOPIC_ICON_PX = 96

# The gallery groups (owner UX rounds 2026-07-12/13): the clock's own
# story first, gods together, the zodiac family with the planets and
# their signs, the remaining week themes with the Trinity, the
# religions, and the cross-cure emblem families last.
_TOPIC_GROUPS = (
    ("The Clock", ("week", "instrument")),
    ("Gods", ("greek", "norse", "egypt", "slavic")),
    ("Zodiac", ("astrology", "chinese", "planets", "planet_signs")),
    ("Themes", ("alchemy", "japan", "profession", "trinity")),
    ("Religions", ("religion", "religion_alt")),
    ("The Inner Wheel", ("virtues", "sins", "moods")),
)

# The WEEK page image strip (owner spec: each day gathers everything it
# owns): planet render, planet sign, then the day's virtue / sin / mood
# emblems — Sunday, the dual day, carries both of each.
_WEEK_EMBLEMS = {
    "sun": (("Justice", "Humility"), ("Pride", "Servility"),
            ("Glory", "Eclipse")),
    "moon": (("Serenity",), ("Fear",), ("Calm",)),
    "mars": (("Courage",), ("Wrath",), ("Zeal",)),
    "mercury": (("Wisdom",), ("Greed",), ("Sorrow",)),
    "jupiter": (("Generosity",), ("Excess",), ("Joy",)),
    "venus": (("Love",), ("Jealousy",), ("Passion",)),
    "saturn": (("Patience",), ("Envy",), ("Renewal",)),
}
_VSM_DAYS = {
    "virtues": ("Justice", "Humility", "Serenity", "Courage", "Wisdom",
                "Generosity", "Love", "Patience"),
    "sins": ("Pride", "Servility", "Fear", "Wrath", "Greed", "Excess",
             "Jealousy", "Envy"),
    "moods": ("Glory", "Eclipse", "Calm", "Zeal", "Sorrow", "Joy",
              "Passion", "Renewal"),
}
_VSM_DIRS = {"virtues": "virtue", "sins": "sin", "moods": "mood"}
_INSTRUMENT_KEYS = (
    "dial", "solar_rotation", "twilight", "year_wheel", "moon_lunations",
    "paint_light", "metals", "ring_letters",
)


def _looks(base: Path, colored: Path | None) -> tuple:
    """The four LOOKS of a bronze-plate image (owner 2026-07-13):
    Bronze as drawn, Gold and Silver through the selective-swap disk
    cache, Colored from its own art when it exists."""
    looks = [
        ("Bronze", base),
        ("Gold", metal_variant_file(base, "gold")),
        ("Silver", metal_variant_file(base, "silver")),
    ]
    if colored is not None and colored.exists():
        looks.append(("Colored", colored))
    return tuple(looks)


def _weekday_topic(theme: str):
    """(icon path, entries) for one weekday theme: seven bodies in
    week order with their themed art, display names and article set —
    the SUN pairs the Ruler plate with its Servant face, and the metal
    themes carry the four-look arrows."""
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
    metal = theme in constants.METAL_THEMES
    week_order = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
    dual = defaults.WEEKDAY_ART_DIR / f"{defaults.WEEKDAY_DUAL_FILES[theme]}.png"
    entries = []
    for body in week_order:
        base = directory / f"{files[body]}.png"
        images = (base, dual) if body == "sun" and dual.exists() else (base,)
        entry = {
            "images": images,
            "name": names[body],
            "article": ("article", article_set, body),
            "accents": defaults.BODY_ACCENT_HUES[body],
        }
        if metal:
            colored_dir = directory / "colored"
            if body == "sun" and dual.exists():
                folder, _, stem = defaults.WEEKDAY_DUAL_FILES[theme].rpartition("/")
                dual_colored = (
                    defaults.WEEKDAY_ART_DIR / folder / "colored" / f"{stem}.png"
                )
                entry["looks"] = tuple(
                    (label, (one, two))
                    for (label, one), (_, two) in zip(
                        _looks(base, colored_dir / f"{files[body]}.png"),
                        _looks(dual, dual_colored),
                    )
                )
            else:
                entry["looks"] = tuple(
                    (label, (path,))
                    for label, path in _looks(
                        base, colored_dir / f"{files[body]}.png"
                    )
                )
        entries.append(entry)
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
                # The animals wear the four looks too (bronze plate,
                # the two swaps, the colored art).
                "looks": tuple(
                    (label, (path,))
                    for label, path in _looks(
                        defaults.ZODIAC_ART_DIR / "chinese" / f"{animal}.png",
                        defaults.ZODIAC_ART_DIR / "chinese_colored"
                        / f"{animal}.png",
                    )
                ),
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
    # THE CLOCK (owner expansion 2026-07-13): the Week day pages and
    # the Instrument functionality articles — names and texts live in
    # Database/encyclopedia.json and resolve lazily per entry.
    topics["week"] = {
        "title": "The Week",
        "icon": defaults.WEEKDAY_ART_DIR / "planets" / "sun.png",
        "entries": [
            {
                "images": (
                    defaults.WEEKDAY_ART_DIR / "planets" / f"{body}.png",
                    defaults.WEEKDAY_ART_DIR / "planet_signs" / f"{body}.png",
                    *(
                        defaults.EMBLEM_ART_DIRS[family] / f"{name}.png"
                        for family, names in zip(
                            ("virtues", "sins", "moods"),
                            _WEEK_EMBLEMS[body],
                        )
                        for name in names
                    ),
                ),
                "name": ("week_title", body),
                "article": ("week", body),
                "accents": defaults.BODY_ACCENT_HUES[body],
            }
            for body in (
                "sun", "moon", "mars", "mercury", "jupiter", "venus",
                "saturn",
            )
        ],
    }
    topics["instrument"] = {
        "title": "The Instrument",
        "icon": None,
        "entries": [
            {
                "images": (),
                "name": ("instrument_title", key),
                "article": ("instrument", key),
                "accents": (),
            }
            for key in _INSTRUMENT_KEYS
        ],
    }
    # THE INNER WHEEL: one entry per emblem, its logo above its text.
    for family in ("virtues", "sins", "moods"):
        topics[family] = {
            "title": family.capitalize(),
            "icon": (
                defaults.EMBLEM_ART_DIRS[family]
                / f"{_VSM_DAYS[family][0]}.png"
            ),
            "entries": [
                {
                    "images": (
                        defaults.EMBLEM_ART_DIRS[family]
                        / f"{name}.png",
                    ),
                    "name": name,
                    "article": ("emblem", family, name),
                    "accents": (),
                }
                for name in _VSM_DAYS[family]
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
        self._encyclopedia = EncyclopediaRepository(overlay=self._overlay)
        self._topics = _topics()
        self._cells: list[dict] = []
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
        if kind == "week":
            return self._encyclopedia.week(ref[1])["base"]
        if kind == "instrument":
            return self._encyclopedia.instrument(ref[1])["base"]
        if kind == "emblem":
            return self._encyclopedia.entry(ref[1], ref[2])["base"]
        return self._symbolism.trio_article(ref[1])["base"]

    def _entry_name(self, entry: dict) -> str:
        """An entry's display name: the WEEK and INSTRUMENT pages take
        their titles from the encyclopedia database (localized there);
        everything else translates through the UI overlay."""
        name = entry["name"]
        if isinstance(name, tuple):
            if name[0] == "week_title":
                return self._encyclopedia.week(name[1])["title"]
            return self._encyclopedia.instrument(name[1])["title"]
        return self._tr(name)

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
            # LOOKS (owner 2026-07-13): a metal entry cycles Bronze /
            # Gold / Silver / Colored with the arrow buttons; a plain
            # entry is a one-look list.
            looks = entry.get("looks") or (("", tuple(entry["images"])),)
            look_pixmaps = [
                [
                    QPixmap(str(path))
                    for path in paths_
                    if path is not None and Path(path).exists()
                ]
                for _, paths_ in looks
            ]
            state = {
                "labels": [],
                "looks": look_pixmaps,
                "titles": [label for label, _ in looks],
                "index": 0,
                "caption": None,
            }
            count = max((len(p) for p in look_pixmaps), default=0)
            if count:
                images_row = QHBoxLayout()
                images_row.setSpacing(defaults.GUIDE_SPACING_PX * 2)
                images_row.addStretch(1)
                for _ in range(count):
                    label = QLabel()
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    state["labels"].append(label)
                    images_row.addWidget(label)
                images_row.addStretch(1)
                cell.addLayout(images_row)
                self._cells.append(state)
            if len(look_pixmaps) > 1:
                arrows = QHBoxLayout()
                arrows.addStretch(1)
                back = QToolButton()
                back.setText("◀")
                caption = QLabel(self._tr(state["titles"][0]))
                caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
                caption.setMinimumWidth(80)
                state["caption"] = caption
                forward = QToolButton()
                forward.setText("▶")
                back.clicked.connect(
                    lambda checked=False, s=state: self._cycle_look(s, -1)
                )
                forward.clicked.connect(
                    lambda checked=False, s=state: self._cycle_look(s, 1)
                )
                arrows.addWidget(back)
                arrows.addWidget(caption)
                arrows.addWidget(forward)
                arrows.addStretch(1)
                cell.addLayout(arrows)
            name = QLabel(f"<b>{self._entry_name(entry)}</b>")
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
        for state in self._cells:
            self._render_cell(state, block_width)

    def _render_cell(self, state: dict, block_width: int) -> None:
        """Draw the cell's CURRENT look into its labels (scaled to the
        block width, siblings splitting it)."""
        pixmaps = state["looks"][state["index"]]
        siblings = max(1, len(pixmaps))
        for label, art in zip(state["labels"], pixmaps):
            share = block_width // siblings - defaults.GUIDE_SPACING_PX * 2
            width = min(max(120, share), art.width())
            label.setPixmap(
                art.scaledToWidth(
                    width, Qt.TransformationMode.SmoothTransformation
                )
            )
        for label in state["labels"][len(pixmaps):]:
            label.clear()

    def _cycle_look(self, state: dict, step: int) -> None:
        """The ◀ / ▶ arrows (owner 2026-07-13): the next metal look of
        this entry, caption updated."""
        state["index"] = (state["index"] + step) % len(state["looks"])
        if state["caption"] is not None:
            state["caption"].setText(
                self._tr(state["titles"][state["index"]])
            )
        block_width = round(
            max(320, self._scroll.viewport().width())
            * defaults.ENCYCLOPEDIA_TEXT_WIDTH_FRACTION
        )
        self._render_cell(state, block_width)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rescale()
