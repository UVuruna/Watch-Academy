"""One-shot executor of the owner-approved TREE LAW (2026-07-26):

    assets/<category>/<group>/<theme>/<register>/<look>/<Figure>[_vN]_<src>.png

Dry-run by default (prints the full move plan + collision check + counts,
touches NOTHING); `--execute` performs the plan with `git mv` (history
preserved) and re-verifies counts. See [Migrate Tree Law](migrate_tree_law.md).

The PLAN below is the single auditable record of how the existing zoo
maps onto the law — every oddball is a named row, never an if-branch
surprise.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Look folder names that may legally sit inside a register — anything
# else holding files directly in a register (or theme) descends.
LOOK_DIRS = {
    "bronze", "colored", "logo", "photo", "sign", "art", "constellation",
}

# SPECIAL themes whose children are re-mapped case by case (the law's
# oddballs). rel-source-dir -> rel-dest-dir, applied in ORDER (the
# astrology "primary -> primary/logo" move must run before anything
# else lands inside the new primary/).
SPECIAL_DIR_MOVES = [
    # THE ZODIAC (astrology): its four folders are LOOKS of the one
    # primary register — "primary" (the logo badges) is renamed to the
    # honest look name "logo".
    ("calendars/zodiac/astrology/primary", "calendars/zodiac/astrology/primary/logo"),
    ("calendars/zodiac/astrology/colored", "calendars/zodiac/astrology/primary/colored"),
    ("calendars/zodiac/astrology/constellation", "calendars/zodiac/astrology/primary/constellation"),
    ("calendars/zodiac/astrology/sign", "calendars/zodiac/astrology/primary/sign"),
    # THE PLANETS: photos/signs/art are LOOKS of the one primary
    # register — "primary" (the photos) renamed to "photo", "signs"
    # singular to match the law's look naming.
    ("weeks/celestial_bodies/planets/primary", "weeks/celestial_bodies/planets/primary/photo"),
    ("weeks/celestial_bodies/planets/signs", "weeks/celestial_bodies/planets/primary/sign"),
    ("weeks/celestial_bodies/planets/art", "weeks/celestial_bodies/planets/primary/art"),
    # THE LIFE FAMILY: circle badges exist only for the tree register
    # and sit ILLEGALLY deep (life/circle/tree) — they merge straight
    # into the family's one circle register at its final look level.
    ("archetypes/life/circle/tree", "archetypes/life/circle/colored"),
]

# Folder names that ARE registers — anything else holding files
# directly is a bare THEME and gains a primary/ register around them.
REGISTER_NAMES = {
    "primary", "pantheon", "secondary", "dark", "glass", "circle",
    "badges", "animals", "tree",
}

# Themes (rel to assets/) whose direct child "colored" descends into
# "primary/colored" (the owner's own complaint: COLORED inside pantheon
# must equal COLORED inside primary) — discovered dynamically: every
# theme dir having BOTH colored/ and primary/ children.

# assets/titles/<sheet>_<src>.png -> the theme register that Title
# introduces (law rule 6; look = colored — the AI title cards are
# full-color). Sheet keys with NO tree home yet stay PENDING and the
# files stay in assets/titles until the owner's sheets land their
# themes.
TITLES_MAP = {
    "alchemy": "weeks/crafts/alchemy/primary",
    "bee": "weeks/societies/bee/primary",
    "bible": "weeks/faith/bible/primary",
    "bible2": "weeks/faith/bible/secondary",
    "bible_dark": "weeks/faith/bible/dark",
    "chinese_myth": "weeks/myth/celestial_court/primary",
    "corporate": "weeks/crafts/corporate/primary",
    "cosmos": "weeks/celestial_bodies/cosmos/primary",
    "cyberpunk_gangs": "weeks/gaming/cp_gangs/primary",
    "cyberpunk_power": "weeks/gaming/cp_corpo/primary",
    "cyberpunk_street": "weeks/gaming/cp_street/primary",
    "egypt": "weeks/myth/egypt/primary",
    "elephant": "weeks/societies/elephant/primary",
    "greek": "weeks/myth/greek/primary",
    "intelligences": "weeks/inner_wheel/intelligence/primary",
    "japan": "weeks/crafts/japan/primary",
    "monsters": "weeks/myth/age_of_heroes/primary",
    "months": "calendars/slavic_months/primary",
    "moods": "weeks/inner_wheel/mood/primary",
    "norse": "weeks/myth/norse/primary",
    "planet_signs": "weeks/celestial_bodies/planets/primary/sign",
    "planets": "weeks/celestial_bodies/planets/primary/photo",
    "planets_art": "weeks/celestial_bodies/planets/primary/art",
    "profession": "weeks/crafts/profession/primary",
    "religion": "weeks/faith/creeds/primary",
    "religion_alt": "weeks/faith/creeds/secondary",
    "sins": "weeks/inner_wheel/sin/primary",
    "slavic": "weeks/myth/slavic/primary",
    "starwars_nova": "weeks/films/sw_dyad/primary",
    "starwars_svetla": "weeks/films/sw_jedi/primary",
    "starwars_tamna": "weeks/films/sw_sith/primary",
    "virtues": "weeks/inner_wheel/virtue/primary",
    "wolf": "weeks/societies/wolf/primary",
    "wow_alliance": "weeks/gaming/wow_alliance/primary",
    "wow_evil": "weeks/gaming/wow_evil/primary",
    "wow_horde": "weeks/gaming/wow_horde/primary",
}
# (chinese_myth -> celestial_court and monsters -> age_of_heroes were
# resolved from their own sheets' drop paths — no PENDING keys remain.)
TITLES_PENDING: set[str] = set()

FIGURE_ROOTS = ("weeks", "calendars", "archetypes")


def plan() -> tuple[list[tuple[Path, Path]], list[str]]:
    """Every (source, dest) file move the law demands, plus PENDING
    notes. Pure computation — nothing is touched."""
    moves: list[tuple[Path, Path]] = []
    notes: list[str] = []
    special_sources = {ASSETS / s for s, _ in SPECIAL_DIR_MOVES}

    # 1) SPECIAL dir remaps, in declared order.
    for src_rel, dst_rel in SPECIAL_DIR_MOVES:
        src = ASSETS / src_rel
        if not src.is_dir():
            notes.append(f"SPECIAL source missing (already migrated?): {src_rel}")
            continue
        for f in sorted(src.iterdir()):
            if f.is_file():
                moves.append((f, ASSETS / dst_rel / f.name))

    # 2) Theme-level colored/ descends into primary/colored.
    for root in FIGURE_ROOTS:
        for colored in sorted((ASSETS / root).rglob("colored")):
            if not colored.is_dir() or colored in special_sources:
                continue
            parent = colored.parent
            if (parent / "primary").is_dir() and parent.name not in (
                "primary", "pantheon", "secondary", "dark",
            ):
                for f in sorted(colored.iterdir()):
                    if f.is_file():
                        moves.append((f, parent / "primary" / "colored" / f.name))

    # 3) Loose files in a register (or bare theme) descend into a look:
    #    bronze/ when a colored twin set exists for the register (the
    #    cameo+colored generation pairs — present on disk at d/colored,
    #    or arriving there via a pass-2 move), colored/ otherwise
    #    (as-drawn full-color sets).
    planned_colored_dirs = {m[1].parent for m in moves}
    for root in FIGURE_ROOTS:
        for d in sorted((ASSETS / root).rglob("*")):
            if not d.is_dir() or d.name in LOOK_DIRS or d in special_sources:
                continue
            if any(str(d).startswith(str(s)) for s in special_sources):
                continue
            files = [f for f in sorted(d.iterdir()) if f.is_file()]
            if not files:
                continue
            # Bare THEME holding files directly gains its primary/.
            base = d if d.name in REGISTER_NAMES else d / "primary"
            has_colored_twin = (
                (d / "colored").is_dir()
                or (base / "colored") in planned_colored_dirs
            )
            look = "bronze" if has_colored_twin else "colored"
            for f in files:
                moves.append((f, base / look / f.name))

    # 4) The titles drop distributes (law rule 6): Title_<src>.png.
    titles = ASSETS / "titles"
    if titles.is_dir():
        for f in sorted(titles.iterdir()):
            if not f.is_file():
                continue
            stem = f.name
            for src_tag in ("_gem.png", "_gpt.png"):
                if stem.endswith(src_tag):
                    key, tag = stem[: -len(src_tag)], src_tag
                    break
            else:
                notes.append(f"titles: unrecognized suffix, left in place: {f.name}")
                continue
            if key in TITLES_PENDING:
                notes.append(f"titles PENDING (no tree home yet): {f.name}")
                continue
            dest_reg = TITLES_MAP.get(key)
            if dest_reg is None:
                notes.append(f"titles UNMAPPED, left in place: {f.name}")
                continue
            moves.append((f, ASSETS / dest_reg / "colored" / f"Title{tag}"))
    return moves, notes


def main() -> int:
    execute = "--execute" in sys.argv
    moves, notes = plan()
    dests = {}
    collisions = []
    for src, dst in moves:
        if dst.exists() or str(dst) in dests:
            collisions.append((src, dst))
        dests[str(dst)] = src
    before = sum(1 for r in FIGURE_ROOTS for _ in (ASSETS / r).rglob("*") if _.is_file())
    print(f"planned moves: {len(moves)}   figure-tree files before: {before}")
    for note in notes:
        print(f"NOTE: {note}")
    for src, dst in collisions:
        print(f"COLLISION: {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    if collisions:
        print("ABORT: collisions must be resolved by hand first (law: zero loss).")
        return 1
    if not execute:
        for src, dst in moves:
            print(f"PLAN {src.relative_to(ASSETS)}  ->  {dst.relative_to(ASSETS)}")
        print("dry run — nothing touched; rerun with --execute")
        return 0
    for index, (src, dst) in enumerate(moves):
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "mv", str(src), str(dst)], cwd=ROOT, check=True,
            capture_output=True,
        )
        if (index + 1) % 100 == 0:
            print(f"moved {index + 1}/{len(moves)}")
    after = sum(1 for r in FIGURE_ROOTS for _ in (ASSETS / r).rglob("*") if _.is_file())
    moved_titles = sum(1 for s, _ in moves if "titles" in s.parts)
    print(f"figure-tree files after: {after} (before {before} + titles {moved_titles})")
    if after != before + moved_titles:
        print("COUNT MISMATCH — investigate before committing!")
        return 1
    print("execute complete — counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
