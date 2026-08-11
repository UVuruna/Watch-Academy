# Settings Ring

**Script:** [Settings Ring (script)](../settings_ring.py)

## Purpose

Ring-name resolution + custom-ring-card normalization, split out of
[Settings Store](settings_store.md) (THE STRUCTURE LAW, owner decree
2026-08-05 — the compositional ring model's own migration pushed the
settings file over the line-of-logic threshold). Holds the bundled
preset RENAME table (Mason → Dollar, Omega → The One, Morph/Pilot → LOOP),
the shared per-ring-name dict loader (`ring_eye_shine`,
`ring_inner`, the crown-text fields all use it) and
the legacy custom-ring-card migration (`positions` → `outer`).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.RING_OUTERS`
- [Rings (data)](../../data/__about/rings.md) — `validate_preset`

### Used by
- [Settings Store](settings_store.md) — `fold_ring_name`,
  `load_named_dict`, `normalized_ring_card`

## Functions

- `fold_ring_name(raw_name, by_fold)`: a stored ring name resolved to
  its current bundled/custom name, or `None` when it names nothing
  loaded.
- `load_named_dict(raw, key, by_fold, valid)`: one stored per-ring-name
  dict, loaded with the shared lenient policy (an invalid value or an
  unresolved name is dropped, never corrupts the whole file).
- `migrate_legacy_ring_card(entry)`: a custom ring card saved before
  the compositional ring model (`positions`, no `outer`) upgraded in
  place by matching its positions signature.
- `normalized_ring_card(entry)`: one custom ring card, validated and
  stored in its JSON-serializable shape (`{name, outer, jewels,
  thematic?}`).
