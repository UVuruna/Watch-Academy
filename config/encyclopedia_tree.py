"""The Encyclopedia's THREE-LEVEL tree (owner Session 27, sealed
2026-07-28).

The rework replaced the old two-screen browser (one gallery of 39 tiles
in five halls -> article slider) with three levels:

1. **Home** — NINE wholes, 3x3, no scroll ever (the window's own minimum
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


# ═══════════════════════════ THE NINE WHOLES ═══════════════════════════
class Whole(NamedTuple):
    """One top-level card on the Home screen."""

    key: str
    title: str
    accent: str
    themes: tuple[str, ...]


# THE NINE WHOLES (owner-sealed 2026-07-29, Session 35 — "može i 9
# grupacija sa ovim novim velikim sekcijama"; the exact table is
# WORKPLAN-STRUCTURE.md §THE NINE WHOLES). The Session 27 six split
# further: `celestial` divides into the near sky (`sky` — sun, moon,
# seasons, eclipses) and the far sky (`cosmos` — planets, the cosmos
# theme, continents, astrology, the Chinese court); `divine` sheds its
# two WRITTEN faiths (Bible, Creeds) into the new `faith`, which also
# takes Trinity and Duality off `human`; `human` itself splits into
# `inner` (the four emblem families alone) and `worlds` (the trades, the
# Corporation and the three FRANCHISE cards the Theme Backlog arc
# registered — WoW, Cyberpunk, Star Wars, Sessions 31-33). `instrument`,
# `cube` and `living` are untouched, seat and membership both. No card
# lost an article, a variant or its dial wiring in the move — only its
# SEAT on Home changed (RESEAT, never re-wire).
#
# THE ACCENTS are the Rose's own hues (`palette.ROSE_PALETTE`, sealed —
# Rule #5, one palette) plus the Moon's own face (`palette.MOON_SILVER`
# — owner: "koristi ROSE paletu + neka boja Silver kao moon"): all eight
# Rose hues are now spent, and the ninth accent is the silver the Moon's
# own dial body wears. The accent rides the card's edge, the breadcrumb
# and the article header, so the reader always knows which whole he is
# inside.
WHOLES = (
    Whole(
        # 12h yellow — noon, the hour the whole watch is built around
        # (unchanged since Session 27). The Guide (owner 2026-07-28:
        # "jedno mesto za čitanje svega") is the fifth card — the paged
        # help book folded in from its own retired window, built from
        # the SAME `assets/.../guide/*.json` it always used (Rule #5,
        # no content copied).
        "instrument", "The Instrument", palette.ROSE_PALETTE[0],
        ("week", "instrument", "era", "months", "guide"),
    ),
    Whole(
        # The Moon's own silver — the near sky's face; eclipses ARE
        # sun-moon crossings, so they seat here rather than in the far
        # sky (owner: "Silver kao moon").
        "sky", "The Sky", palette.MOON_SILVER,
        ("sun", "moon", "seasons", "eclipses"),
    ),
    Whole(
        # 03h cyan — deep night, the hours the far sky is read against
        # (inherited from the old `celestial`).
        "cosmos", "The Cosmos", palette.ROSE_PALETTE[5],
        ("planets", "cosmos", "continents", "astrology", "chinese",
         "celestial_court"),
    ),
    Whole(
        # 24h moon-violet — midnight, the sacred hour (inherited from
        # `divine`).
        "gods", "The Gods", palette.ROSE_PALETTE[4],
        ("greek", "norse", "egypt", "slavic", "age_of_heroes"),
    ),
    Whole(
        # 21h rose — the vesper hour: Love's red thinned by moonlight
        # (the Rose canon's own reading), the one hue the six-whole
        # table left unspent until now.
        "faith", "The Faith", palette.ROSE_PALETTE[3],
        ("bible", "creeds", "trinity", "duality"),
    ),
    Whole(
        # 06h blue — the Cube's own axis blue (CUBE.md, the colour law;
        # unchanged since Session 27).
        "cube", "The Character Cube", palette.ROSE_PALETTE[6],
        ("cube_doctrine", "cube_axes", "cube_figures", "cube_projections",
         "double_trinity", "crosses", "one_soul"),
    ),
    Whole(
        # 18h red — sunset, the human fire, Lucifer's own hue on the
        # Scale (inherited from `human`).
        "inner", "The Inner Wheel", palette.ROSE_PALETTE[2],
        ("virtues", "sins", "moods", "intelligences"),
    ),
    Whole(
        # 09h green — spring's own centre, blue and yellow blended: life
        # (unchanged since Session 27).
        "living", "The Living World", palette.ROSE_PALETTE[7],
        ("wolf", "bee", "elephant", "alchemy", "japan"),
    ),
    Whole(
        # 15h orange — the working afternoon, the Merchant's copper: the
        # other hue the six-whole table left unspent. Worlds PEOPLE
        # build — trades and their offices, and the invented worlds of
        # games and film (the three franchise cards, moved here whole —
        # never renamed, never split).
        "worlds", "The Worlds", palette.ROSE_PALETTE[1],
        ("profession", "corporate", "wow", "cyberpunk", "starwars"),
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

# All nine hues spent, in whole order — the eight `ROSE_PALETTE` hues
# and the Moon's own `MOON_SILVER`, each used exactly once (Session 35
# — the six-whole table's two unspent hues, orange 15h and rose 21h,
# are now `worlds` and `faith`).
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
    # The SAME wave's second franchise, on the same argument. Gangs,
    # Street and Power are Night City read from three heights — the
    # factions that hold the ground, the people who live on it, and the
    # powers that move behind both — on one set of nine seats with the
    # same arm bundles, the same Sunday dual and the same Ninth seat.
    # Three keys on the dial, ONE card here; the labels are the sheet's
    # own block names.
    "cyberpunk": ("Cyberpunk 2077", (("Gangs", "cp_gangs"),
                                     ("Street", "cp_street"),
                                     ("Power", "cp_corpo"))),
    # COMPLETION WAVE III (Session 33, same day), the third franchise and
    # the last of the backlog. Jedi, Sith and Dyad are one saga read from
    # its two sides and then from the generation that inherits both — one
    # set of nine seats, the same arm bundles, the same Sunday dual and
    # the same Ninth seat. The merge is what makes the franchise's own
    # REPEATS legible: Anakin, Leia and Han each hold a seat in two of
    # the three blocks at different ages, and the switcher is where a
    # reader walks from one age of a person to the other. The labels are
    # the sheet's block names in English (its own Svetla | Tamna | Nova
    # stay in the sheet, root Rule #17).
    "starwars": ("Star Wars", (("Jedi", "sw_jedi"),
                               ("Sith", "sw_sith"),
                               ("Dyad", "sw_dyad"))),
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
# The Planets/Signs/Art LOOK switcher is one theme wearing three art
# registers (RESTRUCTURE §Themes vs looks) — the dial's `planet_signs`
# slot still has to resolve a page, and it is the Planets card's own. It
# has no variant row of its own, so it joins the derived rows here rather
# than patching the table after the fact (THE CONFIG SECTION LAW).
_LOOK_SWITCHER_ALIASES = {"planet_signs": ("planets", 0)}

TOPIC_ALIASES = {
    **{
        source: (topic, index)
        for topic, (_title, variants) in VARIANT_SOURCES.items()
        for index, (_label, source) in enumerate(variants)
    },
    **_LOOK_SWITCHER_ALIASES,
}


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


# ═══════════════════════════ ACCESSOR FUNCTIONS ═══════════════════════════
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
