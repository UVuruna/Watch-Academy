"""THE SLAVIC MONTHS — a Calendar-pointer 12-set + Encyclopedia topic
(owner-sealed R7b 2026-07-21).

Pins the config registration (twelve Croatian months, one per Gregorian
month), the CANONICAL SOURCELESS `months/` root (outside
ART_SOURCED_ROOTS, the subdial precedent — graceful-absent art), the
mount-radius per the DESIGN ZODIAC law, and the Encyclopedia topic's page
order + article web (etymology, Gregorian equivalent, pan-Slavic siblings,
the pointer wedge).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import calendar
from datetime import date

from config import calendar_mounts, constants, defaults, paths
from data.encyclopedia import EncyclopediaRepository


GREGORIAN = {i: calendar.month_name[i] for i in range(1, 13)}


# --- 1. The config registration ---------------------------------------------


def test_slavic_months_table_is_twelve_in_gregorian_order():
    months = calendar_mounts.SLAVIC_MONTHS
    assert len(months) == 12
    assert [m[3] for m in months] == list(range(1, 13))     # Jan..Dec
    stems = [m[2] for m in months]
    croats = [m[0] for m in months]
    assert len(set(stems)) == 12 and len(set(croats)) == 12
    # The sealed opening name (owner's own example convention).
    assert months[5][:2] == ("Lipanj", "the Linden Month")   # June
    # ASCII, diacritic-free plate stems (the owner's future prompt sheet).
    assert all(stem.isascii() and stem.isalpha() for stem in stems)


def test_mount_radius_is_in_the_design_law_band():
    """The DESIGN ZODIAC law fixes the marks at 60-70% of the dial radius."""
    assert 0.60 <= calendar_mounts.CALENDAR_MOUNT_RADIUS_FRACTION <= 0.70


# --- 2. The canonical sourceless root (subdial precedent) -------------------


def test_months_root_is_the_slavic_months_calendar_dir():
    """The Slavic months are a Calendar-category mount set (RESTRUCTURE
    2026-07-22), living at their primary register's colored look since
    the tree law (2026-07-26):
    assets/calendars/slavic_months/primary/colored/."""
    assert defaults.MONTHS_ART_DIR.name == "colored"
    assert defaults.MONTHS_ART_DIR.parent.name == "primary"
    assert defaults.MONTHS_ART_DIR.parent.parent.name == "slavic_months"
    assert defaults.MONTHS_ART_DIR.parent.parent.parent.name == "calendars"


def test_month_plates_resolve_by_suffix_or_stay_absent():
    """`paths.art_file` resolves a `slavic_months/` plate to its source
    suffix when the art exists (the owner's partial ChatGPT drop), else
    returns the canonical path unchanged so every consumer hides it — the
    wired-ahead graceful-absent contract."""
    for _cro, _gloss, stem, _m in calendar_mounts.SLAVIC_MONTHS:
        plate = defaults.MONTHS_ART_DIR / f"{stem}.png"
        resolved = paths.art_file(plate)
        if resolved.exists():
            assert resolved.stem.endswith(("_gem", "_gpt"))
        else:
            assert resolved == plate


# --- 3. The Encyclopedia topic ----------------------------------------------


def test_topic_page_order_title_then_twelve():
    from app.encyclopedia import topics as _topics

    entries = _topics(date(2026, 7, 7))["months"]["entries"]
    # Title + twelve Slavic months + the Blue Moon Law's Sol/Modrenik
    # pair (owner-sealed 2026-07-22, R12) closing the topic.
    assert len(entries) == 15
    assert entries[0]["name"] == "The Slavic Months"
    assert entries[0]["article"] == ("emblem", "months", "The Slavic Months")
    for entry, (cro, gloss, _stem, _m) in zip(
        entries[1:13], calendar_mounts.SLAVIC_MONTHS
    ):
        assert entry["name"] == f"{cro} ({gloss})"
        assert entry["article"] == ("emblem", "months", cro)
    assert entries[13]["name"] == "Sol (the Sun's Month)"
    assert entries[13]["article"] == ("emblem", "months", "Sol")
    assert entries[14]["name"] == "Modrenik (the Blue Moon Month)"
    assert entries[14]["article"] == ("emblem", "months", "Modrenik")


def test_the_thirteenth_pair_articles_carry_the_duality():
    """Sol and Modrenik (owner-sealed 2026-07-22, R12): each names its
    own real-world/invented origin AND weaves the OTHER's name in (the
    owner's duality — the Sun's thirteenth at the year's top, the
    Moon's at its bottom)."""
    enc = EncyclopediaRepository()
    sol = enc.entry("months", "Sol")["base"]
    modrenik = enc.entry("months", "Modrenik")["base"]
    assert len(sol) > 300 and len(modrenik) > 300
    assert "Cotsworth" in sol and "Kodak" in sol
    assert "Modrenik" in sol                          # weaves the sibling in
    assert "Sol" in modrenik                          # weaves the sibling in
    assert "blue" in modrenik.lower()                 # modar/blue moon etymology


def test_topic_rides_the_instrument_once():
    """SESSION 27 (owner-sealed 2026-07-28): the Slavic Months moved
    with the split of the old Celestial Engine — the year's own wheel
    of labour belongs to THE INSTRUMENT, beside the week and the eras
    (the wheels the watch turns), while the Engine keeps the sky it
    computes."""
    from app.encyclopedia import topics as _topics
    from config.encyclopedia_tree import WHOLES

    instrument = {whole.key: whole for whole in WHOLES}["instrument"]
    assert "months" in instrument.themes
    every = [theme for whole in WHOLES for theme in whole.themes]
    assert every.count("months") == 1        # not scattered into two wholes
    assert "months" in _topics()


def test_every_month_article_carries_its_web():
    """Each article names its own Croatian month, states the Gregorian
    equivalent in prose, and reads non-trivially (Rule #2 — real content,
    not a placeholder)."""
    enc = EncyclopediaRepository()
    for cro, _gloss, _stem, month in calendar_mounts.SLAVIC_MONTHS:
        base = enc.entry("months", cro)["base"]
        assert len(base) > 300, cro
        assert cro in base, cro                          # its own name
        assert GREGORIAN[month] in base, (cro, GREGORIAN[month])  # Gregorian


def test_title_and_sibling_shifts_are_written():
    """The title page frames the set + the pointer; the drift stories the
    owner asked for (siblings 'priče bogatije') are actually present."""
    enc = EncyclopediaRepository()
    title = enc.entry("months", "The Slavic Months")["base"]
    assert "Calendar" in title and "wedge" in title
    assert "Czech" in title or "Polish" in title or "Ukrainian" in title
    # The signature drift: Listopad = October here, November up north
    # (the house style caps the shifted month for emphasis).
    listopad = enc.entry("months", "Listopad")["base"].lower()
    assert "november" in listopad and "october" in listopad
    # The sickle/linden swap: Croatia's July sickle, the north's August.
    srpanj = enc.entry("months", "Srpanj")["base"].lower()
    assert "august" in srpanj
