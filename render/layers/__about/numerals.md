# render/layers/numerals.py

The three layers that put the live-rendered numerals on the dial.

| Layer | Cadence | Draws |
|---|---|---|
| `OuterNumeralLayer` | `STATIC` | the 24 hour numerals band plate |
| `InnerNumeralLayer` | `STATIC` | the minute numerals + tick lines band plate |
| `LiveCrownLayer` | `MINUTE` | the crown's live time, re-composed each tick |

## Purpose

`RingLayer` still draws everything it drew before — the outer plate PNG,
the inner plate PNG, the preset's letter art and the static `crown_text`
stamps. These layers ADD the hand-drawn numerals on top of that
composition; nothing was replaced.

The two band layers are `STATIC`, so the compositor bakes them into its
cached pixmap and they cost nothing per frame. Each asks
[Numeral Bands](../../__about/numeral_bands.md) for a plate keyed by the
skin's numeral settings and the plate pixel size, and blits it centred on
the dial origin. A settings change rebuilds the composite, which asks for a
plate under the new key, which builds once and is then shared by every
watch on those settings.

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
- [Compositor](../../__about/compositor.md) — stacks them just above
  `RingLayer`
