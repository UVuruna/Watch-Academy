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

# Top-level names under `masters/` whose governance is claimed one level
# DEEPER — see `governed_subtrees` for why this exists and what it
# protects. Keep it as short as the danger requires.
DEEP_GOVERNED_ROOTS = ("instrument",)

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


def governed_subtrees(masters: Path) -> tuple[str, ...]:
    """The areas the masters folder OWNS.

    The whole safety of pruning rests on this line. `shared/assets/`
    holds a great deal the bakery never made and no master will ever
    account for — `_baked/`, `_state/`, the SVG logos, the letter
    plates — and a prune that reasoned "not in the manifest, therefore
    delete" would erase the plates of THE ONE PLATE LAW on its first
    run. So the bakery claims authority over exactly the names that
    exist under `masters/` and over nothing else.

    THE HALF-GOVERNED AREA (owner verdict 2026-08-14): `instrument` is
    the one top-level name where claiming the WHOLE area would be a
    disaster rather than a policy. The owner's verdict was that new
    subdial art must be baked like every other kind — but
    `shared/assets/instrument/` also holds `letters/` (the 57 gold
    masters THE ONE PLATE LAW draws every glyph from), plus `guide/`,
    `hands/`, `icons/` and `ring/`: ~147 files the bakery never made and
    no master will ever claim. Under whole-area governance every one of
    them becomes a stray, `--check` goes red forever, and a single
    `--prune-strays` deletes the letter library.

    So for the roots named here, authority is claimed ONE LEVEL DEEPER:
    `masters/instrument/subdial/` governs `instrument/subdial` and
    nothing else in the area. Adding a master folder is how an area
    comes under the bakery — never a side effect of its parent's name.
    """
    claimed: list[str] = []
    for entry in masters.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in DEEP_GOVERNED_ROOTS:
            claimed.extend(
                f"{entry.name}/{child.name}"
                for child in entry.iterdir()
                if child.is_dir()
            )
            continue
        claimed.append(entry.name)
    return tuple(sorted(claimed))


def _is_governed(relative: str, subtrees: tuple[str, ...]) -> bool:
    return any(
        relative == subtree or relative.startswith(subtree + "/")
        for subtree in subtrees
    )


def reconcile(
    masters: Path, assets: Path, records: dict
) -> tuple[list[str], list[str]]:
    """Find where the shipped tree and the masters have drifted apart.

    Two different kinds of drift, and they get two different answers
    because only one of them is provably ours:

    * **orphans** — a manifest entry whose master is GONE. The manifest
      is proof the bakery wrote that output from that master, so
      deleting it is undoing our own work, not destroying someone's
      file. This is the owner's "brisanje ako je uklonjeno iz masters".
    * **strays** — a file inside a governed subtree that no manifest
      entry claims. It might be art a master would have produced under a
      name that has since changed; it might equally be something placed
      by hand. We do not know, so we REPORT and let `--prune-strays`
      say it out loud.

    Returns (orphan relative-master-paths, stray asset paths).
    """
    subtrees = governed_subtrees(masters)
    orphans = [
        relative
        for relative in records
        if not (masters / relative).exists()
    ]
    claimed = {
        record["output"]
        for relative, record in records.items()
        if relative not in orphans
    }
    strays: list[str] = []
    for existing in sorted(assets.rglob("*")):
        if not existing.is_file():
            continue
        relative = _rel(existing, assets)
        if not _is_governed(relative, subtrees):
            continue
        if relative not in claimed:
            strays.append(relative)
    return orphans, strays


def _prune(
    assets: Path, records: dict, orphans: list[str], strays: list[str],
    prune_strays: bool,
) -> int:
    """Delete what reconciliation condemned. Returns files removed."""
    removed = 0
    for relative in orphans:
        output = assets / records[relative]["output"]
        if output.exists():
            output.unlink()
            removed += 1
        del records[relative]
        print(f"  removed {relative} (master gone)")
    if prune_strays:
        for relative in strays:
            (assets / relative).unlink()
            removed += 1
            print(f"  removed stray {relative}")
    # An emptied theme folder left behind reads as a theme that ships
    # nothing, and `test_theme_completeness.py` judges folders, not
    # files — so a deletion that leaves the directory would fail the
    # suite for a theme that no longer exists at all.
    for directory in sorted(assets.rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
            print(f"  removed empty {_rel(directory, assets)}/")
    return removed


def bake(
    force: bool = False,
    dry_run: bool = False,
    prune_strays: bool = False,
    check: bool = False,
) -> int:
    """Bake every changed master. Returns how many files were written.

    With `check=True` nothing is written: the function reports the drift
    and returns the number of files that WOULD change, which is what a
    build gate reads as its exit code.
    """
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
    orphans, strays = reconcile(masters, assets, previous)
    print(
        f"masters: {masters}\n"
        f"assets:  {assets}\n"
        f"{len(jobs)} to bake, {skipped} unchanged, "
        f"{len(orphans)} to remove, {len(strays)} unclaimed, "
        f"quality q{bakery.ART_BAKE_QUALITY}"
    )
    for relative in strays[:20]:
        print(f"  unclaimed: {relative}")
    if len(strays) > 20:
        print(f"  ... and {len(strays) - 20} more unclaimed")

    if check:
        # The build gate. It writes NOTHING — a check that repairs is a
        # check nobody can trust to have told the truth about the state
        # it found.
        pending = len(jobs) + len(orphans) + (len(strays) if prune_strays else 0)
        print(
            "shared/assets is in sync with masters/"
            if not pending else
            f"OUT OF SYNC: {pending} file(s) — run "
            "`python -m setup.make_art_bake` before building"
        )
        return pending

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
    # Prune BEFORE baking, on `previous`, so the records the bake then
    # writes into are already free of the entries whose masters are
    # gone. Doing it after would mean a run that crashes mid-bake leaves
    # a manifest still promising files that were deleted.
    removed = _prune(assets, previous, orphans, strays, prune_strays)
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
    if removed:
        print(f"{removed} file(s) removed — shared/assets follows masters/")
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
    parser.add_argument(
        "--check", action="store_true",
        help="THE BUILD GATE: report drift, write nothing, exit non-zero "
             "with the number of files out of sync",
    )
    parser.add_argument(
        "--prune-strays", action="store_true",
        help="also delete governed files no master accounts for "
             "(reported, never deleted, without this flag)",
    )
    arguments = parser.parse_args()
    pending = bake(
        force=arguments.force,
        dry_run=arguments.list,
        prune_strays=arguments.prune_strays,
        check=arguments.check,
    )
    # Only --check turns the count into an exit code; an ordinary bake
    # returns how many files it WROTE, and a successful bake of 12 files
    # must not look like a failure to a shell.
    return min(pending, 1) if arguments.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
