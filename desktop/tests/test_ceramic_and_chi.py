"""S5 — the ring rework's final wave: the ceramic finish, the CHI preset
and the per-crown-text hover law.

Covers [The Ring Rework](../research/ring_rework.md) §3-4 and
[Crown & Letter Content](../research/crown_content.md): TASK 1 (ceramic
ramp), TASK 2 (the CHI preset) and TASK 3 (every crown text answers for
itself, never the seat's letter legend — the exact reported Dollar bug).
"""

import math
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

from app.skin_builder import build_skin
from app.settings_store import Settings, replace
from config import constants, defaults, dial
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from render import letter_plates
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def july_wednesday(app):
    """2026-07-08 (a Wednesday) at noon in Belgrade — mirrors
    tests/test_pointer.py's own fixture (module-local, no shared
    conftest fixture exists for this)."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# ═══════════════════════ TASK 1 — THE CERAMIC FINISH ═══════════════════════

def test_ceramic_is_a_choosable_thematic_shade():
    """Registered in the SAME roster every other transformer ramp lives
    in (test_thematic_choices_mirror_the_recolor_presets is the sync
    against recolor/presets/metals.json's own order)."""
    assert "ceramic" in constants.METAL_SHADE_NAMES["thematic"]
    assert constants.METAL_SHADE_TITLES["ceramic"] == "Ceramic"


def test_ceramic_ramp_reads_visibly_distinct_from_silver():
    """A real letter plate (X.png, CHI's own glyph) recolored ceramic
    must differ from the same plate recolored silver — the porcelain
    ramp is cold/near-white/desaturated, not a silver re-tint (owner
    law: one formula for every image, but every image is its OWN
    ramp). "ceramic" is a THEMATIC shade (like every ring theme
    color), so it is reached the same way `test_thematic_finish_wears_
    the_preset_color` reaches "cross_red" — through the thread-local
    DisplayContext, not a bare `metal=` name."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from config import paths
    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    letter = letter_plates.plate_path("X")
    cache = AssetCache()
    with paths.display(paths.display_context(
        metal_shades={"thematic": "ceramic"}
    )):
        ceramic = cache.pixmap_by_height(
            letter, 128, 1.0, metal="thematic"
        ).toImage()
    silver = cache.pixmap_by_height(letter, 128, 1.0, metal="silver").toImage()
    assert ceramic.width() == silver.width()
    differing = sum(
        1 for x in range(0, ceramic.width(), 4)
        for y in range(0, ceramic.height(), 4)
        if ceramic.pixelColor(x, y) != silver.pixelColor(x, y)
    )
    assert differing > 0


# ═══════════════════════════ TASK 2 — THE CHI PRESET ═══════════════════════

def test_chi_preset_validates_and_locks_its_outer():
    presets = ring_presets()
    chi = presets["CHI"]
    assert chi["outer"] == "full"
    assert chi["positions"] == (24,)
    assert chi["jewels"] == ("X",)
    assert chi["thematic"] == "ceramic"
    assert chi["about"]
    assert constants.RING_OUTER_LOCK["CHI"] == "full"
    # RULED "može" (Crown Polish round, owner 2026-08-06).
    assert constants.RING_INNER_PRESET_DEFAULT["CHI"] == "simple"


def test_chi_crown_text_chars_all_drawable():
    presets = ring_presets()
    chi = presets["CHI"]
    texts = [entry["text"] for entry in chi["crown_text"]]
    assert texts == ["IXΘYΣ", "IN HOC SIGNO VINCES"]
    for text in texts:
        for char in text:
            assert char == " " or char in constants.LETTER_PLATE_FILES


def test_chi_crown_text_carries_its_own_reading():
    presets = ring_presets()
    chi = presets["CHI"]
    ixthys, ihsv = chi["crown_text"]
    assert ixthys["reading"]["title"] == "ΙΧΘΥΣ"
    assert ihsv["reading"]["title"] == "IN HOC SIGNO VINCES"


def test_chi_builds_a_skin_with_no_missing_assets():
    from skins.manifest import missing_assets

    skin = build_skin(replace(Settings(), ring="CHI"))
    assert skin.ring.jewel_art
    assert missing_assets(skin) == []


# ═══════════════ TASK 3 — EVERY CROWN TEXT SPEAKS FOR ITSELF ═══════════════

def test_dollar_crown_word_hover_answers_with_the_motto_not_the_seat_legend(
    july_wednesday,
):
    """THE reported bug: hovering ANNUIT used to narrate the Anointed
    Aegis (the A letter's own legend) instead of the Latin motto. Now
    the entry's own `reading` wins (render.compositor's THE ONE TERM
    ONE HOVER LAW). Same geometry as
    tests/test_pointer.py::test_ring_arc_words_answer_their_own_entry_reading."""
    day, tick = july_wednesday
    radius = 180.0
    band = dial.RING_CROWN_TEXT_RADIUS_FRACTION

    def point_at(theta_deg: float) -> QPointF:
        theta = math.radians(theta_deg)
        return QPointF(
            radius * band * math.sin(theta), -radius * band * math.cos(theta)
        )

    dollar = Compositor(
        build_skin(replace(Settings(), ring="Dollar")), AssetCache()
    )
    dollar.render_offscreen(360.0, 1.0, day, tick)
    annuit = dollar._tooltips._tick_tooltip(point_at(316.7), radius)
    assert annuit is not None
    assert "ANNUIT CŒPTIS" in annuit
    assert "Anointed Aegis" not in annuit


def test_every_bundled_legend_carries_its_ordinal_line():
    presets = ring_presets()
    # One representative seat per card, per research/crown_content.md §2.
    checks = [
        ("DOMY", 24, "24th and last letter of the Greek alphabet"),
        ("LOOP", 8, "8th letter of the Greek alphabet"),
        ("Dollar", 8, "1st letter of the modern Latin alphabet"),
        ("Templar", 12, "cross pattée is a symbol, not a letter"),
        ("CHI", 24, "24th letter of the modern Latin alphabet"),
    ]
    for name, position, fragment in checks:
        reading = presets[name]["legend"][position]["reading"]
        assert fragment in reading
