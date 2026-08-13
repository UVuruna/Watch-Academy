"""THE ECLIPSE ENCYCLOPEDIA DEBT (owner ballot 2026-08-13, item 14) —
pinned.

The ballot's 14th accepted item was the Encyclopedia page carrying the
explanations for the eclipse family: the seven kinds, why a hybrid is
both at once, why a totally eclipsed Moon turns copper, the Danjon
scale (and that this app's L is indicative), the four contacts P1/U1/
U4/P4 (and that this app's marks are derived, not observed), and how
to read all twelve display styles the six new painters (2026-08-13)
added. It shipped as content inside the ALREADY-registered eclipse
whole rather than as a new, separately-registered page, because the
Encyclopedia's own law (`test_registers_of_one_subject_became_one
_card`) is that one subject gets ONE card — the Solar/Lunar Overview
chapters are that card's entry-zero, exactly where a reader meets the
whole-phenomenon explanation before the specific kinds.

This test is the tooth: it asserts the eclipse pages EXIST, are
REGISTERED in the tree, are REACHABLE from Home through the built
topic table, and are NON-EMPTY — carrying the ballot's own honesty
language for `danjon_scale`, `contact_marks` and `totality_path`.
"""

from app.encyclopedia import topics as build_topics
from app.encyclopedia.tree import resolve_target
from config import encyclopedia_tree as tree
from data.encyclopedia import shared_encyclopedia


def test_eclipses_are_seated_in_the_sky_whole():
    sky = next(w for w in tree.WHOLES if w.key == "sky")
    assert "eclipses" in sky.themes


def test_eclipse_solar_and_lunar_topics_are_built_and_reachable():
    topics = build_topics()
    assert "eclipses" in topics
    # The two dial-facing names merge into the ONE "eclipses" card
    # (THE REACHABILITY LAW) — each keeps its own variant slice.
    assert topics["eclipses"]["variants"] == (
        ("Solar", 0, 5), ("Lunar", 5, 9),
    )
    assert resolve_target(topics, "eclipse_solar", 0) == ("eclipses", 0)
    assert resolve_target(topics, "eclipse_lunar", 0) == ("eclipses", 5)


def test_every_eclipse_chapter_is_registered_and_non_empty():
    topics = build_topics()
    entries = topics["eclipses"]["entries"]
    assert len(entries) == 9   # 5 solar (Overview + 4 kinds) + 4 lunar (Overview + 3 kinds)

    enc = shared_encyclopedia()
    for key in (
        "Solar_Overview", "Solar_Total", "Solar_Annular", "Solar_Partial",
        "Solar_Hybrid", "Lunar_Overview", "Lunar_Total", "Lunar_Partial",
        "Lunar_Penumbral",
    ):
        page = enc.eclipse(key)
        assert page["title"].strip()
        assert len(page["base"].strip()) > 200, key


def test_the_solar_overview_states_the_totality_path_honesty():
    page = shared_encyclopedia().eclipse("Solar_Overview")["base"]
    assert "GREATEST eclipse" in page
    assert "UNDER-reads" in page
    assert "DASHED" in page


def test_the_lunar_overview_states_the_danjon_and_contact_honesty():
    page = shared_encyclopedia().eclipse("Lunar_Overview")["base"]
    assert "INDICATIVE" in page
    assert "DANJON SCALE" in page
    assert "INSTANT OF GREATEST ECLIPSE" in page
    assert "DERIVED" in page


def test_all_twelve_display_styles_are_named_somewhere_in_the_pages():
    enc = shared_encyclopedia()
    solar_text = "\n".join(
        enc.eclipse(k)["base"] for k in (
            "Solar_Overview", "Solar_Total", "Solar_Annular",
            "Solar_Partial", "Solar_Hybrid",
        )
    )
    lunar_text = "\n".join(
        enc.eclipse(k)["base"] for k in (
            "Lunar_Overview", "Lunar_Total", "Lunar_Partial",
            "Lunar_Penumbral",
        )
    )
    for style in (
        "BITE", "MAGNITUDE ARC", "HALO", "TOTALITY PATH", "TYPE EMBLEM",
        "DIAL SHADOW",
    ):
        assert style in solar_text, style
    for style in (
        "UMBRA SWEEP", "HORIZON SHADOW", "BLOOD MOON", "HALO",
        "DANJON SCALE", "CONTACT MARKS",
    ):
        assert style in lunar_text, style
