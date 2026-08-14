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

## Connections

### Uses

- [Widgets](widgets.md) — `FlowLayout`/`literal`/`TILE_ICON_PX`, the
  shared vocabulary this grammar composes
- [Ui Style](../../__about/ui_style.md) — `tooltip_wrap` for blurbs
- [Palette (config)](../../../config/__about/palette.md) —
  `THEME_COLORS["accent"]` (radio) and `UI_BUTTON_COLORS["next"]`
  (switch): no new hex enters the program

### Used by

- The Watch Face section modules, migrated one by one (classes phase,
  ballot verdict 1A) — `pointer`/`ring`/`bodies`/… adopt
  `CardGroup` in place of hand-rolled QGroupBox+loop pairs

## Design Decisions

- The RADIO/SWITCH split lives on the GROUP (`add_card` follows the
  group's mode, `add_switch` is always a switch): mixing kinds
  arbitrarily inside one flow was the bug class the ballot named, so
  the API makes it unrepresentable — and the divider between the two
  subsets draws itself.
- A `blurb` is a REQUIRED constructor argument (owner order: hover
  description always exists). An intentionally empty blurb must be
  passed explicitly — omitting it is a TypeError, not a silent blank.
- Icon growth happens in `CardGroup.resizeEvent`, not per card: the
  group is the only one who knows the row's width budget, and clamping
  at `min_icon_px` is what lets a narrow window wrap instead of starve.
