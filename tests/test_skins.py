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


def test_mason_g_preset_loads_and_splits_metal():
    """The MASON G bundled preset (ROADMAP 15b, CANON.md §The Banknote):
    G(12) S(16) M(20) Ω(24) N(4) A(8) on the seal layout, splitting the
    metal into the Trinity triangle (12/20/4 = G,M,N) wearing the chosen
    finish and the Union triangle (16/24/8 = S,Ω,A) wearing its counter-
    metal — NOT the NUMBERS-style single finish on all six, because this
    preset carries its own `triangle` override."""
    from data.rings import ring_presets

    presets = ring_presets()
    mason = presets["MASON G"]
    assert mason["layout"] == "seal"
    assert mason["positions"] == (12, 16, 20, 24, 4, 8)
    assert mason["letters"] == ("G", "S", "M", "Ω", "N", "A")
    assert mason["triangle"] == (12, 20, 4)
    assert set(mason["legend"]) == {12, 16, 20, 24, 4, 8}

    art_dir = defaults.RING_LETTER_ART_DIR
    gold = build_skin(replace(Settings(), ring="MASON G")).ring.letter_art
    # Trinity (12/20/4 = G, M, N) wears the finish metal (gold, no suffix).
    assert gold[12] == art_dir / "G.png"
    assert gold[20] == art_dir / "M.png"
    assert gold[4] == art_dir / "N.png"
    # Union (16/24/8 = S, Ω, A) wears the counter-metal (silver here).
    assert gold[16] == art_dir / "S_silver.png"
    assert gold[0] == art_dir / "Omega_silver.png"       # 24h -> hour 0
    assert gold[8] == art_dir / "A_silver.png"

    silver = build_skin(
        replace(Settings(), ring="MASON G", ring_finish="silver")
    ).ring.letter_art
    assert silver[12] == art_dir / "G_silver.png"
    assert silver[20] == art_dir / "M_silver.png"
    assert silver[4] == art_dir / "N_silver.png"
    assert silver[16] == art_dir / "S.png"
    assert silver[0] == art_dir / "Omega.png"
    assert silver[8] == art_dir / "A.png"

    assert missing_assets(build_skin(replace(Settings(), ring="MASON G"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="MASON G", ring_finish="silver"))
    ) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="MASON G", ring_finish="bronze"))
    ) == []

    # NUMBERS keeps its own plain reading — untouched by the new override
    # machinery (no `triangle` key on its card).
    numbers = build_skin(replace(Settings(), ring="NUMBERS")).ring.letter_art
    assert all(
        not name.endswith(("_silver.png", "_bronze.png"))
        for name in (p.name for p in numbers.values())
    )


def test_ring_preset_triangle_override_validation():
    """A `triangle` override only makes sense on the seal (6-position)
    layout, and must be exactly 3 of the preset's own positions."""
    import pytest

    from data.rings import validate_preset

    with pytest.raises(ValueError):
        # DOMY's own 4-position signature -> flame layout, not seal.
        validate_preset({
            "name": "BAD", "positions": [12, 20, 24, 4],
            "letters": ["G", "M", "Ω", "N"], "triangle": [12, 20, 4],
        })
    with pytest.raises(ValueError):
        validate_preset({
            "name": "BAD", "positions": [12, 16, 20, 24, 4, 8],
            "letters": ["G", "S", "M", "Ω", "N", "A"],
            "triangle": [12, 20],  # only 2 positions
        })
    with pytest.raises(ValueError):
        validate_preset({
            "name": "BAD", "positions": [12, 16, 20, 24, 4, 8],
            "letters": ["G", "S", "M", "Ω", "N", "A"],
            "triangle": [12, 20, 99],  # 99 is not one of its positions
        })


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
    assert gold[12] == art_dir / "M.png"          # triangle 12/20/4 gold
    assert gold[20] == art_dir / "Y.png"
    assert gold[4] == art_dir / "D.png"
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
    assert morph_silver[12] == art_dir / "M.png"
    assert morph_silver[0] == art_dir / "Omega_silver.png"


def test_bronze_finish_and_theme_metals():
    """Owner 2026-07-12: (1) BRONZE ring finish — the triangle wears
    bronze, the accent letter silver, the Seal all six bronze, and the
    pre-rendered bronze files exist for every glyph; (2) the bronze-
    plate weekday themes wear the chosen METAL as a render tint —
    gold/silver tritone, bronze = the art as drawn; follow-the-ring
    maps the ring finish onto them; full-color themes never tint."""
    art_dir = defaults.RING_LETTER_ART_DIR
    bronze = build_skin(replace(Settings(), ring_finish="bronze")).ring.letter_art
    assert bronze[12] == art_dir / "M_bronze.png"   # triangle 12/20/4 bronze
    assert bronze[4] == art_dir / "D_bronze.png"
    assert bronze[0] == art_dir / "Omega_silver.png"  # accent stays silver
    assert missing_assets(build_skin(replace(Settings(), ring_finish="bronze"))) == []
    from config import constants as c

    for filename in c.RING_LETTER_FILES.values():
        stem = filename.rsplit(".", 1)[0]
        assert (art_dir / f"{stem}_bronze.png").exists(), stem
    seal = {
        "name": "SEALB", "positions": [4, 8, 12, 16, 20, 24],
        "letters": ["S", "O", "L", "M", "N", "A"],
    }
    seal_art = build_skin(replace(
        Settings(), ring="SEALB", ring_finish="bronze", custom_rings=(seal,),
    )).ring.letter_art
    assert all(p.name.endswith("_bronze.png") for p in seal_art.values())
    # Theme metals: explicit choice, the bronze rest state, follow-ring.
    gold_greek = build_skin(replace(
        Settings(), weekday_theme="greek", theme_metals={"greek": "gold"},
    )).weekday_set
    assert gold_greek.metal == "gold"
    plain_greek = build_skin(replace(Settings(), weekday_theme="greek")).weekday_set
    assert plain_greek.metal is None                 # bronze = as drawn
    follow = build_skin(replace(
        Settings(), weekday_theme="norse", ring_finish="silver",
        theme_metals={"norse": "gold"}, theme_metal_follow_ring=True,
    )).weekday_set
    assert follow.metal == "silver"
    colorful = build_skin(replace(
        Settings(), weekday_theme="egypt", theme_metal_follow_ring=True,
        ring_finish="gold",
    )).weekday_set
    assert colorful.metal is None                    # full-color theme
    # COLORED (owner 2026-07-12): fresh full-color badges from the
    # theme's colored/ subfolder — no swap; the whole set exists for
    # every metal-capable theme, plus the 12 colored Chinese badges.
    colored = build_skin(replace(
        Settings(), weekday_theme="greek", theme_metals={"greek": "colored"},
    )).weekday_set
    assert colored.metal is None
    assert "colored" in str(colored.bodies["jupiter"])
    # Canonical paths resolve through the ART SOURCE (owner 2026-07-14).
    from config import paths as _paths

    assert all(
        _paths.art_file(path).exists()
        for path in colored.bodies.values()
    )
    for theme in c.METAL_THEMES:
        if "colored" not in c.theme_metals(theme):
            # planets_art (owner 2026-07-18): bronze medallions with NO
            # colored/ subfolder — offering "Colored" for it would
            # dangle on a missing asset, so it is excluded up front.
            continue
        # colored is the variant SIBLING (owner restructure 2026-07-14).
        folder = (
            defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        ).parent / "colored"
        for body in c.WEEKDAY_BODIES:
            stem = defaults.WEEKDAY_THEME_FILES[theme][body]
            assert _paths.art_file(
                folder / f"{stem}.png"
            ).exists(), (theme, body)
    # planets_art itself DOES ship gold/bronze/silver (owner 2026-07-18):
    # the render-chain gate is METAL_THEMES membership + _theme_metal —
    # confirm the tint actually reaches the theme's WeekdaySpec.
    gold_planets_art = build_skin(replace(
        Settings(), weekday_theme="planets_art",
        theme_metals={"planets_art": "gold"},
    )).weekday_set
    assert gold_planets_art.metal == "gold"
    plain_planets_art = build_skin(replace(
        Settings(), weekday_theme="planets_art",
    )).weekday_set
    assert plain_planets_art.metal is None            # bronze = as drawn
    assert c.theme_metals("planets_art") == ("gold", "bronze", "silver")
    assert "colored" not in c.theme_metals("planets_art")
    for animal in c.CHINESE_ANIMALS:
        assert _paths.art_file(
            defaults.ZODIAC_ART_DIR / "chinese" / "colored" / f"{animal}.png"
        ).exists(), animal
    for sign, _ in c.ZODIAC_SIGNS:
        assert _paths.art_file(
            defaults.ZODIAC_ART_DIR / "astrology" / "colored" / f"{sign}.png"
        ).exists(), sign
    # The hue-SELECTIVE swap (owner insight 2026-07-12): warm bronze
    # pixels take the target metal, gray pixels stay untouched.
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor, QPixmap
    from PySide6.QtWidgets import QApplication

    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    probe = QPixmap(2, 1)
    probe.fill(QColor("#B08050"))                    # warm bronze
    image = probe.toImage()
    image.setPixelColor(1, 0, QColor("#808080"))     # neutral gray
    swapped = AssetCache._metal_swapped(
        QPixmap.fromImage(image), "silver"
    ).toImage()
    bronze_out = swapped.pixelColor(0, 0)
    gray_out = swapped.pixelColor(1, 0)
    assert bronze_out.saturationF() < 0.15           # bronze went silver
    assert gray_out == QColor("#808080")             # gray untouched


def test_planets_art_body_renders_differently_by_metal():
    """Render-chain confirmation (owner 2026-07-18): the real
    planets/art/sun.png plate — a bronze medallion like the pantheon
    sets — must actually come out of AssetCache looking different
    under gold vs bronze, not just carry a different metal LABEL."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from config import paths as _paths
    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    sun = (
        defaults.WEEKDAY_ART_DIR
        / defaults.WEEKDAY_THEME_DIRS["planets_art"] / "sun.png"
    )
    assert _paths.art_file(sun).exists()
    cache = AssetCache()
    bronze = cache.pixmap_by_height(sun, 128, 1.0, metal=None).toImage()
    gold = cache.pixmap_by_height(sun, 128, 1.0, metal="gold").toImage()
    silver = cache.pixmap_by_height(sun, 128, 1.0, metal="silver").toImage()
    assert bronze.width() == gold.width() == silver.width()
    differing_gold = sum(
        1 for x in range(0, bronze.width(), 4)
        for y in range(0, bronze.height(), 4)
        if bronze.pixelColor(x, y) != gold.pixelColor(x, y)
    )
    differing_silver = sum(
        1 for x in range(0, bronze.width(), 4)
        for y in range(0, bronze.height(), 4)
        if bronze.pixelColor(x, y) != silver.pixelColor(x, y)
    )
    assert differing_gold > 0
    assert differing_silver > 0


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


def test_earth_marker_follows_the_location_continent():
    """Owner bug 2026-07-12: the Earth marker was pinned to Europe —
    the picked continent decides (Americas splits by SUBREGION: owner
    rule — Central America and the Caribbean wear the north art), and
    hand-tuned coordinates fall back to a coarse estimate."""
    def variant(**kwargs):
        return build_skin(replace(Settings(), **kwargs)).year_marker.default_variant

    assert variant() == "europe"                        # Belgrade default
    assert variant(
        city_path=("Oceania", "Australia and New Zealand", "Australia", "Sydney"),
        latitude=-33.87, longitude=151.21,
    ) == "oceania"
    assert variant(
        city_path=("Americas", "Northern America", "United States", "New York"),
        latitude=40.7, longitude=-74.0,
    ) == "north_america"
    assert variant(
        city_path=("Americas", "Caribbean", "Jamaica", "Kingston"),
        latitude=18.0, longitude=-76.8,
    ) == "north_america"                                # owner rule
    assert variant(
        city_path=("Americas", "South America", "Brazil", "Rio de Janeiro"),
        latitude=-22.9, longitude=-43.2,
    ) == "south_america"
    # No picked city: the geographic fallback.
    assert variant(city_path=(), latitude=35.7, longitude=139.7) == "asia"
    assert variant(city_path=(), latitude=-1.3, longitude=36.8) == "africa"


def test_earth_pole_regions_full_res_and_latitude_override():
    """Owner 2026-07-15 (the Globe originals round): the pole views
    exist in ALL FOUR variants and the marker swaps to them at extreme
    latitudes — the latitude rides the DAY CONTEXT, so the pole Quick
    Jumps see the pole even though the settings still name a
    continent. Every earth face is his full-resolution original."""
    from PySide6.QtGui import QImageReader

    from render.layers import earth_region

    # The full 32-variant table exists at full resolution.
    for style in ("clean", "atmo"):
        for region in (
            "europe", "north_america", "south_america", "africa",
            "asia", "oceania", "north_pole", "south_pole",
        ):
            for phase in ("day", "night"):
                key = f"{style}_{region}_{phase}"
                path = defaults.DEFAULT_SKIN.year_marker.variants[key]
                assert path.exists(), key
                size = QImageReader(str(path)).size()
                assert size.width() >= 1500, (key, size.width())
    # The latitude override: poles beyond the knob, continents inside.
    assert earth_region(89.99, "europe") == "north_pole"
    assert earth_region(-89.99, "europe") == "south_pole"
    assert earth_region(defaults.EARTH_POLE_LATITUDE, "asia") == "north_pole"
    assert earth_region(69.65, "europe") == "europe"      # Tromsø stays
    assert earth_region(44.82, "europe") == "europe"


def test_working_set_downscales_oversized_dial_art():
    """Owner 2026-07-15: the originals ship full-res, the WORKING SET
    serves the dial — the warmup builds a downscaled copy per
    oversized source (idempotent: a warm second run builds nothing),
    the ceiling follows the assets subtree, and trees the dial never
    draws stay untouched."""
    from pathlib import Path

    from config import paths
    from render.assets import (
        scaled_variant_file,
        warm_working_set,
        working_ceiling,
    )

    assets = paths.assets_dir()
    assert working_ceiling(
        assets / "earth" / "earth_clean_europe_day.png"
    ) == 800
    assert working_ceiling(assets / "weekday" / "x.png") == 800
    assert working_ceiling(assets / "zodiac" / "x.png") == 1200
    assert working_ceiling(assets / "guide" / "x.png") is None
    assert working_ceiling(Path("C:/elsewhere/x.png")) is None
    warm_working_set()
    # Warm: the earth originals (1992 px) wear 800-wide copies…
    copy = scaled_variant_file(
        assets / "earth" / "earth_clean_north_pole_day.png", 800
    )
    assert copy is not None and copy.exists()
    assert copy.name.endswith("_earth_clean_north_pole_day.png")
    # …and a second run rebuilds nothing.
    assert warm_working_set() == 0


def test_hand_packs_load_and_resolve():
    """Owner spec 2026-07-12: hand PACKS (folder + hands.json). The
    bundled CLASSIC and STEEL load, pivots flow into the skin, and the
    classic sizing stays pinned (minute tip 0.849R, hour at the pack's
    own 225/275 ratio -> 0.695R)."""
    from data.hands import hand_packs

    packs = hand_packs()
    assert {"CLASSIC", "STEEL"} <= set(packs)
    assert packs["STEEL"]["pivots"]["seconds"] == (None, 310.0)
    # STEEL is the install default (owner list 2026-07-12).
    steel = build_skin(Settings()).hands
    assert "steel" in str(steel.hour.asset)
    assert steel.second.pivot_y == 310.0
    assert steel.second.natural_height == 1040.0
    assert steel.desaturate is False               # bundled art stays as drawn
    assert steel.z_order == ("hours", "minutes", "seconds")
    classic = build_skin(replace(Settings(), hands="CLASSIC")).hands
    hour_tip = classic.hour.natural_height - classic.hour.pivot_y
    minute_tip = classic.minute.natural_height - classic.minute.pivot_y
    reach = classic.minute_reach_fraction * hour_tip / minute_tip
    assert abs(reach - 0.695) < 0.005
    # A vanished pack name falls back to CLASSIC (documented) instead
    # of bricking the startup.
    gone = build_skin(replace(Settings(), hands="NO-SUCH-PACK")).hands
    assert gone.hour.asset == classic.hour.asset


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
    path = defaults.LOGO_ASSET                       # the last SVG in the app
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
    # LOWERCASE canon mentions burn too (owner report 2026-07-12), the
    # -šću instrumentals included.
    lower = _article_body_html(
        "njegov porok je gordost, a vrlina poniznost — gordošću pada"
    )
    assert f'<b style="color:{defaults.LEGEND_VICE_COLOR}">gordost</b>' in lower
    assert f'<b style="color:{defaults.LEGEND_VIRTUE_COLOR}">poniznost</b>' in lower
    assert f'<b style="color:{defaults.LEGEND_VICE_COLOR}">gordošću</b>' in lower
    # No accents (e.g. the Chinese article): color words stay plain.
    plain = _article_body_html("A green field under a red sky.")
    assert "</b>" not in plain


def test_subhead_markers_render_as_translated_headings():
    """RUNDA D (owner plan 2026-07-14): a [[Marker]] paragraph prefix
    becomes a bold left-aligned heading translated through the ui
    catalog; the marker itself never reaches the justified body."""
    from render.compositor import _article_paragraphs

    text = "[[The Figure]] Odin rules Wednesday.\n\nA plain paragraph."
    sr = _article_paragraphs(
        text, tr=lambda s: {"The Figure": "Lik"}.get(s, s)
    )
    assert "<b>Lik</b>" in sr
    assert "[[" not in sr and "The Figure" not in sr
    assert "Odin rules Wednesday." in sr
    # Round two (owner 2026-07-14): CENTERED, hugging its paragraph —
    # the gap above beats the gap below.
    assert "align='center'" in sr
    assert (
        f"margin-bottom:{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px" in sr
    )
    assert (
        defaults.ARTICLE_SUBHEAD_GAP_ABOVE_PX
        > defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX
    )
    en = _article_paragraphs(text)                   # no translator: EN label
    assert "<b>The Figure</b>" in en and "[[" not in en


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
