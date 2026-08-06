# app/watch_face/numerals.py

The Watch Face window's **Numerals** page — the controls for the two
LIVE-RENDERED numeral bands and the live crown.

## Purpose

`research/hour_numerals.md` §8 and `research/ring_rework.md` §5 settle a
list of settings; this page is where a reader meets them. FIVE groups,
in the order they appear on the dial — the MODE first, because it is the
one pick that says whether the hour band below is a fixed ring of markers
or a world that turns:

| Group | Rows |
|---|---|
| **Mode — which one turns** | world_mode (`Geocentric (Ptolemy)` / `Heliocentric (Copernicus)`, `dial.WORLD_MODE_LABELS`) |
| **Hour ring — the outer band** | ring face (the 7-face roster), numeral size, **outer ring size** (the width of the band the letters and numbers stand in), seating (`arc` / `upright`) |
| **Minute ring — the inner band** | inner face (the 5-face roster), numeral size |
| **Relief** | relief style (`cast` / `extrude` / `emboss`), depth, light (`radial` / `fixed`), darkness, contact blur, border |
| **The live crown** | crown face, time format (`12:35` / `12h 35min`) |

Solar Rotation is deliberately NOT here: it stays its own independent
switch in the right-click menu and keeps meaning the same thing in both
modes (whether the solar offset is taken at all).

Every combo is built from the vocabulary in `config.dial` itself, in the
order documented there — so the page can never offer a value the settings
store would reject as corrupt, and adding a roster face is a one-line
config edit rather than a UI edit.

## What is deliberately absent

The inner band carries no seating, no relief and no rotation control:
the ledger settles that it NEVER rotates in any mode, that it follows the
hour ring's seating, and that its relief is the fixed white glow. The
page says so in a note rather than offering dead controls.

The crown keeps its OWN face rather than following the hour ring,
because the crown needs the colon and the hour ring only needs digits —
and on this install the hour ring's default face draws an empty colon
(see [Numeral Fonts](../../../render/__about/numeral_fonts.md)).

## Live-apply

Like every Watch Face section: each pick calls its setter through
`setters` immediately, the controller persists and rebuilds the skin,
and the window rebuilds this page fresh. Nothing here holds state.

## Connections

### Uses
- `config.dial` — the rosters, ranges and SETTLED defaults

### Used by
- [Watch Face Window](window.md) — registers it as a sidebar section
