"""THE DOUBLE NINTH LAW (standing law, owner decree 2026-07-29):

    A theme may mount a DOUBLE NINTH only with a DEFINED alternation
    mechanism, and the Encyclopedia always shows ONLY the currently
    active ninth — never both.

This module is the LAW's own guard: it collects every double ninth
this program registers, from EVERY registry shape that can carry one —
`constants.WEEKDAY_THEME_NINTH_EASTER_EGG`, `constants.
WEEKDAY_THEME_NINTH_NIGHT`, and `pantheon.WEEKDAY_SEAT_ROSTERS[*]
["ninth"]` — and fails the build the moment one is found with no
`constants.NINTH_MECHANISMS` entry, or an entry naming a mechanism no
dispatch actually implements. It also pins the three sealed mechanisms
by name (continents "easter_egg", sw_dyad "daynight", cp_corpo
"term_weekly") and proves the Encyclopedia's active-only law for the
two mechanisms that read live state.

Layer: tests. See project CLAUDE.md "THE DOUBLE NINTH LAW" and
[Config (folder)](../config/___config.md).
"""

from datetime import date

from config import constants, pantheon
from render.ninths import ninth_table_for


def _double_ninth_themes() -> set:
    """Every theme carrying a DOUBLE Ninth, gathered from EVERY registry
    shape that can hold one — the union THE DOUBLE NINTH LAW's guard
    reads. A future registry (a fourth shape) joins this union the
    moment it exists; forgetting to add it here is exactly the silent
    drift the law exists to catch."""
    return (
        set(constants.WEEKDAY_THEME_NINTH_EASTER_EGG)
        | set(constants.WEEKDAY_THEME_NINTH_NIGHT)
        | {
            theme for theme, seats in pantheon.WEEKDAY_SEAT_ROSTERS.items()
            if "ninth" in seats
        }
    )


def test_every_double_ninth_has_a_defined_mechanism():
    """No double ninth may exist without a `NINTH_MECHANISMS` entry —
    the exact failure mode THE DOUBLE NINTH LAW forbids."""
    double_ninths = _double_ninth_themes()
    assert double_ninths, "the probe itself found nothing — check the union"
    missing = double_ninths - set(constants.NINTH_MECHANISMS)
    assert not missing, f"double ninth with no mechanism: {sorted(missing)}"


def test_every_mechanism_name_is_one_a_dispatch_implements():
    """Every `NINTH_MECHANISMS` value must be in the vocabulary a real
    dispatch recognizes — a typo or an unimplemented name fails here
    instead of silently falling through to the canonical plate."""
    unknown = set(constants.NINTH_MECHANISMS.values()) - constants.NINTH_MECHANISM_KINDS
    assert not unknown, f"unimplemented mechanism name(s): {sorted(unknown)}"


def test_every_mechanism_entry_names_a_real_double_ninth():
    """The REVERSE direction: a `NINTH_MECHANISMS` entry with no double
    ninth behind it would be a stale/orphan lie — nothing to dispatch
    for."""
    double_ninths = _double_ninth_themes()
    orphans = set(constants.NINTH_MECHANISMS) - double_ninths
    assert not orphans, f"mechanism entry with no double ninth: {sorted(orphans)}"


def test_the_three_sealed_mechanisms():
    """The owner's three Double-Ninth verdicts (2026-07-29), pinned
    together so a future edit cannot blur one theme's mechanism into
    another's by accident."""
    assert constants.NINTH_MECHANISMS == {
        "continents": "easter_egg",
        "sw_dyad": "daynight",
        "cp_corpo": "term_weekly",
    }


def test_ninth_table_for_dispatches_by_mechanism():
    """`render.ninths.ninth_table_for` — the ONE place `theme_ninth`
    asks "which alt table?" — reads EXACTLY the table its own theme's
    mechanism names, and cp_corpo's "term_weekly" deliberately reaches
    NEITHER alt table (its rotation rides `on_date` through the seat
    roster alone, `config.pantheon.rotating_art_file`'s cadence
    override — see that function's own docstring)."""
    assert (
        ninth_table_for("continents", active_alt=True)
        is constants.WEEKDAY_THEME_NINTH_EASTER_EGG
    )
    assert (
        ninth_table_for("sw_dyad", active_alt=True)
        is constants.WEEKDAY_THEME_NINTH_NIGHT
    )
    assert ninth_table_for("cp_corpo", active_alt=True) is None
    # Inactive is inactive regardless of mechanism.
    for theme in ("continents", "sw_dyad", "cp_corpo"):
        assert ninth_table_for(theme, active_alt=False) is None
    # A theme with no double ninth at all never reaches an alt table.
    assert ninth_table_for("greek", active_alt=True) is None


def test_every_alt_ninth_name_has_an_encyclopedia_article():
    """Every ALT face's NAME (not just the canonical one
    `tests/test_theme_completeness.py` already checks) must resolve a
    real `encyclopedia.json` "ninths" article — the exact landmine THE
    THEME COMPLETION LAW exists to catch: the day it becomes reachable
    is the day `render.compositor._dual_face_columns` calls `self.
    _encyclopedia.entry("ninths", name)` on it, a plain dict lookup that
    raises loudly (Rule #1) rather than swallowing a missing key."""
    from data.encyclopedia import EncyclopediaRepository

    enc = EncyclopediaRepository()
    for name, _rel in constants.WEEKDAY_THEME_NINTH_EASTER_EGG.values():
        enc.entry("ninths", name)          # raises KeyError if missing
    for name, _rel in constants.WEEKDAY_THEME_NINTH_NIGHT.values():
        enc.entry("ninths", name)
    assert "Exegol" in enc.entry("ninths", "Exegol")["base"]


def _bronze_plate(entry: dict):
    """The Bronze look's resolved plate from a metal-cycled Encyclopedia
    entry — the SAME shape `_metal_looks` builds ("Colored"?/"Bronze"/
    "Gold"/"Silver")."""
    for label, rows in entry["looks"]:
        if label == "Bronze":
            return rows[0][0]
    raise AssertionError("entry carries no Bronze look")


def _variant_block(topic: dict, label: str) -> list:
    """One SOURCE theme's own entries out of a merged VARIANT card
    (`app.encyclopedia.tree._merge_variants` concatenates registers of
    one subject into ONE card and deletes the source keys — cp_corpo
    lives inside `topics()["cyberpunk"]`'s "Power" span, sw_dyad inside
    `topics()["starwars"]`'s "Dyad" span; this reads the block back out
    by its own declared label rather than a hardcoded offset)."""
    entries = topic["entries"]
    for variant_label, start, stop in topic["variants"]:
        if variant_label == label:
            return entries[start:stop]
    raise AssertionError(f"no {label!r} variant in {topic['title']!r}")


def test_sw_dyad_encyclopedia_shows_only_the_active_ninth_face():
    """THE DOUBLE NINTH LAW's Encyclopedia clause for sw_dyad: the page
    speaks ONE name/plate, switching with `is_daylight` — never a
    two-face page, and never the frozen "always Ghosts" the shared
    ninths loop gave every OTHER theme before this law. sw_dyad lives
    inside the merged "starwars" card (Jedi | Sith | Dyad switcher)."""
    from app.encyclopedia import topics as _topics

    day_dyad = _variant_block(_topics(is_daylight=True)["starwars"], "Dyad")
    night_dyad = _variant_block(_topics(is_daylight=False)["starwars"], "Dyad")
    assert len(day_dyad) == len(night_dyad) == 11   # one Ninth page, not two
    day_ninth, night_ninth = day_dyad[10], night_dyad[10]
    assert day_ninth["name"] == "The Ghosts"
    assert night_ninth["name"] == "Exegol"
    assert day_ninth["images"] != night_ninth["images"]
    assert day_ninth["article"] == ("emblem", "ninths", "The Ghosts")
    assert night_ninth["article"] == ("emblem", "ninths", "Exegol")


def test_cp_corpo_encyclopedia_shows_only_the_ruling_weeks_triple():
    """THE DOUBLE NINTH LAW's Encyclopedia clause for cp_corpo's WEEKLY
    MANDATE: the Throne (good), Mirror (evil) and Ninth pages all rotate
    to the traveled date's RULING half — never a two-face page — while
    the display NAME stays the theme's static `WEEKDAY_DUAL_NAMES`
    (Session 32's established convention, unchanged by this law).
    cp_corpo lives inside the merged "cyberpunk" card (Gangs | Street |
    Power switcher)."""
    from app.encyclopedia import topics as _topics

    even_week, odd_week = date(2026, 7, 26), date(2026, 7, 27)   # ISO 30, 31
    even_entries = _variant_block(_topics(even_week)["cyberpunk"], "Power")
    odd_entries = _variant_block(_topics(odd_week)["cyberpunk"], "Power")
    assert len(even_entries) == len(odd_entries) == 11

    even_good, odd_good = even_entries[8], odd_entries[8]
    even_evil, odd_evil = even_entries[9], odd_entries[9]
    even_ninth, odd_ninth = even_entries[10], odd_entries[10]

    # Names stay static — the established Sunday-duality convention.
    assert even_good["name"] == odd_good["name"] == "Saburo Arasaka"
    assert even_evil["name"] == odd_evil["name"] == "Yorinobu"
    assert even_ninth["name"] == odd_ninth["name"] == "Alt Cunningham"

    # Plates flip with the ruling week.
    assert _bronze_plate(even_good).stem.startswith("Saburo_Arasaka")
    assert _bronze_plate(odd_good).stem.startswith("Rosalind_Myers")
    assert _bronze_plate(even_evil).stem.startswith("Yorinobu")
    assert _bronze_plate(odd_evil).stem.startswith("Kurt_Hansen")
    assert even_ninth["images"][0].stem.startswith("Alt_Cunningham")
    assert odd_ninth["images"][0].stem.startswith("Rache_Bartmoss")


def test_cp_gangs_and_cp_street_stay_on_plain_date_rotation():
    """THE WEEKLY MANDATE is cp_corpo's OWN law — its Cyberpunk
    siblings' rosters (no "sun"/"dual"/"ninth" seats to synchronize,
    and no `NINTH_MECHANISMS` entry) must not have drifted onto ISO-week
    parity by accident."""
    assert "cp_gangs" not in constants.NINTH_MECHANISMS
    assert "cp_street" not in constants.NINTH_MECHANISMS
    assert "ninth" not in pantheon.WEEKDAY_SEAT_ROSTERS["cp_gangs"]
    assert "ninth" not in pantheon.WEEKDAY_SEAT_ROSTERS["cp_street"]
