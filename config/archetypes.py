"""The ARCHETYPE MODE configuration (owner-sealed package 2026-07-16).

One home for the whole archetype system (CANON.md §Pointer
Archetypes): the (pointer, palette_style) → archetype grid, the
per-archetype figure tables (arm angle, stained-glass file, the
two-row names, article entity, encyclopedia target), the center
table, the article-set names Session 6 fills, and the render
tunables. Documentation: config/archetypes.md.
"""

from config import paths

# Canonical (source-less) art root — config.paths.art_file inserts the
# active source (assets/archetype/<source>/...) at every disk boundary.
ARCHETYPE_ART_DIR = paths.assets_dir() / "archetype"
# The two REUSED Prism seats inherit the owner's Scale glass as it
# exists on disk (owner assets are authoritative).
_SCALE_GLASS_DIR = paths.assets_dir() / "badge" / "scale"

# The grid (CANON, owner 2026-07-16): paint carries the WORLD's order,
# light the HOME's. The Seasons serve ONE archetype under both wheels
# (one palette, one set of four windows, the Throne on both); Aurora
# and the Calendar have NO archetype at all.
ARCHETYPE_GRID = {
    ("trio", "paint"): "trinity_paint",
    ("trio", "light"): "trinity_light",
    # The Seasons carry TWO archetypes now (owner 2026-07-17, CANON
    # §Seasons light): PAINT = the Four Temperaments on the seasons
    # palette; LIGHT = the Tetramorph on the Four Elements wheel. Both
    # keep the Throne at the center.
    ("cross", "paint"): "seasons_paint",
    ("cross", "light"): "seasons_light",
    ("hexa", "paint"): "prism_paint",
    ("hexa", "light"): "prism_light",
    ("octa", "paint"): "compass_paint",
    ("octa", "light"): "compass_light",
}

# The Eight Ages ship TWO image registers (owner "oba", CANON §Compass
# light): Register I the Tree (one oak, eight states — the ★-marked
# default) and Register II the Menagerie (eight creatures). This picks
# the rendered one until the owner wires a user-facing choice.
ARCHETYPE_LIFE_REGISTER = "tree"
ARCHETYPE_LIFE_REGISTERS = ("tree", "animals")

# --- Render tunables -----------------------------------------------------------
# Figure height as a fraction of the star TIP radius, per pointer —
# the lancet scales INTO the diamond with the arm color visible around
# it (the slim-armed cross/octa carry smaller glass). Owner tunes when
# the real art lands.
ARCHETYPE_FIGURE_HEIGHT_OF_TIP = {
    "trio": 0.62, "hexa": 0.58, "cross": 0.46, "octa": 0.40,
}
# The figure NAME label (the lit figure with Names on, and the
# fallback while art is missing/placeholder): fitted to this fraction
# of the diamond's widest width, capped against the figure height.
ARCHETYPE_NAME_WIDTH_FRACTION = 0.92
ARCHETYPE_NAME_MAX_OF_FIGURE = 0.24
# A file at or under this many pixels per side is a committed 1×1
# placeholder (the WORKPLAN missing-art rule) — the renderer draws the
# figure's NAME instead of a stretched pixel.
ARCHETYPE_ART_MIN_PX = 8
# THE CENTER WINDOW (owner seal 2026-07-18): the archetype CENTER
# figure (ArchetypeCenterLayer — the Eye / Hearth / Seal / Union /
# Throne) burns FULL only while the hour hand stands within this many
# degrees of TRUE solar noon OR TRUE solar midnight (±1h == 15°, so
# BOTH windows together cover 4 of the 24 hours, ~16.7% of the day) —
# the rest of the time it draws at the weekday ghost_opacity, exactly
# like an un-lit arm figure. The reveal gesture still forces it full.
ARCHETYPE_CENTER_WINDOW_DEG = 15.0
# The Earth Weekday option (settings.earth_weekday — a GENERAL Earth
# marker option since 2026-07-17, no longer archetype-only): the date
# shifts up and the abbreviated weekday writes below it, both as
# fractions of the marker size. The geometry lives here beside the other
# Earth-marker archetype tunables.
ARCHETYPE_EARTH_DAY_OFFSET = 0.16
ARCHETYPE_EARTH_DAY_TEXT_SIZE = 0.26

# The one-line stand-in the hover speaks while an archetype's article
# set has not been written yet (Session 6 delivers the texts) — shown
# under the figure's name, never a KeyError.
ARCHETYPE_PENDING_LINE = (
    "The Canon has already named this seat; its article is still "
    "being written."
)


def _fig(angle, file, name, row2, entity, enc=None):
    """One figure row: unrotated arm angle (dial degrees from the
    top), canonical art path, the TWO-ROW names (row 1 the figure,
    row 2 its calling/role/quality/shadow/object/being), the article
    entity key, and the encyclopedia (topic, entry) or None."""
    return {
        "angle": angle, "file": file, "name": name, "row2": row2,
        "entity": entity, "enc": enc,
    }


_TRINITY_DIR = ARCHETYPE_ART_DIR / "trinity"
_FAMILY_DIR = ARCHETYPE_ART_DIR / "family"
_TEMPERAMENTS_DIR = ARCHETYPE_ART_DIR / "temperaments"
_TETRAMORPH_DIR = ARCHETYPE_ART_DIR / "tetramorph"
_PERSONS_DIR = ARCHETYPE_ART_DIR / "persons"
_ONE_SOUL_DIR = ARCHETYPE_ART_DIR / "one_soul"
_WALKS_DIR = ARCHETYPE_ART_DIR / "walks"
_LIFE_DIR = ARCHETYPE_ART_DIR / "life"

# The Eight Ages, shared by both registers: (angle, age name, row-2
# being per register, entity, file stem) — ordered by arm position so
# the tuple index IS the hour-space index (0 = the top arm).
_LIFE_AGES = (
    (0.0, "Youth", {"tree": "The Blossoming Crown", "animals": "The Lion"},
     "youth", "Youth"),
    (45.0, "Maturity", {"tree": "The Full Crown", "animals": "The Ox"},
     "maturity", "Maturity"),
    (90.0, "The Elder", {"tree": "The Fruited Crown",
                         "animals": "The Elephant"}, "elder", "Elder"),
    (135.0, "Old Age", {"tree": "The Leaf-fall", "animals": "The Owl"},
     "old_age", "OldAge"),
    (180.0, "Death", {"tree": "The Bare Tree", "animals": "The Swan"},
     "death", "Death"),
    (225.0, "The Unborn", {"tree": "The Seed", "animals": "The Phoenix"},
     "unborn", "Unborn"),
    (270.0, "Birth", {"tree": "The Sprout", "animals": "The Chick"},
     "birth", "Birth"),
    (315.0, "Childhood", {"tree": "The Sapling", "animals": "The Swallow"},
     "childhood", "Childhood"),
)


def _life_figures(register: str) -> tuple:
    return tuple(
        _fig(angle, _LIFE_DIR / register / f"{stem}.png", name,
             beings[register], entity)
        for angle, name, beings, entity, stem in _LIFE_AGES
    )


# Per archetype: the article SET (Session 6 writes {"rows": [...]}
# nodes into Database/symbolism.json → articles.<set>, entity keys
# below + "center"), the ordered FIGURES (index = hour-space index)
# and the CENTER (or None — the Compass rose is the wheel itself).
ARCHETYPES = {
    # Trinity paint — the heavenly courtroom (CANON §Trinity).
    "trinity_paint": {
        "articles": "archetype_trinity_paint",
        "figures": (
            _fig(0.0, _TRINITY_DIR / "One_Judge.png",
                 "The One", "Judge", "one"),
            _fig(120.0, _TRINITY_DIR / "Devil_Prosecutor.png",
                 "The Devil", "Prosecutor", "devil"),
            _fig(240.0, _TRINITY_DIR / "Jesus_Advocate.png",
                 "Jesus", "Advocate", "jesus"),
        ),
        "center": {
            "file": _TRINITY_DIR / "Providence_Eye.png",
            "name": "The Eye of Providence", "entity": "center",
        },
    },
    # Trinity light — the Family triangle (CANON §Trinity light).
    "trinity_light": {
        "articles": "archetype_trinity_light",
        "figures": (
            _fig(0.0, _FAMILY_DIR / "Child_Dawn.png",
                 "The Child", "The Dawn", "child"),
            _fig(120.0, _FAMILY_DIR / "Mother_Heart.png",
                 "The Mother", "The Heart", "mother"),
            _fig(240.0, _FAMILY_DIR / "Father_Shield.png",
                 "The Father", "The Shield", "father"),
        ),
        "center": {
            "file": _FAMILY_DIR / "Hearth.png",
            "name": "The Hearth", "entity": "center",
        },
    },
    # Seasons PAINT — the Four Temperaments (CANON §Seasons). COLOR-fixed:
    # the humors sit on the palette hues (Choleric = summer yellow top),
    # so the southern hemisphere does NOT flip them — the palette itself
    # never flips either. Row 2 = the age of man. (Renamed from "seasons"
    # 2026-07-17 when the Seasons gained a second, LIGHT archetype — the
    # article set has no texts yet, so the rename is consistent
    # everywhere: symbolism.json carries no archetype nodes until
    # Session 6, and archetype_article() answers None gracefully.)
    "seasons_paint": {
        "articles": "archetype_seasons_paint",
        "figures": (
            _fig(0.0, _TEMPERAMENTS_DIR / "Choleric.png",
                 "Choleric", "The Prime", "choleric"),
            _fig(90.0, _TEMPERAMENTS_DIR / "Melancholic.png",
                 "Melancholic", "Middle Age", "melancholic"),
            _fig(180.0, _TEMPERAMENTS_DIR / "Phlegmatic.png",
                 "Phlegmatic", "Old Age", "phlegmatic"),
            _fig(270.0, _TEMPERAMENTS_DIR / "Sanguine.png",
                 "Sanguine", "Childhood & Youth", "sanguine"),
        ),
        "center": {
            "file": _TEMPERAMENTS_DIR / "Throne.png",
            "name": "The Throne", "entity": "center",
        },
    },
    # Seasons LIGHT — the TETRAMORPH (owner 2026-07-17, CANON §Seasons
    # light): the four living creatures of Ezekiel 1 / Revelation 4 on
    # the Four Elements wheel, each on its canonical FIXED-CROSS season
    # arm. Row 2 = the Evangelist the creature became (Mark/Luke/John/
    # Matthew). The EIGHTH archetype, the only non-human one — the
    # creatures WITNESS, circling the Throne (kept as the center). Ordered
    # by arm angle (0/90/180/270 = summer/autumn/winter/spring), matching
    # the _CROSS_ELEMENTS hues (fire/earth/water/air).
    "seasons_light": {
        "articles": "archetype_seasons_light",
        "figures": (
            _fig(0.0, _TETRAMORPH_DIR / "Lion.png",
                 "The Lion", "Mark", "lion"),
            _fig(90.0, _TETRAMORPH_DIR / "Ox.png",
                 "The Ox", "Luke", "ox"),
            _fig(180.0, _TETRAMORPH_DIR / "Eagle.png",
                 "The Eagle", "John", "eagle"),
            _fig(270.0, _TETRAMORPH_DIR / "Man.png",
                 "The Man", "Matthew", "man"),
        ),
        "center": {
            "file": _TEMPERAMENTS_DIR / "Throne.png",
            "name": "The Throne", "entity": "center",
        },
    },
    # Prism paint — the Persons (CANON §Prism light—the Persons).
    # Lucifer and Judas REUSE their Scale glass (canon: no new art
    # for those two seats).
    "prism_paint": {
        "articles": "archetype_prism_paint",
        "figures": (
            _fig(0.0, _PERSONS_DIR / "One_Love.png",
                 "The One", "Love", "one"),
            _fig(60.0, _PERSONS_DIR / "Michael_Courage.png",
                 "Michael", "Courage", "michael"),
            _fig(120.0, _SCALE_GLASS_DIR / "Lucifer_Triangle.png",
                 "Lucifer", "Pride", "lucifer"),
            _fig(180.0, _PERSONS_DIR / "Devil_Hatred.png",
                 "The Devil", "Hatred", "devil"),
            _fig(240.0, _SCALE_GLASS_DIR / "Judas_Triangle.png",
                 "Judas", "Weakness (Fear)", "judas"),
            _fig(300.0, _PERSONS_DIR / "Jesus_Humility.png",
                 "Jesus", "Humility", "jesus"),
        ),
        # The Seal — the banknote hexagram (owner seal 2026-07-16;
        # the rosette whose overlap is clear glass).
        "center": {
            "file": _PERSONS_DIR / "Seal.png",
            "name": "The Seal", "entity": "center",
        },
    },
    # Prism light — One Soul, the Bond (CANON): pillar + its SHADOW.
    "prism_light": {
        "articles": "archetype_prism_light",
        "figures": (
            _fig(0.0, _ONE_SOUL_DIR / "Gratitude.png",
                 "Gratitude", "Taking for Granted", "gratitude"),
            _fig(60.0, _ONE_SOUL_DIR / "Support.png",
                 "Support", "The Fight", "support"),
            _fig(120.0, _ONE_SOUL_DIR / "Passion.png",
                 "Passion", "Jealousy", "passion"),
            _fig(180.0, _ONE_SOUL_DIR / "Tolerance.png",
                 "Tolerance", "Score-keeping", "tolerance"),
            _fig(240.0, _ONE_SOUL_DIR / "Trust.png",
                 "Trust", "Suspicion", "trust"),
            _fig(300.0, _ONE_SOUL_DIR / "Respect.png",
                 "Respect", "Contempt", "respect"),
        ),
        "center": {
            "file": _ONE_SOUL_DIR / "Union.png",
            "name": "The Union", "entity": "center",
        },
    },
    # Compass paint — the Eight Walks of Life (CANON): estate + its
    # OBJECT. Six estates already have Professions pages — the only
    # archetype→encyclopedia mapping that exists today (the Scholar
    # and the Wanderer wait for their own topics).
    "compass_paint": {
        "articles": "archetype_compass_paint",
        "figures": (
            _fig(0.0, _WALKS_DIR / "King.png", "The King", "The Crown",
                 "king", enc=("profession", 0)),
            _fig(45.0, _WALKS_DIR / "Merchant.png", "The Merchant",
                 "The Coin", "merchant", enc=("profession", 3)),
            _fig(90.0, _WALKS_DIR / "Soldier.png", "The Soldier",
                 "The Sword", "soldier", enc=("profession", 2)),
            _fig(135.0, _WALKS_DIR / "Artist.png", "The Artist",
                 "The Mask", "artist", enc=("profession", 5)),
            _fig(180.0, _WALKS_DIR / "Wanderer.png", "The Wanderer",
                 "The Staff", "wanderer"),
            _fig(225.0, _WALKS_DIR / "Scholar.png", "The Scholar",
                 "The Book", "scholar"),
            _fig(270.0, _WALKS_DIR / "Farmer.png", "The Farmer",
                 "The Plough", "farmer", enc=("profession", 6)),
            _fig(315.0, _WALKS_DIR / "Priest.png", "The Priest",
                 "The Bell", "priest", enc=("profession", 4)),
        ),
        "center": None,          # the rose is the wheel itself (owner)
    },
    # Compass light — the Eight Ages (CANON): age + its LIVING BEING;
    # the figures resolve per ARCHETYPE_LIFE_REGISTER in figures().
    "compass_light": {
        "articles": "archetype_compass_light",
        "registers": {
            register: _life_figures(register)
            for register in ARCHETYPE_LIFE_REGISTERS
        },
        "center": None,
    },
}


# The four elements the TETRAMORPH creatures ride (owner 2026-07-17,
# CANON §Seasons light). Index = the arm/hour-space index, in the SAME
# order as the seasons_light figures and the _CROSS_ELEMENTS hues: fire
# (summer/Lion), earth (autumn/Ox), water (winter/Eagle), air
# (spring/Man). The THIRD column of the tetramorph three-side hover.
TETRAMORPH_ELEMENTS = ("Fire", "Earth", "Water", "Air")


def tetramorph_element(index: int) -> str:
    """The element name for one Tetramorph arm (Rule #5: one ordering
    shared with the figures and the Four-Elements wheel hues)."""
    return TETRAMORPH_ELEMENTS[index]


def grid_key(pointer: str, palette_style: str) -> str | None:
    """The archetype of one (pointer, wheel) grid seat — None on the
    archetype-less instruments (Aurora, Calendar)."""
    return ARCHETYPE_GRID.get((pointer, palette_style))


def has_archetype(pointer: str) -> bool:
    """Whether ANY wheel of this pointer carries an archetype — the
    menu gates the Archetype toggle on it."""
    return any(seat_pointer == pointer for seat_pointer, _ in ARCHETYPE_GRID)


def figures(key: str) -> tuple:
    """The ordered figure tuple of one archetype (index = hour-space
    index); the Ages resolve the active image register here."""
    spec = ARCHETYPES[key]
    if "registers" in spec:
        return spec["registers"][ARCHETYPE_LIFE_REGISTER]
    return spec["figures"]


def center(key: str) -> dict | None:
    """The archetype's center figure — the Eye / the Hearth / the
    Seal / the Union / the Throne — or None (the Compass)."""
    return ARCHETYPES[key]["center"]
