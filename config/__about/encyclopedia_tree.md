# Encyclopedia Tree

**Script:** [Encyclopedia Tree (script)](../encyclopedia_tree.py) · **Flow:** [diagram](../__flow/encyclopedia_tree.md)

## Purpose

The ONE table of the Encyclopedia's three levels — nine wholes, their
theme cards, the variant loops and the accent hues. Written for the
Session 27 rework (owner-sealed 2026-07-28), which replaced the old
two-screen browser (one gallery of 39 tiles in five halls → article
slider) with Home → Themes → Article; regrouped from six wholes to
nine by Session 35 (2026-07-29, "može i 9 grupacija sa ovim novim
velikim sekcijama" — `WORKPLAN-STRUCTURE.md` §THE NINE WHOLES).

Nothing else declares a whole, a membership or an accent: the home
screen, the theme grid, the breadcrumb, the article header and the
structure tests all read this module.

Layer: config — pure, no Qt, no wall clock.

## Contents

- `Whole` — one Home card: `key`, `title`, `accent` (a hex colour),
  `themes` (its theme-card keys).
- `WHOLES` — the nine, in Home reading order: `instrument`, `sky`,
  `cosmos`, `gods`, `faith`, `cube`, `inner`, `living`, `worlds`.
- `THEME_TO_WHOLE`, `WHOLE_BY_KEY` — derived reverse lookups.
- `ROSE_ACCENTS_USED` — the nine accent hues, one per whole.
- `VARIANT_SOURCES` — merged-card definitions: new topic key → (card
  title, ((switcher label, source topic key), ...)) — `eclipses`,
  `creeds`, `bible`, `wow`, `cyberpunk`, `starwars`.
- `GOD_VARIANT_LABELS` — the four merged god themes' shared switcher
  labels (`Planetary`, `Pantheon`, `Wider Court`).
- `CUBE_TOPICS` — the 42-page Cube run split into four cards
  (`cube_doctrine`, `cube_axes`, `cube_figures`, `cube_projections`) as
  half-open slices.
- `TOPIC_ALIASES` — derived: dial THEME key → (topic key, variant
  index), the ONE table every Spacebar jump and menu shortcut resolves
  through.
- `PLATELESS_PAGES` — deliberately empty (owner verdict 2026-07-29: the
  law "every article carries an image" now has zero exceptions —
  computed diagrams cover what generated art cannot).
- `cube_target(flat_index)`, `whole_of(topic)`, `accent_of(topic)`,
  `all_topics()`.

## Connections

### Uses
- [Palette](palette.md) — `ROSE_PALETTE`, the sealed eight hues eight
  of the nine accents draw from (Rule #5, one palette); the ninth is
  `MOON_SILVER`, the Moon's own dial hue
- [Defaults](defaults.md) — imported alongside `palette` (unused
  directly by this module today, kept for the pair's historical import
  shape)

### Used by
- [App (folder)](../../app/___app.md) — the Encyclopedia package
  builds all three screens from this table
- [Taxonomy](taxonomy.md) — the asset/settings hierarchy this tree
  mirrors on the reading side (independently curated, same themes)

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
night for the far sky, midnight for the sacred, the vesper hour for
the written faiths, the Cube's own axis blue for the Cube, sunset's
fire for the inner wheel, spring green for the living world, the
working afternoon for the worlds people build. All eight Rose hues are
spent — orange (`worlds`) and rose (`faith`) were the two the
six-whole table left idle — plus the ninth, the Moon's silver (`sky`).

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
and Moods stay three cards (opposites, not dresses). A FRANCHISE with
several casts is the merged case, not the split one: its blocks are
one week read several times over, so every one of their nine casts is
still a theme of its own on the DIAL, which is what `TOPIC_ALIASES`
(derived from this table) exists to reconcile.

## Jump resolution

Two kinds of address arrive from the dial and must land on a real
page:

- **A dial theme key** — `TOPIC_ALIASES` maps it to (topic, variant):
  `bible_dark → ("bible", 2)`, `religion_alt → ("creeds", 1)`,
  `planet_signs → ("planets", 0)`.
- **An old flat Cube index** — `cube_target(flat)` maps it to (topic,
  local page) across the four Cube cards, so [Archetypes](archetypes.md)'
  wheel table keeps addressing `("cube", 35)` unchanged.

## Design Decisions

- **A variant is a contiguous run of pages, never a re-ordering.** The
  merged topics build their source blocks exactly as before and record
  the boundaries; nothing about an existing page changes when it joins
  a loop.
- **Identity aliases are kept** (`bible → ("bible", 0)`) so the
  resolver has one path and no special case.
- **`cube_target` clamps instead of raising.** Its caller is the dial:
  a stale wheel target must not take the window down.
- **THE REACHABILITY LAW.** Born from the owner's exact 2026-07-29
  complaint: twelve casts had been registered on the dial
  (`constants.WEEKDAY_THEMES`) with full text and art, and still had no
  seat anywhere in the Encyclopedia. Every registered dial theme,
  except the documented look-only keys, must resolve through
  `THEME_TO_WHOLE` or `TOPIC_ALIASES` to a topic seated in a whole —
  pinned by `tests/test_encyclopedia_tree.py`. It is deliberately the
  REACHABILITY half of a pair: `test_theme_completeness.py` owns
  REGISTRATION (art on disk ↔ a `WEEKDAY_THEMES` key ↔ the staging
  ledger); this law owns the seat on Home.
