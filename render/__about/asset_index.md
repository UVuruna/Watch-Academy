# Asset Index

**Script:** [Asset Index (script)](../asset_index.py) · **Flow:** [diagram](../__flow/asset_index.md)

## Purpose

**One stat walk per launch, and nothing ever reopens a file it already
knows.**

Born from the owner's 2026-08-12 report — `[91.6s] working set complete
— 961 oversized sources, **0 built cold**`. Ninety-one seconds that
built **nothing**. Every launch re-discovered, from scratch, facts that
had not changed since the last launch, and it did so by OPENING files:

| Startup pass | What it opened | Why |
|---|---|---|
| `asset_variants.warm_working_set` | `QImageReader` on every PNG in five subtrees — **2,511 files / 3.76 GB** | to read one integer: the width |
| `app.warm._collect_cache_garbage` | `raster_store.fingerprint` on every PNG/SVG/JPG in the tree | 64 KiB head + 4 KiB tail, per file |
| `app.encyclopedia_warm.warm_encyclopedia` | `source_prefix` per job, hundreds of paths | the same fingerprint, again |

The measurements that made this module (this machine, 2026-08-12):

| | |
|---|---|
| the working-set scan, **warm** OS cache | **0.45 s** |
| the same scan, **cold** OS cache (the owner's number) | **91.6 s** |
| `os.scandir` stat-walk of the whole tree — 2,710 PNG / 3.76 GB | **0.015 s** |

That last row is the whole design. On Windows, a directory enumeration
already carries each entry's size and timestamps —
`os.DirEntry.stat()` costs **no extra I/O at all**. So the tree's shape
can be re-read essentially for free; what is expensive is opening
files, and a file whose `(size, mtime_ns)` is unchanged has nothing new
to say.

This module therefore keeps a persistent record — `asset_index.json`
beside `raster_cache` — of every asset's `(size, mtime_ns, fingerprint,
width, height)`. A launch walks the tree with `scandir`, compares
stats, and pays the open cost **only for files that are genuinely new
or changed**. Steady state: zero opens.

It is deliberately NOT a cache of pixels — `raster_cache` is that. This
is a cache of *facts about files*, and it is the cheap half that the
expensive half kept re-deriving.

### Why not simply move the assets to an SSD

Owner's ruling, 2026-08-12: **no.** Where the art sits is the
installer's business; the program must be fast on an ordinary machine
with an ordinary disk — his words, that a user must not be required to
own an aeroplane of a computer to run a clock.
<!-- lang-ok: the owner's own verdict, quoted below in his words -->
*"ne traži od korisnika da imaju jebeni avion od kompjutera"*
An HDD makes the old code's cost visible (~36 ms of seek per file ×
2,511), but the cost was always wrong. Doing the work once instead of
every launch is the fix; faster hardware only hides it.

## Connections

### Uses
- [Raster Store](raster_store.md) — `compute_fingerprint`, the sampled
  content-key ALGORITHM. This module owns the memo; that module owns
  the recipe and the cache naming built on it (Rule #5). The
  `attach_fingerprint_source` hook lets `source_prefix` read this
  index without importing it — so the working-set subprocess workers
  keep importing a dependency-light `raster_store`, exactly as its own
  docstring promises.
- [Config (folder)](../../config/___config.md) — `paths`
  (`assets_dir`, the user directory)

### Used by
- [Asset Variants](asset_variants.md) — `warm_working_set` reads widths
  from here instead of opening every PNG
- [Warm](../../app/__about/warm.md) — phase 0 refreshes the index, and
  the cache-GC phase reads its fingerprints instead of re-sampling the
  whole tree
- [Raster Store](raster_store.md) — through the attached hook, so every
  existing `source_prefix` caller (the Encyclopedia's hundreds of path
  resolutions included) is served from the index with no change of its
  own

## Functions

### `refresh(should_stop=None, progress=None) -> tuple[int, int]`
The one walk. Returns `(known, rescanned)`. Walks `assets/` with
`os.scandir`, keeps every entry whose `(size, mtime_ns)` matches the
stored record, and re-reads the rest **in a thread pool** — both the
fingerprint windows and the image header release the GIL, so the warm
thread waits on futures instead of holding it. Prunes records whose
file is gone. Marks the index dirty; `save()` publishes it.

### `fingerprint(path) -> str | None`
The index-served content key. `None` for anything outside `assets/`
(the caller falls back to `raster_store`'s own in-process memo), which
is what keeps user-directory files and test fixtures working unchanged.

### `image_size(path) -> tuple[int, int] | None`
Width and height without opening the file. `None` when unknown — the
caller opens it and the answer lands in the index.

### `save() / load() / index_path()`
Atomic publish, lazy read, and where it lives. A corrupt or
version-stale index is DISCARDED, never repaired: the next refresh
rebuilds it, which costs one slow launch and can never serve a wrong
answer.

## Design Decisions

- **Keyed by `(size, mtime_ns)`, not by content.** Deciding whether to
  re-read a file may not itself require reading the file. The
  fingerprint is what the index STORES; the stat pair is what decides
  whether the stored value is still true. A same-size, same-mtime edit
  keeps a stale entry — the same documented limit `raster_store`
  already carries for its sampled window, and no editor produces one.
- **A missing answer is never an error.** Every getter returns `None`
  rather than raising or guessing, and every caller keeps its existing
  slow path. The index can be deleted at any moment; the program is
  only slower (Rule #1 — degraded and visible, never absent).
- **Version-stamped and discarded, not migrated.** `INDEX_VERSION`
  bumps whenever the record's shape or the fingerprint recipe changes.
  A one-launch rebuild is cheap; a subtly-wrong migration is not.
- **The GUI thread never triggers `refresh`.** It may READ the index
  (that is one dict lookup); building it belongs to the warm thread.
- **Not merged into `raster_store`.** That module is dependency-light
  on purpose so subprocess workers import it cheaply. This one knows
  about `config.paths` and Qt's image reader. The hook keeps the
  arrow pointing one way.
