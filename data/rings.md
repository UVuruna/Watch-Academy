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
  custom ring stays silent there, unchanged. **TASK 2 (owner "može"
  2026-07-19):** each `reading` may carry a SECOND `\n\n`-separated
  paragraph — the AXIS-OPPOSITION line, "Across the wheel: {letter} —
  {phrase}." The MASON G hexagram's six seats form THREE diameters
  (opposite = +12h/180°): **N(4h)↔S(16h)** the Nazarene against Satan
  (the Advocate against the Accuser, 1 John 2:1 / Revelation 12:10),
  **A(8h)↔M(20h)** the Angel against the Master (Hebrews 1:14's
  ministering spirit against Pride's boss-syndrome), **G(12h)↔Ω(24h)**
  God against the End (Revelation 1:8's Alpha facing the Omega). Both
  seats of one axis quote the SAME clause, each naming the OTHER
  letter as the pointer — see [The DOMY Canon](../CANON.md)'s §The
  Banknote for the sealed wording.

- **`motto`** (TASK 1, owner "može radi" 2026-07-19) — a list of Great
  Seal motto entries, each `{text, pins}`: `text` is the motto string
  (spaces included) and `pins` is a list of `[letter, occurrence,
  position]` triples — e.g. `["N", 1, 4]` pins the FIRST "N" in `text`
  to the 4h ring seat, `["O", 3, 12]` the THIRD "O" to noon (occurrence
  counting from 1, so a repeated letter can be pinned at any of its
  appearances — the O ENDING "ORDO", not NOVUS's own O). Validated and
  ANGLE-SOLVED by `validate_preset` (delegating the actual per-glyph
  math to [Motto](../core/motto.md)'s `motto_glyph_angles`) at LOAD
  time, so a broken pin (an out-of-range occurrence, a position that
  is not one of the preset's own six, a letter the shared PNG library
  cannot draw) fails loudly at startup — never a silently blank or
  lopsided arc. Card entries resolve to `{"text", "angles"}` (one angle
  per character, spaces included); `app.controller.build_skin` then
  pairs every NON-space character with its gold-master asset path into
  `SkinDefinition.ring.motto`, which `RingLayer._draw_motto` draws
  outside the ring band (see [Layers](../render/layers.md)). Only
  MASON G carries one today:

  | Motto | Pins (letter, occurrence, seat) | Own arc |
  |---|---|---|
  | ANNUIT COEPTIS | A→1st→8h, O→1st→12h, S→1st→16h | 8h → 16h (120°, through noon) |
  | NOVUS ORDO SECLORUM | N→1st→4h, O→3rd→12h, S→2nd→16h, M→1st→20h | 4h → 20h (240°, the long way through 8h/12h/16h) |

  The two arcs' pinned O (noon) and S (16h) land at the IDENTICAL
  angle on purpose — "MASON outside, G inside" reads TWICE — so they
  draw at two different radii (`RING_MOTTO_RADIUS_FRACTION` for
  ANNUIT COEPTIS, `+ RING_MOTTO_RADIUS_STEP` for NOVUS ORDO SECLORUM);
  see [Motto](../core/motto.md)'s Design Decisions for why one arc
  could not serve both.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `RING_LAYOUTS`,
  `RING_LETTER_FILES`, database path
- [Motto](../core/motto.md) — `motto_glyph_angles`, the per-glyph angle
  solve for the optional `motto` card field
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
- `_validate_motto(name, raw, positions)`: the optional `motto` field's
  own validator — unknown letters, out-of-range pin positions and a
  broken angle solve all raise with the preset named (Rule #1)
