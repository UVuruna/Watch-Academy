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

## Cross-referenced (written in their own theme sheets, not here)

- **`monsters` — Greek Monsters** → `assets/titles/monsters.png`. Brief:
  Typhon & Echidna, the parents of the roster, in
  [Greek Monsters Prompts](../monsters/greek_monsters_prompts.md)'s own
  "Cross-reference" section.
- **`chinese_myth` — Chinese Mythology** → `assets/titles/chinese_myth.png`.
  Brief: The Peach Banquet, in
  [Chinese Myth Prompts](../chinese/chinese_myth_prompts.md)'s own
  "Cross-reference" section.

---

## Status

- New sheet (R8c PROMPT SHEETS round, owner item 7, 2026-07-21).
  **Art: 0/24** in this file; the 2 cross-referenced plates are tracked
  in their own sheets' Status sections. `assets/titles/**` is NOT a
  data-driven root and no code reads it yet (the wiring is a future
  round) — every one of the 26 paths this family declares (24 here + 2
  cross-referenced) needs an explicit `tests/test_prompt_paths.py`
  whitelist entry, added this round.
- `continents` is deliberately ABSENT from this sheet — it already has
  a real, wired title image (`assets/earth/world.png`,
  `defaults.CONTINENTS_TITLE_IMAGE`) — see the owner's own SKIP
  instruction.
- Verify with `python main.py "research/prompts/titles/theme_title_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner.
