"""The Scale badge's Judas/Lucifer ROTATION (owner decree 2026-07-19/20,
CANON.md one-image-one-place amendment — Judas-Lucifer is a MAIN theme,
"koje cemo koristiti na smenu": every being lives between excessive
self-criticism and excessive self-love, so both poles keep MULTIPLE
generated versions instead of freezing on one master. These tests drive
`config.defaults.scale_variant_file`/`_scale_candidates` against
SYNTHETIC tmp trees — never the real bundled assets — so the owner's
naming-zoo tolerance and the day-by-day rotation math are pinned
independently of whatever art happens to be on disk today."""

from datetime import date

from config import defaults


def test_scale_candidates_tolerate_the_naming_zoo(tmp_path):
    """The owner's batches landed under more than one stem (the
    canonical `_Triangle` master beside a later lowercase refresh) and
    more than one suffix spelling (a bare `_v` instead of a proper
    `_v2`) — `_scale_candidates` must find every real version and
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
        for path in defaults._scale_candidates(
            (tmp_path,), ("Judas_Triangle", "judas")
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
    found = defaults._scale_candidates(
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
