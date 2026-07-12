# Sunday Duality — Servant Companion + Cross-Theme Survey

Sunday is the dial's one dual day: an angel on one shoulder, a devil on
the other, one figure with two faces. In Professions this is already
named in code — `config/defaults.py` gives the Sunday body the display
name **"Ruler · Servant"** — and the Ruler's own article
(`Database/symbolism.json` → `articles/profession/sun`) states it
outright:

> "The canon makes him DOUBLE — the servant-king, black and white in
> one figure, the dial's own yin-yang. As ruler he practices Justice
> and is stalked by Pride; as servant he practices Humility and is
> stalked by Servility, the bent spine that serves the throne instead
> of the truth."

A Servant companion image already has a precedent in this repo: the
**Humility (Sunday — Servant face)** badge in
[Virtue, Sin and Mood Prompts](virtue_sin_mood_prompts.md) describes
"the same king's Servant face, the crown lifted from his own head and
held low in both hands, eyes downcast, a plain dark robe replacing
royal dress, one bare foot resting in a basin of water." The two
prompts below reuse that exact iconography — crown surrendered, eyes
down, bare foot in a basin — so the Servant reads as the same
established figure across both art sets, just rendered in the
Professions medallion style instead of the allegorical-badge style.

---

## 1. Servant.png — bronze plate (matches Ruler.png exactly)

House style, read off `assets/weekday/profession/Ruler.png`,
`Soldier.png`, `Priest.png` and `Merchant.png`: a weathered
bronze/antique-gold sculptural relief figure standing on a dark
cracked-slate stone background with motifs specific to the calling
ghosted faintly behind it (eagles for the Ruler); a double-ring
border — an outer thin band of foliage/vine scrollwork and an inner
band of interlocking Celtic knotwork — studded with small bronze
roundels carrying a calling-specific emblem (crowns for the Ruler) and
single rune-like glyphs at the four cardinal points; no bright colors
anywhere, pure weathered bronze/gold/slate-gray.

Drop at `assets/weekday/profession/Servant.png`.

```
Circular bronze/antique-gold sculptural relief medallion on a dark cracked-slate stone background, photorealistic render, perfectly centered, isolated on transparent background — same weathered bronze relief finish, stone texture and lighting as Ruler.png and the rest of the Profession set. Center: the Ruler's Servant face — the same bearded king, standing before his own empty throne, crown lifted from his head and held low in both hands, eyes downcast, the ermine-trimmed royal robe replaced by a plain rope-belted tunic, one bare foot resting in a bronze basin of water at the foot of the throne where the eagle-blazoned shield stood in the Ruler plate; the same imperial eagles are engraved faintly into the stone behind him, wings folded low instead of raised. Border: identical double-ring Celtic knotwork to Ruler.png with lion supporters and rune-like glyphs at the four cardinal points, but the crown roundels are replaced with small bronze roundels bearing a basin-and-towel emblem. Palette: dark antique bronze, muted gold, weathered slate gray only — no bright colors, same matte sculptural metal finish and cracked-stone texture as the rest of the bronze Profession set.
```

## 2. colored/Servant.png — colored house style (matches colored/Ruler.png)

House style from [Colored Badge Prompts](colored_badge_prompts.md):
"Ornate circular badge, vivid full-color guild-crest style" with the
day's dial-arm color dominant — Ruler is white-gold. The Servant stays
in the SAME white-gold family (they are one figure, one color) but
reads cooler and quieter: dawn light instead of noon blaze, exactly
the "black and white in one body" the canon text names.

Drop at `assets/weekday/profession/colored/Servant.png`.

```
Ornate circular badge, vivid full-color guild-crest style, photorealistic render, perfectly centered, isolated on white background. Center: the Ruler's Servant face kneeling before his own empty golden throne, the crown lifted from his own head and held low in both hands, eyes downcast, the ermine-and-gold robe replaced by a plain ivory-white tunic with a simple rope belt, one bare foot resting in a golden basin of water; a soft, low dawn-grey glow behind him instead of a blazing halo — the muted, quiet twin of the Ruler's radiant noon field, same white-gold family read cooler and lower. Border: polished gold ring with small white-enamel roundels bearing a basin-and-towel emblem (echoing the Ruler badge's crown roundels), laurel scrollwork between them. Colors: white and gold dominant — same family as the Ruler badge — with cool dawn-grey accents in place of its warm sunrise-orange.
```

---

## 3. Legend/hover concept — showing both plates on Sunday

Grounded in the actual mechanism (`render/compositor.py`): every
weekday hover is one block of HTML built by `_article_html()` and
shown in `LegendPopup` (`app/legend_popup.py`), a `QLabel` in
`Qt.TextFormat.RichText` — a `QTextDocument` subset that already
supports basic `<table>` markup, not just a single `<img>`. Today
`_weekday_tooltip()` passes ONE `image` path into `_article_html()`;
for `body == "sun"` it would pass a PAIR instead.

**Layout** — a two-column row above the shared title, each column its
own portrait + caption, divided by a small centered glyph so the pair
reads as one duality rather than two unrelated pictures:

```
┌───────────────┬───┬───────────────┐
│   Ruler.png    │ ⚖ │  Servant.png   │
│    "Ruler"     │   │   "Servant"    │
└───────────────┴───┴───────────────┘
        Ruler · Servant                 <- existing display name, unchanged
   Thursday... (only on the active day)
   [ the base article + active variant — already narrates both faces ]
```

- The divider glyph is the dial's own yin-yang shorthand already named
  in the Ruler article ("the dial's own yin-yang") — a small ☯ or a
  vertical hairline rule both read fine in Qt rich text; ☯ is more
  legible at hover size.
- Caption color continues the existing `accents=defaults.BODY_ACCENT_HUES[body]`
  mechanism: "Ruler" in warm gold, "Servant" in cool silver/gray — no
  new plumbing, just two `<span style='color:...'>` labels next to
  captions that don't exist for any other body today.
- The shared title stays exactly what it already is —
  `defaults.WEEKDAY_THEME_NAMES[...]["sun"]` already resolves to
  "Ruler · Servant" — so no new string is needed there.
- Every other body keeps the single-image path untouched; this is a
  `body == "sun"` branch inside `_weekday_tooltip()`/`_article_html()`,
  not a redesign of the popup.
- The mechanism generalizes for free to any OTHER theme that grows a
  second Sunday plate (see the survey below) — the branch keys off
  `body == "sun"`, not off the Professions theme specifically, so
  Egypt/Norse/Japan/etc. get the same two-portrait hover the day their
  art lands.

---

## 4. Open invitation — survey of the other 10 themes

Every theme's own Sunday article ALREADY narrates the "center is
DOUBLE" duality in its own mythology's terms — the quotes below are
lifted straight from `Database/symbolism.json`. Ten themes checked
(`planet_signs` and `planets` share one article set and are listed
together); `profession` is the assigned item above and isn't repeated.

| Theme | Existing Sunday figure | Proposed second figure | Verdict |
|---|---|---|---|
| Egypt | Ra-Horakhty, falcon-headed, day barque (`ra.png`) | Afu-Ra, ram-headed night form, towed through the Duat fighting Apophis | **Canon-strong** |
| Norse | Sól, sun held aloft, chariot racing the wolf (`Sol.png`) | Skoll the wolf catching the sun-disc — the Eclipse foretold | **Canon-strong** |
| Japan | Amaterasu's radiant disc + torii (`nichiyobi.png`) | The sealed boulder of Ama-no-Iwato, the mirror's last glint | **Canon-strong** |
| Christianity (religion) | Cross + Chi-Rho on black stone (`christianity.png`) | The washbasin and towel, staff and loosened crown of thorns | **Canon-strong** — but see the REMAP note below: since 2026-07-12 the religion theme's SUNDAY entity is Freemasonry; the washbasin stays as Christianity's own two-faces pair for its new Friday |
| Mithraism (religion_alt) | The tauroctony, Sol blazing above the cave (`mithraism.png`) | Pater enthroned at the cave banquet, served by a masked Corax | **Canon-strong** |
| Alchemy | Refined gold — ingots, nuggets, wire in a solar corona (`gold.png`) | The same gold unrefined — a raw vein in dark quartz, corona still buried | **Canon-strong** |
| Greek | Helios driving the quadriga (`Helios.png`) | Phaethon losing control of that same chariot — the scorched sky | **Canon-strong** |
| Slavic | Young Dažbog, radiant giver, horn of plenty (`dazbog.png`) | Old gray Dažbog, winter elder, near-empty horn, banked corona | **Canon-strong** |
| Planets | The physical Sun — plasma sphere, no personification (`sun.png`) | A darkened/eclipsed sun disc — no distinct second FIGURE, just the same disc dimmed | Stretch |
| Planet signs | Same article as Planets, glyph-style art | An eclipsed-sun glyph — same limitation as Planets, and thinner still since the set is minimal glyphs, not full scenes | Stretch |

The eight canon-strong themes all have the pairing spelled out in
their own article prose — none of this is invented; each quote below
is the line that licenses the prompt under it.

### Greek — Helios / Phaethon

> "Phaethon's day tells the rest — the chariot in a son's proud hands
> is Pride, the scorched sky its Eclipse, and Glory is the same
> chariot back on its arc the very next morning."

Style read off `Helios.png`: bronze-and-gold relief on cracked dark
marble, Greek-key (meander) border.

```
Circular medallion, weathered bronze-and-gold sculptural relief on a dark cracked-marble background, photorealistic render, perfectly centered, isolated on transparent background — same finish and Greek-key meander border as Helios.png. Center: Phaethon, Helios's proud young son, gripping the reins of the sun chariot in white-knuckled panic as the four winged horses bolt out of control, the chariot tilting and scorching a jagged black streak across the sky and earth below, small stars and a cracked, smoking cloud-strip beneath the wheels; the same radiant sun-disc corona as the Helios plate now guttering and uneven behind him. Border: identical dark bronze-and-gold Greek key ring to Helios.png, small roundels bearing a cracked sun-disc in place of a whole one. Palette: bronze, aged gold, ash gray, dark ember red — matching the Helios plate's weathered stone finish exactly, no bright colors.
```

### Norse — Sól / Skoll

> "No mythology stages Glory and Eclipse more honestly: Skoll catches
> her at Ragnarok — the Eclipse foretold — yet the Eddas promise her
> daughter drives on, Glory reborn on the same road."
(This is the exact pairing the owner's own prompt suggested — "Sol and
the pursuing wolf Skoll.")

Style read off `Sol.png`: bronze relief on dark slate stone, Celtic
knotwork border.

```
Circular medallion, weathered bronze sculptural relief on dark slate stone, photorealistic render, perfectly centered, isolated on transparent background — same finish and Celtic-knotwork ring border as Sol.png. Center: Skoll, the great wolf of Norse myth, caught mid-leap against a starless dusk sky, jaws closing around the last sliver of the sun-disc Sól once held aloft — her empty upraised hand and trailing golden hair just visible at the wolf's shoulder, swallowed in his shadow, the chariot and horses Arvakr and Alsvidr rearing behind in his dust; the sun-disc from the Sol plate reduced to a thin crescent disappearing between the wolf's teeth. Border: identical bronze Celtic knotwork ring to Sol.png, small roundels bearing a wolf's snapping jaw in place of a sun-disc. Palette: dark bronze, iron gray, dying ember-gold — matching the Sol plate's weathered metal finish exactly, no bright colors.
```

### Egypt — Ra-Horakhty / Afu-Ra

> "That center is DOUBLE... which is simply Ra's day written as
> doctrine: the day barque in Glory, the night barque through the
> Duat in Eclipse, one god in two boats."
(Also the owner's own suggested pairing.)

Style read off `ra.png`: polished gold-and-silver relief on deep
lapis-blue field, ankh/Eye-of-Horus border.

```
Circular medallion, polished gold-and-silver relief on a deep lapis-blue night field, photorealistic render, perfectly centered, isolated on transparent background — same finish and ankh/Eye-of-Horus border as ra.png. Center: Ra in his aged ram-headed night form (Afu-Ra, "the flesh of Ra"), standing in the night barque as it is towed through the serpent-haunted dark of the Duat, the sun-disc dimmed to a dull ember behind curved ram horns, the great serpent Apophis coiling to strike the boat's prow while spears drive it back; the crown-cobra Wadjet from the ra.png plate now coiled low and watchful. Border: identical ankh-and-Eye-of-Horus ring to ra.png, small roundels bearing a coiled serpent in place of the sun-disc. Palette: gold on silver over deep lapis blue, dimmed ember-orange — matching the ra.png plate's finish exactly, no bright colors beyond the ember glow.
```

### Japan — Amaterasu / Ama-no-Iwato

> "Japan owns the canon's Glory-and-Eclipse pair outright: when she
> shut herself in the Ama-no-Iwato cave the world's light went out —
> the Eclipse told as a story — and her coaxed return, mirror-first,
> is Glory itself."
(Also the owner's own suggested pairing.)

Style read off `nichiyobi.png`: gold relief, sunburst-ray segments,
chrysanthemum-crest/kanji border.

```
Circular medallion, polished gold relief on a darkened field, photorealistic render, perfectly centered, isolated on transparent background — same finish, sunburst-ray segments and chrysanthemum/kanji border as nichiyobi.png. Center: the sealed boulder of Ama-no-Iwato filling the frame in near-total darkness, the gold sunburst rays from the nichiyobi.png plate snuffed to cold gray-black behind it, the sacred mirror Yata no Kagami propped against the rock catching one last thin glint of light, a single sakaki branch hung with jewels beside it, the torii gate barely visible, dark and empty; a sliver of warm gold light just beginning to leak from where the boulder has not quite sealed. Border: identical chrysanthemum-crest and kanji-roundel ring to nichiyobi.png. Palette: cold gray-black dominant, one thin sliver of warm gold — matching the nichiyobi.png plate's border finish exactly, the center field deliberately darkened against its usual glossy sunburst.
```

### Christianity — Cross / Washbasin

> "The king who washes feet, the God who empties himself... where the
> king of kings who kneels to wash feet is the servant-king in one
> body."
This is the SAME Ruler/Servant framing as Professions, in explicit
scripture terms — arguably the single strongest match in the survey.

Style read off `christianity.png`: polished silver relief on black
marble, grapevine-and-ichthys border.

```
Circular medallion, polished silver relief on black marble stone, photorealistic render, perfectly centered, isolated on transparent background — same finish and grapevine-and-ichthys border as christianity.png. Center: a plain silver washbasin and folded linen towel resting on black marble, water rippling in the basin catching a soft glow, a simple wooden staff leaning beside it where the cross stood in the christianity.png plate, the crown of thorns now resting loose and open beside the basin instead of at a cross's foot; the same soft glow that lit the cross in christianity.png now lighting the water's surface. Border: identical silver grapevine-and-ichthys knotwork ring to christianity.png. Palette: polished silver, deep black marble, soft warm-white glow — matching the christianity.png plate's finish exactly, no bright colors.
```

### Mithraism — Pater / Corax

> "Whoever rose to Pater had first crawled as a Corax and served the
> banquet — the king in the cult was its former servant, on purpose."

Style read off `mithraism.png`: bronze-and-gold relief on starred
lapis-blue field, raven/hound/scorpion/star border — the raven grade
is already present in this plate, perched on Mithras's cloak.

```
Circular medallion, weathered bronze-and-gold relief on a starred lapis-blue field, photorealistic render, perfectly centered, isolated on transparent background — same finish and raven/hound/scorpion star border as mithraism.png. Center: the Mithraic grade-banquet in the cave-temple — Pater, the cult's highest grade, seated in a Phrygian cap at the head of a stone table lit by the radiate face of Sol blazing through the cave arch behind him (the same Sol face as the mithraism.png plate), while a raven-masked Corax initiate kneels low, serving him a cup and plate at the table's foot, a raven perched on the initiate's shoulder; the tauroctony carved faintly into the stone wall behind them, echoing the mithraism.png center. Border: identical raven-hound-scorpion-star knotwork ring to mithraism.png. Palette: bronze and gold on deep starred lapis blue — matching the mithraism.png plate's finish exactly, no bright colors.
```

### Alchemy — refined gold / raw ore

> "Its Glory is the incorruptible shine no age can tarnish — and its
> Eclipse the same metal buried nameless in the ore, waiting for the
> Work to call it out."
(Also the owner's own suggested pairing — "gold vs its shadow.")

Style read off `gold.png`: polished gold border, sun-rosette
geometric ring, solar-corona field.

```
Circular medallion, polished gold relief border with a matte, unpolished center field, photorealistic render, perfectly centered, isolated on transparent background — same finish and sun-rosette geometric border as gold.png. Center: raw gold still buried and nameless — a jagged vein of dull, unrefined gold ore embedded in a broken chunk of dark quartz stone, matte and unglinting, resting in shadow with only the faintest corona of gold light bleeding from within the rock, as if the blazing solar corona from the gold.png plate were trapped and waiting under the surface. Border: identical ring of sun-rosettes (radiant starbursts and small sun-faces) to gold.png. Palette: dull unpolished gold, dark quartz gray, faint buried amber glow — matching the gold.png plate's border finish exactly, the center deliberately unpolished against its usual glossy corona.
```

### Slavic — young Dažbog / old Dažbog

> "His Glory is the high summer he pours from the horn — and his
> Eclipse the winter dimming, when the grandfather of the people walks
> his road old and gray, trusting the spring to crown him again."

Style read off `dazbog.png`: bronze-and-silver relief, wolf-and-rune
knotwork border, flame field.

```
Circular medallion, weathered silver-and-bronze relief on a cold winter-gray field, photorealistic render, perfectly centered, isolated on transparent background — same finish and wolf-and-rune knotwork border as dazbog.png. Center: Dažbog grown old and gray, the giving sun in its winter face — a bent, silver-bearded elder wrapped in a thin gray cloak stamped with faded sun-discs, his winged helm dulled, walking a snow-dusted road with a near-empty horn of plenty at his side and his scepter now a plain traveler's staff; behind him a pale, low corona of cold silver-gold light, the same corona from the dazbog.png plate but banked to embers. Border: identical wolf-and-glowing-rune knotwork ring to dazbog.png, small roundels bearing a bare winter branch in place of a sun-disc. Palette: tarnished silver, dull bronze, ash gray, faint amber ember — matching the dazbog.png plate's finish exactly, no bright colors.
```

---

## Notes on the two "stretch" themes

**Planets** and **planet_signs** share one article set, and that
article never personifies the Sun beyond the physical body — no named
second character exists to draw, only the same plasma sphere with its
light dimmed. A companion image there would just be an eclipsed disc,
which is a mood tint, not a duality FIGURE the way Skoll or Afu-Ra is
— worth doing only if the owner wants total 8-per-theme coverage for
its own sake, not because the canon asks for it. No prompt is offered
for either; if wanted later, "the same sun.png disc in eclipse, a thin
corona ring around a black disc" is the entire brief.

---

## Freemasonry — the NEW religion-theme Sunday pair (owner remap 2026-07-12)

The owner moved the base religion set to narrative-first days:
Freemasonry now holds SUNDAY (the quest for more Light under the
All-Seeing Eye; the Master seated in the East), Christianity moved to
Friday (the God who forgives, agape, Good Friday). So the religion
theme's Sunday DUAL is now the masonic one — and no tradition states
the center's double nature more literally than the two ashlars:

> The ROUGH ASHLAR is the apprentice's stone — unhewn, aware it needs
> the chisel (Humility, the Servant face). The PERFECT ASHLAR is the
> fellow-craft's proof — the polished cube that returns the light it
> is given (Glory, the Ruler face). The Eye above watches the work
> either way (Justice).

The main face stays the owner's `freemasonry.png` (square and
compasses); the companion below is the dark face. An OPTIONAL third
prompt upgrades the main medallion to work the All-Seeing Eye into
the composition — the owner's call whether to regenerate or keep the
plain square-and-compasses.

**Rough Ashlar — the Servant face (drop at `assets/weekday/religion/dual/rough_ashlar.png`)**
```
Circular medallion, polished silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on transparent background — same finish and border family as the owner's freemasonry religion medallion. Center: a rough-hewn cubic block of stone on a masonic tracing board, its faces still cracked and unworked, a gavel and a chisel resting against its base and a plumb line hanging beside it; high above, the All-Seeing Eye within a radiant triangle watches faintly through the gloom, a single thin ray touching the stone's top edge — the work not yet begun, the light only promised. Border: silver ring bearing small roundels that alternate the square-and-compasses with a tiny radiant delta. Palette: silver, graphite black, one faint warm ray of pale gold — matching the religion set's black-stone finish exactly.
```

**Perfect Ashlar — optional bright counterpart (drop at `assets/weekday/religion/dual/perfect_ashlar.png`, only if the owner wants the pair as TWO new images instead of reusing freemasonry.png)**
```
Circular medallion, polished silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on transparent background — same finish and border family as the owner's freemasonry religion medallion. Center: a perfectly squared and polished cubic ashlar on a masonic tracing board, its faces mirror-smooth and returning the light, suspended from a lewis hook above a builder's level; the All-Seeing Eye within a radiant triangle blazes directly over it, its glory rays breaking on the cube's edges into small stars. Border: silver ring bearing small roundels that alternate the square-and-compasses with a tiny radiant delta. Palette: silver, graphite black, radiant white-gold rays — matching the religion set's black-stone finish exactly.
```

**Optional main-medallion upgrade — square, compasses AND the Eye (would replace `assets/weekday/religion/freemasonry.png`)**
```
Circular medallion, polished silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on transparent background — same finish and border family as the other religion medallions (black stone, silver relief). Center: the square and compasses opened over an open book of constitutions, the letter G at their crossing; above them the All-Seeing Eye within a radiant triangle, its glory rays fanning down so the tools work literally UNDER the Eye's light; two small columns flank the composition at the edges. Border: silver ring with small roundels alternating a radiant delta, a trowel and a plumb line. Palette: silver, graphite black, pale white-gold rays.
```

---

## Colored variants for the metal themes (owner correction 2026-07-12)

Greek, Norse and Professions carry FOUR looks (Gold/Silver/Bronze +
Colored full art) — so their Sunday companions need TWO generations
each, exactly like the Servant pair above. The bronze Phaethon and
Skoll are delivered; these are the missing COLORED prompts, in the
same house styles as `colored/Helios.png` and `colored/Sol.png`.

**Phaethon — colored (drop at `assets/weekday/greek/dual/colored/Phaethon.png`)**
```
Ornate circular badge, vivid full-color enamel over dark gold, photorealistic render, perfectly centered, isolated on white background — same finish and Greek-key border family as the colored Helios badge. Center: Phaethon, Helios's proud young son, gripping the reins of the runaway sun chariot in white-knuckled panic, the four winged horses bolting in different directions, the chariot tilting; the sun-disc behind him guttering from radiant gold to ember red, a jagged black scorch-streak burning across a glossy twilight-orange sky field, tiny stars and a smoking cloud-strip beneath the wheels. Border: darkened gold Greek key pattern with small roundels bearing a cracked ember-red sun-disc. Colors: ember orange, scorched crimson, aged gold, ash black — visibly the SAME palette family as the colored Helios badge but overheated and breaking.
```

**Skoll — colored (drop at `assets/weekday/norse/dual/colored/Skoll.png`)**
```
Ornate circular badge, vivid full-color painted-wood-and-iron finish with aurora accents, photorealistic render, perfectly centered, isolated on white background — same finish and Celtic-knotwork border family as the colored Sol badge. Center: Skoll, the great charcoal-black wolf of Norse myth, caught mid-leap against a deep indigo dusk sky threaded with a thin green-violet aurora, jaws closing around the last golden sliver of the sun-disc; Sol's empty upraised hand and trailing golden hair just visible at the wolf's shoulder, her chariot horses rearing behind in his dust. Border: iron-and-painted-wood Celtic knotwork ring with small roundels bearing a wolf's snapping jaw in dying-ember gold. Colors: charcoal black, deep indigo, aurora green-violet, dying ember gold — the SAME aurora-accent family as the colored Sol badge with its daylight swallowed.
```

---

## Delivered art — where everything landed (2026-07-12)

All ten generated images processed (circle cut / alpha crop, 800×800
RGBA) and placed; the `dual/` subfolders are inert until the legend
wiring lands:

| Source | Destination |
|---|---|
| servant.png | `assets/weekday/profession/Servant.png` |
| servant colored.png | `assets/weekday/profession/colored/Servant.png` |
| phaethon.png | `assets/weekday/greek/dual/Phaethon.png` |
| skoll.png | `assets/weekday/norse/dual/Skoll.png` |
| afu-ra.png | `assets/weekday/egypt/dual/afu_ra.png` |
| Ama-no-Iwato.png | `assets/weekday/japan/dual/ama_no_iwato.png` |
| corax.png | `assets/weekday/religion/dual/corax.png` |
| washbasin.png | `assets/weekday/religion/dual/washbasin.png` |
| old dazbog.png | `assets/weekday/slavic/dual/dazbog_old.png` |
| raw ore.png | `assets/weekday/alchemy/dual/ore.png` |

The Servant pair sits directly beside the Ruler (an eighth plate of
the profession set, per section 1); everything else waits in its
theme's `dual/` folder. When the colored Phaethon/Skoll land, they
take `dual/colored/` next to their bronze versions.
