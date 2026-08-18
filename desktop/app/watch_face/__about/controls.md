# Controls

**Script:** [Controls (script)](../controls.py)

## Purpose

THE ELEMENT CLASSES (owner ballot verdicts 2026-08-14 — 1A, and the
follow-up seals): the shared grammar of the Watch Face window's picker
elements. `widgets.py` holds the VOCABULARY (tile/pill/flow builders);
this module holds the GRAMMAR the ballot found missing — who is a
radio, who is a switch, how a group aligns, describes and resizes
itself:

- **`OptionCard`** — one choice with (or without) a picture. Owns its
  `kind` (RADIO amber / SWITCH green selection border — always
  reserved, never resizing the box), its MANDATORY hover `blurb`, and
  its icon size clamped to `[min_icon_px, max_icon_px]`.
- **`CardGroup`** — the grammar: title + one-sentence description,
  RADIO exclusivity enforced by the group (a card cannot know its
  sisters), independent switches, the DIVIDER line whenever the radio
  and switch subsets meet inside one group (owner order 2026-08-14),
  CENTER-flowing rows (the sealed alignment), uniform member widths
  (ALG-5), icons GROWING toward `max_icon_px` as the viewport widens
  (the wide-window remedy the owner approved), and
  `disable_with_reason` — a group is grayed with a tooltip, never
  hidden.
- **`picture_group(...)`** — THE ONE DOOR every picture gallery walks
  through since the migration of 2026-08-14. It takes
  `(key, label, blurb, icon)` radio entries and
  `(key, label, blurb, icon, on)` switches, wires the section's own
  live-apply setters, sets the current pick and calls `finish()`. It
  replaced the `QGroupBox(title) + QLabel(sentence) +
  widgets.flow_gallery([tile, ...])` triple that eleven galleries each
  assembled by hand — which is why eleven galleries could each forget
  the blurb, the reserved border or the uniform width.

## Connections

### Uses

- [Widgets](widgets.md) — `FlowLayout`/`literal`/`TILE_ICON_PX`, the
  shared vocabulary this grammar composes
- [Ui Style](../../__about/ui_style.md) — `tooltip_wrap` for blurbs
- [Palette (config)](../../../config/__about/palette.md) —
  `THEME_COLORS["accent"]` (radio) and `UI_BUTTON_COLORS["next"]`
  (switch): no new hex enters the program

### Used by

- EVERY picture gallery in the window, through `picture_group`:
  [Pointer](pointer.md) (the variant gallery), [Ring](ring.md) (preset
  + inner), [Hands & Bodies](bodies.md) (hands, globe, marker shape,
  the Moon's four, eclipses, stations),
  [Umbra & Aura](umbra_aura.md) (form + contrast),
  [Themes & Slots](themes.md) (artwork, subdial set),
  [Theme Tree](theme_tree.md) (complications, style families) and
  [Weekday Theme Grid](../../__about/weekday_theme_grid.md) (theme
  families, a family's casts, the calendar mount)
- The knob-bearing sections — `opacity`/`size`/`colors`/`numerals` —
  through `ValueKnob`/`knob_row`

## Design Decisions

- The RADIO/SWITCH split lives on the GROUP (`add_card` follows the
  group's mode, `add_switch` is always a switch): mixing kinds
  arbitrarily inside one flow was the bug class the ballot named, so
  the API makes it unrepresentable — and the divider between the two
  subsets draws itself. Both doors are one line over `_add(kind, ...)`,
  which is the only place that knows a member joins its kind's own
  dict, host and flow (clone C7, OOP audit 2026-08-18).
- A `blurb` is a REQUIRED constructor argument (owner order: hover
  description always exists). An intentionally empty blurb must be
  passed explicitly — omitting it is a TypeError, not a silent blank.
- **The card host is a `FlowContent`, never a bare `QWidget`** — a flow
  only knows its height once it has a width, and `QScrollArea`'s
  widgetResizable path sizes pages from plain minimum hints. The bare
  host the first draft used would have let a wrapped group starve
  inside the page's scroll area, the measured failure
  [Widgets](widgets.md) documents.
- **A group is painted, not implied** — the box wears `surface_2` inside
  a `surface_3` hairline. `surface_1` was tried first and is not
  distinguishable from the page ground at the audit's own 12-per-channel
  tolerance, which is a measurement of exactly what the eye reported: a
  group that reads as nothing at all.
- **A card is never narrower than its own label** — both
  `OptionCard.sizeHint` and `minimumSizeHint` pass Qt's answer through
  ONE `_label_floor(hint)`, measured from the text, so a longer name in
  any language moves the floor and neither hint can drift from the
  other (clone C8; the 2026-08-15 CLIPPED finding is in that method's
  docstring).
- **Its own height, and not a pixel more** — `heightForWidth` /
  `sizeHint` / `minimumSizeHint` all answer from the COLUMN's
  arithmetic. QGroupBox's minimum is computed from the flow's one-row
  minimum (far too little for a wrapped gallery) while its frame
  allowance runs a few pixels above what the column margins actually
  consume (which reads as a permanent clip). Both were measured on
  2026-08-14.
- **An empty host is not space** — a group with no switches hides the
  switch host entirely; a zero-height child still cost the column's
  spacing and was reported by the audit as drawn over its sibling.
- Icon growth happens in `CardGroup.resizeEvent`, not per card: the
  group is the only one who knows the row's width budget, and clamping
  at `min_icon_px` is what lets a narrow window wrap instead of starve.
