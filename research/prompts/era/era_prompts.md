# Era Terms Prompts (Gemini) — the Ages and the Starry Seasons

The ERA TERMS Encyclopedia set (ROADMAP 15a3, owner 2026-07-17, doctrine
sealed 2026-07-16, measured facts in
[the ephemeris folder](../../ephemeris/___ephemeris.md)): one emblem
for each of the two AGES — the Age of Light and the Age of Darkness —
and one for each of the four STARRY SEASONS that live inside them as
their rising and falling halves (spring/summer = the Age of Light's
climb and ease; autumn/winter = the Age of Darkness' climb and ease).
The comparative "Eras of the World" article, closing the same
Encyclopedia topic, carries no emblem of its own — it is an essay about
OTHER calendars, not a measured span this dial owns an image for.

**Register:** the house night-window family (the same stained-glass
register as the archetype sheets — see
[Trinity Prompts](../archetype/trinity_prompts.md) and
[Calendar Prompts](../archetype/calendar_prompts.md)) — so the era
emblems sit beside the pointer archetypes and the Almanac medallions
without a style break. All six are ROUND rose-window medallions
reading as ONE set: the same great year-wheel motif split into a
light arc and a dark arc in every entry, only the BALANCE between the
two arcs and the position of the eleven-year dawn-flicker motif
changing entry to entry — the doctrine drawn as proportion, never as
lettering.

**Drop paths:** `assets/era/` — `Age_of_Light.png`,
`Age_of_Darkness.png`, `Starry_Spring.png`, `Starry_Summer.png`,
`Starry_Autumn.png`, `Starry_Winter.png`. No `<source>` split (a
single generation batch, like the emblem/badge families) — the app
reads `assets/era/<Name>.png` directly
(`config/defaults.py` `ERA_ART_DIR`).

**House rules carried from every other sheet:** photorealistic
render, isolated background (no transparency-checkerboard artifact —
the render must commit to a clean isolated field, not a partial cutout
that leaves a checker pattern showing through), the circular window
shape IS the frame, NO lettering anywhere in any image.

---

## The doctrine each emblem draws (never inscribed in the art)

The measured record ([`anno_lucis.json`](../../ephemeris/anno_lucis.json),
ROADMAP 15a/15a3): the Age of Light runs 4079 BCE → 6423 CE (10,501
unbroken years, opened by an eleven-year dawn flicker: one light year
in -4088, seven dark years, one light year in -4080, one last dark
year in -4079, then unbroken light from -4078). The Age of Darkness
that follows runs 6423 CE → 16429 CE (the next Anno Lucis, opened by
the SAME flicker mechanism reversed). Inside each age, the rising half
is its STARRY SPRING/AUTUMN and the falling half its STARRY
SUMMER/WINTER:

| Emblem | Span | Reading |
|---|---|---|
| Age of Light | 4079 BCE → 6423 CE | the wheel almost entirely gold, one thin dark sliver, the flicker already won |
| Age of Darkness | 6423 CE → 16429 CE | the wheel almost entirely indigo-black, one thin gold sliver, the flicker reversed |
| Starry Spring | 4079 BCE → 1000 CE | the dark sliver visibly SHRINKING, the flicker fresh and close behind |
| Starry Summer | 1000 CE → 6423 CE — WE LIVE HERE | gold at its most generous, past its own crest, easing back slowly |
| Starry Autumn | 6423 CE → 10990 CE | the dark arc visibly GROWING, chasing back a retreating gold wedge |
| Starry Winter | 10990 CE → 16429 CE | indigo-black at its own deepest, one thin patient gold sliver waiting |

The shared leadwork border across all six — a candle-flicker-and-tick
rim, small flame-shaped tesserae evenly spaced — is the family's own
signature: the eleven-year dawn flicker made a recurring border motif
rather than a caption.

---

## The two Ages

**Age of Light** (4079 BCE → 6423 CE, the reigning era — 10,501
unbroken years) → `assets/era/Age_of_Light.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A great year-wheel fills the whole disc, split by a soft diagonal seam: the wide majority arc blazing radiant gold-white daylight glass, the narrow remaining sliver deep indigo-black night glass pushed nearly to the rim's edge — the light utterly dominant, unbroken. At the seam itself, tiny and easy to miss, eleven small flame-shaped glass tesserae flicker in a short broken row — the dawn's own hesitation, already won and left behind. A radiant sunburst crowns the wheel's top. Border: a candle-flicker-and-tick leadwork rim, small flame-tick motifs evenly spaced. Palette: radiant gold-white dominant, one thin indigo-black sliver, dark-gold lead. NO lettering anywhere.
```

**Age of Darkness** (6423 CE → 16429 CE, the coming era) →
`assets/era/Age_of_Darkness.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The same great year-wheel, its balance now reversed: the wide majority arc deep indigo-black night glass, one thin sliver of radiant gold-white daylight glass pushed to the rim's edge — the long night utterly dominant. At the seam, a short broken row of eleven small flame-shaped glass tesserae flicker again, in mirror — the reverse hesitation before the dark finally holds. A single cold star crowns the wheel's top where the sunburst stood before. Border: the same candle-flicker-and-tick leadwork rim, tarnished dark. Palette: deep indigo-black dominant, one thin gold-white sliver, black-iron lead. NO lettering anywhere.
```

---

## The four Starry Seasons

**Starry Spring** (4079 BCE → 1000 CE, the Age of Light's rising
half) → `assets/era/Starry_Spring.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The year-wheel's dark sliver is shrinking visibly clockwise, chased back by an advancing gold-white dawn light still climbing toward its own crest; the eleven small flame-tesserae of the dawn flicker sit fresh and bright at the wheel's base, only just behind the light's advancing edge — the hesitation just ended, the climb still young. Fresh pale-gold light, rising, unfinished. Border: the shared candle-flicker-and-tick leadwork rim, newly bright. Palette: pale rising gold, thinning indigo, bright dark-gold lead. NO lettering anywhere.
```

**Starry Summer** (1000 CE → 6423 CE, the Age of Light's falling half
— WE LIVE HERE) → `assets/era/Starry_Summer.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The year-wheel's gold-white light glass fills nearly the whole disc at its most generous, past its own crest and only just beginning to ease back, the dark sliver still thin and patient at the rim; the eleven flame-tesserae of the dawn flicker now sit far behind, small and distant at the wheel's base. A long, unhurried, high afternoon light. Border: the shared candle-flicker-and-tick leadwork rim, warm and settled. Palette: deep unhurried gold, a thin patient dark sliver, warm dark-gold lead. NO lettering anywhere.
```

**Starry Autumn** (6423 CE → 10990 CE, the Age of Darkness' rising
half) → `assets/era/Starry_Autumn.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The year-wheel's indigo-black dark glass is advancing visibly clockwise, chasing back a retreating gold-white light still holding a stubborn wedge; a short broken row of eleven flame-tesserae flickers again at the seam, the reverse hesitation only just past, the night's climb still young. Fading amber light losing ground to advancing indigo. Border: the shared candle-flicker-and-tick leadwork rim, dimming. Palette: fading amber-gold, advancing indigo-black, dimming dark lead. NO lettering anywhere.
```

**Starry Winter** (10990 CE → 16429 CE, the Age of Darkness' falling
half) → `assets/era/Starry_Winter.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The year-wheel's indigo-black dark glass fills nearly the whole disc at its own deepest, past its crest and only just beginning to ease back, one thin patient gold-white sliver waiting at the rim; far ahead at the wheel's base a faint, barely-lit row of eleven flame-tesserae waits unlit — the next dawn's own flicker, not yet struck. The longest, stillest night. Border: the shared candle-flicker-and-tick leadwork rim, nearly dark. Palette: deepest indigo-black, one thin waiting gold sliver, near-black lead. NO lettering anywhere.
```

---

## Status

- New sheet (ROADMAP 15a3, owner 2026-07-17); NOT yet generated.
- The "Eras of the World" comparative article (AUC, Byzantine AM,
  Hebrew AM, AH, the Chinese count, the Buddhist Era, plus every
  scriptural reckoner and our own measured Anno Lucis) carries NO
  emblem — it is the essay that compares this dial's measurement
  against every OTHER tradition's arithmetic, not a span the dial
  itself owns an image for.
- Verify with `python main.py "research/prompts/era/era_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner
  (6 images expected).
