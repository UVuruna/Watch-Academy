# Time Travel

**Script:** [Time Travel (script)](time_travel.py)

## Purpose
The owner's scenario tester, opened from the menu: enter any moment and
any latitude/longitude — the dial renders that exact situation (sun arc,
hexagram tilt, Earth and Moon positions, moon phase, hovers) for
`TIME_TRAVEL_DURATION_S`, then returns to the present by itself. The
entered wall time is interpreted in the active timezone. Since Session
16 (owner slika 13, 2026-07-17) the moment editor accepts ANY year of
the active coverage INCLUDING BCE. **R5 MENU REWORK (item 3A, owner
spec: "TIME TRAVEL ostaje trenutni i proširuje se nadole"):** the
dialog now GROWS DOWN with its own Quick Jump section — see below —
absorbing the whole deep Quick Jump submenu chain the old right-click
menu used to hold (Rule #6, no both-paths).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — coordinate ranges,
  duration, the warning color, the advertised Deep Time span, era
  constants, the row icon/arrow pixel sizes
  (`TIME_TRAVEL_ROW_ICON_PX`/`TIME_TRAVEL_ARROW_BUTTON_PX`)
- [Deep Time](../core/deep_time.md) — era mapping, the proxy frame,
  month lengths, the year-line formatters
- [UI Style](ui_style.md) — the shared vivid button pills
- [Theme](theme.md) — the dark dialog surface + the moment editor's
  combos/spinboxes + `size_to_screen` (square, 50% height — the
  dialog grew enough this round to want the same opening-size law
  Settings/Guide already use)

### Used by
- [Watch Controller](controller.md) — `_open_time_travel()` passes the
  ACTIVE coverage (bundled ∩, widened by the pack), the bundled core
  coverage (the tier line), the year-line settings and the pack flag,
  plus (R5) `jump_callback=self._dialog_jump` and
  `jump_cities=self._settings.jump_cities`; feeds the frozen (proxy
  moment, cycles, observer) into the tick flow

## Classes

### TimeTravelDialog
Stay-on-top `QDialog`. The MOMENT editor (Session 16): a day spinbox +
month combo + year spinbox + ERA combo (labels per the `era_notation`
setting — BCE/CE default or BC/AD; the year INPUT is official-only,
owner amendment 2026-07-17) + an HH:mm time editor — QDateTimeEdit
cannot hold negative years. Internally everything is the ASTRONOMICAL
year (1 BCE = year 0); `moment()` returns the 400-year PROXY datetime
and `cycles()` its cycle count. The day spinbox re-clamps live to the
proleptic month length (Feb 29 only in leap astronomical years — year
0 IS leap). Latitude/longitude spinboxes and the vivid button row
(blue **Now** → `RETURN_TO_NOW`, green OK, neutral Cancel) as before.

**The dual-calendar header (owner amendment 2026-07-17).** A live bold
line pairs the target with its Anno Lucis year — "21 Jun 4500 BCE ·
-420. Anno Lucis" — plus the optional third calendar, through the ONE
formatter (`core.deep_time.format_year_line`).

**Coverage and the precision tiers (documented in-app).** A live
coverage line ("Coverage: 12999 BCE … 16993") and the tier line for the
ENTERED year: (i) bundled core years → "minute-exact"; (ii) inside the
pack span → "events exact; the local clock drifts ±hours at the far
extremes (ΔT)"; (iii) beyond → "only era lengths are known (Laskar), no
dates". The year spinbox deliberately reaches PAST the active coverage
(the greater of coverage and the advertised span) so an out-of-range
year can be DIALED and its refusal READ (owner 2026-07-16) — OK then
shows the warning inline and the dialog stays open, never travelling:
with the pack the message names the Laskar tier, without it the Deep
Time pack ("not installed").

<a id="quick-jump-rows-item-3a"></a>

**Quick Jump rows (item 3A, R5 MENU REWORK).** Below the coverage
warning, a `QGroupBox` "Quick Jump" (inside a `QScrollArea`, so a long
custom-city list scrolls instead of growing the window unbounded)
holds one row per motion the old submenu chain used to hold, in the
owner's own shape:
- **Turning-point rows** (`_turning_point_row`) — "← [icon TEXT] →":
  the heavy monochrome arrow pair (U+1F844/U+1F846, the SAME glyphs
  the old menu used) are the ONLY clickable part; the center is a
  passive icon+label. Sun (☀️, no dedicated icon file), Solar Eclipse
  (`eclipse_sun`, grayed without the Deep Time pack), Moon (🌙), Lunar
  Eclipse (`eclipse_moon`, grayed without the pack), Day/Month/Year
  (📅), Century/Millennium (🏛). `kind` is the JUMP STEM — the arrow
  click calls `_on_jump(f"prev_{kind}")`/`f"next_{kind}"`, matching
  `WatchController._UNIT_JUMPS`/`_ECLIPSE_JUMPS`/the sun-moon literals
  exactly (Rule #5, no separate naming scheme).
- **Place rows** (`_place_button`) — single-click, no arrows: North
  Pole and South Pole (icons `north_pole`/`south_pole`, text follows
  the SAME light/dark seasonal split the old menu's pole rows used —
  `defaults.pole_emoji`/`pole_is_light` — refreshed after every
  `_apply_moment` call since the DIALOG's own displayed date can
  change many times per visit), Greenwich (icon `compass`, the
  Prime Meridian reads as a compass reference point rather than a
  pole or a sun/moon event), then every entry of the `jump_cities`
  constructor argument (📍, no dedicated icon).
- `_on_jump(kind, city=None)`: calls the constructor's
  `jump_callback(moment(), cycles(), latitude(), longitude(), kind,
  city)` — a pure function owned by the controller
  (`WatchController._dialog_jump`/`_compute_jump`) that chains from
  THIS dialog's own current fields, never a live simulation; `None`
  (an edge clamp) is a no-op, otherwise `_apply_moment`/the lat-lon
  spinboxes update in place. OK still applies the final choice
  transactionally — a chain of jumps only ever edits the draft.
- `_apply_moment(moment, cycles)`: loads a landed jump into the
  moment-editor widgets (signals blocked so ONE row click repaints
  `_refresh()` exactly once, not once per widget touched) — the SAME
  fields `__init__` sets from `initial_moment`, kept as a SEPARATE
  method rather than folded into `__init__`'s own sequencing (lower
  regression risk than interleaving construction with reusable
  apply-logic in a correctness-critical astronomical dialog).
- `jump_callback=None` (the default) hides the WHOLE Quick Jump
  section — tests that only exercise the moment editor may omit it.

#### Methods
- `astro_year()`: the entered astronomical year (1 BCE = 0)
- `moment()` / `cycles()`: the naive PROXY wall time (the controller
  attaches the timezone) and its 400-year cycle count
- `latitude()` / `longitude()`
- `target_within_coverage()`: True when the entered year lies inside
  the supplied ACTIVE coverage (always True when none was given)
- `accept()`: refuses an out-of-range target inline (message per the
  pack state, stays open) instead of accepting
- `RETURN_TO_NOW`: the third dialog result code, produced by Now
