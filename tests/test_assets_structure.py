"""The assets/ tree's structural law — the TAXONOMY MIRROR (RESTRUCTURE
2026-07-22). One hierarchy: the `assets/` folder tree mirrors
`config.taxonomy`. These tests walk the real disk so the source-folder
chaos (gemini/chatgpt subtrees, seat-named `alt/` files, per-root
naming zoos) the RESTRUCTURE abolished can never quietly regrow.

The invariants:
  1. Top-level roots are exactly the five categories (+ the meta `_state`
     ledger and the two build-pipeline logos).
  2. No source FOLDER (`gemini`/`chatgpt`) survives anywhere — the source
     is a terminal filename SUFFIX now (`_gem`/`_gpt`).
  3. No `alt/` folder survives — figure versions are `_vN` siblings in
     the same source-free folder.
  4. `assets/weeks/<group>/<theme>` mirrors `taxonomy.WEEK_GROUPS`: every
     group folder is a known group, every theme folder belongs to it.
  5. Every PNG under a sourced category (weeks / calendars / archetypes /
     celestial's era, eclipse, seasons) carries a `_gem`/`_gpt` suffix;
     the instrument furniture and the Earth faces are owner hand-made and
     carry none.
  6. THE TREE LAW (owner-approved 2026-07-26): every figure-tree image
     lives at exactly `<theme>/<register>/<look>/<Figure>[_vN]_<src>.png`
     — never loose in a theme or register folder, colored always a CHILD
     of its register (identical for pantheon and primary). The guard
     names each offender so a stray drop fails the suite immediately,
     with the destination rule in the message — the owner never has to
     report the same naming chaos twice.
"""

from pathlib import Path

from config import paths, taxonomy

# Top-level entries allowed directly under assets/.
_ALLOWED_ROOTS = set(taxonomy.CATEGORIES) | {
    "_state",              # the PromptPainter per-source run ledger (meta)
    "logo.svg", "logo-setup.svg",   # build-pipeline contract (unchanged)
    "___assets.md",
}

# Categories whose art shipped from an AI source — every PNG under them
# must carry the source suffix. The instrument furniture and the Earth
# marker faces are owner hand-made (no suffix).
_SUFFIXED_AREAS = (
    "weeks", "calendars", "archetypes",
    "celestial/era", "celestial/eclipse", "celestial/seasons",
)


def _iter_png(root: Path):
    return (p for p in root.rglob("*.png") if p.is_file())


# THE TREE LAW's vocabulary (owner-approved 2026-07-26). A LOOK folder
# is the only legal direct parent of a figure image; its own parent
# must be a REGISTER. New look/register names are added HERE, in one
# sealed vocabulary — never invented ad hoc in a drop.
_FIGURE_LAW_AREAS = ("weeks", "calendars", "archetypes")
_LAW_LOOKS = {
    "bronze", "colored", "logo", "photo", "sign", "art", "constellation",
}
_LAW_REGISTERS = {
    "primary", "pantheon", "secondary", "dark", "glass", "circle",
    "badges", "animals", "tree", "wider",
    # THE THREE FIGURE SETS (owner 2026-07-27, CUBE.md §The Rose +
    # Article Charter rule 5): a seat's three sets are three DIFFERENT
    # PEOPLE holding one office — archetypal (biblical, mythological,
    # classical-literary), historical (real persons), modern (fantasy,
    # film, comics) — so each set is a parallel READING of the same
    # seat, which is exactly what a register is. Precedent: the Ages
    # wheel already carries its two readings as the "tree" and
    # "animals" registers (archetypes.ARCHETYPE_LIFE_REGISTERS).
    "archetypal", "historical", "modern",
}


def test_figure_trees_obey_the_tree_law():
    """Invariant 6 — the law itself, not a hand-pinned folder list:
    `assets/<category>/<group>/<theme>/<register>/<look>/<file>` for
    every image in the three figure categories. `Title` plates are the
    one reserved stem and obey the same seat (a look folder inside the
    register they introduce). Planets' looks (photo/sign/art) hold
    their own Title directly — a look folder is always a legal image
    home."""
    offenders = []
    for area in _FIGURE_LAW_AREAS:
        for file in _iter_png(paths.assets_dir() / area):
            look = file.parent.name
            register = file.parent.parent.name
            if look not in _LAW_LOOKS or register not in _LAW_REGISTERS:
                offenders.append(
                    file.relative_to(paths.assets_dir()).as_posix()
                )
    assert offenders == [], (
        "files off the TREE LAW — every image belongs at "
        "<theme>/<register>/<look>/<Figure>[_vN]_<src>.png "
        "(see research/migrate_tree_law.py): "
        + ", ".join(offenders[:20])
    )


def test_top_level_roots_are_the_five_categories():
    assets = paths.assets_dir()
    offenders = [
        p.name for p in assets.iterdir() if p.name not in _ALLOWED_ROOTS
    ]
    assert offenders == [], offenders


def test_no_source_folder_survives_anywhere():
    """The source moved onto the filename — no `gemini`/`chatgpt` folder
    may exist under assets/ (the `_state` ledger keeps its own per-source
    subdirs and is exempt)."""
    assets = paths.assets_dir()
    offenders = [
        str(p.relative_to(assets))
        for p in assets.rglob("*")
        if p.is_dir()
        and p.name in ("gemini", "chatgpt")
        and "_state" not in p.relative_to(assets).parts
    ]
    assert offenders == [], offenders


def test_no_alt_folder_survives_anywhere():
    """`alt/` is abolished — figure versions are `_vN` siblings now."""
    assets = paths.assets_dir()
    offenders = [
        str(p.relative_to(assets))
        for p in assets.rglob("*")
        if p.is_dir() and p.name.lower() == "alt"
    ]
    assert offenders == [], offenders


def test_weeks_tree_mirrors_the_taxonomy():
    """Every folder under assets/weeks/ is a known group, and every theme
    folder inside it belongs to that group (taxonomy.WEEK_GROUPS)."""
    weeks = paths.assets_dir() / "weeks"
    assert weeks.is_dir()
    group_offenders = []
    theme_offenders = []
    for group_dir in weeks.iterdir():
        if not group_dir.is_dir():
            continue
        if group_dir.name not in taxonomy.WEEK_GROUPS:
            group_offenders.append(group_dir.name)
            continue
        allowed_themes = set(taxonomy.WEEK_GROUPS[group_dir.name][1])
        for theme_dir in group_dir.iterdir():
            if theme_dir.is_dir() and theme_dir.name not in allowed_themes:
                theme_offenders.append(f"{group_dir.name}/{theme_dir.name}")
    assert group_offenders == [], group_offenders
    assert theme_offenders == [], theme_offenders


def test_theme_to_group_reverse_map_is_consistent():
    """The derived THEME_TO_GROUP is an exact reverse of WEEK_GROUPS (no
    theme claimed by two groups, none dropped)."""
    flat = [
        theme
        for _group, (_display, themes) in taxonomy.WEEK_GROUPS.items()
        for theme in themes
    ]
    assert len(flat) == len(set(flat)), "a theme is listed in two groups"
    assert set(flat) == set(taxonomy.THEME_TO_GROUP)


def test_sourced_areas_carry_the_source_suffix():
    """Every PNG under a sourced category is `<stem>_gem.png`/`_gpt.png`.
    Owner hand-made art (instrument furniture, Earth faces) is exempt by
    living OUTSIDE these areas."""
    assets = paths.assets_dir()
    offenders = []
    for area in _SUFFIXED_AREAS:
        root = assets / area
        if not root.exists():
            continue
        for png in _iter_png(root):
            if not png.stem.endswith(("_gem", "_gpt")):
                offenders.append(str(png.relative_to(assets)))
    assert offenders == [], offenders[:20]


def test_instrument_furniture_and_earth_are_suffixless_owner_art():
    """The complement of the rule above: the instrument FURNITURE
    (hands, ring, subdial, icons, guide) and the Earth marker faces are
    owner hand-made and carry NO source suffix. (The instrument LOGO and
    paint/light legend DID ship from a source and keep their suffix —
    they live at instrument/ top level, outside these furniture dirs.)
    ONE documented exception (DOLLAR/EYE round, owner decree
    2026-07-27): the ring letter library's Eye of Providence pieces
    (`Eye[_shine]_gem/_gpt.png`) ARE sourced — the owner shipped a
    ChatGPT and a Gemini eye, each with and without rays, and placed
    them with the letters; their canonical `Eye[_shine].png` stems
    resolve through `config.paths.art_file` like every sourced area."""
    assets = paths.assets_dir()
    suffixless_areas = (
        "instrument/hands", "instrument/ring", "instrument/subdial",
        "instrument/icons", "instrument/guide", "celestial/earth",
    )
    offenders = []
    for area in suffixless_areas:
        for png in _iter_png(assets / area):
            if png.stem.endswith(("_gem", "_gpt")) and not (
                png.parent.name == "letters" and png.stem.startswith("Eye")
            ):
                offenders.append(str(png.relative_to(assets)))
    assert offenders == [], offenders[:20]


def test_subdial_sets_are_shared_not_per_source():
    """Rsub round (owner decree 2026-07-21): the subdial plate is its OWN
    shared thing — sets 1-4 carry all three hand-drawn finishes, "solo"
    only silver (gold/bronze are algorithmic). Now under instrument/."""
    root = paths.assets_dir() / "instrument" / "subdial"
    for set_name in ("set1", "set2", "set3", "set4"):
        for finish in ("gold", "silver", "bronze"):
            assert (root / set_name / f"{finish}.png").is_file(), (
                set_name, finish,
            )
    solo_files = sorted(p.name for p in (root / "solo").iterdir())
    assert solo_files == ["silver.png"]
