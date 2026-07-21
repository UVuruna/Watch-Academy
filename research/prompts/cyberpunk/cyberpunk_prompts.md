# Cyberpunk 2077 — the Three-Circle Weekday Theme (Gemini/ChatGPT)

Owner-sealed rosters, 2026-07-22 (GAMING + CORPORATION SHEET WAVE): a
NEW weekday theme with THREE parallel casts riding the same nine
seats, the same generalized "Two Rosters" doctrine `wow_prompts.md`
uses (`CANON.md`, two → three). **Gangs**, **Street** and **Power** are
three circles of Night City — the factions that hold territory, V's own
found family, and the powers that move behind them all — each riding
the SAME nine weekday seats (six days, a Throne/Mirror dual, an Unfound
Ninth) with its own cast. `Throne` / `Mirror` / `Unfound` name the
Ruler / Servant(dual) / Ninth(Excluded) seats, same vocabulary
`wow_prompts.md` establishes.

**Register — TWO deliberately different objects, the project-wide
law (corrected 2026-07-22):** `primary` is a MONOCHROME AGED-BRONZE
CARVED RELIEF — a sculpture in ONE metal (warm bronze patina, darker
recesses, polished highlights; no other colors, no enamel, no
gang-neon paint), every emblem carved as relief in the same bronze —
this is the recolor master the metal-shade pipeline strikes gold/
silver from, the same law `greek_prompts.md`'s planetary bronze plates
set. `colored` is the vivid full-saturated neon-noir-poster version — a
fresh full-color repaint, never a recolor of the bronze art, still
carrying each gang/faction's OWN canonical in-game neon color
(Maelstrom's toxic acid-green, Arasaka's imperial crimson, and so on,
named per entry below). The two MUST read as different objects — a
sculpture, not a painting — never near-duplicates of each other. The
BORDER motif — a continuous circuit-trace (PCB) ring broken by four
small roundels, one bearing that day's ruling-planet glyph, carved in
bronze relief on `primary` and recut in chrome/neon on `colored` —
stays constant across all three blocks, the same house convention
every weekday sheet's roundels use. Every plate carries a `primary/`
aged-bronze-relief version and a `colored/` full-saturated poster
version — the per-figure IDENTITY survives entirely through the scene
itself, never through paint.

**Derivation check (Rule #19):** every plate is an irreducible scene —
a different figure or faction, a different beat; `primary`/`colored` is
a fresh repaint, not a tint pass, same as every sibling sheet. The
ROTATION seats below (see next section) are NOT a derivable recolor
either — Aldecaldos and Mox are two different collectives in two
different scenes sharing one SEAT, not one artwork retinted; each
rotation sibling gets its own full, independently-generated brief.
Nothing here is a candidate for algorithmic collapse.

**House rules:** photorealistic render, isolated background (no
transparency-checkerboard artifact), the circular medallion shape IS
the frame, NO lettering anywhere in any image (title plates are the
one documented exception, tracked in their own file — see the
cross-reference at the bottom).

**Drop paths:** `assets/weekday/cyberpunk/<block>/primary/<Stem>.png`
and `assets/weekday/cyberpunk/<block>/colored/<Stem>.png` — `<block>`
is `gangs`, `street` or `power`, both flat, no `dual/` subfolder (DUAL
FLATTEN convention).

## The rotation convention — canonical vs. alt vs. alt2

Several Gangs and Street seats hold MORE THAN ONE named faction/figure,
rotating on the same seat. This is a genuinely new pattern for this
sheet family (every prior weekday theme seats exactly one figure per
day) — implemented here the same way the era calendar's Byzantine v2
already proved out (`era_prompts.md`, `COVERAGE.md` §Era Terms):
`config.defaults.rotating_art_file` pools a seat's candidates from its
canonical file's OWN STEM (`<Stem>.png` / `<Stem>_v*.png`) in the
canonical directory UNION the same stems one level down in `alt/`, then
picks by the date's ordinal — so **the alt/alt2 sibling's file is named
after the SEAT's canonical stem, never the alt figure's own name.**
Concretely, for the Tuesday Gangs seat (Maelstrom canonical / Barghest
alt / Wraiths alt2):

| Slot | Figure | File |
|---|---|---|
| canonical | Maelstrom | `primary/Maelstrom.png` |
| alt | Barghest | `primary/alt/Maelstrom.png` |
| alt2 | Wraiths | `primary/Maelstrom_v2.png` |

Three candidates, one shared stem ("Maelstrom"), exactly the pooling
`_rotation_candidates` already performs — no code change needed beyond
calling `rotating_art_file` on this seat once wiring lands (future
round, out of this sheet's scope). Every rotation seat below is written
out fully — a complete, independent brief per named figure/faction, not
a placeholder — per the round brief's "briefs for ALL" instruction.

**Power's trio carries a SYNCHRONIZED PAIR ROTATION**, not an
independent one: Throne, Mirror and Unfound each hold exactly TWO
candidates (canonical + one `alt/` sibling), so `_pick_rotation`'s
shared `on_date.toordinal() % len(candidates)` naturally lands on the
SAME index for all three seats on any given date — the identical
mechanism that already keeps Judas and Lucifer "IN STEP" across the
Scale badges (`defaults.scale_variant_file`'s own docstring: "one index
driving two independent counts"). No special-case code is needed; the
lockstep is a consequence of every pole owning the same candidate
count, not a separate synchronization flag.

---

## Gangs

The territory-holders. Rotation pairs share a seat via the `alt/`
convention above; every canonical AND every alt/alt2 sibling gets its
own full brief.

| Day | Arm color · vice/virtue | Figure(s) | Rotation |
|---|---|---|---|
| Monday | blue · Fear/Serenity | **Aldecaldos** / Mox (alt) | 2-way |
| Tuesday | orange · Wrath/Courage | **Maelstrom** / Barghest (alt) / Wraiths (alt2) | 3-way |
| Wednesday | purple · Greed/Wisdom | **Voodoo Boys** / 6th Street (alt) | 2-way |
| Thursday | yellow · Excess/Generosity | **Tyger Claws** | none |
| Friday | red · Jealousy/Love | **Valentinos** | none |
| Saturday | green · Envy/Patience | **Animals** / Scavengers (alt) | 2-way |
| Sunday (Throne) | white-gold · Pride/Justice | **Arasaka** | none |
| Sunday (Mirror, dual) | black-silver · Servility/Humility | **Militech** | none |
| Ninth (Unfound) | — | **Netwatch** | none |
| Title plate | — | **Gangs of Night City** | — |

### Monday — Aldecaldos / Mox

*The nomad convoy's own safety, and the fear of the corpo world always
one raid away from breaking the circle.*

**Aldecaldos** → `assets/weekday/cyberpunk/gangs/primary/Aldecaldos.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: an Aldecaldos convoy circled at night around a low fire, sun-bleached orange-and-tan car hoods forming a ring like a wagon-fort, a lone scout's silhouette watching the dark horizon beyond the firelight. Border: a continuous circuit-trace (PCB) ring carved in bronze relief, broken by four small roundels, one bearing the Moon crescent glyph in bronze relief. NO lettering anywhere.
```

**Aldecaldos (colored)** → `assets/weekday/cyberpunk/gangs/colored/Aldecaldos.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: the Aldecaldos convoy in full color, sun-bleached orange and rust-tan car hoods circled around a low campfire under a deep-blue Badlands night, a scout's silhouette on watch at the ring's edge. Border: the circuit-trace ring recut in warm chrome, four glitch-glyph roundels, one flickering a pale-blue Moon crescent. Colors: convoy orange, desert tan, deep dusk blue, firelight amber.
```

**Mox (alt)** → `assets/weekday/cyberpunk/gangs/primary/alt/Aldecaldos.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Mox sentinel in hot-pink-and-lavender leathers standing watch at Lizzie's Bar's own neon-lit doorway, one hand resting easy near a holstered pistol, her stance relaxed but her eyes scanning the street beyond the threshold. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Moon crescent glyph in bronze relief. NO lettering anywhere.
```

**Mox (alt, colored)** → `assets/weekday/cyberpunk/gangs/colored/alt/Aldecaldos.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Mox sentinel in full color, hot-pink-and-lavender leather at Lizzie's Bar's glowing neon doorway, one hand near a holstered pistol, eyes on the street. Border: the circuit-trace ring recut in warm chrome, four glitch-glyph roundels, one flickering a pale-blue Moon crescent. Colors: hot pink, lavender neon, deep-blue night, chrome doorway.
```

### Tuesday — Maelstrom / Barghest / Wraiths

*Wrath at its most raw — cybernetic overgrowth, PMC discipline, and
Badlands cold, three faces of the same fire (the three-face rotation).*

**Maelstrom** → `assets/weekday/cyberpunk/gangs/primary/Maelstrom.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Maelstrom enforcer bristling with exposed chrome and cybernetic overgrowth, both arms replaced by heavy weapon-limbs raised mid-swing, a wall of scavenged machine parts welded into a barricade behind him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Maelstrom (colored)** → `assets/weekday/cyberpunk/gangs/colored/Maelstrom.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Maelstrom enforcer in full color, raw chrome overgrowth and exposed wiring, heavy weapon-arms raised, acid-green optic implants glowing, a barricade of welded scrap behind him. Border: the circuit-trace ring recut in scorched chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: acid green, ember orange, raw chrome, scorched black.
```

**Barghest (alt)** → `assets/weekday/cyberpunk/gangs/primary/alt/Maelstrom.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Barghest operator in disciplined ex-Militech tactical gear, rifle held low-ready rather than swinging wild, a squad's hand-signal frozen mid-order — precision replacing chaos as this Wrath's own shape. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Barghest (alt, colored)** → `assets/weekday/cyberpunk/gangs/colored/alt/Maelstrom.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Barghest operator in full color, navy-and-olive tactical armor, rifle held low-ready, a squad hand-signal frozen mid-order. Border: the circuit-trace ring recut in gunmetal chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: navy blue, olive drab, gunmetal grey, tactical black.
```

**Wraiths (alt2)** → `assets/weekday/cyberpunk/gangs/primary/Maelstrom_v2.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Wraith raider in white-and-grey Badlands wraps, a cryo-frost weapon exhaling a thin white vapor, standing atop a frozen, snow-dusted wreck in the open waste — wrath frozen down to something patient and lethal instead of hot. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Wraiths (alt2, colored)** → `assets/weekday/cyberpunk/gangs/colored/Maelstrom_v2.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Wraith raider in full color, white-and-grey wraps, a cryo weapon venting white vapor, standing on a frost-dusted wreck. Border: the circuit-trace ring recut in frost-pale chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: ice white, frost blue, wasteland grey, vapor-white glow.
```

### Wednesday — Voodoo Boys / 6th Street

*Forbidden net-wisdom against a borrowed flag's own self-styled
wisdom — greed and cunning in two very different uniforms.*

**Voodoo Boys** → `assets/weekday/cyberpunk/gangs/primary/VoodooBoys.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Voodoo Boys netrunner deep in trance, veve sigils glowing teal across his bared skin, both hands raised into a cascade of raw code, a small distant glimpse of the Blackwall's own storm visible in the data behind him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mercury glyph in bronze relief. NO lettering anywhere.
```

**Voodoo Boys (colored)** → `assets/weekday/cyberpunk/gangs/colored/VoodooBoys.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Voodoo Boys netrunner in full color, dark skin lit by glowing teal veve sigils, hands raised into cascading green code, the storming Blackwall glimpsed faint behind him. Border: the circuit-trace ring recut in dark chrome, four glitch-glyph roundels, one flickering a purple Mercury glyph. Colors: teal, code green, deep black, Blackwall violet-grey.
```

**6th Street (alt)** → `assets/weekday/cyberpunk/gangs/primary/alt/VoodooBoys.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a 6th Street patriot in faded stars-and-stripes gear, standing sentry over a checkpoint of stacked tires and painted oil drums, one hand raised to wave a car through, his gaze equal parts protective and proprietary over the block he's claimed. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mercury glyph in bronze relief. NO lettering anywhere.
```

**6th Street (alt, colored)** → `assets/weekday/cyberpunk/gangs/colored/alt/VoodooBoys.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a 6th Street sentry in full color, faded red-white-and-blue gear, standing at a tire-and-drum checkpoint, waving a car through. Border: the circuit-trace ring recut in weathered chrome, four glitch-glyph roundels, one flickering a purple Mercury glyph. Colors: desert tan, faded star-red, checkpoint grey, old-flag blue.
```

### Thursday — Tyger Claws

*Japantown's own neon nightclub law — generosity of pleasure sold at
excess prices.*

**Tyger Claws** → `assets/weekday/cyberpunk/gangs/primary/TygerClaws.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Tyger Claws enforcer in a sharp neon-trimmed suit, katana held loose at his side, standing before a wall of stacked braindance parlor signage and overflowing neon vice-district light, his expression a host's practiced smile over a debt-collector's eyes. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Jupiter glyph in bronze relief. NO lettering anywhere.
```

**Tyger Claws (colored)** → `assets/weekday/cyberpunk/gangs/colored/TygerClaws.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Tyger Claws enforcer in full color, a sharp black suit trimmed in glowing pink neon, katana at his side, a wall of overflowing neon signage behind him. Border: the circuit-trace ring recut in pink-lit chrome, four glitch-glyph roundels, one flickering a yellow Jupiter glyph. Colors: hot pink, neon red, chrome silver, deep night black.
```

### Friday — Valentinos

*Love as fierce territory — jealousy only for whatever threatens the
block that raised him.*

**Valentinos** → `assets/weekday/cyberpunk/gangs/primary/Valentinos.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Valentinos lieutenant in a purple satin jacket, one hand pressed over a gold chain and a small framed photo tucked at his chest, standing before a lowrider hood painted with his own family's name, his stance a wall between the street and everyone he loves behind him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Venus glyph in bronze relief. NO lettering anywhere.
```

**Valentinos (colored)** → `assets/weekday/cyberpunk/gangs/colored/Valentinos.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Valentinos lieutenant in full color, a purple satin jacket over gold chains, a hand over a small framed photo at his chest, a painted lowrider hood behind him. Border: the circuit-trace ring recut in gold-veined chrome, four glitch-glyph roundels, one flickering a red Venus glyph. Colors: purple satin, gold chain, lowrider chrome, warm brown skin.
```

### Saturday — Animals / Scavengers

*Iron discipline against a far darker harvest — the grower and the
harvester of flesh.*

**Animals** → `assets/weekday/cyberpunk/gangs/primary/Animals.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: an Animals bodybuilder mid-lift in a scrapyard gym, muscle-and-chrome physique gleaming with sweat and oil in equal measure, a slow patient count visible on a chalk-marked wall behind him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Saturn glyph in bronze relief. NO lettering anywhere.
```

**Animals (colored)** → `assets/weekday/cyberpunk/gangs/colored/Animals.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: an Animals bodybuilder in full color, oiled muscle-and-chrome physique mid-lift in a scrapyard gym, a chalk-marked tally wall behind him. Border: the circuit-trace ring recut in oiled chrome, four glitch-glyph roundels, one flickering a green Saturn glyph. Colors: burnt orange, oiled tan, scrapyard black, chalk white.
```

**Scavengers (alt)** → `assets/weekday/cyberpunk/gangs/primary/alt/Animals.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: a Scavenger surgeon in a stained apron over an improvised operating table, one hand steady on a chrome bone-saw, rows of harvested organs preserved in glowing green cold-storage jars lining the wall behind — the same iron patience as the Animals' own discipline, turned toward a far darker harvest, taken instead of grown. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Saturn glyph in bronze relief. NO lettering anywhere.
```

**Scavengers (alt, colored)** → `assets/weekday/cyberpunk/gangs/colored/alt/Animals.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Scavenger surgeon in full color, a blood-rust apron, a chrome bone-saw in hand, glowing green cold-storage jars of harvested organs lining the wall. Border: the circuit-trace ring recut in surgical chrome, four glitch-glyph roundels, one flickering a green Saturn glyph. Colors: rust red, surgical green, cold-storage glass-blue, chrome steel.
```

### Sunday (Throne) — Arasaka

*The imperial tower crest — an authority no single person needs to sit
in.*

**Arasaka** → `assets/weekday/cyberpunk/gangs/primary/Arasaka.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Brightly polished bronze relief throughout, the brightest plate of the block. Center: the Arasaka Tower itself rising as a great obsidian-and-crimson spire, its own imperial crest — a stylized eye-in-diamond — blazing at the tower's crown, a thin ring of security drones orbiting it like a crown's own points. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Sun glyph in brightly polished bronze relief. NO lettering anywhere.
```

**Arasaka (colored)** → `assets/weekday/cyberpunk/gangs/colored/Arasaka.png`
```
Ornate circular badge, vivid saturated neon-noir paint over polished bright gold-and-chrome, photorealistic render, perfectly centered, isolated on white background. Center: the Arasaka Tower in full color, a crimson-and-black obsidian spire, its eye-in-diamond crest blazing gold at the crown, a ring of security drones orbiting like a crown's points. Border: the circuit-trace ring recut in polished gold chrome, four glitch-glyph roundels, one flickering a white-gold Sun glyph. Colors: crimson red, obsidian black, imperial gold, chrome drone-silver.
```

### Sunday (Mirror, dual) — Militech

*The eternal corporate war — two towers reflecting. The SAME tower
silhouette as Arasaka's own throne, deliberately.*

**Militech** → `assets/weekday/cyberpunk/gangs/primary/Militech.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief darkened to a near-black patina, the darkest plate of the block — the SAME tower silhouette as Arasaka's own throne, deliberately, a rival spire rising just as tall, crowned with its own crest — a stylized eagle-and-star — in place of the eye-in-diamond. Center: the Militech Tower standing in the identical composition, navy-and-white instead of crimson-and-black, its own drone ring orbiting in perfect mirrored formation — sixty years of corporate war distilled into two towers that have learned to reflect each other exactly. Border: a continuous circuit-trace ring carved in bronze relief, its patina darkened to match, broken by four roundels bearing the Sun glyph in oxidized dark-bronze relief — the same glyph the Throne wears, the shadow face of the same crown. NO lettering anywhere.
```

**Militech (colored)** → `assets/weekday/cyberpunk/gangs/colored/Militech.png`
```
Ornate circular badge, vivid saturated neon-noir paint over dark iron and cold silver, photorealistic render, perfectly centered, isolated on white background — the identical tower composition to the Throne's own colored plate, palette inverted to navy-and-night. Center: the Militech Tower in full color, navy-blue-and-white steel, its eagle-and-star crest glowing silver at the crown, a mirrored drone ring orbiting. Border: the circuit-trace ring recut in dark iron and cold silver, four roundels bearing a dull ember Sun glyph. Colors: navy blue, cold silver, iron black, white trim.
```

### Ninth (Unfound) — Netwatch

*The unseen watchers of the Blackwall — present everywhere, located
nowhere.*

**Netwatch** → `assets/weekday/cyberpunk/gangs/primary/Netwatch.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief fading to bare unpatinated metal at the rim, a light that belongs to no physical place. Center: a faceless Netwatch agent rendered almost as pure code, an outline more than a body, standing before the storming grey wall of the Blackwall itself, watching rather than acting. Border: a continuous circuit-trace ring carved in bronze relief, its own lines fading into bare metal at the top, no roundel glyph — Netwatch answers to no single day. NO lettering anywhere.
```

**Netwatch (colored)** → `assets/weekday/cyberpunk/gangs/colored/Netwatch.png`
```
Ornate circular badge, vivid saturated neon-noir paint over pale static-chrome, photorealistic render, perfectly centered, isolated on white background. Center: a Netwatch agent in full color, a translucent code-outline body barely holding human shape, standing before the storming grey Blackwall. Border: the circuit-trace ring dissolving into static at the top, no day-glyph roundel. Colors: cyan white, storm grey, code blue, static white.
```

---

## Street

V's own circle. Same rotation convention as Gangs.

| Day | Arm color · vice/virtue | Figure(s) | Rotation |
|---|---|---|---|
| Monday | blue · Fear/Serenity | **Viktor Vektor** | none |
| Tuesday | orange · Wrath/Courage | **Jackie** / Panam (alt) / River (alt2) | 3-way |
| Wednesday | purple · Greed/Wisdom | **Wakako** / Padre (alt) | 2-way |
| Thursday | yellow · Excess/Generosity | **Misty** | none |
| Friday | red · Jealousy/Love | **Kerry** / Lizzy Wizzy (alt) | 2-way |
| Saturday | green · Envy/Patience | **Judy** | none |
| Sunday (Throne) | white-gold · Pride/Justice | **Johnny Silverhand** | none |
| Sunday (Mirror, dual) | black-silver · Servility/Humility | **Rogue** | none |
| Ninth (Unfound) | — | **V** | none |
| Title plate | — | **The Afterlife** | — |

### Monday — Viktor Vektor

*The ripperdoc — the one still, quiet room in a city that never stops
cutting.*

**Viktor Vektor** → `assets/weekday/cyberpunk/street/primary/Viktor.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: Viktor Vektor at his ripperdoc's chair, steady hands mid-surgery over an open chrome arm-port, surgical light haloing his bald head, his face calm and unhurried even with a half-finished patient before him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Moon crescent glyph in bronze relief. NO lettering anywhere.
```

**Viktor Vektor (colored)** → `assets/weekday/cyberpunk/street/colored/Viktor.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Viktor in full color, a heavyset bald ripperdoc in a stained apron, steady hands over an open chrome arm-port under warm surgical light. Border: the circuit-trace ring recut in clinic-white chrome, four glitch-glyph roundels, one flickering a pale-blue Moon crescent. Colors: clinic blue, chrome steel, surgical gold, warm skin-tone.
```

### Tuesday — Jackie / Panam / River

*Three faces of Courage: reckless heart, nomad readiness, a lawman's
banked wrath.*

**Jackie** → `assets/weekday/cyberpunk/street/primary/Jackie.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, hot and reckless. Center: Jackie Welles mid-charge, chrome-plated arm raised, a wide grin under a thick mustache, a lucha libre mask hanging from his belt. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Jackie (colored)** → `assets/weekday/cyberpunk/street/colored/Jackie.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Jackie in full color, a broad grinning face and thick mustache, chrome-plated arm raised mid-charge, a lucha mask at his belt. Border: the circuit-trace ring recut in warm chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: ember orange, chrome silver, warm brown skin, mask red.
```

**Panam (alt)** → `assets/weekday/cyberpunk/street/primary/alt/Jackie.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, hot and steady. Center: Panam Palmer braced atop a Basilisk's open hatch, rifle raised toward the Badlands horizon, goggles pushed up into wind-blown hair. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Panam (alt, colored)** → `assets/weekday/cyberpunk/street/colored/alt/Jackie.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Panam in full color, sun-bronzed skin and wind-blown dark hair, braced atop a Basilisk's hatch with a raised rifle, goggles pushed up. Border: the circuit-trace ring recut in dust-tan chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: desert orange, dust tan, gunmetal grey, sun-bronzed skin.
```

**River (alt2)** → `assets/weekday/cyberpunk/street/primary/Jackie_v2.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, steady and righteous. Center: River Ward, ex-NCPD detective, standing his ground in a modest jacket rather than armor, a worn badge held up in one hand though it no longer means what it used to, his gaze fixed forward against a system he no longer trusts. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**River (alt2, colored)** → `assets/weekday/cyberpunk/street/colored/Jackie_v2.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: River in full color, warm brown skin, a modest jacket, a worn badge held up in one hand, his gaze steady and forward. Border: the circuit-trace ring recut in badge-blue chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: badge blue, ember orange, worn denim, warm brown skin.
```

### Wednesday — Wakako / Padre

*Two fixers, two temples — a teahouse den and a converted chapel,
wisdom weighed before any price is named.*

**Wakako** → `assets/weekday/cyberpunk/street/primary/Wakako.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, patient and calculating. Center: Wakako Okada seated at a low table in a quiet teahouse-fixer's den, a data-shard held delicately between two fingers over a spread of untouched tea, her expression unreadable. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mercury glyph in bronze relief. NO lettering anywhere.
```

**Wakako (colored)** → `assets/weekday/cyberpunk/street/colored/Wakako.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Wakako in full color, an elegant older woman in a jade kimono-inspired coat, holding a glowing data-shard over an untouched tea setting. Border: the circuit-trace ring recut in jade-toned chrome, four glitch-glyph roundels, one flickering a purple Mercury glyph. Colors: jade green, deep violet, tea gold, chrome silver.
```

**Padre (alt)** → `assets/weekday/cyberpunk/street/primary/alt/Wakako.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, patient and knowing. Center: Padre in a threadbare clerical collar behind a fixer's makeshift desk inside a converted chapel, a rosary wound once around one wrist beside a stack of eddie-chits, his half-smile equally at home hearing a confession or closing a deal. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mercury glyph in bronze relief. NO lettering anywhere.
```

**Padre (alt, colored)** → `assets/weekday/cyberpunk/street/colored/alt/Wakako.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Padre in full color, a threadbare clerical collar, a rosary at one wrist beside a stack of chits on a chapel desk, candlelight warm on his face. Border: the circuit-trace ring recut in candle-gold chrome, four glitch-glyph roundels, one flickering a purple Mercury glyph. Colors: candle gold, deep violet, worn wood-brown, chrome silver.
```

### Thursday — Misty

*The tarot guide — major arcana motifs, generosity given as freely as
the cards turn.*

**Misty** → `assets/weekday/cyberpunk/street/primary/Misty.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, warm and generous. Center: Misty in flowing esoteric layers behind a table scattered with major arcana tarot cards, one card turned face-up and glowing softly, her hands open in an offering gesture over the spread, incense smoke curling into the holo-light. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Jupiter glyph in bronze relief. NO lettering anywhere.
```

**Misty (colored)** → `assets/weekday/cyberpunk/street/colored/Misty.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Misty in full color, dark flowing layered clothing and warm eyes, a spread of glowing major arcana cards before her, incense smoke curling upward. Border: the circuit-trace ring recut in warm gold chrome, four glitch-glyph roundels, one flickering a yellow Jupiter glyph. Colors: amber gold, incense violet, card gold-leaf, warm candlelight.
```

### Friday — Kerry / Lizzy Wizzy

*A rockerboy legend's restless love, and a pop idol's love of the
spotlight — jealousy in two different registers of fame.*

**Kerry** → `assets/weekday/cyberpunk/street/primary/Kerry.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, warm and restless. Center: Kerry Eurodyne mid-riff on a battered electric guitar under a single spotlight, silver hair falling across his face, a faded Samurai-era backstage pass clipped to his jacket. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Venus glyph in bronze relief. NO lettering anywhere.
```

**Kerry (colored)** → `assets/weekday/cyberpunk/street/colored/Kerry.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Kerry in full color, silver hair and a worn leather jacket, mid-riff on an electric guitar under warm spotlight, a faded backstage pass at his collar. Border: the circuit-trace ring recut in rose-gold chrome, four glitch-glyph roundels, one flickering a red Venus glyph. Colors: rose red, spotlight gold, silver hair, worn leather black.
```

**Lizzy Wizzy (alt)** → `assets/weekday/cyberpunk/street/primary/alt/Kerry.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, dazzling and restless. Center: Lizzy Wizzy mid-performance, twin chrome-bladed cyberarms flashing under stage light, a crowd's worth of adoration implied in the glow around her but her own eyes fixed somewhere just past the camera. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Venus glyph in bronze relief. NO lettering anywhere.
```

**Lizzy Wizzy (alt, colored)** → `assets/weekday/cyberpunk/street/colored/alt/Kerry.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Lizzy Wizzy in full color, platinum hair and a glittering stage outfit, twin chrome-bladed cyberarms flashing under hot-pink stage light. Border: the circuit-trace ring recut in hot-pink chrome, four glitch-glyph roundels, one flickering a red Venus glyph. Colors: hot pink, chrome-blade silver, stage-light white, platinum hair.
```

### Saturday — Judy

*The patient braindance artisan — in no rush to finish a cut she wants
exactly right.*

**Judy** → `assets/weekday/cyberpunk/street/primary/Judy.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, careful and unhurried. Center: Judy Alvarez seated at a braindance editing rig, headset half-lowered, both hands moving with slow deliberate precision over a floating timeline of recorded memory, her focus total. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Saturn glyph in bronze relief. NO lettering anywhere.
```

**Judy (colored)** → `assets/weekday/cyberpunk/street/colored/Judy.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Judy in full color, undercut teal-dyed hair, warm brown skin, seated at a glowing BD editing rig with a headset half-lowered, hands moving over a floating memory-timeline. Border: the circuit-trace ring recut in teal-toned chrome, four glitch-glyph roundels, one flickering a green Saturn glyph. Colors: teal green, warm brown skin, editing-rig blue-white, chrome silver.
```

### Sunday (Throne) — Johnny Silverhand

*Pride crowned — the legend, silver arm, the Samurai jacket.*

**Johnny Silverhand** → `assets/weekday/cyberpunk/street/primary/Johnny.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Brightly polished bronze relief throughout, the brightest plate of the block. Center: Johnny Silverhand enthroned in his own legend, the iconic Samurai jacket worn open over bare chrome, his silver cybernetic arm resting along the armrest like a scepter, an electric guitar leaned against the seat beside him. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Sun glyph in brightly polished bronze relief. NO lettering anywhere.
```

**Johnny Silverhand (colored)** → `assets/weekday/cyberpunk/street/colored/Johnny.png`
```
Ornate circular badge, vivid saturated neon-noir paint over polished bright gold-and-chrome, photorealistic render, perfectly centered, isolated on white background. Center: Johnny in full color, the black Samurai jacket open over a bare chest, a gleaming silver cybernetic arm resting along the armrest, an electric guitar leaned against the throne. Border: the circuit-trace ring recut in polished gold chrome, four glitch-glyph roundels, one flickering a white-gold Sun glyph. Colors: crimson red, silver chrome, jacket black, gold trim.
```

### Sunday (Mirror, dual) — Rogue

*Sixty years reflecting him — the Afterlife queen of the night, his gun
kept behind her bar. The SAME throne silhouette as Johnny's own seat.*

**Rogue** → `assets/weekday/cyberpunk/street/primary/Rogue.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief darkened to a near-black patina, the darkest plate of the block — the SAME throne silhouette as Johnny's own seat, deliberately, a queen's bearing instead of a king's. Center: Rogue seated behind the Afterlife's own bar in the identical enthroned pose, decades written into her face, Johnny's own silver-plated pistol mounted in a place of honor on the wall behind her rather than an armrest. Border: a continuous circuit-trace ring carved in bronze relief, its patina darkened to match, broken by four roundels bearing the Sun glyph in oxidized dark-bronze relief — the same glyph the Throne wears, the shadow face of the same crown. NO lettering anywhere.
```

**Rogue (colored)** → `assets/weekday/cyberpunk/street/colored/Rogue.png`
```
Ornate circular badge, vivid saturated neon-noir paint over dark iron and cold silver, photorealistic render, perfectly centered, isolated on white background — the identical seated composition to the Throne's own colored plate, palette inverted to night. Center: Rogue in full color, silver-streaked dark hair and a sharp black coat, seated behind the Afterlife's bar, Johnny's silver-plated pistol mounted on the wall behind her. Border: the circuit-trace ring recut in dark iron and cold silver, four roundels bearing a dull ember Sun glyph. Colors: iron black, cold silver, warm amber bar-light, silver-streaked hair.
```

### Ninth (Unfound) — V

*The self being overwritten. KEPT DELIBERATELY AMBIGUOUS — a mirrored
visor and a silhouette reading as neither gender, per the owner's own
note.*

**V** → `assets/weekday/cyberpunk/street/primary/V.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief fading to bare unpatinated metal at the rim, a light that belongs to no fixed identity. Center: V rendered as a deliberately AMBIGUOUS silhouette — a mirrored full-face visor reflecting the city back instead of any single face, build and stance read as neither clearly masculine nor feminine, one hand pressed to their own temple where a second flickering silhouette (Johnny's own outline) bleeds faintly through. Border: a continuous circuit-trace ring carved in bronze relief, its own lines doubling at the top, no roundel glyph — V answers to no single day, still becoming. NO lettering anywhere.
```

**V (colored)** → `assets/weekday/cyberpunk/street/colored/V.png`
```
Ornate circular badge, vivid saturated neon-noir paint over pale static-chrome, photorealistic render, perfectly centered, isolated on white background. Center: V in full color, the SAME deliberately ambiguous silhouette, a mirrored visor reflecting neon city color, build read as neither clearly masculine nor feminine, a second flickering outline bleeding faintly through at the temple. Border: the circuit-trace ring glitching and doubling at the top, no day-glyph roundel. Colors: static white, neon city-reflection, flickering double-exposure blue, silhouette black.
```

---

## Power

The forces that move behind Gangs and Street alike. The trio carries
the SYNCHRONIZED PAIR ROTATION described above (each pole's `alt/`
sibling turns in lockstep with the other two, same date, same index).

| Day | Arm color · vice/virtue | Figure | Rotation |
|---|---|---|---|
| Monday | blue · Fear/Serenity | **Songbird** (So Mi) | none |
| Tuesday | orange · Wrath/Courage | **Adam Smasher** | none |
| Wednesday | purple · Greed/Wisdom | **Dexter DeShawn** | none |
| Thursday | yellow · Excess/Generosity | **Solomon Reed** | none |
| Friday | red · Jealousy/Love | **Evelyn Parker** | none |
| Saturday | green · Envy/Patience | **Takemura** | none |
| Sunday (Throne) | white-gold · Pride/Justice | **Saburo Arasaka** / Rosalind Myers (alt) | 2-way, synced |
| Sunday (Mirror, dual) | black-silver · Servility/Humility | **Yorinobu** / Kurt Hansen (alt) | 2-way, synced |
| Ninth (Unfound) | — | **Alt Cunningham** / Rache Bartmoss (alt) | 2-way, synced |
| Title plate | — | **Soulkiller** | — |

### Monday — Songbird (So Mi)

*Fear seeking its cure — red netrunner lines threaded through the
day's own blue.*

**Songbird** → `assets/weekday/cyberpunk/power/primary/Songbird.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout. Center: Songbird slumped against a cold diagnostic wall, breathing mask fogged, both hands pressed over her own chest as red neural warning-lines crawl visibly under her skin, her eyes fixed not on any enemy but on a small distant light she cannot yet reach. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Moon crescent glyph in bronze relief. NO lettering anywhere.
```

**Songbird (colored)** → `assets/weekday/cyberpunk/power/colored/Songbird.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Songbird in full color, pale exhausted skin against a blue-lit wall, fine red neural lines glowing visibly beneath her skin, a fogged breathing mask at her jaw, eyes fixed on a distant light. Border: the circuit-trace ring recut in clinical-blue chrome, four glitch-glyph roundels, one flickering a pale-blue Moon crescent. Colors: clinical blue, warning red, pale skin, distant-light gold.
```

### Tuesday — Adam Smasher

*The machine that was a man — wrath with nothing human left to
restrain it.*

**Adam Smasher** → `assets/weekday/cyberpunk/power/primary/AdamSmasher.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, heavy and merciless. Center: Adam Smasher, a towering full-body cyborg with barely a scrap of visible human tissue left, twin heavy weapon-fists raised, a single unblinking red optic sensor where a face should be, standing in a wreckage-strewn corridor. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mars glyph in bronze relief. NO lettering anywhere.
```

**Adam Smasher (colored)** → `assets/weekday/cyberpunk/power/colored/AdamSmasher.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Adam Smasher in full color, a massive dull-chrome cyborg frame, twin heavy weapon-fists raised, one glowing red optic sensor, standing amid wreckage. Border: the circuit-trace ring recut in scorched gunmetal chrome, four glitch-glyph roundels, one flickering an orange Mars glyph. Colors: gunmetal chrome, ember orange, single red optic, wreckage black.
```

### Wednesday — Dexter DeShawn

*The betrayer-fixer — a fixer's wisdom of the network turned entirely
toward himself.*

**Dexter DeShawn** → `assets/weekday/cyberpunk/power/primary/Dexter.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, smooth and self-serving. Center: Dexter DeShawn in a sharp gold-trimmed suit, a golden prosthetic hand closed around a credchip, his other hand extended for a handshake that is already a betrayal, a hidden second contract folded just out of sight beneath his sleeve. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Mercury glyph in bronze relief. NO lettering anywhere.
```

**Dexter DeShawn (colored)** → `assets/weekday/cyberpunk/power/colored/Dexter.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Dexter in full color, a sharp violet-and-gold suit, a golden prosthetic hand closed around a glowing credchip, a hidden contract folded beneath his sleeve. Border: the circuit-trace ring recut in gold-veined chrome, four glitch-glyph roundels, one flickering a purple Mercury glyph. Colors: deep violet, gold prosthetic, smooth chrome, hidden-contract cream.
```

### Thursday — Solomon Reed

*The FIA handler-teacher — decades of hard-won tradecraft given away
freely.*

**Solomon Reed** → `assets/weekday/cyberpunk/power/primary/Solomon.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, warm and world-weary. Center: Solomon Reed in a weathered field coat, kneeling to steady a younger operative's aim with one guiding hand on their shoulder, his own eyes carrying the excess weight of every asset he has ever had to spend. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Jupiter glyph in bronze relief. NO lettering anywhere.
```

**Solomon Reed (colored)** → `assets/weekday/cyberpunk/power/colored/Solomon.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Solomon in full color, a weathered brown field coat, kneeling with a guiding hand on a younger operative's shoulder, warm amber light on his lined face. Border: the circuit-trace ring recut in warm gold chrome, four glitch-glyph roundels, one flickering a yellow Jupiter glyph. Colors: amber gold, field-coat brown, steady grey, warm skin-tone.
```

### Friday — Evelyn Parker

*The doll — beauty used and broken, the world's own jealous hunger for
it.*

**Evelyn Parker** → `assets/weekday/cyberpunk/power/primary/Evelyn.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, aching and fragile. Center: Evelyn Parker seated at a mirror in doll-perfect makeup and a glittering dress, one hand reaching to touch her own reflection rather than her real face, the mirror's surface subtly cracked at the edges. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Venus glyph in bronze relief. NO lettering anywhere.
```

**Evelyn Parker (colored)** → `assets/weekday/cyberpunk/power/colored/Evelyn.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Evelyn in full color, doll-perfect makeup and a glittering rose-gold dress, reaching to touch her own cracked mirror reflection. Border: the circuit-trace ring recut in rose-gold chrome, four glitch-glyph roundels, one flickering a red Venus glyph. Colors: rose red, mirror-silver, porcelain skin, cracked-glass white.
```

### Saturday — Takemura

*The patient samurai retainer — patience as the last loyalty he has
left to give.*

**Takemura** → `assets/weekday/cyberpunk/power/primary/Takemura.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Warm aged-bronze relief throughout, still and disciplined. Center: Goro Takemura kneeling in formal seiza posture, a katana laid across his knees rather than drawn, his gaze steady on a small photograph propped before him of an era already gone. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Saturn glyph in bronze relief. NO lettering anywhere.
```

**Takemura (colored)** → `assets/weekday/cyberpunk/power/colored/Takemura.png`
```
Ornate circular badge, vivid saturated neon-noir paint over brushed chrome, photorealistic render, perfectly centered, isolated on white background. Center: Takemura in full color, formal dark green-and-black attire, kneeling in seiza with a katana across his knees, a small photograph propped before him. Border: the circuit-trace ring recut in jade-toned chrome, four glitch-glyph roundels, one flickering a green Saturn glyph. Colors: jade green, formal black, katana silver, warm photograph sepia.
```

### Sunday (Throne) — Saburo Arasaka / Rosalind Myers

*An emperor's stillness and a handler's stillness — the same seat, two
different empires. Synchronized with Mirror and Unfound below.*

**Saburo Arasaka** → `assets/weekday/cyberpunk/power/primary/SaburoArasaka.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Brightly polished bronze relief throughout, the brightest plate of the block. Center: Saburo Arasaka enthroned in a formal dark suit within his own tower's highest office, the Arasaka eye-in-diamond crest inlaid in the floor beneath his seat, his hands folded with absolute stillness. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Sun glyph in brightly polished bronze relief. NO lettering anywhere.
```

**Saburo Arasaka (colored)** → `assets/weekday/cyberpunk/power/colored/SaburoArasaka.png`
```
Ornate circular badge, vivid saturated neon-noir paint over polished bright gold-and-chrome, photorealistic render, perfectly centered, isolated on white background. Center: Saburo in full color, silver-grey hair and a formal dark suit, seated with folded hands over the glowing gold Arasaka crest inlaid beneath him. Border: the circuit-trace ring recut in polished gold chrome, four glitch-glyph roundels, one flickering a white-gold Sun glyph. Colors: crimson red, imperial gold, formal black, silver hair.
```

**Rosalind Myers (alt)** → `assets/weekday/cyberpunk/power/primary/alt/SaburoArasaka.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Brightly polished bronze relief throughout, the brightest plate of the block — the SAME enthroned composition, an authority that answers to no visible tower at all. Center: Rosalind Myers seated in the identical formal stillness inside a windowless FIA office, a wall of sealed case-files standing in for the Arasaka crest behind her, her folded hands carrying the same unshowy certainty — a different empire, the same seat. Border: a continuous circuit-trace ring carved in bronze relief, broken by four small roundels, one bearing the Sun glyph in brightly polished bronze relief. NO lettering anywhere.
```

**Rosalind Myers (alt, colored)** → `assets/weekday/cyberpunk/power/colored/alt/SaburoArasaka.png`
```
Ornate circular badge, vivid saturated neon-noir paint over polished bright gold-and-chrome, photorealistic render, perfectly centered, isolated on white background — the identical seated composition to Saburo's own colored plate. Center: Rosalind in full color, silver-streaked dark hair and a severe formal suit, seated with folded hands before a wall of sealed case-files. Border: the circuit-trace ring recut in polished gold chrome, four glitch-glyph roundels, one flickering a white-gold Sun glyph. Colors: crimson red, muted federal gold, formal black, silver-streaked hair.
```

### Sunday (Mirror, dual) — Yorinobu / Kurt Hansen

*The son the father returns through, and the colonel who built his own
midnight state. The SAME throne silhouette as the Throne's own seat.*

**Yorinobu** → `assets/weekday/cyberpunk/power/primary/Yorinobu.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief darkened to a near-black patina, the darkest plate of the block — the SAME throne silhouette as Saburo's own seat, deliberately. Center: Yorinobu Arasaka seated in the identical composition, younger and restless where his father was still, the same eye-in-diamond crest beneath him now cracked through its center, his father's own engram flickering faintly in the air just behind his shoulder like a shadow that refuses to leave. Border: a continuous circuit-trace ring carved in bronze relief, its patina darkened to match, broken by four roundels bearing the Sun glyph in oxidized dark-bronze relief — the same glyph the Throne wears, the shadow face of the same crown. NO lettering anywhere.
```

**Yorinobu (colored)** → `assets/weekday/cyberpunk/power/colored/Yorinobu.png`
```
Ornate circular badge, vivid saturated neon-noir paint over dark iron and cold silver, photorealistic render, perfectly centered, isolated on white background — the identical seated composition to the Throne's own colored plate, palette inverted to night. Center: Yorinobu in full color, dark tousled hair and an open black jacket, seated over a cracked gold crest, his father's translucent blue engram-figure flickering faintly behind his shoulder. Border: the circuit-trace ring recut in dark iron and cold silver, four roundels bearing a dull ember Sun glyph. Colors: iron black, cold silver, engram blue, cracked-gold accent.
```

**Kurt Hansen (alt)** → `assets/weekday/cyberpunk/power/primary/alt/Yorinobu.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief darkened to a near-black patina, the darkest plate of the block — the SAME throne silhouette, a different kind of usurped seat. Center: Colonel Kurt Hansen seated in the identical composition inside a fortified compound of his own making, a hand-painted militia insignia standing in for any corporate crest, a wall of surveillance screens flickering behind him like a throne room built entirely from stolen watchfulness. Border: a continuous circuit-trace ring carved in bronze relief, its patina darkened to match, broken by four roundels bearing the Sun glyph in oxidized dark-bronze relief. NO lettering anywhere.
```

**Kurt Hansen (alt, colored)** → `assets/weekday/cyberpunk/power/colored/alt/Yorinobu.png`
```
Ornate circular badge, vivid saturated neon-noir paint over dark iron and cold silver, photorealistic render, perfectly centered, isolated on white background — the identical seated composition to the Throne's own colored plate. Center: Kurt Hansen in full color, a grizzled militia uniform, seated before a wall of flickering surveillance screens standing in for a crest. Border: the circuit-trace ring recut in dark iron and cold silver, four roundels bearing a dull ember Sun glyph. Colors: iron black, cold silver, screen blue, militia-olive accent.
```

### Ninth (Unfound) — Alt Cunningham / Rache Bartmoss

*She taken by the Wall, he the one who broke it; body in a fridge, mind
in the net. Two legends dissolved into the same net-space.*

**Alt Cunningham** → `assets/weekday/cyberpunk/power/primary/AltCunningham.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief fading to bare unpatinated metal at the rim, a light with no physical source. Center: Alt Cunningham rendered as a luminous translucent presence made entirely of code, no body left behind her at all, standing within the storming architecture of the Blackwall itself as though it were both her prison and her only remaining home. Border: a continuous circuit-trace ring carved in bronze relief, its own lines fading into bare metal at the top, no roundel glyph — Alt answers to no single day. NO lettering anywhere.
```

**Alt Cunningham (colored)** → `assets/weekday/cyberpunk/power/colored/AltCunningham.png`
```
Ornate circular badge, vivid saturated neon-noir paint over pale static-chrome, photorealistic render, perfectly centered, isolated on white background. Center: Alt in full color, a translucent glowing code-blue figure with no solid body, standing within the storming grey architecture of the Blackwall. Border: the circuit-trace ring dissolving into static at the top, no day-glyph roundel. Colors: static white, storm grey, translucent code-blue, faint human-outline silver.
```

**Rache Bartmoss (alt)** → `assets/weekday/cyberpunk/power/primary/alt/AltCunningham.png`
```
ROUND medallion, aged bronze relief, photorealistic render, isolated background, the circular shape IS the frame. Aged bronze relief fading to bare unpatinated metal at the rim — the SAME dissolving composition, the other half of the same old net-legend. Center: Rache Bartmoss rendered as a ragged, half-corporeal netrunner silhouette, a physical body reduced to a single cryo-fridge glimpsed faintly in the static behind him while his mind sprawls vast and formless through the net he himself tore open. Border: a continuous circuit-trace ring carved in bronze relief, its own lines fading into bare metal at the top, no roundel glyph. NO lettering anywhere.
```

**Rache Bartmoss (alt, colored)** → `assets/weekday/cyberpunk/power/colored/alt/AltCunningham.png`
```
Ornate circular badge, vivid saturated neon-noir paint over pale static-chrome, photorealistic render, perfectly centered, isolated on white background — the identical dissolving composition to Alt's own colored plate. Center: Rache in full color, a ragged half-transparent figure fraying into green breach-static, a small glimpse of a cryo-fridge visible faintly behind him. Border: the circuit-trace ring dissolving into static at the top, no day-glyph roundel. Colors: static white, breach-static green, translucent code-blue, fridge-frost pale.
```

---

## Cross-reference — the title plates

Three title plates, one per block. Briefs and drop paths live in
[Theme Title Prompts](../titles/theme_title_prompts.md), NOT here — see
that sheet's own "Cross-referenced" section. Do not duplicate the
briefs in this file.

- **Gangs** → `assets/titles/cyberpunk_gangs.png`. Brief: Night City's
  own district map as a glowing neon mosaic, one tile per resident
  gang's canonical color (the owner's own suggestion).
- **Street** → `assets/titles/cyberpunk_street.png`. Brief: The
  Afterlife's bar interior, the whole circle implied by empty stools
  and one untouched glass (the owner's own suggestion).
- **Power** → `assets/titles/cyberpunk_power.png`. Brief: SOULKILLER —
  NOT a person, the FORCE: a human silhouette dissolving between living
  flesh and cold code, neither a heartbeat nor a flat-line ever
  resolving — the parent of this block's own ghosts (Alt Cunningham and
  Rache Bartmoss both live and die by exactly this program), the same
  "parent, not seat-holder" device as `wow_evil`'s Sargeras and Greek
  Monsters' Typhon & Echidna.

---

## Status

- **PRIMARY BRIEFS CORRECTED 2026-07-22:** the first generation pass
  across the gaming + corporation wave produced near-duplicate
  primary/colored pairs — a color palette (gang/faction neon) had
  leaked into the primary-register briefs, contradicting the project's
  monochrome aged-bronze-relief law (`greek_prompts.md`). Every
  primary brief in this sheet has been rewritten to the aged-bronze
  convention; composition/scene/pose text is untouched. The COLORED
  outputs already generated are VALID, no regeneration needed. Any
  PRIMARY output generated before this fix (confirmed at least for WoW
  Alliance: Anduin, Khadgar, Muradin) must be REGENERATED from the
  corrected briefs above.
- New sheet (R10 GAMING + CORPORATION SHEET WAVE, owner-sealed rosters
  2026-07-22). Theme not yet registered in `config/defaults.py` — that
  wiring, AND the `rotating_art_file` wiring the rotation seats above
  need, are FUTURE app-code rounds, out of this sheet-writing round's
  scope ("Sheets ONLY... NO app code"). `assets/weekday/**` is a
  data-driven root, so every path in this sheet — including every
  `alt/` and `_v2` rotation sibling — passes the sheet-path lint today
  with no whitelist entry needed.
- **Rotation seats: 5 in Gangs/Street (2-way ×4, 3-way ×1), 3 in Power
  (all 2-way, synchronized as one triad)** — every canonical AND alt/
  alt2 sibling is written out as a full independent brief per the round
  brief's "briefs for ALL" instruction; none are placeholders.
- **Art: 0/78** — Gangs 14 figures × 2 = 28, Street 13 figures × 2 = 26,
  Power 12 figures × 2 = 24 (the 3 title plates are tracked separately
  in [Theme Title Prompts](../titles/theme_title_prompts.md), see
  above).
- Verify with `python main.py "research/prompts/cyberpunk/cyberpunk_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner.
