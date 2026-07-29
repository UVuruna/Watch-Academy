# Encyclopedia Tree

**Script:** [Encyclopedia Tree (script)](encyclopedia_tree.py)

## Purpose

The ONE table of the Encyclopedia's three levels — six wholes, their
theme cards, the variant loops and the accent hues. Written for the
Session 27 rework (owner-sealed 2026-07-28), which replaced the old
two-screen browser (one gallery of 39 tiles in five halls → article
slider) with Home → Themes → Article.

Nothing else declares a whole, a membership or an accent: the home
screen, the theme grid, the breadcrumb, the article header and the
structure tests all read this module.

## Connections

### Uses
- [Defaults](defaults.md) — `ROSE_PALETTE`, the sealed eight hues the
  six accents are drawn from (Rule #5, one palette)

### Used by
- [Encyclopedia (subfolder)](../app/encyclopedia/___encyclopedia.md) —
  builds all three screens from this table
- [Taxonomy](taxonomy.md) — the asset/settings hierarchy this tree
  mirrors on the reading side

## The three levels

```
Home  ──►  Themes  ──►  Article
6 cards    5–10 cards    pages + ◀ variant ▶
no scroll  Y scroll      Y scroll
```

## The six wholes

| Whole | Accent (Rose hour) | Cards | Pages |
|---|---|---|---|
| The Instrument | yellow, 12h | 5 | 38 + guide |
| The Celestial Engine | cyan, 03h | 10 | 101 |
| The Divine | purple, 24h | 7 | 173 |
| The Human Wheel | red, 18h | 10 | 130 |
| The Character Cube | blue, 06h | 7 | 70 |
| The Living World | green, 09h | 5 | 54 |

The accent is argued by the hour it stands on, never picked by taste:
noon for the instrument, deep night for the sky, midnight for the
sacred, sunset's fire for the human wheel, the Cube's own axis blue for
the Cube, spring green for the living world.

**Completion wave I (Session 31, 2026-07-29)** added three cards, each
its own card rather than a switcher member — three distinct subjects,
not three registers of one subject (the variant law below): Chinese
Mythology into The Celestial Engine, Greek Monsters into The Divine
beside the Greek gods, and The Corporation into The Human Wheel beside
the Professions. The Celestial Engine is one card over the comfort cap
`tests/test_settings_dialog.py` keeps (9 = three full rows); that whole
is the one the nine-whole structural arc splits into `sky` and
`cosmos`, and the guard carries a named, expiring carve-out for it
rather than a raised ceiling.

**Completion wave II, WoW half (Session 32, 2026-07-29)** added ONE
card, `wow`, into The Human Wheel beside the Corporation — three casts,
not three cards. Alliance, Horde and Evil hold the SAME nine seats with
the same arm bundles and differ only in who sits there, which is the
variant law's own definition of registers of one subject; the card
carries a three-way switcher and 33 pages. That takes the whole to 9
cards, exactly the comfort cap and no carve-out needed. The nine-whole
structural arc moves this card, the Professions and the Corporation
together into the new `worlds` whole.

**Completion wave II, Cyberpunk half (Session 32, same day)** added the
second franchise card, `cyberpunk`, beside it on the identical
argument — Gangs, Street and Power are Night City read from three
heights on one set of nine seats — with its own three-way switcher
and another 33 pages. This one DOES pass the cap: The Human Wheel now
stands at 10 cards, and the guard carries a second named, expiring
carve-out rather than a raised ceiling, pointing at the same arc, which
dissolves this whole into `inner` and `worlds` and takes both franchise
cards with it.

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

Wolf, Bee and Elephant stay three cards (three animals). Virtues, Sins
and Moods stay three cards (opposites, not dresses). Astrology and the
Chinese zodiac stay two cards (two systems). A FRANCHISE with several
casts is the merged case, not the split one: its blocks are one week
read several times over, so World of Warcraft is one card and Cyberpunk
2077 is one card — and each of their six casts is still a theme of
its own on the DIAL, which is what `TOPIC_ALIASES` (derived from this
table) exists to reconcile.

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
