"""Ring presets and the built render config (the skin-pack system is
gone — DOMY and PILOT are ring preset names, nothing more)."""

import pytest

from app.controller import build_skin
from app.settings_store import Settings, replace
from config import continents, defaults, dial, encyclopedia_ui, pantheon, paths
from skins.manifest import missing_assets


def test_ring_preset_cards_load_and_validate():
    """The bundled cards (owner spec: {name, positions, letters}) load
    with their layouts resolved by the positions signature; a broken
    card names itself loudly."""
    import pytest

    from config import constants, continents, dial, encyclopedia_ui, pantheon
    from data.rings import ring_presets, validate_preset

    presets = ring_presets()
    assert presets["DOMY"]["layout"] == "flame"
    assert presets["DOMY"]["letters"] == ("M", "Y", "Ω", "D")
    # The chalice card is PILOT since the CROSS-WORDS round (owner UV
    # inbox + PILOT pick 2026-07-27): Π-I-L-Ω-Θ, the guide who carries
    # the traveler home; its four letters initial the light stations.
    assert presets["PILOT"]["layout"] == "chalice"
    assert presets["PILOT"]["letters"] == ("L", "Π", "Ω", "Θ")
    # The third bundled styling (owner spec 2026-07-11): every hour
    # number on its OWN position, Omega on the bottom — a seal, so one
    # metal dresses all six. Named "The One" since the DOLLAR/EYE round
    # (owner decree 2026-07-27) — the banknote's denomination.
    assert presets["The One"]["layout"] == "seal"
    assert presets["The One"]["letters"] == ("12", "16", "20", "Ω", "4", "8")
    for layout in constants.RING_LAYOUTS.values():
        assert (dial.RING_FACE_DIR / layout["face"]).exists()
    with pytest.raises(ValueError):
        validate_preset({"name": "BAD", "positions": [1, 2], "letters": ["M"]})
    with pytest.raises(ValueError):
        validate_preset(
            {"name": "BAD", "positions": [12, 20, 24, 4],
             "letters": ["M", "Y", "Ω", "š"]}
        )


def test_dollar_preset_loads_and_splits_metal():
    """The Dollar bundled preset (ROADMAP 15b, CANON.md §The Banknote;
    renamed from Mason and crowned with the Eye in the DOLLAR/EYE
    round, owner decree 2026-07-27): 👁(12) S(16) M(20) Ω(24) N(4) A(8)
    on the seal layout, splitting the metal into the Trinity triangle
    (12/20/4) wearing the chosen finish and the Union triangle
    (16/24/8) wearing its counter-metal — NOT the single finish on all
    six, because this preset carries its own `triangle` override."""
    from data.rings import ring_presets

    presets = ring_presets()
    mason = presets["Dollar"]
    assert mason["layout"] == "seal"
    assert mason["positions"] == (12, 16, 20, 24, 4, 8)
    assert mason["letters"] == ("👁", "S", "M", "Ω", "N", "A")
    assert mason["triangle"] == (12, 20, 4)
    assert set(mason["legend"]) == {12, 16, 20, 24, 4, 8}

    art_dir = dial.RING_LETTER_ART_DIR
    # letter_art is ALWAYS the gold master now (owner 2026-07-19
    # live-render round); letter_metal carries the active finish per
    # hour — silver/bronze are derived from the gold master at paint
    # time (render.asset_recolor.letter_metal_file), never separate files.
    gold_ring = build_skin(replace(Settings(), ring="Dollar")).ring
    # The apex wears the Eye — with the Dollar's own Shine default ON
    # (constants.RING_EYE_SHINE_DEFAULT) the glory-of-rays master.
    assert gold_ring.letter_art[12] == art_dir / "Eye_shine.png"
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
        replace(Settings(), ring="Dollar", ring_finish="silver")
    ).ring
    assert silver_ring.letter_metal[12] == "silver"
    assert silver_ring.letter_metal[20] == "silver"
    assert silver_ring.letter_metal[4] == "silver"
    assert silver_ring.letter_metal[16] == "gold"
    assert silver_ring.letter_metal[0] == "gold"
    assert silver_ring.letter_metal[8] == "gold"

    assert missing_assets(build_skin(replace(Settings(), ring="Dollar"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="Dollar", ring_finish="silver"))
    ) == []
    assert missing_assets(
        build_skin(replace(Settings(), ring="Dollar", ring_finish="bronze"))
    ) == []

    # The One keeps its own plain reading — untouched by the override
    # machinery (its toggle default is off).
    numbers = build_skin(replace(Settings(), ring="The One")).ring
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

    art_dir = dial.RING_LETTER_ART_DIR
    skin = build_skin(replace(Settings(), ring="Templar")).ring
    assert all(path == art_dir / "templar.png" for path in skin.letter_art.values())
    assert missing_assets(build_skin(replace(Settings(), ring="Templar"))) == []


def test_ring_two_metals_toggle_switches_the_split(monkeypatch):
    """TASK 3 (MASON/ICONS round, owner verdicts 2026-07-19, third
    batch): Dollar/The One/Templar all carry the SAME `triangle`
    override now, but only actually SPLIT into two metals when the
    owner's per-preset toggle resolves True — the stored choice first,
    else the documented per-preset default (Dollar True, everything
    else False — "default matching today's look")."""
    from config import constants, continents, dial, encyclopedia_ui, pantheon

    # Defaults, no stored choice at all: Dollar splits, the others don't.
    mason = build_skin(replace(Settings(), ring="Dollar")).ring
    omega = build_skin(replace(Settings(), ring="The One")).ring
    templar = build_skin(replace(Settings(), ring="Templar")).ring
    assert mason.letter_metal[12] == "gold" and mason.letter_metal[16] == "silver"
    assert all(metal == "gold" for metal in omega.letter_metal.values())
    assert all(metal == "gold" for metal in templar.letter_metal.values())

    # Explicit stored choices invert both defaults.
    mason_off = build_skin(replace(
        Settings(), ring="Dollar", ring_two_metals={"Dollar": False},
    )).ring
    assert all(metal == "gold" for metal in mason_off.letter_metal.values())
    omega_on = build_skin(replace(
        Settings(), ring="The One", ring_two_metals={"The One": True},
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

    assert constants.RING_TWO_METALS_DEFAULT == {"Dollar": True}


def test_dollar_eye_shine_toggle_swaps_the_master():
    """DOLLAR/EYE round (owner decree 2026-07-27): the Dollar's apex
    Eye follows the per-preset Shine toggle — default ON (the
    banknote's eye radiates), stored False drops the glory of rays;
    the canonical stems resolve to the active art source's _gem/_gpt
    file on disk; a custom ring's EXPLICIT eye variant is untouched by
    the toggle (its rays are baked into the chosen glyph)."""
    from config import constants, continents, dial, encyclopedia_ui, pantheon

    art_dir = dial.RING_LETTER_ART_DIR
    assert constants.RING_EYE_SHINE_DEFAULT == {"Dollar": True}

    shine_on = build_skin(replace(Settings(), ring="Dollar")).ring
    assert shine_on.letter_art[12] == art_dir / "Eye_shine.png"
    shine_off = build_skin(replace(
        Settings(), ring="Dollar", ring_eye_shine={"Dollar": False},
    )).ring
    assert shine_off.letter_art[12] == art_dir / "Eye.png"
    for state in (shine_on,):
        assert paths.art_file(state.letter_art[12]).exists()
    assert paths.art_file(shine_off.letter_art[12]).exists()
    assert missing_assets(build_skin(replace(Settings(), ring="Dollar"))) == []
    assert missing_assets(build_skin(replace(
        Settings(), ring="Dollar", ring_eye_shine={"Dollar": False},
    ))) == []

    # A custom seal with an explicit eye variant: the file is the
    # chosen one, and the Shine toggle has nothing to grab (the card
    # seats no adaptive glyph).
    custom = (
        {
            "name": "MyEye",
            "positions": [12, 16, 20, 24, 4, 8],
            "letters": ["👁 Gemini ☀", "S", "M", "Ω", "N", "A"],
        },
    )
    custom_ring = build_skin(replace(
        Settings(), ring="MyEye", custom_rings=custom,
        ring_eye_shine={"MyEye": False},
    )).ring
    assert custom_ring.letter_art[12] == art_dir / "Eye_shine_gem.png"

    # THE SHINE ENLARGE (owner UV inbox 2026-07-27): the shine master
    # draws bigger by the measured per-source factor so the TRIANGLE
    # stays the no-light size — stamped as ring.letter_zoom, absent
    # (1.0) for the plain eye and for every ordinary letter.
    assert shine_on.letter_zoom == {
        12: constants.RING_EYE_SHINE_ENLARGE["gem"]
    }
    assert shine_off.letter_zoom == {}
    assert custom_ring.letter_zoom == {
        12: constants.RING_EYE_SHINE_ENLARGE["gem"]
    }
    gpt_shine = build_skin(replace(
        Settings(), ring="Dollar", art_source="chatgpt",
    )).ring
    assert gpt_shine.letter_zoom == {
        12: constants.RING_EYE_SHINE_ENLARGE["gpt"]
    }


def test_cross_words_ring_the_dial():
    """CROSS-WORDS round (owner UV inbox 2026-07-27): DOMY wears its
    dark-cross station words (FEAR ANGER HATE SUFFERING) and PILOT its
    light-cross station words (HOPE FAITH LOVE SALVATION) as
    outside-the-band arc text — one word CENTERED on its station seat
    (`core.motto.centered_word_angles`, the mottos' own letter step),
    clockwise over the top half and counterclockwise under the bottom
    so every word reads left-to-right to a viewer; and both presets
    answer the per-letter hover legend on every seat, like the Dollar."""
    from core.angles import ring_position_angle
    from data.rings import ring_presets

    step = dial.RING_MOTTO_LETTER_STEP_DEG
    expectations = {
        "DOMY": {"SUFFERING": (12, True), "FEAR": (20, False),
                 "ANGER": (24, False), "HATE": (4, False)},
        "PILOT": {"HOPE": (8, True), "FAITH": (12, True),
                  "LOVE": (16, True), "SALVATION": (24, False)},
    }
    presets = ring_presets()
    for ring, words in expectations.items():
        card = presets[ring]
        assert {m["text"] for m in card["motto"]} == set(words)
        for entry in card["motto"]:
            seat, clockwise = words[entry["text"]]
            angles = entry["angles"]
            mid = (angles[0] + angles[-1]) / 2.0
            assert mid % 360.0 == pytest.approx(
                ring_position_angle(seat) % 360.0
            ), (ring, entry["text"])
            expected_step = step if clockwise else -step
            assert angles[1] - angles[0] == pytest.approx(expected_step)
        # The hover legend answers on every seat of both cross rings.
        assert sorted(card["legend"]) == sorted(card["positions"])
    # build_skin resolves every word glyph onto a real letter asset.
    for ring in ("DOMY", "PILOT"):
        skin = build_skin(replace(Settings(), ring=ring))
        assert len(skin.ring.motto) == 4
        assert missing_assets(skin) == []


def test_motto_words_map_to_their_seats():
    """WORD-HOVER round (owner 2026-07-27): every arc word knows the
    SEAT whose legend it answers with — a station word its own station,
    and each Dollar motto word the seat of its ONE pinned letter (the
    five words spell the five letters: ANNUIT→A, COEPTIS→S, NOVUS→N,
    ORDO→Ω, SECLORUM→M)."""
    from data.rings import ring_presets

    presets = ring_presets()
    dollar_words = {
        w["text"]: w["seat"]
        for e in presets["Dollar"]["motto"] for w in e["words"]
    }
    assert dollar_words == {
        "ANNUIT": 8, "COEPTIS": 16, "NOVUS": 4, "ORDO": 24, "SECLORUM": 20,
    }
    domy_words = {
        w["text"]: w["seat"]
        for e in presets["DOMY"]["motto"] for w in e["words"]
    }
    assert domy_words == {"SUFFERING": 12, "FEAR": 20, "ANGER": 24, "HATE": 4}
    # build_skin carries the solved hover geometry per word.
    skin = build_skin(replace(Settings(), ring="Dollar"))
    words = [w for e in skin.ring.motto for w in e["words"]]
    assert all(
        w["seat"] is not None and w["half"] > 0.0 for w in words
    )


def test_two_metals_toggle_now_covers_the_cross_rings():
    """ENLARGE/THEMATIC round (owner 2026-07-27, "hoću da Two Metals
    opcija bude i za DOMY tj PILOT"): the flame/chalice presets are
    eligible too — default ON (today's 3+1 look), stored OFF dresses
    every letter in the ONE finish."""
    domy_off = build_skin(replace(
        Settings(), ring_two_metals={"DOMY": False},
    )).ring
    assert all(m == "gold" for m in domy_off.letter_metal.values())
    pilot_off = build_skin(replace(
        Settings(), ring="PILOT", ring_finish="silver",
        ring_two_metals={"PILOT": False},
    )).ring
    assert all(m == "silver" for m in pilot_off.letter_metal.values())
    # Default stays the split look.
    domy_on = build_skin(Settings()).ring
    assert domy_on.letter_metal[12] == "gold"
    assert domy_on.letter_metal[0] == "silver"


def test_thematic_finish_wears_the_preset_color():
    """ENLARGE/THEMATIC round (owner 2026-07-27): the 4th ring finish —
    the letters wear the ACTIVE preset's own theme color through the
    recolor transformer (DOMY cross red, PILOT cross blue, Dollar
    green, The One moon indigo, Templar black); outside the ring band
    the skin reads gold (documented containment)."""
    from config import constants, continents, dial, encyclopedia_ui, pantheon, paths

    thematic = build_skin(replace(Settings(), ring_finish="thematic"))
    assert thematic.ring.letter_metal[12] == "thematic"   # the triangle
    assert thematic.ring.letter_metal[0] == "silver"      # the accent
    assert thematic.ring.motto_metal == "thematic"
    assert thematic.ring_finish == "gold"                 # containment
    # The shade rides THIS skin (owner bug 2026-07-28) — never a process
    # global, so building another watch's skin cannot repaint this one.
    assert thematic.display.shade("thematic") == "cross_red"   # DOMY's
    dollar = build_skin(replace(Settings(), ring="Dollar", ring_finish="thematic"))
    assert dollar.display.shade("thematic") == "dollar_green"
    pilot = build_skin(replace(Settings(), ring="PILOT", ring_finish="thematic"))
    assert pilot.display.shade("thematic") == "cross_blue"
    # ...and the earlier skins are UNMOVED by the later builds.
    assert thematic.display.shade("thematic") == "cross_red"
    assert dollar.display.shade("thematic") == "dollar_green"
    assert paths.metal_shade("thematic") == paths.DEFAULT_DISPLAY.shade(
        "thematic"
    )                                    # nothing leaked to the process
    # Two metals OFF + thematic = every letter in the theme color.
    flat = build_skin(replace(
        Settings(), ring_finish="thematic", ring_two_metals={"DOMY": False},
    )).ring
    assert all(m == "thematic" for m in flat.letter_metal.values())
    # The full preset->shade table is pinned.
    assert constants.RING_THEMATIC_SHADES == {
        "DOMY": "cross_red", "PILOT": "cross_blue", "Dollar": "dollar_green",
        "The One": "moon_indigo", "Templar": "templar_black",
    }


def test_thematic_choices_mirror_the_recolor_presets():
    """CUSTOM-THEMATIC widening (owner 2026-07-27, "iron, copper...
    sve"): constants.py is a pure-literals file (its own docstring
    law), so the thematic choice roster cannot READ metals.json — THIS
    test is the sync: every transformer ramp is choosable, in the
    preset file's own order, and nothing is choosable that no ramp
    draws; defaults identity-maps the full roster and every choice has
    a display title for the custom builder's combo."""
    import json
    from pathlib import Path

    from config import constants, continents, dial, encyclopedia_ui, pantheon

    presets = json.loads(
        (Path(__file__).resolve().parents[1]
         / "recolor" / "presets" / "metals.json").read_text(encoding="utf-8")
    )
    assert constants.METAL_SHADE_NAMES["thematic"] == tuple(
        presets["metals"].keys()
    )
    assert defaults.METAL_SHADES["thematic"] == {
        name: name for name in constants.METAL_SHADE_NAMES["thematic"]
    }
    for shade in constants.METAL_SHADE_NAMES["thematic"]:
        assert shade in constants.METAL_SHADE_TITLES, shade


def test_two_watches_keep_their_own_thematic_color():
    """THE MULTI-WATCH COLOUR LEAK (owner bug 2026-07-28) — the
    regression pin.

    Reported: "Boji oba isto (kao poslednji ucitani sat — imamo DOMY i
    PILOT tematic i oba su crvena)". Root cause: the art source, subdial
    set and metal shades were PROCESS-WIDE module globals that
    `apply_display_settings` overwrote on every skin build.
    `AppController.__init__` builds EVERY watch before the first one
    paints, so by paint time all of them read the LAST-BUILT watch's
    shade — DOMY's `cross_red`.

    This test reproduces that exact order: build all the skins FIRST,
    resolve the art AFTERWARDS. Each watch must still resolve its own
    letter file. If the display state ever becomes process-wide again,
    the two paths collapse into one and this fails."""
    from pathlib import Path

    from config import continents, dial, encyclopedia_ui, pantheon, paths
    from render.asset_recolor import letter_metal_path

    # Real order: every watch's skin is built before any of them paints.
    pilot = build_skin(replace(Settings(), ring="PILOT", ring_finish="thematic"))
    domy = build_skin(replace(Settings(), ring="DOMY", ring_finish="thematic"))
    assert pilot.display.shade("thematic") == "cross_blue"
    assert domy.display.shade("thematic") == "cross_red"

    # The SAME master letter, resolved by each watch in turn — so the only
    # thing that can make the two answers differ is the watch's own shade.
    master = Path(domy.ring.letter_art[12])
    derived = {}
    for name, skin in (("PILOT", pilot), ("DOMY", domy)):
        # Exactly what the compositor does: install THIS watch's context,
        # then resolve. (`paths.in_display` wraps every real entry point.)
        with paths.display(skin.display):
            derived[name] = letter_metal_path(master, "thematic")

    assert derived["PILOT"] != derived["DOMY"], derived
    assert "cross_blue" in derived["PILOT"].name
    assert "cross_red" in derived["DOMY"].name


def test_custom_ring_picks_its_own_thematic_color():
    """CUSTOM-THEMATIC widening (owner 2026-07-27): a custom card's own
    `thematic` field wins under the Thematic finish — any transformer
    ramp, metals included; absent, the moon indigo fallback; an unknown
    name fails loudly at validation (Rule #1)."""
    import pytest as _pytest

    from config import constants, continents, dial, encyclopedia_ui, pantheon, paths
    from data.rings import validate_preset

    custom = (
        {"name": "IRONRING", "positions": [12, 20, 24, 4],
         "letters": ["I", "R", "O", "N"], "thematic": "copper"},
    )
    iron = build_skin(replace(
        Settings(), ring="IRONRING", custom_rings=custom,
        ring_finish="thematic",
    ))
    assert iron.display.shade("thematic") == "copper"
    plain = (
        {"name": "PLAINRING", "positions": [12, 20, 24, 4],
         "letters": ["A", "B", "C", "D"]},
    )
    bare = build_skin(replace(
        Settings(), ring="PLAINRING", custom_rings=plain,
        ring_finish="thematic",
    ))
    assert bare.display.shade("thematic") == "moon_indigo"
    with _pytest.raises(ValueError):
        validate_preset({
            "name": "X", "positions": [12, 20, 24, 4],
            "letters": ["A", "B", "C", "D"], "thematic": "neon",
        })


def test_mason_motto_arc_loads_and_pins_its_key_letters():
    """MOTO-FIX round (owner correction 2026-07-19, the Great Seal
    reference image): ANNUIT COEPTIS pins its own A at 8h and S at 16h
    (the TOP arc); NOVUS ORDO SECLORUM pins its own N at 4h, ORDO's own
    final O at the bottom/24h, and M at 20h (the BOTTOM arc, reading
    counterclockwise)."""
    from config import constants, continents, dial, encyclopedia_ui, pantheon
    from data.rings import ring_presets

    presets = ring_presets()
    mason = presets["Dollar"]
    assert [entry["text"] for entry in mason["motto"]] == [
        "ANNUIT COEPTIS", "NOVUS ORDO SECLORUM",
    ]
    annuit, novus = mason["motto"]
    assert annuit["angles"][0] % 360.0 == pytest.approx(300.0)    # A -> 8h
    assert annuit["angles"][13] % 360.0 == pytest.approx(60.0)    # S -> 16h
    assert novus["angles"][0] % 360.0 == pytest.approx(240.0)     # N -> 4h
    assert novus["angles"][9] % 360.0 == pytest.approx(180.0)     # O -> 24h (bottom)
    assert novus["angles"][18] % 360.0 == pytest.approx(120.0)    # M -> 20h

    # The motto-free bundled presets stay motto-free (graceful
    # absence); DOMY and PILOT carry their own cross words now
    # (CROSS-WORDS round — see test_cross_words_ring_the_dial).
    assert presets["The One"]["motto"] == ()
    assert presets["Templar"]["motto"] == ()

    # build_skin resolves the motto onto real assets, one glyph per
    # NON-SPACE character (spaces are dropped — RingLayer's draw loop
    # never has to check for them), wearing the active ring_finish.
    art_dir = dial.RING_LETTER_ART_DIR
    gold_skin = build_skin(replace(Settings(), ring="Dollar")).ring
    assert gold_skin.motto_metal == "gold"
    assert len(gold_skin.motto) == 2
    annuit_glyphs, novus_glyphs = gold_skin.motto
    assert len(annuit_glyphs["glyphs"]) == 13    # "ANNUIT COEPTIS" minus 1 space
    assert len(novus_glyphs["glyphs"]) == 17     # "NOVUS ORDO SECLORUM" minus 2 spaces
    first_asset, first_angle = annuit_glyphs["glyphs"][0]
    assert first_asset == art_dir / "A.png"
    assert first_angle % 360.0 == pytest.approx(300.0)

    silver_skin = build_skin(
        replace(Settings(), ring="Dollar", ring_finish="silver")
    ).ring
    assert silver_skin.motto_metal == "silver"

    assert missing_assets(build_skin(replace(Settings(), ring="Dollar"))) == []


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
    preset carries one, and stay UNCHANGED for every preset that does
    not — the graceful-absence pattern `triangle`/`legend` already use.
    CROSS-WORDS round (owner UV inbox 2026-07-27): DOMY and PILOT now
    carry their station words as arc text too, so the motto-free
    baseline is Templar/The One. MOTO-FIX round (owner correction
    2026-07-19): both mottos share ONE radius, so the expected extent
    drops the old `RING_MOTTO_RADIUS_STEP` term (deleted, Rule #6)."""
    templar = build_skin(replace(Settings(), ring="Templar"))
    mason = build_skin(replace(Settings(), ring="Dollar"))
    domy = build_skin(Settings())
    templar_margin = defaults.dial_window_margin_fraction(templar)
    mason_margin = defaults.dial_window_margin_fraction(mason)
    assert mason_margin > templar_margin
    # The cross-word presets reserve the SAME motto reach as the Dollar.
    assert defaults.dial_window_margin_fraction(domy) == mason_margin
    # The motto arc's own outer reach is the binding term for the Dollar.
    expected_motto_extent = (
        dial.RING_MOTTO_RADIUS_FRACTION
        + dial.RING_MOTTO_SIZE * mason.ring_letter_scale
        * (1.0 + 2.0 * dial.RING_LETTER_SHADOW_RADIUS)
    )
    expected_margin = (
        expected_motto_extent - 1.0
    ) / 2.0 + defaults.DIAL_WINDOW_MARGIN_EPSILON
    assert mason_margin == pytest.approx(expected_margin)


def test_build_skin_swaps_only_the_ring():
    domy = build_skin(Settings())
    morph = build_skin(replace(Settings(), ring="PILOT"))
    assert domy.ring.asset.name == "domy.png"
    assert morph.ring.asset.name == "morph.png"
    assert morph.ring.letters == {12: "L", 16: "Π", 8: "Θ", 0: "Ω"}
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
    assert missing_assets(build_skin(replace(Settings(), ring="PILOT"))) == []
    assert missing_assets(
        build_skin(replace(Settings(), weekday_theme="norse", earth_style="atmo"))
    ) == []
    assert missing_assets(build_skin(replace(Settings(), ring_finish="silver"))) == []


def test_letter_art_follows_the_finish():
    """Owner metal rule (correction 2026-07-10): the trio of one metal
    always forms a TRIANGLE — gold finish = the layout triangle in
    gold + the rest silver; silver finish = the exact inverse."""
    art_dir = dial.RING_LETTER_ART_DIR
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
    morph = build_skin(replace(Settings(), ring="PILOT")).ring
    assert morph.letter_art[16] == art_dir / "Pi.png"   # triangle 8/16/24 gold
    assert morph.letter_metal[16] == "gold"
    assert morph.letter_metal[0] == "gold"
    assert morph.letter_metal[12] == "silver"
    morph_silver = build_skin(
        replace(Settings(), ring="PILOT", ring_finish="silver")
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

    art_dir = dial.RING_LETTER_ART_DIR
    bronze_ring = build_skin(replace(Settings(), ring_finish="bronze")).ring
    assert bronze_ring.letter_metal[12] == "bronze"   # triangle 12/20/4 bronze
    assert bronze_ring.letter_metal[4] == "bronze"
    assert bronze_ring.letter_metal[0] == "silver"     # accent stays silver
    assert missing_assets(build_skin(replace(Settings(), ring_finish="bronze"))) == []
    from config import constants as c, continents, dial, encyclopedia_ui, pantheon
    # The EAGER door: the dial itself now draws the gold master until the
    # background warm catches up (owner 2026-07-28), so a test that wants
    # to see the real bronze pixels must ask for them (`letter_metal_
    # variant` = name + materialize).
    from render.asset_recolor import letter_metal_variant

    for filename in c.RING_LETTER_FILES.values():
        derived = letter_metal_variant(art_dir / filename, "bronze")
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
    from config import continents, dial, encyclopedia_ui, pantheon, paths as _paths

    assert all(
        _paths.art_file(path).exists()
        for path in colored.bodies.values()
    )
    # The colored set is complete for every metal-capable theme except
    # the seats the ART DEBT REGISTRY names (`tests/art_debt.py` — the
    # ONE list this guard shares with the bronze, dual and Ninth guards,
    # rather than a fourth private copy of the same debt).
    from tests.art_debt import PENDING_BODY_COLORED

    missing_colored = set()
    for theme in c.METAL_THEMES:
        if "colored" not in c.theme_metals(theme):
            # planets_art (owner 2026-07-18): bronze medallions with NO
            # colored/ subfolder — offering "Colored" for it would
            # dangle on a missing asset, so it is excluded up front.
            continue
        # colored is the variant SIBLING (owner restructure 2026-07-14).
        folder = pantheon.weekday_art(
            pantheon.WEEKDAY_THEME_DIRS[theme]
        ).parent / "colored"
        for body in c.WEEKDAY_BODIES:
            stem = pantheon.WEEKDAY_THEME_FILES[theme][body]
            if not _paths.art_file(folder / f"{stem}.png").exists():
                missing_colored.add((theme, body))
    assert missing_colored <= PENDING_BODY_COLORED, sorted(
        missing_colored - PENDING_BODY_COLORED
    )
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
            defaults.ZODIAC_ART_DIR / "zodiac" / "chinese" / "primary" / "colored"
            / f"{animal}.png"
        ).exists(), animal
    for sign, _ in c.ZODIAC_SIGNS:
        assert _paths.art_file(
            defaults.ZODIAC_ART_DIR / "zodiac" / "astrology" / "primary"
            / "colored" / f"{sign}.png"
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
    swapped = AssetCache._recolored(
        image, "silver",
        defaults.METAL_SOURCE_BADGE, defaults.METAL_MASK_BADGE,
    )
    bronze_out = swapped.pixelColor(0, 0)
    gray_out = swapped.pixelColor(1, 0)
    assert bronze_out.saturationF() < 0.15           # bronze went silver
    assert gray_out == QColor("#808080")             # gray untouched


def test_metal_shade_table_pinned():
    """Pin the shade table AFTER the 2026-07-27 transformer rewrite: the
    numeric (hue, saturation, reference value) recipe is gone — a shade
    now NAMES a ramp in `recolor/presets/metals.json`, and the ramp is
    what draws it. What must still hold: the user-facing shade names
    match `config.constants.METAL_SHADE_NAMES` exactly (Settings
    validates against them), every default is one of its own metal's
    names, and every shade resolves to a ramp that actually exists —
    a typo here would surface as a KeyError mid-render on a user's
    machine, which is the failure this pin exists to prevent."""
    from config import constants, continents, dial, encyclopedia_ui, pantheon
    from recolor import recipe as recolor_recipe

    presets = recolor_recipe.load()
    for metal, names in constants.METAL_SHADE_NAMES.items():
        assert tuple(defaults.METAL_SHADES[metal].keys()) == names, metal
        assert constants.METAL_SHADE_DEFAULT[metal] in names, metal
        for shade, ramp_name in defaults.METAL_SHADES[metal].items():
            assert ramp_name in presets.metals, (metal, shade, ramp_name)
        assert constants.METAL_SHADE_TITLES.keys() >= set(names), metal

    # The art's own metals must be describable too — the transform is
    # source-agnostic and asks the presets for its SOURCE as well.
    assert defaults.METAL_SOURCE_BADGE in presets.metals
    assert defaults.METAL_SOURCE_LETTER in presets.metals
    assert defaults.METAL_MASK_BADGE == "chroma"
    assert defaults.METAL_MASK_LETTER == "alpha"


def test_metal_mask_stays_untouched_across_every_shade():
    """THE MASK LAW (R8a round, algorithm point 1a — "the mask stays"):
    whichever SHADE is active, a neutral gray pixel outside the warm-
    bronze hue window must come back byte-for-byte untouched — shade
    selection only changes what the DETECTED metal pixels become,
    never what gets detected."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor, QPixmap
    from PySide6.QtWidgets import QApplication

    from config import continents, dial, encyclopedia_ui, pantheon, paths as _paths
    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    probe = QPixmap(2, 1)
    probe.fill(QColor("#B08050"))                    # warm bronze
    image = probe.toImage()
    image.setPixelColor(1, 0, QColor("#808080"))     # neutral gray
    for metal, shade in (
        ("gold", "dark_amber"), ("gold", "champagne"),
        ("silver", "gunmetal"), ("silver", "platinum"),
    ):
        with _paths.display(
            _paths.display_context(metal_shades={metal: shade})
        ):
            swapped = AssetCache._recolored(
                image, metal,
                defaults.METAL_SOURCE_BADGE, defaults.METAL_MASK_BADGE,
            )
        assert swapped.pixelColor(1, 0) == QColor("#808080"), (metal, shade)
        assert swapped.pixelColor(0, 0) != QColor("#B08050"), (metal, shade)


def test_metal_recolor_relief_order_survives_the_ramp():
    """THE RELIEF GATE, rewritten for the 2026-07-27 transformer
    (replaces the retired gain-multiply pin, whose arithmetic died with
    `METAL_RECOLOR_GAIN_RANGE`): a monotone brightness ramp in must come
    out monotone, so no light/dark relationship anywhere in a medallion
    is ever inverted or flattened. That is the property the reverted
    percentile-RANK attempt (git show 013b5ca) destroyed — it remapped
    each pixel by its rank and turned every relief into a wash.

    A synthetic warm-bronze gradient stands in for a real medallion so
    the expectation is computable independently of any art file. The
    affine-ness of the anchor itself is pinned at the unit level by
    `tests/test_recolor.py::test_anchor_is_monotone_not_a_rank_remap`;
    this is the same law through the real Qt render path."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import numpy as np
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QApplication

    from config import continents, dial, encyclopedia_ui, pantheon, paths as _paths
    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    width, height = 64, 8
    values = np.linspace(0.15, 0.85, width)
    hue, sat = 35.0, 0.5     # squarely inside the warm-bronze mask window
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    for x, v in enumerate(values):
        color = QColor.fromHsvF(hue / 360.0, sat, float(v))
        for y in range(height):
            image.setPixelColor(x, y, color)

    with _paths.display(
        _paths.display_context(metal_shades={"gold": "dark_amber"})
    ):
        swapped = AssetCache._recolored(
            image, "gold",
            defaults.METAL_SOURCE_BADGE, defaults.METAL_MASK_BADGE,
        )

    row = height // 2
    out = np.array([
        swapped.pixelColor(x, row).lightnessF() for x in range(width)
    ])
    # (1) The order survives end to end — never inverted, never flat.
    assert np.diff(out).min() > -1e-9
    assert out[-1] - out[0] > 0.25
    # (2) Nothing is crushed or blown: the failure the old bounded gain
    #     produced on real art was 11.87% of a plate at one flat maximum.
    assert out.max() < 1.0 - 1e-6
    assert out.min() > 0.0 + 1e-6
    # (3) The recolor actually ran — the midpoint wears the gold family's
    #     warm hue, not the source's own.
    sampled = swapped.pixelColor(width // 2, row)
    assert 20.0 < sampled.hsvHueF() * 360.0 < 60.0
    assert sampled.hsvSaturationF() > 0.2


def test_planets_art_body_renders_differently_by_metal():
    """Render-chain confirmation (owner 2026-07-18): the real
    planets/art/sun.png plate — a bronze medallion like the pantheon
    sets — must actually come out of AssetCache looking different
    under gold vs bronze, not just carry a different metal LABEL."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from config import continents, dial, encyclopedia_ui, pantheon, paths as _paths
    from render.assets import AssetCache

    QApplication.instance() or QApplication([])
    sun = (
        pantheon.weekday_art(pantheon.WEEKDAY_THEME_DIRS["planets_art"])
        / "sun.png"
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


def test_live_derived_silver_letters_read_as_cool_silver():
    """The LIVE-derived silver letters (`render.asset_recolor.
    letter_metal_file` — the pre-rendered `_silver.png` files were
    retired 2026-07-19).

    THE LAW CHANGED on 2026-07-27, with the owner's acceptance of the new
    transformer: silver used to be asserted R==G==B EXACTLY, because the
    retired kernel produced it as `HSV(220, S=0, V)` — i.e. a straight
    `max(R,G,B)` grayscale. That is precisely why the owner rejected it
    ("kao da joj je neko polio krec"): a flat achromatic lift reads as
    whitewashed plaster, not as metal. Real silver carries a COOL cast in
    the shadows and a near-white specular, so the new ramp is
    deliberately not neutral. What must hold now: nearly neutral (a
    silver letter must never look tinted), never WARM, and never flat."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication

    import numpy as np

    from config import constants, continents, dial, encyclopedia_ui, pantheon
    from recolor import space as recolor_space
    from render.asset_recolor import letter_metal_variant

    QApplication.instance() or QApplication([])
    # Neutrality is measured as OKLAB CHROMA, not HSV saturation: HSV
    # saturation is a ratio over a vanishing maximum, so a deep shadow
    # pixel reads "saturated" at a chroma the eye cannot see. The silver
    # ramp's own peak chroma is ~0.021; gold's is ~0.135.
    for filename in constants.RING_LETTER_FILES.values():
        gold = dial.RING_LETTER_ART_DIR / filename
        derived = letter_metal_variant(gold, "silver")
        assert derived.exists() and derived != gold, filename
        image = QImage(str(derived))
        seen_opaque = False
        levels = []
        for x in range(0, image.width(), 25):
            for y in range(0, image.height(), 25):
                color = image.pixelColor(x, y)
                if color.alpha() > 200:
                    seen_opaque = True
                    levels.append(color.lightness())
                    lab = recolor_space.linear_to_oklab(
                        recolor_space.srgb_to_linear(
                            np.array(color.getRgbF()[:3])
                        )
                    )
                    chroma = recolor_space.oklab_chroma_hue(lab)[0]
                    # Nearly neutral — a silver letter must never read tinted.
                    assert chroma < 0.05, (filename, x, y, color.getRgb())
                    # ...and never WARM: silver is cool or neutral, so the
                    # blue channel may not sit below the red one.
                    assert color.blue() >= color.red() - 2, (filename, x, y)
        assert seen_opaque, filename
        # Never flat: the glyph keeps a real light-to-dark range.
        assert max(levels) - min(levels) > 20, filename
    omega = QImage(str(letter_metal_variant(
        dial.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES["Ω"], "silver"
    )))
    assert omega.pixelColor(0, 0).alpha() == 0


def test_live_derived_bronze_preserves_relief_and_reads_bronze():
    """Regression pin for the live gold -> bronze letter derivation,
    rewritten for the 2026-07-27 transformer (the retired assertions
    read the old `(hue, saturation, reference value)` tuple, which no
    longer exists — a shade now names a RAMP).

    The law is unchanged in substance: (1) the glyph must read as a real
    copper-warm bronze on every opaque pixel — never gray, never still
    the gold source hue — and (2) THE RELIEF MUST SURVIVE: the gold
    master's brightest and darkest sampled points must bronze in the
    SAME relative order. Point (2) is what the reverted percentile-RANK
    attempt (git show 013b5ca) destroyed."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QColor, QImage

    from config import constants, continents, dial, encyclopedia_ui, pantheon
    from recolor import ramp as recolor_ramp, recipe as recolor_recipe
    from render.asset_recolor import letter_metal_variant

    QApplication.instance() or QApplication([])
    gold_path = dial.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES["M"]
    gold = QImage(str(gold_path))
    bronze = QImage(str(letter_metal_variant(gold_path, "bronze")))
    assert bronze.size() == gold.size()

    # The expected hue comes from the ramp the shade names — one source
    # of truth, so retuning the preset can never leave this pin stale.
    presets = recolor_recipe.load()
    ramp_name = defaults.METAL_SHADES["bronze"]["bronze"]
    body = recolor_ramp.body_color(
        presets.metal(ramp_name), presets.tuning.body_position
    )
    from recolor import space as recolor_space
    body_srgb = recolor_space.linear_to_srgb(body)
    hue_deg = QColor.fromRgbF(*body_srgb).hsvHueF() * 360.0

    darkest = brightest = None
    seen_opaque = False
    for x in range(0, gold.width(), 4):
        for y in range(0, gold.height(), 4):
            gold_px = gold.pixelColor(x, y)
            if gold_px.alpha() <= 200:
                continue
            seen_opaque = True
            bronze_px = bronze.pixelColor(x, y)
            assert bronze_px.alpha() == gold_px.alpha()
            # Skip the two ends of the ramp, where a metal DESATURATES by
            # design (deep shadow and the near-white specular) and a hue
            # reading stops being meaningful.
            if 40 <= bronze_px.value() <= 235:
                hue_diff = min(
                    abs(bronze_px.hsvHueF() * 360.0 - hue_deg),
                    360.0 - abs(bronze_px.hsvHueF() * 360.0 - hue_deg),
                )
                assert hue_diff < 20.0, (x, y, bronze_px.getRgb())
                assert bronze_px.hsvSaturationF() > 0.20, (x, y, bronze_px.getRgb())
            level = gold_px.lightness()
            if darkest is None or level < darkest[0]:
                darkest = (level, x, y)
            if brightest is None or level > brightest[0]:
                brightest = (level, x, y)
    assert seen_opaque and darkest is not None and brightest is not None
    dark_bronze = bronze.pixelColor(darkest[1], darkest[2])
    bright_bronze = bronze.pixelColor(brightest[1], brightest[2])
    # The relief survives: the gold master's brighter sample still
    # bronzes brighter than its darker sample.
    assert bright_bronze.value() > dark_bronze.value()


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
    from render.art_warm import warm_pending_art
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
        compositor = Compositor(skin, AssetCache())
        # Render TWICE with the background drain in between — exactly the
        # production sequence since 2026-07-28: the first frame stands the
        # gold master in for every not-yet-derived letter (which is why a
        # single cold render would make all three finishes identical), the
        # warm builds the real metals, the repaint shows them.
        compositor.render_offscreen(360.0, 1.0, day, tick)
        warm_pending_art()
        compositor.invalidate()
        image = compositor.render_offscreen(360.0, 1.0, day, tick)
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
    from config import constants, continents, dial, encyclopedia_ui, pantheon

    grouped = [
        glyph
        for glyphs in constants.RING_LETTER_GROUPS.values()
        for glyph in glyphs
    ]
    # The ADAPTIVE eye glyph (DOLLAR/EYE round, 2026-07-27) is the ONE
    # library entry the builder deliberately does not offer — it is the
    # Dollar card's own, resolved by the Settings art source and the
    # Shine toggle; custom rings pick one of the four explicit variants
    # instead (owner: "any of the four").
    library = set(constants.RING_LETTER_FILES) - {constants.RING_EYE_GLYPH}
    assert sorted(grouped) == sorted(library)
    assert len(grouped) == len(set(grouped))
    assert len(constants.RING_LETTER_GROUPS["Latin"]) == 26   # the full alphabet
    for glyph, filename in constants.RING_LETTER_FILES.items():
        # The eye stems are SOURCED (canonical Eye[_shine].png resolves
        # to _gem/_gpt on disk) — resolve exactly like the renderer does.
        gold = paths.art_file(dial.RING_LETTER_ART_DIR / filename)
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
    assert earth_region(continents.EARTH_POLE_LATITUDE, "asia") == "north_pole"
    assert earth_region(69.65, "europe") == "europe"      # Tromsø stays
    assert earth_region(44.82, "europe") == "europe"


def test_working_set_downscales_oversized_dial_art():
    """Owner 2026-07-15: the originals ship full-res, the WORKING SET
    serves the dial — the warmup builds a downscaled copy per
    oversized source (idempotent: a warm second run builds nothing),
    the ceiling follows the assets subtree, and trees the dial never
    draws stay untouched."""
    from pathlib import Path

    from config import continents, dial, encyclopedia_ui, pantheon, paths
    from render.asset_variants import (
        scaled_variant_file,
        warm_working_set,
        working_ceiling,
    )

    assets = paths.assets_dir()
    assert working_ceiling(
        assets / "celestial" / "earth" / "earth_clean_europe_day.png"
    ) == 800
    assert working_ceiling(assets / "weeks" / "x.png") == 800
    assert working_ceiling(assets / "calendars" / "x.png") == 1200
    assert working_ceiling(assets / "instrument" / "guide" / "x.png") is None
    assert working_ceiling(Path("C:/elsewhere/x.png")) is None
    warm_working_set()
    # Warm: the earth originals (1992 px) wear 800-wide copies…
    copy = scaled_variant_file(
        assets / "celestial" / "earth" / "earth_clean_north_pole_day.png", 800
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


def test_legend_highlighting_bolds_the_spine_only():
    """THE LEGEND BOLD LAW (owner 2026-07-26, CUBE.md — supersedes the
    2026-07-12 rainbow): the web's spine — virtue, vice, mood and
    WEEKDAY — pops in plain bold; color words and everything else read
    plain, and no colored span survives anywhere; hex notes never
    display."""
    from render.compositor import _article_body_html

    out = _article_body_html(
        "Patience heals Jealousy in green (#007E00), the mood called "
        "Renewal — the red planet pays in gold on Tuesday."
    )
    assert "#007E00" not in out
    assert "<b>Patience</b>" in out
    assert "<b>Jealousy</b>" in out
    assert "<b>Renewal</b>" in out
    assert "<b>Tuesday</b>" in out                  # the weekday spine
    assert 'style="color:' not in out               # the rainbow is dead
    assert ">green</b>" not in out
    assert ">red</b>" not in out
    assert ">gold</b>" not in out
    sr = _article_body_html("Strpljenje leči Ljubomoru, a zeleno je Obnova.")
    assert "<b>Strpljenje</b>" in sr
    assert "<b>Ljubomoru</b>" in sr
    assert "<b>Obnova</b>" in sr
    assert ">zeleno</b>" not in sr
    # LOWERCASE canon mentions burn too (owner report 2026-07-12), the
    # -šću instrumentals included.
    lower = _article_body_html(
        "njegov porok je gordost, a vrlina poniznost — gordošću pada"
    )
    assert "<b>gordost</b>" in lower
    assert "<b>poniznost</b>" in lower
    assert "<b>gordošću</b>" in lower
    # No spine terms at all: nothing bolds.
    plain = _article_body_html("A quiet field under an open sky.")
    assert "</b>" not in plain


def test_hover_teaser_law_truncates_to_the_thesis():
    """THE HOVER TEASER LAW (owner 2026-07-26, CUBE.md): an article
    hover speaks only the first LEGEND_TEASER_SENTENCES of the first
    paragraph, closed with an ellipsis; a short single-paragraph text
    passes whole; a leading [[Subhead]] marker is dropped."""
    from render.compositor import _teaser

    long = (
        "First sentence. Second sentence! Third sentence?"
        "\n\nSecond paragraph never shows."
    )
    out = _teaser(long)
    assert out == "First sentence. Second sentence! …"
    assert "Third" not in out and "Second paragraph" not in out
    # A short, single-paragraph article passes untouched — no ellipsis.
    assert _teaser("One line only.") == "One line only."
    # More paragraphs behind a short first one still earn the ellipsis.
    assert _teaser("One line.\n\nMore.").endswith("…")
    # Subhead markers never leak into a teaser.
    assert _teaser("[[The Figure]] Odin rules. And more. And more.\n\nX") \
        .startswith("Odin rules.")


def test_weekday_title_law_names_the_day_on_ghost_bodies():
    """THE WEEKDAY-TITLE LAW (owner, repeated many times — CUBE.md):
    EVERY weekday-bound badge hover names ITS weekday beside the
    title — ghosts included, any theme, any roster."""
    from render.assets import AssetCache
    from render.compositor import Compositor

    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    for body, day_name in (
        ("mars", "Tuesday"), ("venus", "Friday"), ("sun", "Sunday"),
    ):
        tip = comp._weekday_tooltip(body, active=False)
        assert day_name in tip, body


def test_learn_more_footer_names_both_roads():
    """THE HOVER TEASER LAW's footer (owner 2026-07-26): the clickable
    LEARN MORE anchor and the SPACE hint, on the domy:encyclopedia
    href the popup routes to the Spacebar jump."""
    from render.compositor import _learn_more_footer

    out = _learn_more_footer(lambda s: s)
    assert "domy:encyclopedia" in out
    assert "<u>Learn more</u>" in out
    assert "press SPACE" in out


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
    # The weekday pops bold per THE LEGEND BOLD LAW (2026-07-26).
    assert "Odin rules <b>Wednesday</b>." in sr
    # Round two (owner 2026-07-14): CENTERED, hugging its paragraph —
    # the gap above beats the gap below.
    assert "align='center'" in sr
    assert (
        f"margin-bottom:{encyclopedia_ui.ARTICLE_SUBHEAD_GAP_BELOW_PX}px" in sr
    )
    assert (
        encyclopedia_ui.ARTICLE_SUBHEAD_GAP_ABOVE_PX
        > encyclopedia_ui.ARTICLE_SUBHEAD_GAP_BELOW_PX
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
