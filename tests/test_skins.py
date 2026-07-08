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
