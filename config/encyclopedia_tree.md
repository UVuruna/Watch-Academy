# Encyclopedia Tree

**Script:** [Encyclopedia Tree (script)](encyclopedia_tree.py)

## Purpose

The ONE table of the Encyclopedia's three levels — nine wholes, their
theme cards, the variant loops and the accent hues. Written for the
Session 27 rework (owner-sealed 2026-07-28), which replaced the old
two-screen browser (one gallery of 39 tiles in five halls → article
slider) with Home → Themes → Article; regrouped from six wholes to nine
by Session 35 (2026-07-29, "može i 9 grupacija sa ovim novim velikim
sekcijama" — WORKPLAN-STRUCTURE.md §THE NINE WHOLES).

Nothing else declares a whole, a membership or an accent: the home
screen, the theme grid, the breadcrumb, the article header and the
structure tests all read this module.

## Connections

### Uses
- [Defaults](defaults.md) — `ROSE_PALETTE`, the sealed eight hues eight
  of the nine accents are drawn from (Rule #5, one palette); the ninth
  is `MOON_SILVER`, the Moon's own dial hue

### Used by
- [Encyclopedia (subfolder)](../app/encyclopedia/___encyclopedia.md) —
  builds all three screens from this table
- [Taxonomy](taxonomy.md) — the asset/settings hierarchy this tree
  mirrors on the reading side

## The three levels

```
Home  ──►  Themes  ──►  Article
9 cards    4–7 cards    pages + ◀ variant ▶
no scroll  Y scroll      Y scroll
```

## The nine wholes

| Whole | Accent (Rose hour) | Cards | Pages |
|---|---|---|---|
| The Instrument | yellow, 12h | 5 | 38 + guide |
| The Sky | Moon's silver | 4 | 27 |
| The Cosmos | cyan, 03h | 6 | 74 |
| The Gods | moon-violet, 24h | 5 | 118 |
| The Faith | rose, 21h | 4 | 61 |
| The Character Cube | blue, 06h | 7 | 70 |
| The Inner Wheel | red, 18h | 4 | 36 |
| The Living World | green, 09h | 5 | 54 |
| The Worlds | orange, 15h | 5 | 121 |

The accent is argued by the hour it stands on, never picked by taste:
noon for the instrument, the Moon's own face for the near sky, deep
night for the far sky, midnight for the sacred, the vesper hour for the
written faiths, the Cube's own axis blue for the Cube, sunset's fire for
the inner wheel, spring green for the living world, the working
afternoon for the worlds people build. All eight Rose hues are spent —
orange (15h, `worlds`) and rose (21h, `faith`) were the two the six-whole
table left idle — plus the ninth, the Moon's silver (`sky`).

### How the six became nine (Session 35, 2026-07-29)

`instrument`, `cube` and `living` never moved — same key, same seat,
same membership. The other three split:

- **`celestial` → `sky` + `cosmos`.** The near sky (Sun, Moon, seasons,
  eclipses — the two lights and what they do together) stayed close to
  home; the far sky (planets, the cosmos theme, continents, astrology,
  the Chinese court) took the deep-night cyan the old whole wore.
  `celestial` had grown to 10 cards over completion wave I's addition
  of the Chinese court (Session 31) — the split is also what dissolves
  that overflow.
- **`divine` → `gods` + (its Bible/Creeds pair into `faith`).** The four
  pantheons and the age of heroes keep the sacred midnight hue as
  `gods`; the two WRITTEN faiths join Trinity and Duality (pulled out of
  `human`) in the new `faith`, seated on the vesper-hour rose the
  six-whole table left unspent.
- **`human` → `inner` + `worlds`.** The four emblem families (virtues,
  sins, moods, intelligences) alone become `inner`, keeping the sunset
  red. The trades, the Corporation and all three FRANCHISE cards — `wow`
  (Session 32), `cyberpunk` (Session 32) and `starwars` (Session 33),
  each a merged three-register card, never three cards — become
  `worlds`, seated on the Merchant's copper orange. `human` had reached
  11 cards carrying two named, expiring carve-outs in
  `tests/test_settings_dialog.py`; this split is those carve-outs'
  designed death — DELETED once the new seating passed without them.

No card lost an article, a variant or its dial wiring in the move —
`TOPIC_ALIASES`, `VARIANT_SOURCES` and every theme's own build are
untouched; only the SEAT on Home changed (RESEAT, never re-wire).

## The variant law

Owner decision, 2026-07-28: **registers of one subject merge into one
card and become members of the switcher loop; distinct subjects stay
their own cards.**

| Card | Variants in the loop |
|---|---|
| Greek / Norse / Egyptian / Slavic | Planetary · Pantheon · Wider Court |
| Bible | Bible · Bible II · Bible Dark |
| Creeds | Creeds · Ancient religions |
| Eclipses | Solar · Lunar |
| World of Warcraft | Alliance · Horde · Evil |
| Cyberpunk 2077 | Gangs · Street · Power |
| Star Wars | Jedi · Sith · Dyad |

Wolf, Bee and Elephant stay three cards (three animals). Virtues, Sins
and Moods stay three cards (opposites, not dresses). Astrology and the
Chinese zodiac stay two cards (two systems). A FRANCHISE with several
casts is the merged case, not the split one: its blocks are one week
read several times over, so World of Warcraft, Cyberpunk 2077 and Star
Wars are one card each — and every one of their nine casts is still a
theme of its own on the DIAL, which is what `TOPIC_ALIASES` (derived
from this table) exists to reconcile. Star Wars is also where the merge
does the most work for the reader: three of its figures are seated in
two blocks at different ages, and the switcher is how one walks from
one age of a person straight to the other.

Pseudocode of the switcher:

```
ON variant switch (direction d):
    offset ← current page − start of current variant
    next   ← (current variant + d) MOD variant count
    page   ← start of next + MIN(offset, length of next − 1)
```

The offset is what the owner asked to be remembered — Monday stays
Monday when the roster changes, and a shorter variant (the Wider Court
has 4 pages against Planetary's 11) clamps to its own last page instead
of overrunning.

## Jump resolution

Two kinds of address arrive from the dial and must land on a real page:

- **A dial theme key** — `TOPIC_ALIASES` maps it to (topic, variant):
  `bible_dark → ("bible", 2)`, `religion_alt → ("creeds", 1)`,
  `planet_signs → ("planets", 0)`.
- **An old flat Cube index** — `cube_target(flat)` maps it to (topic,
  local page) across the four Cube cards, so
  [Archetypes](archetypes.md)' wheel table keeps addressing
  `("cube", 35)` unchanged. This is why the entry ORDER of
  `_CUBE_ENTRIES` remains a contract.

## Design Decisions

- **A variant is a contiguous run of pages, never a re-ordering.** The
  merged topics build their source blocks exactly as before and record
  the boundaries; nothing about an existing page changes when it joins
  a loop.
- **Identity aliases are kept** (`bible → ("bible", 0)`) so the
  resolver has one path and no special case.
- **`cube_target` clamps instead of raising.** Its caller is the dial:
  a stale wheel target must not take the window down.
- **The Cube split follows the boundaries the entry table already
  documents** (doctrine / axes with poles and cells / vertex figures /
  projections), not a mechanical quarter-cut.
- **THE REACHABILITY LAW (Session 35, pinned by
  `tests/test_encyclopedia_tree.py::test_every_dial_theme_is_
  reachable_from_home`).** Born from the owner's exact 2026-07-29
  complaint: twelve casts had been registered on the dial
  (`constants.WEEKDAY_THEMES`) with full text and art, and still had no
  seat anywhere in the Encyclopedia. This law closes that gap for good —
  every registered dial theme, except the documented LOOK-ONLY keys
  (`tests/test_theme_completeness.py`'s own exception set, reused
  verbatim, Rule #5 — `planets_art` is the one member today), must
  resolve through `THEME_TO_WHOLE` or `TOPIC_ALIASES` to a topic seated
  in a whole. It is deliberately the REACHABILITY half of a pair:
  `test_theme_completeness.py` owns REGISTRATION (art on disk ↔ a
  `WEEKDAY_THEMES` key ↔ the staging ledger); this law owns the seat on
  Home. A theme can be fully registered and worded and still fail this
  law if nobody added it to a whole's `themes` tuple — which is exactly
  what happened to the twelve casts before this session.
