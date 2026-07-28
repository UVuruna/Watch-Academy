"""THE ONE SOUL THEME — the prism-light doctrine in the Encyclopedia
(owner verdict 2026-07-27: "napravi naravno — jedna od važnijih ljubavnih
tematika").

Pins what this round sealed:

1. THE FAMILY — `one_soul` in `Database/encyclopedia.json`: the theme's
   title page, the six pillars in the wheel's own arm order, the Union
   and the Child, every page obeying the ARTICLE CHARTER's four
   movements (CUBE.md).
2. THE TRIPLE NAME IS VISIBLE — the topic's own title (the reader's top
   header) and its title PAGE both read the full "One Soul — The Vow —
   The Bond", while the gallery CARD, being a label, reads "One Soul".
3. THE HALL — the theme is The Archetypes' fourth card, not a separate
   pointer: the prism-SECONDARY wheel already IS its wheel.
4. THE SPACEBAR CONTRACT — every prism_secondary arm AND the centre jump to
   their own page, by the index `config/archetypes.py` declares.
5. NO DUPLICATED PROSE (Rule #5) — the dial's per-arm hover articles are
   untouched; these pages argue the doctrine instead.
"""

import json

import pytest

from config import archetypes, constants, paths
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository
from data.translations import collect_corpus

_CHARTER_HEADS = ("[[Thesis]]", "[[Argument]]",
                  "[[Correspondences]]", "[[Quote]]")
_PILLARS = ("Gratitude", "Support", "Passion",
            "Tolerance", "Trust", "Respect")


def _family() -> dict:
    return json.loads(
        (paths.database_dir() / "encyclopedia.json").read_text(
            encoding="utf-8"
        )
    )["one_soul"]


def test_the_one_soul_family_is_complete_and_in_wheel_order():
    """Six pillars in the wheel's own arm order (12h, 16h, 20h, 24h,
    04h, 08h), the Union at the centre, the Child as the Ninth, behind
    the theme's own title page — nine in all."""
    family = _family()
    assert list(family) == [
        constants.ONE_SOUL_THEME_TITLE, *_PILLARS,
        "The Union", "The Child",
    ]
    # The pillar order IS the wheel's figure order (CANON §Prism secondary).
    assert [figure["name"] for figure in archetypes.figures("prism_secondary")] \
        == list(_PILLARS)


def test_every_one_soul_page_obeys_the_article_charter():
    """CUBE.md's Article Charter: thesis → argument → correspondences →
    quote, in that order, and no page is a stub."""
    for name, node in _family().items():
        base = node["base"]
        positions = []
        for head in _CHARTER_HEADS:
            assert head in base, f"{name} misses {head}"
            positions.append(base.index(head))
        assert positions == sorted(positions), f"{name} order"
        assert len(base) > 600, f"{name} is a stub"


def test_the_theme_argues_its_doctrine_not_its_seats():
    """The pages carry the DOCTRINE the per-arm hovers cannot: the
    conjugation law, the three axes of love with their cross-cures, the
    union's two faces and the family triangle."""
    repo = EncyclopediaRepository()
    title = repo.entry("one_soul", constants.ONE_SOUL_THEME_TITLE)["base"]
    # The conjugation law — the theme's whole engine.
    assert "honesty is a trait of the individual" in title
    assert "conjugated" in title
    # The three names, argued rather than chosen between.
    for name in ("One Soul", "The Vow", "The Bond"):
        assert name in title, name
    assert "one soul dwelling in two bodies" in title      # Aristotle
    # The axes of love: all three cure pairs named on the title page.
    for cure in ("Trust disarms the Fight", "Support cures Suspicion",
                 "Gratitude cures Score-keeping",
                 "Tolerance cures Taking-for-granted",
                 "Passion burns away Contempt",
                 "Respect calms Jealousy"):
        assert cure in title, cure
    union = repo.entry("one_soul", "The Union")["base"]
    assert "servant-kingship" in union
    assert "union KEPT" in union and "union FELT" in union
    assert "Genesis 2:24" in union
    child = repo.entry("one_soul", "The Child")["base"]
    assert "FAMILY TRIANGLE" in child and "perichoresis" in child
    # The hearth roles as CANON.md amended them (RESTRUCTURE 2026-07-22):
    # Shield / Heart / ANCHOR, with the Dawn kept as the child's
    # time-reading — `research/bond_theme.md`'s older "Dawn AS the role"
    # is superseded, and this pin keeps the page on the canon side.
    for role in ("the Shield", "the Heart", "the Anchor"):
        assert role in child, role
    assert "time-reading stays the Dawn" in child
    assert "Ecclesiastes 4:12" in child


@pytest.mark.parametrize("pillar,shadow", (
    ("Gratitude", "Taking for Granted"),
    ("Support", "the Fight"),
    ("Passion", "jealousy"),
    ("Tolerance", "Score-keeping"),
    ("Trust", "Suspicion"),
    ("Respect", "Contempt"),
))
def test_every_pillar_names_its_own_shadow(pillar, shadow):
    """The conjugation law runs both ways: each pillar is a seat's
    virtue in the dual, each shadow that seat's vice in the dual."""
    base = EncyclopediaRepository().entry("one_soul", pillar)["base"]
    assert shadow in base
    assert "conjugat" in base


def test_the_triple_name_is_what_the_reader_sees():
    """Owner seal 2026-07-27: TITLED IN FULL it is the triple, LABELLED
    it is the single name. The topic title (the reader's own top header,
    `_topic_display_title`) and the title page both carry the triple;
    the gallery card carries "One Soul"."""
    from app.encyclopedia import topics as _topics

    topic = _topics()["one_soul"]
    assert topic["title"] == constants.ONE_SOUL_THEME_TITLE
    assert topic["entries"][0]["name"] == constants.ONE_SOUL_THEME_TITLE
    assert topic["tile_title"] == constants.ONE_SOUL_THEME_NAME


def test_the_theme_opens_on_its_triple_title_in_a_live_dialog():
    """The offscreen probe: the dialog opens the topic and the header
    really prints all three names (Rule #25 — verified, not assumed)."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog

    QApplication.instance() or QApplication([])
    dialog = EncyclopediaDialog(initial_topic="one_soul", initial_entry=0)
    assert dialog._title.text() == constants.ONE_SOUL_THEME_TITLE
    assert dialog._counter.text() == "1 / 9"
    # And every page turns without a crash, plate or no plate.
    for _ in range(9):
        dialog._step(1)
    dialog.deleteLater()


def test_the_one_soul_wheel_jumps_arm_by_arm_and_from_the_centre():
    """THE SPACEBAR CONTRACT: every prism_secondary figure's `enc` lands on
    its own pillar page, and the centre — the first archetype centre
    with a page at all — lands on the Union."""
    from app.encyclopedia import topics as _topics

    names = [
        entry["name"] for entry in _topics()["one_soul"]["entries"]
    ]
    for figure in archetypes.figures("prism_secondary"):
        topic, index = figure["enc"]
        assert topic == "one_soul", figure["entity"]
        assert names[index] == figure["name"], figure["entity"]
    centre = archetypes.center("prism_secondary")
    assert centre["enc"] == ("one_soul", 7)
    assert names[7] == centre["name"]


def test_the_hover_articles_are_untouched_and_never_duplicated():
    """Rule #5: the theme ARGUES the wheel, it does not restate it. The
    dial's own per-arm hover set still answers for every seat, and no
    encyclopedia page copies a hover row verbatim."""
    symbolism = SymbolismRepository()
    hover_rows = set()
    for entity in ("gratitude", "support", "passion", "tolerance",
                   "trust", "respect", "center"):
        node = symbolism.archetype_article("archetype_prism_secondary", entity)
        assert node["rows"]
        assert archetypes.ARCHETYPE_PENDING_LINE not in " ".join(node["rows"])
        hover_rows.update(node["rows"])
    for name, node in _family().items():
        for row in hover_rows:
            assert row not in node["base"], name


def test_the_one_soul_pages_ride_the_translation_corpus():
    """Every page is translatable — the Translation session must not
    have to hunt for them."""
    corpus = collect_corpus()
    for name in _family():
        assert f"encyclopedia/one_soul/{name}/base" in corpus
    # The renamed hexa PAINT label rides the UI corpus too (owner "ok."
    # 2026-07-27: Paint palette → Persons on the Prism's wheel row).
    assert "ui/Persons" in corpus
    assert constants.POINTER_PALETTE_LABELS["hexa"][0] == "Persons"
