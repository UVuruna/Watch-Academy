# Art Warm

**Script:** [Art Warm (script)](../art_warm.py) · **Flow:** [diagram](../__flow/art_warm.md)

## Purpose
Build the dial's derived art (the ring letters' metal finishes) OFF the
GUI thread, so a paint never waits on a recolor. Owner decree
2026-07-28, after a slow-start measurement: a cold raster cache used to
run 15 metal recolors — 3.6 s of numpy each — INSIDE `paintEvent`, so
three watches meant ~15 s with nothing on screen. [Asset
Recolor](asset_recolor.md)'s `letter_metal_file` now hands back the
gold master while a finish is missing and records the recipe in its
lazy ledger; this module drains that ledger on the shared background
thread and calls back so the dial repaints in its real metal.

This is the FIRST warm phase (`app.warm.run_warm` owns the order) — the
pixels the user is actually looking at come before the working-set
downscales, the Encyclopedia inventory and the hover sweep. It runs
once per PROCESS at startup (every watch shares one raster cache, so N
watches asking for the same file is one job, not N) — and again ON
DEMAND: a finish/shade/theme switch after startup records fresh
recipes, and [Watch Manager](../../app/__about/watch_manager.md)'s
`kick_art_warm` (rung by [Asset Recolor](asset_recolor.md)'s stale
notifier the moment a paint observes the miss) drains them without a
restart (owner bug 2026-08-02).

## Connections

### Uses
- [Asset Recolor](asset_recolor.md) — `pending_art()`, `ensure_variant()`
  and the lazy ledger they share
- [Config (folder)](../../config/___config.md) — `profiling` (the "Dial
  art warmup" timer)

### Used by
- `app.warm.run_warm` — phase 1 of the one process-wide warm sequence

## Functions
- `warm_pending_art(progress=None, on_ready=None, should_stop=None)`:
  builds every recorded-but-missing derived image, newest recipes last;
  returns how many were built. `on_ready` fires after EACH build (not
  once at the end) so the dial upgrades finish by finish.

## Design Decisions
- **Repeat until the ledger stops growing, never a single pass.** The
  GUI thread keeps recording new recipes while the drain runs — a paint
  reaching art the previous pass had not seen. One pass would leave the
  dial half-dressed.
- **Each job is attempted at most once** (an `attempted` set) — a cache
  write can fail (full disk, locked file), which would otherwise leave
  the job "pending" forever and turn the repeat loop into an infinite
  one; a failed job simply keeps its master art (Rule #1: degraded and
  visible, never hung).
