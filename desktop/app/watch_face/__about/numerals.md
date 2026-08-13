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
| **Mode — which one turns** | world_mode (`Noon Stays Up (Heliocentric)` / `Sky Follows You (Geocentric)`, `dial.WORLD_MODE_LABELS`), and beside it **What turns** — world_rotation_scope (`Everything Turns` / `Numerals Turn`, `dial.WORLD_ROTATION_SCOPE_LABELS`) |
| **Hour ring — the outer band** | ring face (the 7-face roster), numeral size, **outer ring size** (the width of the band the jewels and numbers stand in), seating (`arc` / `upright`) |
| **Minute ring — the inner band** | inner face (the 5-face roster), numeral size |
| **Relief** | relief style (`cast` / `extrude` / `emboss`), depth, light (`radial` / `fixed`), darkness, contact blur, border |
| **The live crown** | time format (`12:35` / `12h 35min`) |

**What turns is GREYED OUT in Noon Stays Up** (owner question 2026-08-13,
and he was right to ask): `core.world.world_offset_deg` is exactly 0.0 in
that mode, so `render.layers.numerals.jewel_offset` hands back the same
number for either scope and the two picks draw a bit-for-bit identical
dial. Offering a live choice that changes nothing is the defect. The row
is DISABLED rather than hidden — hiding it would jump the form and take
the explanation with it — its tooltip says why, and the stored pick is
never touched, so it is waiting for him the moment he goes back to Sky
Follows You. `_follow_mode` installs that, and
`tests/test_world_mode.py::TestTheWhatTurnsRowFollowsTheMode` pins both
the premise and the behaviour.

The live crown has NO face row (THE ONE PLATE LAW, owner decree
2026-08-07): it draws the owner's letter plates like the jewels and the
crown text beside it, so the font pick that used to stand here — and
`Settings.crown_face` behind it — is gone.

**What turns** (owner ballot verdict 2026-08-13) is a DROPDOWN and not a
checkbox under Solar Rotation, because it is not a switch on the rotation
— it says what the rotation CARRIES. `Everything Turns` is every release
before it: the numerals, the jewels and the crown ride one offset, so a
jewel keeps its own seat and the seats it stands on never carry a number.
`Numerals Turn` pins the jewels and the crown to the screen; a numeral
that would pass under a jewel is left off the ring entirely (never drawn
half under a letter), and the seats the jewels vacate finally show their
numbers, midnight reading `0`. It is the DEFAULT `Everything Turns` on
every stored settings file that predates it, so nothing the owner already
sees changes until he picks.

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
