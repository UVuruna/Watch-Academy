# research/

One-off analysis scripts, oversized data and OWNER-FACING design
documents (image-prompt sheets, audits, expansion specs) — NOT bundled
with the app, not part of the runtime dependency graph.

## Files

### `graph_years.py`
Exploratory plotting of season/year data.

### `efficency.py`
Performance experiments.

### `seasons_large.json` (~11 MB)
Extended variant of `Database/seasons_utc.json` kept for analysis; the app
bundles only the compact file.

### `colored_badge_prompts.md` — Colored Badge Prompts
Gemini image prompts for the COLORED weekday/zodiac badge sets (the
house prompt style every later prompt sheet follows).

### `encyclopedia_expansion.md` — Encyclopedia Expansion
Design + ship-ready copy for the Encyclopedia's second half (owner
task 2026-07-12): "The Instrument" functionality articles (dial, solar
rotation, twilight, year wheel, lunations, palettes, metals, ring
letters), the Virtues/Sins/Moods sections, and the WEEK mode — seven
cross-theme weekday pages with Sunday and Tuesday written in full.

### `virtue_sin_mood_prompts.md` — Virtue/Sin/Mood Prompts
The three canonical 8-item lists (Sunday dual) and 24 Gemini prompts
for their logos — gold cameo virtues, blackened-iron sins, silver
sundial moods; proposed drop dirs assets/virtue|sin|mood/.

### `guide_shotlist.md` — Guide Redesign and Shot List
The Guide's 30-chapter redesign plan plus the numbered 37-screenshot
shot list with exact preconditions per shot (owner shoots these).

### `sunday_duality.md` — Sunday Duality
Servant.png prompts (bronze plate + colored) to pair with the Ruler on
Sunday, the dual-legend concept, and the cross-theme survey of second
sun figures (Ra's night barque, Sól/Skoll, Amaterasu's cave...).

### `bible_theme_prompts.md` — Bible Theme Prompts
The owner-requested 12th weekday theme: both testaments as stained
glass — the day mapping with rationale (Ancient of Days + the Son as
Servant on Sunday, Mary/Moon, David/Mars, Moses/Mercury,
Solomon/Jupiter, Bride and Bridegroom/Venus, Joseph's sheaves/Saturn)
and the 8 Gemini prompts (drop dir assets/weekday/bible/).

### `alchemy_metal_prompts.md` — Alchemy Metal Prompts
Redesign of the seven alchemy weekday plates: the shared ingot-pile
center is replaced by one signature object + signature behavior +
explicit finish per metal (mirror/tarnish, forge/rust, liquid beads,
bell, verdigris, plumb bob) so the four gray metals become
distinguishable; 7 Gemini prompts, borders kept.

### `wolf_pack_prompts.md` — Wolf Pack Theme Prompts
The owner-approved 13th weekday theme: the pack hierarchy as the week
(Alpha with the Omega servant as Sunday dual — the dial's own M/Ω
ring letters made flesh — Luna, Hunter, Scout, Beta, Mate, Elder),
fourth bronze metal-theme with a paw-print border, 8 bronze + 8
colored Gemini prompts; drop dir assets/weekday/wolf/.

### `bee_hive_prompts.md` — Bee Hive Theme Prompts
The 14th weekday theme: the hive's castes as the week (Queen with
the day-one Cleaner as Sunday dual, Nurse, Guard, Scout's waggle
dance, Builder, the Drone on Venus — owner's call — and the dying
Forager on Saturn), honeycomb border echoing the dial's hexagram,
8 bronze + 8 colored prompts; drop dir assets/weekday/bee/.

### `elephant_herd_prompts.md` — Elephant Herd Theme Prompts
The 15th weekday theme closing the animal-society trio (pack=rank,
hive=function, herd=MEMORY): Matriarch with the dead matriarch's
bones as the Memory dual, Allomother, Musth, the infrasound Caller,
the bachelor-school Mentor, the Reunion ceremony, the Elder digging
remembered water on her last molars; acacia-and-tusk border, 8
bronze + 8 colored prompts; drop dir assets/weekday/elephant/.

### `season_trinity_prompts.md` — Season & Trinity Badge Prompts
The remaining concept badges (owner 2026-07-13): the Trinity family
(Faith/Hope/Love, triskelion bronze cameo), the Seasons on the Goethe
axis (Spring/Summer/Autumn/Winter + Wet/Dry, copper growth-ring), the
Turning Points (both Solstices + one Equinox, split gold/silver
hexagram field) and the optional Meteorological twins — 16 prompts,
drop dirs assets/trinity/ and assets/season/.

### `symbolism_audit.md` — Symbolism Audit
Three-auditor report (mythology accuracy / moral axes / consistency):
swap recommendations, improvements and confirmations — the owner
decides each.

## Connections

### Uses
- [Database (folder)](../Database/___database.md) — source data for analysis
