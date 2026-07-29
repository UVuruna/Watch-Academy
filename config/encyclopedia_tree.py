"""The Encyclopedia's THREE-LEVEL tree (owner Session 27, sealed
2026-07-28).

The rework replaced the old two-screen browser (one gallery of 39 tiles
in five halls -> article slider) with three levels:

1. **Home** — SIX wholes, 2x3, no scroll ever (the window's own minimum
   is the 1280x720 the owner specified, so the grid fits by geometry,
   not by luck).
2. **Themes** — the chosen whole's own theme cards, vertical scroll only.
3. **Article** — the page slider, with a VARIANT switcher in the title
   row for a theme that carries several registers of the same subject.

THE VARIANT LAW (owner decision, 2026-07-28): registers of ONE subject
merge into one theme card and become members of the switcher loop
(Greek: Planetary | Pantheon | Wider Court; Bible: Bible | Bible II |
Bible Dark; Creeds: Creeds | Ancient religions; Eclipses: Solar |
Lunar). DISTINCT subjects stay their own cards — Wolf and Bee are two
animals, Virtues and Sins are opposites, never two dresses of one thing.

Layer: config (pure — no Qt, no wall clock). This module is the ONE
table; `app/encyclopedia/` reads it and never re-declares a whole, a
membership or an accent of its own. Documentation:
config/encyclopedia_tree.md.
"""

from typing import NamedTuple

from config import defaults, palette


class Whole(NamedTuple):
    """One top-level card on the Home screen."""

    key: str
    title: str
    accent: str
    themes: tuple[str, ...]


# THE SIX WHOLES (owner-sealed 2026-07-28, "Instrument izdvojen"): the
# old five halls with The Celestial Engine split into the INSTRUMENT
# (the watch and its own wheels) and the ENGINE (the sky it computes),
# and the Cube canon promoted out of the old "The Archetypes" hall into
# a whole of its own — it now carries 7 of the 35 theme cards.
#
# THE ACCENTS are the Rose's own hues (`palette.ROSE_PALETTE`, sealed —
# Rule #5, one palette): six of the eight, each argued by the hour it
# stands on. The accent rides the card's edge, the breadcrumb and the
# article header, so the reader always knows which whole he is inside.
#
# COMPLETION WAVE I (Session 31, 2026-07-29) added three cards, each a
# card of its OWN rather than a switcher member — three DISTINCT
# subjects, which is what the variant law above turns on: the Greek
# bestiary beside the Greek gods in `divine`, the Chinese court beside
# the Chinese zodiac in `celestial`, and the Corporation beside the
# Professions in `human`. The nine-whole arc reseats all three
# (`divine` -> `gods`, `celestial` -> `sky` + `cosmos`, and the
# `profession`/`corporate` pair out of `human` into the new `worlds`);
# WORKPLAN-STRUCTURE.md §THE NINE WHOLES already names those
# destinations and states that its table SUPERSEDES the seats here.
#
# COMPLETION WAVE II (Session 32, 2026-07-29) added ONE card for three
# casts — `wow`, the merge declared in VARIANT_SOURCES below. It is the
# variant law's own shape rather than an exception to it: Alliance,
# Horde and Evil are three registers of ONE subject, the same nine seats
# read three times over. It seats in `human` beside the Professions and
# the Corporation until the nine-whole arc moves the whole group into
# `worlds` (WORKPLAN-STRUCTURE.md §THE NINE WHOLES names the franchise
# cards there explicitly, and that table supersedes this seat).
WHOLES = (
    Whole(
        # 12h yellow — the sun at the top of the dial; the instrument's
        # own noon, the moment the whole watch is built around.
        # The Guide (owner 2026-07-28: "jedno mesto za čitanje svega")
        # is the fifth card — the paged help book folded in from its own
        # retired window, built from the SAME `assets/.../guide/*.json`
        # it always used (Rule #5, no content copied).
        "instrument", "The Instrument", palette.ROSE_PALETTE[0],
        ("week", "instrument", "era", "months", "guide"),
    ),
    Whole(
        # 03h cyan — the deep-night sky, the hours the Engine's own
        # machinery (moon, seasons, eclipses) is read against.
        "celestial", "The Celestial Engine", palette.ROSE_PALETTE[5],
        ("moon", "sun", "seasons", "eclipses", "planets", "cosmos",
         "continents", "astrology", "chinese", "celestial_court"),
    ),
    Whole(
        # 24h purple — midnight, the winter solstice, the sacred hour.
        "divine", "The Divine", palette.ROSE_PALETTE[4],
        ("greek", "norse", "egypt", "slavic", "age_of_heroes",
         "creeds", "bible"),
    ),
    Whole(
        # 18h red — sunset, the autumn equinox, Lucifer's own hue on the
        # Scale: the human fire, which is what this whole reads.
        "human", "The Human Wheel", palette.ROSE_PALETTE[2],
        ("virtues", "sins", "moods", "intelligences", "profession",
         "corporate", "wow", "trinity", "duality"),
    ),
    Whole(
        # 06h blue — sunrise, the spring equinox, Judas's hue: the Cube's
        # own axis blue (CUBE.md, the color law).
        "cube", "The Character Cube", palette.ROSE_PALETTE[6],
        ("cube_doctrine", "cube_axes", "cube_figures", "cube_projections",
         "double_trinity", "crosses", "one_soul"),
    ),
    Whole(
        # 09h green — spring's own centre, blue and yellow blended: life.
        "living", "The Living World", palette.ROSE_PALETTE[7],
        ("wolf", "bee", "elephant", "alchemy", "japan"),
    ),
)

# topic key -> the whole that seats it (derived; the reverse of the
# table above, and the ONE lookup the breadcrumb and the accent use).
THEME_TO_WHOLE = {
    theme: whole.key
    for whole in WHOLES
    for theme in whole.themes
}

WHOLE_BY_KEY = {whole.key: whole for whole in WHOLES}

# The six hues actually spent, in whole order — the Rose keeps eight;
# orange (15h) and rose (21h) stay unspent on purpose: they are the two
# SEASON-CENTRE blends, and a whole is not a season.
ROSE_ACCENTS_USED = tuple(whole.accent for whole in WHOLES)

# --- The variant law ---------------------------------------------------------
# MERGED topics: the new topic key -> (card title, ((switcher label, the
# SOURCE topic key whose pages it contributes), ...)).
# `app.encyclopedia.tree` builds each source block the way it always did
# and concatenates them, keeping the block boundaries as the variant
# ranges — a variant is a contiguous run of pages, never a re-ordering.
VARIANT_SOURCES = {
    "eclipses": ("Eclipses", (("Solar", "eclipse_solar"),
                              ("Lunar", "eclipse_lunar"))),
    "creeds": ("Creeds", (("Creeds", "religion"),
                          ("Ancient religions", "religion_alt"))),
    "bible": ("Bible", (("Bible", "bible"), ("Bible II", "bible2"),
                        ("Bible Dark", "bible_dark"))),
    # COMPLETION WAVE II (Session 32, 2026-07-29). The World of Warcraft
    # franchise is ONE card with a three-way switcher, never three cards
    # (WORKPLAN.md §THE THEME BACKLOG, structural answer 2): its three
    # casts hold the SAME nine seats — the same arm colours, the same
    # virtue/vice bundles, the same Sunday dual and the same Ninth
    # seat — and differ only in who is sitting there, which is precisely
    # what "registers of one subject" means. The dial shows one cast at
    # a time; the reader walks all three. TOPIC_ALIASES derives from
    # this, so each cast's own Spacebar jump still lands on its own
    # pages.
    "wow": ("World of Warcraft", (("Alliance", "wow_alliance"),
                                  ("Horde", "wow_horde"),
                                  ("Evil", "wow_evil"))),
}

# The four merged god themes already BUILD as three contiguous blocks
# (planetary 11 + pantheon 11 + the wider court's trailing run) — the
# old roster button walked them by arithmetic. They keep their build and
# only declare their labels here; the switcher is the same widget the
# merged topics above drive (Rule #5, one switcher).
GOD_VARIANT_LABELS = ("Planetary", "Pantheon", "Wider Court")

# THE CUBE SPLIT (owner-sealed 2026-07-28): the 42-page run became FOUR
# theme cards, cut on the boundaries `_CUBE_ENTRIES` already documents —
# the doctrine block, the thirteen axes with their poles and cells, the
# eight vertex figures, and the two projection readings. (key, title,
# start, stop) as a half-open slice of the ONE `_CUBE_ENTRIES` tuple.
CUBE_TOPICS = (
    ("cube_doctrine", "The Doctrine", 0, 6),
    ("cube_axes", "The Thirteen Axes", 6, 29),
    ("cube_figures", "The Eight Figures", 29, 40),
    ("cube_projections", "The Projections", 40, 42),
)

# Dial THEME key -> (topic key, variant index). Every Spacebar jump and
# every menu shortcut resolves through here, so a merged theme's own
# name still lands on its own pages: `bible_dark` opens the Bible card
# on its third variant, not a ghost topic. Identity entries are included
# on purpose — the resolver has ONE path, never a special case.
TOPIC_ALIASES = {
    source: (topic, index)
    for topic, (_title, variants) in VARIANT_SOURCES.items()
    for index, (_label, source) in enumerate(variants)
}
# The Planets/Signs/Art LOOK switcher is one theme wearing three art
# registers (RESTRUCTURE §Themes vs looks) — the dial's `planet_signs`
# slot still has to resolve a page, and it is the Planets card's own.
TOPIC_ALIASES["planet_signs"] = ("planets", 0)


# --- The coverage law --------------------------------------------------------
# OWNER LAW (Session 27, 2026-07-28): "svaki clanak mora sliku" — every
# article carries an image. `tests/test_encyclopedia_tree.py` enforces it
# on the SLOT, not the file: a page must NAME what it wants — a plate a
# prompt sheet can address, or a DRAWER the program runs — so the reader
# lights up the moment the art lands and no page is ever blank.
#
# The list of exceptions is EMPTY, and that is the point. Twenty-three
# pages were compositions the canon refused to generate art for (CUBE.md,
# Session 25, root Rule #19: an axis IS its two poles through the centre,
# a term grid is a table, a cipher is a word). The owner's verdict
# (2026-07-29) made them COMPUTED instead of blank: `render/diagrams.py`
# draws every one from the canon's own tables. Nothing is exempt now
# because nothing needs to be.
PLATELESS_PAGES: dict = {}


def cube_target(flat_index: int) -> tuple[str, int]:
    """(topic key, local page index) for a Spacebar jump that names the
    OLD flat cube index. `config/archetypes.py` aims the Cube wheels'
    jumps at positions inside the 42-page run (`enc=("cube", 35)`); the
    split moved those pages into four cards, and this is the ONE place
    that knows it — the wheel table stays untouched, which is also why
    the entry ORDER of `_CUBE_ENTRIES` remains a contract.

    An index past the end clamps to the last projection page rather than
    raising: the caller is the dial, and a stale wheel target must not
    take the window down.
    """
    for key, _title, start, stop in CUBE_TOPICS:
        if start <= flat_index < stop:
            return key, flat_index - start
    key, _title, start, stop = CUBE_TOPICS[-1]
    return key, stop - start - 1


def whole_of(topic: str) -> Whole:
    """The whole a topic card is seated in. Raises for an unknown topic
    so a typo fails loudly instead of drawing a card nobody can reach."""
    return WHOLE_BY_KEY[THEME_TO_WHOLE[topic]]


def accent_of(topic: str) -> str:
    """The topic's inherited accent hue — its whole's own."""
    return whole_of(topic).accent


def all_topics() -> tuple[str, ...]:
    """Every theme card, in reading order (whole by whole)."""
    return tuple(theme for whole in WHOLES for theme in whole.themes)
