"""WORKPLAN Session 21 — the Cube Encyclopedia wave (2026-07-27).

Pins what the owner sealed in this session, so nothing here can be
undone by accident:

1. THE CUBE SECTION — the `cube` / `double_trinity` / `crosses`
   families of `Database/encyclopedia.json` exist, are complete, and
   every page obeys the ARTICLE CHARTER's four movements (thesis →
   argument → correspondences → quote, CUBE.md).
2. THE ARCHETYPES HALL — the three topics are gallery cards, in the
   contractual order the Cube wheels' Spacebar targets address by
   INDEX.
3. THE THREE WHEELS' ARTICLE SETS — Genesis, Council and Character
   speak their own prose (the coverage law in `test_archetype.py`
   proves the totals; here we pin the seats' own content).
4. THE SEALED COMBO FIGURES — the six slots the owner delegated to
   this session ("ti pečatiš") are named in the Character wheel's
   articles.
5. THE THEME NAME — "One Soul / The Vow / The Bond" keeps all three
   names: the triple where a title is written in full, "One Soul"
   alone wherever one name must stand.
6. THE CHARTER REWORK — the twenty-one reworked articles no longer
   describe their own picture or talk about the art asset.
"""

import json
import re

import pytest

from config import archetypes, constants, paths
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository
from data.translations import collect_corpus

_CHARTER_HEADS = ("[[Thesis]]", "[[Argument]]",
                  "[[Correspondences]]", "[[Quote]]")
_CUBE_FAMILIES = ("cube", "double_trinity", "crosses")


def _encyclopedia() -> dict:
    return json.loads(
        (paths.database_dir() / "encyclopedia.json").read_text(
            encoding="utf-8"
        )
    )


def test_the_cube_families_are_complete():
    """The Cube section, the Double Trinity and the Two Crosses: 42 + 5
    + 14 pages, with the canon's own required subjects present by
    name. (Session 25 grew the Cube section from 20 to 42 — the
    Thirteen-Axes wave.)"""
    data = _encyclopedia()
    cube, dt, crosses = (data[f] for f in _CUBE_FAMILIES)
    assert (len(cube), len(dt), len(crosses)) == (42, 5, 14)
    # The three axes, the six poles, the eight vertices, the sets, the
    # coordinate doctrine's own page and the Banknote seal.
    for name in ("The Cube", "The Activation Axis", "The Moral Scope Axis",
                 "The Self-Regard Axis", "The Three Sets",
                 "The Banknote Axes"):
        assert name in cube, name
    # The Y axis is Moral Scope since the owner's approval of
    # 2026-07-28; the old short name is gone from the whole corpus.
    assert "The Judgment Axis" not in cube
    for pole in ("Composure", "Vigor", "Loyalty", "Integrity",
                 "Humility", "Dignity"):
        assert pole in cube, pole
    for vertex in ("The Quiet Devotee", "The Steady Guardian",
                   "The Contemplative Sage", "The Wise Statesman",
                   "The Sacrificial Protector", "The Charismatic Champion",
                   "The Principled Reformer", "The Visionary Founder"):
        assert vertex in cube, vertex
    # The Double Trinity's three triangles plus the 24-field table.
    for page in ("The Double Trinity", "The Court", "Genesis",
                 "The Council", "The Twenty-Four Fields"):
        assert page in dt, page
    # The two crosses: both paths, all eight stations, the centres and
    # both cipher pages.
    for page in ("The Two Crosses", "The Path of Light",
                 "The Path of Darkness", "Hope", "Faith", "Love",
                 "Salvation", "Fear", "Anger", "Hate", "Suffering",
                 "Trust and Distrust", "FALL and STAR", "DOMY and SAFE"):
        assert page in crosses, page


def test_the_thirteen_axes_each_have_their_page():
    """WORKPLAN Session 25: every axis `config.cube.AXES` declares owns
    an Encyclopedia page, under the canon's own name — the three
    primaries in the section's older "The X Axis" style, the ten others
    verbatim. The mapping is derived from the canon table, so a renamed
    axis fails here rather than drifting silently."""
    from config import cube as cube_canon

    pages = _encyclopedia()["cube"]
    for axis in cube_canon.AXES:
        name = axis.name
        if name in ("Activation", "Moral Scope", "Self-Regard"):
            name = f"The {name} Axis"
        assert name in pages, name
    assert "The Thirteen Axes" in pages          # the arithmetic itself
    assert "The One" in pages                    # the centre
    assert "The Sixty-Five Terms" in pages       # the economy law
    assert "The Hexagram Projection" in pages    # the two X-rays


def test_the_one_carries_both_descriptions():
    """Owner decree: the centre is described BOTH ways, and the empty
    exemplar column is doctrine rather than a vacancy."""
    base = EncyclopediaRepository().entry("cube", "The One")["base"]
    for fall in ("Lethargy", "Frenzy", "Tribalism", "Legalism",
                 "Self-Annihilation", "Self-Worship"):
        assert fall in base, fall                       # the apophatic six
    for power in ("Composure", "Vigor", "Loyalty", "Integrity",
                  "Humility", "Dignity"):
        assert power in base, power                     # the cataphatic six
    assert "takes no exemplar in any register" in base
    assert "(0,0,0)" in base


def test_the_sacred_axis_page_carries_the_five_stations():
    """The five stations, the three readings, the alias and the ONE
    distinguishing sentence the Charter requires (CUBE.md §The Sacred
    Axis)."""
    base = EncyclopediaRepository().entry("cube", "The Sacred Axis")["base"]
    for station in ("Paralyzed Purist", "Jesus", "The One",
                    "Charismatic Champion", "Devil"):
        assert station in base, station
    for reading in ("Advocate", "Judge", "Prosecutor",
                    "Preserver", "Creator", "Destroyer"):
        assert reading in base, reading
    assert "AXIS MUNDI" in base
    assert "NOT the doctrinal Holy Trinity" in base
    for echo in ("Maximilian Kolbe", "Nero", "Aslan", "Sauron"):
        assert echo in base, echo


def test_the_sixteen_new_edge_readings_are_written():
    """Session 25's own deliverable: the eight new edge cells each have
    a page, and BOTH readings of each — sixteen in all — are argued on
    it, with all six of the seat's figures named."""
    from config import cube as cube_canon

    repo = EncyclopediaRepository()
    new_edges = {
        (-1, -1, 0), (1, 1, 0), (-1, 1, 0), (1, -1, 0),
        (-1, 0, -1), (1, 0, 1), (-1, 0, 1), (1, 0, -1),
    }
    for axis in cube_canon.AXES:
        for cell in (axis.cold, axis.warm):
            if cell.coords not in new_edges:
                continue
            base = repo.entry("cube", cell.luminous)["base"]
            assert cell.fallen in base, (cell.luminous, cell.fallen)
            for register in cube_canon.FIGURE_SETS:
                for figure in cube_canon.roster(cell.coords, register):
                    assert figure in base, (cell.luminous, figure)


def test_the_hexagram_projection_carries_the_blindness_law():
    """Both X-rays and the count the law turns on (19 visible, 7
    hidden, 26 cells)."""
    base = EncyclopediaRepository().entry(
        "cube", "The Hexagram Projection"
    )["base"]
    assert "Sacred Axis" in base and "Genesis" in base
    assert "seven cells are hidden" in base
    assert "twenty-six" in base


def test_every_cube_page_obeys_the_article_charter():
    """CUBE.md's Article Charter: every page argues in four movements —
    thesis, argument, correspondences, quote — in that order, and no
    page is a stub."""
    data = _encyclopedia()
    for family in _CUBE_FAMILIES:
        for name, node in data[family].items():
            base = node["base"]
            positions = []
            for head in _CHARTER_HEADS:
                assert head in base, f"{family}/{name} misses {head}"
                positions.append(base.index(head))
            assert positions == sorted(positions), f"{family}/{name} order"
            assert len(base) > 600, f"{family}/{name} is a stub"


def test_the_twenty_four_fields_name_all_twelve_office_process_pairs():
    """The Double Trinity's full machinery: twelve offices, twelve
    processes, four of each per person."""
    base = EncyclopediaRepository().entry(
        "double_trinity", "The Twenty-Four Fields"
    )["base"]
    for office in ("Judge", "Avenger", "Destroyer", "Tempter",
                   "Prosecutor", "Catalyst", "Creator", "Redeemer",
                   "Advocate", "Shepherd", "Preserver", "Lawgiver"):
        assert office in base, office
    for process in ("Justice", "Retribution", "Punishment", "Ruin",
                    "Guilt", "Critique", "Reinvention", "Renewal",
                    "Salvation", "Mercy", "Stewardship", "Reform"):
        assert process in base, process


def test_the_crosses_carry_the_rows_the_ciphers_and_the_chiasm():
    """The Latin and Greek rows, the FALL/STAR mnemonics, the DOMY and
    SAFE ciphers and the chiasm all have a written home (CUBE.md §The
    Two Crosses — the legend MUST explain the mnemonics)."""
    repo = EncyclopediaRepository()
    overview = repo.entry("crosses", "The Two Crosses")["base"]
    for word in ("TIMOR", "IRA", "ODIUM", "DOLOR",
                 "SPES", "FIDES", "CARITAS", "SALUS",
                 "PHOBOS", "ORGE", "MISOS", "PATHOS",
                 "ELPIS", "PISTIS", "AGAPE", "SOTERIA"):
        assert word in overview, word
    assert "CHIASM" in overview.upper()
    mnemonics = repo.entry("crosses", "FALL and STAR")["base"]
    assert "FALL" in mnemonics and "STAR" in mnemonics
    for term in ("Loathing", "Lament", "Spark", "Redemption"):
        assert term in mnemonics, term
    ciphers = repo.entry("crosses", "DOMY and SAFE")["base"]
    for term in ("DOLOR", "ODIUM", "METUS", "HYBRIS",
                 "SALUS", "AGAPE", "FIDES", "ELPIS",
                 "littera Pythagorica"):
        assert term in ciphers, term
    centres = repo.entry("crosses", "Trust and Distrust")["base"]
    assert "Without trust, even love decays into fear" in centres


def test_the_archetypes_hall_addresses_its_pages_by_index():
    """THE SPACEBAR CONTRACT: every Cube wheel figure's `enc` target
    (topic key, entry index) lands on the page it argues — the
    Character arms on their own pole or vertex, the Genesis and Council
    arms on their triangle."""
    from app.encyclopedia import _topics

    topics = _topics()
    for key in ("cube", "double_trinity", "crosses"):
        assert key in topics
    names = {
        key: [entry["name"] for entry in topics[key]["entries"]]
        for key in ("cube", "double_trinity", "crosses")
    }
    expect = {
        "trinity_genesis": {"god": ("double_trinity", "Genesis"),
                            "jesus": ("double_trinity", "Genesis"),
                            "devil": ("double_trinity", "Genesis")},
        "prism_council": {
            entity: ("double_trinity", "The Council")
            for entity in ("god_judge", "devil_destroyer",
                           "devil_prosecutor", "god_creator",
                           "jesus_advocate", "jesus_preserver")
        },
        "compass_character": {
            "loyalty": ("cube", "Loyalty"),
            "patronage": ("cube", "The Steady Guardian"),
            "dignity": ("cube", "Dignity"),
            "conviction": ("cube", "The Wise Statesman"),
            "integrity": ("cube", "Integrity"),
            "renunciation": ("cube", "The Contemplative Sage"),
            "humility": ("cube", "Humility"),
            "devotion": ("cube", "The Quiet Devotee"),
        },
    }
    for wheel, per_entity in expect.items():
        for figure in archetypes.figures(wheel):
            topic, index = figure["enc"]
            wanted_topic, wanted_page = per_entity[figure["entity"]]
            assert topic == wanted_topic, figure["entity"]
            assert names[topic][index] == wanted_page, figure["entity"]


@pytest.mark.parametrize("set_name,entity,needle", (
    # Genesis: the inverted trio and its centre.
    ("archetype_trinity_genesis", "god", "Creator"),
    ("archetype_trinity_genesis", "jesus", "Preserver"),
    ("archetype_trinity_genesis", "devil", "Destroyer"),
    ("archetype_trinity_genesis", "center", "Genesis 1:3"),
    # Council: six offices in session, the Lord's Day at the centre.
    ("archetype_prism_council", "god_judge", "Psalm 82:1"),
    ("archetype_prism_council", "devil_prosecutor", "Revelation 12:10"),
    ("archetype_prism_council", "jesus_advocate", "1 John 2:1"),
    ("archetype_prism_council", "center", "Genesis 2:2"),
))
def test_the_cube_wheels_speak_their_own_prose(set_name, entity, needle):
    """No Cube wheel falls back to ARCHETYPE_PENDING_LINE any more."""
    node = SymbolismRepository().archetype_article(set_name, entity)
    joined = " ".join(node["rows"])
    assert needle in joined
    assert archetypes.ARCHETYPE_PENDING_LINE not in joined


@pytest.mark.parametrize("entity,figure", (
    ("devotion", "Alfred Pennyworth"),      # Devotion, modern +
    ("devotion", "Severus Snape"),          # Martyrdom, modern −
    ("patronage", "Charles Xavier"),        # Patronage, modern +
    ("conviction", "Steve Rogers"),         # Conviction, modern +
    ("renunciation", "Father Ferapont"),    # Mortification, archetypal −
    ("renunciation", "Silas"),              # Mortification, modern −
))
def test_the_sealed_combo_figures_are_written(entity, figure):
    """The six OPEN Character combos the owner delegated to this
    session (CUBE.md §The Character Wheel, SEALED 2026-07-27) each have
    a seat AND an argument in the wheel's own articles."""
    node = SymbolismRepository().archetype_article(
        "archetype_compass_character", entity
    )
    assert figure in " ".join(node["rows"])


def test_the_prism_light_theme_keeps_all_three_names():
    """Owner seal 2026-07-27: the theme is titled with the triple and
    labelled with the single name — one declaration, both readers."""
    assert constants.PRISM_LIGHT_THEME_NAME == "One Soul"
    assert constants.PRISM_LIGHT_THEME_TITLE == "One Soul — The Vow — The Bond"
    assert constants.PRISM_LIGHT_THEME_NAME in constants.PRISM_LIGHT_THEME_TITLE
    # The hexa wheel row — the Design window's palette-style labels and
    # the watch TITLE row read this one table (Rule #5). The PAINT slot
    # says Persons since the owner's "ok." of 2026-07-27 (CANON.md names
    # the prism paint wheel The Persons); the generic "Paint palette"
    # default survives only under the "default" key.
    labels = constants.POINTER_PALETTE_LABELS["hexa"]
    assert labels[1] == constants.PRISM_LIGHT_THEME_NAME
    assert labels == ("Persons", "One Soul", "Council")
    assert constants.POINTER_PALETTE_LABELS["default"][0] == "Paint palette"


def test_the_reworked_articles_no_longer_describe_their_picture():
    """CHARTER RULE 4 (owner 2026-07-26): an article never narrates the
    frame, the pose or the glass, and never talks about the art asset.
    The twenty-one articles Session 21 reworked are pinned clean; the
    phrases below are the exact ones that were removed.

    SESSION 22 WIDENED THIS (2026-07-27). Session 21 read rule 4 as "do
    not mention the art asset" and left the STAGING of the figure intact
    — the owner then found "On the blue pre-dawn arm of Calm stands
    Jesus…" and "At the apex, in spring green, stands The Child…" alive
    on the live pages. The staging phrases are pinned here beside the
    Session 21 ones, and the scan now covers EVERY archetype row rather
    than only the sets that session touched. The corpus-wide lint that
    keeps the rest of both databases honest lives in
    `tests/test_article_charter.py`.
    """
    repo = SymbolismRepository()
    banned = re.compile(
        # Session 21 — the art asset named.
        r"rondel keeps|Scale window|no new glass is cut|reused here"
        r"|in open hands|its iris is|center of the reveal"
        r"|overlapping heart|with the plough in hand"
        r"|the student at the lamp|owning nothing but the road"
        # Session 22 — the figure staged (the owner's own two proofs
        # first, then the rest of the archetype wheels' inversions).
        r"|stands Jesus|stands The Child|in spring green, stands"
        r"|stands The One|stands The Mother|stands The Father"
        r"|stands Michael|stands the Lion|stands the Ox"
        r"|stands the Eagle|stands the Man|stands the King"
        r"|stands the Throne|sits The Devil|glows the Hearth"
        r"|At the top of the trio|God stands at midnight",
        re.IGNORECASE,
    )
    data = repo._load()["articles"]
    offenders = []
    for set_name, entities in data.items():
        if not set_name.startswith("archetype_"):
            continue
        for entity, node in entities.items():
            for index, row in enumerate(node["rows"]):
                if banned.search(row):
                    offenders.append(f"{set_name}.{entity}[{index}]")
    assert offenders == []


def test_the_cube_families_ride_the_translation_corpus():
    """Every new page is translatable — the Session 15 wave must not
    have to hunt for them."""
    corpus = collect_corpus()
    for family in _CUBE_FAMILIES:
        for name in _encyclopedia()[family]:
            assert f"encyclopedia/{family}/{name}/base" in corpus
