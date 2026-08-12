"""THE TOOTH THAT WAS MISSING — the startup passes may not re-open the
asset tree they already know.

THE REPEAT LAW, applied to itself. On 2026-08-09 a round shipped commit
0.14.872 titled *"Measured — cold responsiveness under the owner's
3-second bar"*. What it measured was ONE watch on the DEFAULT skin in an
isolated empty user directory: 0.918 s to a responsive GUI thread. What
the owner had reported was `profiling.json`'s `"Working set warmup"` at
71.7 s — a number that round never measured, said so only in a closing
paragraph of `app/__about/warm.md`, and closed as done anyway. Three
days later the same counter read **91.6 s**, and nothing in this suite
could say so, because no test in it measured the thing the owner
actually reported.

That is what these tests are for. They do not measure SECONDS — a
timing threshold on a shared machine is a flaky test, and a flaky test
gets deleted, which is how a suite loses a tooth. They measure the
CAUSE: how many times the startup passes open a file they were already
told about. Cold, that count is the file count. Warm, it must be ZERO.
"""

import json
import os
import re
import tempfile
from pathlib import Path

import pytest

from config import defaults, paths
from render import asset_index, asset_variants, letter_bake, raster_store


@pytest.fixture
def isolated_user_dir(monkeypatch):
    """A throwaway user directory, so a test never reads or writes the
    owner's live index and cache."""
    with tempfile.TemporaryDirectory(prefix="wa_startup_") as folder:
        monkeypatch.setattr(
            paths, "settings_path",
            lambda watch_index=1: Path(folder) / "settings.json",
        )
        asset_index.forget()
        letter_bake.refresh()
        yield Path(folder)
    asset_index.forget()


class _OpenCounter:
    """Counts every `open` and every `QImageReader` construction aimed
    at the asset tree — the two ways a startup pass pays real I/O."""

    def __init__(self, monkeypatch):
        self.opens: list[str] = []
        self.headers: list[str] = []
        root = str(paths.assets_dir())
        real_open = open

        def counting_open(file, *args, **kwargs):
            if str(file).startswith(root):
                self.opens.append(str(file))
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr("builtins.open", counting_open)

        real_reader = asset_variants.QImageReader

        def counting_reader(*args, **kwargs):
            if args and str(args[0]).startswith(root):
                self.headers.append(str(args[0]))
            return real_reader(*args, **kwargs)

        monkeypatch.setattr(asset_variants, "QImageReader", counting_reader)

    @property
    def total(self) -> int:
        return len(self.opens) + len(self.headers)


# ═══════════════════════ THE INDEX'S OWN CONTRACT ═══════════════════════


def test_a_warm_index_reopens_nothing(isolated_user_dir):
    """The whole fix in one assertion: build the index, forget it, load
    it from disk, refresh again — and not one file is re-read."""
    first_known, first_read = asset_index.refresh()
    assert first_known > 0, "the asset tree is empty — check paths.assets_dir"
    assert first_read == first_known, (
        "a cold index must read every file exactly once, "
        f"read {first_read} of {first_known}"
    )

    asset_index.forget()                      # a NEW process, same disk
    second_known, second_read = asset_index.refresh()
    assert second_known == first_known
    assert second_read == 0, (
        "THE 91.6-SECOND BUG: a launch re-read "
        f"{second_read} files whose (size, mtime_ns) had not changed. "
        "Every one of those is a disk seek the previous launch already "
        "paid, and 2,511 of them on an ordinary HDD is the owner's "
        "91.6-second start."
    )


def test_a_changed_file_is_re_read_and_nothing_else_is(isolated_user_dir):
    """The index may only skip files it is still RIGHT about. Touching
    one source's content must re-read exactly that one."""
    asset_index.refresh()
    asset_index.forget()

    victim = next(iter(sorted((paths.assets_dir() / "instrument").rglob("*.png"))))
    before = asset_index.fingerprint(victim)
    original = victim.read_bytes()
    try:
        victim.write_bytes(original + b"\x00" * 8)   # size AND mtime change
        known, read = asset_index.refresh()
        assert read == 1, f"expected exactly the touched file, re-read {read}"
        assert asset_index.fingerprint(victim) != before, (
            "a changed source kept its old content key — every cache "
            "entry derived from it would now be served stale"
        )
    finally:
        victim.write_bytes(original)
        asset_index.forget()


def test_a_version_stale_index_is_discarded_not_trusted(isolated_user_dir):
    """A record shape this build does not understand is thrown away. One
    slow launch is cheap; a misread record paints wrong pixels."""
    asset_index.refresh()
    path = asset_index.index_path()
    stored = json.loads(path.read_text(encoding="utf-8"))
    stored["version"] = asset_index.INDEX_VERSION + 99
    path.write_text(json.dumps(stored), encoding="utf-8")

    asset_index.forget()
    _known, read = asset_index.refresh()
    assert read > 0, "a version-stale index was TRUSTED instead of rebuilt"


def test_a_corrupt_index_is_survivable(isolated_user_dir):
    """Half a JSON file must cost a slow launch, never a dead one."""
    asset_index.refresh()
    asset_index.index_path().write_text("{not json at all", encoding="utf-8")
    asset_index.forget()
    _known, read = asset_index.refresh()     # must not raise
    assert read > 0


def test_the_index_never_answers_for_a_path_outside_assets(isolated_user_dir):
    """`None` means "not mine", and it is what keeps `raster_store`'s own
    memo in service for user-directory files and test fixtures."""
    asset_index.refresh()
    outside = isolated_user_dir / "settings.json"
    outside.write_text("{}", encoding="utf-8")
    assert asset_index.fingerprint(outside) is None
    assert asset_index.image_size(outside) is None


# ═══════════════════ THE PASSES THAT USED TO PAY TWICE ═══════════════════


def test_the_working_set_sweep_opens_no_png_when_the_index_is_warm(
    isolated_user_dir, monkeypatch
):
    """`warm_working_set` used to call `QImageReader` on every PNG in
    five subtrees — 2,511 files, 3.76 GB — to read one integer, on every
    launch, and the owner's own log proved it built NOTHING while doing
    it: `[91.6s] working set complete — 961 oversized sources, 0 built
    cold`. With the index warm it must not open a single one."""
    asset_index.refresh()
    counter = _OpenCounter(monkeypatch)
    asset_variants.warm_working_set()
    assert counter.headers == [], (
        f"{len(counter.headers)} PNG headers were re-read from disk; "
        f"first offenders: {counter.headers[:3]}"
    )


def test_the_working_set_sweep_still_finds_every_oversized_source(
    isolated_user_dir
):
    """Speed that changed the ANSWER would be worthless. The
    index-served sweep must select exactly the set the old
    open-every-file loop selected."""
    asset_index.refresh()
    from PySide6.QtGui import QImageReader

    expected = {
        source
        for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items()
        for source in paths.art_files_under(paths.assets_dir() / subtree)
        if (size := QImageReader(str(source)).size()).isValid()
        and size.width() > ceiling
    }
    served = {
        source
        for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items()
        for source in paths.art_files_under(paths.assets_dir() / subtree)
        if (known := asset_index.image_size(source)) is not None
        and known[0] > ceiling
    }
    assert served == expected, (
        "the index disagrees with the file headers about which sources "
        f"are oversized: {sorted(served ^ expected)[:5]}"
    )


def test_the_cache_gc_roster_costs_no_file_opens(
    isolated_user_dir, monkeypatch
):
    """`_collect_cache_garbage` used to rglob the tree and fingerprint
    (open + read 64 KiB of) EVERY png/svg/jpg in it, per launch, purely
    to decide which cache files were corpses."""
    asset_index.refresh()
    counter = _OpenCounter(monkeypatch)
    roster = {
        raster_store.source_prefix(Path(path))
        for path in asset_index.fingerprints_by_path()
    }
    assert len(roster) > 0
    assert counter.opens == [], (
        f"{len(counter.opens)} assets were opened to build the GC "
        f"roster; first offenders: {counter.opens[:3]}"
    )


def test_source_prefix_is_served_by_the_index(isolated_user_dir, monkeypatch):
    """The hook is why the Encyclopedia warm needed no edit of its own:
    it resolves hundreds of paths through `source_prefix`, and each of
    those must end at a dict lookup."""
    asset_index.refresh()
    sample = sorted((paths.assets_dir() / "instrument").rglob("*.png"))[:40]
    assert sample, "no instrument plates found"
    counter = _OpenCounter(monkeypatch)
    for path in sample:
        assert raster_store.source_prefix(path)
    assert counter.opens == [], (
        f"{len(counter.opens)} of {len(sample)} path resolutions opened "
        "their source file"
    )


def test_the_fingerprint_recipe_and_the_index_agree(isolated_user_dir):
    """`raster_store.compute_fingerprint` is the recipe, the index is the
    memo. A memo that disagrees with its recipe would silently re-key
    every derived image in the program."""
    asset_index.refresh()
    for path in sorted((paths.assets_dir() / "instrument").rglob("*.png"))[:25]:
        assert asset_index.fingerprint(path) == \
            raster_store.compute_fingerprint(path), path


# ═══════════════════════════ THE LETTER BAKE ═══════════════════════════


def test_every_letter_plate_ships_every_eager_finish():
    """Owner order 2026-08-12: all the letters, in the colours actually
    used, at setup. This fails when a plate is added or re-drawn and
    `python -m setup.make_letter_bake` was not re-run — the program
    stays CORRECT either way (a miss derives live), but the promise
    that a launch computes nothing is broken, and a broken promise
    nobody is told about is how this round's own bug happened.

    EAGER, not every, since the art-bakery round of the same day: the
    owner halved the matrix to `defaults.EAGER_BAKED_SHADES` because
    most of what it dropped was duplicate ramps and the rest belongs to
    custom rings nobody has built yet. The roster is read from the
    config table rather than restated here, so this tooth follows the
    decree instead of having to be remembered alongside it."""
    from render.asset_recolor import letter_cache_name

    plates = sorted((paths.assets_dir() / "instrument" / "letters").rglob("*.png"))
    assert plates, "the plate library is empty"
    finishes = [
        (metal, shade)
        for metal, shades in defaults.EAGER_BAKED_SHADES.items()
        for shade in shades
    ]
    missing = [
        f"{master.stem} {metal}/{shade}"
        for master in plates
        for metal, shade in finishes
        if letter_bake.baked_file(letter_cache_name(master, metal, shade)) is None
    ]
    assert missing == [], (
        f"{len(missing)} of {len(plates) * len(finishes)} letter finishes "
        "are not baked — run `python -m setup.make_letter_bake`. "
        f"First: {missing[:5]}"
    )


def test_the_eager_roster_names_only_real_shades():
    """A typo in `EAGER_BAKED_SHADES` would not fail loudly — it would
    bake sixteen finishes instead of seventeen and leave one colour
    deriving live forever, which is the silent-slowness failure the
    whole bake exists to end."""
    for metal, shades in defaults.EAGER_BAKED_SHADES.items():
        assert metal in defaults.METAL_SHADES, metal
        for shade in shades:
            assert shade in defaults.METAL_SHADES[metal], f"{metal}/{shade}"


def test_a_baked_hit_records_no_recipe(isolated_user_dir):
    """The bake must SKIP the lazy ledger, not merely pre-fill it: a
    recorded recipe is one the warm thread dutifully rebuilds, which is
    exactly the work the bake exists to remove."""
    from render import asset_recolor

    asset_index.refresh()
    plate = paths.assets_dir() / "instrument" / "letters" / "latin" / "A.png"
    if not plate.exists():                      # library renamed — say so
        pytest.skip(f"{plate.name} is not in the library")
    asset_recolor._PENDING_VARIANTS.clear()
    resolved = asset_recolor.jewel_metal_path(plate, "gold")
    assert resolved.exists(), "a baked finish must resolve to a real file"
    assert letter_bake.bake_dir() in resolved.parents, (
        f"resolved to {resolved}, not to the shipped bake"
    )
    assert asset_recolor._PENDING_VARIANTS == {}, (
        "a baked hit still recorded a recipe — the warm thread would "
        "rebuild pixels that already shipped"
    )


def test_a_stale_bake_cannot_paint_a_wrong_letter(isolated_user_dir):
    """The name IS the manifest. Bump the recolor version and every
    baked file must stop matching — no manifest to forget, no way to
    serve last month's pixels."""
    from render import asset_recolor

    plate = paths.assets_dir() / "instrument" / "letters" / "latin" / "A.png"
    if not plate.exists():
        pytest.skip(f"{plate.name} is not in the library")
    current = asset_recolor.letter_cache_name(plate, "gold", "classic")
    assert letter_bake.baked_file(current) is not None

    # Bump the version WITHOUT naming the extension. Spelling it out
    # (`_v6.png` -> `_v7.png`) silently stopped bumping anything the day
    # the bake became WebP: `str.replace` found no match, the name went
    # through unchanged, and the assertion below then claimed the CURRENT
    # file was missing. A test that can quietly stop testing is worse
    # than no test — the version now moves by regex, on the version.
    bumped = re.sub(
        rf"_v{defaults.METAL_SWAP_VERSION}(\.\w+)$",
        rf"_v{defaults.METAL_SWAP_VERSION + 1}\1",
        current,
    )
    assert bumped != current, "the version bump matched nothing"
    assert letter_bake.baked_file(bumped) is None, (
        "a bumped METAL_SWAP_VERSION still hit the old bake — the "
        "recolor math would change and the dial would not notice"
    )


def test_the_bake_survives_its_own_absence(isolated_user_dir, monkeypatch):
    """Delete the folder and the program is slower, never broken."""
    monkeypatch.setattr(
        letter_bake, "bake_dir", lambda: Path(os.devnull) / "gone"
    )
    letter_bake.refresh()
    assert letter_bake.baked_count() == 0
    assert letter_bake.baked_file("anything.png") is None
    letter_bake.refresh()
