# The Dial — conventions, architecture and vocabulary

The facts a session must never re-derive. Sibling docs:
[Decisions](DECISIONS.md) · [Art Pipeline](ART-PIPELINE.md) ·
[Enforcement](ENFORCEMENT.md) · [Runtime Notes](RUNTIME-NOTES.md)

## Dial convention

Degrees CLOCKWISE from TOP; 12:00 noon top, 00:00 midnight bottom, 18:00
right, 06:00 left; `DIAL_OFFSET_DEG = 180`. Hour hand = 1 rev/24 h, minute
hand = 1 rev/h, NO seconds hand.

**Hexagram:** the top vertex ALWAYS points at true solar noon; rotation
`(noon_secs − 43200)/240` degrees, positive = clockwise (west-in-zone/DST).
Weekday diamond slots ROTATE WITH the hexagram.

**Year wheel:** piecewise-linear between the six season anchors from
`shared/Database/seasons_utc.json` — every season spans exactly 90° even
though real durations differ (owner spec); equinoxes exactly at 90°/270°.

## Architecture

One-way flow: `config → core (pure, no Qt, no wall clock) → data → skins →
render → app`. Purity is enforced by `desktop/tests/test_purity.py`
(AST-based; covers `core`, `data`, `recolor`).

**Render structure (since 0.14.688):** `render/context.py` is the layer
protocol, the geometry/painting modules beside it are the shared vocabulary,
`render/layers/` holds one module per paint layer, and
`render/compositor.py` stacks them. `render/layers.py` no longer exists —
never import from it.

<a id="ring-vocabulary"></a>

## THE RING VOCABULARY (owner 2026-08-07 — "JEWELS != NUMERALS", learn it once)

The ring band carries FOUR different things and they are not variations of
each other. Never reason about one as though it were another.

| Term | What it is | How many | How it is drawn |
|------|-----------|----------|-----------------|
| **JEWELS** | the letters/glyphs seated on the outer's EMPTY fields | depends on the OUTER mode: full 1, the crosses 4, hexa 6, octa 8 | PLATES |
| **NUMERALS** | the hour numbers 1–23 filling every seat no jewel took | the rest of the 24 | COMPUTED, and **even/odd wear two different styles** — even is white on a grey border, odd the reverse (`palette.NUMERAL_PARITY_COLORS`). That alternation is the DESIGN, not a defect |
| **MINUTES** | the inner band's five-minute numbers | per inner variant | COMPUTED, its own face roster |
| **CROWN** | everything outside the band — its text, the location, the live time | per preset | PLATES |

<a id="one-plate-law"></a>

## THE ONE PLATE LAW (decree 2026-08-07)

Everything drawn from the PLATE library — the jewels, the whole crown, the
duals — is one of the owner's plates in `shared/assets/instrument/letters/`
(latin, greek, numerals, symbols, emblems), taken as the GOLD master and
recolored by the transformer into one of this app's metals or thematic
colours. One style, one source, one algorithm: never a font, never a flat
colour of its own.

The NUMERALS and MINUTES bands above are the other half of the vocabulary —
computed, with their own face rosters, relief and the even/odd parity. They
are not exceptions to this law; they are a different thing.

`render.letter_plates` is the single door: Greek twins alias onto the Latin
plate, two-digit numbers compose from the digit plates at a uniform INK
clearance, and a glyph with no plate RAISES rather than falling back —
because that fallback is how a whole missing digit alphabet once shipped as
a font-drawn crown with every test green. Tooth:
`desktop/tests/test_letter_plates.py`.

<a id="one-copy-rule"></a>

## THE ONE COPY RULE (owner 2026-07-28, extended 2026-08-06)

The only things that may differ between two watches are the OBSERVER
(location/timezone) and the VISUAL picks. Every bundled book and database is
loaded ONCE per process — `render.assets.shared_cache`,
`data.symbolism.shared_symbolism` / `data.encyclopedia.shared_encyclopedia`
(one per LANGUAGE), `shared_seasons`, `shared_moon_phases`,
`shared_deep_time`, `shared_observatory`, and the memoized bundled halves of
`ring_presets()` / `hand_packs()`. Never construct those repository classes
directly in app code.

## Where the doctrine lives

The seating doctrine — the colour–virtue–vice–mood web, the two rosters,
duals, ninths, pointer archetypes — is [The DOMY Canon](../CANON.md); read it
BEFORE any theme, roster or article work. The philosophical core (the
three-axis Character Cube, the Double Trinity, the Two Crosses, the Rose,
naming and the writing laws) is [The Cube Canon](../CUBE.md); read it BEFORE
any character, path, archetype-wheel or naming work.
