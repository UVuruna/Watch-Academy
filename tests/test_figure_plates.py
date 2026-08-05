"""THE HOVER LAW's ledger — three named plates per figure, and what is owed.

Owner decree 2026-08-04. One figure is drawn three times and each
drawing has exactly one place: the round 1:1 plate in the dial's
diamond, the tall LANCET in the hover card's left column, and one small
RONDEL above each paragraph in the hover's right column.

The point of naming the three slots (`config.archetypes.figure_plates`)
is that an EMPTY slot becomes a debt somebody can count. Before this,
"we should add pictures for the paragraphs one day" was a sentence in a
chat; now it is a number this test prints, per family, and a sheet that
briefs every missing plate
(`research/prompts/archetype/rondel_prompts.md`).

The tests below do NOT fail on missing art — the art is the owner's own
to generate, and the renderer's graceful-absent law already draws the
name instead. They fail on the two things that are OURS to get wrong:
a slot that resolves to the wrong register, and a debt count that has
drifted from what the ledger claims.
"""

import json
from pathlib import Path

from config import archetypes, paths

_ROOT = Path(__file__).resolve().parents[1]
_SYMBOLISM = _ROOT / "Database" / "symbolism.json"

# What each family owes in RONDELS today (owner's generation queue, the
# sheet's own count). A family that has them all reads 0. This is a
# ledger, not a target: when the owner generates a set, its number drops
# and this table drops with it — the guard below fails if the disk and
# the table disagree, so the debt can never quietly grow.
RONDEL_DEBT = {
    "temperaments": 4,
    "tetramorph": 4,      # only the ELEMENT row; the evangelist rondels exist
    "persons": 6,
    "one_soul": 6,
    "genesis": 3,
    "council": 6,
    "character": 8,
    "vertices": 8,
    "family": 1,          # Rondel_Anchor — the file on disk says "Dawn"
}


def _rows_per_figure() -> dict:
    """(archetype key, entity) -> how many paragraphs its article has —
    the count that decides how many rondels the figure asks for."""
    articles = json.loads(_SYMBOLISM.read_text(encoding="utf-8"))["articles"]
    out = {}
    for key, spec in archetypes.ARCHETYPES.items():
        entries = articles.get(spec.get("articles"), {})
        for figure in spec.get("figures", ()):
            entry = entries.get(figure.get("entity")) or {}
            out[(key, figure.get("entity"))] = len(entry.get("rows", []))
    return out


def _every_figure():
    for key, spec in archetypes.ARCHETYPES.items():
        for figure in spec.get("figures", ()):
            yield key, figure


def test_the_dial_slot_is_always_the_circle_register():
    """Slot one, restated where the slots are defined: the dial plate is
    the family's `circle` register, whatever the figure's own art is."""
    offenders = [
        f"{key}/{figure['name']}"
        for key, figure in _every_figure()
        if archetypes.figure_plates(figure)["dial"].parts[-3] != "circle"
    ]
    assert offenders == [], (
        "THE DIAL LAW: these figures' dial slot leaves the circle "
        "register: " + ", ".join(offenders)
    )


def test_the_hover_slot_is_the_lancet_the_figure_declares():
    """Slot two: the hover's left column holds the figure's OWN art —
    the lancet — unchanged. If this ever computed something, the hover
    and the dial would have swapped places, which is the failure the
    law was written against."""
    for key, figure in _every_figure():
        plates = archetypes.figure_plates(figure)
        assert plates["hover"] == Path(figure["file"]), key


def test_a_paragraph_rondel_is_named_for_its_subject():
    """Slot three: one rondel per paragraph beyond the first, its stem
    built from the paragraph's SUBJECT (the figure's second row), in the
    family's own register — the drop paths the prompt sheet writes."""
    figure = next(
        f for _k, f in _every_figure() if f["name"] == "The King"
    )
    plates = archetypes.figure_plates(figure, paragraphs=2)
    assert [p.name for p in plates["paragraphs"]] == ["Rondel_Crown.png"]
    assert plates["paragraphs"][0].parent == Path(figure["file"]).parent

    three = archetypes.figure_plates(figure, paragraphs=3)
    assert [p.name for p in three["paragraphs"]] == [
        "Rondel_Crown.png", "Rondel_Crown_3.png",
    ]


def test_paragraph_one_never_asks_for_a_rondel():
    """Row one IS the figure, and the figure already has a round plate.
    A second one would be the same image under a second name (Rule
    #19) — so a one-paragraph figure (the Eight Ages) owes nothing."""
    figure = next(f for _k, f in _every_figure() if f["name"] == "The King")
    assert archetypes.figure_plates(figure, paragraphs=1)["paragraphs"] == ()


def test_the_rondel_debt_matches_what_is_actually_missing():
    """The ledger above must equal the disk. A future round that
    generates a set and forgets to shrink this table fails here; so does
    one that adds figures without briefing their rondels."""
    rows = _rows_per_figure()
    counted: dict[str, int] = {}
    for key, spec in archetypes.ARCHETYPES.items():
        for figure in spec.get("figures", ()):
            paragraphs = rows.get((key, figure.get("entity")), 0)
            plates = archetypes.figure_plates(figure, paragraphs)
            family = Path(figure["file"]).parts[-4]
            for plate in plates["paragraphs"]:
                if paths.art_file(plate) is None or not paths.art_file(plate).exists():
                    counted[family] = counted.get(family, 0) + 1
    # the Tetramorph's row-2 rondel IS the evangelist plate, drawn and
    # wired; only its row-3 element plate is owed (see the sheet)
    assert counted == RONDEL_DEBT, (
        "the rondel debt moved: disk says " + json.dumps(counted, sort_keys=True)
        + " while RONDEL_DEBT claims "
        + json.dumps(RONDEL_DEBT, sort_keys=True)
        + " — update the table (and the sheet) in the same session"
    )
