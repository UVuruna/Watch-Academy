# Watch Face Shared Widgets

**Script:** [Widgets (script)](../widgets.py)

## Purpose
The layout VOCABULARY every Watch Face section imports — the width-aware
flow, the row shapes built on it, the pill and the slider row —
extracted so no section redefines the same styling or its own wrap
(Rule #5).

**The gallery grammar moved out on 2026-08-14:** `tile` and
`flow_gallery` were deleted with the CardGroup migration. Their job —
a picture choice and a gallery of them — belongs to
[Controls](controls.md)'s `OptionCard`/`CardGroup`/`picture_group`,
which additionally carry the mandatory hover blurb, the group title and
sentence, radio-vs-switch kind and the icon growth. Keeping a second,
blurb-less tile builder alive would let a section fork back to it, so
there is exactly one.

## Connections

### Uses
- [UI Style](../../__about/ui_style.md) — `style_button`
- [Config (folder)](../../../config/___config.md) — `palette.THEME_COLORS`
  (the selected-tile border accent)

### Used by
- `app.watch_face.pointer` / `.ring` / `.hands` / `.umbra_aura` / `.size`
- [Controls](controls.md) — the element classes compose `FlowLayout`,
  `FlowContent`, `literal` and `TILE_ICON_PX`

## Functions
- `FlowLayout` / `FlowContent`: THE gallery shape since 2026-08-09 (replacing the fixed-column `pack_grid`, whose
  wrap could not satisfy both ALG-7 and the window minimum at once):
  uniform tiles (the widest label decides, ALG-5) flowing by REAL
  width, CENTERED per the owner's 2026-08-14 decree (left-packed from
  2026-08-06 until then), inside a host
  that publishes its true height at its current width (QScrollArea
  never consults heightForWidth on its own). Since 2026-08-13 that
  publishing happens from `minimumSizeHint()` (the hint the scroll area
  actually reads) and on every `LayoutRequest` as well as on resize — a
  resize is not the only way content grows, and switching stack pages
  changed the content at an unchanged width, leaving the published
  minimum stale. `FlowContent` also serves as the page holder in
  `window.py`; it forwards to whatever layout it holds.
- `number_row(tr, settings, setters, key, low, high, title, form,
  decimals=0)`: the shared numeric slider row (numerals-ledger units) —
  used by the Numerals relief rows and the Size section's band-size
  rows (ALG-9 moved the three size sliders there, owner 2026-08-09).
- `pill(label, checked, on_click)`: a small `QPushButton`, "next" style
  when checked, else "neutral"
- `flow_row(members)` / `FlowRow`: a row of pills/buttons that WRAPS
  instead of running off the page (Space & Legibility ladder step 2).
  Measured on the Themes & Slots page at the 1280x720 minimum, where the
  face-layout row and the content-kind tabs were both cut by the right
  edge — a capture at the previous commit proves it predated the
  CardGroup migration. The row then does two things on show and on every
  resize, in this order: it EQUALIZES its same-kind members (ALG-5, and
  only after `ensurePolished` — an unparented button hints at the bare
  application font) and FILLS the line up to `FILL_FACTOR` times a
  member's natural width (ALG-7). Only the row's own most-numerous class
  is filled, so the lone Names checkbox riding the slot row's tail is
  never stretched into looking like a button. Publishing the wrapped
  height happens AFTER both — a height published before the widths
  changed described a row that no longer existed, and the pills below
  were drawn straight over it.
- `TILE_ICON_PX` (128): the shared gallery icon ceiling, now read by
  [Controls](controls.md)'s `OptionCard` as its `max_icon_px` default
  (owner instruction 2026-08-08: every picker shows WHAT IT PICKS at a
  readable size; nine call sites once relied on Qt's ~16px default
  while only Hands set its own).

## Design Decisions
- **`TILE_ICON_PX` lives in the builder, not per gallery** — the defect
  behind the owner's six 2026-08-08 screenshots was structural: a
  per-gallery `setIconSize` call that eight of nine galleries forgot.
  A default no caller can skip is the fix; today that default is
  `OptionCard`'s own `max_icon_px`.
- **A row is the same problem as a gallery** — `flow_row` reuses
  `FlowLayout` rather than growing a second wrap rule, for the same
  reason the fixed-column grids died in 2026-08-09.
- **Rows justify before they center** (`FlowLayout.MAX_JUSTIFY_GAP_PX`)
  — leftover width is first spent widening the gaps, up to the point
  where a row would read as unrelated pieces; only what remains is split
  at the ends, which is the CENTER alignment the owner sealed on
  2026-08-14.
- **The lonely tail is rebalanced** (`FlowLayout._columns`) — nine equal
  cards with room for four wrap 3-3-3, not 4-4-1. The owner's rule is
  FILL THE ROW ("3-3-2 kad ima prostora za 4-3"), so a tail of at least
  half a row keeps the greedy answer untouched; only a thinner tail,
  whose band stood empty in the runtime audit, is spread.
