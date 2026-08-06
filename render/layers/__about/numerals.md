# render/layers/numerals.py

The band cache key, and the one live-crown layer.

| Name | Kind | Answers |
|---|---|---|
| `band_spec` | function | the `BandSpec` an on-screen watch would ask for |
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

`LiveCrownLayer` is the ONE minute-cadence element of this round. It is
minute-cadence and nothing more: the eleven glyphs it draws were rasterized
at settings-apply time, so its per-tick work is a sequence lookup, an arc
layout and eleven-at-most `drawImage` calls.

## Which presets carry a live crown

`config.dial.RING_LIVE_CROWN` names them, and it is the only place that
list lives:

- **The One** — the top arc is the watch's OWN civil time. Its bottom arc
  is "City, Country", which the existing `Settings.ring_crown_location`
  path already draws through `RingLayer`; this layer does not duplicate it.
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
