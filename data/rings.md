# Ring Presets

**Script:** [Ring Presets (script)](rings.py)

## Purpose
Loads the ring preset "cards" (owner spec): bundled ones from
`Database/ring_presets.json` — DOMY (flame), MORPH (chalice) and
NUMBERS (seal: every hour number on its own position, Ω at the
bottom, one metal for all six) — plus the user's CUSTOM rings from the
settings, each `{name, positions, letters}`. The positions signature
resolves the LAYOUT (`RING_LAYOUTS`: flame / chalice / seal — the ring
face with matching gaps and the metal triangle). Validation is loud:
an unknown position set, an unknown glyph, a count mismatch or a
duplicate name raises with the offending entry named.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `RING_LAYOUTS`,
  `RING_LETTER_FILES`, database path
- Shared JSON loading ([Data (folder)](___data.md))

### Used by
- [App Controller](../app/controller.md) — `build_skin` resolves the
  active preset; the Theme ▸ Ring menu lists every loaded name
- [Settings Store](../app/settings_store.md) — validates the chosen
  ring name against the loaded set

## Functions

- `ring_presets(custom=())`: name → `{positions, letters, layout}` for
  every bundled + custom preset
- `validate_preset(entry)`: the shared card validator (also used for
  the Settings custom-ring builder input)
