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
- `bible_theme_prompts.md` — Bible and Bible II (the Holy Trinity
  ninth; Melchizedek relocated to Bible II)
- `bible_dark_prompts.md` — the dark set (the Ninth Circle ninth)
- `wolf_pack_prompts.md`, `bee_hive_prompts.md`,
  `elephant_herd_prompts.md` — the animal societies (complete:
  bronze + colored + their Union ninths; wolves need NO new art —
  the ranks land as display names)
- `cosmos_prompts.md` — Cosmos (bronze + colored + the Big Bang
  ninth) AND the Planets ART medallion look
- `alchemy_metal_prompts.md`, `japan_prompts.md`,
  `planet_signs_prompts.md`, `bible_theme_prompts.md` — the closed
  sets, unchanged
- `colored_badge_prompts.md` — the remaining shared colored sets
  (zodiac astrology/chinese); the god-theme colored sections have
  MOVED into their theme files (a lookup note inside points where)
- `sunday_duality.md`, `egypt_prompts.md` companions — historical
  delivery notes; the theme files are authoritative

### `badge/`
- `scale_badge_prompts.md` — the Judas–Lucifer Scale triptych
- `season_trinity_prompts.md` — Trinity, Seasons, Turning Points,
  Meteorological twins

### `emblem/`
- `virtue_sin_mood_prompts.md` — the three wheels
- `intelligences_prompts.md` — the nine intelligences

### `instrument/`
- `instrument_prompts.md` — the Instrument reader art
- `subdial_circle_prompts.md` — the subdial plates (the silver
  master ships; gold/bronze recolor at runtime)

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
