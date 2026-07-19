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

## The four LIGHT variants (the sun lives at the dial center)

| Stem | Seat on the dial | Light comes from | Shadow falls |
|---|---|---|---|
| `south` | alone at 24h (bottom) | straight ABOVE | straight below (outward) |
| `h3` | the 3h seat (lower LEFT) | upper RIGHT | to the lower left (outward) |
| `h21` | the 21h seat (lower RIGHT) | upper LEFT | to the lower right (outward) |
| `center` | the dial CENTER (Compass) | dead overhead | a thin, even ring of shadow on ALL sides |

## Drop locations (canonical — the source layer applies)

```
assets/badge/subdial/gold/{south,h3,h21,center}.png
assets/badge/subdial/silver/{south,h3,h21,center}.png
assets/badge/subdial/bronze/{south,h3,h21,center}.png
```

Dropping them into the `chatGPT/` inbox as `subdial gold/…` etc. works
too — the intake maps informal folder names onto these stems.

---

## The prompt (fill FINISH and LIGHT per file)

> A single circular watch SUBDIAL plate, viewed perfectly straight-on,
> isolated on a fully transparent background, high-resolution render,
> nothing outside the circle. RIM: a narrow raised bezel ring in
> {FINISH}, with the same brushed, softly antiqued metal texture as an
> engraved luxury watch letter — fine lengthwise brushing, gentle wear
> on the edges, a slight three-dimensional rounded profile that
> catches the light. INTERIOR: a dark slate-graphite engine-turned
> field (guilloché tapisserie — a fine repeating machined pattern of
> tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY:
> no numerals, no hands, no text, no logo — the plate is a blank
> canvas for content drawn later. LIGHTING: {LIGHT}. The shadow must
> stay SOFT and shallow — the plate sits almost flush with the dial,
> not floating above it. Palette strictly: the {FINISH} metal of the
> rim, dark slate/graphite interior, neutral shadow; no bright colors
> anywhere. Square canvas, the circle filling ~95% of it, transparent
> corners.

**{FINISH} lines** (match the ring-letter metals):

- gold — `warm antique GOLD, the exact tone of an aged 24-karat
  engraved watch numeral (#FFD235 highlights, deep amber shading)`
- silver — `cool brushed SILVER-steel, pale platinum highlights
  (#C9CDD3), graphite shading`
- bronze — `weathered BRONZE with a warm patina (#CD7F32 midtones),
  darkened antique edges`

**{LIGHT} lines**:

- south — `lit from directly ABOVE the plate; the upper inner bezel
  glints, a soft shallow drop shadow hugs the LOWER outer edge`
- h3 — `lit from the UPPER RIGHT; the upper-right bezel glints, a
  soft shallow drop shadow hugs the LOWER-LEFT outer edge`
- h21 — `lit from the UPPER LEFT; the upper-left bezel glints, a
  soft shallow drop shadow hugs the LOWER-RIGHT outer edge`
- center — `lit from DEAD OVERHEAD at the very center of the watch;
  the whole bezel glints evenly, a thin uniform shadow ring hugs the
  entire outer edge`

## Checklist

- [ ] gold: south, h3, h21, center
- [ ] silver: south, h3, h21, center
- [ ] bronze: south, h3, h21, center

## Wiring (mine, once the art lands)

`draw_slot_roundel` picks the plate by the slot's SEAT (south / 3h /
21h / center) and the active letter finish, falls back to the
procedural circle where a file is missing, and keeps drawing the
content (fitted text, glyph art, the mini seconds hand) centered on
top at `SLOT_ROUNDEL_CONTENT_FRACTION` of the diameter.

## Ground truth (PURGE round, 2026-07-19)

`assets/badge/gemini/subdial/silver/center.png` is the ONE master
plate on disk today — generated from THIS sheet's brief, not a
make-script (no `setup/make_subdial*.py` exists; confirmed by the
intake commit, "0.14.227 Owner round six": *"THE OWNER'S FIRST SUBDIAL
PLATE ... intaken ... exactly the sheet brief"*). `subdial_plate_file()`
already covers every seat and every finish from this ONE master —
missing SEATS fall back to `center`, missing FINISHES recolor another
finish's master live — so the gap is pure ART GENERATION against the
11 remaining entries above, not a missing prompt: strictly the code
only needs ONE finish per remaining LIGHT variant (`south`, `h3`,
`h21` — any of gold/silver/bronze, whichever the owner generates
first) to give those three seats their own plate instead of reusing
`center`'s.
