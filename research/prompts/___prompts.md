# prompts/

The image-generation prompt sheets — the owner generates art from
these, one theme at a time, top to bottom. Since the roster doctrine
closed (2026-07-15), **each weekday theme owns ONE complete file**:
every plate the theme needs across BOTH rosters (Planetary +
Pantheon), in every register the theme ships (bronze + colored),
including the Sunday dual and the Ninth — with **REUSE** notes where
an existing plate serves a new seat (nothing to generate) and
**SUPERSEDED / DO NOT GENERATE** notes for everything the doctrine
retired (the old Hades/Baldur/Set/Crnobog/Jester/Legion ninths).
Check the root [Roster](../../ROSTER.md) for what is already on disk
per source.

## Before writing a NEW sheet

Read [How to Write a Prompt Sheet](../../../PromptPainter/instructions.md)
first — PromptPainter's own sheet contract, owned and enforced by its
parser (`painter/sheet_parser.py`), also behind the GUI's own
**Instructions** button. Every image needs a
`**Title** → \`path.png\`` line right in its own entry; skip it and
the tool silently drops that image with ZERO warning — no error, no
log, nothing (`intelligences_prompts.md` shipped with only 1 of 11
entries loading until caught 2026-07-17). Verify any sheet before
handing it to the owner:

```bash
python main.py "path/to/your_sheet.md" --dry-run
```

run from `Gadgets/PromptPainter/` — zero problems and the expected
item count means the sheet is safe to queue.

## Files

### `weekday/` — one complete sheet per theme
- `greek_prompts.md` — Planetary + Pantheon (Zeus/Hades dual, Gaia
  ninth), bronze + colored
- `norse_prompts.md` — Planetary + Pantheon (the Wanderer dual,
  Yggdrasil ninth), bronze + colored
- `egypt_prompts.md` — Planetary + Pantheon (Isis, Horus, Anubis,
  Bastet, the Pharaoh ninth), bronze + tomb-fresco colored
- `slavic_prompts.md` — Planetary + Pantheon (Perun/Veles dual,
  Svarog, Lada, Triglav ninth), bronze + folk-icon colored
- `religion_prompts.md` — the reworked CREEDS (Christianity
  enthroned, the Satanism dual, the Freemasonry ninth)
- `religion_alt_prompts.md` — ANCIENT RELIGIONS (Eleusis seated, the
  Unknown God ninth)
- `profession_prompts.md` — bronze + colored + the Polymath ninth
- `bible_theme_prompts.md` — Bible (the Holy Trinity ninth)
- `bible2_prompts.md` — Bible II (the Isaac dual, the Melchizedek
  ninth)
- `bible_dark_prompts.md` — the dark set (the Lucifer/Judas dual, the
  Ninth Circle ninth)
- `wolf_pack_prompts.md`, `bee_hive_prompts.md`,
  `elephant_herd_prompts.md` — the animal societies (complete:
  bronze + colored + their Union ninths; wolves need NO new art —
  the ranks land as display names)
- `cosmos_prompts.md` — Cosmos (bronze + colored + the Big Bang
  ninth)
- `planet_art_prompts.md` — the Planets ART medallion look (bronze
  only, the seven bodies + the Sun-eclipse dual)
- `alchemy_metal_prompts.md` (the raw-ore dual, the Philosopher's
  Stone ninth), `japan_prompts.md` (the Ama-no-Iwato dual),
  `planet_signs_prompts.md` (its Eclipsed Sun dual) — the closed
  sets, each complete in its own file
- `planets_prompts.md` — the real-photo Planets theme (owner's own
  photographs, no prompts needed) + its Eclipsed Sun dual; pointers to
  its ART-medallion sibling, `planet_art_prompts.md`, and to
  `planet_signs_prompts.md`

### `zodiac/`
- `chinese_zodiac_prompts.md` — bronze + colored (12 animals), the
  excluded Cat thirteenth (Encyclopedia-only, no dial seat)
- `astrology_prompts.md` — sign + logo + constellation + colored (12
  signs), the excluded Ophiuchus thirteenth (Encyclopedia-only, no
  dial seat)

### `badge/`
- `scale_badge_prompts.md` — the Judas–Lucifer Scale, BOTH
  registers: metal cameo triptych + the stained-glass windows
  (owner masters 2026-07-15) with the rose-window UNION
- `season_trinity_prompts.md` — Trinity, Seasons, Turning Points,
  Meteorological twins

### `era/`
- `era_prompts.md` — the ERA TERMS Encyclopedia set (ROADMAP 15a3):
  the Age of Light and Age of Darkness, plus the four Starry Seasons
  inside them (spring/summer of the light era, autumn/winter of the
  dark era) — one rose-window emblem each, night-window register; the
  comparative "Eras of the World" article carries no emblem

### `emblem/` — one file per wheel theme
- `virtue_prompts.md` — the eight Virtues (Humility dual)
- `sin_prompts.md` — the eight Sins (Servility dual)
- `mood_prompts.md` — the eight Moods (Awe dual, the Ninth Mood /
  Eclipse ninth)
- `intelligences_prompts.md` — the nine intelligences (Encyclopedia
  set, not a weekday theme)

### `instrument/`
- `instrument_prompts.md` — the Instrument reader art
- `subdial_circle_prompts.md` — the subdial plates (the silver
  master ships; gold/bronze recolor at runtime)

### `archetype/` — one file per pointer archetype (all seven + the Calendar, complete 2026-07-16)
- `trinity_prompts.md` — the courtroom trio (Jesus the Advocate /
  the Devil the Prosecutor / The One the Judge) + the all-seeing
  Eye rosette as the union of the three at the center
- `family_prompts.md` — Trinity light: the Father/Shield, the
  Mother/Heart, the Child/Dawn + the Hearth rosette + role rondels
- `persons_prompts.md` — Prism paint: One/Love, Michael/Courage,
  Devil/Hatred, Jesus/Humility (Lucifer and Judas REUSE the Scale
  glass windows)
- `one_soul_prompts.md` — Prism light: the six pillar windows each
  carrying its shadow, the Union rosette, the Child rondel
- `temperaments_prompts.md` — Seasons: the four temperaments on the
  season colors + the UNAPPROVED optional tetramorph section
- `walks_prompts.md` — Compass paint: the eight estates in their
  material hues + the eight object rondels (Crown … Bell)
- `life_prompts.md` — Compass light: BOTH image registers — the
  Tree (one oak, eight states) and the Menagerie (eight creatures)
- `calendar_prompts.md` — the Calendar pointer: twelve month
  medallions (wedges stay flat color; zodiac art and the Chinese
  animal medallions REUSE)

## Connections

### Uses
- [The Pantheon Catalog](../pantheon_catalog.md) — the locked rosters
  and doctrine every sheet implements
- [Roster](../../ROSTER.md) — per-source coverage (what exists)

### Used by
- The owner's generation sessions (Gemini / ChatGPT)

## Design Decisions
One theme = one file, because the owner generates in order and hunted
across files before (the colored Skoll case). Prompts are copied
byte-identical when they move; border identities are per-theme
constants (meander / knotwork / cartouche / kolovrat…) so a series
stays recognizable; images never carry lettering.
