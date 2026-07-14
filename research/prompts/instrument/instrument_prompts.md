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
own logo (`assets/zodiac/astrology/primary/`) — the brief below repeats "not a
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

- Pointer = **Seasons** (cross) — shows the year-wheel marker and the
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

- **Gold:** `assets/weekday/alchemy/primary/gold.png` — crucible pouring molten
  gold beside a polished sun-face disc, exactly "gold to the Sun."
- **Silver:** `assets/weekday/alchemy/primary/silver.png` — half-polished,
  half-tarnished mirror-disc and chalice, exactly "silver to the Moon."
- **Bronze:** no dedicated medallion exists (or is needed) — bronze is
  the default, ambient finish of dozens of existing plates project-wide
  (every weekday god, every profession, every ring letter). If the
  article wants one concrete bronze image anyway, reuse
  `assets/guide/63_ring_domy_bronze.png` — an actual in-app screenshot
  of the DOMY ring struck in plain bronze, already owner-captured and
  processed for the Guide.

No new Gemini generation and no new screenshot needed for this article.

---

## The Ring Letters (`ring_letters`) — REUSE

The whole article is a single fact about the app's own rendering (D=4h,
M=12h, Y=20h, Ω=24h, each at its Greek alphabetical hour) — a screenshot
of the ring already proves it, and one already exists from the Guide's
"Rings/Letters/Metals" chapter:

- **Primary:** `assets/guide/22_ring_domy_gold.png` — whole dial, DOMY
  ring in gold, all four letters (D, M, Y, Ω) legible at their hours.
- **Alternative / complement:** `assets/guide/64_ring_numbers_seal.png`
  — the plain-number ring (12/16/20/4 + Ω) that the article's closing
  paragraph calls "the plain confession of the trick"; pairing the two
  images (letters, then numbers) would directly illustrate that line.
- Also on file if a wider view is wanted: `assets/guide/19_rings.png`
  (overview grid) and `assets/guide/36_ring_morph_silver.png` (the
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
