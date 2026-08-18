# render/layers/numerals.py

The band cache key, and the one live-crown layer.

| Name | Kind | Answers |
|---|---|---|
| `band_spec` | function | the `BandSpec` an on-screen watch would ask for |
| `jewel_offset` | function | how far the JEWELS and the CROWN have turned |
| `plate_aspect` | function | one jewel plate's width over its height |
| `jewel_ink_halves` | function | per-seat half-wedge of the jewel's real ink |
| `occluded_hours` | function | the numerals a FIXED jewel currently covers |
| `crown_spec` | function | the `CrownSpec` for the live crown's glyph set |
| `LiveCrownLayer` | `Cadence.MINUTE` | the crown's live time, re-composed each tick |

## Purpose

**The two BAND layers that used to live here are gone** (THE FIDELITY
RULING, owner correction 2026-08-06). They stacked a computed plate on top
of `RingLayer`'s printed one, which is exactly the construction the ruling
outlaws — an Ω with a printed 0 showing under it. Both bands are now part
of the ring's own ordered composition ([Ring](ring.md)); a band layer
reappearing in the stack IS that defect coming back, and
`tests/test_numerals.py` fails the suite if one does.

`band_spec` stayed, because it is the shared door BOTH the ring layer and
every test go through to ask for a plate. Besides the numeral settings it
carries: the OUTER band's `offset_deg` (THE WORLD OFFSET,
[World](../../../core/__about/world.md)), the preset's LETTER seats, the
picked INNER variant's name, and the ring's tint/saturation — because two
presets sharing every numeral setting still compose different bands, and a
COMPUTED plate must answer the Ring sliders exactly as the printed plate it
replaces did. The INNER band keys on `offset_deg = 0.0` in every mode, so
its plate is shared across both phases (ledger §2: "the inner band NEVER
rotates").

**WHAT THE ROTATION CARRIES** (owner ballot verdict 2026-08-13). Two small
functions moved in beside `band_spec`, because both answer the same
question it does — what the outer band looks like right now:

- `jewel_offset(skin, world_offset, night_phase)` is THE ONE DOOR for the
  scope. It returns the world offset in `all_turn` and, in
  `numerals_turn`, THE NIGHT PHASE ALONE.
  **THE WORLD OFFSET IS TWO TERMS, NOT ONE** (owner order 2026-08-16):
  `core.world.world_offset_deg` is `solar_part + night_phase`, and only
  the SOLAR term is what the scope switch chooses between. The night is
  not a rotation anybody picks — it is the state of the world, and it
  turns the WHOLE ring over, every jewel in it, exactly as it does with
  Solar Rotation off. This used to return a flat `0.0`, which threw both
  terms away: the jewels held their DAYLIGHT seats all night while the
  hands turned over under them, and `crown_text_night` could never draw
  because `arc_crosses_horizon(centre, 0.0)` is False at every angle —
  one number, two defects, both fixed by putting the night term back.
  The phase passed in is the EASED one (`Compositor.phase_deg` /
  `ctx.rotation`), so the jewels turn on the same animated arc as
  everything else and every baked member stays phase-linear, which is
  what lets the compositor rotate finished pixels mid-flip.
  Every site that places a jewel, a crown glyph or one of their HOVER
  zones asks here — [Ring Layer](ring.md)'s two draw methods, the
  `LiveCrownLayer` below, and the compositor's `_jewel_offset` /
  `_jewel_theta` (the Omega hit circle, the per-letter jewel legend, the
  Four Greetings trigger and the crown-word hover). One door means the
  drawn dial and the hit zones cannot disagree.
- `plate_aspect(asset)` is one jewel plate's width over its height, read
  from the startup asset index (which knows every picture's size without
  opening it) and cached per path. A file the index never saw costs one
  header read; one that will not decode falls back to 1.0.
- `jewel_ink_halves(skin)` is `hour -> half the arc that seat's jewel
  really covers`, built from exactly the terms [Ring Layer](ring.md)
  stamps with — the `RING_JEWEL_ART_SCALE * ring_jewels_scale` height,
  that seat's `jewel_zoom`, the `outer_centreline` radius, and the
  plate's own aspect. THE INK WEDGE's jewel half (owner order
  2026-08-13): an M claims the width of an M and an I the width of an I,
  where both used to claim a square.
- `occluded_hours(skin, ctx)` returns `()` in `all_turn` — where the
  jewels ride their own seats and a collision is impossible — and
  otherwise THE INK WEDGE's answer from
  [Core Numerals](../../../core/__about/numerals.md), with BOTH halves
  measured: `jewel_ink_halves` above and
  `render.numeral_bands.numeral_ink_halves` for the numerals. It rides
  `BandSpec.occluded_hours`, a SECOND key beside `jewel_hours` rather
  than a reuse of it, because the two say different things — one is
  "this seat belongs to a letter", the other "this numeral happens to be
  underneath one right now", and only the second changes as the world
  turns. In `numerals_turn` `jewel_hours` is therefore empty: a fixed
  jewel owns a place on the SCREEN, not a seat, so the labels 6, 12, 18
  and 0 are composed the moment the rotation carries them clear.

`LiveCrownLayer` is the ONE minute-cadence element of this round. It is
minute-cadence and nothing more: the plate tiles it draws were rasterized
at settings-apply time, so its per-tick work is a sequence lookup, an arc
layout and eleven-at-most `drawImage` calls.

`crown_spec` resolves `skin.ring.crown_text_metal` (the SAME
`settings.ring_finish` the ring's own jewels wear) and its active
`paths.metal_shade` into the `CrownSpec.metal`/`.shade` fields THE TIME
CROWN LOOK (owner correction 2026-08-06) styles every glyph by — never
the outer band's `numeral_relief`/`numeral_depth`/`numeral_light`/
`numeral_darkness`/`numeral_border` knobs, which no longer reach the
crown at all (see [Numeral Bands](../../__about/numeral_bands.md) for
the glyph build itself).

**ONE CROWN SIZE LAW / ONE METAL PER CROWN** (owner defects 2026-08-07).
`crown_spec` now also solves:

- `height_px` — the glyph BOX, from the SAME expression
  [Ring Layer](ring.md) uses for the static arc,
  `2 * radius * RING_CROWN_TEXT_SIZE * crown_text_scale`, in DEVICE
  pixels. It replaces `size_units`, which read the HOUR BAND's
  `numeral_outer_size` and put a second, smaller size family on one ring
  — the owner's "microscopic" crown. `ring_jewels_scale` is deliberately
  absent (THE DECOUPLED SCALES, below).
- `colon_source` — the file `jewel_metal_file` ACTUALLY resolved for the
  colon plate, in the cache KEY so the crown's baked tiles cannot outlive
  the background recolor's gold fallback (the gold colon beside silver
  digits the owner photographed on Templar).

`LiveCrownLayer` lays the arc out by THE CROWN ADVANCE LAW: it passes
`crown_glyph_ink`, the crown radius and
`height_px * CROWN_TRACKING_FRACTION` to `compose_crown`, so each glyph
takes the arc its own ink needs instead of a fixed step.

**THE DECOUPLED SCALES** (owner defect 2026-08-07): the Jewels slider
used to grow the crown, because the crown height multiplied
`ring_jewels_scale` AND `crown_text_scale`. Each term now scales its own
family only — Jewels scales jewels, Crown Text scales EVERY crown arc,
static and live. Both default to 1.0, so the folded constant is exactly
1.0 and no default dial moved a pixel.

## Which presets carry a live crown

`config.dial.RING_LIVE_CROWN` names them, and it is the only place that
list lives:

- **The One** — the top arc is the watch's OWN civil time. Its bottom arc
  is "City, Country", drawn through `RingLayer`'s own crown-text arc from
  the jewel LETTER PLATES. Since the 2026-08-07 round that bottom arc is
  RULED BY THE PRESET (`RING_LIVE_CROWN["The One"]["location"] ==
  "bottom"`, wired in `app.skin_builder._compose_skin`) rather than served
  only by the per-ring `Settings.ring_crown_location` toggle — the toggle
  is OFF by default and draws at the TOP, straight through the live time,
  so the ruled line simply did not exist on the owner's dial. The toggle
  still wins when the user ticks it; the two never draw together.
- **Templar** — the top arc is the hour of **Jerusalem**
  (`Asia/Jerusalem`, resolved through `tzdata` in `core.clock_state`, whose
  `TickState.crown_zone_hm` carries every crown zone's `HH:MM` for the
  tick). Its bottom arc, NON NOBIS DOMINE, is a STATIC plate arc declared
  in the preset card — untouched here.

Every other preset builds no `LiveCrownLayer` at all.

## Connections

### Uses
- [Numeral Bands](../../__about/numeral_bands.md) — the plates and glyphs
- [Numerals](../../../core/__about/numerals.md) — the crown sequence
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`

### Used by
- [Ring Layer](ring.md) — asks `band_spec` for both band plates and
  composes them
- [Compositor](../../__about/compositor.md) — builds `LiveCrownLayer` for
  the two presets that keep a time in the arc
