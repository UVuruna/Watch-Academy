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

from PySide6.QtCore import QSize, Qt
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

import html as _html

from config import constants, defaults
from config.ui_text import ui
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository
from render.assets import metal_variant_file
from render.compositor import _HEX_NOTE, _highlight_terms


def _flow_html(text: str, accents: tuple = ()) -> str:
    """Article prose that REFLOWS with the window (owner 2026-07-13:
    the paragraphs span the block and re-wrap live) — no fixed
    character wrap; QLabel's word wrap fills the width. Canon terms
    highlighted, hex notes stripped, left-aligned."""
    text = _HEX_NOTE.sub("", text)
    paragraphs = [
        _highlight_terms(_html.escape(paragraph), accents)
        for paragraph in text.split("\n\n")
    ]
    return "<div align='left'>" + "<br/><br/>".join(paragraphs) + "</div>"

# The gallery groups (owner UX rounds 2026-07-12/13): the clock's own
# story first, gods together, the zodiac family with the planets and
# their signs, the remaining week themes with the Trinity, the
# religions, and the cross-cure emblem families last.
_TOPIC_GROUPS = (
    ("The Clock", ("week", "instrument", "seasons")),
    ("Gods", ("greek", "norse", "egypt", "slavic")),
    ("Zodiac", ("astrology", "chinese", "planets", "planet_signs")),
    ("Themes", ("alchemy", "japan", "profession", "trinity")),
    ("Religions", ("religion", "religion_alt")),
    ("Animal Societies", ("wolf", "bee", "elephant")),
    ("The Inner Wheel", ("virtues", "sins", "moods", "duality")),
)

# The SEASONS topic (owner 2026-07-13): the year's quarters, the
# tropics' halves, the turning points and the measured twins — badges
# from assets/season/, articles from encyclopedia.json.
_SEASON_ENTRIES = (
    ("Spring", "Spring.png"),
    ("Summer", "Summer.png"),
    ("Autumn", "Autumn.png"),
    ("Winter", "Winter.png"),
    ("Wet_Season", "Wet_Season.png"),
    ("Dry_Season", "Dry_Season.png"),
    ("Summer_Solstice", "turning_point/Summer_Solstice.png"),
    ("Winter_Solstice", "turning_point/Winter_Solstice.png"),
    ("Equinox", "turning_point/Equinox.png"),
    ("Meteorological", None),          # four badges in one entry
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
_INSTRUMENT_KEYS = (
    "dial", "solar_rotation", "twilight", "year_wheel", "moon_lunations",
    "paint_light", "metals", "ring_letters",
)


_WEEK_ORDER = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")


def _metal_looks(base: Path, colored: Path | None) -> tuple:
    """The four LOOKS of a bronze-plate image (owner 2026-07-13),
    COLORED FIRST — the owner's default — then Bronze as drawn and
    the two selective-swap disk-cache variants."""
    looks = []
    if colored is not None and colored.exists():
        looks.append(("Colored", colored))
    looks += [
        ("Bronze", base),
        ("Gold", metal_variant_file(base, "gold")),
        ("Silver", metal_variant_file(base, "silver")),
    ]
    return tuple(looks)


def _theme_body_art(theme: str, body: str) -> Path:
    """One theme's plate for one body (bronze / canon file)."""
    if theme == "planets":
        return defaults.WEEKDAY_ART_DIR / "planets" / f"{body}.png"
    return (
        defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        / f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
    )


def _theme_dual_art(theme: str, colored: bool = False) -> Path:
    """The theme's Sunday SERVANT plate (colored variant on demand)."""
    rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if colored:
        folder, _, stem = rel.rpartition("/")
        return defaults.WEEKDAY_ART_DIR / folder / "colored" / f"{stem}.png"
    return defaults.WEEKDAY_ART_DIR / f"{rel}.png"


def _weekday_topic(theme: str):
    """(icon path, entries) for one weekday theme: seven bodies in
    week order. Every look is a tuple of ROWS — the sun's two plates
    stand SIDE BY SIDE, Ruler left, Servant right (owner correction
    2026-07-13: never stacked); the metal themes cycle Colored/Bronze/
    Gold/Silver; the planets cycle their photos and the sign glyphs."""
    article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
    if theme == "planets":
        names = defaults.DEFAULT_SKIN.weekday_set.body_names
    else:
        names = defaults.WEEKDAY_THEME_NAMES[theme]
    metal = theme in constants.METAL_THEMES
    entries = []
    for body in _WEEK_ORDER:
        base = _theme_body_art(theme, body)
        sun = body == "sun"

        def rows(ruler: Path, servant: Path | None) -> tuple:
            if servant is not None and servant.exists():
                return ((ruler, servant),)
            return ((ruler,),)

        entry = {
            "looks": ((
                "", rows(base, _theme_dual_art(theme) if sun else None),
            ),),
            "name": names[body],
            "article": ("article", article_set, body),
            "accents": defaults.BODY_ACCENT_HUES[body],
        }
        if metal:
            colored = (
                defaults.WEEKDAY_ART_DIR
                / defaults.WEEKDAY_THEME_DIRS[theme] / "colored"
                / f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
            )
            if sun:
                entry["looks"] = tuple(
                    (label, rows(one, two))
                    for (label, one), (_, two) in zip(
                        _metal_looks(base, colored),
                        _metal_looks(
                            _theme_dual_art(theme),
                            _theme_dual_art(theme, colored=True),
                        ),
                    )
                )
            else:
                entry["looks"] = tuple(
                    (label, rows(path, None))
                    for label, path in _metal_looks(base, colored)
                )
        elif theme == "planets":
            # Owner defaults 2026-07-13: the photos lead, the sign
            # glyphs ride the arrows.
            sign = defaults.WEEKDAY_ART_DIR / "planet_signs" / f"{body}.png"
            sign_dual = (
                defaults.WEEKDAY_ART_DIR / "planet_signs" / "dual"
                / "sun_eclipse.png"
            )
            entry["looks"] = (
                ("Planets", rows(base, _theme_dual_art("planets") if sun else None)),
                ("Signs", rows(sign, sign_dual if sun else None)),
            )
        entries.append(entry)
    return _theme_body_art(theme, "sun"), entries


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
                # Owner defaults 2026-07-13: the logo+constellation pair
                # leads; the arrows reach the colored logo and the sign.
                "looks": (
                    ("Logo & Constellation", ((
                        defaults.ZODIAC_ART_DIR / "logo" / f"{sign}.png",
                        defaults.ZODIAC_ART_DIR / "constellation"
                        / f"{sign}.png",
                    ),)),
                    ("Colored", ((
                        defaults.ZODIAC_ART_DIR / "logo_colored"
                        / f"{sign}.png",
                    ),)),
                    ("Sign", ((
                        defaults.ZODIAC_ART_DIR / "sign" / f"{sign}.png",
                    ),)),
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
                "name": animal,
                "article": ("chinese", animal),
                "accents": (),
                # The animals wear the four looks too — BRONZE first
                # (owner default 2026-07-13), the swaps and the
                # colored art on the arrows.
                "looks": tuple(
                    (label, ((path,),))
                    for label, path in (
                        ("Bronze",
                         defaults.ZODIAC_ART_DIR / "chinese"
                         / f"{animal}.png"),
                        ("Gold", metal_variant_file(
                            defaults.ZODIAC_ART_DIR / "chinese"
                            / f"{animal}.png", "gold")),
                        ("Silver", metal_variant_file(
                            defaults.ZODIAC_ART_DIR / "chinese"
                            / f"{animal}.png", "silver")),
                        ("Colored",
                         defaults.ZODIAC_ART_DIR / "chinese_colored"
                         / f"{animal}.png"),
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
    # Database/encyclopedia.json and resolve lazily per entry. The
    # image strip GROUPS by kinship on the arrows (owner: "nećemo da
    # nabacamo sve teme — grupišemo po srodnosti"): the canon strip
    # (planet, sign and the day's emblems), then the gods, the
    # religions and the craft themes; Sunday puts every pair SIDE BY
    # SIDE — Ruler immediately left of its Servant (owner correction
    # 2026-07-13: never stacked).
    def _week_theme_rows(body: str, themes: tuple) -> tuple:
        if body != "sun":
            return (tuple(_theme_body_art(t, body) for t in themes),)
        return (tuple(
            plate
            for t in themes
            for plate in (_theme_body_art(t, "sun"), _theme_dual_art(t))
        ),)

    def _week_canon_rows(body: str) -> tuple:
        virtue, sin, mood = _WEEK_EMBLEMS[body]
        if body != "sun":
            return ((
                _theme_body_art("planets", body),
                _theme_body_art("planet_signs", body),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[0]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[0]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[0]}.png",
            ),)
        return ((
            _theme_body_art("planets", "sun"),
            _theme_dual_art("planets"),
            _theme_body_art("planet_signs", "sun"),
            _theme_dual_art("planet_signs"),
            defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[0]}.png",
            defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[1]}.png",
            defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[0]}.png",
            defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[1]}.png",
            defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[0]}.png",
            defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[1]}.png",
        ),)

    topics["week"] = {
        "title": "The Week",
        "icon": defaults.WEEKDAY_ART_DIR / "planets" / "sun.png",
        "entries": [
            {
                "looks": (
                    ("Canon", _week_canon_rows(body)),
                    ("Gods", _week_theme_rows(
                        body, ("greek", "norse", "egypt", "slavic")
                    )),
                    ("Religions", _week_theme_rows(
                        body, ("religion", "religion_alt")
                    )),
                    ("Themes", _week_theme_rows(
                        body, ("profession", "alchemy", "japan")
                    )),
                    ("Animals", _week_theme_rows(
                        body, ("wolf", "bee", "elephant")
                    )),
                ),
                "name": ("week_title", body),
                "article": ("week", body),
                "accents": defaults.BODY_ACCENT_HUES[body],
            }
            for body in _WEEK_ORDER
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
    # THE TWO TRIANGLES (owner 2026-07-13): the Judas–Lucifer scale —
    # the two fallen extremes of self and the zero no individual
    # reaches. The badge art is wired ahead of its landing (missing
    # files stay hidden); the Union pairs both triangles.
    topics["duality"] = {
        "title": "The Two Triangles",
        "icon": defaults.SCALE_ART_DIR / "Lucifer_Triangle.png",
        "entries": [
            {
                "images": (
                    defaults.SCALE_ART_DIR / "Lucifer_Triangle.png",
                ),
                "name": "Lucifer",
                "article": ("emblem", "duality", "Lucifer"),
                "accents": ("red",),
            },
            {
                "images": (
                    defaults.SCALE_ART_DIR / "Judas_Triangle.png",
                ),
                "name": "Judas",
                "article": ("emblem", "duality", "Judas"),
                "accents": ("blue",),
            },
            {
                "images": (
                    defaults.SCALE_ART_DIR / "Judas_Triangle.png",
                    defaults.SCALE_ART_DIR / "Lucifer_Triangle.png",
                ),
                "name": "The Union",
                "article": ("emblem", "duality", "The Union"),
                "accents": ("red", "blue"),
            },
        ],
    }
    topics["trinity"] = {
        "title": "Trinity",
        "icon": defaults.TRINITY_ART_DIR / "Faith.png",
        "entries": [
            {
                # The trinity badges landed 2026-07-13 — each virtue
                # wears its triskelion emblem above the article.
                "images": (defaults.TRINITY_ART_DIR / f"{virtue}.png",),
                "name": virtue,
                "article": ("trio", virtue),
                "accents": defaults.TRIO_ACCENT_HUES[virtue],
            }
            for virtue in ("Faith", "Hope", "Love")
        ],
    }
    topics["seasons"] = {
        "title": "Seasons",
        "icon": defaults.SEASON_ART_DIR / "Summer.png",
        "entries": [
            {
                "images": (
                    tuple(
                        defaults.SEASON_ART_DIR / "meteorological"
                        / f"{season}.png"
                        for season in ("Spring", "Summer", "Autumn",
                                       "Winter")
                    )
                    if art is None
                    else (defaults.SEASON_ART_DIR / art,)
                ),
                "name": ("season_title", key),
                "article": ("season", key),
                "accents": (),
            }
            for key, art in _SEASON_ENTRIES
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
        # A NORMAL window (owner 2026-07-13: no stay-on-top — it must
        # yield to whatever has focus, like any other application).
        # Maximize/minimize live in the title bar (owner 2026-07-13:
        # "treba button maximize da se proširi preko celog ekrana").
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self._symbolism = SymbolismRepository(overlay=self._overlay)
        self._encyclopedia = EncyclopediaRepository(overlay=self._overlay)
        self._topics = _topics()
        self._cells: list[dict] = []
        self._blocks: list[QWidget] = []
        self._text_labels: list[QLabel] = []
        self._name_labels: list[QLabel] = []
        self._topic_cards: list[QToolButton] = []
        self._pixmap_cache: dict[str, QPixmap] = {}

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
        if kind == "season":
            return self._encyclopedia.season(ref[1])["base"]
        if kind == "emblem":
            return self._encyclopedia.entry(ref[1], ref[2])["base"]
        return self._symbolism.trio_article(ref[1])["base"]

    def _entry_name(self, entry: dict) -> str:
        """An entry's display name: the WEEK, INSTRUMENT and SEASONS
        pages take their titles from the encyclopedia database
        (localized there); everything else translates through the UI
        overlay."""
        name = entry["name"]
        if isinstance(name, tuple):
            if name[0] == "week_title":
                return self._encyclopedia.week(name[1])["title"]
            if name[0] == "season_title":
                return self._encyclopedia.season(name[1])["title"]
            return self._encyclopedia.instrument(name[1])["title"]
        return self._tr(name)

    def _show_topics(self) -> None:
        """Screen 1 — the topic gallery in the owner's groups,
        EVERYTHING centered (owner 2026-07-13: headers and cards
        alike); the card icons are RESPONSIVE — _rescale grows and
        shrinks them with the window between the two bounds, and only
        below the minimum does the scrollbar take over."""
        self._title.setText(self._tr("Encyclopedia"))
        self._back.hide()
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        self._topic_cards = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX)
        for group_title, keys in _TOPIC_GROUPS:
            header = QLabel(self._tr(group_title))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            row = QHBoxLayout()
            row.setSpacing(defaults.GUIDE_SPACING_PX * 2)
            row.addStretch(1)
            for key in keys:
                topic = self._topics[key]
                card = QToolButton()
                card.setToolButtonStyle(
                    Qt.ToolButtonStyle.ToolButtonTextUnderIcon
                )
                card.setText(self._tr(topic["title"]))
                if topic["icon"] is not None and Path(topic["icon"]).exists():
                    # The FULL-RES art backs the icon — QIcon renders
                    # whatever size _rescale asks for.
                    card.setIcon(QIcon(str(topic["icon"])))
                card.clicked.connect(
                    lambda checked=False, chosen=key: self._show_topic(chosen)
                )
                row.addWidget(card)
                self._topic_cards.append(card)
            row.addStretch(1)
            column.addLayout(row)
        column.addStretch(1)
        self._scroll.setWidget(content)
        self._rescale()

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
        self._topic_cards = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX * 3)
        for entry in topic["entries"]:
            block = QWidget()
            cell = QVBoxLayout(block)
            cell.setContentsMargins(0, 0, 0, 0)
            cell.setSpacing(defaults.GUIDE_SPACING_PX)
            # LOOKS (owner 2026-07-13): every look is a tuple of ROWS —
            # the Sunday pairs stand side by side; the arrows page
            # through kinship groups or metal finishes. Only PATHS are
            # kept here — the pixmaps decode lazily in _render_cell
            # (owner 2026-07-13: The Week opened far too slowly when
            # every look of every entry loaded upfront).
            looks = entry.get("looks") or (
                ("", (tuple(entry.get("images", ())),)),
            )
            look_rows = [
                [
                    [
                        path
                        for path in row
                        if path is not None and Path(path).exists()
                    ]
                    for row in rows
                ]
                for _, rows in looks
            ]
            titles = [label for label, _ in looks]
            keep = [
                index for index, rows in enumerate(look_rows)
                if any(rows)
            ]
            look_rows = [look_rows[index] for index in keep]
            titles = [titles[index] for index in keep]
            state = {
                "container": None,
                "looks": look_rows,
                "titles": titles,
                "index": 0,
                "caption": None,
            }
            if look_rows:
                container = QWidget()
                state["container"] = container
                cell.addWidget(
                    container, alignment=Qt.AlignmentFlag.AlignHCenter
                )
                self._cells.append(state)
            if len(look_rows) > 1:
                arrows = QHBoxLayout()
                arrows.addStretch(1)
                back = QToolButton()
                back.setText("◀")
                caption = QLabel(self._tr(state["titles"][0]))
                caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
                caption.setMinimumWidth(120)
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
                _flow_html(
                    self._article_text(entry["article"]),
                    accents=entry["accents"],
                )
            )
            text.setWordWrap(True)
            text.setTextFormat(Qt.TextFormat.RichText)
            self._text_labels.append(text)
            cell.addWidget(text)
            self._blocks.append(block)
            # The block HUGS THE LEFT EDGE (owner 2026-07-13) — only
            # the images/name center within it.
            column.addWidget(block, alignment=Qt.AlignmentFlag.AlignLeft)
        self._scroll.setWidget(content)
        self._scroll.verticalScrollBar().setValue(0)
        self._rescale()

    def _rescale(self) -> None:
        """Everything follows the window — on the gallery the card
        icons resize between their bounds; on a topic each entry BLOCK
        spans the configured width fraction, the images share the
        block, and the font grows with the width at the gentle em-like
        coefficient."""
        if self._topic_cards:
            self._rescale_topics()
            return
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

    def _rescale_topics(self) -> None:
        """The gallery cards follow the window (owner 2026-07-13):
        the icon side grows until the widest group fills the WIDTH or
        the stacked groups fill the HEIGHT — whichever bound bites
        first — clamped between the two configured sizes; below the
        minimum the scroll area takes over."""
        viewport = self._scroll.viewport()
        columns = max(len(keys) for _, keys in _TOPIC_GROUPS)
        spacing = defaults.GUIDE_SPACING_PX * 2
        width_share = (
            (viewport.width() - 48) // columns - spacing
        )
        # Per-group vertical overhead: header + rule + the card's own
        # caption line + spacings (estimate — the scrollbar catches
        # whatever the estimate misses).
        overhead = defaults.GUIDE_SUBTITLE_PX + 2 + 64
        height_share = viewport.height() // len(_TOPIC_GROUPS) - overhead
        icon = max(
            defaults.ENCYCLOPEDIA_TOPIC_ICON_MIN_PX,
            min(
                defaults.ENCYCLOPEDIA_TOPIC_ICON_MAX_PX,
                width_share,
                height_share,
            ),
        )
        for card in self._topic_cards:
            card.setIconSize(QSize(icon, icon))
            card.setMinimumSize(icon + 40, icon + 44)
        # Commit the new card geometry NOW (owner bug 2026-07-13: the
        # first open drew the groups overlapping — the rows kept their
        # pre-show heights until a manual resize forced a relayout).
        content = self._scroll.widget()
        if content is not None and content.layout() is not None:
            content.layout().activate()
            content.adjustSize()

    def _pixmap(self, path) -> QPixmap:
        """The decoded-image cache behind the lazy looks (owner
        2026-07-13: The Week opened far too slowly): a look decodes
        on FIRST display, then the cache answers — paths were already
        filtered for existence."""
        key = str(path)
        pixmap = self._pixmap_cache.get(key)
        if pixmap is None:
            pixmap = QPixmap(key)
            self._pixmap_cache[key] = pixmap
        return pixmap

    def _render_cell(self, state: dict, block_width: int) -> None:
        """Rebuild the cell's image GRID for its current look: each
        look is rows of image paths (the Sunday pairs side by side);
        the columns split the block width and the images SHRINK as
        far as needed (owner 2026-07-13: nothing may overlap or
        clip)."""
        container = state["container"]
        if container is None:
            return
        old = container.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            QWidget().setLayout(old)     # detach so a fresh grid can bind
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(defaults.GUIDE_SPACING_PX)
        rows = state["looks"][state["index"]]
        columns = max((len(row) for row in rows), default=0)
        if not columns:
            return
        share = (
            block_width // columns - defaults.GUIDE_SPACING_PX * 2
        )
        for row_index, row in enumerate(rows):
            offset = (columns - len(row)) // 2    # center shorter rows
            for col_index, path in enumerate(row):
                art = self._pixmap(path)
                label = QLabel()
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                width = max(24, min(share, art.width()))
                label.setPixmap(
                    art.scaledToWidth(
                        width, Qt.TransformationMode.SmoothTransformation
                    )
                )
                grid.addWidget(
                    label, row_index, offset + col_index,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )
        # Commit the new geometry NOW (owner bug 2026-07-13: after a
        # look switch to larger art the container kept its old size —
        # the image drew clipped under the neighboring widgets).
        grid.activate()
        container.updateGeometry()
        container.adjustSize()

    def _cycle_look(self, state: dict, step: int) -> None:
        """The ◀ / ▶ arrows (owner 2026-07-13): the next look of this
        entry — a metal finish or a kinship group — caption updated."""
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

    def showEvent(self, event) -> None:
        # The gallery is built BEFORE the window has its real geometry
        # — rescale once more on the first show (owner bug 2026-07-13:
        # deformed until a manual resize).
        super().showEvent(event)
        self._rescale()
