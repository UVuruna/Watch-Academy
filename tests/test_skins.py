"""Ring presets and the built render config (the skin-pack system is
gone — DOMY and MORPH are ring preset names, nothing more)."""

from app.controller import build_skin
from app.settings_store import Settings, replace
from config import defaults
from skins.manifest import missing_assets


def test_ring_presets_carry_their_letters():
    """Greek-ordinal letter positions per ring (owner spec)."""
    assert defaults.RING_PRESETS["domy"]["letters"] == {12: "M", 20: "Y", 0: "Ω", 4: "D"}
    assert defaults.RING_PRESETS["morph"]["letters"] == {12: "M", 16: "Π", 8: "H", 0: "Ω"}
    for preset in defaults.RING_PRESETS.values():
        assert preset["asset"].exists()


def test_build_skin_swaps_only_the_ring():
    domy = build_skin(Settings())
    morph = build_skin(replace(Settings(), ring="morph"))
    assert domy.ring.asset.name == "domy.png"
    assert morph.ring.asset.name == "morph.png"
    assert morph.ring.letters == {12: "M", 16: "Π", 8: "H", 0: "Ω"}
    # Everything else is identical — the ring preset IS the difference.
    assert morph.hands == domy.hands
    assert morph.background == domy.background
    assert morph.weekday_set == domy.weekday_set
    assert morph.year_marker == domy.year_marker


def test_default_config_assets_all_exist():
    """Every asset the built config references ships in the repo (a miss
    would otherwise surface inside paintEvent, where Qt swallows it)."""
    assert missing_assets(build_skin(Settings())) == []
    assert missing_assets(build_skin(replace(Settings(), ring="morph"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), weekday_theme="norse", earth_style="atmo"))
    ) == []
    assert missing_assets(build_skin(replace(Settings(), ring_finish="silver"))) == []


def test_letter_art_follows_the_finish():
    """Owner spec: gold = M/D/Y/P/H gold with a silver Omega; silver =
    the inverse. The Omega always wears the OTHER metal."""
    gold = build_skin(Settings()).ring.letter_art
    assert gold[12].name == "M_gold.png"
    assert gold[0].name == "Omega_silver.png"
    silver = build_skin(replace(Settings(), ring_finish="silver")).ring.letter_art
    assert silver[12].name == "M_silver.png"
    assert silver[0].name == "Omega_gold.png"
    morph = build_skin(replace(Settings(), ring="morph")).ring.letter_art
    assert morph[16].name == "P_gold.png"       # Π maps to the P file
    assert morph[8].name == "H_gold.png"


def test_ring_tint_flows_to_the_skin_and_the_umbra():
    """The tint reaches the built config and the Umbra render: with a
    pure red tint the wheel's bright top reads red, not gray."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import dataclasses
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral
    from PySide6.QtWidgets import QApplication

    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    QApplication.instance() or QApplication([])
    assert build_skin(replace(Settings(), ring_tint="#FF0000")).ring_tint == "#FF0000"

    city = defaults.DEFAULT_CITY
    now = datetime(2026, 7, 8, 12, 0, tzinfo=ZoneInfo(city["timezone"]))
    day = build_day_context(
        now,
        astral.Observer(latitude=city["latitude"], longitude=city["longitude"]),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    bare = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        colorful=False, show_pointer=False, show_weekday=False,
        show_earth=False, show_moon=False,
    )
    probe = (180, 108)                   # above center — the Umbra's bright top
    gray = Compositor(bare, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    pixel = gray.pixelColor(*probe)
    assert abs(pixel.red() - pixel.blue()) < 12          # neutral gray
    red = Compositor(
        dataclasses.replace(bare, ring_tint="#FF0000"), AssetCache()
    ).render_offscreen(360.0, 1.0, day, tick)
    pixel = red.pixelColor(*probe)
    assert pixel.red() > pixel.blue() + 60               # tinted wheel
