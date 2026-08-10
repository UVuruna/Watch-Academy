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
- [Art Warm](../../render/__about/art_warm.md) — phase 1, the jewel recolors
- [Asset Variants](../../render/__about/asset_variants.md) — phase 2,
  working-set downscales: the ledger drain (`drain_pending_working`,
  owner bar 2026-08-09 — VISIBLE-FIRST, exactly what the dial's first
  paint already asked for and skipped) BEFORE the alphabetical
  whole-tree sweep (`warm_working_set`)
- [Encyclopedia Warm](encyclopedia_warm.md) — phase 3
- [Compositor](../../render/__about/compositor.md) — phase 4, through each watch's
  own `hover_sweep()` callable
- [Raster Store](../../render/__about/raster_store.md) — phase 5
  (0.14.709), `_collect_cache_garbage`: fingerprint the asset tree,
  sweep every cache entry no current source claims (the measured
  backlog was 10,039 files / 10.0 GB)
- [Config (folder)](../../config/___config.md) — `paths` (the asset
  walk and the cache directory)

### Used by
- [Watch Manager](watch_manager.md) — owns the background thread and arms it
  once every watch's first frame has painted

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
Walks the SIX phases in order (dial art, working-set ledger drain,
working-set bulk sweep, Encyclopedia, hover, cache GC), on ONE
background thread. `hover_sweeps`
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
