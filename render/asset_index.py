"""THE ASSET INDEX — one stat walk per launch, and nothing ever reopens
a file it already knows. See [Asset Index](__about/asset_index.md).

Owner report 2026-08-12: `[91.6s] working set complete — 961 oversized
sources, 0 built cold`. Ninety-one seconds that built NOTHING. Three
separate startup passes were re-deriving, by OPENING files, facts that
had not changed since the previous launch:

* `asset_variants.warm_working_set` — `QImageReader` on 2,511 PNGs
  across five subtrees (3.76 GB) to read one integer, the width;
* `app.warm._collect_cache_garbage` — `raster_store.fingerprint` (64
  KiB head + 4 KiB tail) on every PNG/SVG/JPG in the tree;
* `app.encyclopedia_warm` — the same fingerprint again, per job.

Measured here 2026-08-12: that working-set scan costs 0.45 s with a
warm OS cache and 91.6 s cold (assets on an HDD, ~36 ms of seek per
file), while an `os.scandir` stat-walk of the WHOLE tree costs
**0.015 s** — on Windows a directory enumeration already carries each
entry's size and timestamps, so `DirEntry.stat()` is free.

So: keep the per-file facts on disk, keyed by `(size, mtime_ns)`, and
open only what genuinely changed. Steady state is zero opens.

This is a cache of FACTS ABOUT FILES, not of pixels — `raster_cache`
is that, and `raster_store` still owns both the fingerprint recipe and
the cache naming built on it (Rule #5). This module owns only the memo.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from PySide6.QtGui import QImageReader

from config import paths
from render import raster_store

#: Bumped whenever a record's SHAPE or the fingerprint recipe changes.
#: A stale index is DISCARDED, never migrated — one slow launch is
#: cheap, a subtly-wrong migration is not.
INDEX_VERSION = 1

#: Suffixes worth indexing: everything that can seed a cache entry —
#: this set IS the cache GC's source roster (it used to live in
#: `app.warm` as `_GC_SOURCE_SUFFIXES`, walked separately) — and
#: nothing else, since the tree also holds .md/.json that no derived
#: image is ever keyed by.
INDEXED_SUFFIXES = frozenset({".png", ".svg", ".jpg", ".jpeg"})

#: Re-read pool width. Both halves of a re-read release the GIL (the
#: fingerprint's two `read`s, Qt's header decode), so these are real
#: concurrent I/O. Capped: the pool only ever runs on a cold or
#: freshly-changed tree, and it shares the machine with the GUI thread.
_REREAD_WORKERS = 8

# Record layout, per path relative to assets_dir(), POSIX-separated:
#   [size, mtime_ns, fingerprint, width, height]
# width/height are -1 for a file whose header would not decode (an SVG,
# a truncated PNG) — a definite "asked and there is no answer", so the
# re-read is not repeated every launch.
_SIZE, _MTIME, _PRINT, _WIDTH, _HEIGHT = range(5)

_entries: dict[str, list] = {}
_lock = threading.RLock()
_loaded = False
_dirty = False


# ═══════════════════════════ LOCATION & I/O ═══════════════════════════


def index_path() -> Path:
    """Beside `raster_cache`, in the user directory — a derived,
    disposable artifact of THIS install, never something shipped."""
    return paths.settings_path().parent / "asset_index.json"


#: The assets root, resolved ONCE. `_relative` runs on the hot path —
#: `raster_store.fingerprint` calls it per resolved art path, thousands
#: of times per warm — and `Path.resolve()` is a filesystem call, not
#: string arithmetic: doing it per lookup cost 1.1 s across one
#: working-set scan alone (measured 2026-08-12), which would have been
#: a new slow pass replacing the one this module just deleted.
_ROOT: tuple[Path, Path] | None = None


def _root() -> tuple[Path, Path]:
    """`(assets_dir(), its resolved twin)`, memoized per user-dir. Tests
    repoint `paths.assets_dir`, so the raw value is re-checked; only the
    expensive `resolve()` is cached against it."""
    global _ROOT
    raw = paths.assets_dir()
    if _ROOT is None or _ROOT[0] != raw:
        _ROOT = (raw, raw.resolve())
    return _ROOT


def _relative(path: Path) -> str | None:
    """The index key, or None for anything outside `assets/`. Callers
    treat None as "not my business" and keep their own slow path — this
    is what leaves user-directory files and test fixtures untouched.

    Tries pure string arithmetic FIRST (`relative_to` on the path as
    given, which every in-app art path already satisfies — they are all
    built as `assets_dir() / rel`) and only pays `resolve()` when that
    fails, i.e. for a symlink or a `..`-carrying path."""
    root, resolved_root = _root()
    path = Path(path)
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        pass
    try:
        return path.resolve().relative_to(resolved_root).as_posix()
    except (ValueError, OSError):
        return None


def load() -> None:
    """Lazy first read. A corrupt or version-stale file is DISCARDED in
    silence-with-a-word (Rule #1): the next `refresh` rebuilds it, and
    a rebuilt index can never serve a wrong answer the way a repaired
    one might."""
    global _loaded
    with _lock:
        if _loaded:
            return
        _loaded = True
        path = index_path()
        if not path.exists():
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"asset index unreadable, rebuilding: {error}")
            return
        if not isinstance(raw, dict) or raw.get("version") != INDEX_VERSION:
            return
        stored = raw.get("entries")
        if isinstance(stored, dict):
            _entries.update(
                {
                    key: value for key, value in stored.items()
                    if isinstance(value, list) and len(value) == 5
                }
            )


def save() -> None:
    """Publish the index atomically, and only when something changed.
    A failed write is a lost optimisation, never a failed launch."""
    global _dirty
    with _lock:
        if not _dirty:
            return
        payload = {"version": INDEX_VERSION, "entries": dict(_entries)}
        _dirty = False
    path = index_path()
    partial = path.with_name(path.name + ".part")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(partial, path)
    except OSError as error:
        print(f"asset index not saved (harmless, only slower): {error}")
        partial.unlink(missing_ok=True)


def forget() -> None:
    """Drop the in-memory index — tests, and a user directory that
    changed under us (the THE RENAMING migration)."""
    global _loaded, _dirty
    with _lock:
        _entries.clear()
        _loaded = False
        _dirty = False


# ═══════════════════════════ THE READERS ═══════════════════════════


def _record(path: Path) -> list | None:
    """The stored record if it is still TRUE — one stat, one dict hit.
    None when the path is outside `assets/`, unknown, or has changed
    since it was recorded."""
    key = _relative(path)
    if key is None:
        return None
    load()
    with _lock:
        record = _entries.get(key)
    if record is None:
        return None
    try:
        stat = Path(path).stat()
    except OSError:
        return None
    if record[_SIZE] != stat.st_size or record[_MTIME] != stat.st_mtime_ns:
        return None
    return record


def fingerprint(path: Path) -> str | None:
    """The index-served content key, or None to mean "ask someone
    else" — which is exactly what `raster_store.fingerprint` does with
    it through the attached hook."""
    record = _record(path)
    return None if record is None else record[_PRINT]


def image_size(path: Path) -> tuple[int, int] | None:
    """Width and height WITHOUT opening the file. None when unknown, or
    when the header was tried once and would not decode (recorded as
    -1, so the miss is not re-paid every launch)."""
    record = _record(path)
    if record is None or record[_WIDTH] < 0:
        return None
    return record[_WIDTH], record[_HEIGHT]


def widths_under(subtree: str) -> list[tuple[Path, int]]:
    """Every indexed image under `subtree` (a path relative to
    `assets/`) with its WIDTH, sorted — the roster with no directory
    walk and no per-entry re-stat.

    AS OF THE LAST `refresh`, deliberately. `_record`'s stat check is
    what makes a single lookup safe against a file that changed under
    us; a caller sweeping thousands of entries in one pass right after
    phase 0 does not need it per entry, and paying it anyway cost 0.83 s
    across one working-set sweep (measured 2026-08-12) — a new slow
    pass replacing the one this module exists to delete. Art does not
    change between phase 0 and phase 2 of the same warm; if it ever
    does, the next launch's refresh corrects the record and the only
    cost was one working copy built at a stale ceiling."""
    load()
    root = paths.assets_dir()
    prefix = subtree.replace(os.sep, "/").strip("/") + "/"
    with _lock:
        return sorted(
            (root / key, record[_WIDTH])
            for key, record in _entries.items()
            if key.startswith(prefix) and record[_WIDTH] > 0
        )


def fingerprints_by_path() -> dict[str, str]:
    """Every indexed asset's absolute path -> content key. The cache
    GC's whole input, served without a single `open` (`app.warm.
    _collect_cache_garbage` used to fingerprint the entire tree here)."""
    load()
    root = paths.assets_dir()
    with _lock:
        return {
            str(root / key): record[_PRINT]
            for key, record in _entries.items()
        }


# ═══════════════════════════ THE REFRESH WALK ═══════════════════════════


def _read_facts(absolute: str) -> tuple[str, int, int]:
    """The expensive half, run once per genuinely new or changed file:
    the sampled content fingerprint and the image header. Both release
    the GIL, which is what makes the pool below honest."""
    digest = raster_store.compute_fingerprint(Path(absolute))
    size = QImageReader(absolute).size()
    if size.isValid():
        return digest, size.width(), size.height()
    return digest, -1, -1


def _walk() -> dict[str, os.stat_result]:
    """One `os.scandir` sweep of `assets/`. `DirEntry.stat()` costs no
    extra I/O on Windows — the enumeration already carries it — so the
    whole 3.76 GB tree's shape lands in ~0.015 s."""
    root = paths.assets_dir()
    found: dict[str, os.stat_result] = {}
    stack = [root]
    while stack:
        try:
            with os.scandir(stack.pop()) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                    elif Path(entry.name).suffix.lower() in INDEXED_SUFFIXES:
                        key = Path(entry.path).relative_to(root).as_posix()
                        found[key] = entry.stat()
        except OSError as error:
            # A folder that vanished mid-walk or refuses to open is one
            # unindexed subtree — slower, never wrong.
            print(f"asset index walk skipped a folder: {error}")
    return found


def refresh(should_stop=None, progress=None) -> tuple[int, int]:
    """Bring the index up to date and return `(known, rescanned)`.

    Walks the tree with `scandir`, KEEPS every record whose
    `(size, mtime_ns)` still matches — those files are never opened —
    and re-reads only the rest, in a thread pool. Prunes records whose
    file is gone.

    Belongs to the warm thread (`app.warm.run_warm` phase 0). The GUI
    thread may READ the index freely; building it is not its job."""
    global _dirty
    from concurrent.futures import ThreadPoolExecutor
    from time import perf_counter

    start = perf_counter()
    load()
    found = _walk()
    if should_stop is not None and should_stop():
        return len(_entries), 0

    root = paths.assets_dir()
    stale: list[tuple[str, str, os.stat_result]] = []
    with _lock:
        for key, stat in found.items():
            record = _entries.get(key)
            if (
                record is not None
                and record[_SIZE] == stat.st_size
                and record[_MTIME] == stat.st_mtime_ns
            ):
                continue        # THE POINT: a known, unchanged file is never opened
            stale.append((key, str(root / key), stat))
        for gone in [key for key in _entries if key not in found]:
            del _entries[gone]
            _dirty = True

    if not stale:
        if progress is not None:
            progress(
                f"[{perf_counter() - start:.1f}s] asset index current — "
                f"{len(found)} files, 0 reopened"
            )
        save()
        return len(found), 0

    done = 0
    with ThreadPoolExecutor(max_workers=_REREAD_WORKERS) as pool:
        futures = {
            pool.submit(_read_facts, absolute): (key, stat)
            for key, absolute, stat in stale
        }
        for future in futures:
            if should_stop is not None and should_stop():
                break
            key, stat = futures[future]
            try:
                digest, width, height = future.result()
            except OSError as error:
                # One unreadable source is one unindexed file: its
                # readers fall back to opening it themselves.
                print(f"asset index could not read {key}: {error}")
                continue
            with _lock:
                _entries[key] = [
                    stat.st_size, stat.st_mtime_ns, digest, width, height
                ]
                _dirty = True
            done += 1
            if progress is not None and done % 200 == 0:
                progress(
                    f"[{perf_counter() - start:.1f}s] asset index "
                    f"{done}/{len(stale)} new or changed"
                )
    save()
    if progress is not None:
        progress(
            f"[{perf_counter() - start:.1f}s] asset index complete — "
            f"{len(found)} files, {done} reopened"
        )
    return len(found), done


# The hook that serves every existing `source_prefix` caller — the
# Encyclopedia's hundreds of path resolutions included — without any of
# them importing this module, and without `raster_store` losing the
# dependency-light contract its subprocess workers rely on.
raster_store.attach_fingerprint_source(fingerprint)
