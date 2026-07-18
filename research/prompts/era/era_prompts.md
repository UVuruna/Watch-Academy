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
`Starry_Autumn.png`, `Starry_Winter.png`, plus (owner fix-round B,
2026-07-19, TASK 3) `Anno_Lucis.png` and, under `assets/era/calendar/`,
`AUC.png`, `Byzantine.png`, `Hebrew.png`, `Hegirae.png`, `Buddhist.png`,
`Huangdi.png`. No `<source>` split (a single generation batch, like the
emblem/badge families) — the app reads `assets/era/<Name>.png` (or
`assets/era/calendar/<Name>.png`) directly (`config/defaults.py`
`ERA_ART_DIR`).

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

## Anno Lucis — the dial's own measured era

**Anno Lucis** (owner fix-round B, 2026-07-19, TASK 3 — "treba da
napraviš promptove") → `assets/era/Anno_Lucis.png`. Same round
rose-window family as the six above, but the SUBJECT is the dawn
itself rather than the reign it opens: the eleven-year flicker motif
already carried as a border signature on every Age/Season plate here
becomes the FOREGROUND — the first unbroken light year breaking free
of the flicker's hesitation.

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The great year-wheel motif shared by the Age and Starry Season plates, but caught at its single hinge moment: eleven small flame-shaped glass tesserae march across the wheel's base in a broken, hesitating row — seven dark, then light, then dark once more — and at the row's very last tessera the flame catches and HOLDS, a fresh radiant gold-white dawn breaking upward from that one held flame to fill the wheel's upper arc, still climbing, not yet at its crest. A single sunburst begins to form at the top, still gathering itself. Border: the shared candle-flicker-and-tick leadwork rim, brightest exactly where the held flame sits. Palette: fresh dawn gold rising from a held ember, the last dark tesserae still visible behind it, warm dark-gold lead. NO lettering anywhere.
```

## The Eras of the World's own calendars

**Six emblems** (owner fix-round B, 2026-07-19, TASK 3 — "zašto nismo
ubacili kineski" prompted the whole round), one per calendar system the
"Eras of the World" essay compares — SAME round rose-window family,
SAME house rules (photorealistic, isolated background, the circular
window shape IS the frame, NO lettering anywhere — no calligraphy, no
numerals, no inscriptions of any kind, the doctrine drawn as image
alone). Every emblem stays ANICONIC — no human figures, no faces, no
portraiture of any founder or prophet — each speaks its epoch through
CLASSICAL, RESPECTFUL iconography only, the same restraint a rose
window itself keeps; these are living traditions, drawn with the same
care the dial gives its own measured era, never a caricature.
Drop path: `assets/era/calendar/`.

**AUC — Ab Urbe Condita** (Rome, 753 BCE) →
`assets/era/calendar/AUC.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. The Capitoline she-wolf suckling the twin founders fills the disc's lower field in warm bronze-and-amber glass, a laurel wreath arcing above her, seven small hill-shaped tesserae set in a low arc behind her marking Rome's seven hills. Palette: warm bronze, amber and deep laurel green, aged-gold lead. Border: a simple laurel-and-tick leadwork rim. NO lettering anywhere, no human figures beyond the twin infants already fixed in the founding motif itself.
```

**Byzantine Anno Mundi** (1 September 5509 BCE) →
`assets/era/calendar/Byzantine.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A great golden mosaic dome fills the disc's upper field in radiant Byzantine gold-glass tesserae, its curve echoing Hagia Sophia's own; below it a triple interlocking ring motif (the 19-year lunar, 28-year solar and 15-year indiction cycles the era was tuned to close together) sits in deep imperial purple and gold. Palette: radiant Byzantine gold, imperial purple, aged-bronze lead. Border: the shared candle-flicker-and-tick leadwork rim, dressed in a fine mosaic-tessera texture. NO lettering anywhere, no figures.
```

**Hebrew Anno Mundi** (Tishri, 3761 BCE) →
`assets/era/calendar/Hebrew.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A seven-branched menorah in warm gold glass rises from the disc's base, its central flame the brightest point in the whole medallion; behind it a soft autumn-toned sky (Tishri's own season) fades from amber near the flame to deep blue at the rim. Palette: warm menorah gold, deep autumn amber, twilight blue, aged-gold lead. Border: the shared candle-flicker-and-tick leadwork rim. NO lettering anywhere, no figures.
```

**Anno Hegirae** (the Hijra, 622 CE) →
`assets/era/calendar/Hegirae.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A slender crescent moon and a single bright star sit high in a deep midnight-blue glass sky filling the disc's upper field; below them a small caravan of tents and a winding desert path in warm sand-and-amber glass trace a journey toward the rim — the emigration itself, never a face among the tents. Palette: deep midnight blue, silver crescent, warm sand and amber, dark-iron lead. Border: the shared candle-flicker-and-tick leadwork rim. NO lettering anywhere (no calligraphy of any kind — this is the one house rule that matters most here), no figures.
```

**Buddhist Era** (the Parinirvana, 543 BCE) →
`assets/era/calendar/Buddhist.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A Bodhi leaf-shaped canopy of glass fills the disc's upper field in deep jade and gold, sheltering an empty stone seat below it (the aniconic Buddhist convention — presence marked by absence); a single lotus in soft pink-white glass floats at the base, fully open. Palette: deep jade, warm gold, soft lotus pink-white, dark-bronze lead. Border: the shared candle-flicker-and-tick leadwork rim. NO lettering anywhere, no figures — the empty seat and the footprint-free lotus carry the whole doctrine.
```

**Huangdi / Chinese** (the Yellow Emperor, conventionally 2697 BCE) →
`assets/era/calendar/Huangdi.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. An Imperial-yellow jade disc (a bi, the ancient symbol of heaven) sits at the medallion's center, ringed by a single sinuous dragon in deep jade-green and gold tracing the disc's own circular window edge — the dragon never fully closing the circle, echoing the flicker motif's own broken row in spirit though not in literal form. Palette: imperial yellow-gold, deep jade green, dark lacquer-red accents, dark-bronze lead. Border: the shared candle-flicker-and-tick leadwork rim. NO lettering anywhere, no figures.
```

**Future use (owner note, not yet wired further than the essay art):**
these six calendar emblems' art already backs the "Eras of the World"
article's image strip (`app/encyclopedia.py` `_ERA_CALENDAR_ART`,
graceful-absent — see [Encyclopedia](../../../app/encyclopedia.md));
the owner's next planned use is the Settings/era-picker combo
(`app/settings_dialog.py` Third calendar dropdown, currently text-only)
wearing the matching emblem beside each option.

---

## Status

- New sheet (ROADMAP 15a3, owner 2026-07-17); the six Age/Season
  emblems NOT yet generated.
- Extended (owner fix-round B, 2026-07-19, TASK 3 — "treba da napraviš
  promptove"): Anno Lucis's own emblem plus six calendar-system
  emblems (AUC, Byzantine AM, Hebrew AM, AH, Buddhist Era, Huangdi)
  join the sheet — 13 images total, NONE generated yet. The "Eras of
  the World" comparative article itself still carries no plate of its
  OWN — it is the essay that compares this dial's measurement against
  every OTHER tradition's arithmetic — but it now strings the six
  calendar emblems as its own image strip (see the Future use note
  above; `app/encyclopedia.py` wires the paths already, graceful-absent).
- Verify with `python main.py "research/prompts/era/era_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner
  (13 images expected — verified 2026-07-19, dry-run clean, 0 problems).
