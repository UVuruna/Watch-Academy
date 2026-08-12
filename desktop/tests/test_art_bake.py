"""THE ART BAKERY's teeth — the doubt the owner asked us to remove.

His order, 2026-08-12, named the problem before it named the solution:
with masters and shipped art in one tree, nobody could tell by looking
which image had been optimized and which had not. `make_art_bake.py`
answers that by construction — masters in `masters/`, shipped art in
`shared/assets/` — but a construction nothing checks is a convention,
and conventions decay. These are the checks.

Two kinds live here:

* **Unit teeth** on the bakery's own decisions (which area gets which
  ceiling, what is exempt, that a bake actually downscales and
  re-encodes, that an unchanged master is not re-baked).
* **THE SHIPPED-TREE TOOTH** — `test_no_shipped_art_exceeds_its_ceiling`
  walks the real committed tree and fails on any file bigger than its
  own area allows. That is the one that would have caught a forgotten
  bake, and the one that keeps the 4.1 GB from creeping back.
"""

import json
from pathlib import Path

import pytest
from PIL import Image

from config import bakery, defaults, paths
from setup import make_art_bake


# ═══════════════════════════ THE CEILING PLAN ═══════════════════════════
def test_the_bakery_has_no_ceilings_of_its_own():
    """The plan is READ from the runtime's table, never restated. A
    second list is how the shipped tree and the program's idea of "big
    enough" drift apart without either side being wrong."""
    source = Path(make_art_bake.__file__).read_text("utf-8")
    assert "WORKING_SET_CEILINGS" in source
    for ceiling in {512}:
        assert f"= {ceiling}" not in source, (
            "the bakery restated a ceiling instead of reading the table"
        )


@pytest.mark.parametrize(
    "relative, expected",
    [
        ("weeks/faith/bible/primary/colored/Perun_gem.png", 512),
        ("archetypes/crosses/primary/colored/Distrust_gpt.png", 512),
        ("calendars/zodiac/chinese/primary/colored/Tiger_gem.png", 512),
        # 0, not 800: re-encoded but never resized — the owner's Globe
        # decree of 2026-07-15. The FIRST bake of the bakery round DID
        # shrink these to 800 and `test_skins.py::
        # test_earth_pole_regions_full_res_and_latitude_override` caught
        # it, which is why this row is spelled out rather than inferred.
        ("celestial/earth/world.png", 0),
        ("celestial/era/Starry_Autumn_gem.png", 512),
        ("celestial/eclipse/Solar_Total.png", 512),
        ("instrument/hands/classic/hours.png", None),
        ("logo.svg", None),
    ],
)
def test_each_area_gets_its_own_ceiling(relative, expected):
    assert make_art_bake._ceiling_for(relative) == expected


def test_a_full_resolution_area_is_encoded_but_never_resized(tmp_path):
    """The regression this round shipped once and had to take back: a
    ceiling of 0 must compress and leave every pixel where it is."""
    source = _master(tmp_path, size=(1992, 1992))
    target = tmp_path / "globe.webp"
    width, height, size = make_art_bake.bake_one(
        str(source), str(target), 0, bakery.ART_BAKE_QUALITY
    )
    assert (width, height) == (1992, 1992), "a full-resolution area was resized"
    assert size < source.stat().st_size, "it was not compressed either"


def test_the_letter_plates_are_exempt():
    """THE ONE PLATE LAW's gold masters. The transformer runs an oklab
    pass over these exact pixels into 34 finishes — a lossy encode here
    would not soften one image, it would seed artifacts into every
    glyph the program ever draws."""
    assert make_art_bake._is_verbatim("instrument/letters/latin/A.png")
    assert not make_art_bake._is_verbatim("weeks/faith/bible/x.png")


# ═══════════════════════════ BAKING ONE FILE ═══════════════════════════
def _master(tmp_path: Path, size=(2000, 2000)) -> Path:
    source = tmp_path / "big.png"
    Image.new("RGBA", size, (200, 40, 40, 255)).save(source)
    return source


def test_a_bake_downscales_to_the_ceiling_and_writes_webp(tmp_path):
    source = _master(tmp_path)
    target = tmp_path / "out.webp"
    width, height, size = make_art_bake.bake_one(
        str(source), str(target), 512, bakery.ART_BAKE_QUALITY
    )
    assert (width, height) == (512, 512)
    assert target.exists() and size == target.stat().st_size
    assert size < source.stat().st_size
    with Image.open(target) as baked:
        assert baked.format == "WEBP"


def test_a_master_under_its_ceiling_is_not_upscaled(tmp_path):
    source = _master(tmp_path, size=(300, 300))
    width, height, _ = make_art_bake.bake_one(
        str(source), str(tmp_path / "out.webp"), 800, bakery.ART_BAKE_QUALITY
    )
    assert (width, height) == (300, 300)


def test_a_ceilingless_file_is_copied_byte_for_byte(tmp_path):
    source = _master(tmp_path, size=(120, 120))
    target = tmp_path / "copy.png"
    make_art_bake.bake_one(
        str(source), str(target), None, bakery.ART_BAKE_QUALITY
    )
    assert target.read_bytes() == source.read_bytes()


# ═══════════════════════════ INCREMENTAL ═══════════════════════════
def test_an_unchanged_master_is_not_rebaked(tmp_path, monkeypatch):
    masters = tmp_path / "masters"
    assets = tmp_path / "assets"
    (masters / "weeks").mkdir(parents=True)
    Image.new("RGBA", (1000, 1000)).save(masters / "weeks" / "A_gem.png")
    monkeypatch.setattr(paths, "masters_dir", lambda: masters)
    monkeypatch.setattr(paths, "assets_dir", lambda: assets)

    assert make_art_bake.bake() == 1
    assert (assets / "weeks" / "A_gem.webp").exists()
    manifest = json.loads(
        (assets / make_art_bake.MANIFEST_NAME).read_text("utf-8")
    )
    assert manifest["files"]["weeks/A_gem.png"]["width"] == 512

    assert make_art_bake.bake() == 0, "an unchanged master was baked twice"
    assert make_art_bake.bake(force=True) == 1


def test_a_changed_master_is_rebaked(tmp_path, monkeypatch):
    masters = tmp_path / "masters"
    assets = tmp_path / "assets"
    masters.mkdir()
    (masters / "weeks").mkdir()
    Image.new("RGBA", (1000, 1000), (1, 2, 3, 255)).save(
        masters / "weeks" / "A_gem.png"
    )
    monkeypatch.setattr(paths, "masters_dir", lambda: masters)
    monkeypatch.setattr(paths, "assets_dir", lambda: assets)
    make_art_bake.bake()

    Image.new("RGBA", (1000, 1000), (9, 9, 9, 255)).save(
        masters / "weeks" / "A_gem.png"
    )
    assert make_art_bake.bake() == 1


def test_no_masters_folder_is_not_an_error(tmp_path, monkeypatch):
    """A clone without the masters is a complete, working program —
    that is the entire point of baking the shipped tree here."""
    monkeypatch.setattr(paths, "masters_dir", lambda: None)
    assert make_art_bake.bake() == 0


# ═══════════════════════════ THE SINGLE DOOR ═══════════════════════════
def test_art_file_prefers_the_baked_webp(tmp_path, monkeypatch):
    (tmp_path / "x_gem.png").write_bytes(b"png")
    (tmp_path / "x_gem.webp").write_bytes(b"webp")
    resolved = paths.art_file(tmp_path / "x.png")
    assert resolved.suffix == ".webp"


def test_art_file_still_answers_with_png_where_no_bake_exists(tmp_path):
    """A mixed tree is legal FOREVER: the migration needs no flag day,
    and a PNG the owner drops in by hand keeps working."""
    paths.reset_art_file_cache()
    (tmp_path / "y_gem.png").write_bytes(b"png")
    assert paths.art_file(tmp_path / "y.png").suffix == ".png"


def test_an_already_suffixed_path_reaches_the_extension_probe(tmp_path):
    """The regression this rewrite exists to prevent: `art_file` used to
    return a `_gem`/`_gpt` path untouched, which would have left every
    already-suffixed config entry asking for a PNG the bakery replaced."""
    paths.reset_art_file_cache()
    (tmp_path / "z_gpt.webp").write_bytes(b"webp")
    assert paths.art_file(tmp_path / "z_gpt.png").suffix == ".webp"


# ═══════════════════════════ THE SHIPPED TREE ═══════════════════════════
def test_no_shipped_art_exceeds_its_ceiling():
    """THE tooth. Walks the real committed tree: every file in a
    ceiling'd area must already be at or under that ceiling, because
    the bakery put it there. A forgotten bake, a master committed by
    hand, or a ceiling lowered without a re-run all fail HERE — in the
    session that did it — instead of on a user's machine as a slow
    first launch.

    Skipped when an area is empty (a checkout mid-migration)."""
    assets = paths.assets_dir()
    offenders: list[str] = []
    checked = 0
    for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items():
        root = assets / subtree
        if not root.is_dir():
            continue
        # A FULL_RESOLUTION area keeps its runtime ceiling (the working
        # set still makes a small copy to draw from) while the SHIPPED
        # file stays full size on the owner's decree. Read from the
        # bakery's own list rather than restated here, so the two can
        # never disagree about which areas those are.
        if make_art_bake._ceiling_for(subtree) == 0:
            continue
        for path in root.rglob("*"):
            if path.suffix.lower() not in (".png", ".webp", ".jpg", ".jpeg"):
                continue
            with Image.open(path) as image:
                width, height = image.size
            checked += 1
            if max(width, height) > ceiling:
                offenders.append(
                    f"{path.relative_to(assets).as_posix()} "
                    f"{width}x{height} > {ceiling}"
                )
    if checked == 0:
        pytest.skip("no art on disk in any ceiling'd area")
    assert not offenders, (
        f"{len(offenders)} shipped file(s) above their area's ceiling — "
        "re-run `python -m setup.make_art_bake`:\n  "
        + "\n  ".join(sorted(offenders)[:20])
    )
