"""Skin pack loading, merging, validation and DOMY round-trip."""

import json

import pytest

from config import defaults, paths
from skins import resolver
from skins.packs import SkinValidationError, load_pack, serialize_skin


def test_domy_round_trip():
    """serialize(DEFAULT_SKIN) → load == DEFAULT_SKIN, byte for byte."""
    folder = paths.bundled_skins_dir() / "domy"
    loaded = load_pack(folder, defaults.DEFAULT_SKIN)
    assert loaded == defaults.DEFAULT_SKIN


def test_morph_merges_only_the_ring():
    skin = resolver.resolve("morph")
    assert skin.name == "MORPH"
    assert skin.ring.letters == {12: "M", 16: "Π", 8: "H", 0: "Ω"}
    assert skin.ring.asset.name == "ring.png" and "morph" in str(skin.ring.asset)
    # Everything else inherits from the base.
    assert skin.hands == defaults.DEFAULT_SKIN.hands
    assert skin.background == defaults.DEFAULT_SKIN.background
    assert skin.weekday_set == defaults.DEFAULT_SKIN.weekday_set


def test_validation_lists_every_problem_at_once(tmp_path):
    (tmp_path / "skin.json").write_text(
        json.dumps(
            {
                "banana": {},
                "ring": {
                    "asset": "missing.png",
                    "fill": "#000000",
                    "text_color": "#FFFFFF",
                    "letter_color": "#FFD700",
                    "typo_field": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SkinValidationError) as excinfo:
        load_pack(tmp_path, defaults.DEFAULT_SKIN)
    problems = "\n".join(excinfo.value.problems)
    assert "banana" in problems          # unknown section
    assert "missing.png" in problems     # absent asset
    assert "typo_field" in problems      # unknown field
    assert "width_fraction" in problems  # required field missing


def test_unknown_skin_name_fails_loudly():
    with pytest.raises(KeyError, match="atlantis"):
        resolver.resolve("atlantis")


def test_discover_finds_both_bundled_packs():
    found = resolver.discover()
    assert "domy" in found and "morph" in found


def test_serialize_is_json_ready():
    folder = paths.bundled_skins_dir() / "domy"
    payload = serialize_skin(defaults.DEFAULT_SKIN, folder)
    json.dumps(payload)                  # must not raise
    assert payload["ring"]["asset"] == "dial/ring.png"
    assert payload["noon_marker"]["asset"] is None
    assert payload["pointer"] == "hexa"
    assert payload["umbra_contrast"] == "full"
    assert payload["palette_style"] == "paint"
    assert payload["solar_rotation"] is True
    assert payload["octa_slot"] == "time"


def test_pack_display_choices_merge(tmp_path):
    (tmp_path / "skin.json").write_text(
        json.dumps(
            {
                "pointer": "octa",
                "umbra_contrast": "soft",
                "palette_style": "light",
                "solar_rotation": False,
                "octa_slot": "day_length",
            }
        ),
        encoding="utf-8",
    )
    skin = load_pack(tmp_path, defaults.DEFAULT_SKIN)
    assert skin.pointer == "octa"
    assert skin.umbra_contrast == "soft"
    assert skin.palette_style == "light"
    assert skin.solar_rotation is False
    assert skin.octa_slot == "day_length"


def test_pack_rejects_unknown_display_choices(tmp_path):
    (tmp_path / "skin.json").write_text(
        json.dumps({"pointer": "banana", "umbra_contrast": "extreme"}),
        encoding="utf-8",
    )
    with pytest.raises(SkinValidationError) as excinfo:
        load_pack(tmp_path, defaults.DEFAULT_SKIN)
    problems = "\n".join(excinfo.value.problems)
    assert "banana" in problems
    assert "extreme" in problems