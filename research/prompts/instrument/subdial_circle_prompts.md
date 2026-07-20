# Slot Subdials — Prompt Sheet (ChatGPT / Gemini)

The slot ROUNDEL (owner 2026-07-14) is currently drawn procedurally: a
flat circle in the ring's face color with a plain metal rim. This sheet
generates the REAL plates — engine-turned watch subdials in the house
letter metals, lit as if the SUN stands at the dial's center, so every
seat casts its shadow OUTWARD. When the files land, the renderer swaps
the procedural circle for the art (exists-guarded, like everything
else); text, glyphs and the mini seconds hand draw ON TOP of the empty
plate, so the interior must stay CLEAN.

12 files = 4 light variants × 3 finishes. Keep one finish per chat
session so the metal reads identically across its four plates.
(Sheet rewritten to the parser contract 2026-07-20 — the old single
{FINISH}/{LIGHT} template could not be paired by PromptPainter.)

## The four LIGHT variants (the sun lives at the dial center)

| Stem | Seat on the dial | Light comes from | Shadow falls |
|---|---|---|---|
| `south` | alone at 24h (bottom) | straight ABOVE | straight below (outward) |
| `h3` | the 3h seat (lower LEFT) | upper RIGHT | to the lower left (outward) |
| `h21` | the 21h seat (lower RIGHT) | upper LEFT | to the lower right (outward) |
| `center` | the dial CENTER (Compass) | dead overhead | a thin, even ring of shadow on ALL sides |

**Drop paths:** `assets/badge/<source>/subdial/<finish>/<stem>.png` —
the entries below carry the canonical source-agnostic paths; the
intake maps informal inbox folder names (`subdial gold/…`) onto them.

---

## Gold (warm antique gold, #FFD235 highlights)

**Gold — South (24h)** → `assets/badge/subdial/gold/south.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in warm antique GOLD, the exact tone of an aged 24-karat engraved watch numeral (#FFD235 highlights, deep amber shading), with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from directly ABOVE the plate; the upper inner bezel glints, a soft shallow drop shadow hugs the LOWER outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the gold metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Gold — 3h seat** → `assets/badge/subdial/gold/h3.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in warm antique GOLD, the exact tone of an aged 24-karat engraved watch numeral (#FFD235 highlights, deep amber shading), with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER RIGHT; the upper-right bezel glints, a soft shallow drop shadow hugs the LOWER-LEFT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the gold metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Gold — 21h seat** → `assets/badge/subdial/gold/h21.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in warm antique GOLD, the exact tone of an aged 24-karat engraved watch numeral (#FFD235 highlights, deep amber shading), with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER LEFT; the upper-left bezel glints, a soft shallow drop shadow hugs the LOWER-RIGHT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the gold metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Gold — Center** → `assets/badge/subdial/gold/center.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in warm antique GOLD, the exact tone of an aged 24-karat engraved watch numeral (#FFD235 highlights, deep amber shading), with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from DEAD OVERHEAD at the very center of the watch; the whole bezel glints evenly, a thin uniform shadow ring hugs the entire outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the gold metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

## Silver (cool brushed silver-steel, #C9CDD3 highlights)

**Silver — South (24h)** → `assets/badge/subdial/silver/south.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in cool brushed SILVER-steel, pale platinum highlights (#C9CDD3), graphite shading, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from directly ABOVE the plate; the upper inner bezel glints, a soft shallow drop shadow hugs the LOWER outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the silver metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Silver — 3h seat** → `assets/badge/subdial/silver/h3.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in cool brushed SILVER-steel, pale platinum highlights (#C9CDD3), graphite shading, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER RIGHT; the upper-right bezel glints, a soft shallow drop shadow hugs the LOWER-LEFT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the silver metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Silver — 21h seat** → `assets/badge/subdial/silver/h21.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in cool brushed SILVER-steel, pale platinum highlights (#C9CDD3), graphite shading, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER LEFT; the upper-left bezel glints, a soft shallow drop shadow hugs the LOWER-RIGHT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the silver metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Silver — Center** → `assets/badge/subdial/silver/center.png`

*(The one plate already on disk — gemini generated it 0.14.227; the
entry stays for the ChatGPT source and any regeneration.)*

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in cool brushed SILVER-steel, pale platinum highlights (#C9CDD3), graphite shading, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from DEAD OVERHEAD at the very center of the watch; the whole bezel glints evenly, a thin uniform shadow ring hugs the entire outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the silver metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

## Bronze (weathered bronze, #CD7F32 midtones)

**Bronze — South (24h)** → `assets/badge/subdial/bronze/south.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in weathered BRONZE with a warm patina (#CD7F32 midtones), darkened antique edges, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from directly ABOVE the plate; the upper inner bezel glints, a soft shallow drop shadow hugs the LOWER outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the bronze metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Bronze — 3h seat** → `assets/badge/subdial/bronze/h3.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in weathered BRONZE with a warm patina (#CD7F32 midtones), darkened antique edges, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER RIGHT; the upper-right bezel glints, a soft shallow drop shadow hugs the LOWER-LEFT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the bronze metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Bronze — 21h seat** → `assets/badge/subdial/bronze/h21.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in weathered BRONZE with a warm patina (#CD7F32 midtones), darkened antique edges, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from the UPPER LEFT; the upper-left bezel glints, a soft shallow drop shadow hugs the LOWER-RIGHT outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the bronze metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

**Bronze — Center** → `assets/badge/subdial/bronze/center.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in weathered BRONZE with a warm patina (#CD7F32 midtones), darkened antique edges, with the same brushed, softly antiqued metal texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: lit from DEAD OVERHEAD at the very center of the watch; the whole bezel glints evenly, a thin uniform shadow ring hugs the entire outer edge. The shadow must stay SOFT and shallow — the plate sits almost flush with the dial, not floating above it. Palette strictly: the bronze metal of the rim, dark slate/graphite interior, neutral shadow; no bright colors anywhere. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

---

## Wiring (already live)

`subdial_plate_file()` picks the plate by the slot's SEAT (south / 3h /
21h / center) and the active letter finish; a missing SEAT falls back
to `center`, a missing FINISH recolors another finish's master live —
every new file that lands simply takes its own seat.

## Ground truth (PURGE round, 2026-07-19)

`assets/badge/gemini/subdial/silver/center.png` is the ONE master
plate on disk today — generated from this sheet's brief, not a
make-script. The remaining 11 entries above are pure art generation.
