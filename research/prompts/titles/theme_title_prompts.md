# Theme Title Plates — the Encyclopedia's Own Cover Pages (Gemini/ChatGPT)

Owner item 7 (R8c PROMPT SHEETS round, 2026-07-21): every weekday theme
(and a handful of sibling topics) already carries a documented,
graceful-absent slot for its OWN title-page plate —
`app.encyclopedia._weekday_topic`'s `title_entry`, `"images": ()`, the
code comment reads it outright: *"graceful-absent — a future theme
plate's slot"*. This sheet fills that slot for every theme that has
one and does not already have art (Continents is the ONE theme that
already carries a real title image, `assets/earth/world.png` — SKIPPED
here per the owner's own instruction). It also covers two sibling
topics that carry the identical empty-slot pattern outside the weekday
family: **The Nine Intelligences** and **The Slavic Months** (the
latter's gallery tile is genuinely empty today — its icon borrows
June's own month plate, `Lipanj.png`, which does not exist on disk yet
either).

**Greek Monsters and Chinese Mythology are NOT in this file.** Both
new themes (`research/prompts/monsters/greek_monsters_prompts.md`,
`research/prompts/chinese/chinese_myth_prompts.md`) name their own
title plates — Typhon & Echidna, The Peach Banquet — as part of THEIR
sheets' own cast description, but per the canonical root this sheet
establishes below, both plates' brief and drop path are written HERE
(see the two entries at the very end) so every title plate in the
project lives in exactly one place. Cross-referenced, not duplicated.

**The GAMING + CORPORATION SHEET WAVE (R10, 2026-07-22) follows the
same root, ten more title plates.** WoW, Cyberpunk and Star Wars each
carry THREE blocks/sets, so each gets three title plates (one per
block); The Corporation carries one. All ten are written in FULL here
(see "The GAMING + CORPORATION SHEET WAVE title plates" section below)
— their own theme sheets (`research/prompts/wow/wow_prompts.md`,
`research/prompts/cyberpunk/cyberpunk_prompts.md`,
`research/prompts/starwars/starwars_prompts.md`,
`research/prompts/corporate/corporate_prompts.md`) each carry only a
short pointer in their own "Cross-reference" section, never a
duplicate body.

## The lettering exception (read before generating anything)

**Every other sheet in this entire project forbids lettering.** This
one is the sole, deliberate exception: a title plate's whole job is to
carry the theme's own name, so each brief below asks for ONE wordmark
— the theme's ENGLISH display name (`config.defaults.
WEEKDAY_THEME_TITLES`, or the literal topic title where the theme has
no menu entry), rendered in a script that belongs to that theme's own
culture (owner: *"Egipatski bogovi npr treba da ima svoj font"*).
Nothing else in the image ever carries text — no captions, no
inscriptions inside the scene itself, only the one wordmark, placed as
a plaque, banner, cartouche or carved base depending on what the
theme's own material would actually do. Generating fully legible
script is known to fail unreliably on some scripts (`japan_prompts.md`
already documents this for kanji) — where a script cannot be rendered
legibly (runic, glagolitic, hieroglyphic, seal-script), the brief asks
for the correct LETTERFORM FLAVOR applied to the Latin theme name
rather than a genuine foreign alphabet, exactly the same compromise
`japan_prompts.md` already made for its kiku roundels.

## The canonical drop path

**`assets/titles/<key>.png`** — ONE new, sourceless root (no
`<source>` split, deliberately outside `config.constants.
ART_SOURCED_ROOTS`), flat, ASCII theme-key stems taken straight from
`config.defaults.WEEKDAY_THEME_ARTICLES`'s own keys (`planet_signs`,
`religion_alt`, `bible_dark`, `planets_art`, …) plus `intelligences`
and `months` for the two sibling topics. This is the SAME precedent
`assets/months/` and `assets/subdial/` already set (`assets/
___assets.md`'s "NOT art-sourced" family): a title plate is a SHARED
thing, one per theme, not a Gemini/ChatGPT split, and — unlike the
weekday cast root — never a primary/colored pair either (`assets/
earth/world.png`, the Continents title image, is the one title plate
already wired, and it too is a single flat file, no register split).
A future wiring round fills every theme's `title_entry["images"]`
tuple with `(defaults.TITLE_ART_DIR / f"{theme}.png",)`, mirroring
`CONTINENTS_TITLE_IMAGE` exactly — that wiring is OUT of this
sheet-writing round's scope (no app code this round).

**Why not per-theme folders (`assets/weekday/<theme>/title.png`)?**
Considered and rejected: a title plate is read by ONE consumer
(`_weekday_topic`'s title page) regardless of which cast register the
theme otherwise ships, so nesting it inside the sourced weekday tree
would force it through the source-fallback machinery for no reason —
the flat sourceless root is simpler AND matches the one title plate
that already exists.

## Derivation check (Rule #19)

Every plate below is a genuinely different scene in a genuinely
different material (bronze relief, stained glass, brass engraving,
folk woodcut…) with a genuinely different wordmark script — none of
the 26 is a tint, a crop or a recolor of another. The only thing that
LOOKS like a repeatable pattern — "theme essence scene + wordmark
plaque" — is a compositional convention, not a derivable pixel
transform (unlike a metal hue-swap or a shadow angle); a formula
cannot paint Ra's sun-barge from Cronus's clock-halo. Nothing here is a
candidate for algorithmic collapse.

## House rules

Photorealistic (or, where the theme's own cast register is
sculptural/relief, that same relief) render, isolated background (no
transparency-checkerboard artifact), no `dual/`-style subfolder — one
flat file per theme. The circular-medallion vs. rectangular-plate shape
follows whichever shape that theme's OWN cast art already uses (bronze
medallions stay circular, stained-glass sets stay round rose-windows,
the Planets photographic look stays a squared plate like an
observatory print) — consistency with the sibling sheet, not a new
shape invented here.

## The typography direction table

| Theme (key) | Display name | Script direction |
|---|---|---|
| `planets` | Planets | Engraved observatory-plate capitals — thin Roman lapidary caps cut into brass like an antique orrery print |
| `planet_signs` | Planet signs | Astrological glyph-serif — illuminated capitals with tiny planetary glyphs worked into the serifs |
| `greek` | Greek gods | Attic lapidary capitals — carved Greek temple-inscription capitals |
| `norse` | Norse gods | Younger Futhark runic capitals — angular straight-stroke runic letterforms |
| `egypt` | Egyptian gods | Hieroglyph-flavored cartouche capitals (owner example) |
| `slavic` | Slavic gods | Glagolitic-flavored capitals (owner example) |
| `alchemy` | Alchemy | Alchemical manuscript hand — ligatured treatise script, wax-seal red |
| `japan` | Japanese week | Sumi-e brush calligraphy capitals — bold ink brushstrokes, one red seal-stamp accent |
| `religion` | Creeds | Uncial illuminated capitals (owner example) — gold leaf |
| `religion_alt` | Ancient religions | Weathered cuneiform-and-lapidary hybrid capitals — wedge-and-chisel strokes on worn stone |
| `profession` | Professions | Guild-stamp blackletter capitals — a struck trade-guild mark |
| `wolf` | Wolf Pack | Claw-slash primal capitals — gouged strokes raked through bark |
| `bee` | Bee Hive | Honeycomb-cell geometric capitals — hexagon-built letterforms, wax sheen |
| `elephant` | Elephant Herd | Carved-ivory tribal capitals — thick rounded letterforms, beadwork serifs |
| `bible` | Bible | Illuminated Gothic blackletter, gold leaf |
| `bible2` | Bible II | Sepia scriptorium capitals — plainer warm-brown ink monastic hand |
| `bible_dark` | Bible Dark | Ashen cracked-Fraktur capitals — scorched, ember-lit edges |
| `cosmos` | Cosmos | Art-deco astronomical capitals (owner example) — starburst serifs |
| `planets_art` | *(no menu title — see note)* | Engraved bronze-relief capitals — a relief-cut sibling of the Planets script |
| `virtues` | *(The Virtues)* | Classical laurel-serif capitals — chiseled Roman caps, tiny laurel serifs |
| `sins` | *(The Sins)* | Cracked obsidian ichor-drip capitals — jagged fractured black-glass letterforms |
| `moods` | *(The Moods)* | Flowing watercolor-bleed cursive — loose brush-italic, bleeding color |
| `intelligences` | The Nine Intelligences | Copperplate diagram capitals — fine compass-and-protractor construction lines, silver-inlaid bronze |
| `months` | The Slavic Months | Carved folk woodblock capitals — rustic incised wood-carving letterforms |
| `monsters` | *(Greek Monsters — sheet's own file)* | Weathered bestiary lapidary capitals — the Attic family, pitted and claw-scratched |
| `chinese_myth` | *(Chinese Mythology — sheet's own file)* | Seal-script flavored capitals (owner example) — blocky zhuanshu strokes cut into red lacquer |
| `wow_alliance` | *(WoW: Alliance — sheet's own file)* | Gold-inlaid Alliance heraldic capitals — carved rampant-lion serifs, the block's own runestone letterforms |
| `wow_horde` | *(WoW: Horde — sheet's own file)* | Iron-cut Horde tribal capitals — jagged wolf-fang serifs hammered into red-lacquered wood |
| `wow_evil` | *(WoW: Evil — sheet's own file)* | Frost-cracked saronite capitals — jagged rime-rimmed blackletter, corruption-green veins threading the strokes |
| `cyberpunk_gangs` | *(Cyberpunk: Gangs — sheet's own file)* | Spray-tag street capitals — glitch-torn stencil letterforms, gang-neon drip |
| `cyberpunk_street` | *(Cyberpunk: Street — sheet's own file)* | Chrome neon-sign cursive — a bar-marquee script, flickering tube-light strokes |
| `cyberpunk_power` | *(Cyberpunk: Power — sheet's own file)* | Corrupted terminal capitals — monospace code-glyphs dissolving into static at the edges |
| `starwars_svetla` | *(Star Wars: Svetla — sheet's own file)* | Aurebesh-flavored temple capitals — angular geometric letterforms cut in warm bronze (the same documented letterform-flavor compromise as `egypt`/`norse`, never a genuine readable alphabet) |
| `starwars_tamna` | *(Star Wars: Tamna — sheet's own file)* | Aurebesh-flavored Imperial capitals — the same angular geometric letterforms, cut into black durasteel instead |
| `starwars_nova` | *(Star Wars: Nova — sheet's own file)* | Aurebesh-flavored fused capitals — each letterform split down the middle, half bronze, half durasteel |
| `corporate` | *(The Corporation — sheet's own file)* | Engraved lanyard-badge sans — clean brushed-steel capitals, laser-etched |

Two rows carry a caveat, not a doubt about the brief itself: `planets_art`
carries **no menu title on purpose** (`WEEKDAY_THEME_TITLES`'s own
comment — it nests as the Planets "Art" look, never its own gallery
card) and `planet_signs` is **never a gallery card either** (merged
into the Planets topic's own Signs look; `_TOPIC_GROUPS`'s comment
says so outright) — both title plates below are written because the
owner's enumeration named them explicitly, but wiring either one to
anything visible is a future call, not assumed here.

---

## `planets` — Planets (`assets/titles/planets.png`)

*"Shows them AS THEMSELVES, before any myth is laid over them" — the
neutral roster every other theme borrows its shape from.*

```
An antique brass orrery plate, engraved line-art photorealistic render, perfectly centered, isolated on white background. Center: a fine engraved armillary device, the seven classical bodies — Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn — held on thin brass orbit-rings around a small radiant sun at the hub, each body a plain unadorned sphere, no myth-figure riding any of them. Along the base, a narrow engraved brass plaque reads "PLANETS" in precise Roman lapidary capitals, thin serifs, cut clean into the metal — the ONE piece of text anywhere in the image. Palette: warm engraved brass, deep instrument-black shadow, one cool starlight-white accent at the sun's hub.
```

---

## `planet_signs` — Planet signs (`assets/titles/planet_signs.png`)

*The Planets topic's own glyph face — the same seven bodies read
through their zodiac-ruling glyphs instead of a photograph.*

```
An illuminated astrological manuscript page, painted photorealistic render, perfectly centered, isolated on white background. Center: the seven planetary glyphs (☉ ☾ ♂ ☿ ♃ ♀ ♄) arranged in a ring like a small zodiac wheel, each glyph rendered in gold leaf with a faint colored halo matching its own body, floating over a deep midnight-blue star field. Beneath the ring, a curling illuminated banner reads "PLANET SIGNS" in an astrological glyph-serif hand — ornate capitals with tiny planetary glyphs worked into the ascenders — the ONE piece of text anywhere in the image. Palette: gold leaf, midnight blue, faint colored glyph-halos.
```

---

## `greek` — Greek gods (`assets/titles/greek.png`)

*Olympus supplies a body for every classical planet — the title plate
gathers all seven emblems the roster's own figures carry, the same
"every seat at once" device Gaia's own border already uses.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Mount Olympus rising behind a ring of seven small emblematic objects arranged like a wreath — a thunderbolt, a crescent-topped chariot wheel, a spear and shield, a caduceus, an eagle-topped scepter, a golden apple, a scythe — each cast in the same bronze relief as the full medallions those gods carry elsewhere. Along the base, a carved stone plinth bears "GREEK GODS" in Attic lapidary capitals, temple-inscription letterforms cut clean into the stone — the ONE piece of text anywhere in the image. Border: the family's own Greek key (meander) band, broken by laurel-wreath roundels. Palette: aged bronze, warm laurel-gold, Olympian sky-white.
```

---

## `norse` — Norse gods (`assets/titles/norse.png`)

*The Æsir take the seven seats by the same law — Yggdrasil is the
frame every one of them stands inside.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Yggdrasil the world-tree filling the disc, its branches carrying small glimpses of the week's own cast worked into the bark — a wolf's silhouette, a hammer, a raven, a spinning wheel — its roots vanishing into cold mist below. Along the base, a carved wooden plinth bears "NORSE GODS" in Younger Futhark runic capitals, angular straight-stroke letterforms carved deep into weathered wood — the ONE piece of text anywhere in the image. Border: a continuous Celtic interlace-knotwork band, broken by four small roundels. Palette: aged bronze, frost-grey bark, cold northern blue.
```

---

## `egypt` — Egyptian gods (`assets/titles/egypt.png`)

*Ra crosses the sky by day and Khonsu walks it by night — the barge
itself, not any one god, is the theme's own emblem.*

```
Ornate circular medallion, tomb-fresco painted relief, photorealistic render, perfectly centered, isolated on white background. Center: the solar barge sailing across a split sky, sun-disc gold on the upper half where it crosses by day, deep star-strewn indigo on the lower half where it crosses by night, a scarab and an ankh riding the prow, twin pyramids silhouetted on the horizon beneath it. Along the base, a gold cartouche oval encloses "EGYPTIAN GODS" in hieroglyph-flavored capitals, papyrus-reed and ankh flourishes worked into the letterforms — the ONE piece of text anywhere in the image. Palette: tomb-gold, lapis-blue night half, sun-disc amber.
```

---

## `slavic` — Slavic gods (`assets/titles/slavic.png`)

*Dažbog the giving sun opens the week, Morana closes it on the arm of
renewal — the kolovrat wheel already ties the whole roster together.*

```
Ornate circular medallion, folk-icon painted relief, photorealistic render, perfectly centered, isolated on white background. Center: a great kolovrat (spoked sun-wheel) filling the disc, Svarog's forge-fire glowing at its hub, Perun's thunder and Veles's horns glimpsed as small worked reliefs where two spokes meet, a bare winter branch and a green spring branch crossing beneath it — Morana's own turning. Along the base, a carved wooden plinth bears "SLAVIC GODS" in glagolitic-flavored capitals, rounded loop-and-cross letterforms — the ONE piece of text anywhere in the image. Border: a rope-braid rim in folk red and gold. Palette: forge-red, kolovrat gold, folk-icon cream.
```

---

## `alchemy` — Alchemy (`assets/titles/alchemy.png`)

*The classical planet-metal correspondence — one still life of every
metal the week wears, all seven at once on the alchemist's own bench.*

```
Ornate circular medallion, weathered bronze relief on dark stone, photorealistic render, perfectly centered, isolated on white background. Center: a stone workbench holding all seven metals at once — a gold bar, a silver bar, a rough iron nugget, coiled quicksilver in a glass vial, a tin ingot, a coil of copper wire, a dull lead weight — arranged in a loose ring around a central engraved tablet bearing the seven planetary alchemical symbols in low relief. Along the base, a carved stone plinth bears "ALCHEMY" in an ornate alchemical manuscript hand, ligatured letterforms touched with wax-seal red — the ONE piece of text anywhere in the image. Palette: gold, silver, iron-black, copper-red, tin-grey.
```

---

## `japan` — Japanese week (`assets/titles/japan.png`)

*The yōbi week under a second cosmology — Fuji, the torii and the
rising sun in one frame.*

```
Ornate circular medallion, gold relief against a crimson sun-orb, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: Mount Fuji rising snow-capped behind a vermilion torii gate, a blazing gold rising-sun fan filling the sky above both, a few cherry-blossom petals drifting past. Along the base, a simple ink-brushed banner bears "JAPANESE WEEK" in bold sumi-e brush calligraphy capitals, single black ink strokes with one small red seal-stamp beside them — the ONE piece of text anywhere in the image. Border: the family's own seigaiha wave band. Palette: gold relief, crimson sun-orb, Fuji snow-white.
```

---

## `religion` — Creeds (`assets/titles/religion.png`)

*Seven living creeds, seven arguments — the title plate borrows one
small emblem from each faith's own canonical border, arranged as
equals around a shared flame.*

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background. Center: a single tall flame rising from a plain stone lamp, and around it, worked in low silver relief, seven small emblems in a ring — a grapevine-and-fish, geometric strapwork, a lotus, a bagua-and-yin-yang, an Om-rosette, a khanda, a leaf-and-star — each faith's own canonical border-mark, none larger than another. Along the base, a carved black plinth bears "CREEDS" in uncial illuminated capitals, rounded monastic book-hand touched with gold leaf — the ONE piece of text anywhere in the image. Palette: silver-on-black, one warm gold-leaf accent, the flame's own soft white light.
```

---

## `religion_alt` — Ancient religions (`assets/titles/religion_alt.png`)

*A second, older set — Mithraism's sun, Druidism's oak, Zoroastrianism's
fire, Babylon's own invented week.*

```
Ornate circular medallion, weathered stone temple relief, photorealistic render, perfectly centered, isolated on white background. Center: a worn ziggurat altar, and arrayed around its base in low relief, seven older emblems — a bull, an oak leaf, a sacred flame, a shaman's drum, a torch, an eight-pointed star, a veve sigil — each older and cruder-cut than the polished Creeds ring, weathered by age rather than newly carved. Along the base, a wedge-cut stone plinth bears "ANCIENT RELIGIONS" in weathered cuneiform-and-lapidary hybrid capitals, chisel-and-wedge strokes on worn stone — the ONE piece of text anywhere in the image. Palette: worn sandstone, temple-fire orange, weathered grey-brown.
```

---

## `profession` — Professions (`assets/titles/profession.png`)

*A medieval-to-modern career per day — the world's work laid across
the week, one tool per estate.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: six tools of the six weekday professions arranged like guild-hall wall-hooks around a central crowned throne (the Ruler·Servant Sunday seat) — a physician's staff-and-serpent, a soldier's sword, a merchant's scale, a priest's crook, an artist's palette, a farmer's plough — each hung in its own bronze relief bracket. Along the base, a struck metal plaque bears "PROFESSIONS" in guild-stamp blackletter capitals, an embossed trade-guild mark — the ONE piece of text anywhere in the image. Palette: aged bronze, iron-black tool edges, warm workshop amber.
```

---

## `wolf` — Wolf Pack (`assets/titles/wolf.png`)

*A real wolf pack's ranks fill the week — the whole pack together,
not one wolf alone.*

```
Ornate circular medallion, weathered bronze sculptural relief on dark cracked stone, photorealistic render, perfectly centered, isolated on white background. Center: a full wolf pack gathered on a moonlit ridge, muzzles lifted together in one long howl, a bright moon disc rising behind them, the Alpha standing slightly forward of the rest. Along the base, a carved stone plinth bears "WOLF PACK" in claw-slash primal capitals, rough gouged strokes as if raked through bark — the ONE piece of text anywhere in the image. Border: the family's own paw-print trail interlaced with pine sprigs. Palette: aged bronze, moonlit silver-blue, dark cracked stone.
```

---

## `bee` — Bee Hive (`assets/titles/bee.png`)

*A worker bee's whole career IS a clock — the title plate shows the
whole hive at once, every rank in its own cell.*

```
Ornate circular medallion, weathered bronze sculptural relief on dark cracked stone, photorealistic render, perfectly centered, isolated on white background. Center: a full honeycomb cross-section filling the disc, each hexagonal cell holding a tiny worked relief of one hive rank at its task — grooming, nursing, guarding, scouting, building, foraging — radiating outward from a larger central cell holding the Queen. Along the base, a wax-sealed plinth bears "BEE HIVE" in honeycomb-cell geometric capitals, hexagon-built letterforms with a warm wax sheen — the ONE piece of text anywhere in the image. Palette: aged bronze, honey amber, dark waxed cell-walls.
```

---

## `elephant` — Elephant Herd (`assets/titles/elephant.png`)

*A matriarchal herd across the week — an intelligence built on what
the herd carries forward.*

```
Ornate circular medallion, weathered bronze sculptural relief on dark cracked stone, photorealistic render, perfectly centered, isolated on white background. Center: a full elephant herd migrating across a dusk savanna in low relief, the Matriarch leading at the front, calves sheltered in the herd's center, a distant sun sinking behind them. Along the base, a carved-ivory plinth bears "ELEPHANT HERD" in carved-ivory tribal capitals, thick rounded letterforms with beadwork-pattern serifs — the ONE piece of text anywhere in the image. Palette: aged bronze, dusk-savanna amber, pale ivory plinth.
```

---

## `bible` — Bible (`assets/titles/bible.png`)

*Old and New Testament read across the same seven-armed dial — the
Ancient of Days, seen once, whole.*

```
ROUND rose-window stained-glass medallion, radiant register, photorealistic render, isolated background, the circular window shape IS the frame. Center: the Ancient of Days enthroned in flame-white robes, hair like pure wool, a fiery-wheeled throne beneath him, seven small radiating glass panes fanning out around the throne each holding a faint glimpse of the week's own figures — a woman clothed with the sun, a shepherd-king, a lawgiver, a crowned judge, two entwined figures, a dreamer's sheaves. Along the base, a gold-leafed lancet plaque bears "BIBLE" in illuminated Gothic blackletter capitals, heavy gold leaf on the strokes — the ONE piece of text anywhere in the image. Palette: flame-white, radiant gold, deep stained-glass jewel tones.
```

---

## `bible2` — Bible II (`assets/titles/bible2.png`)

*A second seven from the same scriptures — figures whose stories TEST
faith; the ram caught in the thicket is the second set's own hinge.*

```
ROUND rose-window stained-glass medallion, warm parchment-toned register, photorealistic render, isolated background, the circular window shape IS the frame. Center: Abraham's raised hand stayed mid-motion above a stone altar, Isaac bound but unharmed beside him, a ram caught by its horns in a thicket at the frame's edge — the substitute already arriving. Along the base, a plain sepia-inked plaque bears "BIBLE II" in sepia scriptorium capitals, a plainer warm-brown monastic ink hand, far less gilding than the primary Bible plate — the ONE piece of text anywhere in the image. Palette: warm sepia, parchment cream, altar-stone grey, one white ram accent.
```

---

## `bible_dark` — Bible Dark (`assets/titles/bible_dark.png`)

*Every figure here fell, tempted or was cast out — Lucifer's own fall
opens the set.*

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Center: a shattered golden throne tumbling through darkness, a trail of black-ember flame streaking down and away from it like a falling comet, a single crack of cold light showing through the broken glass behind. Along the base, a scorched plaque bears "BIBLE DARK" in ashen cracked-Fraktur capitals, blackletter strokes fractured and ember-lit at the edges — the ONE piece of text anywhere in the image. Palette: near-black, ember-orange trail, one cold sliver of pale light.
```

---

## `cosmos` — Cosmos (`assets/titles/cosmos.png`)

*The sky's own objects standing in for the myths every other theme
tells — the whole star-chart at once.*

```
Ornate circular medallion, weathered bronze sculptural relief on dark cracked stone, photorealistic render, perfectly centered, isolated on white background. Center: a full star-chart relief with a radiant sun at the hub and, arranged around it, small worked reliefs of the week's own bodies — a nebula pillar, a supernova burst, a pulsar's twin beams, a spiral galaxy, two orbiting stars, a comet's arc. Along the base, an engraved brass plaque bears "COSMOS" in art-deco astronomical capitals, streamlined geometric letterforms with starburst serifs — the ONE piece of text anywhere in the image. Border: the family's own fine engraved star-chart rim. Palette: aged bronze, deep space-black, radiant gold hub.
```

---

## `planets_art` — *(no menu title — the "Art" look)* (`assets/titles/planets_art.png`)

*The Planets ART medallion look — same seven bodies as `planets`,
rendered here as sculpted bronze relief instead of engraved brass, so
the two title plates never read as the same image.*

```
Ornate circular medallion, weathered bronze sculptural relief, photorealistic render, perfectly centered, isolated on white background. Center: a sculpted bronze armillary sphere, the seven classical bodies cast as small relief spheres held on interlocking bronze rings around a radiant central sun, every ring and body carved in full dimensional relief rather than thin engraved line. Along the base, a cast bronze plaque bears "PLANETS" in engraved bronze-relief capitals, a relief-cut sibling of the plain `planets` script — the ONE piece of text anywhere in the image. Palette: weathered bronze, dark cracked stone base, radiant gold hub.
```

---

## `virtues` — The Virtues (`assets/titles/virtues.png`)

*The dial's own inner wheel — eight emblems radiating from one
sunburst, Justice and Humility both at the crown.*

```
Ornate circular medallion, engraved sunburst-gold relief, photorealistic render, perfectly centered, isolated on white background. Center: fine gold rays radiating outward from the hub, and set along eight of those rays, eight small emblems in low relief — a scale, a dove, a raised sword, an owl, a horn of plenty, an open heart, an hourglass, a bowed crown — the eight virtues held in one wheel. Along the base, a gold-chiseled plinth bears "THE VIRTUES" in classical laurel-serif capitals, noble Roman caps with tiny laurel-leaf serifs — the ONE piece of text anywhere in the image. Border: a plain gold sunburst rim. Palette: radiant gold, warm ivory, laurel-green accent.
```

---

## `sins` — The Sins (`assets/titles/sins.png`)

*The virtues' own shadow wheel — the same eight emblems, corrupted.*

```
Ornate circular medallion, fissured obsidian relief, photorealistic render, perfectly centered, isolated on white background. Center: cracks of dull red light radiating outward from the hub through black fissured glass, and set along eight of those cracks, the same eight emblems as the Virtues plate now corrupted — a broken scale, a caged dove, a wrathful blade, a hoarding claw, an overflowing horn spilling waste, a jealous eye, a cracked hourglass, a bowed-but-resentful crown. Along the base, a cracked black plinth bears "THE SINS" in cracked obsidian ichor-drip capitals, jagged fractured black-glass letterforms dripping dark ichor — the ONE piece of text anywhere in the image. Palette: obsidian black, dull ember-red fissures, ichor-dark drips.
```

---

## `moods` — The Moods (`assets/titles/moods.png`)

*The dial's own eight-hour wheel of moods, plus the Ninth Mood's
eclipse — one sky-disc cycling through all of them at once.*

```
Ornate circular medallion, gradient sky-disc relief, photorealistic render, perfectly centered, isolated on white background. Center: a great sky-disc filling the frame, its gradient sweeping through all eight mood colors in one continuous ring — glory-gold, calm-blue, zeal-orange, sorrow-purple, joy-yellow, passion-red, renewal-green, awe-white — a thin dark sliver crossing the disc's edge where the Ninth Mood's eclipse briefly darkens it. Along the base, a soft painted banner bears "THE MOODS" in flowing watercolor-bleed cursive, a loose brush-italic hand with colors bleeding into each other — the ONE piece of text anywhere in the image. Palette: the full eight-color mood gradient, one dark eclipse sliver.
```

---

## `intelligences` — The Nine Intelligences (`assets/titles/intelligences.png`)

*Gardner's nine, moved onto the dial's own nine seats — a mind seen
from the instrument-maker's own angle.*

```
Ornate circular medallion, engraved technical-diagram field, silver-inlaid bronze, photorealistic render, perfectly centered, isolated on white background. Center: a stylized brain in profile, fine compass-arc and protractor-angle construction lines radiating outward from it in low relief, nine small facets marked along those lines each holding a tiny instrument — a discus, two clasped hands, a quill, a compass, a musical note, a leaf, an eye, a mirror, a single lit candle. Along the base, a silver-inlaid plinth bears "THE NINE INTELLIGENCES" in copperplate diagram capitals, fine construction-line letterforms in silver-inlaid bronze — the ONE piece of text anywhere in the image. Border: a laurel half-wreath resting along the lower rim, an academic medal. Palette: silver-inlaid bronze, warm parchment-tan field.
```

---

## `months` — The Slavic Months (`assets/titles/months.png`)

*The Wheel of Labour, whole — all twelve months' own seasons visible
on one great turning cart-wheel at once, not any single spoke alone.*

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Center: one great spoked cart-wheel filling the disc, its rim sweeping through all four seasons at once — frost-blue easing into spring green, spring green warming into harvest gold, gold deepening into autumn russet, russet cooling back into frost-blue — a woodcutter's axe, a linden blossom, a sickle and a bare frost-rimed branch each resting at their own quarter of the rim. Along the base, a carved wooden plinth bears "THE SLAVIC MONTHS" in carved folk woodblock capitals, rustic incised wood-carving letterforms — the ONE piece of text anywhere in the image. Palette: frost blue, spring green, harvest gold, autumn russet, dark-iron lead.
```

---

## The GAMING + CORPORATION SHEET WAVE title plates (R10, 2026-07-22)

Ten plates for the four new sheets this round adds
(`wow_prompts.md`, `cyberpunk_prompts.md`, `starwars_prompts.md`,
`corporate_prompts.md`). WoW/Cyberpunk/Star Wars each carry three
blocks/sets, so each names three title plates (one per block); The
Corporation carries one. Every plate follows the SAME "every seat's
own emblem at once" or "parent, not seat-holder" devices the rest of
this file already uses — no new composition class invented.

### `wow_alliance` — WoW: The Alliance (`assets/titles/wow_alliance.png`)

*The founding covenant — many kingdoms becoming one Alliance, the same
"every seat's own emblem" device `greek`/`cosmos` already use.*

```
Ornate circular medallion, carved rune-scarred stone banded with blue-and-gold metal, photorealistic render, perfectly centered, isolated on white background. Center: Stormwind Keep's own gate rising behind six banners planted shoulder to shoulder in the stone — human, dwarf, night elf, gnome, draenei and worgen sigils in a half-ring — a human and a dwarven hand clasped in the foreground over an open founding charter. Along the base, a carved gold plinth bears "THE ALLIANCE" in gold-inlaid Alliance heraldic capitals, carved rampant-lion serifs — the ONE piece of text anywhere in the image. Border: the block's own blue-and-gold rampant-lion frame. Palette: dawn-blue stone, bright gold, six banner colors.
```

### `wow_horde` — WoW: The Horde (`assets/titles/wow_horde.png`)

*The Horde united — many clans becoming one Horde, mirroring the
Alliance's own device.*

```
Ornate circular medallion, carved rune-scarred stone banded with red-and-black metal, photorealistic render, perfectly centered, isolated on white background. Center: Orgrimmar's own iron gate rising behind five totems planted shoulder to shoulder in the stone — orc, tauren, troll, Forsaken and Blood Elf sigils in a half-ring — an orc and a tauren hand clasped in the foreground over a shared war-drum. Along the base, a carved iron plinth bears "THE HORDE" in iron-cut Horde tribal capitals, jagged wolf-fang serifs — the ONE piece of text anywhere in the image. Border: the block's own red-and-black wolf-fang totem frame. Palette: dusk-red stone, iron black, five totem colors.
```

### `wow_evil` — WoW: The Burning Legion (`assets/titles/wow_evil.png`)

*Sargeras, the Fallen Titan — the PARENT of this block's own
corruption (Mannoroth, Gul'dan and Kil'jaeden all serve him directly),
standing outside the seated nine the same way Typhon & Echidna stand
outside the Greek Monsters roster.*

```
Ornate circular medallion, carved rune-scarred black saronite banded with corrupted ice, photorealistic render, perfectly centered, isolated on white background. Center: Sargeras, the Fallen Titan, a colossal armored figure glimpsed only from the waist up, his own burning sword still lodged hilt-deep in a cracked and burning landmass beneath him, his molten eyes the single source of light in an otherwise starless sky. Along the base, a cracked black plinth bears "THE BURNING LEGION" in frost-cracked saronite capitals, jagged rime-rimmed blackletter veined in corruption-green — the ONE piece of text anywhere in the image. Border: the block's own saronite-and-ice fang frame. Palette: molten-eye orange, saronite black, corruption green, ice-white cracks.
```

### `cyberpunk_gangs` — Cyberpunk: Gangs of Night City (`assets/titles/cyberpunk_gangs.png`)

*Night City's own district map as a glowing neon mosaic, one tile per
resident gang's canonical color — the owner's own suggestion.*

```
ROUND chrome-bezel holo-medallion, brushed chrome ring, photorealistic render, perfectly centered, isolated on white background. Center: Night City's own district map rendered as a glowing holographic mosaic seen from above, each district tile lit in its own resident gang's canonical neon color — teal Pacifica, hot-pink Westbrook, purple-and-tan Heywood, burnt-orange Santo Domingo, dust-orange Badlands — the fault-lines between tiles glowing like live circuitry. Along the base, a spray-tag banner bears "GANGS OF NIGHT CITY" in spray-tag street capitals, glitch-torn stencil letterforms dripping gang-neon — the ONE piece of text anywhere in the image. Border: the block's own circuit-trace ring. Palette: the full district neon spread, circuit-white fault-lines.
```

### `cyberpunk_street` — Cyberpunk: The Afterlife (`assets/titles/cyberpunk_street.png`)

*The Afterlife's own bar interior — the whole circle implied by empty
stools and one untouched glass, the owner's own suggestion.*

```
ROUND chrome-bezel holo-medallion, brushed chrome ring, photorealistic render, perfectly centered, isolated on white background. Center: the Afterlife's own bar interior, a Militech cooling-unit repurposed as a trophy wall of mercenary relics behind the counter, a row of empty stools each catching a different colored neon glow, one glass left half-full and untouched at the bar's far end. Along the base, a flickering marquee bears "THE AFTERLIFE" in chrome neon-sign cursive, a bar-marquee script of flickering tube-light strokes — the ONE piece of text anywhere in the image. Border: the block's own circuit-trace ring. Palette: warm bar-amber, mixed stool-neon, chrome trophy-wall.
```

### `cyberpunk_power` — Cyberpunk: Soulkiller (`assets/titles/cyberpunk_power.png`)

*NOT a person, the FORCE — the program that makes a man neither alive
nor dead, the parent of this block's own ghosts (Alt Cunningham and
Rache Bartmoss both live and die by exactly this program).*

```
ROUND chrome-bezel holo-medallion, brushed chrome ring, photorealistic render, perfectly centered, isolated on white background. Center: a human silhouette suspended mid-dissolve between pure code and solid form, one half rendered in warm living flesh-tone, the other already scattering into cold blue static particles, a heart-rate line and a flat-line both running simultaneously across the frame behind it and never resolving into either. Along the base, a corrupted terminal plaque bears "SOULKILLER" in corrupted terminal capitals, monospace code-glyphs dissolving into static at the edges — the ONE piece of text anywhere in the image. Border: the block's own circuit-trace ring, its lines fraying into static on all four sides rather than breaking cleanly at one point. Palette: living flesh-warm, dissolve-static blue, flat-line grey, code-green undertone.
```

### `starwars_svetla` — Star Wars: The Council of Lights (`assets/titles/starwars_svetla.png`)

*A ring of igniting lightsabers, one per seated figure's own blade
color — the "every seat's own emblem at once" device again.*

```
Ornate circular medallion, Jedi bronze-and-blue temple relief, photorealistic render, perfectly centered, isolated on white background. Center: a circle of igniting lightsaber blades rising point-up from a stone floor like a small Jedi Council convening, each blade its own seated figure's color — blue, blue, green, blue-white — arranged in a perfect ring around an empty central seat, twin suns glowing faint through a high temple window behind them. Along the base, a carved bronze plinth bears "THE COUNCIL OF LIGHTS" in Aurebesh-flavored temple capitals, angular geometric letterforms cut in warm bronze — the ONE piece of text anywhere in the image. Border: the set's own bronze-and-blue temple-pillar frame. Palette: kyber-blue, temple bronze, twin-sun amber.
```

### `starwars_tamna` — Star Wars: The Rule of Two (`assets/titles/starwars_tamna.png`)

*Darth Bane — the DOCTRINAL parent of this set's whole lineage
(Plagueis → Sidious → Vader is a direct chain of the rule Bane himself
instituted); chosen over reusing Plagueis, already this set's own
Unfound, to avoid depicting one seat twice.*

```
Ornate circular medallion, Imperial black-and-red cog relief, photorealistic render, perfectly centered, isolated on white background. Center: Darth Bane, a hooded ancient Sith Lord, holding a dark angular holocron open in both hands, its glowing red interior projecting two small silhouettes standing apart from each other — one master, one apprentice, forever only two — the doctrine that shaped every seat in this set glowing in his own palms. Along the base, a cracked iron plinth bears "THE RULE OF TWO" in Aurebesh-flavored Imperial capitals, angular geometric letterforms cut into black durasteel — the ONE piece of text anywhere in the image. Border: the set's own black-and-red cog frame. Palette: holocron red, durasteel black, hooded-robe charcoal.
```

### `starwars_nova` — Star Wars: The Dyad (`assets/titles/starwars_nova.png`)

*Two hands reaching toward each other across a broken, sparking
lightsaber blade — the owner's own suggested image. Justified in one
line: "Dyad in the Force" is the films' own literal term for Rey/
Kylo's bond, and the broken-and-reforged blade is their bond's own
canonical emblem, so the plate depicts the theme's real name as
directly as the source material already does.*

```
Ornate circular medallion, fused bronze-and-durasteel relief, photorealistic render, perfectly centered, isolated on white background. Center: two bare hands reaching toward each other across a shattered lightsaber blade suspended mid-air between them, the blade's break-point sparking white-hot where the two halves almost touch, one hand lit warm and golden, the other lit cold and silver-blue, neither hand quite closing the last inch of distance. Along the base, a fused plinth bears "THE DYAD" in Aurebesh-flavored fused capitals, each letterform split down the middle, half bronze half durasteel — the ONE piece of text anywhere in the image. Border: the set's own fused bronze-and-cog frame. Palette: warm gold, cold silver-blue, spark-white, blade-steel.
```

### `corporate` — The Corporation: The Boardroom Table (`assets/titles/corporate.png`)

*An empty boardroom, nine chairs, eight marked by a small emblem for
their own seat, the ninth left conspicuously bare — the "every seat's
own emblem" device fused with the Founder's own "ghost seat" language.*

```
Ornate circular medallion, brushed-steel-and-glass corporate seal, engraved relief, photorealistic render, perfectly centered, isolated on white background. Center: an empty boardroom seen from directly above, a long glass-and-steel table ringed by nine chairs, eight of them marked by a small engraved emblem laid on the table before each seat — a heart, a gear, a coin-and-scale, a megaphone-halo, a compass-and-pencil, a chip-and-root-network, a crown at the head — and the ninth chair, at the table's far foot, left conspicuously bare: no emblem, a faint dust-pale outline where a nameplate used to sit. Along the base, a brushed-steel plaque bears "THE CORPORATION" in engraved lanyard-badge sans, clean laser-etched capitals — the ONE piece of text anywhere in the image. Border: a thin brushed-steel ring engraved with a continuous subtle org-chart line-and-node motif. Palette: brushed steel, glass-table blue-grey, warm engraved-gold emblems, one pale dust-grey empty seat.
```

---

## The PROMPT SHEETS round title plates (R8c, written in full — the gap closed 2026-07-22)

The two entries the intro above promised "at the very end" — named and
cross-referenced from their own theme sheets since R8c (2026-07-21),
but never actually written as a fenced generatable body until now (the
exact class of gap this whole canonical-root convention exists to
prevent). Written here, matching every sibling entry's own convention;
each theme sheet keeps its short pointer, never a duplicate.

### `monsters` — Greek Monsters (`assets/titles/monsters.png`)

*Typhon & Echidna, the parents of the roster — father and mother of
monsters whose children now hold the week (Nemean Lion and Cerberus
literal brothers among them) — the "parent, not seat-holder" device
`wow_evil`'s Sargeras and Cyberpunk Power's Soulkiller both borrow from
this plate's own precedent. Night-window register and Greek-key
(meander) border, the same family the seated roster wears, recut as
dark leadwork — never the bronze the Olympian gods' own title plate
wears one file over.*

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep primordial black-and-ember glass, older and darker than any single seat's own window. Center: Typhon and Echidna together at the roster's own root, filling the disc shoulder to shoulder — Typhon a mountain-tall storm-titan with a hundred serpent heads hissing from his shoulders in place of arms, Echidna coiled beside him, a woman above the waist and a great serpent below — both turned protectively inward around a small nest of newly-hatched shapes at their feet: a many-necked serpent-head still small, a lion cub with an already-unmarked golden pelt, a three-headed pup barely able to lift its middle head — the roster's own cast, glimpsed here as children before any of them held a day of the week. Border: leadwork rim carved as a continuous Greek key (meander) band, the same family the seated roster's own borders wear, broken by no single roundel glyph — the parents who begot them all answer to no one day. Along the base, a cracked leadwork plaque bears "GREEK MONSTERS" in weathered bestiary lapidary capitals, the Attic family pitted and claw-scratched — the ONE piece of text anywhere in the image. Palette: primordial black, ember orange, cold serpent-green, one small nest-gold accent.
```

### `chinese_myth` — Chinese Mythology (`assets/titles/chinese_myth.png`)

*The Peach Banquet — the myth-beat that MADE the roster's own Ruler
his Pride: Sun Wukong crashes the gods' own banquet and eats the
peaches of immortality after being denied a seat, the self-taken
title "Great Sage Equal to Heaven" born in this exact moment. Chosen
over "the celestial court panorama" because a banquet stages as ONE
coherent circular scene the way an abstract court cannot. Night-window
register and the theme's OWN cloud-scroll (xiangyun) border in
jade-and-lacquer — deliberately NOT the Greek key, the same
instruction that shapes the seated roster's own borders.*

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep jade-green and lacquer-gold glass, festive and about to be broken. Center: the Peach Banquet in full swing, a long celestial table spread with golden peaches of immortality and untouched place-settings laid for gods who have not yet arrived, and at its head, uninvited, Sun Wukong already seated with peach juice on his chin and three more peaches cradled in one arm — the exact appetite that will crown him Pride itself, caught in the single moment before the gods return and find their own table already raided. Border: leadwork rim carved as a continuous cloud-scroll (xiangyun) band, the same family the seated roster's own borders wear, jade-and-lacquer palette rather than the Greek key, broken by no single roundel glyph — the banquet belongs to no one day. Along the base, a red-lacquer plinth bears "CHINESE MYTHOLOGY" in seal-script flavored capitals, blocky zhuanshu strokes cut into red lacquer — the ONE piece of text anywhere in the image. Palette: jade green, peach gold, red lacquer, one warm stolen-fruit accent.
```

---

## Status

- New sheet (R8c PROMPT SHEETS round, owner item 7, 2026-07-21).
  **Art: 0/24** in the original 24 entries. `assets/titles/**` is NOT a
  data-driven root and no code reads it yet (the wiring is a future
  round) — every one of the 26 paths this family declared (24 here + 2
  named from the monsters/chinese sheets) needed an explicit
  `tests/test_prompt_paths.py` whitelist entry, added that round.
- **R10 GAMING + CORPORATION SHEET WAVE (2026-07-22) added TEN more,
  written in full here** (see "The GAMING + CORPORATION SHEET WAVE
  title plates" section above) — `wow_alliance`, `wow_horde`,
  `wow_evil`, `cyberpunk_gangs`, `cyberpunk_street`, `cyberpunk_power`,
  `starwars_svetla`, `starwars_tamna`, `starwars_nova`, `corporate`.
  **Art: 0/10** for this batch. All ten new paths needed their own
  explicit `tests/test_prompt_paths.py` whitelist entries, added this
  round alongside the nine existing ones.
- **GAP CLOSED 2026-07-22:** `monsters` (Typhon & Echidna) and
  `chinese_myth` (The Peach Banquet) were named and cross-referenced
  from their own theme sheets since R8c but never actually carried a
  fenced generatable prompt body anywhere — the exact "sheet's own
  register-preamble law vs. what's actually written" class of gap this
  sheet-writing round exists to close. Both are now written in full
  above (see "The PROMPT SHEETS round title plates" section). **Art:
  0/2** for this pair. Family total across this file: **0/36** (24 + 10
  + 2) — the whole title-plate family, project-wide, in one place, as
  the canonical root always intended.
- `continents` is deliberately ABSENT from this sheet — it already has
  a real, wired title image (`assets/earth/world.png`,
  `defaults.CONTINENTS_TITLE_IMAGE`) — see the owner's own SKIP
  instruction.
- Verify with `python main.py "research/prompts/titles/theme_title_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner.
