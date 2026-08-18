# Locks

**Script:** [Locks (script)](../locks.py)

## Purpose
`KeyedLocks` — a lazily grown table of `threading.Lock`, one per key, so
that the same key is never generated twice at once and two different keys
never wait for each other.

## Connections

### Uses
- `threading` — nothing else; no Qt, no config, no disk

### Used by
- [Asset Recolor](asset_recolor.md) — `_VARIANT_LOCK`, one lock per
  pending metal-variant recipe
- [Asset Variants](asset_variants.md) — `_WORKING_LOCK`, one lock per
  pending working-set downscale

## Design Decisions
- **The table's guard is held only around the lookup**, never while the
  caller holds the per-key lock — so slow work under one key can never
  block the CREATION of a lock for another. That was already true of
  both hand-written copies; writing it once makes it true by
  construction.
- **Callable, not a `get()` method.** `with locks(key):` reads as the
  lock it is. The instance is the table.
- **Locks are never evicted.** A `threading.Lock` is a few dozen bytes
  and the key space is the derived-asset ledger, which is bounded by the
  art that ships; the two hand-written versions never evicted either.
