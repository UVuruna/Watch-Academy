# Palette — The Colour Law

**Script:** [Palette (script)](../palette.py) · **Flow:** [diagram](../__flow/palette.md)

## Purpose

**Every colour in DOMY Watch lives here, and nothing else does.** One
file, one rule: a colour value exists in exactly one place. No hex
literal, no RGBA tuple and no colour table sits anywhere else in the
program — `tests/test_palette_law.py` fails the build if one appears.

### Why it exists (owner verdict, 2026-07-29)

Before this file, `config/defaults.py` held 77 colour-bearing names
spread between line 48 and line 3526, interleaved with window sizes,
timer intervals and file paths. The PRISM pointer declared its
primary and secondary wheels in one place and its THIRD wheel — the
Council — thirty-six lines further down, inside ANOTHER pointer's
block. Finding a colour meant grepping; changing one meant hoping
nothing else nearby owned it. The law is not only written down — it
is executable, in `tests/test_palette_law.py`.

Layer: config — pure, no Qt, no wall clock.

## The order IS the law

Nine sections, fixed. A new colour joins the section it belongs to;
**nothing is ever appended to the end of the file.**

| § | Section | Holds |
|---|---------|-------|
| 1 | THE NAMED HUES | hues the canon names (`MOON_GRAY_VIOLET`, `MOON_SILVER`), referenced by the rest |
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
the section only NAMES them and carries no colour of its own.

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

Two kinds of value stay in [Defaults](defaults.md), because they are
NOT colours: the numeric shaping of a recolor
(`SUBDIAL_RECOLOR_VALUE_RAMP` and its neighbours — ramps, cutoffs,
gains, the cache version tag), and every width, alpha fraction and
radius that merely happens to sit beside a hue (`ARM_OUTLINE_WIDTH` —
the lead line's width, whose colour `ARM_OUTLINE` lives here). A
caller that COMPOSES a colour from a value (`f"rgba({c.red()}, …)"`)
is composing, not declaring, and is allowed anywhere.

## Connections

### Uses
- [Config (folder)](../___config.md) — `constants` only, for the
  per-pointer style roster `effective_palette_style` normalizes
  against

### Used by
- [Defaults](defaults.md) — `DEFAULT_SKIN` reads its ring, planet,
  Earth and Moon hues from §6
- [Render (folder)](../../render/___render.md) — every layer, diagram
  and asset variant that paints
- [App (folder)](../../app/___app.md) — theme, tray, legend, report,
  observatory, encyclopedia, settings dialog
- [Encyclopedia Tree](encyclopedia_tree.md) — the nine wholes' accents:
  eight `ROSE_PALETTE` hues plus the ninth, `MOON_SILVER`
- [Character Cube](cube.md) — `ROSE_POLE_HUE` indexes into
  `ROSE_PALETTE`

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
  contiguous run; the table and the pointer roster agree.
- **The move was proven value-identical.** Every colour-bearing name
  (plus the whole `DEFAULT_SKIN` tree) was snapshotted before and
  after the split: zero differences.
- **A local variable is never called `palette` any more.** The module
  IS the palette; a pointer wheel's hue tuple is a WHEEL.
