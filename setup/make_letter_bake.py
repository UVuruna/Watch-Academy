"""THE LETTER BAKER — pre-render every plate in every metal and every
thematic colour into `assets/_baked/letters/`, once, so no launch ever
derives one again. See
[Make Letter Bake](__about/make_letter_bake.md).

Owner order 2026-08-12: the letters are used constantly now, and all of
them are used; they belong rendered at SETUP into a folder the program
reads, never recomputed on every start. There is no installer on this
machine yet, so this script IS the setup step and its output is
committed with the assets.

Run:

    python -m setup.make_letter_bake            # bake what is missing
    python -m setup.make_letter_bake --force    # rebuild everything
    python -m setup.make_letter_bake --list     # what is there, no work

Every name comes from `render.asset_recolor.letter_cache_name`, the
same function the running program calls, so what this writes is by
construction what the program looks for.
"""

import argparse
import sys
from pathlib import Path
from time import perf_counter

from PySide6.QtGui import QGuiApplication

from config import constants, defaults, paths
from render import letter_bake


def _plates() -> list[Path]:
    """Every plate in the owner's library — latin, greek, numerals,
    symbols, emblems. Read off DISK rather than from a glyph table on
    purpose: the bake must cover what exists, including a plate added
    since the last time any table was updated."""
    root = paths.assets_dir() / "instrument" / "letters"
    return sorted(root.rglob("*.png"))


def _finishes() -> list[tuple[str, str]]:
    """Every (metal, shade) pair the transformer offers — the three
    real metals with all their shades, plus the THEMATIC pseudo-metal
    whose shades are the five ring theme colours and every remaining
    ramp (copper, brass, rose_gold, steel, pewter, iron...).

    Pairs are NOT collapsed onto their ramps even though several share
    one (gold/classic and thematic/gold are both the `gold` ramp): the
    runtime key carries the pair, not the ramp, and teaching this
    script the ramp table is exactly the kind of second source of truth
    the bake's naming design exists to avoid. The cost is a few MB of
    duplicate pixels."""
    return [
        (metal, shade)
        for metal, shades in defaults.METAL_SHADES.items()
        for shade in shades
    ]


def bake(force: bool = False) -> int:
    """Write every missing finish. Returns how many were built."""
    # Imported here: it pulls in `render.assets`, which needs the
    # QGuiApplication that main() creates below.
    from render.asset_recolor import bake_letter_finish, letter_cache_name

    destination = letter_bake.bake_dir()
    destination.mkdir(parents=True, exist_ok=True)
    plates = _plates()
    finishes = _finishes()
    total = len(plates) * len(finishes)
    print(
        f"{len(plates)} plates x {len(finishes)} finishes = {total} files"
    )

    start = perf_counter()
    built = 0
    skipped = 0
    for index, master in enumerate(plates, start=1):
        for metal, shade in finishes:
            name = letter_cache_name(master, metal, shade)
            target = destination / name
            if target.exists() and not force:
                skipped += 1
                continue
            try:
                bake_letter_finish(master, metal, shade, target)
            except (OSError, ValueError) as error:
                # One unbakeable plate is one finish derived live —
                # never a failed bake (Rule #1).
                print(f"  ! {master.stem} {metal}/{shade}: {error}")
                continue
            built += 1
        elapsed = perf_counter() - start
        print(
            f"[{elapsed:6.1f}s] {index:3}/{len(plates)} {master.stem:<12} "
            f"built {built}, skipped {skipped}"
        )
    letter_bake.refresh()
    size = sum(f.stat().st_size for f in destination.glob("*.png"))
    print(
        f"\nDONE in {perf_counter() - start:.1f}s — {built} built, "
        f"{skipped} already present, {letter_bake.baked_count()} files, "
        f"{size / 2**20:.0f} MB in {destination}"
    )
    return built


def show() -> None:
    """What shipped, readably — the index the opaque filenames owe the
    reader (the names are keyed for safety, not for browsing)."""
    letter_bake.refresh()
    print(f"{letter_bake.baked_count()} baked finishes in {letter_bake.bake_dir()}")
    print(f"{len(_plates())} plates, {len(_finishes())} finishes:")
    for metal, shades in defaults.METAL_SHADES.items():
        print(f"  {metal:<9} {', '.join(shades)}")
    unknown = set(defaults.METAL_SHADES) - set(constants.METAL_SHADE_NAMES)
    if unknown:
        print(f"  ! shades with no name table: {sorted(unknown)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true",
        help="rebuild every finish, not only the missing ones",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="report what is baked and exit",
    )
    args = parser.parse_args()
    # QImage/QPainter need a Qt application object; QGuiApplication is
    # enough (no widgets here) and works headless.
    QGuiApplication(sys.argv[:1])
    if args.list:
        show()
        return 0
    bake(force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
