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
    """Owner spec (2026-07-10): the letters are GOLD masters, silver is
    desaturated at load; each preset's ACCENT letter wears the opposite
    metal — DOMY inverts its Omega, MORPH inverts its M."""
    gold = build_skin(Settings()).ring.letter_art
    assert gold[12] == (defaults.RING_LETTER_ART_DIR / "M.svg", False)
    assert gold[0] == (defaults.RING_LETTER_ART_DIR / "Omega.png", True)
    silver = build_skin(replace(Settings(), ring_finish="silver")).ring.letter_art
    assert silver[12][1] is True                 # M desaturated
    assert silver[0][1] is False                 # Omega stays gold
    morph = build_skin(replace(Settings(), ring="morph")).ring.letter_art
    assert morph[16] == (defaults.RING_LETTER_ART_DIR / "Pi.png", False)
    assert morph[8][1] is False                  # H gold
    assert morph[12][1] is True                  # MORPH gold inverts its M
    morph_silver = build_skin(
        replace(Settings(), ring="morph", ring_finish="silver")
    ).ring.letter_art
    assert morph_silver[12][1] is False          # M back to gold
    assert morph_silver[0][1] is True            # Omega desaturated


def test_silver_is_desaturated_gold(app_offscreen=None):
    """The silver look = the gold art with the saturation removed
    (owner-approved derivation): every pixel reads R=G=B, alpha kept."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    cache = AssetCache()
    silver = cache.pixmap_by_height(
        defaults.RING_LETTER_ART_DIR / "M.svg", 48.0, 1.0, desaturate=True
    ).toImage()
    seen_opaque = False
    for x in range(0, silver.width(), 5):
        for y in range(0, silver.height(), 5):
            color = silver.pixelColor(x, y)
            if color.alpha() > 0:
                seen_opaque = True
                assert color.red() == color.green() == color.blue()
    assert seen_opaque
    # Transparent surroundings STAY transparent (owner bug report: a
    # silently no-op alpha mask left the whole bounding box as an opaque
    # gray plate). Probed on the PNG letter — the current latin SVGs
    # carry a semi-opaque gold wash of their own (reported to the owner).
    omega = cache.pixmap_by_height(
        defaults.RING_LETTER_ART_DIR / "Omega.png", 48.0, 1.0, desaturate=True
    ).toImage()
    assert omega.pixelColor(0, 0).alpha() == 0


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
