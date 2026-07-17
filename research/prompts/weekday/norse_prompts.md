# Norse Gods — the Aesir Weekday Theme (Planetary + Pantheon, bronze + colored)

The ONE complete Norse prompt sheet — both rosters, both finishes.
**Planetary** is the shipped set (Sól, Máni, Tyr, Odin, Thor, Freya,
Loki, dual Skoll) and predates the prompt-sheet convention entirely.
**Pantheon** is the new roster locked by the owner in
[Pantheon Catalog](../../pantheon_catalog.md) (round four/five,
2026-07-15): Odin, Hel, Thor, Loki, Tyr, Frigg, Freyr, the Odin/the
Wanderer dual, and **Yggdrasil** as the ninth. Generate top to bottom;
REUSE entries need no generation at all.

**⚠ SUPERSEDED — read before generating:** the old "Baldur, Ninth of
the Aesir" plate (bronze + colored) that used to close this file is
RETIRED. The owner's round-four verdict locks **Yggdrasil** as the
Norse ninth in BOTH rosters — Baldur was never rendered (`baldur.png`
and `colored/baldur.png` show no Gemini/ChatGPT mark in `ROSTER.md`,
so nothing is lost) and now lives in the Encyclopedia's
Wider-Pantheon lane instead (his death still opens the Ragnarok
article, told inside Odin's and Hel's entries). **Do not generate a
Baldur ninth plate from this sheet.**

**Border identity:** a bronze ring carved as an interlaced knotwork
band (an endless Norse braid), running clockwise, broken every
quarter turn by a carved rune-stone roundel holding the day's
planetary glyph between the runes — distinct from every other bronze
theme's border (no meander, no hieroglyphs, no paw-prints). This
border identity is shared by BOTH rosters (bronze) — Planetary and
Pantheon plates read as one family on the dial; only the colored
plates trade the bronze ring for a painted knotwork ring, per the
colored register below.

**Style note:** aged bronze relief is the base register because this
is the metal-swap family — gold and silver variants hue-swap the same
warm bronze pixels programmatically, so no separate gold/silver
prompts are needed here.

**House rules — every prompt in this sheet:**
- Circular medallion (bronze) or badge (colored) — never square, never a scene bleeding past the disc.
- Photorealistic render.
- Perfectly centered composition.
- Isolated on a plain white background.
- No text, no watermark, no lettering of any kind anywhere — runes and glyphs are carved symbols, never alphabetic characters.

**Drop dirs** (`assets/weekday/norse/…`; duals nest under each
variant's own `dual/`, matching the code's authoritative convention
in `config/defaults.py` `WEEKDAY_DUAL_FILES` — the colored dual swaps
only the `primary` → `colored` segment, e.g. `primary/dual/Skoll.png`
→ `assets/weekday/norse/colored/dual/Skoll.png`):

```
📁 assets/weekday/norse/
  📁 primary/            Planetary bronze — 7 gods
    📁 dual/              Planetary bronze dual — Skoll
  📁 colored/            Planetary colored — 7 gods + Skoll
    📁 dual/              Planetary colored dual — Skoll
  📁 pantheon/           Pantheon bronze — new figures; REUSE figures point at primary/
    📁 dual/              Pantheon bronze dual — the Wanderer (REUSE, points at primary/Odin.png)
    📁 colored/           Pantheon colored — new figures; REUSE figures point at colored/
      📁 dual/             Pantheon colored dual — the Wanderer (REUSE, points at colored/Odin.png)
```

---

## Planetary — bronze

The Aesir set — Sól, Máni, Tyr, Odin, Thor, Freya, Loki, plus the
Sunday dual Skoll — regenerates all eight plates from the canon in
`Database/symbolism.json` so the owner can drop fresh renders straight
over the existing files. Copied verbatim, unchanged.

**Sunday — Sol** → `assets/weekday/norse/primary/Sol.png`

*She holds the sun up like a lamp for the world, the wolf Skoll
already at her heels — the article's opening image.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Sol in full scale armor, golden hair streaming, holding the blazing sun disc aloft in one raised hand like a lamp for the world, a two-horse chariot (Arvakr and Alsvidr) racing above the waves behind her, the wolf Skoll forever at their heels. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Sun glyph between the runes. No text, no watermark.
```

**Monday — Mani** → `assets/weekday/norse/primary/Mani.png`

*Sol's brother shown twice over — the moon as phase and as whole —
with his own pursuer, the wolf Hati.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Mani, an older god with long silver hair and a braided beard, bronze scale armor under a night-blue cloak spangled with tiny stars, a silver crescent raised in his right hand, a silver orb marked with its own crescent cradled in his left, his chariot riding above the waves behind him with the wolf Hati at its heels. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Moon crescent glyph between the runes. No text, no watermark.
```

**Tuesday — Tyr** → `assets/weekday/norse/primary/Tyr.png`

*The stump held high and unhidden — the honest price paid at Fenrir's
binding, per the article.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Tyr raising his right arm like a banner, the arm ending at the wrist in a bandage-wrapped, blood-streaked stump, a snarling wolf's head carved at his shoulder, a bloodied sword gripped point-down in his remaining hand, runes arcing through the field around him. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Mars glyph between the runes. No text, no watermark.
```

**Wednesday — Odin** → `assets/weekday/norse/primary/Odin.png`

*Everything he has, he bought: the traded eye, the runes won by
hanging, the ravens Thought and Memory.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Odin the wanderer-sage, an eyepatch over the eye he traded for wisdom, the spear Gungnir gripped in his fist with runes glowing faintly along the shaft, his ravens Huginn and Muninn perched one on the spear-arm and one at his shoulder, a great bare tree rising behind him. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Mercury glyph between the runes. No text, no watermark.
```

**Thursday — Thor** → `assets/weekday/norse/primary/Thor.png`

*Not a portrait of majesty but of labor — the whole relief caught
mid-blow, per the article.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Thor in a winged helmet with a braided beard, both hands locked on the short haft of Mjolnir, the rune-carved hammer swept across his body mid-blow, knees bent in a wide braced stance, the girdle of might at his waist, his cape flaring behind him. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Jupiter glyph between the runes. No text, no watermark.
```

**Friday — Freya** → `assets/weekday/norse/primary/Freya.png`

*Double-armed: the sword the Roman Venus hides, kept in the same
hands as the feather-cloak.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Freya standing double-armed, a raised sword in one hand and a single golden falcon feather from her feather-cloak in the other, a winged diadem on her brow, the amber-stoned Brisingamen at her throat, a boar and the prow of a longship at her side. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Venus glyph between the runes. No text, no watermark.
```

**Saturday — Loki** → `assets/weekday/norse/primary/Loki.png`

*The only smiling god on the dial, every object at his feet either his
invention or his sentence.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Loki grinning, red-gold braids framing the smirk, one hand gripping a spear whose head glows poison-green above green-lit runes, the other lifting a golden woven net, a serpent coiling over a small fire at his feet and a wolf snarling at the lower edge. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Saturn glyph between the runes. No text, no watermark.
```

**Sunday (dual) — Skoll** → `assets/weekday/norse/primary/dual/Skoll.png`

*"No mythology stages Glory and Eclipse more honestly: Skoll catches
her at Ragnarok — the Eclipse foretold — yet the Eddas promise her
daughter drives on."*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: the great wolf Skoll leaping to seize the blazing sun disc in his jaws, Sol's chariot and her horses Arvakr and Alsvidr faltering behind him, the disc darkening into a black orb rimmed by a thin gilded corona as his teeth close on it — Ragnarok's promised eclipse, the same road her daughter is sworn to ride again. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Sun glyph between the runes. No text, no watermark.
```

---

## Planetary — colored

Moved here verbatim from `colored_badge_prompts.md`'s "Norse gods —
painted North, aurora accents" section — these are fresh full-color
paintings of the same compositions, not recolors of the bronze
plates. Plus the ONE plate that section never had: **the colored
Skoll dual**, missing from every source until now (the owner's
coverage complaint) — written fresh in the same register below.

**Sunday — Sol** → `assets/weekday/norse/colored/Sol.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Sol the Norse sun goddess driving her sun chariot across the sky, golden hair blazing like fire, the bright sun disc behind her, the shadowy wolf Skoll chasing at the horizon; glossy amber-gold field with aurora streaks. Border: carved knotwork ring painted gold and red with small roundels bearing golden sun wheels. Colors: blazing gold, amber, aurora green, wolf gray.
```

**Monday — Mani** → `assets/weekday/norse/colored/Mani.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Mani the Norse moon god steering the pale moon chariot through a star-strewn night, silver-white hair and cloak, the full moon glowing behind him, the wolf Hati lurking below; glossy deep-blue night field with green aurora curtains. Border: carved knotwork ring painted silver and blue with small roundels bearing silver crescents. Colors: silver, deep night blue, aurora green, white.
```

**Tuesday — Tyr** → `assets/weekday/norse/colored/Tyr.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Tyr the one-handed Norse god of war and oaths in scale armor and a red cloak, sword raised in his left hand, his right arm ending at the wrist, the great wolf Fenrir bound in chains behind him; glossy ember-orange field. Border: carved knotwork ring painted iron gray and red with small roundels bearing the Tiwaz rune. Colors: ember orange, iron gray, blood red, chain silver.
```

**Wednesday — Odin** → `assets/weekday/norse/colored/Odin.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Odin the wanderer-sage with a wide-brimmed hat shadowing his one eye, deep blue cloak, the spear Gungnir with glowing runes, ravens Huginn and Muninn on his shoulders, the world-tree Yggdrasil faint behind; glossy royal-purple twilight field. Border: carved knotwork ring painted purple and silver with small roundels bearing the Ansuz rune. Colors: royal purple, deep blue, raven black, rune silver.
```

**Thursday — Thor** → `assets/weekday/norse/colored/Thor.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Thor red-bearded and mighty, swinging the hammer Mjolnir wreathed in white-blue lightning, his belt of strength glowing, storm clouds and rain behind, two goats at his feet; glossy golden-yellow field split by lightning. Border: carved knotwork ring painted gold and storm blue with small roundels bearing hammer emblems. Colors: golden yellow, storm blue, lightning white, red beard.
```

**Friday — Freya** → `assets/weekday/norse/colored/Freya.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Freya the Norse goddess of love and war, golden hair braided, wearing the amber necklace Brisingamen glowing at her throat, a falcon-feather cloak over one shoulder, two gray cats drawing her chariot; glossy warm red field with golden sparks. Border: carved knotwork ring painted rose gold and red with small roundels bearing amber gems. Colors: warm red, amber gold, rose, cat gray.
```

**Saturday — Loki** → `assets/weekday/norse/colored/Loki.png`
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Loki the trickster half-smiling, sharp-featured in green and black, small flames dancing between his fingers, a serpent coiling around his arm, faint chains at the edge hinting at his binding; glossy emerald-green field with smoke curls. Border: carved knotwork ring painted green and dark gold with small roundels bearing coiled serpents. Colors: emerald green, flame orange, black, dark gold.
```

**Sunday (dual) — Skoll** → `assets/weekday/norse/colored/dual/Skoll.png` — **NEW, the missing plate**

*The owner's coverage complaint, closed: no colored Skoll prompt
existed in this register anywhere before this rewrite (see the
report for the two near-miss prompts found elsewhere under a
different style and a non-canonical path).*

```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: the great shadow-wolf Skoll leaping to seize the blazing sun disc in his jaws, Sol's chariot and her horses Arvakr and Alsvidr faltering behind him, the disc darkening into a black orb rimmed by a thin gold corona as his teeth close on it — Ragnarok's promised eclipse, the same road her daughter is sworn to ride again; glossy dusk-amber field collapsing into black at the wolf's jaws, aurora streaks bleeding out from the dying corona. Border: carved knotwork ring painted wolf-gray and gold with small roundels bearing golden sun wheels dimmed to a thin ring. Colors: wolf gray, dying gold, eclipse black, aurora violet.
```

---

## Pantheon — bronze

The roster the owner locked by REAL rank and role, bound to the seat
archetypes (see [Pantheon Catalog](../../pantheon_catalog.md), round
four/five, 2026-07-15): Odin, Hel, Thor, Loki, Tyr, Frigg, Freyr, the
Odin/the Wanderer dual, Yggdrasil the ninth. Three seats REUSE
existing Planetary art on a DIFFERENT weekday (no new plate, no new
generation) — read the day-shift note on each before skipping it.

**Sunday — Odin the Allfather** → `assets/weekday/norse/pantheon/Odin.png` — **NEW**

*The sovereign face, not the wanderer: enthroned on the high seat
that sees into every world, Pride that hanged itself on the tree for
wisdom now sitting in judgment rather than walking the road — deliberately
distinct from the Planetary Wednesday plate (which stays the standing
wanderer-sage). His shadow face at the dual below IS that Wednesday
plate, reused.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Odin the Allfather enthroned upon Hlidskjalf, the high seat that sees into every world, a heavy cloak thrown over gilded armor, the empty socket of his traded eye left bare and unhidden beneath a crown rather than a wanderer's hood, the spear Gungnir held upright like a scepter of rule at his shoulder, his ravens Huginn and Muninn perched one on each armrest of the throne, the wolves Geri and Freki lying watchful at his feet. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Sun glyph between the runes. No text, no watermark.
```

**Monday — Hel** → `assets/weekday/norse/pantheon/Hel.png` — **NEW**

*The half-dead queen who keeps the stillest Calm on the whole dial —
Monday's Fear face given a throne rather than a monster.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Hel enthroned in perfect stillness at the edge of Helheim, her body split exactly down the middle — one side a fair young queen in unmarked flesh under a plain crown, the other a rotted blue-black corpse down to bone — both halves seated with the same unmoving calm, her hall Eljudnir rising behind her out of cold mist, the hound Garm chained faint at the gate in the low distance, a ledger of the dead's names left open and untouched on her lap. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Moon crescent glyph between the runes. No text, no watermark.
```

**Tuesday — Thor** → REUSE `primary/Thor.png`

*No new plate.* Thor moves from the Planetary Thursday (jupiter) seat
to the Pantheon Tuesday (mars) seat — the same fighter the world
knows, reread for Courage and Zeal instead of Generosity. Point the
Pantheon Tuesday slot at the existing `assets/weekday/norse/primary/Thor.png`.

**Wednesday — Loki** → REUSE `primary/Loki.png`

*No new plate.* Loki moves from the Planetary Saturday (saturn) seat
to the Pantheon Wednesday (mercury) seat — the cunning purple mind,
Greed/trickery as the seat's own vice. Point the Pantheon Wednesday
slot at the existing `assets/weekday/norse/primary/Loki.png`.

**Thursday — Tyr** → REUSE `primary/Tyr.png`

*No new plate.* Tyr moves from the Planetary Tuesday (mars) seat to
the Pantheon Thursday (jupiter) seat — the Thursday reading: the hand
GIVEN into Fenrir's mouth is Generosity by sacrifice, the priest of
oaths and law. Point the Pantheon Thursday slot at the existing
`assets/weekday/norse/primary/Tyr.png`.

**Friday — Frigg** → `assets/weekday/norse/pantheon/Frigg.png` — **NEW**

*Marriage and devotion — the mother who wove oaths around her son;
Love as devotion rather than passion (Freya keeps the Planetary
Friday passion-reading unchanged), her grief the seat's shadow.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Frigg standing composed and regal, a ring of household keys at her belt, a distaff spinning pale cloud-thread lifted in one hand, her other hand pressed flat over her heart, a single sprig of mistletoe resting apart in the lower field — the one oath she never thought to ask — her seat Hlidskjalf glimpsed empty behind her, hinting at everything she sees and cannot change. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Venus glyph between the runes. No text, no watermark.
```

**Saturday — Freyr** → `assets/weekday/norse/pantheon/Freyr.png` — **NEW**

*THE harvest god — green Patience, the field's Renewal, ending the
week the way Demeter does for Greece.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Freyr standing in a ripened field, the golden-bristled boar Gullinbursti at his side gleaming like struck sunlight, a great sheaf of wheat cradled in one arm, a stag's antler gripped in the other hand in place of the sword he gave away for love, his folded ship Skidbladnir resting small and bright at his feet, ripe grain bowing in every direction around him. Border: bronze ring carved as an interlaced knotwork band, broken by four rune-stone roundels, each holding the Saturn glyph between the runes. No text, no watermark.
```

**Sunday (dual) — Odin the Wanderer** → REUSE `primary/Odin.png`

*No new plate.* The one-eyed beggar-sage at the door is the Servant
face of the same Allfather body seated above — "the cleanest dual
structure in the whole catalog" (the owner's own words). Point the
Pantheon dual slot at the existing `assets/weekday/norse/primary/Odin.png`
(the Planetary Wednesday plate, unchanged).

**Ninth (both rosters) — Yggdrasil** → `assets/weekday/norse/pantheon/Yggdrasil.png` — **NEW**

*Replaces the old Baldur ninth entirely (see the SUPERSEDED note at
the top of this file). Doctrine: the Ninth is either the Excluded One
or the UNION of the week's poles, and the Union must never rank below
the seated figures. Yggdrasil is the Union register — the world-tree
HOLDS all nine worlds, Asgard's hall and Hel's own realm on one trunk
— so its border departs from every other plate's "bare, no day is
his" pattern: it wears ALL SEVEN glyphs, because every day answers to
the tree, not because none does.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. Center: Yggdrasil the great world-tree filling the whole disc, three vast roots plunging into three separate wells at the base, nine worlds nested among its branches and roots in relief — golden Asgard's hall gleaming at the crown, Hel's cold half-lit realm carved into the deepest root, Midgard's ring of land at the trunk's waist — an eagle perched at the topmost branch, the serpent Nidhogg coiled at the deepest root, the squirrel Ratatoskr running the bark between them. Border: bronze ring carved as an interlaced knotwork band, broken not by four but by all seven planetary glyphs set in a continuous rune-stone frieze running root to crown — no single day claims the tree; every day answers to it. No text, no watermark.
```

---

## Pantheon — colored

New colored paintings for the five genuinely new Pantheon figures, in
the same "painted North, aurora accents" register as the Planetary
colored set. The four REUSE seats point at their existing colored
files — no new generation.

**Sunday — Odin the Allfather** → `assets/weekday/norse/pantheon/colored/Odin.png` — **NEW**
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Odin the Allfather enthroned upon Hlidskjalf in deep gold and midnight blue, the bare socket of his traded eye left unhidden beneath a low crown, the spear Gungnir held upright as a scepter with faintly glowing runes, his ravens Huginn and Muninn perched on the throne's armrests, the wolves Geri and Freki lying watchful at his feet; glossy midnight-blue field with pale gold aurora streaks crowning the throne. Border: carved knotwork ring painted gold and deep blue with small roundels bearing golden sun wheels. Colors: royal gold, midnight blue, raven black, aurora pale-green.
```

**Monday — Hel** → `assets/weekday/norse/pantheon/colored/Hel.png` — **NEW**
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Hel enthroned at the edge of Helheim, her body split exactly down the middle — one side a fair queen in pale living skin, the other a rotted blue-black corpse to the bone — both halves seated in the same unmoving calm, her hall Eljudnir rising in cold mist behind her, the hound Garm chained faint at the gate; glossy ice-blue field fading to graveyard black on her dead side. Border: carved knotwork ring painted half silver, half corpse-blue with small roundels bearing silver crescents. Colors: pale living skin, corpse blue-black, ice blue, bone white.
```

**Tuesday — Thor** → REUSE `assets/weekday/norse/colored/Thor.png`

*No new plate.* Same day-shift as the bronze note above — point at
`assets/weekday/norse/colored/Thor.png`.

**Wednesday — Loki** → REUSE `assets/weekday/norse/colored/Loki.png`

*No new plate.* Point at `assets/weekday/norse/colored/Loki.png`.

**Thursday — Tyr** → REUSE `assets/weekday/norse/colored/Tyr.png`

*No new plate.* Point at `assets/weekday/norse/colored/Tyr.png`.

**Friday — Frigg** → `assets/weekday/norse/pantheon/colored/Frigg.png` — **NEW**
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Frigg composed and regal in deep blue-violet robes, a ring of golden household keys at her belt, a distaff spinning pale cloud-thread in one raised hand, her other hand pressed over her heart, a small sprig of mistletoe resting apart in the lower field, her empty seat Hlidskjalf glimpsed faintly behind her; glossy dusk-violet field streaked with soft cloud-white. Border: carved knotwork ring painted violet and gold with small roundels bearing golden keys. Colors: dusk violet, cloud white, warm gold, quiet gray grief.
```

**Saturday — Freyr** → `assets/weekday/norse/pantheon/colored/Freyr.png` — **NEW**
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Freyr standing in a ripened golden field, the boar Gullinbursti gleaming beside him like struck sunlight, a great sheaf of wheat cradled in one arm, a stag's antler raised in the other hand in place of the sword he traded for love, his folded ship Skidbladnir bright and small at his feet; glossy harvest-gold field with warm green undertones. Border: carved knotwork ring painted green and gold with small roundels bearing wheat sheaves. Colors: harvest gold, leaf green, boar-bristle amber, warm earth brown.
```

**Sunday (dual) — Odin the Wanderer** → REUSE `assets/weekday/norse/colored/Odin.png`

*No new plate.* Point at `assets/weekday/norse/colored/Odin.png` (the
Planetary Wednesday colored plate, unchanged).

**Ninth (both rosters) — Yggdrasil** → `assets/weekday/norse/pantheon/colored/Yggdrasil.png` — **NEW**
```
Ornate circular badge, vivid full-color Nordic painted style, photorealistic render, perfectly centered, isolated on white background. Center: Yggdrasil the world-tree filling the whole disc in deep greens and gold, three great roots plunging into three glowing wells, nine worlds glowing faintly among the branches and roots — golden Asgard's hall crowning the highest branch, Hel's cold blue-lit realm glowing in the deepest root, Midgard's green ring at the trunk's waist — an eagle at the crown, the serpent Nidhogg coiled at the root, the squirrel Ratatoskr racing the bark between them; glossy deep-green field with aurora curtains rising behind the crown. Border: carved knotwork ring painted gold and forest green, all seven planetary glyphs woven root to crown in a continuous rune frieze — no single day claims the tree. Colors: deep forest green, aurora green and violet, root-well blue, crown gold.
```

---

## Generation order — run top to bottom

1. **Planetary bronze** (8 plates, already on disk — regenerate only
   to refresh): Sol → Mani → Tyr → Odin → Thor → Freya → Loki → dual Skoll.
2. **Planetary colored** (8 plates, 7 already on disk): Sol → Mani →
   Tyr → Odin → Thor → Freya → Loki → **dual Skoll (the missing plate
   — generate this one; see the report for the path/style
   discrepancy against `sunday_duality.md`)**.
3. **Pantheon bronze — NEW only** (5 plates): Odin the Allfather →
   Hel → Frigg → Freyr → Yggdrasil. Thor/Loki/Tyr/the Wanderer dual
   need no generation — wire the REUSE pointers instead.
4. **Pantheon colored — NEW only** (5 plates): same five figures.
   Thor/Loki/Tyr/the Wanderer dual REUSE their existing colored files.

**Baldur — do not generate.** Superseded by Yggdrasil; see the note
at the top of this file.

Total new art this pass: **11 plates** — 1 (Skoll colored, Planetary)
+ 5 (Pantheon bronze) + 5 (Pantheon colored).
