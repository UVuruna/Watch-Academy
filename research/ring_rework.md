# The Ring Rework & the Two World-Modes — Decision Ledger

**JEWELS naming sweep (owner ruling 2026-08-06):** `letter(s)`/`letter art`/
`Indices` → **JEWELS** everywhere in this document and in the code it
describes — the art glyph plates worn in metal/thematic finish (Latin/Greek
letters, number plates, templar cross, the Eye, the colon plate).

Every ruling of the 2026-08-06 rework round, SETTLED with the owner in one
sitting. This ledger is the implementation session's brief: nothing here is
open, and nothing here is wired into `config/` yet. It extends — never
reopens — [The Dial Numerals](hour_numerals.md), whose SETTLED rows (colour
parity, seating law, relief, light law, font rosters, defaults) carry over
unchanged.

---

## 1. The two world-modes

Solar Rotation stays its own switch, exactly as today. The new **Mode**
setting picks what that switch rotates — and whether the dial turns over at
night. The mode is independent of the ring preset.

| Mode | Picker label | Behaviour |
|---|---|---|
| **GEOCENTRIC** | Geocentric (Ptolemy) | Today's dial: the observer stands still and the sun travels — the star/pointer rotates toward true solar noon, the hour band and every numeral stay fixed, 12 always on top. |
| **HELIOCENTRIC** | Heliocentric (Copernicus) | The sun stands still and the world turns: with Solar Rotation ON the OUTER band rotates so its top centre is true solar noon (true solar midnight in the night phase) while the star stays upright; and — visible even with Solar Rotation OFF — the whole dial **inverts at night**. |

The GUIDE gets a short passage per mode telling the two astronomers' stories
(Ptolemy/Almagest, Copernicus/De revolutionibus); an Encyclopedia expansion
may follow later on the owner's word.

### The night inversion (Heliocentric only)

Two phases. **DAYLIGHT** — as today: 12 on top, midnight at the bottom.
**NIGHT** — everything moved 180°: 0h on top, 1-2-3 running clockwise, noon
at the bottom. Every member re-seats READABLY at its new position, with its
new angle and its new arc — nothing is mirrored:

- outer NUMBERS (the inner band NEVER rotates, in any mode),
- LETTERS, CROWN TEXT, POINTER (star + diamond slots), AURA, UMBRA,
- every image, weekday body and hover,
- the HOUR hand takes +180° (minute/seconds hands do not — they read the
  fixed inner band),
- EARTH/year wheel: winter solstice on top at night (summer by day),
- MOON: full moon on top at night (new moon by day —
  `core.angles.moon_cycle_angle` holds new-at-top, so night is +180°).

**The phase is derived from the sun's actual state** — above the horizon =
DAYLIGHT, below = NIGHT — never from counting "two flips a day": an ordinary
day has two transitions, polar day and polar night have ZERO (Tromsø sits in
one phase for months and no animation fires). The flip, when it genuinely
happens, plays as one short orchestrated turning animation (~1–2 s). Golden
tests cover the ordinary day and both polar regimes.

Timekeeping itself never changes: the hands and the inner band show standard
zone time — what every clock shows — exactly as today. The modes move only
what is DRAWN.

## 2. Live rendering of both bands

The static ring plates give way to composition **rendered once — at startup
and on every settings change**, never per frame:

| | OUTER band | INNER band |
|---|---|---|
| Content | NUMBERS (hour_numerals.md's 7-face roster) + LETTERS from the asset library | NUMBERS (5-face roster) + the LINES: LONG, SHORT (beside a number), POINTER, SECOND, DAY (360 ticks) |
| Rotation | Heliocentric: solar offset + night inversion — numerals seat per the seating law at whatever angle the moment demands | NEVER — standard zone time, may legitimately disagree with the rotated hours above |
| Relief | black SHADOW per hour_numerals.md (cast/extrude/emboss, radial light, parity colours) | WHITE GLOW — small radius, high intensity: a white border+glow, never a diffuse halo; same recipe for every inner element |
| User-changeable | everything in the decision ledger | ONLY the numeral font (+ sizes, §5) |

### The Fidelity Ruling (owner correction 2026-08-06, on seeing wave 3 live)

Three laws, ruled after the first live-rendered bands reached the owner's
screen and diverged from his art:

1. **The live band composes the WHOLE ring — it never paints over the
   printed plates' own content.** The composition chooses, per position,
   what stands there: a letter plate OR a numeral, never both stacked. An
   Ω with a 0 showing beneath it is the defect that triggered this ruling.
   There is no reason to keep the old full-ring plate underneath a band
   the engine builds from parts on the spot.
2. **The owner's art IS the look.** Everything he created is used and
   reproduced exactly: his plates and arrow/pointer art directly where
   they exist, and where the engine draws (numerals, ticks, lines) it must
   match his originals using shadow and glow — compared SIDE BY SIDE
   against the pre-rework rendering. A delivered look that differs from
   his art is a defect — for the letters and for every inner-band element,
   arrows included.
3. **Render time changes WHAT, never HOW it looks.** The user's picks
   (font, display, letters vs numbers per position) decide the content of
   the band; the style is fixed by the owner's art.

**The pixelation defect (1440p):** today's letter shadow is stamped as 8
discrete silhouette copies around a circle (`RING_JEWEL_SHADOW_SAMPLES`,
`config/dial.py`) — at dial sizes the copies fuse, at 1440p they separate
into scalloped edges. The new engine draws relief and glow procedurally at
device resolution (true gaussian, step count derived from the pixel radius);
the existing stamped letters receive the same cure.

## 3. CROWN TEXT — one term, one hover law

**CROWN TEXT is the text arcing around the watch, outside the letter band**
— the Dollar's Great Seal mottos, DOMY's and LOOP's cross stations, the
free-form custom-ring arcs. The code's `motto` name is retired: **full
rename `motto → crown_text`** through code, JSON cards, settings keys (with
stored-settings migration — the migration map is one technical line per
rename and must stay so saved watches never read as corrupt) and docs. The
history-telling in JSON notes and docstrings does NOT stay: this round trims
the evolution narration (Morph→PILOT→LOOP …) to current-state-only — Git is
the history.

**Every crown text carries ITS OWN hover** explaining what the text means
and symbolises. The present content is wrong here and gets a dedicated
correction pass: today a crown word's hover shows the legend of the LETTER
whose seat it hangs on ("ANNUIT" narrates the Anointed Aegis instead of the
Latin motto). New rule: ANNUIT COEPTIS explains "He has favored our
undertakings", NOVUS ORDO SECLORUM "a new order of the ages", each cross
station its own station, NON NOBIS DOMINE its psalm, ΙΧΘΥΣ its acrostic, IN
HOC SIGNO VINCES Constantine's vision; the live time/location crowns say
whose hour they keep. In the same pass every ring letter's hover gains its
alphabet-ordinal line ("Θ — the 8th letter of the Greek alphabet, at 8h") —
seat-placement rationale lives on the glyph's hover, never in the About.

### The live crown (time in the arc)

No seconds. The engine renders **exactly 11 glyphs — digits 0–9 and the
colon — once per settings change**, in crown size, caches them, and once a
minute merely re-composes the arc from the finished glyphs.

**The look is the LETTERS' look (owner correction 2026-08-06, superseding
this section's first draft):** the time wears the same rendered-letters
treatment as everything on the ring — the crown's metal finish and the
letter shadow law, never the outer band's parity plate-and-frame styling.
The colon is the owner's OWN plate, `assets/instrument/ring/letters/
time.png`, made for exactly this and wired under `':'` in the letter
library; the digits (which have no plates) render from the crown face and
are styled by the same fidelity machinery into that family. An earlier
"white frame for the digits" idea is moot — the time crown carries no
parity framing at all.
**Digital-time format is a setting** with two variants: `hh:mm` (12:35) —
the standard default — and `12h 35min` (its h/min in a small cut, styled
the same way; the plate library has no lowercase).

## 4. The six bundled presets

Approved ABOUT texts (v2 — theme and name, never seat listings; owner
"može" 2026-08-06). Every preset keeps gold/bronze/silver plus its own
Thematic; custom rings may pick every thematic colour and every metal.

| | Preset | Outer | Crown text | Ruled |
|---|---|---|---|---|
| A | **DOMY** | bot_cross | FEAR / ANGER / HATE / SUFFERING | — |
| B | **LOOP** (was PILOT) | top_cross | HOPE / FAITH / LOVE / SALVATION | rename ruled; About leads with infinity |
| C | **Dollar** | hexa | ANNUIT COEPTIS / NOVUS ORDO SECLORUM | Eye with SHINE on renders NO shadow — the baked shine replaces it |
| D | **The One** | octa | top `hh:mm` (live) / bottom City, Country | 6 and 18 obey the seating law's square-angle rule |
| E | **Templar** | cross | top: hour of Jerusalem (live) / bottom NON NOBIS DOMINE | Jerusalem moves into the About |
| F | **CHI** (new) | full | ΙΧΘΥΣ / IN HOC SIGNO VINCES | one letter: X at 24h; Thematic = CERAMIC (new ramp, same transformer formula, hexes to `config/palette.py`) |

The approved About texts verbatim, ready for wiring, live in the round's
presentation page; the CHI dossier below feeds its hover and future article.

### The CHI dossier (owner: keep as source material)

Plato's Timaeus 36b — the Maker crossed the two great circles of heaven "in
the shape of the letter Χ": the ecliptic and the celestial equator, whose
two crossing points are the EQUINOXES this dial pins at 90°/270°. The
horizon's own X: east–west (6h/18h), and the four solstice
sunrise/sunset points drawing a saltire across the compass rose — the hexa
pointer's own figure. The 24th Latin letter on the 24th hour — the Latin
twin of Ω on the same seat. The initial of Χριστός; the Chi-Rho labarum (IN
HOC SIGNO VINCES is Constantine's sentence about THIS sign); ΙΧΘΥΣ carries
Χ at its heart; Xmas still writes it. St Andrew's saltire. The unknown of
mathematics at the hour no number can say. The signature of the unlettered;
X marks the spot; the crossroads. The Roman ten — the Decalogue.

## 5. New settings

- **Mode** — Geocentric (Ptolemy) / Heliocentric (Copernicus); Solar
  Rotation remains a separate switch;
- **numeral size** — OUTER and INNER numbers separately;
- **outer ring size** — the width of the band the LETTERS and NUMBERS
  stand in;
- **digital time format** — `hh:mm` (default) / `12h 35min`;
- preset picker: name + mini SVG preview + the About;
- per-preset finish: gold / bronze / silver / Thematic (F = ceramic);
- the inherited ledger settings (fonts, seating, relief …) at their
  SETTLED values.

## Connections

### Uses
- [The Dial Numerals](hour_numerals.md) — the numeral ledger this round
  inherits whole

### Used by
- The implementation session — this ledger is its reading list
