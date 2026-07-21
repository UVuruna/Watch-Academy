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

from PySide6.QtCore import QByteArray, QEvent, QRectF, QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
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

from app.theme import apply_theme, size_to_screen
from app.ui_style import style_button, style_look_chip
from config import constants, defaults, paths
from config.ui_text import ui
from core import continents
from data.encyclopedia import EncyclopediaRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from data.symbolism import SymbolismRepository
from render.asset_recolor import metal_variant_file
from render.asset_variants import moon_phase_file
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


def _image_tooltip(path: Path) -> str:
    """IMAGE HOVER (owner spec, round R3: "posebno vazno kod onih gde
    ima više slika" — critical on multi-image pages like the era
    calendars, e.g. hovering a plate should read "Byzantine"): the
    filename stem, underscores opened to spaces. Stems already carrying
    a real capital somewhere (Byzantine, KaliYuga, Solar_Total) are
    left as drawn — a bare lowercase stem (sigma, swarm) is Title-Cased
    so every tooltip reads as a name, not a raw file token."""
    stem = path.stem.replace("_", " ")
    return stem.title() if stem.islower() else stem


# THE ROSTER-SWITCH LOGOS (Ency INSTRUCTIONS.txt rule 5, round R3b
# item 2): simple line-art SVGs, small enough to read at 24-32px —
# a planetary orbit for PLANETARY, a temple pediment for PANTHEON.
# NOTE for a future ImageGeneration pass (owner: "da pravimo preko
# ImageGeneration i neki SVG"): these are the placeholder-grade marks
# the owner asked for THIS round; a generated pair may replace them
# later without changing `_svg_icon`'s call sites.
_ROSTER_ICON_COLOR = "#D9B978"
_PLANETARY_ORBIT_SVG = f"""<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="2.6" fill="{_ROSTER_ICON_COLOR}"/>
  <ellipse cx="12" cy="12" rx="9.6" ry="4.1" fill="none"
    stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.4"
    transform="rotate(-24 12 12)"/>
  <circle cx="20.3" cy="8.1" r="1.35" fill="{_ROSTER_ICON_COLOR}"/>
</svg>"""
_PANTHEON_TEMPLE_SVG = f"""<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 8.4 L12 2.2 L22 8.4 Z" fill="none"
    stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.4"
    stroke-linejoin="round"/>
  <rect x="1.4" y="8.4" width="21.2" height="1.6" fill="{_ROSTER_ICON_COLOR}"/>
  <line x1="4.6" y1="10" x2="4.6" y2="20" stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.6"/>
  <line x1="9.3" y1="10" x2="9.3" y2="20" stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.6"/>
  <line x1="14.7" y1="10" x2="14.7" y2="20" stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.6"/>
  <line x1="19.4" y1="10" x2="19.4" y2="20" stroke="{_ROSTER_ICON_COLOR}" stroke-width="1.6"/>
  <rect x="1.4" y="20" width="21.2" height="1.6" fill="{_ROSTER_ICON_COLOR}"/>
</svg>"""


def _svg_icon(svg_source: str, size: int) -> QIcon:
    """Rasterize an INLINE SVG string to a QIcon at `size` px (round
    R3b item 2) — mirrors `app.tray._rasterize_logo`'s centered-scale
    recipe (Rule #5: the same QSvgRenderer render-to-QPixmap path, no
    second rasterizer) but for a literal SVG source string instead of
    an asset FILE, since the roster-switch marks are inline, not
    wired art."""
    renderer = QSvgRenderer(QByteArray(svg_source.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    design = renderer.defaultSize()
    scale = size / max(design.width(), design.height())
    width, height = design.width() * scale, design.height() * scale
    renderer.render(
        painter, QRectF((size - width) / 2, (size - height) / 2, width, height)
    )
    painter.end()
    return QIcon(pixmap)


# THE FIVE SECTIONS (owner-approved decision, sealed 2026-07-20, round
# R3 — supersedes the nine-group 2026-07-12/13 layout): the owner's own
# names, exact. "planet_signs" is NOT listed on its own — Planets and
# Planet Signs are ONE topic now, distinguished by the existing
# Planets/Signs/Art look switcher (`_weekday_topic`'s special-cased
# "planets" theme already builds exactly that); the "planet_signs" key
# stays wired in `_topics()` ONLY so a dial slot dressed in that theme
# still resolves a Spacebar jump (compositor contract, item 9) — it is
# never a gallery card.
_TOPIC_GROUPS = (
    ("The Celestial Engine",
     ("week", "instrument", "moon", "seasons", "sun", "era",
      "eclipse_solar", "eclipse_lunar", "astrology", "chinese",
      "planets", "cosmos",
      # THE CONTINENTS (owner-sealed matrix 2026-07-21): the Earth takes
      # its seat among the celestial bodies. It rides the Engine — not
      # the Living World — because the theme IS the dial's own Earth
      # marker read as the week: built from the instrument's day/night
      # faces, poles and season/moon machinery, its Ninth switching by
      # the very sky the Engine computes.
      "continents",
      # THE SLAVIC MONTHS (owner-sealed R7b 2026-07-21): the year's own
      # wheel of labour — a Calendar-pointer 12-set. Rides the Engine
      # because it IS the year's wheel (the same wheel the Almanac reads),
      # not a myth or a craft.
      "months")),
    # THE GODS/FAITHS SPLIT (owner round R8b item 6: "zasto i dalje
    # imamo ove dve verzije" — the standalone Wider-Pantheon topics
    # (WORKPLAN Session 8: "Greek"/"Norse"/"Egyptian"/"Slavic", the
    # culture's seatless A-listers) sat as confusing SECOND tiles right
    # beside the merged "Greek gods"/etc. topic once round R3b folded
    # Planetary+Pantheon into ONE 22-page topic per culture — deleted
    # completely per the owner's verdict; the merged topics are the
    # only home now (Rule #6). The subgroup split itself lives in
    # `_GALLERY_SUBGROUPS` below (item 5c) — this flat tuple is still
    # the group's full membership `_show_topics` iterates.
    ("The Divine",
     ("greek", "norse", "egypt", "slavic",
      "religion", "religion_alt", "bible", "bible2", "bible_dark")),
    ("The Human Wheel",
     ("virtues", "sins", "moods", "intelligences", "profession",
      "trinity", "duality")),
    ("The Living World", ("wolf", "bee", "elephant", "alchemy", "japan")),
    # THE ARCHETYPES (owner: "its OWN section — do not scatter them"):
    # its own group exists NOW so future archetype topics land here
    # rather than being folded into The Divine/The Human Wheel later.
    # Empty on purpose — `config/archetypes.py` names the figures and
    # `render.compositor` already resolves SOME of their Spacebar
    # targets onto OTHER topics (the Walks onto Professions), but no
    # archetype has its OWN encyclopedia topic yet (Sessions 6/8, per
    # the existing ARCHETYPE_PENDING_LINE convention) — that is new
    # content, out of THIS round's scope (encyclopedia.py structure +
    # Database/encyclopedia.json, not a new article-writing pass).
    ("The Archetypes", ()),
)

# THE GALLERY SUBGROUPS (owner round R8b item 5c, GALLERY LAYOUT REWORK
# v2: "imamo te velike grupacije sa velikim naslovom po sredini... a
# onda imamo podnaslove koji su centrirani levo i koji objedinjuju manje
# grupacije... Ovo za podgrupe vazi samo za one tematike koje su
# prenatrpane tj. The Celestial Engine, The Divine"): a LEFT-ALIGNED
# subheading partitions an overloaded HALL's own tiles into smaller
# kinship clusters; every OTHER hall stays one flat run of rows under
# its own big centered title. Each hall's own partition here is
# EXHAUSTIVE and non-overlapping against its `_TOPIC_GROUPS` membership
# (`test_gallery_subgroups_partition_their_hall_exactly` pins this).
#
# Celestial: the CLOCK BODIES riding the dial itself (the day/week
# figures, the instrument's own parts, the two zodiacs, the earth-as-
# weekday theme) / the transient SKY EVENTS (moon phases, seasons, the
# solstice-equinox turning points, both eclipse families) / the year's
# own structural YEAR WHEELS (the calendar-systems essay, the Slavic
# months). Divine: GODS (item 6 — the four merged Planetary/Pantheon
# cultures, now titled by their bare demonym) / FAITHS & CREEDS (the two
# religion sets, the three Bible mirrors).
_GALLERY_SUBGROUPS = {
    "The Celestial Engine": (
        ("The Clock Bodies", (
            "week", "instrument", "planets", "astrology", "chinese",
            "cosmos", "continents",
        )),
        ("The Sky Events", (
            "moon", "seasons", "sun", "eclipse_solar", "eclipse_lunar",
        )),
        ("The Year Wheels", ("era", "months")),
    ),
    "The Divine": (
        ("Gods", ("greek", "norse", "egypt", "slavic")),
        ("Faiths & Creeds", (
            "religion", "religion_alt", "bible", "bible2", "bible_dark",
        )),
    ),
}

# THE GALLERY ROW GEOMETRY (owner round R8b item 5a fix — ground-
# truthed against a LIVE dialog's own horizontal scrollbar, not
# re-derived on paper): the OLD icon-sizing formula
# (`(viewport.width() - 48) // columns - spacing`) silently dropped the
# `columns * ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX` term from its own
# budget — a full 4-column row reliably overflowed the frame by
# ~100px at any viewport narrower than the point where the icon
# saturates at its own MAX ceiling (exactly the "X scroll again"
# regression the owner's screenshot showed). `_show_topics` sets the
# gallery column's own left/right margin to a KNOWN, explicit
# GUIDE_SPACING_PX (never Qt's unstated QVBoxLayout default) so these
# two functions — one pair, Rule #5 — have no hidden fudge factor left:
# `_gallery_content_width` sizes the dialog's own MIN WIDTH (__init__)
# and `_gallery_icon_ceiling` is its exact inverse, the live per-resize
# HARD ceiling `_rescale_topics` clamps every icon size to, zoom
# included — so a full row can never spill past its viewport at ANY
# window width or zoom level.
def _gallery_content_width(icon_px: int) -> int:
    """The pixel width one full ENCYCLOPEDIA_GALLERY_MAX_COLUMNS row
    needs at `icon_px` icon size: the cards side by side with their own
    padding, the inter-card spacing, and the column's own margins."""
    columns = defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS
    spacing = defaults.GUIDE_SPACING_PX * 2
    margins = defaults.GUIDE_SPACING_PX * 2
    card = icon_px + defaults.ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX
    return columns * card + (columns - 1) * spacing + margins


def _gallery_icon_ceiling(viewport_width: int) -> int:
    """The LARGEST icon size a full row can wear inside `viewport_width`
    without overflowing it — the exact inverse of
    `_gallery_content_width` above."""
    columns = defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS
    spacing = defaults.GUIDE_SPACING_PX * 2
    margins = defaults.GUIDE_SPACING_PX * 2
    available = viewport_width - margins - (columns - 1) * spacing
    return available // columns - defaults.ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX


# THE SESSION ZOOM (owner round R8b item 5b): Ctrl+MouseWheel scales
# fonts/images/tiles together; module-level so it SURVIVES a Home ->
# reopen within the same app run ("persisted for the session at
# least") without touching `app.settings_store` (owned by the parallel
# METAL_SWAP/settings agent this round) — never written to disk, resets
# on app restart.
_session_zoom = 1.0

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

# THE SPACE-JUMP INDEX REMAP (owner contract, round R3 restructure,
# item 9): `render.compositor._weekday_encyclopedia_target` (out of
# this round's scope) still returns the OLD raw index — sun=0,
# moon=1..saturn=6 (`_ENC_WEEK_ORDER`, unaware of the restructure).
# `_weekday_topic`'s new order happens to leave Monday..Saturday at
# that SAME index (Title only pushes in at 0; Sunday moves OUT to the
# end) — only raw index 0 (the Sun) needs remapping, to the GOOD
# (Ruler) half's new seat: Title(0) + Mon..Sat(1-6) + Duality title(7)
# + Good(8) [+ Evil(9) — round R3b item 1 split, EVIL is not a jump
# target of its own: a Spacebar press always lands on GOOD, matching
# the pre-split "jump to the merged dual page" intent]. Applied once
# in `__init__`. The GOOD half happens to land on the SAME raw index
# (8) the R3 merged dual page used to occupy — pure coincidence of the
# arithmetic (title+6+duality-title=8), not a second meaning read into
# the number.
_WEEKDAY_DUAL_PAGE_INDEX = 8
# Every `_weekday_topic`-built topic — every WEEKDAY_THEME_TITLES key
# EXCEPT virtues/sins/moods (those get OVERWRITTEN by the emblem-family
# pass in `_topics()` below and are never weekday-shaped in the end).
_WEEKDAY_RESTRUCTURED_TOPICS = frozenset(defaults.WEEKDAY_THEME_TITLES) - {
    "virtues", "sins", "moods",
}

# THE NINTH SEAT'S PHILOSOPHICAL NAME (owner decree 2026-07-20, round
# R3): across every theme the Ninth is the SAME archetype underneath
# its many costumes (CANON.md "The Ninth — Outside the Circle") — a
# potential member who never found its place and was never found BY
# the eight, the union or the exile alike. UV/INSTRUCTION.txt #7 walks
# the case studies: the Sigma wolf is a potential leader with no pack,
# the shepherd with no flock, the sailor with no sea, Freemasonry's own
# undefined god (the Unknown God, Ancient religions), the profession
# that knows a little of everything and is master of none, the
# existential intelligence that questions every OTHER intelligence,
# the virtue of Balance/objectivity (never loving, trusting or giving
# too much OR too little), the sin of WISH — the root every other sin
# grows from (wanting to be loved: servility; wanting to rule: pride;
# wanting what others have or keeping what is one's own: envy/
# jealousy). The sealed name for this position is **The Unfound**.
# Alternatives discussed and rejected the same evening: **The
# Uncalled** (implies someone else's failure to call, not the figure's
# own unsettled nature), **The Ninth Door** (a place, not a person —
# most Ninths ARE persons), **The Seeker** (too active/heroic — several
# Ninths, like Melchizedek or the Union badges, are not searching for
# anything), **The Unclaimed** (close, but reads as ownable property
# rather than a member who could belong and does not) — "The Unfound"
# won because it holds BOTH readings the owner insisted on keeping
# open at once (never found itself / never found by others), where
# every alternative above only covers one.
NINTH_SEAT_PHILOSOPHICAL_NAME = "The Unfound"

# THE GOD-TOPIC GALLERY TITLE (owner round R8b item 6): "Ubuduce posto
# ce biti podnaslov Gods onda ce nazivi biti samo Greek, Egypt, Norse
# ... itd" — with a "Gods" SUBGROUP heading now sitting above these four
# cards (`_GALLERY_SUBGROUPS` below, item 5c), the "gods" suffix is
# redundant on the tile itself. This overrides ONLY the gallery card
# text and the reader's own top header (`_topic_display_title`) — every
# OTHER reader of `defaults.WEEKDAY_THEME_TITLES` (the Ancient Gods
# menu, the Weekday theme picker, Settings) is a DIFFERENT surface the
# owner never asked to rename, so the shared table itself stays
# untouched (Rule #5: one shared name would have widened the blast
# radius past what was asked). Demonyms per the owner's own pick:
# "Egypt" (not "Egyptian"), "Norse" stays Norse (not "Nordic").
_GOD_TOPIC_GALLERY_TITLES = {
    "greek": "Greek", "norse": "Norse", "egypt": "Egypt", "slavic": "Slavic",
}


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


def _colored_sibling(path: Path) -> Path:
    """The COLORED twin of a bronze-plate FILE (owner round R8b item 3:
    "Panteon bogovi nemaju Colored verzije u switchu" — the Pantheon
    pages lack Colored even though the art landed). The asset tree
    nests `colored/` at TWO different depths depending on where the
    bronze file itself lives: an ordinary plate under `<theme>/primary/
    <File>.png` has its colored twin as a SIBLING of `primary/` itself
    (`<theme>/colored/<File>.png`, two parents up); a SEATED Pantheon
    plate under `<theme>/pantheon/<file>.png` nests its colored twin
    ONE level in, directly inside `pantheon/`
    (`<theme>/pantheon/colored/<file>.png`) — the shape the owner's art
    pipeline actually shipped (ground-truthed against
    assets/weekday/*/greek/pantheon/colored/ and .../norse/pantheon/
    colored/). The old call sites each hardcoded ONE of these two
    depths: `_pantheon_topic.looks_for` assumed the shallow pantheon
    nesting (right for a genuine Pantheon-only figure like Poseidon,
    silently missing for a seat that FALLS BACK to the planetary
    primary plate, like Zeus/Thor/Loki/Tyr, since none of those four
    Norse/Greek pantheon seats grew their own dedicated art); the
    Ninth's `_ninth_looks` assumed the deep primary-sibling shape
    unconditionally, missing Gaia/Yggdrasil (both pantheon-rooted
    plates). One function, one rule, checked against the folder name
    itself rather than guessed from the call site (Rule #5/#6)."""
    if path.parent.name == "pantheon":
        return path.parent / "colored" / path.name
    return path.parent.parent / "colored" / path.name


def _ninth_looks(theme: str, plate: Path) -> tuple | None:
    """The Ninth's OWN look switcher (owner bug, "Gaia screenshot":
    the 9th member's page carried the color switcher for NONE of its
    metal-plate themes) — every theme whose seated eight cycle Colored/
    Bronze/Gold/Silver gives its Ninth the SAME cycle, `colored` found
    via `_colored_sibling` (owner round R8b item 3 fix — Gaia/Yggdrasil
    sit under `pantheon/`, the shallow-nested colored twin the old
    unconditional `parent.parent` guess always missed); the Chinese
    Ninth (The Cat) mirrors the OTHER eleven animals' Bronze-first
    order instead. Themes with no per-metal art (egypt, slavic, the
    plain-color families) return None — the Ninth stays the single
    plain plate, same as before, since there is nothing to switch."""
    if theme == "chinese":
        return tuple(
            (label, ((path,),))
            for label, path in (
                ("Bronze", plate),
                ("Gold", metal_variant_file(plate, "gold")),
                ("Silver", metal_variant_file(plate, "silver")),
                ("Colored", _colored_sibling(plate)),
            )
        )
    if theme not in constants.METAL_THEMES:
        return None
    return tuple(
        (label, ((path,),))
        for label, path in _metal_looks(plate, _colored_sibling(plate))
    )


# One theme's plate for one body (bronze / canon file) — the
# resolution itself lives in config (Rule #5: `app.pointer_theme` and
# `app.slot_theme` need the SAME preview art for their picker grids).
_theme_body_art = defaults.weekday_theme_body_art


def _theme_dual_art(theme: str, colored: bool = False) -> Path:
    """The theme's Sunday SERVANT plate — the colored dual lives in
    the SIBLING variant (owner restructure 2026-07-14)."""
    rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if colored:
        rel = rel.replace("/primary/", "/colored/")
    return defaults.WEEKDAY_ART_DIR / f"{rel}.png"


def _weekday_topic(theme: str):
    """(icon path, entries) for one weekday theme (owner ARTICLE ORDER
    restructure, round R3; SPLIT into two separate GOOD/EVIL pages,
    round R3b item 1 — owner verdict A, supersedes the R3 MERGED dual
    page): entry 0 is the theme's OWN title page (`theme_title` —
    describes the whole theme; the plate is a documented graceful-
    absent slot for a future theme plate, the TEXT is written now);
    entries 1-6 are Monday..Saturday, in that order (owner: "Ponedeljak
    PRVI"); entry 7 is the WEEK-DUALITY title page (`week_duality`);
    entry 8 is the GOOD (Ruler) half of Sunday, its own ordinary single-
    image page; entry 9 is the EVIL (Servant) half, ALSO its own
    ordinary single-image page with its OWN plate — the R3 two-column-
    in-one-page dual layout is retired (each half is now indistinguish-
    able in shape from a Monday..Saturday page, just fed through
    `evil_looks_for` for the Servant side). The metal themes still
    cycle Colored/Bronze/Gold/Silver on EACH half independently; the
    planets still cycle their photos and the sign glyphs. The Ninth
    (where the theme has one) is appended AFTER this function returns
    (`_topics`' ninths loop), landing last either way."""
    article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
    if theme == "planets":
        names = defaults.DEFAULT_SKIN.weekday_set.body_names
    else:
        names = defaults.WEEKDAY_THEME_NAMES[theme]
    metal = theme in constants.METAL_THEMES

    def rows(ruler: Path, servant: Path | None) -> tuple:
        if servant is not None and paths.art_file(servant).exists():
            return ((ruler, servant),)
        return ((ruler,),)

    def looks_for(body: str) -> tuple:
        """A Monday..Saturday (or GOOD/Ruler) page's own looks — always
        a SINGLE image per look now (round R3b item 1: the old
        `dual=True` two-plate-per-row branch retired with the merged
        page; `evil_looks_for` below is EVIL's own sibling)."""
        base = _theme_body_art(theme, body)
        if metal:
            colored = (
                defaults.WEEKDAY_ART_DIR
                / defaults.WEEKDAY_THEME_DIRS[theme]
            ).parent / "colored" / (
                f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
            )
            return tuple(
                (label, rows(path, None))
                for label, path in _metal_looks(base, colored)
            )
        if theme == "planets":
            # Owner defaults 2026-07-13: the photos lead, the sign
            # glyphs and the bronze medallions ride the arrows.
            sign = defaults.WEEKDAY_ART_DIR / "planets" / "signs" / f"{body}.png"
            art = defaults.WEEKDAY_ART_DIR / "planets" / "art" / f"{body}.png"
            return (
                ("Planets", rows(base, None)),
                ("Signs", rows(sign, None)),
                ("Art", rows(art, None)),
            )
        return (("", rows(base, None)),)

    def evil_looks_for() -> tuple:
        """The EVIL half's OWN page (owner verdict A, round R3b item 1
        — the Servant plate ALONE, never paired with the Ruler's any
        more): mirrors `looks_for`'s per-metal/per-planets-look cycle
        exactly, built from `_theme_dual_art` instead of
        `_theme_body_art` (Rule #5 — the same shapes, the Servant's own
        files)."""
        servant = _theme_dual_art(theme)
        if metal:
            colored = _theme_dual_art(theme, colored=True)
            return tuple(
                (label, rows(path, None))
                for label, path in _metal_looks(servant, colored)
            )
        if theme == "planets":
            sign_dual = (
                defaults.WEEKDAY_ART_DIR / "planets" / "signs" / "sun_eclipse.png"
            )
            art_dual = (
                defaults.WEEKDAY_ART_DIR / "planets" / "art" / "sun_eclipse.png"
            )
            return (
                ("Planets", rows(servant, None)),
                ("Signs", rows(sign_dual, None)),
                ("Art", rows(art_dual, None)),
            )
        return (("", rows(servant, None)),)

    def body_entry(body: str) -> dict:
        return {
            "looks": looks_for(body),
            "name": names[body],
            "article": ("article", article_set, body),
            "accents": defaults.BODY_ACCENT_HUES[body],
            # TITLES CARRY THE DAY (owner round R8b item 8): read by
            # `_entry_name`, the ONE build point that appends it.
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    def good_entry() -> dict:
        """The GOOD (Ruler) half of Sunday — its OWN page now (owner
        verdict A, round R3b item 1), an ordinary single-image page
        exactly shaped like Monday..Saturday's."""
        ruler_name, _servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        return {
            "looks": looks_for("sun"),
            "name": ruler_name,
            "article": ("article_face", article_set, "sun", "ruler"),
            "accents": defaults.BODY_ACCENT_HUES["sun"],
            "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
        }

    def evil_entry() -> dict:
        """The EVIL (Servant) half of Sunday — its OWN page, its OWN
        plate (owner verdict A, round R3b item 1)."""
        _ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        return {
            "looks": evil_looks_for(),
            "name": servant_name,
            "article": ("article_face", article_set, "sun", "servant"),
            "accents": defaults.BODY_ACCENT_HUES["sun"],
            "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
        }

    title_entry = {
        "images": (),      # graceful-absent — a future theme plate's slot
        "name": ("theme_title", theme),
        "article": ("theme_title", theme),
        "accents": (),
    }
    duality_title_entry = {
        "images": (),
        "name": ("week_duality_title", theme),
        "article": ("week_duality", theme),
        "accents": (),
    }
    entries = (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry(), evil_entry()]
    )
    return _theme_body_art(theme, "sun"), entries


# THE PANTHEON/PLANETARY MERGE (Ency INSTRUCTIONS.txt rule 5, round
# R3b item 2): the four themes with a documented Pantheon roster
# (`defaults.WEEKDAY_PANTHEON`) become ONE topic each — pages 1-11 the
# Planetary run `_weekday_topic` already builds (title, Mon..Sat, week-
# duality title, good, evil, ninth), pages 12-22 the SAME 11-page shape
# again for the Pantheon roster (`_pantheon_topic` below), reusing the
# Planetary block's OWN Ninth (CANON.md: a theme names ONE Ninth,
# outside BOTH rosters, never a second seatless figure per roster) —
# both blocks close on the identical Gaia/Yggdrasil/Pharaoh/Triglav
# page. `_PANTHEON_BLOCK_SIZE` is the fixed span every merged theme's
# Planetary block occupies (11 — all four Pantheon cultures also carry
# a Ninth, so the arithmetic never varies): the roster-switch button
# jumps `entry_index +/- _PANTHEON_BLOCK_SIZE`. Page 23 onward is a
# THIRD block, The Wider Court (`_wider_topic` below, round R8d) — see
# there for why it is NOT a third roster the switch button cycles into.
_PANTHEON_BLOCK_SIZE = 11
# The fixed span of BOTH the Planetary and Pantheon blocks together —
# page 23 (0-indexed 22) is where The Wider Court title opens.
_WIDER_BLOCK_START = 2 * _PANTHEON_BLOCK_SIZE
_PANTHEON_MERGED_THEMES = frozenset(defaults.WEEKDAY_PANTHEON)

# THE WIDER COURT'S FIGURES (round R8d, THE WIDER COURT RE-WIRE, owner-
# approved 2026-07-22 — restores WORKPLAN Session 8's content after
# round R8b's `_WIDER_TOPICS` deletion turned out to be a MISDIAGNOSIS:
# the owner's "zasto i dalje imamo ove dve verzije" complaint was about
# the standalone topics sitting as confusing SECOND gallery tiles next
# to the merged culture topics — never about the fifteen articles
# themselves, which stayed untouched in `encyclopedia.json` the whole
# time, simply unreachable from the UI). Same figure roster the deleted
# `_WIDER_TOPICS` carried verbatim — the culture's famous A-list gods
# that NEITHER roster seats (see the old comment preserved in git
# history, commit 4081445, for the full reconciliation reasoning against
# the round-four/five ninth-seat locks).
_WIDER_FIGURES = {
    "greek": ("Dionysus", "Hephaestus", "Hestia"),
    "norse": ("Baldur", "Heimdall", "Njord"),
    "egypt": ("Set", "Nut", "Geb", "Ptah", "Sekhmet"),
    "slavic": ("Crnobog", "Stribog", "Jarilo", "Rod"),
}


def _pantheon_topic(theme: str) -> list[dict]:
    """The PANTHEON roster's OWN 11-page run for `theme` (round R3b
    item 2) — the SAME [title, Monday..Saturday, week-duality title,
    good, evil] shape `_weekday_topic` builds (the Ninth is appended
    separately, shared with the Planetary block — see
    `_PANTHEON_MERGED_THEMES` above), sourced from
    `defaults.WEEKDAY_PANTHEON[theme]` through `defaults.pantheon_seat`
    — the SAME safety law the live dial's Pantheon roster reads (Rule
    #5, CANON.md "Two Rosters"): a seat whose pantheon plate has not
    landed keeps the WHOLE planetary bundle (file + name + article
    together), and a missing pantheon DUAL pulls the whole Sunday pair
    (both faces) back to the planetary bundle too — never a pantheon
    name paired with planetary art or the reverse. Metal cycling
    follows the theme's OWN rule (`theme in constants.METAL_THEMES`) —
    greek/norse cycle Colored/Bronze/Gold/Silver on the Pantheon plates
    too, `_colored_sibling` finding the twin at whichever depth the
    seat's OWN plate lives at (owner round R8b item 3 fix: a seat that
    falls back to the planetary primary plate — Zeus, Thor, Loki, Tyr,
    none of whom grew dedicated Pantheon art — used to silently drop
    Colored, since the old code only ever checked the shallow
    `pantheon/colored/` nesting); egypt/slavic stay a single plain
    plate, like their Planetary block."""
    table = defaults.WEEKDAY_PANTHEON[theme]
    metal = theme in constants.METAL_THEMES

    def seated(body: str) -> tuple[Path, str, str, str]:
        """(plate, name, article_set, article_body) for one body."""
        found = defaults.pantheon_seat(theme, body)
        if found is not None:
            path, name, (article_set, article_body) = found
            return path, name, article_set, article_body
        return (
            _theme_body_art(theme, body),
            defaults.WEEKDAY_THEME_NAMES[theme][body],
            constants.WEEKDAY_THEME_ARTICLES[theme],
            body,
        )

    def looks_for(path: Path) -> tuple:
        if metal:
            return tuple(
                (label, ((one,),))
                for label, one in _metal_looks(path, _colored_sibling(path))
            )
        return (("", ((path,),)),)

    def body_entry(body: str) -> dict:
        path, name, article_set, article_body = seated(body)
        return {
            "looks": looks_for(path),
            "name": name,
            "article": ("article", article_set, article_body),
            "accents": defaults.BODY_ACCENT_HUES[body],
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    sun_path, _sun_name, _sun_set, _sun_body = seated("sun")
    dual_path = defaults.WEEKDAY_ART_DIR / f"{table['dual'][0]}.png"
    if paths.art_file(dual_path).exists():
        ruler_name, servant_name = table["dual_names"]
        face_article_set = table["articles"]
    else:
        # The safety law's Sunday half (CANON.md "Two Rosters"): a
        # missing pantheon dual pulls the WHOLE Sunday pair back to
        # the planetary bundle — never a pantheon Ruler over a
        # planetary Servant, or the reverse.
        sun_path = _theme_body_art(theme, "sun")
        dual_path = _theme_dual_art(theme)
        ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        face_article_set = constants.WEEKDAY_THEME_ARTICLES[theme]

    title_key = f"{theme}_pantheon"
    title_entry = {
        "images": (),
        "name": ("theme_title", title_key),
        "article": ("theme_title", title_key),
        "accents": (),
    }
    duality_title_entry = {
        "images": (),
        "name": ("week_duality_title", title_key),
        "article": ("week_duality", title_key),
        "accents": (),
    }
    good_entry = {
        "looks": looks_for(sun_path),
        "name": ruler_name,
        "article": ("article_face", face_article_set, "sun", "ruler"),
        "accents": defaults.BODY_ACCENT_HUES["sun"],
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    evil_entry = {
        "looks": looks_for(dual_path),
        "name": servant_name,
        "article": ("article_face", face_article_set, "sun", "servant"),
        "accents": defaults.BODY_ACCENT_HUES["sun"],
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    return (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry, evil_entry]
    )


def _wider_topic(theme: str) -> list[dict]:
    """THE WIDER COURT — a culture's seatless A-list figures, folded
    back in as a TRAILING third block (round R8d, restoring WORKPLAN
    Session 8's content after round R8b deleted its standalone topics
    as misdiagnosed "duplicate tiles" — see `_WIDER_FIGURES` above): a
    section TITLE page (`"<theme>_wider"` in `encyclopedia.json`'s
    `theme_title` family, the SAME family `_pantheon_topic`'s
    `"<theme>_pantheon"` title reads, Rule #5) followed by one ordinary
    single-image page per figure — sourced from the exact same
    `EncyclopediaRepository.entry("wider", name)` family the deleted
    topics read, so the prose is untouched, only its HOME moved. NO
    `looks` key: ground-truthed against the asset tree
    (`assets/weekday/<source>/<theme>/wider/`) — none of the fifteen
    figures has ANY art yet, not even a bronze master, so there is
    nothing to cycle; the page renders on `"images"` alone and stays
    gracefully absent (a name and a text, no plate) exactly like the
    old standalone topics did, until the owner's art lands."""
    title_key = f"{theme}_wider"
    title_entry = {
        "images": (),
        "name": ("theme_title", title_key),
        "article": ("theme_title", title_key),
        "accents": (),
    }
    figure_entries = [
        {
            "images": (
                defaults.WEEKDAY_ART_DIR / theme / "wider"
                / f"{figure.lower()}.png",
            ),
            "name": figure,
            "article": ("emblem", "wider", figure),
            "accents": (),
        }
        for figure in _WIDER_FIGURES[theme]
    ]
    return [title_entry] + figure_entries


def _continents_topic(travel_date: date) -> dict:
    """THE CONTINENTS topic (owner-sealed matrix 2026-07-21) — a CUSTOM
    weekday-shaped topic that OVERWRITES the generic `_weekday_topic`
    build so it can carry the world-map TITLE page and the Atmosphere/
    Clean · Day/Night LOOK SWITCHER on every earth-face page (the generic
    build gives a single unlabeled look). The eleven pages keep the same
    ORDER as every restructured theme (title, Monday..Saturday, duality
    title, Antarctic Ruler, Arctic Servant, Ninth) so the Spacebar remap
    and the article-order canon still hold.

    The six continent bodies and the two poles reuse the dial's OWN Earth
    faces (assets/earth/, owner exception, sealed) and their prose is the
    SAME symbolism.json articles the dial hover reads (Rule #5). The Ninth
    is LIVING: Zealandia the Unfound normally, Pangea on a Pangea day
    (`core.continents` against the traveled date and the bundled Seasons/
    Moon data) — both articles exist; the plate is graceful-absent until
    the owner's art lands, like every wired-ahead Ninth.

    THE LOOK-SWITCHER default (honest choice): the static gallery cannot
    read the live sky, so every earth-face page OPENS on "Atmosphere"
    (atmo · day) and offers all four looks; the LIVE-sky default belongs
    to the dial, where `continents_body_art` reads the tick. Finish
    persistence carries the chosen look across the pages exactly as it
    does the metal finishes."""
    def region_looks(region: str) -> tuple:
        return tuple(
            (label, ((defaults.earth_face_art(style, region, phase),),))
            for label, style, phase in (
                ("Atmosphere", "atmo", "day"),
                ("Atmosphere · Night", "atmo", "night"),
                ("Clean", "clean", "day"),
                ("Clean · Night", "clean", "night"),
            )
        )

    def body_entry(body: str) -> dict:
        return {
            "looks": region_looks(defaults.CONTINENTS_REGIONS[body]),
            "name": defaults.WEEKDAY_THEME_NAMES["continents"][body],
            "article": ("article", "continents", body),
            "accents": defaults.BODY_ACCENT_HUES[body],
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES["continents"]
    title_entry = {
        "images": (defaults.CONTINENTS_TITLE_IMAGE,),
        "name": ("theme_title", "continents"),
        "article": ("theme_title", "continents"),
        "accents": (),
    }
    duality_title_entry = {
        # The two poles in eternal antiphase, side by side.
        "images": (
            defaults.earth_face_art("atmo", "south_pole", "day"),
            defaults.earth_face_art("atmo", "north_pole", "day"),
        ),
        "name": ("week_duality_title", "continents"),
        "article": ("week_duality", "continents"),
        "accents": (),
    }
    good_entry = {
        "looks": region_looks("south_pole"),
        "name": ruler_name,
        "article": ("article_face", "continents", "sun", "ruler"),
        "accents": defaults.BODY_ACCENT_HUES["sun"],
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    evil_entry = {
        "looks": region_looks("north_pole"),
        "name": servant_name,
        "article": ("article_face", "continents", "sun", "servant"),
        "accents": defaults.BODY_ACCENT_HUES["sun"],
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    pangea = continents.ninth_is_pangea_from_repos(
        travel_date, SeasonsRepository(), MoonPhaseRepository()
    )
    ninth_name, ninth_rel = (
        constants.WEEKDAY_THEME_NINTH_EASTER_EGG["continents"]
        if pangea
        else constants.WEEKDAY_THEME_NINTHS["continents"]
    )
    ninth_entry = {
        "images": (defaults.WEEKDAY_ART_DIR / ninth_rel,),
        "name": ninth_name,
        "article": ("emblem", "ninths", ninth_name),
        "accents": (),
    }
    entries = (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry, evil_entry, ninth_entry]
    )
    return {
        "title": defaults.WEEKDAY_THEME_TITLES["continents"],
        "icon": defaults.CONTINENTS_TITLE_IMAGE,
        "entries": entries,
    }


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
    # THE CONTINENTS overwrite its generic weekday build with the custom
    # topic (world-map title, look switcher, living Ninth) — same 11-page
    # order, so the Spacebar remap below still lands (owner-sealed matrix
    # 2026-07-21). Its Ninth is built HERE, so the shared ninths loop
    # skips it (see the guard there).
    topics["continents"] = _continents_topic(travel_date)
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
    # THE NINE INTELLIGENCES (owner GO 2026-07-13; canon-web REWRITE +
    # WEEKDAY-LAW reseat, owner-sealed R7b 2026-07-21): Gardner's nine
    # move onto the seats the clock already keeps — SIX on the weekday
    # arms (Mon Interpersonal, Tue Bodily-Kinesthetic, Wed Linguistic,
    # Thu Logical-Mathematical, Fri Musical, Sat Naturalist), THREE on
    # the Sun's own faces (RULER = Visual-Spatial, the all-seeing king;
    # SERVANT = Intrapersonal, the self-mirror at solar midnight; NINTH
    # = Existential, The Unfound, the question itself at the noon
    # window). The page order follows the weekday law like every
    # restructured theme: title -> Mon..Sat -> Ruler -> Servant ->
    # Ninth (no separate trio-title page — the title page's own "The
    # Sun's Three Faces" subhead introduces the trio; the flat emblem
    # machinery wants none). The badge art stems are unchanged — only
    # the DIAL SEAT of each intelligence moved, not the plate.
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
                ("Interpersonal", "interpersonal"),               # Monday
                ("Bodily-Kinesthetic", "bodily_kinesthetic"),     # Tuesday
                ("Linguistic", "linguistic"),                     # Wednesday
                ("Logical-Mathematical", "logical_mathematical"), # Thursday
                ("Musical", "musical"),                           # Friday
                ("Naturalist", "naturalist"),                     # Saturday
                ("Spatial", "spatial"),                           # Sun · Ruler
                ("Intrapersonal", "intrapersonal"),               # Sun · Servant
                ("Existential", "existential"),                   # Ninth
            )
        ],
    }
    # THE SLAVIC MONTHS (owner-sealed R7b 2026-07-21): the Croatian
    # months as a Calendar-pointer 12-set + its own topic — the year's
    # own wheel of labour (etymology, the pan-Slavic siblings, the mark's
    # place on the Calendar pointer wedge). Built from
    # `defaults.SLAVIC_MONTHS` (Rule #4/#5 — one config table drives the
    # display name, the article key and the plate stem). Plates are a
    # FUTURE prompt sheet under the canonical sourceless `months/` root
    # (defaults.MONTHS_ART_DIR, graceful-absent). Rides The Celestial
    # Engine hall (the year's own wheel — see _TOPIC_GROUPS).
    topics["months"] = {
        "title": "The Slavic Months",
        # The Linden Month (June, the wheel's crown) fronts the gallery
        # card — graceful-absent like every month plate until the art
        # lands, so the card shows its name until then.
        "icon": defaults.MONTHS_ART_DIR / "Lipanj.png",
        "entries": [{
            "images": (),
            "name": "The Slavic Months",
            "article": ("emblem", "months", "The Slavic Months"),
            "accents": (),
        }] + [
            {
                "images": (defaults.MONTHS_ART_DIR / f"{stem}.png",),
                "name": f"{croatian} ({gloss})",
                "article": ("emblem", "months", croatian),
                "accents": (),
            }
            for croatian, gloss, stem, _month in defaults.SLAVIC_MONTHS
        ],
    }
    # THE NINTHS close their topics (owner 8+1 doctrine 2026-07-14):
    # the excluded member, the event, the myth, the legend — plates
    # wired ahead of the art (missing files stay hidden). Their shared
    # philosophical NAME is NINTH_SEAT_PHILOSOPHICAL_NAME (module level,
    # above) — see there for the discussed alternatives.
    _w = defaults.WEEKDAY_ART_DIR
    _z = defaults.ZODIAC_ART_DIR
    # Round-four/five verdicts (owner 2026-07-15): the Union ninths —
    # Gaia/Yggdrasil/Triglav/the Pharaoh/the Polymath/the Holy Trinity/
    # the Ninth Circle/Freemasonry — supersede the old exile ninths;
    # Melchizedek relocates to Bible II, the Unknown God to the
    # Ancient set. Retired entries stay in encyclopedia.json for the
    # Wider-Pantheon wave. The 15 WEEKDAY themes' ninths now live in
    # `constants.WEEKDAY_THEME_NINTHS` (round R3b item 3 — the SAME
    # table the CENTER seat's solar-window face law reads, Rule #5);
    # the two ZODIAC-only ninths (no weekday Sunday duality) stay
    # local, since render never needs them.
    for topic_key, name, plate in (
        *(
            (theme, name, _w / rel)
            for theme, (name, rel) in constants.WEEKDAY_THEME_NINTHS.items()
            # THE CONTINENTS builds its own LIVING Ninth inside
            # `_continents_topic` (Zealandia/Pangea by the traveled day),
            # so this shared static append must skip it (owner-sealed
            # matrix 2026-07-21).
            if theme != "continents"
        ),
        ("chinese", "The Cat", _z / "chinese/primary/Cat.png"),
        ("astrology", "Ophiuchus", _z / "astrology/sign/Ophiuchus.png"),
    ):
        ninth_entry = {
            "images": (plate,),
            "name": name,
            "article": ("emblem", "ninths", name),
            "accents": (),
        }
        # THE NINTH'S OWN FINISH SWITCHER (owner bug, Gaia screenshot —
        # round R3): every metal-plate theme's Ninth gets the SAME
        # Colored/Bronze/Gold/Silver cycle as its seated eight.
        ninth_looks = _ninth_looks(topic_key, plate)
        if ninth_looks is not None:
            ninth_entry["looks"] = ninth_looks
        topics[topic_key]["entries"].append(ninth_entry)
    # THE PANTHEON/PLANETARY MERGE (round R3b item 2): pages 12-22 —
    # the SAME 11-page shape all over again, in the culture's OWN
    # hierarchy roster, reusing the ninth entry the loop above JUST
    # appended (`entries[-1]`) rather than building a second one — the
    # SAME figure closes both blocks (CANON.md: one Ninth per theme).
    # THE WIDER COURT (round R8d) then trails as a third block, page 23
    # onward — see `_wider_topic` above.
    for theme in _PANTHEON_MERGED_THEMES:
        entries = topics[theme]["entries"]
        assert len(entries) == _PANTHEON_BLOCK_SIZE, (
            theme, len(entries)
        )  # every Pantheon culture also names a Ninth (documented)
        entries.extend(_pantheon_topic(theme))
        entries.append(entries[_PANTHEON_BLOCK_SIZE - 1])
        entries.extend(_wider_topic(theme))
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
        # NON-MODAL lifecycle (ITEM 1, R4 owner instruction batch
        # 2026-07-20): the controller `.show()`s this dialog instead of
        # `.exec()`ing it — the dial stays interactive while it is
        # open. The controller keeps the ONE live instance as an
        # attribute (raising it, or navigating it via `navigate_to`,
        # on a second open request instead of stacking a duplicate) and
        # clears it on this dialog's `finished` signal; WA_DeleteOnClose
        # tears the C++ object down the moment the window closes.
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
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
        # Every text label spans the FULL block width now (round R3b
        # item 1: the old DUAL page's two side-by-side half-width
        # columns retired with the merged page — GOOD and EVIL are
        # each an ordinary single-column page).
        self._text_labels: list[QLabel] = []
        self._name_labels: list[QLabel] = []
        self._topic_cards: list[QToolButton] = []
        self._pixmap_cache: dict[str, QPixmap] = {}
        # FINISH PERSISTENCE (owner INSTRUCTION #3): once picked, a
        # look/finish (e.g. Bronze) rides EVERY following entry that
        # offers it — never resets to the topic's own default on a page
        # turn or a topic change. `None` = no preference set yet (each
        # entry opens on ITS own default look, index 0).
        self._preferred_look_label: str | None = None
        self._look_state: dict | None = None

        self._title = QLabel()
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: {defaults.GUIDE_TITLE_PX}px; font-weight: bold;"
            f"margin: {defaults.GUIDE_SPACING_PX}px;"
        )
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        # THE SESSION ZOOM (owner round R8b item 5b): seeded from
        # whatever the LAST open Encyclopedia window left it at
        # (`_session_zoom`, module-level); an event filter on the
        # scroll area's own VIEWPORT catches Ctrl+wheel before the
        # scroll logic ever sees it — plain wheel keeps scrolling
        # normally (`eventFilter` below).
        self._zoom = _session_zoom
        self._scroll.viewport().installEventFilter(self)
        self._topic_key: str | None = None
        self._entry_index = 0
        # The reader chrome (owner 2026-07-14: big, vivid, modern —
        # Home top-left, Download top-right, the pager bottom-center).
        self._back = QPushButton("⌂  " + self._tr("Home"))
        self._back.clicked.connect(self._show_topics)
        style_button(self._back, "home")
        # THE PANTHEON/PLANETARY ROSTER SWITCH (Ency INSTRUCTIONS.txt
        # rule 5, round R3b item 2): between Home and Download, ONLY on
        # the four merged themes — its logo shows the roster the click
        # would SWITCH TO (built once here, restyled per page by
        # `_update_roster_button`, called from `_show_entry`).
        self._planetary_icon = _svg_icon(_PLANETARY_ORBIT_SVG, 28)
        self._pantheon_icon = _svg_icon(_PANTHEON_TEMPLE_SVG, 28)
        self._roster_button = QToolButton()
        style_button(self._roster_button, "neutral", small=True)
        self._roster_button.setIconSize(QSize(24, 24))
        self._roster_button.clicked.connect(self._switch_roster)
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
        # THE FINISH SWITCHER (owner fix round R3, Color Switcher.png):
        # moved to the TOP row, in line with Home and Download — ONE
        # persistent set of widgets (not rebuilt per entry, like the
        # pager) driving whichever entry's `self._look_state` is
        # active; `_show_entry` swaps that reference and shows/hides
        # the trio, `_cycle_look` restyles the caption per finish.
        self._look_back = QToolButton()
        self._look_back.setText("◀")
        style_button(self._look_back, "neutral", small=True)
        self._look_back.clicked.connect(lambda: self._cycle_look(-1))
        self._look_caption = QLabel()
        self._look_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._look_caption.setMinimumWidth(120)
        self._look_forward = QToolButton()
        self._look_forward.setText("▶")
        style_button(self._look_forward, "neutral", small=True)
        self._look_forward.clicked.connect(lambda: self._cycle_look(1))
        top = QHBoxLayout()
        top.addWidget(self._back)
        top.addWidget(self._roster_button)
        top.addStretch(1)
        top.addWidget(self._look_back)
        top.addWidget(self._look_caption)
        top.addWidget(self._look_forward)
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
        # LAYOUT fix round R3 (owner: MIN WIDTH = 4 * the single theme
        # tile, "788px width, tiles clipping" dies here); the WIDTH
        # itself is `_gallery_content_width` (owner round R8b item 5a
        # fix — the old ad hoc `tile * columns` arithmetic dropped the
        # inter-card spacing and the column's own margins, reliably
        # undersizing this minimum and letting the frame overflow at
        # exactly this width) — never let the window shrink so far that
        # a max-width (4-column) gallery row would have to spill
        # sideways; the scroll area's own vertical bar is the only
        # overflow this dialog ever needs.
        min_width = _gallery_content_width(
            defaults.ENCYCLOPEDIA_TOPIC_ICON_MIN_PX
        )
        self.setMinimumWidth(min_width)
        # OPENING SIZE (owner DESIGN #1, R4): A4 portrait at 80% of the
        # screen's available height — the R3 min-width law above still
        # wins when it is the larger of the two (`size_to_screen`'s
        # documented resolution), so the 4-tile gallery row never spills.
        size_to_screen(
            self, defaults.DIALOG_A4_ASPECT_W, defaults.DIALOG_A4_ASPECT_H,
            defaults.DIALOG_A4_HEIGHT_FRACTION, min_width=min_width,
        )
        apply_theme(self)
        self._show_topics()
        # The Spacebar jump (owner 2026-07-16, ROADMAP queue #8): open
        # straight onto the hovered topic's matching entry, skipping the
        # gallery — unknown topics fall back to the gallery. Reused by
        # `navigate_to` below (ITEM 1, R4): a second SPACE jump while
        # this window is already open now NAVIGATES it live instead of
        # being a no-op.
        self.navigate_to(initial_topic, initial_entry)

    def navigate_to(self, topic: str | None, entry: int = 0) -> None:
        """Jump this LIVE window to a new (topic, entry) target — the
        exact placement logic `__init__` runs once at construction,
        reused now that a second SPACE jump while the Encyclopedia is
        already open navigates the live window instead of being a
        no-op (ITEM 1, R4 owner instruction batch 2026-07-20).
        `topic=None` (the menu's plain "Encyclopedia…" entry re-opening
        onto an already-live window) leaves the window on whatever page
        the user is already browsing — only a THEMED jump (a real
        topic) moves it. Unknown topics are also a no-op (defensive:
        the controller only ever passes a topic the compositor itself
        named). Round R3 item 9: a restructured weekday topic's raw
        compositor index is remapped first (see
        `_WEEKDAY_DUAL_PAGE_INDEX` above)."""
        if topic is None or topic not in self._topics:
            return
        self._topic_key = topic
        entries = self._topics[topic]["entries"]
        entry_index = entry
        if topic in _WEEKDAY_RESTRUCTURED_TOPICS and entry == 0:
            entry_index = _WEEKDAY_DUAL_PAGE_INDEX
        self._entry_index = min(entry_index, len(entries) - 1) if entries else 0
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
        if kind == "article_face":
            # The GOOD/EVIL split pages (owner verdict A, round R3b
            # item 1): ref = ("article_face", article_set, body, face)
            # — resolves through the SAME "faces" register the dial
            # hover reads (`render.compositor._sun_face_tooltip`),
            # falling back to "base" for a theme whose split has not
            # landed (documented graceful path, Rule #1 — never a
            # KeyError, just the shared read until then).
            node = self._symbolism.article(ref[1], ref[2])
            return node.get("faces", {}).get(ref[3]) or node["base"]
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
        if kind == "theme_title":
            return self._encyclopedia.theme_title(ref[1])["base"]
        if kind == "week_duality":
            return self._encyclopedia.week_duality(ref[1])["base"]
        return self._symbolism.trio_article(ref[1])["base"]

    def _entry_name(self, entry: dict) -> str:
        """An entry's display name — THE ONE BUILD POINT (owner round
        R8b item 8: "Selene — Monday", every weekday-figure title shows
        its day; "encyclopedia builds titles centrally, do it at the
        ONE build point"): the WEEK, INSTRUMENT and SEASONS pages take
        their titles from the encyclopedia database (localized there);
        everything else translates through the UI overlay. A
        `"weekday"` key on `entry` (set by `_weekday_topic`/
        `_pantheon_topic`/`_continents_topic`'s body/good/evil builders
        — never the title pages or the Ninth, which sits OUTSIDE the
        weekday, CANON.md) appends " — {Weekday}" here and ONLY here,
        so no other call site needs to know the convention exists."""
        name = entry["name"]
        if isinstance(name, tuple):
            if name[0] == "week_title":
                base = self._encyclopedia.week(name[1])["title"]
            elif name[0] == "season_title":
                base = self._encyclopedia.season(name[1])["title"]
            elif name[0] == "sun_title":
                base = self._encyclopedia.sun(name[1])["title"]
            elif name[0] == "moon_title":
                base = self._encyclopedia.moon(name[1])["title"]
            elif name[0] == "era_title":
                base = self._encyclopedia.era(name[1])["title"]
            elif name[0] == "eclipse_title":
                base = self._encyclopedia.eclipse(name[1])["title"]
            elif name[0] == "theme_title":
                base = self._encyclopedia.theme_title(name[1])["title"]
            elif name[0] == "week_duality_title":
                base = self._encyclopedia.week_duality(name[1])["title"]
            else:
                base = self._encyclopedia.instrument(name[1])["title"]
        else:
            base = self._tr(name)
        weekday = entry.get("weekday")
        if weekday:
            return f"{base} — {self._tr(weekday)}"
        return base

    def _build_topic_card(self, key: str) -> QToolButton:
        """One gallery tile — factored out of `_show_topics` (owner
        round R8b item 5c: the subgroup rewrite builds MANY row runs,
        not one shared grid, so every caller needs the SAME card
        recipe, Rule #5). `_GOD_TOPIC_GALLERY_TITLES` overrides the
        four god topics' tile text (item 6: "Greek", not "Greek
        gods")."""
        topic = self._topics[key]
        card = QToolButton()
        card.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        card.setText(
            self._tr(_GOD_TOPIC_GALLERY_TITLES.get(key, topic["title"]))
        )
        icon = paths.art_file(topic["icon"])
        if icon is not None and icon.exists():
            # The FULL-RES art backs the icon — QIcon renders whatever
            # size _rescale_topics asks for.
            card.setIcon(QIcon(str(icon)))
        card.clicked.connect(
            lambda checked=False, chosen=key: self._show_topic(chosen)
        )
        self._topic_cards.append(card)
        return card

    def _build_gallery_rows(self, keys: tuple[str, ...]) -> QVBoxLayout:
        """`keys` chunked into ENCYCLOPEDIA_GALLERY_MAX_COLUMNS-wide
        rows (owner round R8b item 5): each row is its OWN QHBoxLayout
        with a stretch on BOTH sides, so every row — a full one or a
        trailing short one — centers as a block with no special case
        (item 5d: "red sa manje od 4 clana... centrirani"). The fixed
        per-row card count plus `_rescale_topics`'s own
        `min(icon, width_share)` ceiling together guarantee no row can
        ever force a horizontal scrollbar (item 5a), at any window
        width or zoom level."""
        rows = QVBoxLayout()
        rows.setSpacing(defaults.GUIDE_SPACING_PX * 2)
        columns = defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS
        for start in range(0, len(keys), columns):
            row = QHBoxLayout()
            row.setSpacing(defaults.GUIDE_SPACING_PX * 2)
            row.addStretch(1)
            for key in keys[start:start + columns]:
                row.addWidget(self._build_topic_card(key))
            row.addStretch(1)
            rows.addLayout(row)
        return rows

    def _show_topics(self) -> None:
        """Screen 1 — the topic gallery in the owner's FIVE sections
        (GALLERY LAYOUT REWORK v2, owner round R8b item 5), EVERYTHING
        centered (owner 2026-07-13): every hall's own BIG CENTERED
        title always leads (unchanged); an OVERLOADED hall additionally
        partitions into LEFT-ALIGNED subgroup headings
        (`_GALLERY_SUBGROUPS`, item 5c) that unify its tiles into
        smaller kinship clusters — every other hall stays one flat run
        of rows. `_build_gallery_rows` (not a QGridLayout any more)
        both centers short rows (item 5d) and, together with
        `_rescale_topics`'s width-clamped icon size, keeps this gallery
        from EVER spilling a horizontal scrollbar (item 5a) — the
        dialog's own MIN WIDTH (set once in __init__) keeps a full row
        readable even at the minimum icon size and zoomed all the way
        out."""
        self._title.setText(self._tr("Encyclopedia"))
        self._topic_key = None
        self._back.hide()
        self._download.hide()
        self._previous.hide()
        self._counter.hide()
        self._next.hide()
        self._look_back.hide()
        self._look_caption.hide()
        self._look_forward.hide()
        self._roster_button.hide()
        self._look_state = None
        self._cells = []
        self._blocks = []
        self._text_labels = []
        self._name_labels = []
        self._topic_cards = []
        content = QWidget()
        column = QVBoxLayout(content)
        column.setSpacing(defaults.GUIDE_SPACING_PX)
        # A KNOWN, explicit margin (owner round R8b item 5a fix) — NOT
        # Qt's unstated QVBoxLayout default (9px each side): the exact
        # value `_gallery_content_width`/`_gallery_icon_ceiling` above
        # both bake in, so the no-overflow guarantee has no hidden
        # fudge factor left to drift if a future Qt/theme change alters
        # that default.
        column.setContentsMargins(
            defaults.GUIDE_SPACING_PX, defaults.GUIDE_SPACING_PX,
            defaults.GUIDE_SPACING_PX, defaults.GUIDE_SPACING_PX,
        )
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
            if not keys:
                continue          # The Archetypes: empty until Sessions 6/8
            subgroups = _GALLERY_SUBGROUPS.get(group_title)
            if subgroups is None:
                column.addLayout(self._build_gallery_rows(keys))
                continue
            for sub_title, sub_keys in subgroups:
                sub_header = QLabel(self._tr(sub_title))
                sub_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
                sub_header.setStyleSheet(
                    f"font-size: {defaults.GUIDE_SUBTITLE_PX}px;"
                    "font-weight: bold;"
                    f"margin-top: {defaults.GUIDE_SPACING_PX}px;"
                )
                column.addWidget(sub_header)
                column.addLayout(self._build_gallery_rows(sub_keys))
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

    def _switch_roster(self) -> None:
        """The PANTHEON <-> PLANETARY logo button (Ency
        INSTRUCTIONS.txt rule 5, round R3b item 2): jumps to the SAME
        position inside the other 11-page block — Monday stays Monday,
        the dual title stays the dual title, and so on."""
        span = _PANTHEON_BLOCK_SIZE
        self._entry_index = (
            self._entry_index + span if self._entry_index < span
            else self._entry_index - span
        )
        self._show_entry()

    def _update_roster_button(self) -> None:
        """Show/restyle the roster-switch button for the OPEN page
        (round R3b item 2) — hidden outside the four merged themes;
        otherwise its logo shows the roster a click would SWITCH TO,
        and it flips automatically when Next/Previous cross the 11/12
        boundary (this is called from `_show_entry` on every page turn,
        so no separate boundary-watch is needed). HIDDEN on The Wider
        Court block too (round R8d, page 23 on): the button's whole
        contract is "jump to the SAME day in the OTHER 11-page roster"
        (Monday stays Monday) — the Wider Court has no such twin block
        to jump to (it is a single trailing run of figures, not a
        second roster the length of the other two), so there is no
        sane destination to name on its icon. Hiding it here is the
        SAME guard this method already applies to every non-merged
        topic, not a new special case."""
        if (
            self._topic_key not in _PANTHEON_MERGED_THEMES
            or self._entry_index >= _WIDER_BLOCK_START
        ):
            self._roster_button.hide()
            return
        in_pantheon_block = self._entry_index >= _PANTHEON_BLOCK_SIZE
        self._roster_button.setIcon(
            self._planetary_icon if in_pantheon_block else self._pantheon_icon
        )
        self._roster_button.setToolTip(
            self._tr("Planetary") if in_pantheon_block else self._tr("Pantheon")
        )
        self._roster_button.show()

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
        lines = [name, ""]
        # Every page — including the GOOD/EVIL halves since their split
        # (round R3b item 1) — is now a single-text page like any
        # other; the old two-face DUAL branch retired with the merged
        # page (Rule #6, no dead special case left behind).
        text = _HEX_NOTE.sub("", self._article_text(entry["article"]))
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

    def _topic_display_title(self) -> str:
        """The reader's TOP header (owner round R8b item 8: "mora gore
        pored naslova cele tematike da piše i da li smo na sekciji
        Panteon ili Planetary" — fix BOTH title spots to a coherent
        pair, no bare topic name stacked twice, his screenshot showed
        "Greek gods" over "Greek gods"): the topic's own title —
        `_GOD_TOPIC_GALLERY_TITLES` overriding the god-topic tiles
        exactly like the gallery card (item 6) — plus, for the four
        merged Planetary/Pantheon themes ONLY, which SECTION this page
        belongs to. The per-entry caption below (`_entry_name`) reads
        the DATABASE's own theme_title text ("Greek gods" / "Greek
        Pantheon") — a different string in a different register, so
        the pair never repeats the identical bare name twice. Learns a
        THIRD section (round R8d): "Wider Court", page 23 on."""
        topic = self._topics[self._topic_key]
        title = self._tr(
            _GOD_TOPIC_GALLERY_TITLES.get(self._topic_key, topic["title"])
        )
        if self._topic_key in _PANTHEON_MERGED_THEMES:
            if self._entry_index >= _WIDER_BLOCK_START:
                section = self._tr("Wider Court")
            elif self._entry_index >= _PANTHEON_BLOCK_SIZE:
                section = self._tr("Pantheon")
            else:
                section = self._tr("Planetary")
            title = f"{title} — {section}"
        return title

    def _show_entry(self) -> None:
        """The current entry's PAGE: the images row (the Astrology
        pair sits side by side), the bold name and the text, all
        inside ONE block (owner: center the whole object, never the
        text lines)."""
        topic = self._topics[self._topic_key]
        entries = topic["entries"]
        entry = entries[self._entry_index]
        self._title.setText(self._topic_display_title())
        self._back.show()
        self._download.show()
        self._update_roster_button()
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
        # FINISH PERSISTENCE (owner INSTRUCTION #3): a page opens on the
        # LAST look the user picked, if this entry offers it — never a
        # silent reset to the topic's own default (owner: "sve naredne
        # slike treba da ostanu u BRONZE a ne da uvek FORSIRA COLORED").
        start_index = 0
        if self._preferred_look_label in titles:
            start_index = titles.index(self._preferred_look_label)
        state = {
            "container": None,
            "looks": look_rows,
            "titles": titles,
            "index": start_index,
        }
        if look_rows:
            container = QWidget()
            state["container"] = container
            cell.addWidget(
                container, alignment=Qt.AlignmentFlag.AlignHCenter
            )
            self._cells.append(state)
        # THE FINISH SWITCHER (owner fix round R3): the persistent top-
        # row trio (Home | ◀ finish ▶ | Download) drives WHICHEVER
        # entry is open — no per-entry widgets to build or wire here
        # anymore, just point it at this entry's look state.
        self._look_state = state if len(look_rows) > 1 else None
        multi_look = self._look_state is not None
        self._look_back.setVisible(multi_look)
        self._look_caption.setVisible(multi_look)
        self._look_forward.setVisible(multi_look)
        if multi_look:
            self._update_look_caption()
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
            text.setWordWrap(True)
            text.setTextFormat(Qt.TextFormat.RichText)
            text.setAlignment(Qt.AlignmentFlag.AlignTop)
            self._text_labels.append(text)
            cell.addWidget(text)
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
            text.setAlignment(Qt.AlignmentFlag.AlignTop)
            self._text_labels.append(text)
            cell.addWidget(text)
        self._blocks.append(block)
        # The block sits CENTERED with even side margins (owner
        # 2026-07-14: "ravnomerno po sredini" — supersedes the
        # left-hug of 2026-07-13).
        column.addWidget(block, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addStretch(1)
        # THE INVISIBLE CLIPPER (owner bug, "Nevidljivi element seče
        # pasus The Lesson" — root cause found fix round R3): fit the
        # block's width/font/pixmaps BEFORE `setWidget` ever hands this
        # widget to the scroll area. QScrollArea's widgetResizable path
        # sizes a FRESH widget to the viewport on its first pass and
        # only grows it to the true heightForWidth sizeHint on a SECOND
        # pass — but Next/Previous never yield to the event loop, so
        # the single frame the user sees is the too-short guess: the
        # tail of the article is clipped AND the scrollbar range comes
        # back 0 (the text "counts as in view" — nothing below it
        # exists to scroll to). Calling `_rescale()` while `content` is
        # NOT YET the scroll area's widget sidesteps the race: `_blocks`
        # / `_text_labels` / `_cells` are already populated above, so
        # the width fit, font size and image grid all resolve to their
        # FINAL sizes first, and `setWidget` then only ever sees one,
        # already-correct, geometry.
        self._rescale()
        self._scroll.setWidget(content)
        self._scroll.verticalScrollBar().setValue(0)

    def _block_width(self) -> int:
        """The article block's width — ONE formula (Rule #5: `_rescale`
        and `_cycle_look` both need it, and used to drift when each
        computed it separately) — the configured fraction of the
        viewport, `self._zoom` (item 5b) scaling it further but NEVER
        past the viewport itself (item 5a: no horizontal scrollbar,
        ever)."""
        viewport = max(320, self._scroll.viewport().width())
        return min(
            viewport,
            round(
                viewport * defaults.ENCYCLOPEDIA_TEXT_WIDTH_FRACTION
                * self._zoom
            ),
        )

    def _rescale(self) -> None:
        """Everything follows the window — on the gallery the card
        icons resize between their bounds; on a topic each entry BLOCK
        spans the configured width fraction, the images share the
        block, and the font grows with the width at the gentle em-like
        coefficient. `self._zoom` (owner round R8b item 5b, Ctrl+wheel)
        then scales the RESULT on top: the block width may grow up to
        the full viewport (never past it — item 5a's no-overflow
        invariant still wins), and fonts/images grow past their
        width-driven ceiling once the block has nowhere wider to go, so
        zooming in keeps doing something even at max block width."""
        if self._topic_cards:
            self._rescale_topics()
            return
        viewport = max(320, self._scroll.viewport().width())
        block_width = self._block_width()
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
        font_px = max(1, round(font_px * self._zoom))
        for label in self._text_labels:
            # A real QFont (owner bug fix round R3, THE INVISIBLE
            # CLIPPER: "Nevidljivi element seče pasus The Lesson"):
            # `setStyleSheet` routes a font-size change through Qt's
            # CSS engine, which only takes effect on the widget's NEXT
            # style polish — a rich-text QLabel's `heightForWidth`
            # queried (by the surrounding QVBoxLayout, mid-relayout)
            # before that polish still measures the OLD font, so the
            # label is allocated a shorter box than the new font
            # actually needs and the tail of the article is silently
            # clipped. `setFont` applies synchronously, so the very
            # first layout pass already measures the right font.
            font = label.font()
            font.setPixelSize(font_px)
            label.setFont(font)
            # RESERVE the article's full height (the same law as the
            # image reservation below, ROADMAP queue #9): now that the
            # font is final, `heightForWidth` measures true — pinning
            # it here means the block/scroll canvas negotiate around
            # the REAL text height on their one and only pass, instead
            # of settling on whatever a stale intermediate guess left
            # behind (THE INVISIBLE CLIPPER bug, fix round R3). Every
            # label spans the full block width (round R3b item 1: the
            # DUAL page's half-width columns retired with the merge).
            label.setFixedHeight(label.heightForWidth(block_width))
        for label in self._name_labels:
            font = label.font()
            font.setPixelSize(font_px + 3)
            label.setFont(font)
        for state in self._cells:
            # First pass builds the grid; resizes only re-fit pixmaps.
            if "cells" in state:
                self._resize_cell(state, block_width)
            else:
                self._render_cell(state, block_width)

    def _rescale_topics(self) -> None:
        """The gallery cards follow the window (owner 2026-07-13, LAYOUT
        fix round R3; GALLERY LAYOUT REWORK v2, owner round R8b item 5):
        every row (`_build_gallery_rows`) holds exactly
        ENCYCLOPEDIA_GALLERY_MAX_COLUMNS cards, so the icon side is
        sized from WIDTH alone — `_gallery_icon_ceiling` is the exact
        LARGEST icon one column of the fixed row can ever afford, by
        construction, so a horizontal scrollbar can never appear (item
        5a; the R8b ground-truthed fix — the OLD `width_share`
        arithmetic silently dropped the columns*CARD_PADDING term,
        reliably overflowing the live dialog's own scrollbar). Zoom
        (item 5b) then scales the WIDTH-driven natural size up or down,
        but `min(icon, ceiling)` is a HARD cap regardless of zoom —
        zooming in on a narrow window saturates at the per-column
        budget instead of overflowing it; `card.setFixedSize` (not
        `setMinimumSize`) makes that ceiling absolute even against a
        long translated label that would otherwise widen its own
        button past the budget."""
        ceiling = _gallery_icon_ceiling(self._scroll.viewport().width())
        icon = max(
            defaults.ENCYCLOPEDIA_TOPIC_ICON_MIN_PX,
            min(defaults.ENCYCLOPEDIA_TOPIC_ICON_MAX_PX, ceiling),
        )
        icon = max(1, min(round(icon * self._zoom), ceiling))
        for card in self._topic_cards:
            card.setIconSize(QSize(icon, icon))
            card.setFixedSize(
                icon + defaults.ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX,
                icon + defaults.ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX + 4,
            )
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
                # IMAGE HOVER (owner spec: critical on multi-image
                # pages like the era calendars — "Byzantine"): every
                # article image names itself on hover.
                label.setToolTip(_image_tooltip(path))
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
        on screen). `self._zoom` (item 5b) scales the ceiling itself —
        WIDTH stays bounded by `block_width` alone (never the frame,
        item 5a), so zooming in only ever grows the page taller
        (vertical scroll, always allowed), never wider."""
        rows = max(1, state.get("rows", 1))
        ceiling = round(
            self._scroll.viewport().height()
            * defaults.READER_IMAGE_MAX_HEIGHT_FRACTION
            * self._zoom
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

    def _cycle_look(self, step: int) -> None:
        """The ◀ / ▶ switcher (owner fix round R3: moved to the TOP
        row, in line with Home/Download — ONE persistent widget trio
        driving `self._look_state`, the OPEN entry's look) — the next
        look of this entry, a metal finish or a kinship group. Every
        pick becomes the session's PREFERRED finish (owner
        INSTRUCTION #3: "sve naredne slike treba da ostanu" — it rides
        every following entry that offers the same look, never a
        silent reset)."""
        state = self._look_state
        if state is None:
            return
        state["index"] = (state["index"] + step) % len(state["looks"])
        self._preferred_look_label = state["titles"][state["index"]]
        self._update_look_caption()
        self._render_cell(state, self._block_width())

    def _update_look_caption(self) -> None:
        """Restyle the persistent top-row caption to the OPEN entry's
        CURRENT look — a FILLED pill in the finish/globe-look's own
        color (owner round R8b item 4, superseding the R3 border-only
        frame), or the neutral filled chip for a kinship-group switcher
        (Planets/Signs/Art and the like, never a metal or globe fill)."""
        state = self._look_state
        if state is None:
            return
        label = state["titles"][state["index"]]
        self._look_caption.setText(self._tr(label))
        style_look_chip(self._look_caption, label)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rescale()

    def showEvent(self, event) -> None:
        # The gallery is built BEFORE the window has its real geometry
        # — rescale once more on the first show (owner bug 2026-07-13:
        # deformed until a manual resize).
        super().showEvent(event)
        self._rescale()

    def _apply_zoom_delta(self, angle_delta_y: int) -> None:
        """One Ctrl+wheel notch (owner round R8b item 5b) — Qt reports
        ±120 `angleDelta().y()` per notch on a standard wheel (finer
        high-resolution wheels report smaller steps; `/120` still lands
        a fair fraction of one STEP for those). Clamped to
        `ENCYCLOPEDIA_ZOOM_RANGE` and written back to the MODULE-level
        `_session_zoom` so the next Encyclopedia window this app run
        opens seeds from where this one left off ("persisted for the
        session at least")."""
        global _session_zoom
        low, high = constants.ENCYCLOPEDIA_ZOOM_RANGE
        steps = angle_delta_y / 120.0
        self._zoom = max(
            low, min(high, self._zoom + steps * constants.ENCYCLOPEDIA_ZOOM_STEP)
        )
        _session_zoom = self._zoom
        self._rescale()

    def wheelEvent(self, event) -> None:  # noqa: N802 — Qt override
        """Ctrl+MouseWheel zooms the WHOLE encyclopedia (item 5b) when
        the cursor sits over the dialog's OWN chrome — the top button
        row, the title, the pager — outside the scroll viewport, which
        installs the identical guard as an event filter instead (Qt
        delivers a wheel event to whichever widget is under the cursor,
        not the top-level window, so both paths are needed to cover
        every cursor position). Plain wheel here is a no-op — there is
        nothing to scroll outside the viewport."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._apply_zoom_delta(event.angleDelta().y())
            event.accept()
            return
        super().wheelEvent(event)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 — Qt override
        """The SAME Ctrl+wheel zoom guard as `wheelEvent` above,
        installed on the scroll area's own VIEWPORT (item 5b, "Ctrl +
        moushe wheel... dakle idemo u 2 pristup"): a plain wheel here is
        NEVER touched — it falls through to the viewport's own
        wheelEvent and scrolls exactly as before; only Ctrl+wheel is
        intercepted before the scroll logic ever sees it."""
        if (
            obj is self._scroll.viewport()
            and event.type() == QEvent.Type.Wheel
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self._apply_zoom_delta(event.angleDelta().y())
            return True
        return super().eventFilter(obj, event)
