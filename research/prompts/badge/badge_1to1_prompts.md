# Badge 1:1 Prompts (Gemini) — round-one circular companions for the lancet vitraži

**BADGE SISTEM, round one** (owner DESIGN INSTRUCTIONS.txt, 2026-07-20/
21: "Za svaku sliku koja se crta negdje na kružnici sata... mora da
postoji ASPECT RATIO 1:1 verzija... sve situacije gdje sada imamo
Vitraž koji je HEIGHT:WIDTH 2:1 moramo da napravimo verzije i sa ovim
pravilom gore" — every 2:1 lancet needs a 1:1 circular companion,
feeding the future hover-card LEFT-COLUMN circle beside the tall
lancet, per the owner's own mockup: [HOVER - arch stained glass.png](../../../UV/DESIGN/HOVER%20-%20arch%20stained%20glass.png)).

**Scope — every LANCET figure enumerated from `config/archetypes.py`**
(the CENTER figures — Providence_Eye, Hearth, Seal, Union, Throne —
are already ROUND rose windows, per their own prompt sheets; they need
no companion and are NOT repeated here; the Tetramorph creatures and
the four Evangelists are likewise already SMALL round rondels, also
excluded). Seven families, 38 figures:

| Family | Source sheet | Figures |
|---|---|---|
| Trinity (paint) | [Trinity Prompts](../archetype/trinity_prompts.md) | One_Judge, Devil_Prosecutor, Jesus_Advocate |
| Family (trinity light) | [Family Prompts](../archetype/family_prompts.md) | Child_Dawn, Mother_Heart, Father_Shield |
| Temperaments (seasons paint) | [Temperaments Prompts](../archetype/temperaments_prompts.md) | Sanguine, Choleric, Melancholic, Phlegmatic |
| Persons (prism paint) | [Persons Prompts](../archetype/persons_prompts.md) | One_Love, Michael_Courage, Lucifer_Pride, Devil_Hatred, Judas_Fear, Jesus_Humility |
| One Soul (prism light) | [One Soul Prompts](../archetype/one_soul_prompts.md) | Gratitude, Support, Passion, Tolerance, Trust, Respect |
| Walks (compass paint) | [Walks Prompts](../archetype/walks_prompts.md) | King, Merchant, Soldier, Artist, Wanderer, Scholar, Farmer, Priest |
| Life — Tree register (compass light) | [Life Prompts](../archetype/life_prompts.md) | Unborn, Birth, Childhood, Youth, Maturity, Elder, OldAge, Death |

**Round-one scoping (documented, not a gap):** the compass_light
archetype ships a SECOND image register, Animals (`config.archetypes.
ARCHETYPE_LIFE_REGISTER = "tree"` is the one actually rendered today
— the owner has not wired a user-facing register picker yet). This
round covers the ACTIVE Tree register's 8 figures only; the Animals
register's own 8 badges are a straightforward round-two follow-up if/
when the owner activates that register — same recipe, same scoping
note as the source `life_prompts.md` sheet itself.

**Register:** the SAME house night-window stained-glass family every
lancet above already uses — a badge is not a new look, it is the SAME
figure and palette POURED into a round frame instead of a tall one.
Each entry below condenses its source lancet's OWN center scene,
palette and border motif into ONE round composition (the lancets'
upper-left/upper-right side panels and their 2-3 rim roundels are
folded away — a badge is the headline image alone, not the whole
window). **Every badge keeps its source lancet's exact palette and
border-motif vocabulary** so the two read as one figure, two frames,
never two different characters.

**Drop paths:** `assets/badge/circle/<family>/<Stem>.png` — a NEW
staging root, deliberately NOT nested inside `assets/archetype/`
(the lancets' own home): the hover-card left-column wiring is not
built yet and its final consumer/path is undecided (owner call,
flagged in Status below) — keeping round-one contained under its own
root means relocating it later touches no other family's directory.
`<family>` mirrors the archetype subfolder each figure's LANCET lives
in (`persons`, `family`, `temperaments`, `trinity`, `one_soul`,
`walks`, `life/tree`) so a badge and its lancet are trivially paired
by eye. `assets/badge/` is a SOURCED root — both Gemini and ChatGPT
generate their own circle subtree, exactly like the Scale/Trinity/
Season badges already there.

**House rules carried from every other sheet:** photorealistic
render, isolated background (no transparency-checkerboard artifact),
the circular window shape IS the frame, NO lettering anywhere.

---

## Trinity (paint) — the Courtroom Trio

**One — the Judge** (gold, 12h) → `assets/badge/circle/trinity/One_Judge.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Radiant gold, amber and white glass. Center: the enthroned Judge's face VEILED in pure white radiance, one hand raised in calm verdict, the other resting on a two-pan balance at PERFECT rest — the throne and the balance drawn close and large, filling the circle. Border: gothic leadwork in dark gold, a small balance-at-rest roundel at the top. Palette: radiant gold, amber, white light, dark-gold lead. NO lettering anywhere.
```

**the Devil — the Prosecutor** (red, 20h) → `assets/badge/circle/trinity/Devil_Prosecutor.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Ember-red, gold and black glass. Center: the horned accuser leaning in with a cruel half-smile, one clawed finger pointing down at a small chained figure crouched at the base, ember light throwing his shadow behind him — composition tightened to fill the round frame. Border: twisted thorn-and-rope leadwork in dark bronze-red, a small tipped-scale roundel at the top. Palette: ember red, molten gold, black-iron lead. NO lettering anywhere.
```

**Jesus — the Advocate** (blue, 04h) → `assets/badge/circle/trinity/Jesus_Advocate.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep midnight-blue and silver glass. Center: Jesus standing as defender, one arm shielding a kneeling accused figure, the other hand open and raised in plea, a cold white rose of light behind his head. Border: thorned-vine leadwork in blue-black, a small open-palm roundel at the top. Palette: midnight blue, silver-white light, blue-black lead. NO lettering anywhere.
```

## Family (trinity light) — the Household Triangle

**the Child — the Dawn** (green, 12h) → `assets/badge/circle/family/Child_Dawn.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Fresh spring-green and pale-gold glass, the brightest of the set. Center: a small radiant child-figure at the top of the circle, arms lifting into a break of pale gold, new leaves and first shoots curling up around the feet, everything reaching upward and outward to the rim. Border: young-vine-and-bud leadwork in leaf green, a small sprouting-seedling roundel at the base. Palette: spring green, pale gold, leaf-green lead. NO lettering anywhere.
```

**the Mother — the Heart** (light red, 20h) → `assets/badge/circle/family/Mother_Heart.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Warm light-red, rose and soft coral glass. Center: the mother gathering the household close, one hand cupped over a small child at her breast, a soft warm radiance blooming from her chest like a lamp behind rose glass — the whole composition drawn as one warm embrace filling the circle. Border: braided rose-vine leadwork in warm carmine, a small glowing-heart roundel at the top. Palette: light rose-red, warm coral, soft gold glow, carmine lead. NO lettering anywhere.
```

**the Father — the Shield** (light blue, 04h) → `assets/badge/circle/family/Father_Shield.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Soft light-blue and clear silver glass, calm and cool. Center: the father as pillar, one arm curved shelteringly over a smaller leaning figure, the other hand resting steady on a large kite shield planted at his side — wide-shouldered, at rest but watchful. Border: interlaced oak-and-rivet leadwork in slate blue, a small kite-shield roundel at the top. Palette: light sky-blue, clear silver, cool slate-blue lead. NO lettering anywhere.
```

## Temperaments (seasons paint) — the Four Humors

**Sanguine — the Companion** (spring green `#129412`) → `assets/badge/circle/temperaments/Sanguine.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Fresh spring-green and pale-gold glass, bright and airy. Center: a young laughing figure, arms open, head thrown back mid-laugh, blossom petals and swallows swirling close around in a tight spring-wind ring that fills the circle. Border: blossom-and-swallow leadwork in leaf green, a small swallow roundel at the top. Palette: spring green, blossom pink-white, pale gold, leaf-green lead. NO lettering anywhere.
```

**Choleric — the Commander** (summer yellow `#D9D900`) → `assets/badge/circle/temperaments/Choleric.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Blazing summer-yellow, gold and hot amber glass, fierce and hot. Center: a commanding figure standing forward-leaning under a hard midday sun, one arm thrust out in a decisive order, a hot corona of yellow light burning behind the head and filling the round frame. Border: sunburst-and-flame leadwork in molten gold, a small blazing-sun roundel at the top. Palette: summer yellow, molten gold, hot amber, dark-gold lead. NO lettering anywhere.
```

**Melancholic — the Thinker** (autumn red `#D4330F`) → `assets/badge/circle/temperaments/Melancholic.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep autumn-red, russet and burnt-amber glass, heavy and low light. Center: a bowed figure hunched over a book, chin on hand, brow furrowed in thought, red and rust leaves settling close around in a tight ring. Border: falling-leaf-and-vine leadwork in burnt umber, a small open-book roundel at the top. Palette: autumn red, russet, burnt amber, deep umber lead. NO lettering anywhere.
```

**Phlegmatic — the Peacemaker** (winter blue `#0A70D8`) → `assets/badge/circle/temperaments/Phlegmatic.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Cool winter-blue, ice-white and pale silver glass, still and quiet. Center: a serene figure at perfect rest beside a frozen lake, hands folded, face composed in mild mercy while a snow-wind passes — the calm ring of the circle unbroken. Border: frost-and-icicle leadwork in pale steel-blue, a small frozen-lake roundel at the top. Palette: winter blue, ice white, pale silver, steel-blue lead. NO lettering anywhere.
```

## Persons (prism paint) — Love, Courage, Pride, Hatred, Fear, Humility

**The One — Love** (yellow, 12h) → `assets/badge/circle/persons/One_Love.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Radiant yellow, warm amber and white glass. Center: a tall figure whose face is veiled in pure golden radiance, both arms open in a wide embrace, a single heart of perfectly clear uncolored glass at the chest, the brightest point of the circle. Border: gothic leadwork in dark gold, a small clear-heart roundel at the top. Palette: radiant yellow, warm amber, white light, dark-gold lead, the clear heart the only uncolored glass. NO lettering anywhere.
```

**Michael the Archangel — Courage** (orange, 16h) → `assets/badge/circle/persons/Michael_Courage.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Warm orange, molten gold and bronze glass. Center: the armored archangel, great feathered wings spread wide, a long spear driven down into a dark dragon's coils pinned beneath his feet — the whole victorious stance compressed to fill the round frame, face calm and lifted. Border: banded gothic leadwork in dark bronze, a small upright-sword roundel at the top. Palette: warm orange, molten gold, bronze, black-iron lead. NO lettering anywhere.
```

**Lucifer — Pride** (red, 20h) → `assets/badge/circle/persons/Lucifer_Pride.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Ember-red, molten gold and black glass, hot and ascending. Center: a winged figure of terrible beauty mid-rise, chin lifted above a crown that already slips from his grasp, morning-star radiance breaking around his head. Border: flame-and-falling-feather leadwork in ember red, a small morning-star roundel at the top. Palette: ember red, molten gold, black glass, dark-gold lead. NO lettering anywhere.
```

**the Devil — Hatred** (purple, 24h) → `assets/badge/circle/persons/Devil_Hatred.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep violet, amethyst-purple and blue-black glass, cold and starless. Center: a gaunt horned figure, arms thrown out in two opposite directions — one dragging a small figure down, the other hurling a second outward — cold loathing on his face, two dark veins of purple lead splitting from his heart. Border: knotted thorn leadwork in blue-black, a small broken-heart roundel at the top. Palette: deep violet, amethyst, blue-black, iron lead. NO lettering anywhere.
```

**Judas — Weakness (Fear)** (blue, 04h) → `assets/badge/circle/persons/Judas_Fear.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Midnight-blue, cold silver and iron-gray glass, heavy and turned inward. Center: a hunched figure at the edge of a lamplit doorway he cannot enter, face in shadow, coins slipping through his fingers into the dark, the warm doorway light just out of reach. Border: thorn-and-coin leadwork in cold blue, a small closed-door roundel at the top. Palette: midnight blue, cold silver, iron gray, black-blue lead. NO lettering anywhere.
```

**Jesus — Humility** (green, 08h) → `assets/badge/circle/persons/Jesus_Humility.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep green, sage and soft gold glass, quiet and low-lit. Center: Jesus kneeling low, bent over a basin washing a seated figure's bare feet, his own head bowed lowest of all beneath a pale gold rose of light — the whole gesture drawn close and tight to fill the round frame. Border: living-vine leadwork in deep green, a small basin-and-towel roundel at the top. Palette: deep green, sage, soft gold light, green-black lead. NO lettering anywhere.
```

## One Soul (prism light) — the Six Pillars of a Home

**Gratitude** (green, 12h) → `assets/badge/circle/one_soul/Gratitude.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Warm spring-green, leaf-gold and soft white glass. Center: two figures close together, one turning with both hands cupped open to receive, a young tree growing upward from where their hands meet, its branches filling the circle with light. Border: living-vine leadwork in deep green, a small leafing-branch roundel at the top. Palette: spring green, leaf-gold, soft white light, green-black lead. NO lettering anywhere.
```

**Support** (yellow, 16h) → `assets/badge/circle/one_soul/Support.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Warm yellow, amber and gold glass, the light of a working day. Center: two figures shoulder to shoulder, one bracing the other under a heavy load, both faces set forward into the same task, filling the round frame close together. Border: banded leadwork in dark gold, a small shoulder-taking-a-beam roundel at the top. Palette: warm yellow, amber, gold light, dark-gold lead. NO lettering anywhere.
```

**Passion** (red, 20h) → `assets/badge/circle/one_soul/Passion.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep rose-red, crimson and warm gold glass. Center: two figures drawn close in an embrace, foreheads together, a single living flame rising between their joined hands and filling the circle with warm red light. Border: rose-and-thorn leadwork in dark red, a small joined-flame roundel at the top. Palette: rose-red, crimson, warm gold light, dark-red lead. NO lettering anywhere.
```

**Tolerance** (magenta, 24h) → `assets/badge/circle/one_soul/Tolerance.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Rich magenta, rose-violet and soft silver glass, a warm midnight. Center: two DIFFERENTLY-glazed figures seated close in quiet conversation around a small shared lamp, each keeping its own hue, warm beside cool, filling the round frame. Border: interlaced leadwork in deep violet, a small shared-lamp roundel at the top. Palette: magenta, rose-violet, soft silver light, violet-black lead. NO lettering anywhere.
```

**Trust** (blue, 04h) → `assets/badge/circle/one_soul/Trust.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep midnight-blue, indigo and soft silver glass. Center: two figures asleep side by side in perfect peace, one hand resting loosely over the other, a calm silver moon of light filling the circle above them. Border: still-water leadwork in blue-black, a small calm-sleeping-face roundel at the top. Palette: midnight blue, indigo, soft silver light, blue-black lead. NO lettering anywhere.
```

**Respect** (cyan, 08h) → `assets/badge/circle/one_soul/Respect.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Cool cyan, clear aqua and pale silver glass, the air after rain. Center: two figures standing tall and facing each other across a clean measured space, a pane of perfectly clear glass between them, a slight bow of the head between equals filling the round frame. Border: clean geometric leadwork in slate-cyan, a small clear-open-pane roundel at the top. Palette: cyan, clear aqua, pale silver light, slate-cyan lead. NO lettering anywhere.
```

## Walks (compass paint) — the Eight Estates

**The King** (royal gold, 12h) → `assets/badge/circle/walks/King.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Royal gold and warm amber glass, the brightest of the set. Center: a crowned king enthroned, one hand closed on an orb, the other on a sceptre laid across his knee, filling the circle at the height of his power. Border: crown-and-fleur leadwork in dark gold, a small crown roundel at the top. Palette: royal gold, warm amber, white noon light, dark-gold lead. NO lettering anywhere.
```

**The Merchant** (copper, 15h) → `assets/badge/circle/walks/Merchant.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Warm copper, bronze and burnt-orange glass. Center: a merchant weighing coins on a small two-pan hand-scale, a ledger open at his elbow, filling the round frame under a slanting afternoon light. Border: coin-and-knot leadwork in dark bronze, a small stacked-coin roundel at the top. Palette: copper, bronze, burnt orange, dark-bronze lead. NO lettering anywhere.
```

**The Soldier** (iron-blood crimson, 18h) → `assets/badge/circle/walks/Soldier.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Iron-grey and deep blood-crimson glass, cold steel against warm blood. Center: an armoured soldier standing guard, spear grounded, shield at his side, helm on, the last red light of sunset burning along the edge of his blade, filling the circle. Border: rivet-and-chain leadwork in dark iron, a small sword roundel at the top. Palette: iron grey, blood crimson, sunset red, dark-iron lead. NO lettering anywhere.
```

**The Artist** (stage velvet violet, 21h) → `assets/badge/circle/walks/Artist.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep stage-velvet violet and purple glass, warm footlight glow from below. Center: an artist mid-performance, one hand raised in a gesture of song, a mask held or worn, velvet curtains drawn back close around, filling the round frame. Border: vine-and-lyre leadwork in dark violet, a small theatre-mask roundel at the top. Palette: stage-velvet violet, deep purple, warm footlight gold, dark-violet lead. NO lettering anywhere.
```

**The Wanderer** (road-dust indigo-charcoal, 24h) → `assets/badge/circle/walks/Wanderer.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Road-dust indigo and charcoal glass, the darkest of the set, only starlight and a small lantern for warmth. Center: a hooded wanderer walking with a staff in hand, a small pack on his back, a lantern lighting the close ring of road ahead. Border: knot-and-thorn leadwork in charcoal-indigo, a small pilgrim's-staff roundel at the top. Palette: indigo, charcoal, cold starlight silver, dark charcoal lead. NO lettering anywhere.
```

**The Scholar** (lamplit ink blue, 03h) → `assets/badge/circle/walks/Scholar.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Lamplit ink-blue and deep midnight-blue glass, a single warm lamp the only bright note. Center: a scholar bent over an open book, a candle burning beside a stack of tomes, quill in hand, warm lamplight pooling gold across the cold blue circle. Border: quill-and-scroll leadwork in dark blue, a small open-book roundel at the top. Palette: ink blue, midnight blue, warm lamp gold, dark-blue lead. NO lettering anywhere.
```

**The Farmer** (field green, 06h) → `assets/badge/circle/walks/Farmer.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Field-green and fresh earth-brown glass, pale rose dawn light along the top. Center: a farmer at first light, both hands on the handles of a plough behind an ox, breaking dark soil as rose-gold dawn washes across the round frame. Border: wheat-and-vine leadwork in dark green, a small plough roundel at the top. Palette: field green, earth brown, dawn rose-gold, dark-green lead. NO lettering anywhere.
```

**The Priest** (alb ivory, 09h) → `assets/badge/circle/walks/Priest.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Alb-ivory, cream and soft white glass, clear morning light. Center: a priest in a white alb, one hand raised in blessing, the other on an open sacred book, a small bell beside it, filling the round frame with clear morning light. Border: cross-and-lily leadwork in pale silver-grey, a small hand-bell roundel at the top. Palette: alb ivory, cream, soft white, pale silver-grey lead. NO lettering anywhere.
```

## Life — Tree register (compass light) — the Eight Ages

**the Unborn — the seed** (predawn mist `#8FA8C8`, 03h) → `assets/badge/circle/life/tree/Unborn.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Predawn misty blue-grey glass, the coldest and dimmest of the eight. Center: a single acorn seed resting in dark turned soil, its first pale root just reaching down, filling the circle underground and waiting, a faint blue mist along the top. Border: root-and-vine leadwork in dark blue-grey, a small acorn roundel at the top. Palette: predawn mist blue-grey, dark soil brown, faint silver, dark blue-grey lead. NO lettering anywhere.
```

**Birth — the sprout** (pale rose `#FFD9CC`, 06h) → `assets/badge/circle/life/tree/Birth.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Pale rose and soft dawn-pink glass, the first warm light. Center: a tender green sprout breaking the soil, two first leaves unfolding, the cracked acorn shell at its base, rose-gold sunrise washing across the round frame. Border: leaf-and-shoot leadwork in soft rose-grey, a small two-leaf-sprout roundel at the top. Palette: pale rose, dawn pink, tender green, earth brown, rose-grey lead. NO lettering anywhere.
```

**Childhood — the sapling** (spring green `#7CE577`, 09h) → `assets/badge/circle/life/tree/Childhood.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Fresh spring-green glass, bright clear morning light. Center: a slender young sapling oak with a first spread of small bright-green leaves, growing eagerly upward, filling the round frame with quick young growth. Border: leaf-and-branch leadwork in dark green, a small young-leaf roundel at the top. Palette: spring green, bright leaf green, clear morning light, dark-green lead. NO lettering anywhere.
```

**Youth — the blossoming crown** (sun yellow `#FFE800`, 12h) → `assets/badge/circle/life/tree/Youth.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Radiant sun-yellow and gold glass, the brightest of the eight, noon light at its zenith. Center: a young oak in full blossom, its crown covered in fresh flowers and vivid new leaves, standing strong and radiant, filling the circle with bloom and promise. Border: blossom-and-leaf leadwork in dark gold, a small open-blossom roundel at the top. Palette: sun yellow, gold, blossom white, fresh green, dark-gold lead. NO lettering anywhere.
```

**Maturity — the full crown** (amber `#FFB400`, 15h) → `assets/badge/circle/life/tree/Maturity.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep amber and warm gold glass, the afternoon of the year. Center: a fully-grown oak at its widest and strongest, a broad dense crown of dark summer-green leaves heavy with shade, its trunk thick and settled, filling the round frame at the height of its strength. Border: leaf-and-acorn leadwork in warm amber, a small full-crown roundel at the top. Palette: amber, warm gold, deep summer green, dark-amber lead. NO lettering anywhere.
```

**the Elder — the fruited crown** (ember `#FF6A3C`, 18h) → `assets/badge/circle/life/tree/Elder.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Deep ember-orange and russet glass, the harvest light of a life. Center: a broad old oak heavy with ripe acorns among its first turning leaves, branches bowed with the weight of what it has borne, filling the circle at the harvest of its own crown. Border: acorn-and-leaf leadwork in dark ember, a small hanging-acorn-cluster roundel at the top. Palette: ember orange, russet, ripe-acorn brown, dark-ember lead. NO lettering anywhere.
```

**Old age — the leaf-fall** (dusk violet `#9C6BD4`, 21h) → `assets/badge/circle/life/tree/OldAge.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Dusk violet and soft grey-lavender glass, the evening of the year. Center: an aged oak, its crown thinned and half-bare, a slow scatter of its last violet-gold leaves falling around a gnarled, still-standing trunk that fills the round frame with quiet dignity. Border: bare-branch leadwork in dusk violet, a small falling-leaf roundel at the top. Palette: dusk violet, grey-lavender, fading gold, dark-violet lead. NO lettering anywhere.
```

**Death — the bare tree** (moonlight silver `#C8D7F0`, 24h) → `assets/badge/circle/life/tree/Death.png`

```
ROUND stained-glass badge medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. Moonlight silver and deep midnight-blue glass — never black; light finds the Moon even here. Center: a completely bare old oak, every branch stripped, standing still and silvered under a calm full moon that fills the circle with cool light, the tree's own silhouette the whole subject. Border: bare-root leadwork in silver-blue, a small full-moon roundel at the top. Palette: moonlight silver, midnight blue, pale silver-white, dark-silver lead. NO lettering anywhere.
```

---

## Status

- New sheet (BADGE SISTEM round one, owner 2026-07-20/21). 38 figures
  enumerated from `config.archetypes.ARCHETYPES` — every LANCET seat
  across all seven archetype families (Trinity, Family, Temperaments,
  Persons, One Soul, Walks, Life-Tree); the five CENTER rosettes and
  the already-round Tetramorph/Evangelist rondels are correctly
  excluded (see the Scope note above). NONE generated yet on either
  source.
- **Wiring is UNDECIDED (owner call, DO NOT invent further):** these
  circles feed a FUTURE hover-card left-column layout per the owner's
  own mockup; no code reads `assets/badge/circle/**` yet. Whitelisted
  in `tests/test_prompt_paths.py` the same way the row2 rondels and
  the Almanac month medallions already are — art prepared ahead of the
  wiring decision, not a lint gap.
- The Animals register's own 8 Life badges (compass_light's alternate,
  non-default register) are a round-two follow-up, scoped out of this
  sheet per the note under Scope above.
- Verify with `python main.py "research/prompts/badge/badge_1to1_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner
  (38 images expected).
