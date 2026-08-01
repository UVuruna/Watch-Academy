# data/

Repositories over `Database/*` — the only code that knows the bundled
JSON/SQLite file schemas. Loud failures with the supported range named
in the message (Rule #1); plain dataclasses out; no Qt (enforced by the
purity test).

## Files

| File | Tier | One line |
|------|------|----------|
| `locations.py` | Algorithmic | lazy world-locations tree, shape-classified by depth — [about](__about/locations.md) · [flow](__flow/locations.md) |
| `seasons.py` | Standard | year → `YearAnchors`, extract-and-discard over `seasons_utc.json` — [about](__about/seasons.md) |
| `moon_phases.py` | Standard | year → `MoonWindow`, windowed over `moonPhases_utc.json` — [about](__about/moon_phases.md) |
| `deep_time.py` | Algorithmic | optional full-span SQLite pack, proxy-shifted years + eclipse catalog — [about](__about/deep_time.md) · [flow](__flow/deep_time.md) |
| `observatory.py` | Algorithmic | Observatory chart bundles + extrema detection — [about](__about/observatory.md) · [flow](__flow/observatory.md) |
| `symbolism.py` | Algorithmic | per-body blurbs + article corpus, `$ref` reseat resolution — [about](__about/symbolism.md) · [flow](__flow/symbolism.md) |
| `encyclopedia.py` | Standard | the Encyclopedia's own sections, overlay-localized — [about](__about/encyclopedia.md) |
| `cube_model_export.py` | Algorithmic | Character Cube canon exported as a 3D Preview MODEL — [about](__about/cube_model_export.md) · [flow](__flow/cube_model_export.md) |
| `translations.py` | Algorithmic | corpus collection, gtx client, hash-tracked cache, sr transliteration — [about](__about/translations.md) · [flow](__flow/translations.md) |
| `rings.py` | Algorithmic | ring preset cards, layout resolution, motto angle solving — [about](__about/rings.md) · [flow](__flow/rings.md) |
| `hands.py` | Standard | hand pack loading + validation — [about](__about/hands.md) |
| `_io.py` | Trivial | `load_json_checked()` / `year_bounds()` — the shared JSON loader every repository above calls |
| `__init__.py` | Trivial | docstring only, no code |

## Connections

### Uses
- [Config (folder)](../config/___config.md) — paths and coverage ranges
- [Core (folder)](../core/___core.md) — `YearAnchors`, `MoonWindow`,
  `EclipseEvent`, `cube_seating`, `deep_time`, `motto`
- [Database (folder)](../Database/___database.md) — the JSON/SQLite
  files
- [Config Cube](../config/__about/cube.md) — the Character Cube canon
  (`cube_model_export.py` only)

### Used by
- [App (folder)](../app/___app.md) — controller, settings dialog,
  encyclopedia browser
- [Render (folder)](../render/___render.md) — compositor,
  cube_preview3d bridge, instrument diagrams
- [Core (folder)](../core/___core.md) CLI selftest
- [Tests (folder)](../tests/___tests.md) — run against the LIVE bundled
  files

## Design Decisions

- **`_io.py` stays a plain function module, not a base class** — a
  handful of small repositories does not justify a hierarchy (Rule #5
  is about not duplicating logic, not about forcing OOP where a
  function suffices).
- **Bundled-first chaining:** `SeasonsRepository` and
  `MoonPhaseRepository` each accept an optional `deep=` repository,
  injected once at startup by the controller when
  `DeepTimeRepository.detect()` finds the optional SQLite pack.
  Bundled years NEVER fall through to the pack — the minute-exact tier
  stays bit-identical whether or not the pack is installed; only a
  year the bundle has no entry for chains to it, and the WHOLE window
  then comes from the pack alone, never mixed with the bundle.
- **`coverage()` is read from the data on every repository that has
  one** (`seasons`, `moon_phases`, `deep_time`) — never hardcoded
  (Rule #4), so a future Deep Time pack simply widens its own file and
  every consumer follows without a code change.
- **`cube_model_export.py` lives in `data/` despite not reading
  `Database/*`** — it belongs here by RESPONSIBILITY (a read-only
  export over canon data, the same shape as every other repository in
  this folder), not by import source; it reads `config.cube` /
  `core.cube_seating` instead of a JSON file.
