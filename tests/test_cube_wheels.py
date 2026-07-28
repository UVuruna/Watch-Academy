"""The Cube wheels engine (WORKPLAN Session 20; owner seal 2026-07-26,
CUBE.md): the third-wheel slot (Genesis / Council / Character), the
Genesis inversion and the Diamond/Cube display toggle — every sealed
behavior pinned golden.

The Rose's goldens left this file on 2026-07-27: they pinned a RING
preset that should never have been built (CUBE.md had mis-transcribed
the owner's POINTER spec). The Rose pointer has its own suite,
`tests/test_rose_pointer.py`.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import archetypes, constants, defaults
from app.controller import apply_display_settings, build_skin, watch_title
from app.settings_store import Settings
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    arm_half_deg,
    arm_offset_deg,
    archetype_key,
    archetype_lit_index,
    cube_look_active,
    palette_for,
    today_slot_theta,
    weekday_slots,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _skin(pointer: str, style: str = "tertiary", **kw):
    return dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer=pointer, palette_style=style,
        solar_rotation=False, **kw,
    )


def _dt(when: datetime):
    city = defaults.DEFAULT_CITY
    now = when.replace(tzinfo=ZoneInfo(city["timezone"]))
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# --- The third-wheel slot ----------------------------------------------------------


def test_cube_styles_exist_only_on_the_cube_pointers():
    """CUBE.md: Genesis (trio), Council (hexa), Character (octa) — the
    Seasons, Aurora and the Calendar stay two-wheel."""
    assert constants.PALETTE_STYLES == ("primary", "secondary", "tertiary")
    for pointer in ("trio", "hexa", "octa"):
        assert constants.palette_styles_for(pointer) == (
            "primary", "secondary", "tertiary"
        )
    for pointer in ("cross", "aurora", "calendar"):
        assert constants.palette_styles_for(pointer) == ("primary", "secondary")


def test_third_wheel_labels_are_the_sealed_names():
    assert constants.POINTER_PALETTE_LABELS["trio"] == (
        "Court", "Family", "Genesis"
    )
    assert constants.POINTER_PALETTE_LABELS["hexa"][2] == "Council"
    assert constants.POINTER_PALETTE_LABELS["octa"][2] == "Character"


def test_effective_palette_style_normalizes_the_third_wheel_off_its_pointers():
    """A stored "tertiary" left behind by a pointer switch reads as
    "primary" on the two-wheel pointers — and survives on the
    three-wheel ones."""
    for pointer in ("trio", "hexa", "octa"):
        assert defaults.effective_palette_style(pointer, "tertiary") == "tertiary"
    for pointer in ("cross", "aurora", "calendar"):
        assert defaults.effective_palette_style(pointer, "tertiary") == "primary"
    assert defaults.effective_palette_style("cross", "secondary") == "secondary"


def test_apply_display_settings_normalizes_a_stray_cube_style():
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        dataclasses.replace(
            Settings(), pointer="cross", palette_style="tertiary"
        ),
    )
    assert skin.palette_style == "primary"
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        dataclasses.replace(
            Settings(), pointer="trio", palette_style="tertiary"
        ),
    )
    assert skin.palette_style == "tertiary"


def test_watch_title_names_the_cube_wheels():
    settings = dataclasses.replace(
        Settings(), pointer="trio", palette_style="tertiary", ring="DOMY",
    )
    assert watch_title(settings, full=True) == (
        "Belgrade-Gold DOMY-Genesis Trinity"
    )


def test_grid_seats_the_three_cube_archetypes():
    genesis = _skin("trio", archetype_mode=True)
    council = _skin("hexa", archetype_mode=True)
    character = _skin("octa", archetype_mode=True)
    assert archetype_key(genesis) == "trinity_genesis"
    assert archetype_key(council) == "prism_council"
    assert archetype_key(character) == "compass_character"


# --- The sealed palettes -----------------------------------------------------------


def test_genesis_palette_is_the_inverted_creation_trio():
    """CUBE.md + genesis sheet: 24h the moon-gray violet (the
    Purple-Gray hue law — NEVER royal purple), 08h the dial's green,
    16h the dial's orange; tuple order follows the drawn arms."""
    assert defaults.PALETTE_PRESETS[("trio", "tertiary")] == (
        "#666699", "#007E00", "#DC9600"
    )


def test_council_palette_wears_the_moon_gray_creator_arm():
    """Council sheet: the hexa primary wheel with the 24h arm re-dressed
    to the Rose's violet (the Purple-Gray hue law, SEALED)."""
    council = defaults.PALETTE_PRESETS[("hexa", "tertiary")]
    assert council == (
        "#F8E600", "#DC9600", "#B60000", "#666699", "#002FFF", "#007E00",
    )
    assert council[3] == defaults.MOON_GRAY_VIOLET


def test_character_palette_is_the_rose_as_drawn():
    """The color law (owner seal): the palette stays EXACTLY as the
    Rose is drawn — poles yellow/red/moon-purple/BLUE (the Scale's own
    Judas–Lucifer axis), blends green/orange/pink/cyan — and ONE tuple
    rules both the Character wheel and the Rose (Rule #5)."""
    assert defaults.PALETTE_PRESETS[("octa", "tertiary")] is defaults.ROSE_PALETTE
    assert defaults.ROSE_PALETTE == (
        "#FCEE21", "#F7931E", "#F03232", "#FF7BAC",
        "#666699", "#29ABE2", "#0078DC", "#39B54A",
    )
    assert palette_for(_skin("octa")) == defaults.ROSE_PALETTE


# --- The Genesis inversion ---------------------------------------------------------


def test_genesis_offset_holds_only_on_the_trio_cube_wheel():
    assert arm_offset_deg(_skin("trio")) == 180.0
    assert arm_offset_deg(_skin("trio", "primary")) == 0.0
    assert arm_offset_deg(_skin("trio", "secondary")) == 0.0
    assert arm_offset_deg(_skin("hexa")) == 0.0
    assert arm_offset_deg(_skin("octa")) == 0.0


def test_genesis_figures_sit_on_the_inverted_arms():
    """CUBE.md: God—Creator 24h, Jesus—Preserver 08h, the
    Devil—Destroyer 16h; the tuple index stays the hour-space index
    under the 180° offset. THE MANY-NAMES DOCTRINE: this wheel says
    God where the Court says The One."""
    figs = archetypes.figures("trinity_genesis")
    assert [(f["angle"], f["name"], f["row2"]) for f in figs] == [
        (180.0, "God", "Creator"),
        (300.0, "Jesus", "Preserver"),
        (60.0, "The Devil", "Destroyer"),
    ]
    court = archetypes.figures("trinity_primary")
    assert court[0]["name"] == "The One"      # the names stay layered


def test_genesis_lit_index_counts_from_the_creator_arm():
    """The hour-space math rides the drawn arms: with the 180° offset
    the hour hand at the bottom lights God—Creator (index 0), at 16h
    the Destroyer (index 2), at 08h the Preserver (index 1)."""
    assert archetype_lit_index("trio", 180.0, 0.0, 180.0) == 0
    assert archetype_lit_index("trio", 60.0, 0.0, 180.0) == 2
    assert archetype_lit_index("trio", 300.0, 0.0, 180.0) == 1
    # The Court keeps its own spaces (no offset).
    assert archetype_lit_index("trio", 0.0, 0.0) == 0


def test_genesis_weekday_slots_ride_the_inverted_arms():
    """Pure geometry (no re-pairing doctrine invented): each occupant
    pair stays glued to its arm as the wheel swings 180°."""
    slots = dict(weekday_slots(_skin("trio")))
    assert slots == {
        180.0: ("jupiter", "saturn"),
        300.0: ("venus", "mars"),
        60.0: ("moon", "mercury"),
    }
    # Every other wheel reads the table untouched.
    assert weekday_slots(_skin("trio", "primary")) == (
        constants.POINTER_WEEKDAY_SLOTS["trio"]
    )
    assert today_slot_theta(_skin("trio"), "jupiter") == 180.0
    assert today_slot_theta(_skin("trio"), "sun") is None


def test_council_offices_seat_the_double_trinity():
    """Council sheet: Judge 12h, Destroyer 16h, Prosecutor 20h,
    Creator 24h, Advocate 04h, Preserver 08h — three persons, six
    seats, in hour-space order."""
    figs = archetypes.figures("prism_council")
    assert [(f["name"], f["row2"]) for f in figs] == [
        ("God", "Judge"), ("The Devil", "Destroyer"),
        ("The Devil", "Prosecutor"), ("God", "Creator"),
        ("Jesus", "Advocate"), ("Jesus", "Preserver"),
    ]
    assert archetypes.center("prism_council")["name"] == "The Lord's Day"


def test_character_directions_carry_their_falls():
    """CUBE.md §Character Wheel: 4 poles + 4 combos, each row-2 the
    direction's own fall — the same virtue walked past its measure."""
    figs = archetypes.figures("compass_character")
    assert [(f["name"], f["row2"]) for f in figs] == [
        ("Loyalty", "Tribalism"), ("Patronage", "Favoritism"),
        ("Dignity", "Self-Worship"), ("Conviction", "Dogmatism"),
        ("Integrity", "Legalism"), ("Renunciation", "Mortification"),
        ("Humility", "Self-Annihilation"), ("Devotion", "Martyrdom"),
    ]


def test_genesis_arm_hover_speaks_the_office(app):
    """The plain (non-archetype) Genesis arm hover names its creation
    office and carries the pending line until Session 21's articles
    land — never a KeyError on the inverted angles."""
    day, tick = _dt(datetime(2026, 7, 16, 14, 30))
    comp = Compositor(_skin("trio"), AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    from render.layers import dial_point

    pos = dial_point(180.0, 180.0 * 0.86 * 0.82)     # the 24h arm
    tooltip = comp.tooltip_at(180.0 + pos.x(), 180.0 + pos.y(), 360.0)
    assert tooltip is not None
    assert "Creator" in tooltip and "God" in tooltip
    assert archetypes.ARCHETYPE_PENDING_LINE in tooltip
    # The Spacebar jump stays silent here until the Cube pages exist.
    assert comp.encyclopedia_target(
        180.0 + pos.x(), 180.0 + pos.y(), 360.0
    ) is None


def test_genesis_renders_offscreen_in_archetype_mode(app):
    day, tick = _dt(datetime(2026, 7, 16, 12, 0))
    comp = Compositor(_skin("trio", archetype_mode=True), AssetCache())
    image = comp.render_offscreen(360.0, 1.0, day, tick)
    assert not image.isNull()


# --- The Diamond/Cube display toggle -----------------------------------------------


def test_cube_look_gates_on_the_double_trinity_family():
    """CUBE.md §Display laws: the toggle dresses the Court, Genesis
    and the Council — and nothing else."""
    for pointer, style in (("trio", "primary"), ("trio", "tertiary"),
                           ("hexa", "tertiary")):
        assert cube_look_active(_skin(pointer, style, cube_look=True))
        assert not cube_look_active(_skin(pointer, style))  # toggle off
    for pointer, style in (("trio", "secondary"), ("hexa", "primary"),
                           ("hexa", "secondary"), ("octa", "tertiary"),
                           ("cross", "primary")):
        assert not cube_look_active(_skin(pointer, style, cube_look=True))
    # No pointer drawn — no cube to dress.
    assert not cube_look_active(
        _skin("trio", "primary", cube_look=True, show_pointer=False)
    )


def test_cube_look_widens_the_arms_to_the_tiling_rhombi():
    """The corner-view faces are the regular 180/N halves — the trio's
    three rhombi and the Council's six tile the hexagon exactly; the
    Diamond look keeps the slim owner values."""
    assert arm_half_deg(_skin("trio", "primary", cube_look=True)) == 60.0
    assert arm_half_deg(_skin("trio", "tertiary", cube_look=True)) == 60.0
    assert arm_half_deg(_skin("hexa", "tertiary", cube_look=True)) == 30.0
    assert arm_half_deg(_skin("trio", "primary")) == 30.0
    assert arm_half_deg(_skin("octa", "tertiary", cube_look=True)) == 22.5
    assert arm_half_deg(_skin("cross", "primary", cube_look=True)) == 22.5


def test_settings_store_round_trips_the_cube_choices(tmp_path):
    from app.settings_store import SettingsStore

    store = SettingsStore(tmp_path / "settings.json")
    store.save(dataclasses.replace(
        Settings(), palette_style="tertiary", cube_look=True,
    ))
    loaded = SettingsStore(tmp_path / "settings.json").load()
    assert loaded.palette_style == "tertiary"
    assert loaded.cube_look is True

