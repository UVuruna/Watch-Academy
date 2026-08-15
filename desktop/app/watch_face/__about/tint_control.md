# The Compact Tint Control

**Script:** [Tint control (script)](../tint_control.py)

## Purpose
Ballot verdict 4A (owner, 2026-08-15): one compact row per colour
target, with the whole palette one click away in a popover — replacing
the same 42-swatch grid drawn seven times down the Colors page.

    Ring tint   (o)  Change…   Gunmetal — #2A3439

## Connections

### Uses
- [Tint Picker](tint_picker.md) — `round_swatch`, `tint_label_text`, and
  `build_preset_grids` for the "All colours" reveal. The grid keeps ONE
  implementation (Rule #5); it simply moved behind a door.
- [Controls](controls.md) — `ValueKnob` in `KnobKind.K360` for the
  custom hue wheel
- [Config (folder)](../../../config/___config.md) —
  `palette.RING_TINT_GROUPS` (the hues the seats point into),
  `palette.RING_TINT_NONE_SWATCH`, `palette.RING_TINT_PICKER_SEED`,
  `palette.KNOB_FAMILY_COLORS["hue"]`, `dial.RING_TINT_SWATCH_PX`

### Used by
- [Colors](colors.md) — every tint target on the page: Ring tint, Inner
  (Minute track), Hands, Jewels, Crown Text, and the Umbra/Aura custom
  pickers

## Design Decisions

- **Why it exists, measured before it was touched.** The same grid of 42
  preset swatches was drawn SEVEN times on one page — about 290 circles,
  many indistinguishable at swatch size (five greys, four near-identical
  yellows) — and the page ran three screens long. The owner's objection
  on the ballot was that the space was bought with nothing.
- **THE TWELVE SEATS are his, and they are one list.** His ballot
  verdict names twelve tints and answers the scope question in his own
  words — "the same twelve everywhere", not per control, not last-used.
  They live HERE, in `OPEN_SEAT_NAMES`, not in `config.palette`, and
  the boundary is responsibility (THE STRUCTURE LAW): the palette owns
  the HUES, this module owns the PICKER, and "which twelve does the
  picker open with" is a picker decision. They sat in `palette.py` for
  one round and pushed that module past the config-cohesion threshold,
  which is how the question got asked at all. NAMES, not hex, so
  retuning a hue moves the seat with it and deleting one raises at
  `open_seats()` instead of silently seating nothing.
- **Nothing is lost.** The twelve sit open in the popover; "All
  colours…" reveals the full Lighter/Darker grids; "Custom" reaches any
  hue at all. Hidden, never absent — the full grid is the promise that
  the twelve cost nothing.
- **The custom picker is the app's ONE K-360** (knob taxonomy, verdict
  7): a hue genuinely IS an angle. It previews live over a chip and
  commits on Apply, so turning the wheel does not fire a rebuild of the
  watch per degree. The wheel moves ONLY the hue and keeps the seed's
  saturation and value — a wheel that flattened those would make every
  custom pick the same garish primary. The knob's ring wears the live
  hue rather than a family colour, which is the one place a family
  colour may move: there the ring is showing the value, not labelling a
  family (see the `"hue"` entry in `palette.KNOB_FAMILY_COLORS`).
- **The state reads BESIDE the control, not across the row.** Pushed to
  the far right by a stretch it was the first thing a narrow window cut
  ("Gray (…"), and it reads better next to the button it describes. The
  stretch goes after it, so leftover width stays leftover.
- **The swatch lives in its own container** (runtime audit ALG-5): it is
  a `QPushButton` and so is "Change…", and the uniform-siblings rule
  measures same-kind controls sharing one container — a 22px circle
  beside an 86px button is exactly the mismatch that rule catches. The
  circle is a swatch, not a button of the same family, and the honest
  way to say so is to stop making them siblings.
- **Both the swatch and the button open the popover.** The swatch is the
  bigger, more obvious target, and a user who clicks the colour expects
  the colours — on the old page it did nothing.
