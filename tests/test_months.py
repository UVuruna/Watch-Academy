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

from config import constants, defaults, paths
from data.encyclopedia import EncyclopediaRepository


GREGORIAN = {i: calendar.month_name[i] for i in range(1, 13)}


# --- 1. The config registration ---------------------------------------------


def test_slavic_months_table_is_twelve_in_gregorian_order():
    months = defaults.SLAVIC_MONTHS
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
    assert 0.60 <= defaults.CALENDAR_MOUNT_RADIUS_FRACTION <= 0.70


# --- 2. The canonical sourceless root (subdial precedent) -------------------


def test_months_root_is_outside_art_sourced_roots():
    """A mount-set plate is its OWN shared thing, not a Gemini/ChatGPT
    split — so `months/` stays out of ART_SOURCED_ROOTS, exactly like
    `subdial/`."""
    assert defaults.MONTHS_ART_DIR.name == "months"
    assert "months" not in constants.ART_SOURCED_ROOTS


def test_month_plates_are_sourceless_and_graceful_absent():
    """`paths.art_file` passes a `months/` path straight through (never
    source-qualified) and it does not exist yet — the FUTURE prompt sheet
    — so every consumer hides it, the wired-ahead contract."""
    for _cro, _gloss, stem, _m in defaults.SLAVIC_MONTHS:
        plate = defaults.MONTHS_ART_DIR / f"{stem}.png"
        assert paths.art_file(plate) == plate            # no source segment
        assert not plate.exists()                        # art is a future work


# --- 3. The Encyclopedia topic ----------------------------------------------


def test_topic_page_order_title_then_twelve():
    from app.encyclopedia import _topics

    entries = _topics(date(2026, 7, 7))["months"]["entries"]
    assert len(entries) == 13
    assert entries[0]["name"] == "The Slavic Months"
    assert entries[0]["article"] == ("emblem", "months", "The Slavic Months")
    for entry, (cro, gloss, _stem, _m) in zip(
        entries[1:], defaults.SLAVIC_MONTHS
    ):
        assert entry["name"] == f"{cro} ({gloss})"
        assert entry["article"] == ("emblem", "months", cro)


def test_topic_rides_the_celestial_engine_once():
    from app.encyclopedia import _TOPIC_GROUPS, _topics

    groups = dict(_TOPIC_GROUPS)
    assert "months" in groups["The Celestial Engine"]
    every = [k for keys in groups.values() for k in keys]
    assert every.count("months") == 1
    assert "months" in _topics()


def test_every_month_article_carries_its_web():
    """Each article names its own Croatian month, states the Gregorian
    equivalent in prose, and reads non-trivially (Rule #2 — real content,
    not a placeholder)."""
    enc = EncyclopediaRepository()
    for cro, _gloss, _stem, month in defaults.SLAVIC_MONTHS:
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
