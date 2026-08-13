# World

**Script:** [World (script)](../world.py) · **Flow:** [diagram](../__flow/world.md)

## Purpose
THE TWO WORLD-MODES ([the ring rework ledger](../../research/ring_rework.md)
§1) as pure arithmetic: which of the two turns — the sky, or the world —
and by how many degrees, at this moment.

NOON_UP is the dial every release before this one drew: the observer
stands still and the sun travels, so the STAR rotates toward true solar
noon and the hour band never moves. SKY_UP stands the star still
and turns the WORLD beneath it — one offset carried by the outer band,
the letters, the crown text, the aura and umbra, the weekday seats, the
Earth and Moon markers and the hour hand alike — and inverts the whole
dial through the night.

Two numbers come out of this module and the render layer uses nothing
else to place a rotating element:

| Number | Who rides it |
|---|---|
| `pointer_rotation_deg` | the star/pointer, its arms and diamond seats, the umbra, the aura's own wedges |
| `world_offset_deg` | the outer numeral band, the ring letters, the crown text, the daylight arcs, the Earth and Moon markers, the hour hand, and every hover hit zone that reads the dial band |

The two never disagree with each other by accident: in NOON_UP the
world offset is exactly 0 and the pointer rotation is what it always
was (so the mode is a bit-for-bit no-op there), and in SKY_UP the
world offset carries `−star_rotation` so that true solar noon lands
under the pointer's own top arm — the two cancel by construction.

**The phase is the SUN'S ACTUAL STATE, never a count of flips.** Above
the horizon = DAYLIGHT, below = NIGHT. That fact already exists on the
tick (`core.clock_state.TickState.is_daylight`, itself derived from the
day's regime and boundaries), so an ordinary day yields two genuine
transitions, and polar day / polar night yield ZERO for months — Tromsø
simply stands in its phase and nothing ever fires.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `WORLD_MODES`,
  `WORLD_MODE_DEFAULT`, `WORLD_NIGHT_PHASE_DEG`, `WORLD_FLIP_DURATION_S`

### Used by
- [Compositor](../../render/__about/compositor.md) — resolves both
  numbers once per paint, threads them into `RenderContext`
  (`rotation` / `world_offset`) and owns the flip animation's clock
- [Layers](../../render/layers/___layers.md) — every rotating element
  reads one of the two off the context
- [App (folder)](../../app/___app.md) — the controller reports each
  tick's daylight state and says whether the change may animate
- [Tests (folder)](../../tests/___tests.md) — `tests/test_world_mode.py`
  pins the Belgrade band offsets, the phase boundaries, both polar
  regimes and the flip

## Functions
- `night_phase_deg(is_daylight)`: `0.0` by day, `WORLD_NIGHT_PHASE_DEG`
  (180) by night — the phase part of every offset below.
- `solar_part_deg(star_rotation, solar_rotation)`: `−star_rotation`
  while the Solar Rotation switch is on, `0.0` while it is off. The
  MINUS is the whole sign derivation: `star_rotation_deg` is the dial
  angle at which true solar noon stands, so the band must turn by the
  negative of it to bring that angle to the top.
- `world_offset_deg(mode, star_rotation, solar_rotation, phase_deg)`:
  `0.0` in NOON_UP; `solar_part + phase_deg` in SKY_UP.
- `pointer_rotation_deg(mode, star_rotation, solar_rotation, phase_deg)`:
  today's `star_rotation`-or-0 in NOON_UP; the phase alone in
  SKY_UP — the star stands upright and never tilts toward noon
  again, because the world already turned noon under it.
- `flip_eased(progress)`: the smoothstep the turning move runs on —
  `0` and `1` exactly at the ends, symmetric, no overshoot.
- `flip_phase_deg(start_deg, target_deg, elapsed_s, duration_s)`: the
  phase mid-move; `target_deg` exactly once `elapsed_s` reaches the
  duration, and immediately for a zero/negative duration (the snap a
  clock correction takes).

## Design Decisions
- **One offset, not many.** Every world member takes the SAME number, so
  a letter and the numeral beside it can never drift apart.
- **The phase animates; the solar part does not.** The solar part moves
  by minutes a day and is folded in at the target; only the 180° flip is
  ever interpolated, which is why the render layer can animate by
  ROTATING already-painted plates instead of re-rendering them.
- **No wall clock here.** `elapsed_s` arrives as an argument, exactly
  like every other moment in `core/`.
