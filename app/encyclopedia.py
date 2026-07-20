"""Encyclopedia — the article browser (owner spec 2026-07-12; expansion
2026-07-13).

Screen 1 is a gallery of TOPICS in GROUPS — THE CLOCK first (the Week
day pages and the Instrument functionality articles), then Gods /
Zodiac / Themes / Religions, and THE INNER WHEEL last (Virtues, Sins,
Moods with their emblem logos); screen 2 is a SLIDER (owner plan round
E, 2026-07-14): the topic's articles page ONE AT A TIME like the Guide
— ← Previous / Next → wrap around, a counter sits between them and a
BIG Back button leads home. Each page shows the entry's image(s), bold
name and full base text — translated through the active overlay and
with the canon terms highlighted exactly like the dial legends. The whole article BLOCK is centered and spans a
fraction of the window width; the font grows gently with the window
(em-like coefficient). Astrology shows BOTH the sign logo and its
constellation side by side; the SUN entries pair the Ruler plate with
the Servant face. Metal themes (and the Chinese animals) carry LOOK
ARROWS — Bronze / Gold / Silver / Colored cycled per entry (owner
2026-07-13: "sve slike od te teme, može skrol levo desno strelice").
Resizable: everything rescales live.
"""

import json
import shutil
from datetime import date
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
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

from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults, paths
from config.ui_text import ui
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository
from render.assets import metal_variant_file, moon_phase_file
from render.compositor import _HEX_NOTE, _SUBHEAD, _highlight_terms


def _flow_html(text: str, accents: tuple = (), tr=None) -> str:
    """Article prose that REFLOWS with the window (owner 2026-07-13:
    the paragraphs span the block and re-wrap live) — no fixed
    character wrap; QLabel's word wrap fills the width. Canon terms
    highlighted, hex notes stripped, JUSTIFIED like the legend, and
    [[Subhead]] markers drawn as bold headings (owner 2026-07-14;
    `tr` localizes the label)."""
    text = _HEX_NOTE.sub("", text)
    parts = []
    for paragraph in text.split("\n\n"):
        match = _SUBHEAD.match(paragraph)
        body_style = ""
        if match:
            label = match.group(1)
            if tr is not None:
                label = tr(label)
            # CENTERED, hugging its own paragraph (owner 2026-07-14
            # round two — same rule as the hover legends).
            parts.append(
                "<p align='center' style='"
                f"margin-top:{defaults.ARTICLE_SUBHEAD_GAP_ABOVE_PX}px;"
                f"margin-bottom:{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'>"
                f"<b>{_html.escape(label)}</b></p>"
            )
            paragraph = paragraph[match.end():]
            body_style = (
                f" style='margin-top:"
                f"{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'"
            )
        parts.append(
            f"<p align='justify'{body_style}>"
            + _highlight_terms(_html.escape(paragraph), accents)
            + "</p>"
        )
    return "<div>" + "".join(parts) + "</div>"

# The gallery groups (owner UX rounds 2026-07-12/13): the clock's own
# story first, gods together, the zodiac family with the planets and
# their signs, the remaining week themes with the Trinity, the
# religions, and the cross-cure emblem families last.
_TOPIC_GROUPS = (
    ("The Clock",
     ("week", "instrument", "moon", "seasons", "sun", "era",
      "eclipse_solar", "eclipse_lunar")),
    ("Gods", ("greek", "norse", "egypt", "slavic")),
    # THE WIDER PANTHEON (owner 2026-07-15, WORKPLAN Session 8): one
    # topic per culture for the A-list figures no dial seat could hold
    # — the seatless famous names, plus the retired ninths whose
    # written material folds in here (Set, Baldur, Crnobog). Seated
    # figures keep their weekday topics; these carry only the omitted.
    ("The Wider Pantheon",
     ("wider_greek", "wider_norse", "wider_egypt", "wider_slavic")),
    ("Zodiac", ("astrology", "chinese", "planets", "planet_signs")),
    ("Themes", ("alchemy", "japan", "profession", "trinity", "cosmos")),
    ("Creeds & Mysteries", ("religion", "religion_alt")),
    ("Scripture", ("bible", "bible2", "bible_dark")),
    ("Animal Societies", ("wolf", "bee", "elephant")),
    ("The Inner Wheel",
     ("virtues", "sins", "moods", "duality", "intelligences")),
)

# The SEASONS topic (owner 2026-07-13; split 2026-07-16, ROADMAP queue
# #10): the year's quarters, the tropics' halves and the measured twins
# — the turning points moved to the SUN topic below. Badges from
# assets/badge/season/, articles from encyclopedia.json.
_SEASON_ENTRIES = (
    ("Spring", "Spring.png"),
    ("Summer", "Summer.png"),
    ("Autumn", "Autumn.png"),
    ("Winter", "Winter.png"),
    ("Wet_Season", "Wet_Season.png"),
    ("Dry_Season", "Dry_Season.png"),
    ("Meteorological", None),          # four badges in one entry
)

# The SUN topic (owner 2026-07-16, ROADMAP queue #10): the turning
# points — the two solstices and the shared-badge equinox.
_SUN_ENTRIES = (
    ("Summer_Solstice", "turning_point/Summer_Solstice.png"),
    ("Winter_Solstice", "turning_point/Winter_Solstice.png"),
    ("Equinox", "turning_point/Equinox.png"),
)

# The ERA TERMS topic (ROADMAP 15a3, owner 2026-07-17): the two AGES
# and the four STARRY SEASONS carry an emblem each. Badges from
# assets/era/ (research/prompts/era/era_prompts.md).
# The comparative "Eras of the World" essay carries no plate of its
# own — instead it strings the calendar-system emblems the essay
# compares (owner fix-round B, 2026-07-19, TASK 3; Maya added the MAYA
# round, owner 2026-07-20; Kali Yuga/Olympiad/Unix added the ERA-TRIO
# round, owner 2026-07-20): graceful-absent until PromptPainter
# generates assets/era/calendar/*.png. Every entry here (Byzantine
# included) rotates through `_era_image` below like the six Age/Starry
# plates — the Byzantine v2 emblem (ERA-TRIO round) is a same-named
# `calendar/alt/Byzantine.png` sibling, discovered automatically, no
# second entry needed here.
_ERA_CALENDAR_ART = (
    "calendar/AUC.png",
    "calendar/Byzantine.png",
    "calendar/Hebrew.png",
    "calendar/Hegirae.png",
    "calendar/Buddhist.png",
    "calendar/Huangdi.png",
    "calendar/Maya.png",
    "calendar/KaliYuga.png",
    "calendar/Olympiad.png",
    "calendar/Unix.png",
)
_ERA_ENTRIES = (
    ("Age_of_Light", "Age_of_Light.png"),
    ("Age_of_Darkness", "Age_of_Darkness.png"),
    ("Starry_Spring", "Starry_Spring.png"),
    ("Starry_Summer", "Starry_Summer.png"),
    ("Starry_Autumn", "Starry_Autumn.png"),
    ("Starry_Winter", "Starry_Winter.png"),
    ("Eras_of_the_World", _ERA_CALENDAR_ART),
    # The Great Oscillations (fix round F, owner "bravo"): the season-
    # length / Milankovitch essay near the Observatory — an ESSAY, no
    # plate of its own (like the comparative Eras article), None -> ().
    ("The_Great_Oscillations", None),
)

# THE ECLIPSES ENCYCLOPEDIA (fix round F, owner order 2026-07-19:
# "posebno za mesec i sunce"): two topics, one per body, each opened
# by a per-body OVERVIEW (the entry-zero — a whole-phenomenon page a
# reader meets before the specific kinds) then one chapter per category
# we distinguish. Each category chapter wears its OWN category emblem
# (assets/eclipse/<Stem>.png, graceful-absent); the overview strings its
# body's category emblems as a strip, like the Eras essay. The chapter
# ORDER here is the golden the Spacebar jump indexes into
# (render.compositor._ENC_ECLIPSE_SOLAR_ORDER / _LUNAR_ORDER) — keep
# them in lockstep.
_ECLIPSE_SOLAR_EMBLEMS = (
    "Solar_Total.png", "Solar_Annular.png",
    "Solar_Partial.png", "Solar_Hybrid.png",
)
_ECLIPSE_LUNAR_EMBLEMS = (
    "Lunar_Total.png", "Lunar_Partial.png", "Lunar_Penumbral.png",
)
_ECLIPSE_SOLAR_ENTRIES = (
    ("Solar_Overview", _ECLIPSE_SOLAR_EMBLEMS),
    ("Solar_Total", "Solar_Total.png"),
    ("Solar_Annular", "Solar_Annular.png"),
    ("Solar_Partial", "Solar_Partial.png"),
    ("Solar_Hybrid", "Solar_Hybrid.png"),
)
_ECLIPSE_LUNAR_ENTRIES = (
    ("Lunar_Overview", _ECLIPSE_LUNAR_EMBLEMS),
    ("Lunar_Total", "Lunar_Total.png"),
    ("Lunar_Partial", "Lunar_Partial.png"),
    ("Lunar_Penumbral", "Lunar_Penumbral.png"),
)
_ECLIPSE_TOPICS = (
    ("eclipse_solar", "Solar Eclipses", "Solar_Total.png",
     _ECLIPSE_SOLAR_ENTRIES),
    ("eclipse_lunar", "Lunar Eclipses", "Lunar_Total.png",
     _ECLIPSE_LUNAR_ENTRIES),
)

# The WEEK page image strip (owner spec: each day gathers everything it
# owns): planet render, planet sign, then the day's virtue / sin / mood
# emblems — Sunday, the dual day, carries both of each.
_WEEK_EMBLEMS = {
    "sun": (("Justice", "Humility"), ("Pride", "Servility"),
            ("Glory", "Awe")),
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
    "moods": ("Glory", "Awe", "Calm", "Zeal", "Sorrow", "Joy",
              "Passion", "Renewal"),
}
_INSTRUMENT_KEYS = (
    "dial", "solar_rotation", "twilight", "year_wheel", "moon_lunations",
    "paint_light", "metals", "ring_letters",
)


_WEEK_ORDER = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")

# THE WIDER PANTHEON (WORKPLAN Session 8): (topic key, gallery title,
# theme dir, icon plate, figure names). The figures are the culture's
# famous A-list gods that NEITHER roster seats (the pantheon catalog's
# Wider-Pantheon lane), reconciled against the round-four/five locks:
# figures the Pantheon roster went on to seat (Artemis, Hera, Frigg,
# Mokoš, Bastet) drop off, and the retired ninths whose canon moved
# them out of a seat fold back in (Set, Baldur, Crnobog). The already-
# plated Planetary figures (Hermes, Helios, Selene, Cronus, Amun,
# Khonsu, Montu, Sól, Máni, Hors) keep their own weekday topics and
# are not re-articled here (Rule #5). Each figure's article lives in
# the encyclopedia.json "wider" section; the plate is wired ahead of
# the art under <theme>/wider/ (missing files stay hidden, like every
# topic). The icon reuses the culture's existing ninth plate so the
# gallery card always shows a face.
_WIDER_TOPICS = (
    ("wider_greek", "Greek", "greek", "greek/pantheon/gaia.png",
     ("Dionysus", "Hephaestus", "Hestia")),
    ("wider_norse", "Norse", "norse", "norse/pantheon/Yggdrasil.png",
     ("Baldur", "Heimdall", "Njord")),
    ("wider_egypt", "Egyptian", "egypt", "egypt/pantheon/pharaoh.png",
     ("Set", "Nut", "Geb", "Ptah", "Sekhmet")),
    ("wider_slavic", "Slavic", "slavic", "slavic/primary/triglav.png",
     ("Crnobog", "Stribog", "Jarilo", "Rod")),
)


def _metal_looks(base: Path, colored: Path | None) -> tuple:
    """The four LOOKS of a bronze-plate image (owner 2026-07-13),
    COLORED FIRST — the owner's default — then Bronze as drawn and
    the two selective-swap disk-cache variants."""
    looks = []
    if colored is not None and paths.art_file(colored).exists():
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
        return (
            defaults.WEEKDAY_ART_DIR / "planets" / "primary"
            / f"{body}.png"
        )
    return (
        defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        / f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
    )


def _theme_dual_art(theme: str, colored: bool = False) -> Path:
    """The theme's Sunday SERVANT plate — the colored dual lives in
    the SIBLING variant (owner restructure 2026-07-14)."""
    rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if colored:
        rel = rel.replace("/primary/", "/colored/")
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
            if servant is not None and paths.art_file(servant).exists():
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
                / defaults.WEEKDAY_THEME_DIRS[theme]
            ).parent / "colored" / (
                f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
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
            # glyphs and the bronze medallions ride the arrows.
            sign = (
                defaults.WEEKDAY_ART_DIR / "planets" / "signs"
                / f"{body}.png"
            )
            sign_dual = (
                defaults.WEEKDAY_ART_DIR / "planets" / "signs"
                / "sun_eclipse.png"
            )
            art = (
                defaults.WEEKDAY_ART_DIR / "planets" / "art"
                / f"{body}.png"
            )
            art_dual = (
                defaults.WEEKDAY_ART_DIR / "planets" / "art"
                / "sun_eclipse.png"
            )
            entry["looks"] = (
                ("Planets", rows(base, _theme_dual_art("planets") if sun else None)),
                ("Signs", rows(sign, sign_dual if sun else None)),
                ("Art", rows(art, art_dual if sun else None)),
            )
        entries.append(entry)
    return _theme_body_art(theme, "sun"), entries


def _topics(travel_date: date | None = None) -> dict:
    """topic key -> {title, icon, entries}; article refs resolve lazily
    against the repository so the overlay always applies. Every entry
    carries an `images` TUPLE — Astrology pairs the sign logo with its
    constellation (owner spec: both, side by side). `travel_date`
    drives the Scale rotation (owner decree 2026-07-19/20, "koje cemo
    koristiti na smenu") — defaults to today when the caller has no
    Time Travel moment to hand in."""
    if travel_date is None:
        travel_date = date.today()
    topics: dict = {}
    for theme, title in defaults.WEEKDAY_THEME_TITLES.items():
        icon, entries = _weekday_topic(theme)
        topics[theme] = {"title": title, "icon": icon, "entries": entries}
    topics["astrology"] = {
        "title": "Astrology",
        "icon": defaults.ZODIAC_ART_DIR / "astrology" / "sign" / "Leo.png",
        "entries": [
            {
                # Owner defaults 2026-07-13: the logo+constellation pair
                # leads; the arrows reach the colored logo and the sign.
                "looks": (
                    ("Logo & Constellation", ((
                        defaults.ZODIAC_ART_DIR / "astrology" / "primary"
                        / f"{sign}.png",
                        defaults.ZODIAC_ART_DIR / "astrology"
                        / "constellation" / f"{sign}.png",
                    ),)),
                    ("Colored", ((
                        defaults.ZODIAC_ART_DIR / "astrology" / "colored"
                        / f"{sign}.png",
                    ),)),
                    ("Sign", ((
                        defaults.ZODIAC_ART_DIR / "astrology" / "sign"
                        / f"{sign}.png",
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
    chinese_primary = defaults.ZODIAC_ART_DIR / "chinese" / "primary"
    topics["chinese"] = {
        "title": "Chinese zodiac",
        "icon": chinese_primary / "Dragon.png",
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
                        ("Bronze", chinese_primary / f"{animal}.png"),
                        ("Gold", metal_variant_file(
                            chinese_primary / f"{animal}.png", "gold")),
                        ("Silver", metal_variant_file(
                            chinese_primary / f"{animal}.png", "silver")),
                        ("Colored",
                         defaults.ZODIAC_ART_DIR / "chinese" / "colored"
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
        # Sunday STACKS each pair (owner 2026-07-14: "Sun pa ispod
        # Eclipse, pa sledeća kolona nova tematika") — Rulers across
        # the top row, each Servant directly UNDER its Ruler.
        if body != "sun":
            return (tuple(_theme_body_art(t, body) for t in themes),)
        return (
            tuple(_theme_body_art(t, "sun") for t in themes),
            tuple(_theme_dual_art(t) for t in themes),
        )

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
        return (
            (
                _theme_body_art("planets", "sun"),
                _theme_body_art("planet_signs", "sun"),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[0]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[0]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[0]}.png",
            ),
            (
                _theme_dual_art("planets"),
                _theme_dual_art("planet_signs"),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[1]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[1]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[1]}.png",
            ),
        )

    topics["week"] = {
        "title": "The Week",
        "icon": defaults.WEEKDAY_ART_DIR / "planets" / "primary" / "sun.png",
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
        # The owner's gear-tooth section logo (2026-07-13); article
        # images join per key as they land (missing files stay hidden).
        "icon": defaults.INSTRUMENT_ART_DIR / "logo.png",
        "entries": [
            {
                "images": (
                    defaults.INSTRUMENT_ART_DIR / f"{key}.png",
                ),
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
    # The comparative WHEEL article leads the Moods topic (owner GO
    # 2026-07-14): humors -> Plutchik -> the dial's own eight, with
    # the owner's wheel plate as the illustration.
    topics["moods"]["entries"].insert(0, {
        "images": (
            defaults.EMBLEM_ART_DIRS["moods"] / "Wheel_of_Moods.png",
        ),
        "name": "The Wheel of Moods",
        "article": ("emblem", "moods", "The Wheel of Moods"),
        "accents": (),
    })
    # THE NINTH MOOD closes it (owner 8+1 structure, 2026-07-14):
    # Eclipse keeps its plate as the EVENT mood outside the eight
    # hours — the moment the Servant crosses the Ruler.
    topics["moods"]["entries"].append({
        "images": (defaults.EMBLEM_ART_DIRS["moods"] / "Eclipse.png",),
        "name": "The Ninth Mood",
        "article": ("emblem", "moods", "The Ninth Mood"),
        "accents": (),
    })
    # THE NINE INTELLIGENCES (owner GO 2026-07-13): the academy cameos
    # — 9 = the six Prism arms + the three Trinity arms.
    intel = defaults.EMBLEM_ART_DIRS["intelligence"]
    topics["intelligences"] = {
        "title": "The Nine Intelligences",
        "icon": intel / "existential.png",
        "entries": [{
            "images": (),
            "name": "The Nine Intelligences",
            "article": ("emblem", "intelligence", "The Nine Intelligences"),
            "accents": (),
        }] + [
            {
                "images": (intel / f"{stem}.png",),
                "name": name,
                "article": ("emblem", "intelligence", name),
                "accents": (),
            }
            for name, stem in (
                ("Bodily-Kinesthetic", "bodily_kinesthetic"),
                ("Interpersonal", "interpersonal"),
                ("Linguistic", "linguistic"),
                ("Naturalist", "naturalist"),
                ("Logical-Mathematical", "logical_mathematical"),
                ("Musical", "musical"),
                ("Existential", "existential"),
                ("Intrapersonal", "intrapersonal"),
                ("Spatial", "spatial"),
            )
        ],
    }
    # THE NINTHS close their topics (owner 8+1 doctrine 2026-07-14):
    # the excluded member, the event, the myth, the legend — plates
    # wired ahead of the art (missing files stay hidden).
    _w = defaults.WEEKDAY_ART_DIR
    _z = defaults.ZODIAC_ART_DIR
    # Round-four/five verdicts (owner 2026-07-15): the Union ninths —
    # Gaia/Yggdrasil/Triglav/the Pharaoh/the Polymath/the Holy Trinity/
    # the Ninth Circle/Freemasonry — supersede the old exile ninths;
    # Melchizedek relocates to Bible II, the Unknown God to the
    # Ancient set. Retired entries stay in encyclopedia.json for the
    # Wider-Pantheon wave.
    for topic_key, name, plate in (
        ("wolf", "Sigma", _w / "wolf/primary/sigma.png"),
        ("bee", "The Swarm", _w / "bee/primary/swarm.png"),
        ("elephant", "The Graveyard",
         _w / "elephant/primary/graveyard.png"),
        ("cosmos", "The Big Bang", _w / "cosmos/primary/big_bang.png"),
        ("greek", "Gaia", _w / "greek/pantheon/gaia.png"),
        ("norse", "Yggdrasil", _w / "norse/pantheon/Yggdrasil.png"),
        ("egypt", "The Pharaoh", _w / "egypt/pantheon/pharaoh.png"),
        ("slavic", "Triglav", _w / "slavic/pantheon/triglav.png"),
        ("alchemy", "The Philosopher's Stone",
         _w / "alchemy/primary/stone.png"),
        ("profession", "The Polymath",
         _w / "profession/primary/Polymath.png"),
        ("religion", "Freemasonry",
         _w / "religion/primary/freemasonry.png"),
        ("religion_alt", "The Unknown God",
         _w / "religion/secondary/unknown_god.png"),
        ("bible", "The Holy Trinity",
         _w / "bible/primary/holy_trinity.png"),
        ("bible2", "Melchizedek",
         _w / "bible/secondary/melchizedek.png"),
        ("bible_dark", "The Ninth Circle",
         _w / "bible/dark/ninth_circle.png"),
        ("chinese", "The Cat", _z / "chinese/primary/Cat.png"),
        ("astrology", "Ophiuchus", _z / "astrology/sign/Ophiuchus.png"),
    ):
        topics[topic_key]["entries"].append({
            "images": (plate,),
            "name": name,
            "article": ("emblem", "ninths", name),
            "accents": (),
        })
    # THE TWO TRIANGLES (owner 2026-07-13): the Judas–Lucifer scale —
    # the two fallen extremes of self and the zero no individual
    # reaches. The badge art is wired ahead of its landing (missing
    # files stay hidden); the Union pairs both triangles.
    # THE SCALE ROTATION (owner decree 2026-07-19/20, CANON.md
    # one-image-one-place amendment — Judas-Lucifer is a MAIN theme,
    # "koje cemo koristiti na smenu"): Lucifer and Judas each keep
    # MULTIPLE generated versions on disk; the shown face advances
    # with `travel_date` instead of freezing on one master. Only the
    # two poles rotate — the Union stays fixed.
    topics["duality"] = {
        "title": "The Two Triangles",
        "icon": defaults.SCALE_ART_DIR / "Union.png",
        "entries": [
            {
                "images": (
                    defaults.scale_variant_file("Lucifer", travel_date)
                    or defaults.SCALE_ART_DIR / "Lucifer_Triangle.png",
                ),
                "name": "Lucifer",
                "article": ("emblem", "duality", "Lucifer"),
                "accents": ("red",),
            },
            {
                "images": (
                    defaults.scale_variant_file("Judas", travel_date)
                    or defaults.SCALE_ART_DIR / "Judas_Triangle.png",
                ),
                "name": "Judas",
                "article": ("emblem", "duality", "Judas"),
                "accents": ("blue",),
            },
            {
                # The owner's hexagram badge (2026-07-13): the two
                # triangles interlocked, the white circle at the cross.
                "images": (defaults.SCALE_ART_DIR / "Union.png",),
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
    # THE MOON (owner 2026-07-16, ROADMAP queue #8b): EIGHT phase pages —
    # the four principal phases and the four between them — in cycle
    # order, each a house-voice article carrying the phase's geometry,
    # its myth and the tides (spring at new/full, neap at the quarters).
    # The order is constants.MOON_PHASE_NAMES, so the Spacebar jump
    # (compositor._element_encyclopedia_target) indexes a hovered phase
    # straight into this list. Every page wears ITS OWN phase plate,
    # rendered LIVE (owner decree 2026-07-19: "bolje crtati na licu
    # mesta nego 15MB fajlova") from the full-moon master with the
    # dial's own terminator geometry — moon_phase_file, disk-cached.
    moon_plate = defaults.WEEKDAY_ART_DIR / "planets" / "primary" / "moon.png"
    topics["moon"] = {
        "title": "Moon",
        "icon": moon_plate,
        "entries": [
            {
                "images": (
                    moon_phase_file(
                        index / len(constants.MOON_PHASE_NAMES),
                        phase.lower().replace(" ", "_"),
                    ),
                ),
                "name": ("moon_title", phase),
                "article": ("moon", phase),
                "accents": (),
            }
            for index, phase in enumerate(constants.MOON_PHASE_NAMES)
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
    # THE SUN (owner 2026-07-16, ROADMAP queue #10): the turning points
    # — the solstices and the equinoxes and their glow.
    topics["sun"] = {
        "title": "Sun",
        "icon": defaults.SEASON_ART_DIR / "turning_point"
        / "Summer_Solstice.png",
        "entries": [
            {
                "images": (defaults.SEASON_ART_DIR / art,),
                "name": ("sun_title", key),
                "article": ("sun", key),
                "accents": (),
            }
            for key, art in _SUN_ENTRIES
        ],
    }
    # THE ERA TERMS (ROADMAP 15a3, owner 2026-07-17): the Age of Light,
    # the Age of Darkness and the four Starry Seasons, closed by the
    # comparative "Eras of the World" essay (no plate of its own).
    def _era_image(art: str):
        """One rotating era emblem (THE UNIVERSAL ROTATION CONVENTION,
        owner decree 2026-07-20): the canonical file plus any `_v2`
        siblings and its `alt/` twin feed one daily pool, keyed by
        `travel_date` exactly like the Scale rotation above. Zero
        candidates (art not landed yet) keeps the plain canonical path
        — graceful-absent, the Encyclopedia hides missing art. Used for
        BOTH the six single Age/Starry-Season entries below AND every
        emblem in the "Eras of the World" calendar strip (ERA-TRIO
        round, owner 2026-07-20 — ground-truthed: the calendar strip
        used to bypass rotation entirely, a straight `ERA_ART_DIR / a`
        with no `rotating_art_file` call, so a `calendar/alt/*`
        sibling like the Byzantine v2 emblem would never have been
        found; fixed the same round, since the convention is
        universal)."""
        canonical = defaults.ERA_ART_DIR / art
        return defaults.rotating_art_file(canonical, travel_date) or canonical

    topics["era"] = {
        "title": "Eras & Ages",
        "icon": defaults.ERA_ART_DIR / "Age_of_Light.png",
        "entries": [
            {
                "images": (
                    tuple(_era_image(a) for a in art)
                    if isinstance(art, tuple)
                    else (_era_image(art),) if art else ()
                ),
                "name": ("era_title", key),
                "article": ("era", key),
                "accents": (),
            }
            for key, art in _ERA_ENTRIES
        ],
    }
    # THE ECLIPSES (fix round F, owner order 2026-07-19): two topics —
    # Solar and Lunar — one per body, each an overview page then a
    # category chapter per kind. Every category chapter wears its own
    # emblem; the overview strings its body's emblems as a strip
    # (isinstance tuple), graceful-absent until the art lands.
    for topic_key, title, icon_stem, entry_specs in _ECLIPSE_TOPICS:
        topics[topic_key] = {
            "title": title,
            "icon": defaults.ECLIPSE_ART_DIR / icon_stem,
            "entries": [
                {
                    "images": (
                        tuple(defaults.ECLIPSE_ART_DIR / a for a in art)
                        if isinstance(art, tuple)
                        else (defaults.ECLIPSE_ART_DIR / art,)
                    ),
                    "name": ("eclipse_title", key),
                    "article": ("eclipse", key),
                    "accents": (),
                }
                for key, art in entry_specs
            ],
        }
    # THE WIDER PANTHEON (WORKPLAN Session 8): the seatless A-list
    # figures, one topic per culture. Every article resolves through
    # the encyclopedia "wider" family; the wired plates land later.
    for topic_key, title, theme, icon, figures in _WIDER_TOPICS:
        topics[topic_key] = {
            "title": title,
            "icon": defaults.WEEKDAY_ART_DIR / icon,
            "entries": [
                {
                    "images": (
                        defaults.WEEKDAY_ART_DIR / theme / "wider"
                        / f"{figure.lower()}.png",
                    ),
                    "name": figure,
                    "article": ("emblem", "wider", figure),
                    "accents": (),
                }
                for figure in figures
            ],
        }
    return topics


class EncyclopediaDialog(QDialog):
    def __init__(
        self,
        translations: dict | None = None,
        hidden_unlocked: bool = False,
        initial_topic: str | None = None,
        initial_entry: int = 0,
        stay_on_top: bool = False,
        travel_date: date | None = None,
    ):
        super().__init__()
        self._overlay = translations or {}
        self._tr = lambda text: ui(self._overlay, text)
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Encyclopedia')}"
        )
        # A NORMAL window by default (owner 2026-07-13: no stay-on-top —
        # it must yield to whatever has focus, like any other
        # application). FIX ROUND A (owner verdict 2026-07-19,
        # screenshots): in "top" z-mode the dial forces itself to the
        # TRUE top of the Z-order (`native.assert_topmost`,
        # HWND_TOPMOST) — an ordinary window then opens UNDER it, unlike
        # Settings/Time Travel/Guide (which already carry
        # WindowStaysOnTopHint unconditionally). `stay_on_top` is the
        # controller's `z_mode == "top"` reading — the 2026-07-13 intent
        # (yield to focus) is UNCHANGED for every other z-mode.
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # Maximize/minimize live in the title bar (owner 2026-07-13:
        # "treba button maximize da se proširi preko celog ekrana").
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self._symbolism = SymbolismRepository(overlay=self._overlay)
        self._encyclopedia = EncyclopediaRepository(overlay=self._overlay)
        self._topics = _topics(travel_date)
        if hidden_unlocked:
            # The Four Greetings (owner 2026-07-14): the owner's own
            # verses, Serbian in EVERY language, unlocked by the
            # hidden-mode code — they close the Trinity topic (the
            # dial's own top-letter hover legend, unchanged).
            verses = json.loads(
                (paths.database_dir() / "verses.json").read_text(
                    encoding="utf-8"
                )
            )
            data = verses["trinity"]
            self._topics["trinity"]["entries"].append({
                "images": (defaults.SCALE_ART_DIR / "Union.png",),
                "name": data["title"],
                "article": ("verses", data),
                "accents": (),
                "poem": True,
            })
            # The poem's CANONICAL home (ROADMAP queue #6, owner
            # 2026-07-16): bound to the Seasons — the four greetings
            # sit on the four temperament arms (CANON.md). A SECOND,
            # shorter reading — the CANON's three-line quote plus an
            # English framing of the four faces — closes the Seasons
            # topic; absent entirely until the same cipher unlocks it.
            season_data = verses["seasons"]
            self._topics["seasons"]["entries"].append({
                "images": (defaults.SEASON_ART_DIR / "Poem.png",),
                "name": season_data["title"],
                "article": ("verses", season_data),
                "accents": (),
                "poem": True,
            })
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
        self._topic_key: str | None = None
        self._entry_index = 0
        # The reader chrome (owner 2026-07-14: big, vivid, modern —
        # Home top-left, Download top-right, the pager bottom-center).
        self._back = QPushButton("⌂  " + self._tr("Home"))
        self._back.clicked.connect(self._show_topics)
        style_button(self._back, "home")
        self._download = QPushButton("⬇  " + self._tr("Download"))
        self._download.clicked.connect(self._download_entry)
        style_button(self._download, "download")
        self._counter = QLabel()
        self._counter.setStyleSheet(
            f"font-size: {defaults.UI_BUTTON_FONT_PX}px;"
            "font-weight: bold;"
        )
        self._previous = QPushButton(self._tr("← Previous"))
        self._previous.clicked.connect(lambda: self._step(-1))
        style_button(self._previous, "previous")
        self._next = QPushButton(self._tr("Next →"))
        self._next.clicked.connect(lambda: self._step(+1))
        style_button(self._next, "next")
        top = QHBoxLayout()
        top.addWidget(self._back)
        top.addStretch(1)
        top.addWidget(self._download)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._previous)
        row.addWidget(self._counter)
        row.addWidget(self._next)
        row.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._title)
        layout.addWidget(self._scroll, stretch=1)
        layout.addLayout(row)
        self.resize(
            defaults.GUIDE_INITIAL_IMAGE_PX + 90,
            defaults.GUIDE_INITIAL_IMAGE_PX + 220,
        )
        apply_theme(self)
        self._show_topics()
        # The Spacebar jump (owner 2026-07-16, ROADMAP queue #8): open
        # straight onto the hovered topic's matching entry, skipping the
        # gallery — unknown topics fall back to the gallery.
        if initial_topic is not None and initial_topic in self._topics:
            self._topic_key = initial_topic
            entries = self._topics[initial_topic]["entries"]
            self._entry_index = (
                min(initial_entry, len(entries) - 1) if entries else 0
            )
            self._show_entry()

    def _article_text(self, ref: tuple) -> str:
        kind = ref[0]
        if kind == "verses":
            # The Four Greetings stay SERBIAN in every language
            # (owner 2026-07-14) — verses, their reading, then the
            # watchmaker's commentary.
            return "\n\n".join((
                ref[1]["verses"], ref[1]["explanation"],
                ref[1]["commentary"],
            ))
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
        if kind == "sun":
            return self._encyclopedia.sun(ref[1])["base"]
        if kind == "moon":
            return self._encyclopedia.moon(ref[1])["base"]
        if kind == "era":
            return self._encyclopedia.era(ref[1])["base"]
        if kind == "eclipse":
            return self._encyclopedia.eclipse(ref[1])["base"]
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
            if name[0] == "sun_title":
                return self._encyclopedia.sun(name[1])["title"]
            if name[0] == "moon_title":
                return self._encyclopedia.moon(name[1])["title"]
            if name[0] == "era_title":
                return self._encyclopedia.era(name[1])["title"]
            if name[0] == "eclipse_title":
                return self._encyclopedia.eclipse(name[1])["title"]
            return self._encyclopedia.instrument(name[1])["title"]
        return self._tr(name)

    def _show_topics(self) -> None:
        """Screen 1 — the topic gallery in the owner's groups,
        EVERYTHING centered (owner 2026-07-13: headers and cards
        alike); the card icons are RESPONSIVE — _rescale grows and
        shrinks them with the window between the two bounds, and only
        below the minimum does the scrollbar take over."""
        self._title.setText(self._tr("Encyclopedia"))
        self._topic_key = None
        self._back.hide()
        self._download.hide()
        self._previous.hide()
        self._counter.hide()
        self._next.hide()
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
                icon = paths.art_file(topic["icon"])
                if icon is not None and icon.exists():
                    # The FULL-RES art backs the icon — QIcon renders
                    # whatever size _rescale asks for.
                    card.setIcon(QIcon(str(icon)))
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
        """Screen 2 — the topic SLIDER (owner plan round E,
        2026-07-14): entries page one at a time from the first."""
        self._topic_key = key
        self._entry_index = 0
        self._show_entry()

    def _step(self, delta: int) -> None:
        """← Previous / Next → — wraps around like the Guide pages."""
        entries = self._topics[self._topic_key]["entries"]
        self._entry_index = (self._entry_index + delta) % len(entries)
        self._show_entry()

    def _download_entry(self) -> None:
        """⬇ Download (owner 2026-07-14): save the OPEN entry — the
        current look's image(s) and the article text (headings kept
        as [Label] lines) — into a folder the user picks."""
        entry = self._topics[self._topic_key]["entries"][self._entry_index]
        target = QFileDialog.getExistingDirectory(
            self, self._tr("Download")
        )
        if not target:
            return
        name = self._entry_name(entry)
        safe = "".join(
            ch if ch.isalnum() or ch in " ·-_()" else "_" for ch in name
        ).strip()
        text = _HEX_NOTE.sub("", self._article_text(entry["article"]))
        lines = [name, ""]
        for paragraph in text.split("\n\n"):
            match = _SUBHEAD.match(paragraph)
            if match:
                lines.append(f"[{self._tr(match.group(1))}]")
                paragraph = paragraph[match.end():]
            lines += [paragraph, ""]
        (Path(target) / f"{safe}.txt").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        state = self._cells[0] if self._cells else None
        if state is not None:
            rows = state["looks"][state["index"]]
            images = [path for row in rows for path in row]
            for index, path in enumerate(images, start=1):
                suffix = f"_{index}" if len(images) > 1 else ""
                shutil.copyfile(
                    path, Path(target) / f"{safe}{suffix}.png"
                )

    def _show_entry(self) -> None:
        """The current entry's PAGE: the images row (the Astrology
        pair sits side by side), the bold name and the text, all
        inside ONE block (owner: center the whole object, never the
        text lines)."""
        topic = self._topics[self._topic_key]
        entries = topic["entries"]
        entry = entries[self._entry_index]
        self._title.setText(self._tr(topic["title"]))
        self._back.show()
        self._download.show()
        self._counter.setText(f"{self._entry_index + 1} / {len(entries)}")
        pager = len(entries) > 1
        self._previous.setVisible(pager)
        self._counter.setVisible(pager)
        self._next.setVisible(pager)
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        self._topic_cards = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX * 3)
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
        # Resolve through the active ART SOURCE here (owner 2026-07-14:
        # Gemini vs ChatGPT with per-file fallback) — the grid, the
        # pixmap cache and Download all consume the resolved paths.
        look_rows = [
            [
                [
                    resolved
                    for resolved in (
                        paths.art_file(path) for path in row
                        if path is not None
                    )
                    if resolved.exists()
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
            style_button(back, "neutral", small=True)
            caption = QLabel(self._tr(state["titles"][0]))
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption.setMinimumWidth(140)
            caption.setStyleSheet(
                f"font-size: {defaults.UI_BUTTON_SMALL_FONT_PX}px;"
                "font-weight: bold;"
            )
            state["caption"] = caption
            forward = QToolButton()
            forward.setText("▶")
            style_button(forward, "neutral", small=True)
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
        if entry.get("poem"):
            # The Four Greetings page: CENTERED italic stanzas with
            # their line breaks kept, the reading justified below.
            data = entry["article"][1]
            gap = defaults.GREETINGS_STANZA_GAP_PX
            stanzas = "".join(
                f"<p align='center' style='margin-top:{gap}px;"
                f"margin-bottom:{gap}px'><i>"
                + "<br/>".join(
                    _html.escape(line) for line in stanza.split("\n")
                )
                + "</i></p>"
                for stanza in data["verses"].split("\n\n")
            )
            text = QLabel(stanzas + _flow_html(
                data["explanation"] + "\n\n" + data["commentary"]
            ))
        else:
            text = QLabel(
                _flow_html(
                    self._article_text(entry["article"]),
                    accents=entry["accents"],
                    tr=self._tr,
                )
            )
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.RichText)
        self._text_labels.append(text)
        cell.addWidget(text)
        self._blocks.append(block)
        # The block sits CENTERED with even side margins (owner
        # 2026-07-14: "ravnomerno po sredini" — supersedes the
        # left-hug of 2026-07-13).
        column.addWidget(block, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addStretch(1)
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
            # First pass builds the grid; resizes only re-fit pixmaps.
            if "cells" in state:
                self._resize_cell(state, block_width)
            else:
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
        """Build the cell's image GRID for its current look — ONCE per
        look. Window resizes only RE-SCALE the pixmaps in place
        (`_resize_cell`, the Guide's approach): tearing the grid down
        on every resize left half-deleted labels painting as ghosts
        and stale container heights CLIPPING the art (owner bug
        2026-07-14: the full-size crop)."""
        container = state["container"]
        if container is None:
            return
        old = container.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
            QWidget().setLayout(old)     # detach so a fresh grid can bind
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(defaults.GUIDE_SPACING_PX)
        rows = state["looks"][state["index"]]
        columns = max((len(row) for row in rows), default=0)
        state["cells"] = []
        state["rows"] = sum(1 for row in rows if row)
        if not columns:
            return
        for row_index, row in enumerate(rows):
            offset = (columns - len(row)) // 2    # center shorter rows
            for col_index, path in enumerate(row):
                art = self._pixmap(path)
                label = QLabel()
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                state["cells"].append((label, art, columns))
                grid.addWidget(
                    label, row_index, offset + col_index,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )
        self._resize_cell(state, block_width)

    def _resize_cell(self, state: dict, block_width: int) -> None:
        """Fit the look's images to the block width — the columns
        split it and every image shrinks as far as needed (owner
        2026-07-13: nothing may overlap or clip) — AND to the height
        ceiling (owner imperative 2026-07-14 round two: the WHOLE image
        grid never eats more than READER_IMAGE_MAX_HEIGHT_FRACTION of
        the page — stacked rows SHARE the ceiling — so the text stays
        on screen)."""
        rows = max(1, state.get("rows", 1))
        ceiling = round(
            self._scroll.viewport().height()
            * defaults.READER_IMAGE_MAX_HEIGHT_FRACTION
        )
        max_height = max(
            24,
            (ceiling - defaults.GUIDE_SPACING_PX * (rows - 1)) // rows,
        )
        for label, art, columns in state.get("cells", ()):
            if art.isNull():
                continue
            share = block_width // columns - defaults.GUIDE_SPACING_PX * 2
            width = max(24, min(share, art.width()))
            pixmap = art.scaledToWidth(
                width, Qt.TransformationMode.SmoothTransformation
            )
            if pixmap.height() > max_height:
                pixmap = art.scaledToHeight(
                    max_height,
                    Qt.TransformationMode.SmoothTransformation,
                )
            label.setPixmap(pixmap)
            # RESERVE the image's full rectangle (owner REPEAT complaint
            # 2026-07-16, ROADMAP queue #9: the title above and the
            # style/nav row below cut into the art). Fixing the label to
            # the pixmap makes the whole grid's minimum size equal the
            # scaled image, so the QVBoxLayout can never squeeze the
            # container below it — no neighbour overlaps it, and the
            # image is never clipped. When space is tight the height
            # ceiling above has already scaled the WHOLE image down.
            label.setFixedSize(pixmap.size())

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
