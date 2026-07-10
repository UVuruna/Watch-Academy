"""Ring presets and the built render config (the skin-pack system is
gone — DOMY and MORPH are ring preset names, nothing more)."""

from app.controller import build_skin
from app.settings_store import Settings, replace
from config import defaults
from skins.manifest import missing_assets


def test_ring_preset_cards_load_and_validate():
    """The bundled cards (owner spec: {name, positions, letters}) load
    with their layouts resolved by the positions signature; a broken
    card names itself loudly."""
    import pytest

    from config import constants
    from data.rings import ring_presets, validate_preset

    presets = ring_presets()
    assert presets["DOMY"]["layout"] == "flame"
    assert presets["DOMY"]["letters"] == ("M", "Y", "Ω", "D")
    assert presets["MORPH"]["layout"] == "chalice"
    for layout in constants.RING_LAYOUTS.values():
        assert (defaults.RING_FACE_DIR / layout["face"]).exists()
    with pytest.raises(ValueError):
        validate_preset({"name": "BAD", "positions": [1, 2], "letters": ["M"]})
    with pytest.raises(ValueError):
        validate_preset(
            {"name": "BAD", "positions": [12, 20, 24, 4],
             "letters": ["M", "Y", "Ω", "š"]}
        )


def test_build_skin_swaps_only_the_ring():
    domy = build_skin(Settings())
    morph = build_skin(replace(Settings(), ring="MORPH"))
    assert domy.ring.asset.name == "domy.png"
    assert morph.ring.asset.name == "morph.png"
    assert morph.ring.letters == {12: "M", 16: "Π", 8: "H", 0: "Ω"}
    # Everything else is identical — the ring preset IS the difference.
    assert morph.hands == domy.hands
    assert morph.background == domy.background
    assert morph.weekday_set == domy.weekday_set
    assert morph.year_marker == domy.year_marker


def test_custom_ring_card_builds_a_seal():
    """A user card with the six-position signature gets the hexagram
    face and one metal for all six letters (owner rules)."""
    card = {
        "name": "SOLOMON",
        "positions": [12, 16, 20, 24, 4, 8],
        "letters": ["S", "Ω", "Σ", "M", "Θ", "Ψ"],
    }
    skin = build_skin(
        replace(Settings(), ring="SOLOMON", custom_rings=(card,))
    )
    assert skin.ring.asset.name == "hexagram.png"
    assert len(skin.ring.letter_art) == 6
    assert all(
        not path.name.endswith("_silver.png")
        for path in skin.ring.letter_art.values()
    )
    silver = build_skin(
        replace(
            Settings(), ring="SOLOMON", ring_finish="silver",
            custom_rings=(card,),
        )
    )
    assert all(
        path.name.endswith("_silver.png")
        for path in silver.ring.letter_art.values()
    )
    assert missing_assets(silver) == []


def test_default_config_assets_all_exist():
    """Every asset the built config references ships in the repo (a miss
    would otherwise surface inside paintEvent, where Qt swallows it)."""
    assert missing_assets(build_skin(Settings())) == []
    assert missing_assets(build_skin(replace(Settings(), ring="MORPH"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), weekday_theme="norse", earth_style="atmo"))
    ) == []
    assert missing_assets(build_skin(replace(Settings(), ring_finish="silver"))) == []


def test_letter_art_follows_the_finish():
    """Owner metal rules (2026-07-10): GOLD puts the layout triangle's
    three letters in gold and the remaining one in silver; SILVER puts
    the 12h letter in gold and the rest in silver. Silver letters are
    pre-rendered files."""
    art_dir = defaults.RING_LETTER_ART_DIR
    gold = build_skin(Settings()).ring.letter_art
    assert gold[12] == art_dir / "M.svg"          # triangle 12/20/4 gold
    assert gold[20] == art_dir / "Y.svg"
    assert gold[4] == art_dir / "D.svg"
    assert gold[0] == art_dir / "Omega_silver.png"
    silver = build_skin(replace(Settings(), ring_finish="silver")).ring.letter_art
    assert silver[12] == art_dir / "M.svg"        # the 12h letter stays gold
    assert silver[20] == art_dir / "Y_silver.png"
    assert silver[0] == art_dir / "Omega_silver.png"
    morph = build_skin(replace(Settings(), ring="MORPH")).ring.letter_art
    assert morph[16] == art_dir / "Pi.png"        # triangle 8/16/24 gold
    assert morph[0] == art_dir / "Omega.png"
    assert morph[12] == art_dir / "M_silver.png"
    morph_silver = build_skin(
        replace(Settings(), ring="MORPH", ring_finish="silver")
    ).ring.letter_art
    assert morph_silver[12] == art_dir / "M.svg"
    assert morph_silver[0] == art_dir / "Omega_silver.png"


def test_pre_rendered_silver_letters_are_grayscale():
    """The generated silver files exist for every active letter, read
    R=G=B on opaque pixels and keep their surroundings transparent."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    from config import constants

    QApplication.instance() or QApplication([])
    for filename in constants.RING_LETTER_FILES.values():
        stem = filename.rsplit(".", 1)[0]
        path = defaults.RING_LETTER_ART_DIR / f"{stem}_silver.png"
        assert path.exists(), path
        image = QImage(str(path))
        seen_opaque = False
        for x in range(0, image.width(), 25):
            for y in range(0, image.height(), 25):
                color = image.pixelColor(x, y)
                if color.alpha() > 200:
                    seen_opaque = True
                    assert color.red() == color.green() == color.blue(), path
        assert seen_opaque, path
    omega = QImage(str(defaults.RING_LETTER_ART_DIR / "Omega_silver.png"))
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
