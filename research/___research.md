# research/

One-off analysis scripts, oversized data and OWNER-FACING design
documents (image-prompt sheets, audits, expansion specs) — NOT bundled
with the app, not part of the runtime dependency graph. The GEMINI/CHATGPT PROMPT SHEETS live under
`prompts/<area>/` MIRRORING the assets tree (owner 2026-07-14):
`prompts/weekday/`, `prompts/zodiac/`, `prompts/emblem/`,
`prompts/badge/`, `prompts/instrument/` — new sheets land there.

## Files

### `graph_years.py`
Exploratory plotting of season/year data.

### `efficency.py`
Performance experiments.

### `seasons_large.json` (~11 MB)
Extended variant of `Database/seasons_utc.json` kept for analysis; the app
bundles only the compact file.

### `encyclopedia_expansion.md` — Encyclopedia Expansion
Design + ship-ready copy for the Encyclopedia's second half (owner
task 2026-07-12): "The Instrument" functionality articles (dial, solar
rotation, twilight, year wheel, lunations, palettes, metals, ring
letters), the Virtues/Sins/Moods sections, and the WEEK mode — seven
cross-theme weekday pages with Sunday and Tuesday written in full.

### `prompts/emblem/` — Virtue, Sin and Mood Prompts (one file each)
The three wheel themes split per the one-theme-one-file rule
(2026-07-15): `virtue_prompts.md` (gold cameo, Humility dual),
`sin_prompts.md` (blackened iron, Servility dual), `mood_prompts.md`
(silver sundial, Awe dual + the Ninth Mood / Eclipse ninth); drop
dirs assets/emblem/virtue|sin|mood/.

### `guide_shotlist.md` — Guide Redesign and Shot List
The Guide's 30-chapter redesign plan plus the numbered 37-screenshot
shot list with exact preconditions per shot (owner shoots these).

### `prompts/weekday/bible_theme_prompts.md` — Bible Theme Prompts
The owner-requested 12th weekday theme: both testaments as stained
glass — the day mapping with rationale (Ancient of Days + the Son as
Servant on Sunday, Mary/Moon, David/Mars, Moses/Mercury,
Solomon/Jupiter, Bride and Bridegroom/Venus, Joseph's sheaves/Saturn)
and the 8 Gemini prompts (drop dir assets/weekday/bible/primary/).

### `prompts/weekday/alchemy_metal_prompts.md` — Alchemy Metal Prompts
Redesign of the seven alchemy weekday plates: the shared ingot-pile
center is replaced by one signature object + signature behavior +
explicit finish per metal (mirror/tarnish, forge/rust, liquid beads,
bell, verdigris, plumb bob) so the four gray metals become
distinguishable; 7 Gemini prompts, borders kept.

### `prompts/weekday/wolf_pack_prompts.md` — Wolf Pack Theme Prompts
The owner-approved 13th weekday theme: the pack hierarchy as the week
(Alpha with the Omega servant as Sunday dual — the dial's own M/Ω
ring letters made flesh — Luna, Hunter, Scout, Beta, Mate, Elder),
fourth bronze metal-theme with a paw-print border, 8 bronze + 8
colored Gemini prompts; drop dir assets/weekday/wolf/primary/.

### `prompts/weekday/bee_hive_prompts.md` — Bee Hive Theme Prompts
The 14th weekday theme: the hive's castes as the week (Queen with
the day-one Cleaner as Sunday dual, Nurse, Guard, Scout's waggle
dance, Builder, the Drone on Venus — owner's call — and the dying
Forager on Saturn), honeycomb border echoing the dial's hexagram,
8 bronze + 8 colored prompts; drop dir assets/weekday/bee/primary/.

### `prompts/weekday/elephant_herd_prompts.md` — Elephant Herd Theme Prompts
The 15th weekday theme closing the animal-society trio (pack=rank,
hive=function, herd=MEMORY): Matriarch with the dead matriarch's
bones as the Memory dual, Allomother, Musth, the infrasound Caller,
the bachelor-school Mentor, the Reunion ceremony, the Elder digging
remembered water on her last molars; acacia-and-tusk border, 8
bronze + 8 colored prompts; drop dir assets/weekday/elephant/primary/.

### `prompts/` — the Prompt Sheets (restructured 2026-07-15)
One weekday theme = ONE complete sheet (both rosters, both registers,
duals, ninths, REUSE and DO-NOT-GENERATE marks) — the owner generates
top to bottom without hunting. The folder's own
[index](prompts/___prompts.md) lists every sheet; the per-file
sections below describe the pre-restructure content and remain as
history.

### `merge_articles.py` — Staged-Articles Merger
The article-wave pipeline (2026-07-15): per-theme writer agents stage
JSON files under `research/articles_staging/`, this script validates
the shape (7 bodies, the six variant keys, $ref only for same-seat
reuse), lands the four pantheon article sets and the Religion rework
into `Database/symbolism.json`, the new ninths into
`Database/encyclopedia.json`, and every staged Serbian text into the
sr-Latn bundle (hash-keyed, orphans pruned, audit printed). The
staging folder is deleted after a clean merge — the databases are the
source of truth.

### `build_roster.py` — ROSTER.md Generator
Generates the root [Master Systematics](../ROSTER.md) (owner
2026-07-15): the seat-archetype matrix, every weekday theme's seven
figures + dual + ninth, zodiac/chinese/badge/emblem inventories, and
per-SOURCE (Gemini/ChatGPT) art coverage with a shortage list — the
one place to check what is missing. Regenerate after any theme-table
change or art drop; keep its NINTHS table in sync with
`app/encyclopedia.py`.

### `bond_theme.md` — The Bond (relationship pillars theme draft)
The owner's man-and-woman pillars (prompt.txt notes, 2026-07-16)
seated on the wheel through the CONJUGATION LAW — every pillar is a
seat's virtue conjugated between two persons, every shadow its vice
(Trust/Moon, Support/Mars, Tolerance/Mercury, Gratitude/Jupiter,
Passion/Venus, Respect/Saturn, the Union enthroned with Loyalty and
Closeness as its faces); ninth candidates (the Child / Loneliness),
name options, 1 Corinthians 13 as the anchor — open questions await
the owner (the Dracula telling, the ninth, the name).

### `pantheon_catalog.md` — The Pantheon Catalog (the owner's review)
Both rosters seat by seat with everything on the table: Planetary vs
Pantheon per theme, every alternative with pros and cons, every
dilemma flagged ⚖ for the joint decision (Greek Tuesday Ares↔Artemis
with the owner's hunting-is-green reading, the Greek dual, Egyptian
Isis placement, Norse Monday Hel↔Njord↔Frigg, Slavic Svarog/Lada,
the Wolf OMEGA discovery — Omega already IS the Alpha/Omega dual),
the unchanged themes argued, the Wider-Pantheon lane, and the open
picks list. Option names approved: Pantheon / Planetary.

### `pantheon_roster_report.md` — The Two Rosters: Seats Are Archetypes
The owner's doctrine (2026-07-15): a seat is OUR archetype
(color + virtue + vice + mood + estate — the matrix from our own
Database), never a planet hunting its literal counterpart — fame
comes first and WE forge the symbolism (Zeus takes the throne,
Poseidon takes the blue sea-Moon, Athena takes Wisdom's own seat).
Proposed Pantheon rosters for Greek, Egyptian, Norse, Slavic and the
Wolf ladder (Gamma/Delta/Omega complete it; Sigma stays the Ninth),
the Planetary rosters staying as the second Settings option
("Pantheon" / "Planetary" naming proposal), the audit facts from the
Haiku pass, the Wider-Pantheon Encyclopedia lane and the execution
checklist — awaiting the GO per table.

### `prompts/badge/scale_badge_prompts.md` — Scale Badge Prompts
The Judas–Lucifer Scale triptych behind the Duality topic and the
Trinity doctrine (owner: duality rides the scale, the Trinity is
their union 2+1): the flame-bearing Lucifer up-triangle, the empty
Judas down-triangle with noose and thirty coins, and the Union
hexagram around the blank zero where the Sun stands — documents the
EXISTING assets/badge/gemini/scale/ renders for regeneration and the
ChatGPT parallel set.

### `prompts/badge/season_trinity_prompts.md` — Season & Trinity Badge Prompts
The remaining concept badges (owner 2026-07-13): the Trinity family
(Faith/Hope/Love, triskelion bronze cameo), the Seasons on the Goethe
axis (Spring/Summer/Autumn/Winter + Wet/Dry, copper growth-ring), the
Turning Points (both Solstices + one Equinox, split gold/silver
hexagram field) and the optional Meteorological twins — 16 prompts,
drop dirs assets/badge/trinity/ and assets/badge/season/.

### `prompts/weekday/bible_dark_prompts.md` — Bible II & Dark Set Prompts
The owner's two-sets decision (2026-07-13): BIBLE II (Abraham·Isaac
dual, Jonah, Samson, Jacob, Noah, Ruth/Esther alternatives, Job) and
the DARK set as night-window stained glass where every figure MIRRORS
a light one (Lucifer·Judas dual, Lilith, Goliath, the Serpent,
Herod/Nebuchadnezzar alternatives, Delilah, Cain) — 18 theme prompts
+ the two scale badges (Judas ▽ blue / Lucifer △ red) for "The Two
Triangles"; drop dirs assets/weekday/bible/secondary|bible_dark/ and
assets/badge/scale/.

### `prompts/weekday/cosmos_prompts.md` — Cosmos & Planets Medallion Prompts
The COSMOS weekday theme (owner 2026-07-13): deep-sky objects as
bronze star-chart medallions — Sun with the event-horizon black hole
dual, nebula, supernova, pulsar-as-clock, galaxy, binary stars,
comet — 16 prompts (bronze + colored arcs) plus the 8-prompt Planets
medallion look (drop dir assets/weekday/planets/art/).

### `prompts/emblem/intelligences_prompts.md` — Nine Intelligences & Wheel of Moods
The Nine Intelligences badges (owner GO 2026-07-13): a new
silver-inlaid "academy cameo" family, 9 = the six Prism arms + the
three Trinity arms, each with its instrument and arm-color enamel
(drop dir assets/emblem/intelligence/); plus the Wheel of Moods medallion —
the dial's own eight-mood wheel in the exact paint hues with the
white Glory center and the Awe crescent below (assets/emblem/mood/).

### `prompts/zodiac/chinese_zodiac_prompts.md` — Chinese Zodiac Prompts
The bronze Chinese-zodiac redesign (owner 2026-07-13): the Greek
key border replaced by a huiwen meander with Wu Xing element
roundels on the pentagram points — 12 Gemini prompts, drop dir
assets/zodiac/chinese/primary/.

### `prompts/instrument/instrument_prompts.md` — Instrument Prompt & Shot Sheet
Images for the Encyclopedia's "The Instrument" articles (owner
2026-07-13): a section-logo Gemini prompt in its own gear-tooth
bronze family, a Paint/Light abstraction prompt, exact SCREENSHOT
instructions for the five articles the app itself already draws
(dial, solar rotation, twilight, year wheel, lunations) and
existing-asset pointers for metals and ring letters.

### Legacy regeneration sheets (owner 2026-07-14, ChatGPT wave)
Scenes authored FRESH from the symbolism canon with stems matching
the existing assets so regenerations overwrite in place:
`prompts/weekday/greek_prompts.md` (8, meander+laurel),
`norse_prompts.md` (8, knotwork+runes),
`egypt_prompts.md` (8+8 colored, cartouche+scarab),
`slavic_prompts.md` (8+8 colored, kolovrat+wheat),
`religion_prompts.md` (Creeds, 8, silver-on-black),
`religion_alt_prompts.md` (Mysteries, 8),
`profession_prompts.md` (8, Servant dual sits flat per defaults),
`japan_prompts.md` (8, seigaiha ring, kanji-free),
`planet_signs_prompts.md` (8, metal sigils + eclipsed dual) and
`prompts/zodiac/astrology_prompts.md` (36: sign/logo/constellation
under the strict element palettes).

### `symbolism_audit.md` — Symbolism Audit
Three-auditor report (mythology accuracy / moral axes / consistency):
swap recommendations, improvements and confirmations — the owner
decides each.

## Connections

### Uses
- [Database (folder)](../Database/___database.md) — source data for analysis
