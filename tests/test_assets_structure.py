"""The assets/ tree's own structural law (owner decree 2026-07-19, DUAL
FLATTEN round — "hocu broj 1 tu istu strukturu SVUDA"): a weekday theme's
art lives FLAT inside its register folder — no `dual/` subfolder
anywhere, no matter how deeply nested. WHO a file is (the Sunday dual, a
pantheon seat, a servant face) is written ONLY in config tables
(`WEEKDAY_DUAL_FILES`, `WEEKDAY_PANTHEON`) — never encoded as a folder
segment. These tests walk the real disk tree so the chaos the owner
flagged (`research/ASSETS_AUDIT.md`) can never regrow unnoticed."""

from pathlib import Path

from config import paths

# The REAL post-flatten variant-folder vocabulary (owner DUAL FLATTEN
# 2026-07-19), confirmed by a full walk of both art sources — every
# folder one level or more below a theme family is one of these, never
# anything else:
#   primary   — the base/bronze register every theme has
#   colored   — the full-color sibling register (metal themes + a few
#                more); may itself hold a colored/pantheon/... nested
#                bronze-mirroring folder (pantheon/colored)
#   pantheon  — the four mythologies with a documented Pantheon roster
#                (greek/norse/egypt/slavic); nests its own colored/
#   secondary — the second variant of a two-variant family (bible,
#                religion)
#   dark      — bible's third (night-window) variant
#   signs     — planets' zodiac-glyph variant
#   art       — planets' bronze-medallion variant
WEEKDAY_VARIANT_WHITELIST = frozenset(
    {"primary", "colored", "pantheon", "secondary", "dark", "signs", "art",
     # The universal rotation convention (owner decree 2026-07-20): an
     # `alt/` folder mirrors its parent's filenames and rotates daily by
     # the traveled date. The owner's first weekday drop is
     # bible/dark/alt/ (both sources, 2026-07-20 night) — the weekday
     # consumers still need the rotating_art_file wiring (queued), but
     # the FOLDER is legal everywhere the convention reaches.
     "alt"}
)


def _all_dir_names(root: Path) -> list[str]:
    return [p.name for p in root.rglob("*") if p.is_dir()]


def test_no_dual_folder_survives_anywhere_in_assets():
    """The LAW, root form: a folder literally named `dual` (any case)
    must not exist anywhere under assets/ — not nested under `primary/`,
    not under `colored/`, not under `pantheon/`, not bare. 60 files (plus
    8 more found on a fresh disk walk, some misfiled two levels deep
    under `primary/dual/colored/`) moved up one level this round; this
    test is the tripwire so the pattern can never quietly regrow."""
    assets_root = paths.assets_dir()
    offenders = [
        str(p.relative_to(assets_root))
        for p in assets_root.rglob("*")
        if p.is_dir() and p.name.lower() == "dual"
    ]
    assert offenders == []


def test_weekday_theme_subfolders_are_all_whitelisted():
    """Every folder under assets/weekday/<source>/<theme>/ (any depth)
    must be one of the documented variant names — no stray `dual/`, no
    ad hoc `ninth/`, `alt/` or similar creeping back in unannounced. A
    NEW legitimate variant is welcome, but it must be added to
    WEEKDAY_VARIANT_WHITELIST deliberately, in the same commit as the
    asset drop, not discovered by accident."""
    weekday_root = paths.assets_dir() / "weekday"
    sources = [p for p in weekday_root.iterdir() if p.is_dir()]
    assert sources, "expected at least one art source under assets/weekday/"
    offenders = []
    for source_dir in sources:
        for theme_dir in source_dir.iterdir():
            if not theme_dir.is_dir():
                continue
            for name in _all_dir_names(theme_dir):
                if name not in WEEKDAY_VARIANT_WHITELIST:
                    offenders.append(
                        f"{source_dir.name}/{theme_dir.name}/.../{name}"
                    )
    assert offenders == []


def test_weekday_variant_whitelist_has_no_unused_members():
    """The flip side of the whitelist test: every documented variant name
    must actually appear at least once on disk — an entry nobody uses is
    either stale documentation or a typo hiding a real mismatch."""
    weekday_root = paths.assets_dir() / "weekday"
    seen: set[str] = set()
    for source_dir in weekday_root.iterdir():
        if not source_dir.is_dir():
            continue
        for theme_dir in source_dir.iterdir():
            if theme_dir.is_dir():
                seen.update(_all_dir_names(theme_dir))
    assert WEEKDAY_VARIANT_WHITELIST <= seen


def test_alt_folders_mirror_their_parent_names():
    """THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20):
    `alt/` is a legal subfolder ANYWHERE under assets/ — it opts a
    family into daily rotation (`config.defaults.rotating_art_file`)
    beside the `<Name>_v2.png`-style suffix siblings — so this test does
    NOT whitelist where an `alt/` folder may appear. It only pins the
    one real invariant: `alt/` mirrors its parent's names, one level
    up, file for file. An `alt/<Name>.png` with no `<Name>.png` sibling
    in the parent is an ORPHAN — nothing computes a rotation pool for a
    stem the canonical directory doesn't also carry."""
    assets_root = paths.assets_dir()
    offenders = []
    for alt_dir in assets_root.rglob("alt"):
        if not alt_dir.is_dir():
            continue
        parent = alt_dir.parent
        for entry in alt_dir.iterdir():
            if entry.is_file() and not (parent / entry.name).exists():
                offenders.append(str(entry.relative_to(assets_root)))
    assert offenders == []


def test_every_sourced_root_is_registered():
    """The silent-absence tripwire (GUIDE shoot find, 2026-07-20): a
    top-level assets/<root> whose art ships in gemini/ or chatgpt/
    subtrees MUST be listed in constants.ART_SOURCED_ROOTS, or
    `paths.art_file` passes the sourceless canonical path straight
    through and every consumer quietly draws nothing. "era" (fixed in
    the Rule #19 round) and "eclipse" (found by the GUIDE screenshot
    session — chapter plates and hover badges absent) both died of
    exactly this; this walk ends the class."""
    from config import constants

    assets_root = paths.assets_dir()
    sourced_on_disk = sorted(
        child.name
        for child in assets_root.iterdir()
        if child.is_dir()
        # _-prefixed roots are meta, not art (assets/_state holds the
        # PromptPainter per-source run reports)
        and not child.name.startswith("_")
        and any((child / source).is_dir() for source in constants.ART_SOURCES)
    )
    missing = [
        name for name in sourced_on_disk
        if name not in constants.ART_SOURCED_ROOTS
    ]
    assert not missing, (
        f"assets roots with per-source subtrees not in ART_SOURCED_ROOTS: "
        f"{missing} — their art resolves to nonexistent sourceless paths"
    )
