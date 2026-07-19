# Ring Presets

**Script:** [Ring Presets (script)](rings.py)

## Purpose
Loads the ring preset "cards" (owner spec): bundled ones from
`Database/ring_presets.json` — DOMY (flame), Morph (chalice), Omega
(seal: every hour number on its own position, Ω at the bottom), Templar
(seal: the templar-cross glyph on all six) and Mason (seal: the
banknote's G/S/M/Ω/N/A, ROADMAP 15b, see below) — plus the user's
CUSTOM rings from the settings, each `{name, positions, letters}`. The
positions signature resolves the LAYOUT (`RING_LAYOUTS`: flame /
chalice / seal — the ring face with matching gaps and the metal
triangle). Validation is loud: an unknown position set, an unknown
glyph, a count mismatch or a duplicate name raises with the offending
entry named.

**RENAMES (TASK 2, MASON/ICONS round, owner verdicts 2026-07-19, third
batch):** the bundled cards were "MORPH", "NUMBERS" and "MASON G" —
renamed to "Morph", "Omega" and "Mason" to match the rest (DOMY stays
DOMY). `app.settings_store` migrates an older settings file's stored
"MASON G"/"NUMBERS" onto the new names ("MORPH" -> "Morph" is a pure
case change the store's existing case-insensitive fold already bridges
for free, no dedicated migration entry needed). New bundled preset
**Templar**: the seal layout, all six positions wearing the templar-
cross glyph (`✠`, `constants.RING_LETTER_FILES`), no motto, no legend —
its own `triangle` override (see below) is the SAME `[12, 20, 4]`
Trinity/Union split Mason and Omega now both carry too.

**Mason (ROADMAP 15b, CANON.md §The Banknote):** the owner's earlier
`InGodWeTrust_UVS_BIG.png` hexagram, upgraded onto the seal layout —
positions `12 16 20 24 4 8` wear letters `G S M Ω N A`. Extra OPTIONAL
card fields, wired through `validate_preset` and `app.controller.
build_skin`:

- **`triangle`** — a 3-position override of the seal layout's own
  (empty) metal triangle, so a 6-letter preset can split into two
  3-letter metal groups instead of the seal's own plain one-finish-on-
  all-six. CANON reads the hexagram as TWO triangles — the Trinity
  (12/20/4 = G, M, N — God, the Master, the Nazarene) and the Union
  (16/24/8 = S, Ω, A — Sigma, Omega, Alpha) — so Mason's card sets
  `"triangle": [12, 20, 4]`, the same rule `_letter_metal` already
  applies to DOMY/Morph's 4-letter triangle, now on a 3+3 split. Only
  valid on the seal layout; raises otherwise. **TASK 3 (MASON/ICONS
  round):** Omega and Templar now carry the SAME `triangle` field too
  — but on all three (Mason/Omega/Templar) the override only actually
  APPLIES when the owner's per-preset "Two metals" toggle
  (`Settings.ring_two_metals`, `app.controller._ring_two_metals`) is
  on for that preset; off, the card reads exactly like one with no
  `triangle` at all (one finish on all six). Default matching the
  pre-Task-3 look: Mason on, Omega/Templar off
  (`constants.RING_TWO_METALS_DEFAULT`).
- **`legend`** — position -> `{name, reading}`, the per-letter HOVER
  LEGEND text (what that letter stands for), quoted verbatim from
  CANON's Banknote table. Flows into `SkinDefinition.ring.
  letter_legend` (hour -> entry) and answers in
  [Compositor](../render/compositor.md)'s ring-band hover — every
  bundled preset without a `legend` (DOMY, Morph, Omega, Templar) and
  every custom ring stays silent there, unchanged. **TASK 2 (owner
  "može" 2026-07-19):** each `reading` may carry a SECOND
  `\n\n`-separated paragraph — the AXIS-OPPOSITION line, "Across the
  wheel: {letter} — {phrase}." The Mason hexagram's six seats form THREE diameters
  (opposite = +12h/180°): **N(4h)↔S(16h)** the Nazarene against Satan
  (the Advocate against the Accuser, 1 John 2:1 / Revelation 12:10),
  **A(8h)↔M(20h)** the Angel against the Master (Hebrews 1:14's
  ministering spirit against Pride's boss-syndrome), **G(12h)↔Ω(24h)**
  God against the End (Revelation 1:8's Alpha facing the Omega). Both
  seats of one axis quote the SAME clause, each naming the OTHER
  letter as the pointer — see [The DOMY Canon](../CANON.md)'s §The
  Banknote for the sealed wording.

- **`motto`** (TASK 1, owner "može radi" 2026-07-19; corrected
  MOTO-FIX round, owner correction 2026-07-19, the dollar's Great Seal
  reference image; corrected ANNUIT WORD-GAP round, owner correction
  2026-07-19, third batch) — a list of Great Seal motto entries, each
  `{text, pins, clockwise}`: `text` is the motto string (spaces
  included), `pins` is a list of `[letter, occurrence, position]`
  triples — e.g. `["N", 1, 4]` pins the FIRST "N" in `text` to the 4h
  ring seat, `["O", 3, 24]` the THIRD "O" to the bottom/24h seat
  (occurrence counting from 1, so a repeated letter can be pinned at
  any of its appearances — the O ENDING "ORDO", not NOVUS's own O) —
  and the optional `clockwise` (default true) picks the arc's reading
  direction: true sweeps increasing angle (the TOP arc), false sweeps
  decreasing angle (the BOTTOM arc — see [Motto](../core/motto.md)'s
  Design Decisions for why the bottom must reverse direction to still
  read left-to-right to a viewer). Validated and ANGLE-SOLVED by
  `validate_preset` (delegating the actual per-glyph math to
  [Motto](../core/motto.md)'s `motto_glyph_angles`) at LOAD time, so a
  broken pin (an out-of-range occurrence, a position that is not one
  of the preset's own six, a letter the shared PNG library cannot
  draw) fails loudly at startup — never a silently blank or lopsided
  arc. With exactly 2 pins (ANNUIT COEPTIS's own shape — pinned only at
  its first and last character) the ANNUIT WORD-GAP layout applies:
  every letter advances at the fixed `defaults.
  RING_MOTTO_LETTER_STEP_DEG` step from both pins inward, and the
  leftover slack becomes ONE BIG GAP at the motto's own single interior
  word gap — instead of spreading evenly across the whole span (the
  owner's "too wide" correction). Card entries resolve to `{"text",
  "angles"}` (one angle per character, spaces included);
  `app.controller.build_skin` then pairs every NON-space character with
  its gold-master asset path into `SkinDefinition.ring.motto`, which
  `RingLayer._draw_motto` draws outside the ring band (see
  [Layers](../render/layers.md)). Only Mason carries one today:

  | Motto | Pins (letter, occurrence, seat) | Direction | Own arc |
  |---|---|---|---|
  | ANNUIT COEPTIS | A→1st→8h, S→1st→16h | clockwise | 8h → 16h (120°, over the TOP through noon) |
  | NOVUS ORDO SECLORUM | N→1st→4h, O→3rd→24h, M→1st→20h | counterclockwise | 4h → 20h (120°, under the BOTTOM through 24h) |

  The two arcs are now angularly DISJOINT (top 300°-360°-60°, bottom
  120°-180°-240°) — exactly like the real seal, ANNUIT COEPTIS over the
  pyramid, NOVUS ORDO SECLORUM under it — so BOTH draw at the SAME
  `RING_MOTTO_RADIUS_FRACTION` (the first round's two-radius scheme,
  `RING_MOTTO_RADIUS_STEP`, is deleted — Rule #6). The MOTO-FIX round
  (owner correction 2026-07-19, the Great Seal reference image) undid
  the first round's mistaken "Mason reads twice" shared-angle design
  (both mottos' own O and own S landing on the identical seat); the
  ANNUIT WORD-GAP round then tightened ANNUIT COEPTIS's own letter
  spacing (NOVUS ORDO SECLORUM's own 3-pin segments already read tight
  by construction — untouched); see [Motto](../core/motto.md)'s Design
  Decisions for both reasonings in full.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `RING_LAYOUTS`,
  `RING_LETTER_FILES`, database path
- [Motto](../core/motto.md) — `motto_glyph_angles`, the per-glyph angle
  solve for the optional `motto` card field
- Shared JSON loading ([Data (folder)](___data.md))

### Used by
- [App Controller](../app/controller.md) — `build_skin` resolves the
  active preset (and, TASK 3, its own metal-split choice via
  `_ring_two_metals`/`constants.RING_TWO_METALS_DEFAULT`); the Design ▸
  Ring menu lists every loaded name and carries the per-preset "Two
  metals" toggle
- [Settings Store](../app/settings_store.md) — validates the chosen
  ring name against the loaded set (migrating a stored old bundled
  name, TASK 2) and the per-preset `ring_two_metals` dict (TASK 3)

## Functions

- `ring_presets(custom=())`: name → `{positions, letters, layout}` for
  every bundled + custom preset
- `validate_preset(entry)`: the shared card validator (also used for
  the Settings custom-ring builder input)
- `_validate_motto(name, raw, positions)`: the optional `motto` field's
  own validator — unknown letters, out-of-range pin positions and a
  broken angle solve all raise with the preset named (Rule #1)
