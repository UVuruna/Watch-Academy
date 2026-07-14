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

### `prompts/weekday/colored_badge_prompts.md` — Colored Badge Prompts
Gemini image prompts for the COLORED weekday/zodiac badge sets (the
house prompt style every later prompt sheet follows).

### `encyclopedia_expansion.md` — Encyclopedia Expansion
Design + ship-ready copy for the Encyclopedia's second half (owner
task 2026-07-12): "The Instrument" functionality articles (dial, solar
rotation, twilight, year wheel, lunations, palettes, metals, ring
letters), the Virtues/Sins/Moods sections, and the WEEK mode — seven
cross-theme weekday pages with Sunday and Tuesday written in full.

### `prompts/emblem/virtue_sin_mood_prompts.md` — Virtue/Sin/Mood Prompts
The three canonical 8-item lists (Sunday dual) and 24 Gemini prompts
for their logos — gold cameo virtues, blackened-iron sins, silver
sundial moods; proposed drop dirs assets/virtue|sin|mood/.

### `guide_shotlist.md` — Guide Redesign and Shot List
The Guide's 30-chapter redesign plan plus the numbered 37-screenshot
shot list with exact preconditions per shot (owner shoots these).

### `prompts/weekday/sunday_duality.md` — Sunday Duality
Servant.png prompts (bronze plate + colored) to pair with the Ruler on
Sunday, the dual-legend concept, and the cross-theme survey of second
sun figures (Ra's night barque, Sól/Skoll, Amaterasu's cave...).

### `prompts/weekday/bible_theme_prompts.md` — Bible Theme Prompts
The owner-requested 12th weekday theme: both testaments as stained
glass — the day mapping with rationale (Ancient of Days + the Son as
Servant on Sunday, Mary/Moon, David/Mars, Moses/Mercury,
Solomon/Jupiter, Bride and Bridegroom/Venus, Joseph's sheaves/Saturn)
and the 8 Gemini prompts (drop dir assets/weekday/bible/).

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
colored Gemini prompts; drop dir assets/weekday/wolf/.

### `prompts/weekday/bee_hive_prompts.md` — Bee Hive Theme Prompts
The 14th weekday theme: the hive's castes as the week (Queen with
the day-one Cleaner as Sunday dual, Nurse, Guard, Scout's waggle
dance, Builder, the Drone on Venus — owner's call — and the dying
Forager on Saturn), honeycomb border echoing the dial's hexagram,
8 bronze + 8 colored prompts; drop dir assets/weekday/bee/.

### `prompts/weekday/elephant_herd_prompts.md` — Elephant Herd Theme Prompts
The 15th weekday theme closing the animal-society trio (pack=rank,
hive=function, herd=MEMORY): Matriarch with the dead matriarch's
bones as the Memory dual, Allomother, Musth, the infrasound Caller,
the bachelor-school Mentor, the Reunion ceremony, the Elder digging
remembered water on her last molars; acacia-and-tusk border, 8
bronze + 8 colored prompts; drop dir assets/weekday/elephant/.

### `prompts/badge/season_trinity_prompts.md` — Season & Trinity Badge Prompts
The remaining concept badges (owner 2026-07-13): the Trinity family
(Faith/Hope/Love, triskelion bronze cameo), the Seasons on the Goethe
axis (Spring/Summer/Autumn/Winter + Wet/Dry, copper growth-ring), the
Turning Points (both Solstices + one Equinox, split gold/silver
hexagram field) and the optional Meteorological twins — 16 prompts,
drop dirs assets/trinity/ and assets/season/.

### `prompts/weekday/bible_dark_prompts.md` — Bible II & Dark Set Prompts
The owner's two-sets decision (2026-07-13): BIBLE II (Abraham·Isaac
dual, Jonah, Samson, Jacob, Noah, Ruth/Esther alternatives, Job) and
the DARK set as night-window stained glass where every figure MIRRORS
a light one (Lucifer·Judas dual, Lilith, Goliath, the Serpent,
Herod/Nebuchadnezzar alternatives, Delilah, Cain) — 18 theme prompts
+ the two scale badges (Judas ▽ blue / Lucifer △ red) for "The Two
Triangles"; drop dirs assets/weekday/bible2|bible_dark/ and
assets/scale/.

### `prompts/weekday/cosmos_prompts.md` — Cosmos & Planets Medallion Prompts
The COSMOS weekday theme (owner 2026-07-13): deep-sky objects as
bronze star-chart medallions — Sun with the event-horizon black hole
dual, nebula, supernova, pulsar-as-clock, galaxy, binary stars,
comet — 16 prompts (bronze + colored arcs) plus the 8-prompt Planets
medallion look (drop dir assets/weekday/planets_art/).

### `prompts/emblem/intelligences_prompts.md` — Nine Intelligences & Wheel of Moods
The Nine Intelligences badges (owner GO 2026-07-13): a new
silver-inlaid "academy cameo" family, 9 = the six Prism arms + the
three Trinity arms, each with its instrument and arm-color enamel
(drop dir assets/intelligence/); plus the Wheel of Moods medallion —
the dial's own eight-mood wheel in the exact paint hues with the
white Glory center and the Awe crescent below (assets/mood/).

### `prompts/zodiac/chinese_zodiac_prompts.md` — Chinese Zodiac Prompts
The bronze Chinese-zodiac redesign (owner 2026-07-13): the Greek
key border replaced by a huiwen meander with Wu Xing element
roundels on the pentagram points — 12 Gemini prompts, drop dir
assets/zodiac/chinese/.

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
