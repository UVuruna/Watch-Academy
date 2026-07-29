# The Instrument — Prompt & Shot Sheet (Gemini + Screenshots)

The Encyclopedia's "The Instrument" group (`Database/encyclopedia.json` →
`instrument`, 8 articles) currently ships with NO images at all. This
sheet covers all 8, plus the topic's own section logo: for each article
it either gives an exact screenshot instruction (the app already draws
the thing being explained — no art needed, just a careful capture) or a
Gemini prompt / existing-asset pointer for the handful that are genuine
abstractions rather than on-screen geometry. Paste prompts one at a
time; keep the two Gemini images in one chat session so they read as a
matched pair.

> **SUPERSEDED FOR SEVEN OF THE EIGHT (owner verdict 2026-07-29, root
> Rule #19).** `dial`, `solar_rotation`, `twilight`, `year_wheel`,
> `moon_lunations`, `metals` and `ring_letters` are no longer files at
> all — the program DRAWS them, live, from the same constants the dial
> itself is drawn from (see
> [Instrument Diagrams](../../../render/instrument_diagrams.md)). **Do
> not capture the five screenshots this sheet plans below, and do not
> generate anything for `metals` or `ring_letters`.** A stored capture
> of a live geometry is exactly the asset Rule #19 forbids: it is right
> only until the geometry moves, and then it is a picture that lies
> while the article beside it tells the truth. `paint_light` (a
> doctrine, not a geometry) and the section `logo` are UNCHANGED and
> still belong to this sheet.
>
> The same verdict retired the Great Oscillations plate on the Eras
> topic — its figure is the La2004 envelope the Observatory already
> plots.

Suggested drop locations:
- `assets/instrument/logo.png` — the section logo
- `assets/instrument/paint_light.png` — the one abstract-concept Gemini image
- Encyclopedia screenshots: wherever the owner's existing capture
  pipeline drops raw grabs before processing (see Delivery, below)
- `metals` and `ring_letters` need no new files — see their sections

---

## Design Notes — the Instrument's own house family

None of the earlier families (Virtue's gold cameo, Sin's blackened
iron, Mood's silver, Trinity's brushed bronze, Seasons' weathered
copper, Turning Points' split gold-silver) is a mechanism — they are
all allegorical scenes. The Instrument is the odd one out: it is the
dial ITSELF being explained, so its two Gemini images (the section
logo and the Paint/Light split) get their own family, aged bronze with
an engraved gear-tooth field, deliberately mechanical rather than
mythological:

| Family | Field | Border metal & motif | Reading |
|---|---|---|---|
| Instrument | engraved **gear-tooth** ring, fine machine-cut teeth | **aged bronze** relief, tick-tooth rim echoing the dial's own 360-mark band | the one family that is a device, not a myth — the encyclopedia explaining its own works |

This also keeps the logo unmistakably apart from the Zodiac section's
own logo (`assets/calendars/zodiac/astrology/primary/logo/`) — the brief below repeats "not a
zodiac" inside the prompt itself because a bare circular dial with a
ring of numerals is exactly the kind of image Gemini defaults toward
astrology art unless told otherwise.

One correction to the brief that generated this sheet:
`season_trinity_prompts.md`'s actual prompts specify **"isolated on
white background,"** not a dark neutral background — every prompt
below follows the real file (white, photorealistic, perfectly
centered) rather than the paraphrase.

---

## Section logo — aged bronze cameo, gear-tooth field

**The Instrument section logo** → `assets/instrument/logo.png`

```
Ornate circular badge, aged bronze relief, engraved gear-tooth field, photorealistic render, perfectly centered, isolated on white background. Center: a weathered brass instrument face — a full 24-hour clock, noon marked at the very top and midnight at the very bottom, a slender hour hand standing partway down the right side and a thinner minute hand ticking just past it, fine engraved numerals running once around the rim from 1 to 24, small exposed gears and a tiny pendulum bob visible beneath the hands where the mechanism shows through the case. Read plainly as a working timekeeping instrument, NOT a zodiac wheel: no star signs, no constellations, no astrological glyphs anywhere on the face or the border. Border: aged bronze ring machined with fine tick-tooth relief like the dial's own 360-degree rim, four small dark-patina roundels at the cardinal points each bearing a tiny embossed cog. Colors: aged bronze dominant, warm brass highlight, deep patina shadow.
```

---

## The 24-Hour Dial (`dial`) — SCREENSHOT

The whole point of this article — noon at top, midnight at bottom, the
hour hand's once-a-day sweep, the 13/11/48/288 tick hierarchy — is the
app's own baseline rendering. No Gemini art needed.

- **Shot A (whole dial):** any pointer variant, no Time Travel needed.
  Pick a moment where the hour hand sits clearly between noon and
  midnight (mid-morning or mid-afternoon works best) so its 15°/hour
  crawl reads as a distinct angle from the minute hand's ordinary
  sweep — the two roles should look visibly different at a glance.
  Frame the full circular face.
- **Shot B (rim close-up):** crop tight on one quadrant of the rim
  (e.g. the 10h–14h arc around the noon arrow) so the tick hierarchy is
  legible: the brightest 12h arrow, the ordinary odd-hour white arrows,
  the gray even-hour ticks, and the fine minute subdivisions between
  them all in one frame.

---

## Solar Rotation and the Hexagram (`solar_rotation`) — SCREENSHOT

The hexagram's lean off vertical IS the measurement the article
describes — capture the tilt itself rather than illustrating it.

- City = Belgrade (matches the project's own golden test values: the
  hexagram tilt there swings from −4.17° to +10.76° across the
  DST changeover). Time Travel to one date on each side of the
  spring-forward/fall-back transition, same city, and capture both —
  side by side they show the tilt's sign flip.
- Frame the whole dial so the star's lean is visible against the
  vertical noon tick above it; a slight zoom on just the star and the
  12h/24h ticks is fine if the full-dial shot makes the tilt too small
  to read.

---

## Twilight (`twilight`) — SCREENSHOT

The dawn (blue, 06h side) and dusk (brown, 18h side) bands are drawn
as static arcs sized to that day's actual sunrise/sunset/dawn/dusk
times — they sit at their fixed clock positions all day, so a single
capture at ANY time shows both together.

- **Shot A (ordinary asymmetry):** City = Belgrade (or the project's
  mockup day, 20 June 2025 — sunrise 04:52 / sunset 20:27). Capture the
  whole dial; both the blue civil-twilight arc near 06h and the brown
  one near 18h should be visible in the same frame.
- **Shot B (extreme swelling):** City = Tromsø, high summer (around 21
  June). At this latitude civil twilight can stretch for hours or never
  fully resolve (the project's own WHITE_NIGHTS/TWILIGHT_ONLY regimes)
  — capture the dial so the swollen band is obviously much wider than
  the ordinary ~9° arc from Shot A.

---

## The Year Wheel (`year_wheel`) — SCREENSHOT

The equal-90°-per-season wheel and the true equinox/solstice anchors
are the app's own Seasons/Compass rendering.

- Pointer = **Quaternity** (cross) — shows the year-wheel marker and the
  tropical zodiac ring directly.
- Time Travel to a solstice or equinox date near local noon (e.g. 21
  June for the summer solstice, 23 September for the autumn equinox)
  so the marker sits visibly at a cardinal point — top/bottom for the
  solstices, the 90°/270° left-right corners for the equinoxes.
- Capture the whole dial; if the pointer supports a hover/legend
  popup on the marker, include it — the base article specifically
  invites reading "a third of the way through spring" off the angle.

---

## The Moon Wheel and the Lunations (`moon_lunations`) — SCREENSHOT

- Pointer = **Seasons** (the moon marker rides the same year wheel).
- Time Travel to a date near full moon for a clearly lit marker, or
  reuse the project's own golden test date, 2026-07-07 (moon
  illumination 0.7400, waxing gibbous), for a value already verified
  elsewhere in the project.
- Capture the whole dial with the moon marker's glow visible on the
  wheel; hover it if possible to include the legend popup (lunation
  ordinal + illumination % + phase name + cycle day) since the article
  spends real space on exactly that counting rule.

---

## Paint and Light (`paint_light`) — GEMINI PROMPT

**Paint and Light** → `assets/instrument/paint_light.png`

Genuinely abstract: pre-Newton pigment theory vs. post-Newton light
theory, and the one twist the article hangs everything on — mixed
paint goes to mud (the Sun stays unpainted, unmixable) while summed
light goes to white (the Sun becomes literally the sum of the six
beams). Nothing on screen shows this; it needs its own image.

```
Ornate circular badge, aged bronze relief, engraved gear-tooth field, photorealistic render, perfectly centered, isolated on white background. Center: the disc split cleanly down the middle. Left half: a wooden painter's palette holding six blobs of pigment — yellow, red and blue at its points, orange, green and violet mixed between them — a sable brush laid across it, the palette's own center smeared into a dull muddy brown where all six colors have been stirred together. Right half: a glass prism suspended in a single beam of white light, splitting it into red, green and blue beams that cross and recombine into one bright white spot on a small screen. Straddling the seam between the two halves, one small brass sun disc: on the paint side it is left bare, unpainted bronze, the one shade the palette could never mix; on the light side the same disc glows pure white, the sum of the three beams landing on it. Border: aged bronze ring machined with fine tick-tooth relief like the dial's own 360-degree rim, small roundels at the cardinal points alternating a tiny paintbrush and a tiny prism. Colors: bronze dominant, muddy brown pigment mix on the left, pure RGB spectrum on the right, bare brass and white light at the seam.
```

---

## Gold, Silver, Bronze (`metals`) — REUSE

The article's own core image — gold to the Sun, silver to the Moon,
bronze as the ambient plate finish everything else is struck in — is
already sitting in the asset tree, generated for the weekday alchemy
set and needing no rework:

- **Gold:** `assets/weeks/crafts/alchemy/primary/colored/Gold.png` — crucible pouring molten
  gold beside a polished sun-face disc, exactly "gold to the Sun."
- **Silver:** `assets/weeks/crafts/alchemy/primary/colored/Silver.png` — half-polished,
  half-tarnished mirror-disc and chalice, exactly "silver to the Moon."
- **Bronze:** no dedicated medallion exists (or is needed) — bronze is
  the default, ambient finish of dozens of existing plates project-wide
  (every weekday god, every profession, every ring letter). If the
  article wants one concrete bronze image anyway, reuse
  `assets/instrument/guide/63_ring_domy_bronze.png` — an actual in-app screenshot
  of the DOMY ring struck in plain bronze, already owner-captured and
  processed for the Guide.

No new Gemini generation and no new screenshot needed for this article.

---

## The Ring Letters (`ring_letters`) — REUSE

The whole article is a single fact about the app's own rendering (D=4h,
M=12h, Y=20h, Ω=24h, each at its Greek alphabetical hour) — a screenshot
of the ring already proves it, and one already exists from the Guide's
"Rings/Letters/Metals" chapter:

- **Primary:** `assets/instrument/guide/22_ring_domy_gold.png` — whole dial, DOMY
  ring in gold, all four letters (D, M, Y, Ω) legible at their hours.
- **Alternative / complement:** `assets/instrument/guide/64_ring_numbers_seal.png`
  — the plain-number ring (12/16/20/4 + Ω) that the article's closing
  paragraph calls "the plain confession of the trick"; pairing the two
  images (letters, then numbers) would directly illustrate that line.
- Also on file if a wider view is wanted: `assets/instrument/guide/19_rings.png`
  (overview grid) and `assets/instrument/guide/36_ring_morph_silver.png` (the
  MORPH sister ring: M/Π/H/Ω, same alphabetical-hour rule).

No new Gemini generation and no new screenshot needed for this article
either — these are existing, already-processed owner captures.

---

## Delivery

The two Gemini images (section logo, `paint_light`) land as flat PNGs
in the project root, exactly like previous batches — the owner drops
them for processing (white-background removal, circle crop, 800×800)
before they move into `assets/instrument/`. The five SCREENSHOT
articles are owner-driven captures of the running app, dropped
alongside for whatever crop/export step the Encyclopedia's image
pipeline expects. `metals` and `ring_letters` need nothing new at all —
both point at assets already sitting in the tree.

---

## THE TWO GENERIC PLATES (owner decree 2026-07-29)

Two pages repeat across the whole book with the SAME meaning every
time, and the owner sealed both as ONE shared image rather than one per
theme:

> *"Neka Generic što ćemo osmisliti da opisuje taj DUALITY tj TRINITY
> koji predstavljamo. Neće svaka tema imati svoju — osim ako tu ne
> predstavljamo nešto novo što ne opisuje nijedan od 3 predstavnika
> nedelje."* … *"Isto kao i kod 13ti teme. Dakle 2 generic slike."*

**Why this is the right seat for them.** Both plates belong to no
theme, so they cannot live in a theme's register (the tree law's
`<theme>/<register>/<look>/` has no room for "everyone's"). They are
the instrument's own furniture, exactly like the section logo and the
paint/light legend, and they land beside them at `assets/instrument/`
top level — sourced files, `_gem`/`_gpt` suffix resolved by
`config.paths.art_file` like every other sourced image.

**The rule that shaped the DUALITY plate.** The earlier per-theme
briefs drew the two faces themselves (Zeus enthroned against Hades
enthroned). The owner struck that down for a reason worth writing
down: *"njihova slika se sve pojavljuje odmah na sledeće dve strane,
tako da forsiranje 1 te iste slike na svakoj strani nećemo da
dozvolimo"* — the two faces open the very next two pages, so a title
plate that shows them again spends the reader's attention on a repeat.
**Neither plate carries a single figure.** What they carry is the
SHAPE of the idea: a seat with two faces, and a count that will not
close.

**Neither carries lettering.** The theme-title sheet's wordmark
exception is a per-theme thing; a plate that serves twenty themes can
name none of them.

**When a theme may claim its OWN Duality plate:** only when that page
presents something *none of the three seat-holders already describes*
— a genuinely new third thing, not a restatement of the pair. The
resolver keeps an override table for exactly that case; it is EMPTY
today.

---

**The Generic Duality — the seat with two faces** →
`assets/instrument/duality.png`

*One throne, split down the middle: day on one side, night on the
other, and the ninth standing outside the ring entirely. Nobody is
sitting in it — whoever does is on the next page.*

```
Ornate circular medallion, aged bronze and dark silver relief, photorealistic render, perfectly centered, isolated on white background. NO FIGURE OF ANY KIND — no person, no face, no hand, no animal: the seat is EMPTY, deliberately. Center: one single high-backed throne seen head-on, and the throne is split exactly down its vertical axis into two finishes that meet along one seam — the LEFT half struck in warm polished gold under a small sun disc, its side of the field open and lit; the RIGHT half struck in cold dark iron-silver under a small eclipsed disc, its side of the field closed and unlit. The seat, the arms and the base run through the seam UNBROKEN, so the plate reads as one chair and not as two half-chairs. Beyond the border ring, at the very bottom and clearly OUTSIDE the medallion's rim, stands a third much smaller stool, plain and turned away from the throne, in neither metal — the ninth, outside the circle. Border: a plain double bronze fillet, no ornament of any culture, broken only by twenty-four fine ticks evenly spaced around the ring — the dial's own hour count, the one family this plate belongs to. No text, no watermark, no letters or numerals anywhere.
```

---

**The Generic Thirteenth — the count that does not close** →
`assets/instrument/thirteenth.png`

*Every set on this instrument is built on twelve. This is what happens
when a thirteenth arrives: the same craft, the same metal, and no seat
for it.*

```
Ornate circular medallion, aged bronze relief, photorealistic render, perfectly centered, isolated on white background. NO FIGURE OF ANY KIND — no person, no animal, no symbol of any culture. Center: a closed ring of TWELVE identical segments, cut and finished exactly alike, meeting edge to edge all the way round so the circle is complete and admits nothing more. At the very top, where the ring closes, a THIRTEENTH segment of the same size and the same bronze stands LIFTED clear of the ring — resting slightly above and outside the rim, not fitted into it, casting its own distinct shadow down across the twelve beneath it. The gap it should have occupied is not there: the twelve have already closed over it. Border: a plain double bronze fillet, unbroken and unornamented. No text, no watermark, no letters or numerals anywhere.
```
