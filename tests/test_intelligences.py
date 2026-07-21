"""THE NINE INTELLIGENCES canon-web rewrite + weekday-law reseat
(owner-sealed R7b 2026-07-21).

Pins the topic page order, the sealed day->intelligence mapping and the
Sun's-three-faces trio, checks each article actually carries its arm's
TRUE web (virtue, vice, mood, weekday, profession) as symbolism.json
`arms` states it — so no shuffled-mood transcript can creep back in — and
pins the tiny continents MOOD micro-pass done in the same round.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date

from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository


# The owner-sealed weekday-arm mapping (six arms).
DAY_INTELLIGENCE = {
    "moon": "Interpersonal",
    "mars": "Bodily-Kinesthetic",
    "mercury": "Linguistic",
    "jupiter": "Logical-Mathematical",
    "venus": "Musical",
    "saturn": "Naturalist",
}
# The Sun's three faces (Ruler / Servant / Ninth).
TRIO = {
    "ruler": "Spatial",
    "servant": "Intrapersonal",
    "ninth": "Existential",
}
PROFESSION_TOKEN = {
    "moon": "Physician", "mars": "Soldier", "mercury": "Merchant",
    "jupiter": "Priest", "venus": "Artist", "saturn": "Farmer",
}


def _arms():
    data = SymbolismRepository()._load()
    return {arm["body"]: arm for arm in data["arms"]}


def _base(name):
    return EncyclopediaRepository().entry("intelligence", name)["base"]


# --- 1. Topic page order (weekday law) --------------------------------------


def test_topic_order_follows_the_weekday_law():
    """title -> Monday..Saturday -> Ruler -> Servant -> Ninth."""
    from app.encyclopedia import _topics

    entries = _topics(date(2026, 7, 7))["intelligences"]["entries"]
    assert [e["name"] for e in entries] == [
        "The Nine Intelligences",
        "Interpersonal",         # Monday
        "Bodily-Kinesthetic",    # Tuesday
        "Linguistic",            # Wednesday
        "Logical-Mathematical",  # Thursday
        "Musical",               # Friday
        "Naturalist",            # Saturday
        "Spatial",               # Sun · Ruler
        "Intrapersonal",         # Sun · Servant
        "Existential",           # Ninth
    ]
    # Every entry wires its badge stem and resolves an article.
    enc = EncyclopediaRepository()
    for entry in entries:
        ref = entry["article"]
        assert enc.entry(ref[1], ref[2])["base"].startswith("[[")


# --- 2. The sealed mapping table --------------------------------------------


def test_trio_mapping_table():
    """The Sun's three faces carry Visual-Spatial / Intrapersonal /
    Existential, and each names its sealed reason."""
    ruler = _base(TRIO["ruler"])
    assert "Ruler" in ruler and "Eye" in ruler and "Pride" in ruler
    servant = _base(TRIO["servant"])
    assert "Servant" in servant and "midnight" in servant and "Judas" in servant
    ninth = _base(TRIO["ninth"])
    low = ninth.lower()
    assert "unfound" in low and "noon" in low
    assert "wish" in low and "question" in low


def test_each_weekday_intelligence_carries_its_true_arm_web():
    """Every one of the six weekday intelligences names its arm's TRUE
    virtue, vice, mood, weekday and profession — read straight from
    symbolism.json `arms`, so a shuffled-mood transcript can never
    re-enter (Wed = Sorrow, Thu = Joy, exactly)."""
    arms = _arms()
    for body, intelligence in DAY_INTELLIGENCE.items():
        arm = arms[body]
        base = _base(intelligence)
        for token in (
            arm["day"], arm["mood"], arm["virtue"], arm["vice"],
            PROFESSION_TOKEN[body],
        ):
            assert token in base, (intelligence, token)


def test_no_shuffled_moods_wednesday_sorrow_thursday_joy():
    """The exact trap the round warns of: Wednesday must read Sorrow (not
    Joy) and Thursday Joy (not Sorrow)."""
    wed = _base("Linguistic")
    thu = _base("Logical-Mathematical")
    assert "Sorrow" in wed and "Joy" not in wed
    assert "Joy" in thu and "Sorrow" not in thu


def test_title_page_keeps_the_gardner_core_and_names_the_three_faces():
    title = _base("The Nine Intelligences")
    assert "1983" in title and "1995" in title      # factual Gardner core
    assert "Three Faces" in title                    # the trio subhead
    low = title.lower()                              # house style caps RULER/SERVANT
    assert "ruler" in low and "servant" in low and "unfound" in low


# --- 3. The continents MOOD micro-pass (same round) -------------------------


def test_continents_mood_micro_pass_aligns_to_true_arm_moods():
    """Asia carries Wednesday's Sorrow, Africa carries Thursday's Joy,
    North America carries Saturday's Renewal (its strongest link) — and
    Asia never claims Joy nor Africa Sorrow."""
    sym = SymbolismRepository()
    asia = sym.article("continents", "mercury")["base"]
    africa = sym.article("continents", "jupiter")["base"]
    north_america = sym.article("continents", "saturn")["base"]
    assert "Sorrow" in asia and "Joy" not in asia
    assert "Joy" in africa and "Sorrow" not in africa
    assert "Renewal" in north_america
