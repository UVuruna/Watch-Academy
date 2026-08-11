# The Dial Numerals — Settings Specification

The numbers on the two bands of the dial: the **hour ring** on the outside
and the **minute ring** inside it. Which faces draw them, how they are
coloured, how they are seated, and how they are lifted off the metal.

This is the **decision ledger** for the Watch Face settings page. Every row
is either SETTLED (the owner has ruled) or OPEN. Nothing here is wired into
`config/` yet — this file is written first, and the config tables follow it.

Live specimen sheet — every candidate face, the rotating ring and every
relief recipe on the ring's own colour: `scratchpad/hour-numerals.html`,
published as an Artifact.

---

## 1. Why the numerals are drawn by hand

A preset ring of hour markers would be enough for a clock whose 12 never
moves. DOMY's does move. In the solar mode the whole hour band **rotates so
that true solar noon sits at the top**, which means the numeral standing at
0° is not 12 but whatever the offset put there — 12:45, say, when the ring
has turned 11.25° back.

Everything downstream follows from that one fact:

- **A numeral's seat belongs to the angle it lands on, never to the hour it
  carries.** After a rotation, 18 sits in the upper half and reads like the
  upper scale; 6 sits in the lower half and reads like the lower one.
- The ring must be generated from the numerals themselves, at whatever
  angle the moment demands.

---

## 2. The two dial modes

| Mode | The hour band | Status |
|---|---|---|
| **1 · GEOCENTRIC** | fixed — 12 always at the top, centre; the star alone follows the sun | SETTLED |
| **2 · HELIOCENTRIC** | rotates so true solar noon is at the top (star upright), and the whole dial inverts at night | SETTLED |

The full description of mode 2 — the names (Ptolemy/Copernicus), the night
inversion, what every element does — was ruled 2026-08-06 and lives in
[The Ring Rework Ledger](ring_rework.md); that ledger inherits every
SETTLED row of this one unchanged.

**Only the outer band turns.** The inner band — minutes and seconds — never
rotates, in either mode: it is a plain clock face and its hands read
ordinary time. The **hour hand alone** carries the solar offset when mode 2
is on.

---

## 3. The two colour rules

The ring is `#656A70`. Against it the numerals alternate, and the
alternation is the point: parity is readable without counting.

| | Body | Border | Reads as |
|---|---|---|---|
| **A · even** | `#FFFFFF` white | `#656A70` ring | a white plate laid on the ring |
| **B · odd** | `#656A70` ring | `#FFFFFF` white | a cut-out — the ring seen through the numeral |

Rule B has no body of its own. At **border 0** an odd numeral is exactly the
ring colour on the ring colour, so it exists *only* through its relief. That
is deliberate: the odd hours recede, the even hours advance, and the dial
gains depth without gaining ink.

---

## 4. The seating law

Angles run **clockwise from the top**. In mode 1 an hour sits at
`deg(h) = (h − 12) × 15`; in mode 2 the solar offset is added to that and
the result folded into (−180°, 180°].

**`arc`** (owner amendment 2026-08-11, THE FLOWING SIDES) — only **TOP**
(0°) and **BOTTOM** (180°) stand upright. The two SIDE squares (90°,
270°/−90°) no longer stand upright of their own right — they FLOW with
whichever half they open clockwise: the +90° seat turns with the lower
half that follows it (the extra 180° flip), the −90° seat turns with the
upper half that follows it (no flip). Every non-square numeral takes the
angle it sits on, and the lower half turns a further 180° so nothing ever
reads upside down — on BOTH signs of the fold.

```
rot(deg) = 0                if deg == 0 or |deg| == 180     top / bottom only
         = deg + 180        if |deg| > 90 or deg == 90      lower half, incl. the +90 seat
         = deg              otherwise                       upper half, incl. the -90 seat
```

**`upright`** — `rot = 0` everywhere.

With the ring square-on this puts only 12 and 0 upright; 18 (at +90) turns
with the lower half and 6 (at −90) rides the upper half unflipped — the
former "all four square angles stand upright" rule is gone. The moment the
ring turns, every numeral (12/18/0/6 included) rides the arc like anyone
else, seated by the angle it lands on.

Labels are written bare: `0, 1, 2 … 23`. No leading zero. The minute band
labels every fifth minute: `0, 5, 10 … 55`.

---

## 5. The relief model

Three styles, all short-throw and hard-edged. A wide soft halo was tried and
rejected: it turns to smoke the moment the numerals shrink to dial size.

**`cast`** — ONE copy of the numeral, in the shade colour, moved the full
depth along the light vector and drawn behind the original. The gap stays
open, so the numeral reads as a thin plate *floating above* the ring.

**`extrude`** — the SAME offset, laid down in N unit steps from the far end
back to the numeral, so the copies overlap and weld into a solid side wall.
Nothing floats: the numeral becomes a block *standing on* the ring, and
depth is the height of that block.

```
cast     glyph + 1 copy at  depth
extrude  glyph + N copies at depth·1/N, depth·2/N … depth   (N = round(depth))
emboss   glyph + 1 dark copy at depth, 1 white copy at −0.6·depth
```

**`emboss`** — a dark copy one way and a lit rim the other: pressed metal
rather than cast metal.

Over any style sits an optional **contact blur** — a small, intense black
blur with no offset, which seats the numeral against the metal. A separator,
not an atmosphere; the radius stays low.

The relief is **real geometry**: the shadow is a copy of the numeral moved
in page space. It is never a filter applied inside a numeral's own rotated
frame — a tilted seat would then bend its own shadow, and the lower half of
the ring (which carries the extra 180°) would throw its relief the opposite
way from the upper half.

---

## 6. The light law

**`radial`** — one lamp at the centre of the dial. Every numeral throws its
shadow straight outward. With `y` counted positive upward, the four square
angles must come out exactly:

| Angle | Seat | Offset |
|---|---|---|
| 0° | top | `(0, +depth)` |
| 90° | right | `(+depth, 0)` |
| 180° | bottom | `(0, −depth)` |
| 270° | left | `(−depth, 0)` |

```
offset(deg) = depth · ( sin deg,  cos deg )            y positive up
```

The panel's readout prints these four live, so the lamp can always be
checked against this table at a glance.

**`fixed`** — one lamp somewhere off the dial. The X/Y offset **is** the
throw: what is typed is what lands, in units, X positive right and Y
positive up. `depth` says nothing in this mode. For `extrude`, the number of
steps comes from the offset's own length.

---

## 7. The faces

Two rosters. The hour ring and the minute ring do not share a voice: the
hours are display faces with weight and character, the minutes are compact
and quiet.

**Hour ring — outer band**

| Face | Character |
|---|---|
| **Bernard MT Condensed** | the dial's own — fat condensed display serif |
| Bahnschrift Bold | DIN 1451, the instrument voice |
| Poppins SemiBold | true circles, even weight |
| Poppins Black | maximum mass, still round |
| Roboto Bold | neutral, tight apertures |
| Impact | extreme condensation |
| Palatino Linotype Bold | calligraphic, high contrast |

**Minutes (the inner minute band)**

| Face | Character |
|---|---|
| **Eras Bold ITC** | the dial's own — humanist geometric |
| Unispace | squared terminals, techno |
| Poppins Black | maximum mass, still round |
| Arial Black | the safe heavyweight |
| Segoe UI Black | Windows' own black cut |

**Verified on this install, 2026-08-06** (`render.numeral_fonts.glyph_coverage`,
by glyph GEOMETRY — `QRawFont.supportsCharacter` answers True for all of them):
the recovered **Bernard MT Condensed** draws its ten digits perfectly and draws
**nothing at all** for `:` `.` `h` `m` `i` (empty outlines, non-zero advances),
so it keeps the hour ring — which needs digits only — while the live crown,
which needs the colon and the h/min cut, defaults to **Bahnschrift Bold**
instead of inheriting it; Eras Bold ITC covers every glyph.

Bernard MT Condensed and Eras Bold ITC are the faces the original artwork
was drawn in. They are Monotype/ITC and ship with Microsoft Office, not with
Windows — they were **recovered from `illustrator/Clock 24h.ai`**, which
carries them embedded, renamed back to their proper families and installed
for the user. Complete faces, 244 and 250 glyphs. If the app is ever shipped
to another machine, those two travel with the installer.

---

## 8. The settings

| Setting | Type | Range | Value | Status |
|---|---|---|---|---|
| **Mode** | choice | `classic` · `solar` | both shipped | **SETTLED** |
| **Seating** | choice | `arc` · `upright` | both shipped, user picks | **SETTLED** |
| **Ring face** | choice | the seven above | `Bernard MT Condensed` | **SETTLED** |
| **Minutes face** | choice | the five above | `Eras Bold ITC` | **SETTLED** |
| **Size** | number | 40 – 140 units | `90`, user-adjustable | **SETTLED** |
| **Border** | number | 0 – 16 units | `0` | **SETTLED** |
| **Relief style** | choice | `cast` · `extrude` · `emboss` | `extrude` | **SETTLED** |
| **Depth** | number | 0 – 16 units | `3` | **SETTLED** |
| **Light** | choice | `radial` · `fixed` | `radial` | **SETTLED** |
| **Darkness** | number | 0 – 1 | `1.00` | **SETTLED** |
| **Contact blur** | number | 0 – 8 units | `0.5` | **SETTLED** |
| Offset X / Y | number | ±16 units | fixed light only | OPEN |

Lengths are in the same units as the numeral's own size, so a setting
survives any change of dial resolution.

---

## 9. Still to settle

Nothing — every item below was ruled 2026-08-06, in
[The Ring Rework Ledger](ring_rework.md):

- Mode 2 in full → the Heliocentric mode: solar rotation of the outer band
  plus the night inversion, phase derived from the sun's actual state.
- The minute ring's seating → moot: the inner band never rotates in any
  mode; only its numeral font and size are user-changeable.
- Relief exposure → the settings of §8 ship as listed, at their SETTLED
  defaults.
- The crown text → one relief for the whole crown; its live time renders
  11 glyphs once per settings change and re-composes per minute.
