# Warm

**Script:** [Warm (script)](../warm.py) · **Flow:** [diagram](../__flow/warm.md)

## Purpose
The ONE background warm for the whole process (owner ruling 2026-07-28:
every watch used to run its own warm thread, so N watches walked the
SAME working-set files, Encyclopedia paths and hover probes N times —
visible in the startup log as every progress line printed two/three
times). The watches share one asset tree, one raster cache and one
`AssetCache`, so the work is done ONCE, in a fixed priority order.

## Connections

### Uses
- [Asset Index](../../render/__about/asset_index.md) — **phase 0**
  (0.14.950, the owner's 91.6-second launch): one `os.scandir` walk
  replaces three full-tree passes that opened every file on every
  launch. It runs first because every phase below reads from it — the
  working-set sweep takes its ROSTER and widths from it, the
  Encyclopedia's hundreds of `source_prefix` calls take fingerprints
  from it through `raster_store`'s attached hook, and the cache GC
  takes its whole valid-prefix set from it
- [Art Warm](../../render/__about/art_warm.md) — phase 1, the jewel
  recolors. Since 0.14.950 most letter finishes never reach it at all:
  [Letter Bake](../../render/__about/letter_bake.md) ships them
  pre-rendered, so `jewel_metal_path` resolves them without recording a
  recipe
- [Asset Variants](../../render/__about/asset_variants.md) — phase 2,
  working-set downscales: the ledger drain (`drain_pending_working`,
  owner bar 2026-08-09 — VISIBLE-FIRST, exactly what the dial's first
  paint already asked for and skipped) BEFORE the alphabetical
  whole-tree sweep (`warm_working_set`)
- [Encyclopedia Warm](encyclopedia_warm.md) — phase 3
- [Compositor](../../render/__about/compositor.md) — phase 4, through each watch's
  own `hover_sweep()` callable
- [Raster Store](../../render/__about/raster_store.md) — the last
  phase (0.14.709), `_collect_cache_garbage`: sweep every cache entry
  no current source claims (the measured backlog was 10,039 files /
  10.0 GB). It used to `rglob` the whole tree and fingerprint — i.e.
  open and sample 64 KiB of — every png/svg/jpg in 3.76 GB to build
  that roster, on every launch; since 0.14.950 it reads phase 0's
  index and costs no file opens at all
- [Config (folder)](../../config/___config.md) — `paths` (the asset
  walk and the cache directory)

### Used by
- [Watch Manager](watch_manager.md) — owns the background thread and arms it
  once every watch's first frame has painted

## THE 91.6-SECOND CORRECTION (2026-08-12) — read this before the table below

**The measurement below is real. Its commit title was a lie, and this
section exists so the lie cannot be read again without its correction.**

Commit `4c976cb` (0.14.872, 2026-08-09) is titled *"Measured — cold
responsiveness under the owner's 3-second bar."* The owner's report was
`profiling.json`'s **`"Working set warmup"` = 71.7 s**. That counter was
never measured by that round — not before its fix and not after. What
was measured was one watch on the default skin in an empty isolated
user directory: a different metric, on a different corpus, under a
different cache state. The round's own honest-scope paragraph said so
(it is still below, unedited). Then the winning claim went into the
commit title, where it was the only thing anyone would read; the task
was closed as done; no `[~]` was carried forward; and no test in the
suite measured the number the owner had actually reported.

Three days later the same counter read **91.6 s**, in a pass whose own
log line proved it built nothing: `[91.6s] working set complete — 961
oversized sources, **0 built cold**`.

**The 0.14.872 fix did not cause that.** `git show 0a913c1 --
render/asset_variants.py` shows the scan loop byte-identical before and
after; the fix moved WHERE builds happen (off the paint path, which
works and stands), and the 91.6 s contains no builds at all. It simply
never touched the reported number, and said it had.

Root cause of the 91.6 s, found 2026-08-12: three separate startup
passes re-derived, by OPENING files, facts unchanged since the previous
launch — the working-set sweep header-read 2,511 PNGs (3.76 GB) for
their widths, the cache GC fingerprinted the whole tree, and the
Encyclopedia warm fingerprinted its way through hundreds of paths
again. Assets sit on an HDD (`Get-PhysicalDisk`: Disk 0 HDD, the SSD is
`C:`), so ~36 ms of seek × 2,511 is the whole 91.6 s. The counter grew
from 71.7 s only because the tree grew: 795 working-set files on
2026-07-28, 961 today. The cure is
[Asset Index](../../render/__about/asset_index.md) — phase 0 above.

**What is measured now, and how honestly** (this machine,
2026-08-12, against the owner's REAL user directory and REAL
`raster_cache`, not an isolated one):

| | |
|---|---|
| working-set sweep, OLD code — file opens | **2,511** |
| working-set sweep, NEW code — file opens | **0** |
| index refresh (warm) + working-set sweep, per launch | **0.51 s** |
| index build, cold — once per install or art change | 1.13 s |

**The honest gap, named rather than buried:** the owner's 91.6 s was a
COLD-OS-cache number on an HDD. This machine's OS cache is warm from
the work itself, so the same loop times 0.21 s here — the seconds
cannot be reproduced on demand, and any figure claiming to be his is
arithmetic, not measurement. What IS proved without a stopwatch is the
CAUSE: the open count, 2,511 → 0, asserted by
`tests/test_startup_cost.py` rather than described here. His 91.6 s
becomes a real number again only on his next launch after a reboot, and
until he reports it this line stays as it is.

## Measured (MIGRATE-GUI Phase 1, owner bar 2026-08-09 — "3 seconds
cold, everything responsive")

**Method:** a real `python main.py`-shaped launch (real `QApplication`,
real `AppController`, real assets) run as its own process, pointed at
an ISOLATED, empty directory via `config.paths.user_dir`'s
`WATCH_ACADEMY_USER_DIR_OVERRIDE` dev escape hatch (never the owner's live
`%APPDATA%\DOMY Watch`) so `settings.json`/`raster_cache` start
genuinely cold. Three milestones, timestamped from process start: a
`QTimer.singleShot(0, ...)` armed the instant `AppController.run()`
returns (its own fire time IS how long the event loop was blocked
before it could service anything — the exact shape of "window drag/
right-click dead"); the first watch's `first_painted` signal; and
(after the fix only) both derived-image ledgers
(`asset_variants.pending_working()` + `asset_recolor.pending_art()`)
reading empty, i.e. the dial's own art is fully real, not standing in.

One watch, the shipped DEFAULT skin (`hexa` pointer, `planets` weekday
theme, `show_weekday=True` — enough oversized working-set art to
matter: `Saturn`/`Jupiter`/`Sun_Eclipse`/`earth_atmo_europe_night`, all
≥800px, needed a working copy on this very first paint):

| Milestone | BEFORE (this round's own fix reverted) | AFTER |
|---|---|---|
| GUI thread responsive (zero-delay timer fires) | 2.943 s | **0.918 s** |
| First painted frame | 4.516 s | **1.345 s** |
| Dial fully dressed (both ledgers empty) | *(no ledger; the old code's first paint already forces every inline build it needs, so "painted" and "dressed" are the same moment)* | 4.216 s |

AFTER clears the owner's 3 s bar on responsiveness and first paint with
real headroom (0.92 s / 1.35 s), and the dial is fully dressed as real
pixels — not a placeholder — by 4.2 s, inside the ~5 s progressive-art
allowance. BEFORE's own numbers, on this modest single-watch DEFAULT
skin alone, already sit at 2.9 s / 4.5 s — over budget before a single
customization is added.

**Honest scope note:** this measures ONE watch on the DEFAULT skin, not
the owner's actual three-watch, richly customized setup his 71.7 s
`profiling.json` entry ("Working set warmup") and 75–90 s reports came
from — reproducing that exactly (three watches, his specific weekday
themes/archetypes, his 3.4 GB / 2,318-file corpus) was out of this
round's time budget. The mechanism the fix installs — a working-set
miss is named ONCE in a process-wide ledger and shared by every
watch/caller through `render.assets.shared_cache`, never rebuilt per
watch — is architecturally the same fix that already ended the
N-times-duplicated-work class of bug for the metal-recolor ledger
(`app/__about/watch_manager.md` → THE ONE COPY RULE), so the SAME
watches × assets multiplication that made 71.7 s out of one watch's
slower number is expected to shrink by the same shared-ledger
mechanism — but that is reasoning from the fix's shape, not a second
measurement, and is named here as exactly that.

## Functions

### `run_warm(hover_sweeps=(), progress=None, on_art_ready=None, should_stop=None)`
Walks the SEVEN phases in order — **the asset index first** (0.14.950;
every phase after it is a customer of it), then dial art, the
working-set ledger drain, the working-set bulk sweep, Encyclopedia,
hover, and cache GC — on ONE background thread. `hover_sweeps`
is one callable per watch (each closes over its own compositor/dial
size) — they run one after another, never in parallel, so N
concurrent pure-Python sweeps never compete with each other for the GIL.
`should_stop` is checked between phases so Exit does not wait for a
90-second cold walk to finish (the thread is a daemon and would die with
the process anyway; the check just means it stops between files instead
of mid-write).

## Design Decisions
- **A free function, not a class** — it holds no state; the phases are
  ordered calls, and everything they need is passed in. The thread, the
  roster and the stop flag belong to [Watch Manager](watch_manager.md).
- **A background THREAD does not shield the GUI from image work** —
  the correction the 0.14.706 round wrote in blood: this doc used to
  claim "the image phases release the GIL around their C-level codec
  calls", and they DON'T — a multi-MB `QImage` decode/scale/encode
  holds the GIL for seconds, which is exactly the owner's 75-second
  unmovable window. That is why the working set's COLD builds now run
  in subprocesses ([Asset Variants](../../render/__about/asset_variants.md));
  numpy (the recolors) genuinely does release the GIL, so the art drain
  may stay on threads.
- **Hover articles run after the builds, deliberately** — pure Python,
  so it is the phase that competes hardest with the GUI thread for the
  GIL. Running it first is what made a freshly launched dial feel stuck.
- **Cache GC runs dead last** — pure disk hygiene must never delay a
  pixel anyone is waiting for, and running after every build phase
  means a freshly-built cache is never the thing being judged stale.
- **VISIBLE-FIRST working-set order** (owner bar 2026-08-09,
  MIGRATE-GUI Phase 1): the ledger drain runs before the alphabetical
  whole-tree sweep because the ledger is not an arbitrary subset — it
  is EXACTLY what the dial's own first paint(s) asked for and skipped
  (`render.assets.AssetCache.pixmap_by_height` records a miss instead
  of decoding inline). Draining that first dresses the on-screen dial
  in a few seconds even stone-cold; the bulk sweep then finishes
  whatever nothing has asked for yet, skipping files the ledger already
  built (`cache.exists()`).
