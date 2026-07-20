# Slot Subdial — Prompt Sheet (ChatGPT / Gemini)

The slot ROUNDEL (owner 2026-07-14) is the watch-face plate every flat
slot face (text modes, flat astrology art) sits on. This sheet used to
carry TWELVE briefs — 4 seat/light variants × 3 letter finishes — for
what the program can compute from ONE image. Rule #19, "Compute, Don't
Generate" (owner decree 2026-07-20, monorepo root `CLAUDE.md`), was
written FOR this exact failure and is enforced here first: the sheet
now carries exactly ONE entry.

## The derivation check (Rule #19)

- **Tint/metal** — NEVER a separate image. `render.assets.
  subdial_plate_file()` recolors the master to any letter finish live
  (numpy, disk-cached): the master's OWN finish draws as drawn
  (`config.defaults.SUBDIAL_MASTER_FINISH`), the other two are derived
  the same recipe the ring letters use — silver is the achromatic
  value alone, gold/bronze tint that value by their own color — masked
  to the brushed rim only, the dark tapisserie field untouched.
- **Lighting/shadow** — NEVER a separate image. The plate's soft
  outward drop shadow is one line of circle math,
  `render.layers._draw_subdial_shadow`: the offset direction IS the
  seat's own dial angle (south straight down, an arm seat toward its
  own outward corner, the center seat symmetric — distance 0, no
  offset), drawn live under the plate every paint. The twelve-brief
  sheet asked for this shadow FOUR TIMES, pre-baked, per seat — the
  exact waste Rule #19 exists to end.
- **The irreducible core** — the engine-turned tapisserie field and
  brushed bezel texture itself: one master, generated once, under flat
  and neutral (dead-overhead) lighting so no baked shadow direction
  ever fights the live one drawn on top of it.

## The one master

**Drop path:** `assets/badge/subdial/master.png` — a single
generation per source (no `<finish>` or `<seat>` split any more; the
canonical path resolves through `config.paths.art_file`/
`config.defaults.SUBDIAL_ART_DIR` exactly like every other sourced
family).

**The Subdial Master** → `assets/badge/subdial/master.png`

```
A single circular watch SUBDIAL plate, viewed perfectly straight-on, isolated on a fully transparent background, high-resolution render, nothing outside the circle. RIM: a narrow raised bezel ring in a brushed metal, the same brushed, softly antiqued texture as an engraved luxury watch letter — fine lengthwise brushing, gentle wear on the edges, a slight three-dimensional rounded profile that catches the light. INTERIOR: a dark slate-graphite engine-turned field (guilloché tapisserie — a fine repeating machined pattern of tiny squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no numerals, no hands, no text, no logo — the plate is a blank canvas for content drawn later. LIGHTING: flat and neutral, lit evenly from directly overhead with no directional shadow of any kind — the render code casts its own shadow live, so the plate itself must read as if lit from dead center, no side, top or bottom bias. Palette strictly: a neutral brushed metal rim, dark slate/graphite interior; no bright colors, no color cast from the metal choice — the program recolors the rim live. Square canvas, the circle filling ~95% of it, transparent corners. NO lettering anywhere.
```

Any metal reads for the rim brief above — the program recolors it, so
only the TEXTURE (brushing, wear, rounded profile) and the flat
lighting matter. One clean generation per source is enough.

## Wiring (live)

`subdial_plate_file(finish, tint=None)` resolves the ONE master
through `config.paths.art_file`, returns it AS DRAWN when `finish`
matches the master's own metal (`SUBDIAL_MASTER_FINISH`) and no tint
is requested, and otherwise returns a disk-cached live recolor. The
layer draws the directional shadow separately, underneath, keyed off
the seat's own dial position — never the file.

## Status

- **PURGE round (2026-07-19):** gemini's silver `center` plate (the
  seat/finish structure this round retires) was the one plate on disk,
  generated from this sheet's original brief (not a make-script).
- **THE TWELVE-PLATE ROUND (2026-07-20):** the sheet as it stood before
  this entry — 4 seat/light variants × 3 finishes — was run to
  completion for Gemini (12/12) and mostly for ChatGPT (9/12, quota
  limit) before the owner caught the failure Rule #19 now names: the
  shadow direction and the letter metal were BOTH already computable
  live, so eleven of Gemini's twelve renders and eight of ChatGPT's
  nine were pure waste — generated, then deleted the same round
  ("da obrišemo ostatak").
- **RULE #19 ENFORCEMENT (owner decree 2026-07-20, same round):** this
  sheet rewritten to the single master above. Kept:
  `assets/badge/gemini/subdial/master.png` (the PURGE round's original
  silver `center` plate — the "original good master", per the owner)
  and `assets/badge/chatgpt/subdial/master.png` (one of the fresh gold
  `center` generations — picked because it existed and was clean; the
  `center` variant's own brief already asked for the most neutral,
  dead-overhead lighting of the four, so both masters happen to carry
  only a thin, even vignette rather than a strong baked directional
  shadow). Deleted: the other 20 files (11 Gemini + 8 ChatGPT
  variants, plus one stray `silver/center2.png` duplicate) — `git rm`/
  plain deletion, no replacement needed, `render.assets.
  subdial_plate_file` and `render.layers._draw_subdial_shadow` cover
  every seat and finish live.
- **Future work (documented, not required):** both current masters
  still carry their own small baked vignette from the `center` brief's
  "thin uniform shadow ring". A future regeneration against the fully
  flat brief above would remove even that — optional, since the live
  shadow already draws on top and the existing vignette is faint.
