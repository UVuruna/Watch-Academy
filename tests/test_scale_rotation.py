"""THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20, sealed
alongside Rule #19 "Compute, Don't Generate"): beside any canonical
asset `<dir>/<Name>.png`, additional versions live as `<dir>/<Name>
_v2.png`-style suffix siblings OR same-named files inside `<dir>/alt/`
— both pools merge into one daily rotation, `config.defaults.
rotating_art_file`. The Scale badge's Judas/Lucifer rotation (owner
decree 2026-07-19/20, CANON.md one-image-one-place amendment — Judas-
Lucifer is a MAIN theme, "koje cemo koristiti na smenu": every being
lives between excessive self-criticism and excessive self-love, so
both poles keep MULTIPLE generated versions instead of freezing on one
master) is the family the convention was generalized FROM, and keeps
its own naming-zoo tolerance (more than one valid stem per figure, a
`glass/` register instead of `alt/`) as a thin caller of the shared
`_rotation_candidates`/`_pick_rotation` machinery. These tests drive
both the generic resolver and the Scale-specific wrapper against
SYNTHETIC tmp trees — never the real bundled assets — so the naming
tolerance and the day-by-day rotation math are pinned independently of
whatever art happens to be on disk today."""

from datetime import date

from config import defaults


# --- The generic resolver (era, tetramorph, and any future family) --------------


def test_rotating_art_file_pool_is_base_plus_suffix_plus_alt(tmp_path):
    """THE CONVENTION itself: the canonical file, its `_v2`-style
    siblings, AND the same-named file inside `alt/` all feed ONE pool."""
    canonical = tmp_path / "Age_of_Light.png"
    canonical.write_bytes(b"")
    (tmp_path / "Age_of_Light_v2.png").write_bytes(b"")
    alt = tmp_path / "alt"
    alt.mkdir()
    (alt / "Age_of_Light.png").write_bytes(b"")
    picks = {
        defaults.rotating_art_file(canonical, date(2026, 7, 20 + offset))
        for offset in range(6)
    }
    assert picks == {
        canonical, tmp_path / "Age_of_Light_v2.png", alt / "Age_of_Light.png",
    }


def test_rotating_art_file_is_deterministic_and_advances(tmp_path):
    """The SAME date always yields the SAME file; with more than one
    candidate, consecutive dates advance through the set."""
    canonical = tmp_path / "Judas.png"
    canonical.write_bytes(b"")
    (tmp_path / "Judas_v2.png").write_bytes(b"")
    (tmp_path / "Judas_v3.png").write_bytes(b"")
    day = date(2026, 7, 20)
    assert defaults.rotating_art_file(
        canonical, day
    ) == defaults.rotating_art_file(canonical, day)
    picks = {
        defaults.rotating_art_file(canonical, date(2026, 7, 20 + o)).name
        for o in range(3)
    }
    assert len(picks) == 3


def test_rotating_art_file_alt_alone_is_enough_to_rotate(tmp_path):
    """A family with no `_v2` siblings, only an `alt/` file sharing the
    canonical's OWN name, still rotates between exactly two candidates
    — the pool is never suffix-only."""
    canonical = tmp_path / "Starry_Summer.png"
    canonical.write_bytes(b"")
    alt = tmp_path / "alt"
    alt.mkdir()
    (alt / "Starry_Summer.png").write_bytes(b"")
    picks = {
        defaults.rotating_art_file(canonical, date(2026, 7, 20 + o))
        for o in range(4)
    }
    assert picks == {canonical, alt / "Starry_Summer.png"}


def test_rotating_art_file_alt_ignores_unrelated_names(tmp_path):
    """`alt/` is scoped to the SAME stem — a different figure's alt
    file sitting beside it never joins this pool (the mirroring rule
    `test_alt_folders_mirror_their_parent_names` also pins on disk)."""
    canonical = tmp_path / "Eagle.png"
    canonical.write_bytes(b"")
    alt = tmp_path / "alt"
    alt.mkdir()
    (alt / "Lion.png").write_bytes(b"")
    assert defaults.rotating_art_file(canonical, date(2026, 7, 20)) == canonical


def test_rotating_art_file_single_candidate_never_rotates(tmp_path):
    canonical = tmp_path / "Anno_Lucis.png"
    canonical.write_bytes(b"")
    for offset in range(3):
        assert defaults.rotating_art_file(
            canonical, date(2026, 7, 20 + offset)
        ) == canonical


def test_rotating_art_file_missing_canonical_is_none(tmp_path):
    """No master at all -> None (the caller keeps its own fallback) —
    graceful-absent, never a crash."""
    assert defaults.rotating_art_file(
        tmp_path / "Nothing.png", date(2026, 7, 20)
    ) is None


# --- The Scale badge (the family the convention was generalized from) -----------


def test_scale_candidates_tolerate_the_naming_zoo(tmp_path):
    """The owner's batches landed under more than one stem (the
    canonical `_Triangle` master beside a later lowercase refresh) and
    more than one suffix spelling (a bare `_v` instead of a proper
    `_v2`) — `_rotation_candidates_in` must find every real version and
    reject anything that merely starts with the stem."""
    names = [
        "Judas_Triangle.png", "Judas_Triangle_v2.png",
        "judas.png", "judas_v.png", "judas_v1.png",
        "judas_v2.png", "judas_v3.png",
        "judas_alt.png",       # NOT a version suffix — must be rejected
        "judasx.png",          # NOT a version suffix — must be rejected
        "lucifer.png",         # a different figure entirely
        "readme.txt",          # wrong extension
    ]
    for name in names:
        (tmp_path / name).write_bytes(b"")
    found = {
        path.name
        for path in defaults._rotation_candidates_in(
            tmp_path, ("Judas_Triangle", "judas")
        )
    }
    assert found == {
        "Judas_Triangle.png", "Judas_Triangle_v2.png",
        "judas.png", "judas_v.png", "judas_v1.png",
        "judas_v2.png", "judas_v3.png",
    }


def test_scale_candidates_search_the_glass_register_too(tmp_path):
    """The metal-cameo root and the stained-glass `glass/` subfolder
    are two parallel batches of the SAME two figures — both count
    toward one rotation."""
    (tmp_path / "Judas_Triangle.png").write_bytes(b"")
    glass = tmp_path / "glass"
    glass.mkdir()
    (glass / "Judas_Triangle.png").write_bytes(b"")
    (glass / "Judas_Triangle_v2.png").write_bytes(b"")
    found = defaults._rotation_candidates(
        (tmp_path, glass), ("Judas_Triangle", "judas")
    )
    assert len(found) == 3
    assert {p.parent.name for p in found} == {tmp_path.name, "glass"}


def test_scale_variant_file_is_deterministic(tmp_path, monkeypatch):
    """The SAME date must always yield the SAME file — a live dial
    that flickered between versions within one day would be worse than
    no rotation at all."""
    monkeypatch.setattr(defaults, "SCALE_ART_DIR", tmp_path)
    for suffix in ("", "_v1", "_v2"):
        (tmp_path / f"judas{suffix}.png").write_bytes(b"")
    day = date(2026, 7, 20)
    first = defaults.scale_variant_file("Judas", day)
    second = defaults.scale_variant_file("Judas", day)
    assert first is not None
    assert first == second


def test_scale_variant_file_advances_on_consecutive_dates(tmp_path, monkeypatch):
    """With more than one version on disk, consecutive days must show
    a different file — otherwise there is no rotation to speak of."""
    monkeypatch.setattr(defaults, "SCALE_ART_DIR", tmp_path)
    for suffix in ("", "_v1", "_v2"):
        (tmp_path / f"judas{suffix}.png").write_bytes(b"")
    picks = {
        defaults.scale_variant_file("Judas", date(2026, 7, 20 + offset)).name
        for offset in range(3)
    }
    # Three versions, three consecutive days -> all three get shown
    # (day-ordinal modulo 3 cycles through every index exactly once).
    assert len(picks) == 3


def test_scale_variant_file_keeps_judas_and_lucifer_in_step(tmp_path, monkeypatch):
    """Judas and Lucifer are called with the SAME date — with matching
    version counts per figure, the SAME relative slot (base/_v1/_v2)
    must be picked for both on any given day, so the pair always
    advances together."""
    monkeypatch.setattr(defaults, "SCALE_ART_DIR", tmp_path)
    for stem in ("judas", "lucifer"):
        for suffix in ("", "_v1", "_v2"):
            (tmp_path / f"{stem}{suffix}.png").write_bytes(b"")
    for offset in range(5):
        day = date(2026, 7, 20 + offset)
        judas = defaults.scale_variant_file("Judas", day)
        lucifer = defaults.scale_variant_file("Lucifer", day)
        judas_suffix = judas.stem[len("judas"):]
        lucifer_suffix = lucifer.stem[len("lucifer"):]
        assert judas_suffix == lucifer_suffix


def test_scale_variant_file_graceful_with_one_or_zero_files(tmp_path, monkeypatch):
    """Missing everything falls back to the caller's own default (None
    here); exactly one file on disk means there is nothing to rotate —
    the same file shows every day."""
    monkeypatch.setattr(defaults, "SCALE_ART_DIR", tmp_path)
    assert defaults.scale_variant_file("Judas", date(2026, 7, 20)) is None
    only = tmp_path / "judas.png"
    only.write_bytes(b"")
    assert defaults.scale_variant_file("Judas", date(2026, 7, 20)) == only
    assert defaults.scale_variant_file("Judas", date(2026, 7, 21)) == only


def test_scale_variant_file_graceful_when_the_directory_is_missing(tmp_path, monkeypatch):
    """A source with no scale/ folder at all (not expected in practice,
    but the resolver must not raise) reads as zero candidates -> None,
    same as an empty existing folder."""
    monkeypatch.setattr(defaults, "SCALE_ART_DIR", tmp_path / "does_not_exist")
    assert defaults.scale_variant_file("Judas", date(2026, 7, 20)) is None
