"""Ring presets and the built render config (the skin-pack system is
gone — DOMY and MORPH are ring preset names, nothing more)."""

import pytest

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
    assert presets["Morph"]["layout"] == "chalice"
    # The third bundled styling (owner spec 2026-07-11): every hour
    # number on its OWN position, Omega on the bottom — a seal, so one
    # metal dresses all six.
    assert presets["Omega"]["layout"] == "seal"
    assert presets["Omega"]["letters"] == ("12", "16", "20", "Ω", "4", "8")
    for layout in constants.RING_LAYOUTS.values():
        assert (defaults.RING_FACE_DIR / layout["face"]).exists()
    with pytest.raises(ValueError):
        validate_preset({"name": "BAD", "positions": [1, 2], "letters": ["M"]})
    with pytest.raises(ValueError):
        validate_preset(
            {"name": "BAD", "positions": [12, 20, 24, 4],
             "letters": ["M", "Y", "Ω", "š"]}
        )


def test_mason_preset_loads_and_splits_metal():
    """The Mason bundled preset (ROADMAP 15b, CANON.md §The Banknote):
    G(12) S(16) M(20) Ω(24) N(4) A(8) on the seal layout, splitting the
    metal into the Trinity triangle (12/20/4 = G,M,N) wearing the chosen
    finish and the Union triangle (16/24/8 = S,Ω,A) wearing its counter-
    metal — NOT the Omega-style single finish on all six, because this
    preset carries its own `triangle` override."""
    from data.rings import ring_presets

    presets = ring_presets()
    mason = presets["Mason"]
    assert mason["layout"] == "seal"
    assert mason["positions"] == (12, 16, 20, 24, 4, 8)
    assert mason["letters"] == ("G", "S", "M", "Ω", "N", "A")
    assert mason["triangle"] == (12, 20, 4)
    assert set(mason["legend"]) == {12, 16, 20, 24, 4, 8}

    art_dir = defaults.RING_LETTER_ART_DIR
    # letter_art is ALWAYS the gold master now (owner 2026-07-19
    # live-render round); letter_metal carries the active finish per
    # hour — silver/bronze are derived from the gold master at paint
    # time (render.assets.letter_metal_file), never separate files.
    gold_ring = build_skin(replace(Settings(), ring="Mason")).ring
    assert gold_ring.letter_art[12] == art_dir / "G.png"
    assert gold_ring.letter_art[20] == art_dir / "M.png"
    assert gold_ring.letter_art[4] == art_dir / "N.png"
    assert gold_ring.letter_art[16] == art_dir / "S.png"
    assert gold_ring.letter_art[0] == art_dir / "Omega.png"    # 24h -> hour 0
    assert gold_ring.letter_art[8] == art_dir / "A.png"
    # Trinity (12/20/4 = G, M, N) wears the finish metal (gold, no suffix).
    assert gold_ring.letter_metal[12] == "gold"
    assert gold_ring.letter_metal[20] == "gold"
    assert gold_ring.letter_metal[4] == "gold"
    # Union (16/24/8 = S, Ω, A) wears the counter-metal (silver here).
    assert gold_ring.letter_metal[16] == "silver"
    assert gold_ring.letter_metal[0] == "silver"                # 24h -> hour 0
    assert gold_ring.letter_metal[8] == "silver"

    silver_ring = build_skin(
        replace(Settings(), ring="Mason", ring_finish="silver")
    ).ring
    assert silver_ring.letter_metal[12] == "silver"
    assert silver_ring.letter_metal[20] == "silver"
    assert silver_ring.letter_metal[4] == "silver"
    assert silver_ring.letter_metal[16] == "gold"
    assert silver_ring.letter_metal[0] == "gold"
    assert silver_ring.letter_metal[8] == "gold"

    assert missing_assets(build_skin(replace(Settings(), ring="Mason"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="Mason", ring_finish="silver"))
    ) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="Mason", ring_finish="bronze"))
    ) == []

    # Omega keeps its own plain reading — untouched by the new override
    # machinery (no `triangle` key on its card).
    numbers = build_skin(replace(Settings(), ring="Omega")).ring
    assert all(metal == "gold" for metal in numbers.letter_metal.values())


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


def test_templar_preset_loads_all_six_seats_with_the_cross_glyph():
    """TASK 2 (MASON/ICONS round, owner verdicts 2026-07-19, third
    batch): the new bundled Templar preset — the seal layout, all six
    positions wearing the templar-cross glyph (the owner's gold master,
    silver/bronze derived live like every other letter), no motto, no
    legend."""
    from data.rings import ring_presets

    presets = ring_presets()
    templar = presets["Templar"]
    assert templar["layout"] == "seal"
    assert templar["positions"] == (12, 16, 20, 24, 4, 8)
    assert templar["letters"] == ("✠",) * 6
    assert templar["triangle"] == (12, 20, 4)
    assert templar["legend"] == {}
    assert templar["motto"] == ()

    art_dir = defaults.RING_LETTER_ART_DIR
    skin = build_skin(replace(Settings(), ring="Templar")).ring
    assert all(path == art_dir / "templar.png" for path in skin.letter_art.values())
    assert missing_assets(build_skin(replace(Settings(), ring="Templar"))) == []


def test_ring_two_metals_toggle_switches_the_split(monkeypatch):
    """TASK 3 (MASON/ICONS round, owner verdicts 2026-07-19, third
    batch): Mason/Omega/Templar all carry the SAME `triangle` override
    now, but only actually SPLIT into two metals when the owner's
    per-preset toggle resolves True — the stored choice first, else the
    documented per-preset default (Mason True, everything else False —
    "default matching today's look")."""
    from config import constants

    # Defaults, no stored choice at all: Mason splits, Omega/Templar don't.
    mason = build_skin(replace(Settings(), ring="Mason")).ring
    omega = build_skin(replace(Settings(), ring="Omega")).ring
    templar = build_skin(replace(Settings(), ring="Templar")).ring
    assert mason.letter_metal[12] == "gold" and mason.letter_metal[16] == "silver"
    assert all(metal == "gold" for metal in omega.letter_metal.values())
    assert all(metal == "gold" for metal in templar.letter_metal.values())

    # Explicit stored choices invert both defaults.
    mason_off = build_skin(replace(
        Settings(), ring="Mason", ring_two_metals={"Mason": False},
    )).ring
    assert all(metal == "gold" for metal in mason_off.letter_metal.values())
    omega_on = build_skin(replace(
        Settings(), ring="Omega", ring_two_metals={"Omega": True},
    )).ring
    assert omega_on.letter_metal[12] == "gold" and omega_on.letter_metal[16] == "silver"
    templar_on = build_skin(replace(
        Settings(), ring="Templar", ring_two_metals={"Templar": True},
    )).ring
    assert templar_on.letter_metal[12] == "gold" and templar_on.letter_metal[16] == "silver"

    # A preset with NO triangle override at all is never eligible, even
    # if the settings dict names it (a stray/leftover key, harmless).
    domy = build_skin(replace(
        Settings(), ring="DOMY", ring_two_metals={"DOMY": True},
    )).ring
    assert domy.letter_metal[12] == "gold" and domy.letter_metal[0] == "silver"

    assert constants.RING_TWO_METALS_DEFAULT == {"Mason": True}


def test_mason_motto_arc_loads_and_pins_its_key_letters():
    """MOTO-FIX round (owner correction 2026-07-19, the Great Seal
    reference image): ANNUIT COEPTIS pins its own A at 8h and S at 16h
    (the TOP arc); NOVUS ORDO SECLORUM pins its own N at 4h, ORDO's own
    final O at the bottom/24h, and M at 20h (the BOTTOM arc, reading
    counterclockwise)."""
    from config import constants
    from data.rings import ring_presets

    presets = ring_presets()
    mason = presets["Mason"]
    assert [entry["text"] for entry in mason["motto"]] == [
        "ANNUIT COEPTIS", "NOVUS ORDO SECLORUM",
    ]
    annuit, novus = mason["motto"]
    assert annuit["angles"][0] % 360.0 == pytest.approx(300.0)    # A -> 8h
    assert annuit["angles"][13] % 360.0 == pytest.approx(60.0)    # S -> 16h
    assert novus["angles"][0] % 360.0 == pytest.approx(240.0)     # N -> 4h
    assert novus["angles"][9] % 360.0 == pytest.approx(180.0)     # O -> 24h (bottom)
    assert novus["angles"][18] % 360.0 == pytest.approx(120.0)    # M -> 20h

    # Every OTHER bundled preset stays motto-free (graceful absence).
    assert presets["DOMY"]["motto"] == ()
    assert presets["Morph"]["motto"] == ()
    assert presets["Omega"]["motto"] == ()

    # build_skin resolves the motto onto real assets, one glyph per
    # NON-SPACE character (spaces are dropped — RingLayer's draw loop
    # never has to check for them), wearing the active ring_finish.
    art_dir = defaults.RING_LETTER_ART_DIR
    gold_skin = build_skin(replace(Settings(), ring="Mason")).ring
    assert gold_skin.motto_metal == "gold"
    assert len(gold_skin.motto) == 2
    annuit_glyphs, novus_glyphs = gold_skin.motto
    assert len(annuit_glyphs["glyphs"]) == 13    # "ANNUIT COEPTIS" minus 1 space
    assert len(novus_glyphs["glyphs"]) == 17     # "NOVUS ORDO SECLORUM" minus 2 spaces
    first_asset, first_angle = annuit_glyphs["glyphs"][0]
    assert first_asset == art_dir / "A.png"
    assert first_angle % 360.0 == pytest.approx(300.0)

    silver_skin = build_skin(
        replace(Settings(), ring="Mason", ring_finish="silver")
    ).ring
    assert silver_skin.motto_metal == "silver"

    assert missing_assets(build_skin(replace(Settings(), ring="Mason"))) == []


def test_motto_validation_rejects_bad_cards():
    """Unknown letters, pin positions outside the preset's own six, and
    a broken angle solve (data.rings delegates to core.motto) all fail
    loudly at load time (Rule #1) — never a silent blank arc."""
    from data.rings import validate_preset

    base = {
        "name": "BAD", "positions": [12, 16, 20, 24, 4, 8],
        "letters": ["G", "S", "M", "Ω", "N", "A"],
    }
    with pytest.raises(ValueError):
        # "Ž" is not in RING_LETTER_FILES.
        validate_preset({
            **base, "motto": [{"text": "ŽANNUIT", "pins": [["Ž", 1, 8]]}],
        })
    with pytest.raises(ValueError):
        # 10 is not one of this preset's own positions.
        validate_preset({
            **base,
            "motto": [{"text": "AB", "pins": [["A", 1, 10], ["B", 1, 12]]}],
        })
    with pytest.raises(ValueError):
        # Only 1 pin — core.motto needs at least 2 to interpolate.
        validate_preset({
            **base, "motto": [{"text": "AB", "pins": [["A", 1, 8]]}],
        })


def test_dial_window_margin_grows_only_for_a_motto_preset():
    """TASK 1's margin interaction: `dial_window_margin_fraction` must
    reserve enough for the outer motto arc's own reach when the active
    preset carries one (Mason), and stay UNCHANGED for every preset
    that does not (DOMY) — the graceful-absence pattern `triangle`/
    `legend` already use. MOTO-FIX round (owner correction 2026-07-19):
    both mottos now share ONE radius, so the expected extent drops the
    old `RING_MOTTO_RADIUS_STEP` term (deleted, Rule #6)."""
    domy = build_skin(Settings())
    mason = build_skin(replace(Settings(), ring="Mason"))
    domy_margin = defaults.dial_window_margin_fraction(domy)
    mason_margin = defaults.dial_window_margin_fraction(mason)
    assert mason_margin > domy_margin
    # The motto arc's own outer reach is the binding term for Mason.
    expected_motto_extent = (
        defaults.RING_MOTTO_RADIUS_FRACTION
        + defaults.RING_MOTTO_SIZE * mason.ring_letter_scale
        * (1.0 + 2.0 * defaults.RING_LETTER_SHADOW_RADIUS)
    )
    expected_margin = (
        expected_motto_extent - 1.0
    ) / 2.0 + defaults.DIAL_WINDOW_MARGIN_EPSILON
    assert mason_margin == pytest.approx(expected_margin)


def test_build_skin_swaps_only_the_ring():
    domy = build_skin(Settings())
    morph = build_skin(replace(Settings(), ring="Morph"))
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
    assert all(metal == "gold" for metal in skin.ring.letter_metal.values())
    silver = build_skin(
        replace(
            Settings(), ring="SOLOMON", ring_finish="silver",
            custom_rings=(card,),
        )
    )
    assert all(metal == "silver" for metal in silver.ring.letter_metal.values())
    assert missing_assets(silver) == []


def test_default_config_assets_all_exist():
    """Every asset the built config references ships in the repo (a miss
    would otherwise surface inside paintEvent, where Qt swallows it)."""
    assert missing_assets(build_skin(Settings())) == []
    assert missing_assets(build_skin(replace(Settings(), ring="Morph"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), weekday_theme="norse", earth_style="atmo"))
    ) == []
    assert missing_assets(build_skin(replace(Settings(), ring_finish="silver"))) == []


def test_letter_art_follows_the_finish():
    """Owner metal rule (correction 2026-07-10): the trio of one metal
    always forms a TRIANGLE — gold finish = the layout triangle in
    gold + the rest silver; silver finish = the exact inverse."""
    art_dir = defaults.RING_LETTER_ART_DIR
    gold = build_skin(Settings()).ring
    assert gold.letter_art[12] == art_dir / "M.png"    # triangle 12/20/4 gold
    assert gold.letter_art[20] == art_dir / "Y.png"
    assert gold.letter_art[4] == art_dir / "D.png"
    assert gold.letter_metal[12] == "gold"
    assert gold.letter_metal[0] == "silver"
    silver = build_skin(replace(Settings(), ring_finish="silver")).ring
    assert silver.letter_metal[12] == "silver"          # the triangle inverts
    assert silver.letter_metal[20] == "silver"
    assert silver.letter_metal[0] == "gold"             # Omega back to gold
    morph = build_skin(replace(Settings(), ring="Morph")).ring
    assert morph.letter_art[16] == art_dir / "Pi.png"   # triangle 8/16/24 gold
    assert morph.letter_metal[16] == "gold"
    assert morph.letter_metal[0] == "gold"
    assert morph.letter_metal[12] == "silver"
    morph_silver = build_skin(
        replace(Settings(), ring="Morph", ring_finish="silver")
    ).ring
    assert morph_silver.letter_metal[12] == "gold"
    assert morph_silver.letter_metal[0] == "silver"


def test_bronze_finish_and_theme_metals():
    """Owner 2026-07-12: (1) BRONZE ring finish — the triangle wears
    bronze, the accent letter silver, the Seal all six bronze, and the
    live-derived bronze pixmap resolves for every glyph (owner
    2026-07-19 live-render round: no more pre-rendered files); (2) the
    bronze-plate weekday themes wear the chosen METAL as a render tint
    — gold/silver tritone, bronze = the art as drawn; follow-the-ring
    maps the ring finish onto them; full-color themes never tint."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])

    art_dir = defaults.RING_LETTER_ART_DIR
    bronze_ring = build_skin(replace(Settings(), ring_finish="bronze")).ring
    assert bronze_ring.letter_metal[12] == "bronze"   # triangle 12/20/4 bronze
    assert bronze_ring.letter_metal[4] == "bronze"
    assert bronze_ring.letter_metal[0] == "silver"     # accent stays silver
    assert missing_assets(build_skin(replace(Settings(), ring_finish="bronze"))) == []
    from config import constants as c
    from render.assets import letter_metal_file

    for filename in c.RING_LETTER_FILES.values():
        derived = letter_metal_file(art_dir / filename, "bronze")
        assert derived.exists(), filename
        assert derived != art_dir / filename
    seal = {
        "name": "SEALB", "positions": [4, 8, 12, 16, 20, 24],
        "letters": ["S", "O", "L", "M", "N", "A"],
    }
    seal_ring = build_skin(replace(
        Settings(), ring="SEALB", ring_finish="bronze", custom_rings=(seal,),
    )).ring
    assert all(metal == "bronze" for metal in seal_ring.letter_metal.values())
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


def test_live_derived_silver_letters_are_grayscale():
    """The LIVE-derived silver letters (owner 2026-07-19 live-render
    round — `render.assets.letter_metal_file`, replacing the retired
    pre-rendered `_silver.png` files) read R=G=B on opaque pixels and
    keep their surroundings transparent, for every active letter."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    from config import constants
    from render.assets import letter_metal_file

    QApplication.instance() or QApplication([])
    for filename in constants.RING_LETTER_FILES.values():
        gold = defaults.RING_LETTER_ART_DIR / filename
        derived = letter_metal_file(gold, "silver")
        assert derived.exists() and derived != gold, filename
        image = QImage(str(derived))
        seen_opaque = False
        for x in range(0, image.width(), 25):
            for y in range(0, image.height(), 25):
                color = image.pixelColor(x, y)
                if color.alpha() > 200:
                    seen_opaque = True
                    assert color.red() == color.green() == color.blue(), filename
        assert seen_opaque, filename
    omega = QImage(str(letter_metal_file(
        defaults.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES["Ω"], "silver"
    )))
    assert omega.pixelColor(0, 0).alpha() == 0


def test_live_derived_bronze_matches_the_retired_recipe():
    """Regression pin (owner 2026-07-19 live-render round): the live
    `letter_metal_file(gold, "bronze")` must read like the RETIRED
    pre-rendered recipe (setup/make_bronze_letters.py) — a straight
    multiply of the grayscale silver with BRONZE_LETTER_TINT
    (#CD7F32): opaque pixels carry that hue and are strictly darker
    than pure white (never a translucent wash), matching the owner's
    sealed channel statistics rather than pixel-exact PIL output
    (Qt's Multiply-mode float blending vs. PIL's integer floor
    division round slightly differently)."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QApplication

    from config import constants
    from render.assets import letter_metal_file

    QApplication.instance() or QApplication([])
    gold = defaults.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES["M"]
    silver = QImage(str(letter_metal_file(gold, "silver")))
    bronze = QImage(str(letter_metal_file(gold, "bronze")))
    assert bronze.size() == silver.size()
    tint = QColor(defaults.BRONZE_LETTER_TINT)
    seen_opaque = False
    for x in range(0, bronze.width(), 10):
        for y in range(0, bronze.height(), 10):
            silver_px = silver.pixelColor(x, y)
            if silver_px.alpha() <= 200:
                continue
            seen_opaque = True
            bronze_px = bronze.pixelColor(x, y)
            assert bronze_px.alpha() == silver_px.alpha()
            # A straight multiply can only darken (or match at 0) —
            # never brighten a channel above the tint's own ceiling.
            assert bronze_px.red() <= tint.red() + 1
            assert bronze_px.green() <= tint.green() + 1
            assert bronze_px.blue() <= tint.blue() + 1
            # Where the silver source is bright, the bronze result
            # reads the tint hue itself (a warm, low-saturation-blue
            # copper, not gray) — checked at the brightest sampled
            # pixel below.
    assert seen_opaque
    # The letter's brightest silver pixel (near-white, the glyph
    # core) must bronze to something close to the tint color itself.
    brightest = max(
        (
            (silver.pixelColor(x, y).lightness(), x, y)
            for x in range(0, silver.width(), 4)
            for y in range(0, silver.height(), 4)
            if silver.pixelColor(x, y).alpha() > 200
        ),
    )
    _, bx, by = brightest
    core = bronze.pixelColor(bx, by)
    assert abs(core.red() - tint.red()) <= 12
    assert abs(core.green() - tint.green()) <= 12
    assert abs(core.blue() - tint.blue()) <= 12


def test_full_dial_renders_distinctly_per_letter_finish():
    """Smoke test (owner 2026-07-19 live-render round): a full offscreen
    dial render must actually come out DIFFERENT under gold/silver/
    bronze ring finishes — not just carry a different label — now that
    the letters are derived live instead of loading separate files."""
    import os
    from datetime import datetime
    from zoneinfo import ZoneInfo

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import astral
    from PySide6.QtWidgets import QApplication

    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    QApplication.instance() or QApplication([])
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 7, 10, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=44.82, longitude=20.46)
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    images = {}
    for finish in ("gold", "silver", "bronze"):
        skin = build_skin(replace(Settings(), ring_finish=finish))
        image = Compositor(skin, AssetCache()).render_offscreen(
            360.0, 1.0, day, tick
        )
        assert not image.isNull()
        images[finish] = image
    finishes = list(images)
    for i, a in enumerate(finishes):
        for b in finishes[i + 1:]:
            differing = sum(
                1
                for x in range(0, images[a].width(), 8)
                for y in range(0, images[a].height(), 8)
                if images[a].pixelColor(x, y) != images[b].pixelColor(x, y)
            )
            assert differing > 0, (a, b)


def test_letter_groups_cover_the_library_exactly():
    """The builder's grouped dropdown (owner spec 2026-07-11: Latin /
    Greek / Numbers / Symbols sections) must offer every library glyph
    exactly once — and every glyph's gold master must exist (silver/
    bronze are derived at load, owner 2026-07-19 — no separate files
    to check)."""
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
        assert gold.exists(), glyph


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
