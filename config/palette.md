# Palette — The Colour Law

**Script:** [Palette (script)](palette.py)

## Purpose

**Every colour in DOMY Watch lives here, and nothing else does.** One
file, one rule: a colour value exists in exactly one place. No hex
literal, no RGBA tuple and no colour table sits anywhere else in the
program.

### Why it exists (owner verdict, 2026-07-29)

The owner went looking for a colour and found this:

> *"sada tražim boje u defaults.py i vidim katastrofu da popizdi čovjek
> gdje nema nikakvih pravila gdje PRISM ima na jednom mestu primary i
> tertiary na skroz drugom dodeljuje tertiary."*

He was exactly right. `config/defaults.py` held **77 colour-bearing
names spread between line 48 and line 3526**, interleaved with window
sizes, timer intervals and file paths. The PRISM pointer declared its
primary and secondary wheels in one place and its THIRD wheel — the
Council — thirty-six lines further down, inside ANOTHER pointer's
block. The octa pointer was split the same way. Finding a colour meant
grepping; changing one meant hoping nothing else nearby owned it.

The diagnosis behind it is the one that matters:

> *"kada se implementira nova funkcionalnost svakoga bole kurac kako je
> to prethodno i ne prati nikakvu strukturu nego samo nabaci novu
> promenljivu samo nabaci novu funkciju na kraj dokumenta."*

A structure nobody enforces lasts exactly one session. So the law is
not only written down here — it is **executable**, in
[Tests (folder)](../tests/___tests.md)'s `test_palette_law.py`.

## The order IS the law

Nine sections, fixed. A new colour joins the section it belongs to;
**nothing is ever appended to the end of the file.**

| § | Section | Holds |
|---|---------|-------|
| 1 | THE NAMED HUES | hues the canon names (`MOON_GRAY_VIOLET`), referenced by the rest |
| 2 | THE POINTER WHEELS | one block per pointer — ALL its wheels together |
| 3 | THE RING | `RING_TINT_GROUPS` |
| 4 | THE DIAL | labels, markers, calendar pointer, glows, eclipses, instrument bands |
| 5 | THE SUBDIAL AND THE SLOTS | roundel borders, small-seconds ticks, plate shadows, recolor targets |
| 6 | THE DEFAULT SKIN's OWN HUES | the ring face, the seven planet bodies, Earth day/night, the Moon's limbs |
| 7 | THE TRAY AND THE FAST-TRAVEL FLASH | the per-watch tint wheel, the flash chip |
| 8 | THE UI CHROME | dialog theme, buttons, legend, encyclopedia finishes, look chips |
| 9 | THE CHARTS | the Report and the Observatory series |

### Section 2 — the one the bug was in

A pointer's wheels **never separate**. Primary, then secondary, then
tertiary, in that order, every time; `PALETTE_PRESETS` at the end of
the section only NAMES them and carries no colour of its own:

```
FOR EACH pointer, in dial order:
    declare its PRIMARY wheel, with the canon's reason for its hues
    declare its SECONDARY wheel
    declare its TERTIARY wheel, if it serves one
THEN, once:
    PALETTE_PRESETS maps (pointer, slot) -> the NAME declared above
    — one contiguous run of entries per pointer, never a literal
```

Each wheel carries the canon name the owner uses for it, so the file is
searchable by the words he thinks in:

| Pointer | primary | secondary | tertiary |
|---------|---------|-----------|----------|
| hexa (PRISM) | `HEXA_PRIMARY` | `HEXA_SECONDARY` | `COUNCIL` |
| trio (TRINITY) | `TRINITY` | `FAMILY` | `GENESIS` |
| cross (QUATERNITY) | `TEMPERAMENTS` | `ELEMENTS` | `SEASONS` |
| octa (COMPASS) | `COMPASS_PAINT` | `COMPASS_LIGHT` | `ROSE_PALETTE` |
| rose | `ROSE_PALETTE` | `ROSE_PALETTE` | — |
| aurora | `AURORA_PAINT` | `AURORA_LIGHT` | — |
| calendar | `CALENDAR_ZODIAC` | `CALENDAR_ALMANAC` | — |

Every tuple runs CLOCKWISE from the 12h arm, matching the drawn
pointer and the dial convention.

## What deliberately stays out

Two kinds of value stay in [Config (folder)](___config.md)'s
`defaults.py`, because they are **not colours**:

- the numeric shaping of a recolor — `SUBDIAL_RECOLOR_VALUE_RAMP` and
  its neighbours (ramps, cutoffs, gains, the cache version tag);
- every width, alpha fraction and radius that merely happens to sit
  beside a hue (`ROSE_ARM_OUTLINE_WIDTH`, `CALENDAR_WEDGE_ALPHA`,
  `RING_TINT_SWATCH_PX`).

A caller that COMPOSES a colour from a value — `f"rgba({c.red()}, …)"`
in the Encyclopedia's card hover — is composing, not declaring, and is
allowed anywhere.

## Connections

### Uses
- [Config (folder)](___config.md) — `constants` only, for the
  per-pointer style roster `effective_palette_style` normalizes against

### Used by
- [Config (folder)](___config.md) — `defaults.DEFAULT_SKIN` reads its
  ring, planet, Earth and Moon hues from §6
- [Render (folder)](../render/___render.md) — every layer, diagram and
  asset variant that paints
- [App (folder)](../app/___app.md) — theme, tray, legend, report,
  observatory, encyclopedia, settings dialog
- [Encyclopedia Tree](encyclopedia_tree.md) — the six wholes' accents
  are `ROSE_PALETTE` hues

## Functions

### `effective_palette_style(pointer, palette_style)`
The wheel slot AS RENDERED for this pointer: `"tertiary"` holds only
where the pointer actually serves a third wheel; everywhere else — a
stored `"tertiary"` left behind by a pointer switch — it normalizes to
`"primary"`. The ONE normalization point, so no consumer ever indexes
`PALETTE_PRESETS` with a pair that does not exist.

### `pointer_arm_labels(pointer, palette_style)`
The palette-editor arm labels for the ACTIVE wheel — the Genesis wheel
(trio + tertiary) speaks its inverted seats, every other wheel its
pointer's own row.

## Design Decisions

- **The law is executable, not advisory.** `test_palette_law.py` pins
  four clauses: no colour literal outside this file; `PALETTE_PRESETS`
  names wheels and spells out none; every pointer's entries form one
  contiguous run; the table and the pointer roster agree. Run against
  the pre-2026-07-29 `defaults.py` the guard reports 251 literals over
  lines 346–3554 and names both split pointers (`hexa`, `octa`).
- **The move was proven value-identical.** Every one of the 66
  colour-bearing names (plus the whole `DEFAULT_SKIN` tree) was
  snapshotted before and after: zero differences. The wheels were not
  retyped — the segments were cut out of `defaults.py` verbatim, so no
  owner-sealed hue could drift while the file was being ordered.
- **The wheels lost their private names** (`_COUNCIL`, `_TRINITY`,
  `_CROSS_ELEMENTS` …). A wheel the canon NAMES is a public constant —
  the owner asks for "the Council", so the file answers to `COUNCIL`.
  No alias was left behind (Rule #6).
- **A local variable is never called `palette` any more.** The module
  is the palette; a pointer wheel's hue tuple is a WHEEL. The three
  files that shadowed the module now say `aura_hues` / `wheel_hues`,
  which is also what they actually hold.
