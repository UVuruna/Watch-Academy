"""THE ART BAKERY — turn the owner's full-resolution research masters
into the small, application-sized art both platforms read. See
[Make Art Bake](__about/make_art_bake.md).

Owner order 2026-08-12: one gitignored folder is the inbox every
research prompt writes into; from there WE produce the compressed,
downscaled versions, into the folders the desktop and Android
applications read. Masters in, shipped art out, one way, never back.

Run:

    python -m setup.make_art_bake            # bake what changed
    python -m setup.make_art_bake --force    # rebuild everything
    python -m setup.make_art_bake --list     # report the plan, no work

The ceilings come from `defaults.WORKING_SET_CEILINGS` — the very table
the RUNTIME working set uses — so this script cannot drift from what
the program considers big enough. It has no ceilings of its own.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter

from PIL import Image

from config import bakery, defaults, paths


MANIFEST_NAME = "_bake_manifest.json"

# Subtrees the bakery must never touch even though they live under
# `masters/`. `instrument/letters` is THE ONE PLATE LAW's gold-master
# library: the transformer runs an oklab pass with a guided box filter
# and a specular ramp over those exact pixels, so a lossy re-encode
# would not soften one image — it would bake artifacts into all 34
# finishes of every glyph, everywhere the program draws text. They are
# palette PNGs of a few tens of KB; there is nothing to win.
VERBATIM_SUBTREES = ("instrument/letters",)

# Subtrees that are RE-ENCODED but never RESIZED (ceiling 0 below).
#
# `celestial/earth` is here on the owner's decree of 2026-07-15, the
# Globe originals round: "every earth face is his full-resolution
# original", pinned at >= 1500 px by
# `tests/test_skins.py::test_earth_pole_regions_full_res_and_latitude_override`.
# The area DOES carry a runtime `WORKING_SET_CEILINGS` entry (512 since
# his ceiling decree of 2026-08-13, 800 before it), and
# that is not a contradiction: the working set makes a small copy to
# DRAW from and leaves the original alone. The bakery replaces the file
# itself, so obeying that ceiling here destroyed the original — which is
# exactly what the first bake of this round did, and exactly what that
# test caught. Compression still applies; only the resize is skipped.
FULL_RESOLUTION_SUBTREES = ("celestial/earth",)

# What the bakery considers art. Anything else under `masters/` (SVG
# logos, a stray .txt, a JSON sidecar) is copied through untouched —
# the shipped tree must be complete WITHOUT the masters existing.
ART_SUFFIXES = (".png", ".jpg", ".jpeg")


def _rel(path: Path, root: Path) -> str:
    """A master's identity in the manifest: its path under `masters/`,
    forward-slashed so a manifest written on Windows still reads on the
    machine that builds the phone pack."""
    return path.relative_to(root).as_posix()


def _ceiling_for(relative: str) -> int | None:
    """The pixel ceiling of the area a master belongs to.

    Three answers, and they are three different instructions:

    * **an int > 0** — re-encode, capped at this many pixels on the long
      edge;
    * **0** — re-encode at FULL resolution (`FULL_RESOLUTION_SUBTREES`);
    * **None** — copy through untouched (verbatim, or not an image).

    The LONGEST matching prefix wins, so a future `weeks/something` with
    its own entry could override the `weeks` default without this
    function learning anything."""
    if any(
        relative == subtree or relative.startswith(subtree + "/")
        for subtree in FULL_RESOLUTION_SUBTREES
    ):
        return 0
    best: tuple[int, int] | None = None
    for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items():
        if relative == subtree or relative.startswith(subtree + "/"):
            if best is None or len(subtree) > best[0]:
                best = (len(subtree), ceiling)
    return None if best is None else best[1]


def _is_verbatim(relative: str) -> bool:
    return any(
        relative == subtree or relative.startswith(subtree + "/")
        for subtree in VERBATIM_SUBTREES
    )


def _digest(path: Path) -> str:
    """sha256 of a master. This is the incremental key AND the only
    provenance the repo can keep, because the masters themselves are
    gitignored — see the script's docs."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def bake_one(
    source: str, destination: str, ceiling: int | None, quality: int
) -> tuple[int, int, int]:
    """Bake ONE master. Returns (width, height, bytes) of what landed.

    A module-level function taking only picklable arguments on purpose:
    it is the process-pool worker below. Pillow's decode/resize/encode
    holds the GIL for a good fraction of a second on a multi-megabyte
    plate, which is the same reason `defaults.WORKING_SET_WORKERS`
    exists for the runtime builder — threads would serialize.
    """
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    # ATOMIC, like `raster_store.atomic_save` (and for the reason a test
    # run against a bake still in flight found first-hand): a WebP
    # encode of a multi-megabyte plate takes a visible fraction of a
    # second, and anything reading the tree meanwhile — a guard, the
    # running watch, git — must never see a half-written image. Encode
    # to a sibling, publish with one rename.
    partial = target.with_name(target.name + ".part")
    if ceiling is None:
        # NO DECODE on this branch. It used to open the copy to report
        # its dimensions, which meant every non-image travelling with the
        # art — `.gitkeep`, a stray cache file — raised
        # UnidentifiedImageError and was announced as SKIPPED even though
        # the copy had in fact succeeded. Reporting work as failed when
        # it succeeded is the same class of lie as the reverse. Files
        # with no dimensions report (0, 0), which the manifest records
        # honestly as "not an image".
        shutil.copy2(source, partial)
        os.replace(partial, target)
        if Path(source).suffix.lower() in ART_SUFFIXES:
            with Image.open(target) as image:
                return (*image.size, target.stat().st_size)
        return (0, 0, target.stat().st_size)

    with Image.open(source) as image:
        image = image.convert("RGBA")
        width, height = image.size
        # `ceiling == 0` means re-encode at full resolution — never
        # resize. Testing the ceiling first also keeps a 0 from being
        # read as a limit and scaling the image to nothing.
        if ceiling and max(width, height) > ceiling:
            scale = ceiling / max(width, height)
            image = image.resize(
                (max(1, round(width * scale)), max(1, round(height * scale))),
                Image.LANCZOS,
            )
        # method=6 is Pillow's slowest/best WebP search. This runs once,
        # by us, on our machine — the user pays nothing for the extra
        # seconds and gets the smaller file forever.
        image.save(partial, "WEBP", quality=quality, method=6)
        os.replace(partial, target)
        return (*image.size, target.stat().st_size)


def _plan(
    masters: Path, assets: Path, previous: dict, force: bool
) -> tuple[list[tuple[Path, Path, int | None, str]], int]:
    """Every master paired with where it lands, minus the ones whose
    source hash and output both already match the manifest.

    Returns (jobs, skipped)."""
    jobs: list[tuple[Path, Path, int | None, str]] = []
    skipped = 0
    for source in sorted(masters.rglob("*")):
        if not source.is_file():
            continue
        relative = _rel(source, masters)
        if source.name == MANIFEST_NAME:
            continue
        verbatim = _is_verbatim(relative) or (
            source.suffix.lower() not in ART_SUFFIXES
        )
        ceiling = None if verbatim else _ceiling_for(relative)
        # A ceiling means a WebP output; everything else keeps its own
        # name and extension so the shipped tree mirrors the masters.
        if ceiling is None:
            destination = assets / relative
        else:
            destination = (assets / relative).with_suffix(".webp")
        digest = _digest(source)
        record = previous.get(relative)
        if (
            not force
            and record is not None
            and record.get("sha256") == digest
            # The CEILING is part of the skip test, not only the source
            # hash (owner's 800 -> 512 decree, 2026-08-13, found this).
            # Lower a ceiling and every master is still byte-identical,
            # so a hash-only check would skip the whole tree and report
            # "0 to bake" — the change would appear to have been applied
            # and would in fact have done nothing. A silent no-op is the
            # worst answer a setup script can give.
            and record.get("ceiling") == ceiling
            and record.get("quality") == bakery.ART_BAKE_QUALITY
            and destination.exists()
            and destination.stat().st_size == record.get("bytes")
        ):
            skipped += 1
            continue
        jobs.append((source, destination, ceiling, digest))
    return jobs, skipped


def bake(force: bool = False, dry_run: bool = False) -> int:
    """Bake every changed master. Returns how many files were written."""
    masters = paths.masters_dir()
    if masters is None:
        print(
            "no masters/ folder — nothing to bake.\n"
            "This is NOT an error: the masters are gitignored and a "
            "clone without them is a complete, working program. Only "
            "the machine that holds the owner's research art bakes.",
            file=sys.stderr,
        )
        return 0

    assets = paths.assets_dir()
    manifest_path = assets / MANIFEST_NAME
    previous: dict = {}
    if manifest_path.exists() and not force:
        previous = json.loads(manifest_path.read_text("utf-8")).get("files", {})

    jobs, skipped = _plan(masters, assets, previous, force)
    print(
        f"masters: {masters}\n"
        f"assets:  {assets}\n"
        f"{len(jobs)} to bake, {skipped} unchanged, "
        f"quality q{bakery.ART_BAKE_QUALITY}"
    )
    if dry_run:
        for source, destination, ceiling, _ in jobs[:40]:
            kind = "verbatim" if ceiling is None else f"<= {ceiling}px webp"
            print(f"  {_rel(source, masters):70s} {kind}")
        if len(jobs) > 40:
            print(f"  ... and {len(jobs) - 40} more")
        return 0

    start = perf_counter()
    written = 0
    saved_from = 0
    saved_to = 0
    workers = max(1, min(defaults.WORKING_SET_WORKERS, os.cpu_count() or 1))
    records = dict(previous)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                bake_one,
                str(source),
                str(destination),
                ceiling,
                bakery.ART_BAKE_QUALITY,
            ): (source, destination, digest, ceiling)
            for source, destination, ceiling, digest in jobs
        }
        for index, future in enumerate(futures, start=1):
            source, destination, digest, ceiling = futures[future]
            relative = _rel(source, masters)
            try:
                width, height, size = future.result()
            except Exception as error:
                # One unbakeable master is skipped, LOUDLY, never fatal —
                # the same call `make_letter_bake` makes: a partial bake
                # is a partially small program, an aborted one is nothing.
                print(f"  SKIPPED {relative}: {error}", file=sys.stderr)
                continue
            records[relative] = {
                "sha256": digest,
                "output": _rel(destination, assets),
                # Recorded so the next run can tell a re-bake is needed
                # when the CEILING or the QUALITY changed while the
                # master did not — see the skip test in `_plan`.
                "ceiling": ceiling,
                "quality": bakery.ART_BAKE_QUALITY,
                "width": width,
                "height": height,
                "bytes": size,
            }
            saved_from += source.stat().st_size
            saved_to += size
            written += 1
            if index % 100 == 0 or index == len(futures):
                print(
                    f"  [{perf_counter() - start:6.1f}s] "
                    f"{index}/{len(futures)}"
                )

    manifest_path.write_text(
        json.dumps(
            {
                "quality": bakery.ART_BAKE_QUALITY,
                "ceilings": defaults.WORKING_SET_CEILINGS,
                "files": dict(sorted(records.items())),
            },
            indent=2,
        ),
        "utf-8",
    )
    if saved_from:
        print(
            f"{written} baked in {perf_counter() - start:.1f}s — "
            f"{saved_from / 1e6:.0f} MB of masters -> "
            f"{saved_to / 1e6:.0f} MB shipped "
            f"({saved_to / saved_from * 100:.1f}%)"
        )
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="rebuild every master"
    )
    parser.add_argument(
        "--list", action="store_true", help="report the plan, do no work"
    )
    arguments = parser.parse_args()
    bake(force=arguments.force, dry_run=arguments.list)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
