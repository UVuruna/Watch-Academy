# Slot Subdial — Prompt Sheet (ChatGPT / Gemini)

The slot ROUNDEL (owner 2026-07-14) is the watch-face plate every flat
slot face (text modes, flat astrology art) sits on. This sheet used to
carry TWELVE briefs — 4 seat/light variants × 3 letter finishes — for
what the program can compute from ONE image; Rule #19, "Compute, Don't
Generate" (owner decree 2026-07-20, monorepo root `CLAUDE.md`), was
written FOR that exact failure and collapsed the sheet to ONE master
per art source. **THE Rsub ROUND (owner decree 2026-07-21) retires
that one-master model in turn** — the subdial plate is not an
AI-generation family any more at all. Kept below only as the historical
record of what the one master's brief asked for; see "Status" for the
current model.

## The derivation check (Rule #19)

- **Lighting/shadow** — still NEVER a separate image, unchanged by
  this round: the plate's soft outward drop shadow is one line of
  circle math, `render.layers._draw_subdial_shadow` — the offset
  direction IS the seat's own dial angle (south straight down, an arm
  seat toward its own outward corner, the center seat symmetric —
  distance 0, no offset), drawn live under the plate every paint.
- **Tint/metal, SETS 1-4** — an owner-directed EXCEPTION (sealed
  2026-07-21): the three letter finishes are hand-drawn PER SET now,
  not derived — his explicit call after weighing the algorithmic
  recolor against hand color for four picked looks and preferring hand
  color. Twelve files, twelve looks, no apology needed: Rule #19 exists
  to stop GENERATING what a formula already computes for free, not to
  forbid an artist's own finished color choice once made and handed
  over.
- **Tint/metal, the SOLO set** — Rule #19 stands exactly as it did for
  the retired one-master model: ONE hand-drawn master (silver) plus a
  disk-cached ALGORITHMIC recolor for gold/bronze
  (`render.assets._recolored_plate`, the same recipe the ring letters
  use — silver is the achromatic value alone, gold/bronze tint that
  value by their own color, masked to the brushed rim only, the dark
  tapisserie field untouched).
- **The irreducible core** — the owner's own hand-picked plates ARE the
  core now; nothing under `assets/subdial/` is a candidate for further
  collapse by this round.

## The retired one master (historical brief, kept for reference)

> A single circular watch SUBDIAL plate, viewed perfectly straight-on,
> isolated on a fully transparent background, high-resolution render,
> nothing outside the circle. RIM: a narrow raised bezel ring in a
> brushed metal, the same brushed, softly antiqued texture as an
> engraved luxury watch letter — fine lengthwise brushing, gentle wear
> on the edges, a slight three-dimensional rounded profile that catches
> the light. INTERIOR: a dark slate-graphite engine-turned field
> (guilloché tapisserie — a fine repeating machined pattern of tiny
> squares or circular ripples), matte, elegant, COMPLETELY EMPTY: no
> numerals, no hands, no text, no logo — the plate is a blank canvas
> for content drawn later. LIGHTING: flat and neutral, lit evenly from
> directly overhead with no directional shadow of any kind — the render
> code casts its own shadow live, so the plate itself must read as if
> lit from dead center, no side, top or bottom bias. Palette strictly:
> a neutral brushed metal rim, dark slate/graphite interior; no bright
> colors, no color cast from the metal choice — the program recolors
> the rim live. Square canvas, the circle filling ~95% of it,
> transparent corners. NO lettering anywhere.

Any metal read the rim brief above — the program recolored it, so only
the TEXTURE (brushing, wear, rounded profile) and the flat lighting
mattered. This brief no longer drives any generation; it stays here
only as visual-target inspiration should the owner ever want a NEW set
generated in a similar spirit.

## Wiring (live)

`subdial_plate_file(finish, tint=None)` reads the ACTIVE set from
`config.paths.subdial_set()` (a module global set by
`app.controller.apply_display_settings` from `Settings.subdial_set`,
mirroring the art-source switch — the function's own signature never
changed, so `render.layers.draw_slot_roundel`'s call site did not need
to either). For sets 1-4 it returns the matching hand-drawn file
directly — `assets/subdial/<set>/<finish>.png` (`<set>` = set1..set4,
`<finish>` = gold/silver/bronze — twelve files, no placeholder glob
needed since every combination is a real file on disk). For "solo" it
returns `assets/subdial/solo/<finish>.png` where `<finish>` = silver AS
DRAWN (the only hand-drawn file — the owner's original silver plate),
or a disk-cached live recolor for gold/bronze. The layer draws the
directional shadow separately, underneath, keyed off the seat's own
dial position — never the file, in either model.

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
- **RULE #19 ENFORCEMENT (owner decree 2026-07-20, same round):** the
  sheet collapsed to a single master per source — gemini's silver
  `center` plate (the PURGE round's original) and one of chatgpt's
  fresh gold `center` generations, each dropped as a source's own
  subdial/master.png — with every OTHER finish derived live via
  `render.assets.subdial_plate_file`/`_recolored_plate`.
- **THE Rsub ROUND (owner decree 2026-07-21) — CURRENT MODEL:** the
  one-master-per-source idea retired WHOLE, not refined. The subdial
  plate stops being an art-SOURCE family at all — the owner hand-picked
  13 plates (`UV/subdial/` inbox) forming FIVE SETS: four full sets of
  three hand-drawn finishes each (gold/silver/bronze — "set1".."set4"),
  plus a fifth "solo" set carrying only a hand-drawn silver, gold/
  bronze still algorithmic. Both former per-source master files are
  `git rm`-ed (their subdial/ folders are gone with them); the new tree
  lives at `assets/subdial/<set>/<finish>.png` (`<set>` = set1..set4,
  `<finish>` = gold/silver/bronze) and `assets/subdial/solo/<finish>.png`
  (`<finish>` = silver, the only hand-drawn file there) — a root
  deliberately OUTSIDE `constants.ART_SOURCED_ROOTS` (see
  `assets/___assets.md`: the set choice is now orthogonal to the
  Gemini/ChatGPT art-source pick, not nested under it). The user picks
  the SET in Settings (`Settings.subdial_set`, default `"set1"`); the
  letter FINISH (`ring_finish`, tray Design menu) still decides which
  color draws within it, exactly as before.
