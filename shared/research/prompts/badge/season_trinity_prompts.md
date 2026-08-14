# Trinity and Season Prompts (Gemini)

> **STALE ART — THE ORDER LAW re-seating (owner decree 2026-08-09).**
> This sheet predates its own art: the three Trinity badge PNGs exist
> (Faith, Hope and Love, each as a `_gem` and a `_gpt` file in the
> colored badges folder this sheet drops into, generated
> 2026-07-13/14) and are WIRED into the product
> (`config/defaults.py` → the Encyclopedia's virtue pages), but they
> were generated under the retired mapping — Faith in noon gold, Hope
> in dawn blue, Love in evening red. The Trinity briefs below are
> RE-SEATED (Love 12h yellow noon, Hope 20h red evening, Faith 04h
> blue dawn): the three badges must be REGENERATED from them, on both
> sources, and until that happens the Encyclopedia shows the retired
> colors. Generation is the owner's step in the chain. The Seasons,
> Turning-Point and Meteorological families are untouched by the
> re-seating — their existing art stays valid.

Prompts for the concept badges: the three
**Theological Trio** entries (Faith, Love, Hope — a separate set from
the Trio *pointer*, but the same three names), the six **Seasons**
(the four astronomical seasons plus the tropics' Wet/Dry pair), the
three **Turning Points** (the two solstices plus one shared Equinox
badge), and the four OPTIONAL **Meteorological** twins. Same house
rules as [Virtue](../emblem/virtue_prompts.md), [Sin](../emblem/sin_prompts.md)
and [Mood Prompts](../emblem/mood_prompts.md):
allegorical cameo badges, concrete objects and scenes, NO lettering
anywhere in the image, circular, isolated on white background. Paste
one prompt at a time; generate a whole family in one chat session so
the set stays visually consistent.

Suggested drop locations (flat PNGs, matching the existing
`assets/weeks/inner_wheel/virtue/primary/colored/`, `assets/calendars/zodiac/astrology/primary/sign/` conventions):

- `masters/archetypes/trinity/badges/colored/Faith.png`, `Hope.png`, `Love.png`
- `masters/celestial/seasons/badges/Spring.png`, `Summer.png`, `Autumn.png`, `Winter.png`,
  `Wet_Season.png`, `Dry_Season.png` (owner correction, RULE-19 round
  2026-07-20 — the code reads the UNDERSCORED stems,
  `render.compositor._current_season_key`; the two bare `WetSeason.png`/
  `DrySeason.png` names below were dead weight, `research/ASSETS_AUDIT.md`
  §Structure Inconsistencies #3)
- `masters/celestial/seasons/badges/turning_point/Summer_Solstice.png`,
  `Winter_Solstice.png`, `Equinox.png` (same correction — the code
  reads the underscored stems, `render.compositor._earth_text`'s
  `season_event.replace(" ", "_")`)
- `masters/celestial/seasons/badges/meteorological/Spring.png`, `Summer.png`, `Autumn.png`,
  `Winter.png` *(OPTIONAL set)*

---

## Design Notes — Four Families, One Cross-Cure Canon

Same principle as the Virtue/Sin/Mood set: a constant **field texture
+ border metal + motif**, held fixed across every item in a family, so
the CATEGORY reads at a glance while the day/season's own color
carries the individual identity. None of these four devices repeats
the polished-gold, blackened-iron or polished-silver devices already
spoken for by Virtue, Sin and Mood.

| Family | Field | Border metal & motif | Reading |
|---|---|---|---|
| Trinity | engraved **triskelion** — three rays sweeping outward from center like the Trio pointer's three arms, tinted the virtue's color | brushed **bronze** ring, triquetra (three interlaced arcs) motif | a third, covenant metal for a three-armed, cross-place-spanning set — vertical, horizon, human |
| Seasons | engraved **growth-ring** — concentric annual tree rings radiating outward, tinted the season's color | weathered **verdigris-copper** ring, wheel-of-the-year quarter-spoke motif | copper weathers with the year itself; the quarter-spokes are the four turning points the wheel visits |
| Turning Points | engraved **hexagram** — six rays crossing at center exactly like the dial's own hexagram pointer | **split gold-and-silver** ring, sundial gnomon motif at the seam | the alchemy metals of noon and midnight (`SYMBOLISM.md` — gold top tip, silver bottom tip) made literal on the one family that IS the solstice/equinox axis |
| Meteorological (OPT.) | Seasons' own growth-ring field, unchanged | Seasons' own copper ring, PLUS a small bundle of three calendar leaves tied with twine and a slender thermometer laid across them, pinned like a wax seal at the badge's lower edge | the "measured" twin of the astronomical season — same wheel, a human calendar tag added |

The Trinity's triskelion deliberately echoes the TRIO POINTER's own
three-armed geometry (`SYMBOLISM.md` — Love 12h, Hope 20h, Faith 4h,
THE ORDER LAW re-seating of 2026-08-09) without copying it exactly:
the badge field spins the three rays from
a shared center the way the pointer's three arms share the dial's
center. The Seasons' growth rings and the Turning Points' hexagram are
both literal — a tree actually rings itself once a year, and the dial
actually carries a hexagram pointer whose top vertex is true solar
noon (`CLAUDE.md` project facts). Colors below hold Goethe's axis
exactly (`SYMBOLISM.md` — Seasons Axis section): summer yellow-gold =
the light pole, winter deep blue = the dark pole, spring green = the
poles' union at the equinox, autumn red-orange = *Steigerung*, the
light going down fighting.

---

## The Trinity — brushed bronze cameo, triskelion field

Hues from `config/palette.py` `TRINITY` (`("#F8E600", "#B60000",
"#002FFF")`, paired with `config/constants.py` `TRIO_ARM_THEMES` for
the virtue-name seating): Love yellow, Hope red, Faith blue — exactly
the arm colors the Trio pointer already paints at 12h/20h/4h; only the
virtue NAMES moved, one arm each, THE ORDER LAW (owner decree
2026-08-09).

**Love (yellow — the center's own axis, vertical, 12h)** → `masters/archetypes/trinity/badges/colored/Love.png`
```
Ornate circular badge, vivid allegorical enamel in brushed bronze cameo, engraved triskelion field, photorealistic render, perfectly centered, isolated on white background. Center: a small burning heart cradled gently between two open, giving hands held straight up at the noon zenith, one steady unwavering flame rising from its crown, lit by a single shaft of pure golden-yellow light falling straight down from directly overhead; glossy triskelion field of three golden-yellow rays sweeping outward from the zenith like sunlight given a spinning shape. Border: brushed bronze ring with a triquetra motif, three small yellow-gold enamel roundels at the 12h/20h/4h angles bearing a tiny flame. Colors: bronze dominant, radiant yellow-gold, warm noon amber.
```

**Hope (red — the evening arm, 20h, toward what comes)** → `masters/archetypes/trinity/badges/colored/Hope.png`
```
Ornate circular badge, vivid allegorical enamel in brushed bronze cameo, engraved triskelion field, photorealistic render, perfectly centered, isolated on white background. Center: a ship's anchor standing fast upright on a bare evening shoreline, its stock catching the day's last red-gold light, one bright point of light already kindling low over the eastern horizon where tomorrow has not yet risen; glossy triskelion field of three rays sweeping outward, deep evening red deepening toward horizon gold at the rim. Border: brushed bronze ring with a triquetra motif, three small red-enamel roundels at the 12h/20h/4h angles bearing a tiny anchor. Colors: bronze dominant, evening red, horizon gold.
```

**Faith (blue — the dawn arm, 04h, what was already given)** → `masters/archetypes/trinity/badges/colored/Faith.png`
```
Ornate circular badge, vivid allegorical enamel in brushed bronze cameo, engraved triskelion field, photorealistic render, perfectly centered, isolated on white background. Center: a lone robed figure kneeling on a bare dawn shoreline, both arms lifted toward a single shaft of pale blue-silver light breaking low across the eastern horizon, eyes closed, no ground visible ahead but the light itself, received rather than sought; glossy triskelion field of three pale blue rays sweeping outward from the horizon like moonlight handed on to the coming day. Border: brushed bronze ring with a triquetra motif, three small blue-enamel roundels at the 12h/20h/4h angles bearing a tiny descending ray. Colors: bronze dominant, dawn blue, moonlit silver.
```

---

## The Seasons — weathered copper cameo, growth-ring field

Palette locked to Goethe's axis (`SYMBOLISM.md` — The Seasons Axis
section): Summer = the light pole, Winter = the dark pole, Spring =
their union, Autumn = *Steigerung*. Wet/Dry are the tropics' own pair,
standing in for the temperate zone's Spring/Autumn where the year
turns on rain instead of temperature.

**Spring (green — the union of the poles, light and dark in equal parts)** → `masters/celestial/seasons/badges/Spring.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a single green shoot breaking through dark soil at the exact moment of sunrise, a pair of scales balanced perfectly level beside it — one pan resting in sunlight, one pan resting in shade — neither side tipping; glossy growth-ring field of concentric rings in fresh union-green, half warmed gold and half cool blue bleeding into the green at the outer rim. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny balanced scale. Colors: copper dominant, union green, half-gold half-blue rim.
```

**Summer (yellow-gold — the light pole, the year's longest light)** → `masters/celestial/seasons/badges/Summer.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a ripe wheat field blazing under a sun at its exact zenith, heat shimmer rising off the gold, a reaper's basket overflowing with grain in the foreground, not a single shadow cast anywhere in the scene; glossy growth-ring field of concentric rings blazing pure yellow-gold, brightest at the very center. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny zenith sun. Colors: copper dominant, blazing yellow-gold, wheat amber.
```

**Autumn (red-orange — Steigerung, the light going down fighting)** → `masters/celestial/seasons/badges/Autumn.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a bonfire of fallen leaves burning red-orange against a low gathering-dusk sky, more leaves still spiraling down from bare branches into the flame; glossy growth-ring field of concentric rings deepening from ember gold at the rim to fierce red-orange at the center. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny falling leaf. Colors: copper dominant, ember red-orange, ash gray.
```

**Winter (deep blue — the dark pole, the year's longest dark)** → `masters/celestial/seasons/badges/Winter.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a single bare tree standing alone in deep snow under a moonlit midnight-blue sky, icicles hanging from its lowest branch catching cold silver-blue light; glossy growth-ring field of concentric rings deepening to the darkest midnight blue at the very center. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny icicle. Colors: copper dominant, deep midnight blue, frost silver.
```

**Wet Season (lush green & rain silver — the tropics' light half)** → `masters/celestial/seasons/badges/Wet_Season.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: monsoon rain falling in silver sheets over a lush green jungle canopy, a swollen river catching the rain's silver light below, broad banana leaves glistening wet in the foreground; glossy growth-ring field of concentric rings in saturated jungle green streaked with silver rain. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny raindrop. Colors: copper dominant, lush jungle green, monsoon silver.
```

**Dry Season (bleached gold & dust — the tropics' other half)** → `masters/celestial/seasons/badges/Dry_Season.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: sun-cracked red earth stretching to a shimmering heat-haze horizon, tall grass bleached to pale gold, a small dust devil spiraling up in the distance past a lone baobab silhouette; glossy growth-ring field of concentric rings in bleached dust-gold deepening to cracked-earth brown at the rim. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny dust devil. Colors: copper dominant, bleached gold, cracked-earth brown.
```

---

## The Turning Points — split gold-and-silver cameo, hexagram field

Three badges, not seven: one shared Equinox serves both the March and
September crossing — "the day of perfect balance" reads the same
either way. Field and border literally draw the dial's own hexagram
pointer (`CLAUDE.md` — top vertex always points at true solar noon).

**Summer Solstice (all gold — the year's shortest shadow)** → `masters/celestial/seasons/badges/turning_point/Summer_Solstice.png`
```
Ornate circular badge, vivid allegorical enamel in polished gold cameo, engraved hexagram field, photorealistic render, perfectly centered, isolated on white background. Center: the sun standing motionless at its highest point of the year, a golden hexagram of six blazing rays crossing behind it exactly like the dial's own hexagram pointer, a standing gnomon below casting a shadow reduced to almost nothing at high noon. Border: polished gold ring, unbroken, with a sundial gnomon motif marking the year's shortest shadow. Colors: gold dominant, blazing white-gold, high-noon sky blue.
```

**Winter Solstice (all silver-blue — the year's longest shadow)** → `masters/celestial/seasons/badges/turning_point/Winter_Solstice.png`
```
Ornate circular badge, vivid allegorical enamel in oxidized silver cameo, engraved hexagram field, photorealistic render, perfectly centered, isolated on white background. Center: the sun barely clearing a snow-bound horizon at its lowest arc of the year, a silver hexagram of six pale rays crossing behind it exactly like the dial's own hexagram pointer, a standing gnomon casting the longest shadow of the year across frozen ground. Border: oxidized silver ring, unbroken, with a sundial gnomon motif marking the year's longest shadow. Colors: silver dominant, deep winter blue, frost white.
```

**Equinox (exact half gold, half silver — the day of perfect balance)** → `masters/celestial/seasons/badges/turning_point/Equinox.png`
```
Ornate circular badge, vivid allegorical enamel in split gold-and-silver cameo, engraved hexagram field, photorealistic render, perfectly centered, isolated on white background. Center: a single gnomon standing dead center casting a shadow exactly as long as it is tall, one half of the disc behind it lit in full gold daylight and the other half in full silver-blue night, the split running vertically straight through a sun hanging exactly on the horizon line. Border: ring split exactly in half, polished gold meeting oxidized silver at two opposite points, with a tiny sundial gnomon motif marking the seam. Colors: half gold dominant, half silver dominant, a thin seam of true green where the day-light and night-light bleed together.
```

---

## The Meteorological Set — OPTIONAL, the Seasons' measured twins

Same copper cameo and growth-ring field as the astronomical Seasons
above (same center imagery, same palette) — each meteorological badge
adds ONE small corner device pinned at the lower edge like a wax seal:
three calendar leaves bound with twine and a slender thermometer laid
across them, marking the "measured" calendar-quarter twin against the
astronomical badge's pure celestial imagery. The owner may skip this
set entirely; it exists only to distinguish `Meteorological {season}`
(the fixed calendar-month spans already named in the ring hover) from
the solstice/equinox-anchored astronomical seasons above.

**Meteorological Spring** → `masters/celestial/seasons/badges/meteorological/Spring.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a single green shoot breaking through dark soil at sunrise, a pair of scales balanced perfectly level beside it — one pan in sunlight, one pan in shade; glossy growth-ring field of concentric rings in fresh union-green, half warmed gold and half cool blue bleeding into the green at the rim; a small bundle of three calendar leaves tied with twine and a slender thermometer laid across them pinned like a wax seal at the lower edge of the disc. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny balanced scale. Colors: copper dominant, union green, half-gold half-blue rim, small twine-and-thermometer accent.
```

**Meteorological Summer** → `masters/celestial/seasons/badges/meteorological/Summer.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a ripe wheat field blazing under a zenith sun, heat shimmer rising off the gold, a reaper's basket overflowing with grain in the foreground; glossy growth-ring field of concentric rings blazing pure yellow-gold, brightest at the center; a small bundle of three calendar leaves tied with twine and a slender thermometer laid across them pinned like a wax seal at the lower edge of the disc. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny zenith sun. Colors: copper dominant, blazing yellow-gold, wheat amber, small twine-and-thermometer accent.
```

**Meteorological Autumn** → `masters/celestial/seasons/badges/meteorological/Autumn.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a bonfire of fallen leaves burning red-orange against a low gathering-dusk sky, more leaves spiraling down from bare branches into the flame; glossy growth-ring field of concentric rings deepening from ember gold at the rim to fierce red-orange at the center; a small bundle of three calendar leaves tied with twine and a slender thermometer laid across them pinned like a wax seal at the lower edge of the disc. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny falling leaf. Colors: copper dominant, ember red-orange, ash gray, small twine-and-thermometer accent.
```

**Meteorological Winter** → `masters/celestial/seasons/badges/meteorological/Winter.png`
```
Ornate circular badge, vivid allegorical enamel in weathered copper cameo, engraved growth-ring field, photorealistic render, perfectly centered, isolated on white background. Center: a single bare tree standing alone in deep snow under a moonlit midnight-blue sky, icicles on its lowest branch catching cold silver-blue light; glossy growth-ring field of concentric rings deepening to the darkest midnight blue at the center; a small bundle of three calendar leaves tied with twine and a slender thermometer laid across them pinned like a wax seal at the lower edge of the disc. Border: weathered verdigris-copper ring with a wheel-of-the-year quarter-spoke motif, four small copper-patina roundels at the cardinal turning points bearing a tiny icicle. Colors: copper dominant, deep midnight blue, frost silver, small twine-and-thermometer accent.
```
