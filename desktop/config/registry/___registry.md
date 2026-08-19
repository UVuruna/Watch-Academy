# config/registry/

**THE REGISTRY** — one dictionary of all themes, grouped by KIND
(owner decree 2026-08-01, designed with the owner 2026-08-04/05).

Theme knowledge used to live in ~20 tables across six modules, two
databases and a markdown ledger; the ~30 `WEEKDAY_THEME_FILES[key] =
...` assignments that followed their own definition were the visible
symptom, and they were never exceptions to a rule — they were DATA with
no home. Here a theme declares its whole contract in ONE entry, and
every table a consumer reads is COMPUTED from it in ONE assignment, so
THE CONFIG SECTION LAW's ban on post-definition patching holds by
construction.

Layer: config — pure. `week.py` imports NOTHING, which is what lets
`pantheon`, `config/ninth.py` and `config/ring.py` all derive from it
without a cycle. Since THE CONSTANTS SPLIT (2026-08-19) `week.py` also
holds the WEEKDAY VOCABULARY itself — bodies, labels, full names, figure
rosters, the Sunday-first index and the per-pointer weekday slots — and
`slots.py` holds BOTH slot vocabularies, the dial's three and the
wheel's three.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Algorithmic | the derivation layer — every legacy table computed from `WEEK` in one assignment apiece — [about](__about/__init__.md) · [flow](__flow/__init__.md) |
| `sentinel.py` | Standard | `COMPUTED` — the one value the registry refuses to freeze — [about](__about/sentinel.md) |
| `pointers.py` | Algorithmic | THE POINTER REGISTRY — the permission matrix: what each pointer may carry, per shape — [about](__about/pointers.md) |
| `week.py` | Algorithmic | THE WEEK REGISTRY, the 6+3 kind: all 35 theme entries, whole — [about](__about/week.md) · [flow](__flow/week.md) |
| `availability.py` | Standard | THE AVAILABILITY FIELD — base vs. locked, per WEEK theme — [about](__about/availability.md) |
| `slots.py` | Standard | THE SLOT REGISTRY — the three dial slots and the `Settings` field each keeps its mode/style/theme/roster/names/enablement in — [about](__about/slots.md) |

## Connections

### Uses
- nothing — `week.py` is a leaf by design; the derivation layer reaches
  `config.continents` lazily, inside a function, for the one family
  whose stems are computed rather than declared.

### Used by
- [Ninth](../__about/ninth.md) and [Ring](../__about/ring.md) — the
  Ninth tables and the metal looks, derived here
- [Pantheon](../__about/pantheon.md) — seat names, dirs, stems, duals,
  titles, rosters and the picker menu
- [The Theme Dictionary](../../../docs/archive/THEME-REGISTRY.md) — the design brief
  this package answers

### Related
- [Config (folder)](../___config.md)
