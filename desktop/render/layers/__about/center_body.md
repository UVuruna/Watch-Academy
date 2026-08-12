# Center Body Layer

**Script:** [Center Body Layer (script)](../center_body.py) ·
**Flow:** [diagram](../__flow/center_body.md)

## Purpose

Paints the current day's body seated at the dial's literal center, ABOVE
the hands, so the hands sweep behind it: the opaque Sun on Sundays for the
hexa/trio center-duality wheels, or today's body in `center_only` mode.
During the reveal-week window the ghost center Sun also rises here, opaque,
on every day — that IS the z-order lift the reveal promises. On an actual
Sunday the SOLAR clock (not the wall clock) may swap the face to the
Servant or, where the theme names one, the Ninth (`center_dual_face`). THE
BLUE MOON LAW (owner-sealed 2026-07-22) is checked FIRST, independent of
everything else: when the Calendar pointer's own mode is showing a 13th
month/animal today, that plate draws here instead — the Calendar pointer
never carries a classic weekday seat, so its own dial center is otherwise
empty.

`Cadence.MINUTE`: the solar-time dual-face windows and the Blue Moon
13th's own window are evaluated against `ctx.tick`, and `hover_factor`
resizes the body live — needs a per-tick repaint. Not `hover_variable` —
`MINUTE` already repaints every frame, and this layer never calls
`Layer._gate`: unlike the seated/arm layers it does not need a hover z-lift
twin, because `_build_layers()` already appends it AFTER the hands, so
`hover_factor` alone resizes it in place without needing to rise above
anything.

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Ninths](../../__about/ninths.md) — `active_thirteenth`, `center_face`,
  `ninth_alt_active`, `theme_ninth`, `thirteenth_plate`
- [Painting](../../__about/painting.md) — `draw_name_label`, `draw_pixmap_centered`,
  `name_label_px`
- [Skin Geometry](../../__about/skin_geometry.md) — `center_duality`, `hover_factor`
- [Slot Layout](../../__about/slot_layout.md) — `center_dual_face`, `weekday_body_size`,
  `weekday_classic_slot`
- [Weekday Body](../../__about/weekday_body.md) — `draw_weekday_body`,
  `weekday_label_set_px`

### Used by
- [Compositor](../../__about/compositor.md) — appended right after the hand layers when
  `weekday_set` is in `z_order` and `show_weekday` is on (replaced by
  `ArchetypeCenterLayer` in Archetype mode); NOT one of `HoverLiftLayer`'s
  twins (see Purpose)

## Classes

### CenterBodyLayer
`cadence = Cadence.MINUTE`.
- `paint()`: checks `active_thirteenth` first (Blue Moon Law) and delegates
  to `_draw_thirteenth` if it names one; otherwise no-ops for a pinned slot
  layout or an inapplicable display mode, resolves the dual/Ninth face for
  an actual Sunday, and falls through to the plain `draw_weekday_body` call.
- `_draw_thirteenth()`: draws the Blue Moon 13th's own plate (or a
  name-only fallback) at the dial's exact origin, opaque, above the hands.

## Design Decisions

**No `HoverLiftLayer` twin — investigated 2026-08-01, confirmed
deliberate.** Every OTHER element-owning layer with individually-hoverable
elements (`WeekdayLayer`, `SlotLayer`, `YearMarkerLayer`, `ArchetypeLayer`,
`ArchetypeCenterLayer`) gets a `lift=True` twin in `HoverLiftLayer` because
those layers draw BELOW the hands in the base stack (`_build_layers()`) —
without the twin, an enlarged hovered element would visibly hide behind a
hand sweeping over it. `CenterBodyLayer` is structurally different: it is
appended to `_build_layers()` right AFTER every `HandLayer` instance
(`render/compositor.py`'s `_build_layers()`, "the current day's center
body rides ABOVE everything — the hands sweep behind the Sun"), so it is
already the top of the stack (short of the center-seated `SlotLayer`,
`ArchetypeCenterLayer` and `HoverLiftLayer` itself, which are mutually
exclusive with it or come after). `hover_factor()` inflating `center_size`
in place is therefore sufficient — there is no hand to rise above.

This also rules out the one other reason a twin might still be needed
despite already being top-stacked: `ArchetypeCenterLayer` sits in the
SAME above-the-hands slot yet still takes a twin, because it sometimes
paints at `ghost_opacity` (< 1.0, when its lit window is closed) — an
ungated base pass plus an unconditional twin pass would double-composite
a translucent pixmap into a visibly darker/more opaque result during
hover. `CenterBodyLayer` never has this hazard: every `paint()` path
draws at a hardcoded `opacity=1.0` (the `draw_weekday_body(...)` call's
literal `1.0` argument, and the explicit `painter.setOpacity(1.0)` in the
dual/ninth-face branch and in `_draw_thirteenth`) — it never draws
translucent, so it never needed `Layer._gate` or a second painting pass
in the first place, twin or not.

Evidence checked: `render/compositor.py::_build_layers()` (append order —
`CenterBodyLayer`/`ArchetypeCenterLayer` after `HandLayer`, before
`HoverLiftLayer`), `render/layers/hover_lift.py` (the five twins it
builds, `CenterBodyLayer` absent), `render/context.py::Layer._gate`
(the exactly-once invariant the gate exists to enforce), and
`render/layers/___layers.md` §Design Decisions (states the same
conclusion at the folder level: "`CenterBodyLayer` needs none: it is
already appended after the hands... no z-lift required"). No code change
made — the gap the owner flagged does not exist; hover on the center body
already enlarges correctly, in place, above the hands.
