# Hand Layer

**Script:** [Hand Layer (script)](../hand.py) ·
**Flow:** [diagram](../__flow/hand.md)

## Purpose

One class, three instances (hour/minute/second) — rotates a hand image
about its pack-defined pivot. Sizing uses TIP-TO-PIVOT lengths only: the
seconds tip reaches `second_reach_fraction` of the dial radius, the minutes
tip `minute_reach_fraction`, and the hours follow the pack's own
hours/minutes tip ratio — the counterweight below the pivot comes along at
the same scale.

`Cadence.MINUTE`: hands sweep continuously with wall-clock time, so they
must repaint every tick. Not `hover_variable` — `MINUTE` already guarantees
a live repaint every frame, and hands have no individually-hoverable
element.

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Asset Cache](../../__about/assets.md) — `ctx.cache.pixmap_by_height` (tinted to
  `ring_tint`, desaturated first when the pack's own art is colored)

### Used by
- [Compositor](../../__about/compositor.md) — instantiated once per hand kind
  (`skin.hands.z_order`, default hour → minute → second) whenever `z_order`
  reaches "hands"; the seconds instance is skipped when the skin has no
  seconds asset or `show_seconds` is off

## Classes

### HandLayer
`cadence = Cadence.MINUTE`.
- `__init__(skin, kind)`: `kind` is `"hour"`, `"minute"` or `"second"` —
  selects which `HandSpec` and which `TickState` angle this instance reads.
- `_spec` (property): the `HandSpec` for this instance's kind.
- `_tip_reach_fraction()`: the dial-radius fraction this hand's tip must
  touch — a direct skin setting for minute/second, derived from the pack's
  own hour/minute tip-height ratio for the hour hand.
- `paint()`: rotates by the kind's tick angle (`hour_angle` /
  `minute_angle` / `second_angle`), scales the pack's natural height so the
  tip lands exactly on the target reach, and draws the tinted pixmap with
  its pivot at the origin.
