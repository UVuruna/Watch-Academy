"""THE SESSION 27 LAWS (owner-sealed 2026-07-28) — pinned.

Four things the rework promised the owner, each of which has to survive
every future change:

1. **The tree IS the Encyclopedia.** Six wholes, every theme seated in
   exactly one, and the built table matching the declaration exactly —
   no orphan card nobody can reach, no declared card that does not
   exist.
2. **No horizontal scroll, ever** — at the minimum window size and at
   maximum zoom, on all three levels. This one has regressed twice
   before (rounds R3 and R8b), which is why it is pinned by geometry
   AND by a live dialog.
3. **The home screen never scrolls** — it owns no scroll area at all,
   and its 3x2 grid is measured from the viewport.
4. **The variant switcher keeps the reader's place** — Monday stays
   Monday across a register change, and a shorter register clamps to
   its own last page instead of overrunning.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QScrollArea

from app.encyclopedia import EncyclopediaDialog, topics as build_topics
from app.encyclopedia.cards import card_width_for, row_content_width
from app.encyclopedia.tree import resolve_target, switch_variant, variant_at
from config import defaults
from config import encyclopedia_tree as tree


@pytest.fixture(scope="module")
def topics():
    return build_topics()


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


# --- 1. THE TREE ------------------------------------------------------------

def test_six_wholes_each_carrying_cards():
    """The owner's home screen is 2x3 — six wholes, none of them empty
    (the old "The Archetypes" hall stood empty for weeks; a whole with
    no cards is a dead tile on the FIRST screen the reader meets)."""
    assert len(tree.WHOLES) == 6
    for whole in tree.WHOLES:
        assert whole.themes, whole.key


def test_every_theme_is_seated_exactly_once():
    seats = [theme for whole in tree.WHOLES for theme in whole.themes]
    assert len(seats) == len(set(seats))


def test_the_built_table_matches_the_declared_tree_exactly(topics):
    """No ghost card, no unreachable topic. `planet_signs` is the case
    this catches: it is a LOOK of the Planets card, not a theme, and it
    used to sit in the table as a topic no gallery could open."""
    assert set(topics) == set(tree.all_topics())


def test_every_whole_wears_a_rose_hue():
    """The accents are the Rose's own (Rule #5, one palette) — never a
    hand-picked hex."""
    for whole in tree.WHOLES:
        assert whole.accent in defaults.ROSE_PALETTE
    assert len(set(tree.ROSE_ACCENTS_USED)) == 6      # no hue used twice


# --- 2/3. THE SCROLL LAWS ---------------------------------------------------

@pytest.mark.parametrize("columns", [
    defaults.ENCYCLOPEDIA_HOME_COLUMNS,
    defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS,
])
def test_a_full_row_never_exceeds_the_minimum_viewport(columns):
    """The geometry half of the no-X-scroll law: at the narrowest window
    the owner can make, a FULL row of cards still fits — the card-width
    and row-width formulas are exact inverses (Rule #5, one pair)."""
    width = defaults.ENCYCLOPEDIA_MIN_WIDTH_PX
    card = card_width_for(width, columns)
    assert row_content_width(card, columns) <= width


def test_the_home_screen_owns_no_scroll_area(app, topics):
    """The strongest form of "the first screen never scrolls": there is
    nothing there that COULD scroll."""
    dialog = EncyclopediaDialog()
    assert dialog._stack.currentWidget() is dialog._home
    assert not dialog._home.findChildren(QScrollArea)
    dialog.deleteLater()


def test_no_horizontal_bar_on_any_level_at_the_minimum_size(app):
    """The live half: open the window at its own minimum, walk all three
    levels, and demand every scroll area keep its horizontal bar OFF."""
    dialog = EncyclopediaDialog()
    dialog.resize(dialog.minimumWidth(), dialog.minimumHeight())
    dialog.show()
    app.processEvents()
    for step in (lambda: None,
                 lambda: dialog.show_whole("divine"),
                 lambda: dialog.show_topic("greek")):
        step()
        app.processEvents()
        for area in dialog.findChildren(QScrollArea):
            assert area.horizontalScrollBarPolicy() == (
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            assert not area.horizontalScrollBar().isVisible()
    dialog.deleteLater()


def test_zooming_all_the_way_in_still_grows_no_horizontal_bar(app):
    """Zoom scales cards, fonts and images — never the page's width past
    its viewport (owner round R8b item 5a; the regression that started
    this law was exactly "zoom in on a narrow window")."""
    from config import constants

    dialog = EncyclopediaDialog()
    dialog.resize(dialog.minimumWidth(), dialog.minimumHeight())
    dialog.show()
    dialog.show_topic("week")
    app.processEvents()
    dialog._apply_zoom_delta(120 * 40)        # far past the ceiling
    app.processEvents()
    assert dialog._zoom == constants.ENCYCLOPEDIA_ZOOM_RANGE[1]
    for area in dialog.findChildren(QScrollArea):
        assert not area.horizontalScrollBar().isVisible()
    dialog.deleteLater()


# --- 4. THE VARIANT LAW -----------------------------------------------------

def test_registers_of_one_subject_became_one_card(topics):
    """The merges the owner sealed — and the sources are GONE, not kept
    alongside (Rule #6)."""
    assert [label for label, _s, _e in topics["bible"]["variants"]] == [
        "Bible", "Bible II", "Bible Dark",
    ]
    assert [label for label, _s, _e in topics["creeds"]["variants"]] == [
        "Creeds", "Ancient religions",
    ]
    assert [label for label, _s, _e in topics["eclipses"]["variants"]] == [
        "Solar", "Lunar",
    ]
    assert [label for label, _s, _e in topics["greek"]["variants"]] == list(
        tree.GOD_VARIANT_LABELS
    )
    for retired in ("bible2", "bible_dark", "religion", "religion_alt",
                    "eclipse_solar", "eclipse_lunar", "cube"):
        assert retired not in topics


def test_every_topic_carries_a_variant_range_covering_its_pages(topics):
    """`variants` is TOTAL — a single-register theme carries one nameless
    range, so no screen needs a special case (Rule #7)."""
    for key, topic in topics.items():
        variants = topic["variants"]
        assert variants[0][1] == 0, key
        assert variants[-1][2] == len(topic["entries"]), key
        for (_label, start, stop), (_next, next_start, _ns) in zip(
            variants, variants[1:]
        ):
            assert start < stop == next_start, key


def test_the_switcher_keeps_the_page_offset(topics):
    """Monday stays Monday: page 3 of Planetary is page 3 of Pantheon."""
    greek = topics["greek"]
    assert switch_variant(greek, 3, +1) == 14      # 11 + 3
    assert variant_at(greek, 14) == 1
    assert switch_variant(greek, 14, -1) == 3


def test_a_shorter_register_clamps_instead_of_overrunning(topics):
    """The Wider Court runs 4 pages against Planetary's 11 — page 9 of
    the Pantheon lands on the Court's LAST page, never past it."""
    greek = topics["greek"]
    landed = switch_variant(greek, 11 + 9, +1)
    _label, start, stop = greek["variants"][2]
    assert landed == stop - 1
    assert variant_at(greek, landed) == 2


def test_the_loop_wraps(topics):
    greek = topics["greek"]
    assert variant_at(greek, switch_variant(greek, 22, +1)) == 0


# --- THE JUMP CONTRACT ------------------------------------------------------

def test_a_merged_register_still_answers_to_its_own_dial_name(topics):
    """`bible_dark` is a dial theme with no card of its own any more —
    its Spacebar jump must still land on its own pages."""
    assert resolve_target(topics, "bible_dark", 3) == ("bible", 25)
    assert resolve_target(topics, "religion_alt", 2) == ("creeds", 13)
    assert resolve_target(topics, "eclipse_lunar", 1) == ("eclipses", 6)


def test_planet_signs_resolves_onto_the_planets_card(topics):
    assert resolve_target(topics, "planet_signs", 2) == ("planets", 2)


def test_the_old_flat_cube_index_is_re_aimed_across_the_four_cards(topics):
    """The wheel table in `config/archetypes.py` still says
    `("cube", 35)`; the resolver puts it on the page that entry always
    named — which is why the entry ORDER stays a contract."""
    for flat, (expected_topic, name) in {
        0: ("cube_doctrine", "The Cube"),
        11: ("cube_axes", "Loyalty"),
        35: ("cube_figures", "The Steady Guardian"),
        41: ("cube_projections", "The Banknote Axes"),
    }.items():
        key, index = resolve_target(topics, "cube", flat)
        assert key == expected_topic
        assert topics[key]["entries"][index]["name"] == name


def test_an_unknown_target_is_a_no_op_not_a_crash(topics):
    """The caller is the dial: a stale wheel target must leave the
    window where it is (Rule #1's documented-fallback exception)."""
    assert resolve_target(topics, "no_such_theme", 0) is None


# --- THE CUBE SPLIT AND THE GUIDE CARD --------------------------------------

def test_the_four_cube_cards_partition_the_forty_two_pages(topics):
    """A PARTITION, not a re-cut: no page dropped, none read twice, the
    order untouched (it is the Spacebar contract itself)."""
    covered = []
    for key, title, start, stop in tree.CUBE_TOPICS:
        assert topics[key]["title"] == title
        assert len(topics[key]["entries"]) == stop - start
        covered.extend(range(start, stop))
    assert covered == list(range(42))


def test_the_guide_is_a_card_built_from_the_help_books_own_json(topics):
    """Owner decision 2026-07-28: the Guide is a card in The Instrument
    ("jedno mesto za čitanje svega"), built from
    `assets/instrument/guide/*.json` — the help book's content is read
    where it already lives, never copied into the encyclopedia database
    (Rule #5)."""
    import json

    guide = topics["guide"]
    pages = json.loads(
        (defaults.GUIDE_DIR / "pages.json").read_text(encoding="utf-8")
    )["pages"]
    assert len(guide["entries"]) == len(pages)
    assert guide["entries"][0]["name"] == pages[0]["title"]
    for entry, page in zip(guide["entries"], pages):
        assert len(entry["images"]) == len(page["images"])
        assert entry["article"][0] == "guide"
        assert entry["article"][1].startswith("[[")
    assert tree.THEME_TO_WHOLE["guide"] == "instrument"
