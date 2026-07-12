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
    # The third bundled styling (owner spec 2026-07-11): every hour
    # number on its OWN position, Omega on the bottom — a seal, so one
    # metal dresses all six.
    assert presets["NUMBERS"]["layout"] == "seal"
    assert presets["NUMBERS"]["letters"] == ("12", "16", "20", "Ω", "4", "8")
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
    face and ONE metal on all six letters (owner correction): gold
    finish = everything gold, silver = everything silver."""
    card = {
        "name": "SOLOMON",
        "positions": [12, 16, 20, 24, 4, 8],
        "letters": ["S", "Ω", "Σ", "M", "Θ", "✠"],
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
    """Owner metal rule (correction 2026-07-10): the trio of one metal
    always forms a TRIANGLE — gold finish = the layout triangle in
    gold + the rest silver; silver finish = the exact inverse."""
    art_dir = defaults.RING_LETTER_ART_DIR
    gold = build_skin(Settings()).ring.letter_art
    assert gold[12] == art_dir / "M.svg"          # triangle 12/20/4 gold
    assert gold[20] == art_dir / "Y.svg"
    assert gold[4] == art_dir / "D.svg"
    assert gold[0] == art_dir / "Omega_silver.png"
    silver = build_skin(replace(Settings(), ring_finish="silver")).ring.letter_art
    assert silver[12] == art_dir / "M_silver.png"  # the triangle inverts
    assert silver[20] == art_dir / "Y_silver.png"
    assert silver[0] == art_dir / "Omega.png"      # Omega back to gold
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


def test_letter_groups_cover_the_library_exactly():
    """The builder's grouped dropdown (owner spec 2026-07-11: Latin /
    Greek / Numbers / Symbols sections) must offer every library glyph
    exactly once — and every glyph must ship BOTH its gold art and its
    pre-rendered silver twin."""
    from pathlib import Path

    from config import constants

    grouped = [
        glyph
        for glyphs in constants.RING_LETTER_GROUPS.values()
        for glyph in glyphs
    ]
    assert sorted(grouped) == sorted(constants.RING_LETTER_FILES)
    assert len(grouped) == len(set(grouped))
    assert len(constants.RING_LETTER_GROUPS["Latin"]) == 26   # the full alphabet
    for glyph, filename in constants.RING_LETTER_FILES.items():
        gold = defaults.RING_LETTER_ART_DIR / filename
        silver = (
            defaults.RING_LETTER_ART_DIR / f"{Path(filename).stem}_silver.png"
        )
        assert gold.exists(), glyph
        assert silver.exists(), glyph


def test_letter_shadow_is_a_black_silhouette():
    """Owner bug 2026-07-12: the tritone left bright GOLD pixels bright
    under the #000000 shadow tint (a red halo on the ring letters) —
    pure black must produce a SILHOUETTE: every opaque pixel black,
    alpha untouched."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
    from PySide6.QtWidgets import QApplication

    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    source = QPixmap(2, 1)
    source.fill(Qt.GlobalColor.transparent)
    painter = QPainter(source)
    painter.fillRect(0, 0, 1, 1, QColor(230, 180, 60))    # a bright gold
    painter.end()
    shadow = AssetCache._tinted(source, "#000000").toImage().convertToFormat(
        QImage.Format.Format_ARGB32
    )
    gold = shadow.pixelColor(0, 0)
    assert (gold.red(), gold.green(), gold.blue()) == (0, 0, 0)
    assert gold.alpha() == 255
    assert shadow.pixelColor(1, 0).alpha() == 0            # air stays air


def test_svg_masters_survive_flush():
    """Owner bug 2026-07-12: traced letter SVGs parse in seconds — the
    master raster must be parsed once and survive flush() (monitor/DPI
    switches), so a screen change never re-pays the parse."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    path = defaults.RING_LETTER_ART_DIR / "M.svg"
    cache = AssetCache()
    first = cache.pixmap_by_height(path, 60.0, 1.0)
    assert str(path) in AssetCache._svg_masters
    master, master_px = AssetCache._svg_masters[str(path)]
    assert master_px >= AssetCache.MASTER_MIN_PX
    cache.flush()
    assert str(path) in AssetCache._svg_masters      # the parse is kept
    again = cache.pixmap_by_height(path, 120.0, 1.0)
    assert first.height() == 60 and again.height() == 120


def test_legend_highlighting_colors_canon_terms():
    """Owner spec 2026-07-12: virtues pop bold blue, vices bold red,
    moods bold yellow — always; a COLOR word lights up only when it is
    the entity's own diamond hue (accents), so the Soldier's "red
    planet" and the Merchant's gold coins stay plain; hex notes never
    display."""
    from render.compositor import _article_body_html

    out = _article_body_html(
        "Patience heals Jealousy in green (#007E00), the mood called "
        "Renewal — the red planet pays in gold.",
        accents=("green", "cyan"),
    )
    assert "#007E00" not in out
    assert f'<b style="color:{defaults.LEGEND_VIRTUE_COLOR}">Patience</b>' in out
    assert f'<b style="color:{defaults.LEGEND_VICE_COLOR}">Jealousy</b>' in out
    assert f'<b style="color:{defaults.LEGEND_MOOD_COLOR}">Renewal</b>' in out
    assert 'style="color:#3ECC3E">green</b>' in out
    assert ">red</b>" not in out                    # not this arm's hue
    assert ">gold</b>" not in out
    sr = _article_body_html(
        "Strpljenje leči Ljubomoru, a zeleno je Obnova.",
        accents=defaults.BODY_ACCENT_HUES["saturn"],
    )
    assert f'<b style="color:{defaults.LEGEND_VIRTUE_COLOR}">Strpljenje</b>' in sr
    assert f'<b style="color:{defaults.LEGEND_VICE_COLOR}">Ljubomoru</b>' in sr
    assert f'<b style="color:{defaults.LEGEND_MOOD_COLOR}">Obnova</b>' in sr
    assert 'style="color:#3ECC3E">zeleno</b>' in sr
    # No accents (e.g. the Chinese article): color words stay plain.
    plain = _article_body_html("A green field under a red sky.")
    assert "</b>" not in plain


def test_ring_tint_is_a_tritone_map():
    """Owner spec 2026-07-11: the tint must NOT touch whites or blacks
    (ring numerals stay legible) — black -> black, white -> white, the
    exact midtone -> the tint. Checked on both twins: the pixmap
    recolor (AssetCache._tinted) and the scalar Umbra map."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
    from PySide6.QtWidgets import QApplication

    from render.assets import AssetCache
    from render.layers import tinted_gray

    QApplication.instance() or QApplication([])
    source = QPixmap(3, 1)
    painter = QPainter(source)
    painter.fillRect(0, 0, 1, 1, QColor(0, 0, 0))
    painter.fillRect(1, 0, 1, 1, QColor(128, 128, 128))
    painter.fillRect(2, 0, 1, 1, QColor(255, 255, 255))
    painter.end()
    tinted = AssetCache._tinted(source, "#007E00").toImage().convertToFormat(
        QImage.Format.Format_ARGB32
    )
    black, mid, white = (tinted.pixelColor(x, 0) for x in range(3))
    assert (black.red(), black.green(), black.blue()) == (0, 0, 0)
    assert (white.red(), white.green(), white.blue()) == (255, 255, 255)
    assert mid.green() > 100 and mid.red() < 30 and mid.blue() < 30  # ~the tint

    assert tinted_gray(0, "#007E00").getRgb()[:3] == (0, 0, 0)
    assert tinted_gray(255, "#007E00").getRgb()[:3] == (255, 255, 255)
    mid = tinted_gray(128, "#007E00")
    assert mid.green() > 100 and mid.red() < 10 and mid.blue() < 10


def test_ring_tint_flows_to_the_skin_and_the_umbra():
    """The tint reaches the built config and the Umbra render — as a
    TRITONE: the wheel's bright TOP stays white (owner spec: whites are
    untouchable), while the midtone flank reads red."""
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
    probe = (180, 108)                   # above center — a MIDTONE wheel shade
    gray = Compositor(bare, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    pixel = gray.pixelColor(*probe)
    assert abs(pixel.red() - pixel.blue()) < 12          # neutral gray
    assert 30 < pixel.red() < 225                        # a real midtone — the
                                                         # tritone must move it
    red = Compositor(
        dataclasses.replace(bare, ring_tint="#FF0000"), AssetCache()
    ).render_offscreen(360.0, 1.0, day, tick)
    pixel = red.pixelColor(*probe)
    assert pixel.red() > pixel.blue() + 60               # midtone takes the tint
    # Whites/blacks staying untouched is pinned by the tritone unit
    # test above — this test guards the skin -> Umbra plumbing.
