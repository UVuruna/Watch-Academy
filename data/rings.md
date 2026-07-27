# Ring Presets

**Script:** [Ring Presets (script)](rings.py)

## Purpose
Loads the ring preset "cards" (owner spec): bundled ones from
`Database/ring_presets.json` — DOMY (flame, the dark cross), PILOT
(chalice, the light cross — born MORPH), The One (seal: every hour
number on its own position, Ω at the bottom), Templar (seal: the
templar-cross glyph on all six), Dollar (seal: the banknote's
👁/S/M/Ω/N/A, ROADMAP 15b, see below) — plus the user's
CUSTOM rings from the settings, each `{name, positions, letters}`. The
positions signature resolves the LAYOUT (`RING_LAYOUTS`: flame /
chalice / seal — the ring face with matching gaps and the metal
triangle). Validation is loud: an unknown position set, an unknown
glyph, a count mismatch or a duplicate name raises with the offending
entry named.

**THE ROSE IS NOT A RING (owner correction 2026-07-27).** Session 20
shipped a `{"name": "Rose", "rose": true}` card here that painted 24
computed rays into the ring band. It should never have existed: the
owner had specified a POINTER, and [The Cube Canon](../CUBE.md) had
mis-transcribed that as a ring preset and stamped it SEALED, so the
implementing session built the wrong thing faithfully. The card, the
`rose` branch in `validate_preset`, the `RingSpec.rose` flag, the
computed per-ray legend and `RingLayer._draw_rose` are all DELETED —
no compatibility shim (Rule #6). The Rose lives as the seventh
POINTER; see [The Cube Canon](../CUBE.md) §The Rose of the
Twenty-Four.

**RENAMES (TASK 2, MASON/ICONS round, owner verdicts 2026-07-19, third
batch; DOLLAR/EYE round, owner decree 2026-07-27; CROSS-WORDS round,
owner UV inbox + PILOT pick 2026-07-27):** the bundled cards were
"MORPH", "NUMBERS" and "MASON G" — first renamed to "Morph", "Omega"
and "Mason"; then (DOLLAR/EYE round) "Mason" → **"Dollar"** and
"Omega" → **"The One"**, both back onto the banknote itself (the note
and its denomination — CANON.md §The Banknote: "the denomination is
THE ONE"); then (CROSS-WORDS round) "Morph" → **"PILOT"** with NEW
letters **L/Π/Ω/Θ** — Π-I-L-Ω-Θ spells the guide who carries the
traveler home, and each letter initials its own light station (DOMY
stays DOMY). `app.settings_store` migrates an older settings file's
stored name from ANY generation onto the current one via
`_LEGACY_RING_NAMES`. New bundled preset **Templar**: the seal layout, all
six positions wearing the templar-cross glyph (`✠`,
`constants.RING_LETTER_FILES`), no motto, no legend — its own
`triangle` override (see below) is the SAME `[12, 20, 4]`
Trinity/Union split Dollar and The One now both carry too.

**Dollar (ROADMAP 15b, CANON.md §The Banknote):** the owner's earlier
`InGodWeTrust_UVS_BIG.png` hexagram, upgraded onto the seal layout —
positions `12 16 20 24 4 8` wear letters `👁 S M Ω N A`.

**THE EYE AT THE APEX (DOLLAR/EYE round, owner decree 2026-07-27):**
the 12h seat wears the EYE OF PROVIDENCE instead of the letter G. The
adaptive glyph `👁` (`constants.RING_EYE_GLYPH`) maps to the canonical
`Eye.png` stem, which `config.paths.art_file` resolves to the active
art source's `Eye_gem.png`/`Eye_gpt.png` on disk (the same `_gem`/
`_gpt` convention every sourced area uses — the four masters live
beside the letters, a documented exception to the "furniture is
suffixless" rule, `tests/test_assets_structure.py`). The per-preset
**Shine** toggle (`Settings.ring_eye_shine`,
`constants.RING_EYE_SHINE_DEFAULT` — Dollar default ON, the banknote's
own eye radiates) swaps the whole stem for the glory-of-rays master
`Eye_shine.png` in `app.controller.build_skin`
(`_ring_eye_shine`, the same resolution shape as the Two-metals
toggle); the checkbox sits on the Design ▸ Ring tab beside Two metals
and only shows when the active card seats the adaptive glyph. The
CUSTOM builder instead offers the four EXPLICIT variants in its
Symbols group (owner: "any of the four") — `👁 ChatGPT`,
`👁 ChatGPT ☀`, `👁 Gemini`, `👁 Gemini ☀` — with source and rays
baked into the chosen glyph, untouched by either switch. The Eye runs
the ordinary letter pipeline otherwise: gold master, metal recolor,
shadow stamp, hover legend.

Extra OPTIONAL card fields, wired through `validate_preset` and
`app.controller.build_skin`:

- **`triangle`** — a 3-position override of the seal layout's own
  (empty) metal triangle, so a 6-letter preset can split into two
  3-letter metal groups instead of the seal's own plain one-finish-on-
  all-six. CANON reads the hexagram as TWO triangles — the Trinity
  (12/20/4 = 👁, M, N — the Eye, the Master, the Nazarene) and the
  Union (16/24/8 = S, Ω, A — Sigma, Omega, Alpha) — so the Dollar's
  card sets `"triangle": [12, 20, 4]`, the same rule `_letter_metal`
  already applies to DOMY/Morph's 4-letter triangle, now on a 3+3
  split. Only valid on the seal layout; raises otherwise. **TASK 3
  (MASON/ICONS round):** The One and Templar now carry the SAME
  `triangle` field too — but the override only actually APPLIES when
  the owner's per-preset "Two metals" toggle
  (`Settings.ring_two_metals`, `app.controller._ring_two_metals`) is
  on for that preset; off, the card reads exactly like one with no
  `triangle` at all (one finish on all six). **ENLARGE/THEMATIC round
  (owner 2026-07-27):** the toggle now covers the 4-LETTER layouts too
  — DOMY/PILOT (and custom flame/chalice rings) can switch their
  once-unconditional 3+1 split OFF and dress every letter in the one
  finish. Defaults keep today's look: Dollar on
  (`constants.RING_TWO_METALS_DEFAULT`), other seal presets off,
  flame/chalice presets on (the layout's own nature).
- **`legend`** — position -> `{name, reading}`, the per-letter HOVER
  LEGEND text (what that letter stands for), quoted verbatim from
  CANON's Banknote table. Flows into `SkinDefinition.ring.
  letter_legend` (hour -> entry) and answers in
  [Compositor](../render/compositor.md)'s ring-band hover — THREE
  bundled presets carry one now (CROSS-WORDS round, owner UV inbox
  2026-07-27): the **Dollar** (dual symbolism per letter — the
  Double-Trinity OFFICE and the Cube term: Malignant Accuser /
  Megalomania, Anointed Aegis / Abnegation, Satanic Scourge / Storm,
  Omnific Originator / Obligation, Nazarene Advocate / Numbness, the
  Eye as Judge — replacing the retired Sigma/Alpha/Master readings),
  **DOMY** (the dark-cross stations with initial-matched symbolism:
  Y Ysteria/Fear, Ω Orgē/Anger, D Detestatio/Hate, M Miseria/
  Suffering) and **PILOT** (the light-cross stations: Θ Tharsos/Hope,
  L Latria/Faith, Π Pothos/Love, Ω Ōpheleia/Salvation); The One,
  Templar and every custom ring stay silent there, unchanged. **TASK
  2 (owner "može" 2026-07-19):** each `reading` may carry a SECOND
  `\n\n`-separated paragraph — the AXIS-OPPOSITION line. The Dollar's
  three diameters read office against office: **N(4h)↔S(16h)** the
  Advocate against the Scourge, **A(8h)↔M(20h)** the Aegis against
  the Accuser, **👁(12h)↔Ω(24h)** the Judge against the Creator; the
  cross rings read their spine (12h↔24h) and crossbar instead. Both
  seats of one pair quote the SAME clause, each naming the OTHER
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
  [Layers](../render/layers.md)).

  **THE CROSS-WORDS FORM (owner UV inbox 2026-07-27):** an entry may
  instead carry `{text, center, clockwise}` — ONE station word
  CENTERED on one of the preset's own seats (`center`), letters at
  the mottos' fixed step ([Motto](../core/motto.md)'s
  `centered_word_angles`), `clockwise` picking the reading direction
  by the seat's half (top = true, bottom = false — both read
  left-to-right to a viewer). `center` and `pins` are mutually
  exclusive; a spaced text under `center` fails loudly. DOMY wears
  its dark-cross stations this way (SUFFERING↑12h cw, FEAR@20h ccw,
  ANGER@24h ccw, HATE@4h ccw) and PILOT its light-cross stations
  (HOPE@8h cw, FAITH@12h cw, LOVE@16h cw, SALVATION@24h ccw) — the
  chiasm of the Two Crosses drawn as typography (CANON.md §The
  Banknote, The Cross Rings). Every resolved entry also carries
  `words` — per-word spans plus the SEAT each word answers for
  (WORD-HOVER round, owner 2026-07-27: a centered word its own
  station; a pinned motto word the seat of its one pinned letter —
  ANNUIT→A/8h, COEPTIS→S/16h, NOVUS→N/4h, ORDO→Ω/24h, SECLORUM→M/20h,
  the five words spelling the five letters); `build_skin` turns those
  into angular hover geometry and
  `render.compositor._ring_word_legend_tooltip` answers the hover with
  the seat's legend. The Dollar keeps the pinned Great Seal form:

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
- [Motto](../core/motto.md) — `motto_glyph_angles` and
  `centered_word_angles`, the per-glyph angle solves for the optional
  `motto` card field's pinned and centered entry forms
- Shared JSON loading ([Data (folder)](___data.md))

### Used by
- [Watch Controller](../app/controller.md) — `build_skin` resolves the
  active preset (TASK 3: its own metal-split choice via
  `_ring_two_metals`/`constants.RING_TWO_METALS_DEFAULT`; DOLLAR/EYE
  round: the Eye's shine via `_ring_eye_shine`/`constants.
  RING_EYE_SHINE_DEFAULT`); the Design ▸ Ring tab lists every loaded
  name and carries the per-preset "Two metals" and "Shine" toggles
- [Settings Store](../app/settings_store.md) — validates the chosen
  ring name against the loaded set (migrating a stored old bundled
  name of either rename generation, TASK 2 + DOLLAR/EYE) and the
  per-preset `ring_two_metals` (TASK 3) / `ring_eye_shine`
  (DOLLAR/EYE) dicts

## Functions

- `ring_presets(custom=())`: name → `{positions, letters, layout}` for
  every bundled + custom preset
- `validate_preset(entry)`: the shared card validator (also used for
  the Settings custom-ring builder input)
- `_validate_motto(name, raw, positions)`: the optional `motto` field's
  own validator — unknown letters, out-of-range pin positions and a
  broken angle solve all raise with the preset named (Rule #1)
