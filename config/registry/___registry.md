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
`constants` and `pantheon` both derive from it without a cycle.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Algorithmic | the derivation layer — every legacy table computed from `WEEK` in one assignment apiece — [about](__about/__init__.md) · [flow](__flow/__init__.md) |
| `sentinel.py` | Standard | `COMPUTED` — the one value the registry refuses to freeze — [about](__about/sentinel.md) |
| `week/` | (package) | THE WEEK REGISTRY, the 6+3 kind: 35 theme entries split one file per group — [folder](week/___week.md) |

## Connections

### Uses
- nothing — `week.py` is a leaf by design; the derivation layer reaches
  `config.continents` lazily, inside a function, for the one family
  whose stems are computed rather than declared.

### Used by
- [Constants](../__about/constants.md) — the weekday master list, the
  Ninth tables and the metal looks
- [Pantheon](../__about/pantheon.md) — seat names, dirs, stems, duals,
  titles, rosters and the picker menu
- [The Theme Dictionary](../../THEME-REGISTRY.md) — the design brief
  this package answers

### Related
- [Config (folder)](../___config.md)
