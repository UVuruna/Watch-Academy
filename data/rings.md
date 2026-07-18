# Ring Presets

**Script:** [Ring Presets (script)](rings.py)

## Purpose
Loads the ring preset "cards" (owner spec): bundled ones from
`Database/ring_presets.json` — DOMY (flame), MORPH (chalice), NUMBERS
(seal: every hour number on its own position, Ω at the bottom, one
metal for all six) and MASON G (seal: the banknote's G/S/M/Ω/N/A,
ROADMAP 15b, see below) — plus the user's CUSTOM rings from the
settings, each `{name, positions, letters}`. The positions signature
resolves the LAYOUT (`RING_LAYOUTS`: flame / chalice / seal — the ring
face with matching gaps and the metal triangle). Validation is loud:
an unknown position set, an unknown glyph, a count mismatch or a
duplicate name raises with the offending entry named.

**MASON G (ROADMAP 15b, CANON.md §The Banknote):** the owner's earlier
`InGodWeTrust_UVS_BIG.png` hexagram, upgraded onto the seal layout —
positions `12 16 20 24 4 8` wear letters `G S M Ω N A`. Two extra
OPTIONAL card fields, both wired through `validate_preset` and
`app.controller.build_skin`, that only this preset uses today:

- **`triangle`** — a 3-position override of the seal layout's own
  (empty) metal triangle, so a 6-letter preset can split into two
  3-letter metal groups instead of NUMBERS' one-finish-on-all-six.
  CANON reads the hexagram as TWO triangles — the Trinity (12/20/4 =
  G, M, N — God, the Master, the Nazarene) and the Union (16/24/8 = S,
  Ω, A — Sigma, Omega, Alpha) — so MASON G's card sets
  `"triangle": [12, 20, 4]`: the Trinity vertices wear the chosen
  finish metal, the Union vertices the counter-metal, the same rule
  `_letter_metal` already applies to DOMY/MORPH's 4-letter triangle,
  now on a 3+3 split. Only valid on the seal layout; raises otherwise.
- **`legend`** — position -> `{name, reading}`, the per-letter HOVER
  LEGEND text (what that letter stands for), quoted verbatim from
  CANON's Banknote table. Flows into `SkinDefinition.ring.
  letter_legend` (hour -> entry) and answers in
  [Compositor](../render/compositor.md)'s ring-band hover — every
  bundled preset without a `legend` (DOMY, MORPH, NUMBERS) and every
  custom ring stays silent there, unchanged.

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
