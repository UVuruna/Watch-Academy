# Time Travel

**Script:** [Time Travel (script)](time_travel.py)

## Purpose
The owner's scenario tester, opened from the menu: enter any moment and
any latitude/longitude — the dial renders that exact situation (sun arc,
hexagram tilt, Earth and Moon positions, moon phase, hovers) for
`TIME_TRAVEL_DURATION_S`, then returns to the present by itself. The
entered wall time is interpreted in the active timezone. Since Session
16 (owner slika 13, 2026-07-17) the moment editor accepts ANY year of
the active coverage INCLUDING BCE.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — coordinate ranges,
  duration, the warning color, the advertised Deep Time span, era
  constants
- [Deep Time](../core/deep_time.md) — era mapping, the proxy frame,
  month lengths, the year-line formatters
- [UI Style](ui_style.md) — the shared vivid button pills

### Used by
- [App Controller](controller.md) — `_open_time_travel()` passes the
  ACTIVE coverage (bundled ∩, widened by the pack), the bundled core
  coverage (the tier line), the year-line settings and the pack flag;
  feeds the frozen (proxy moment, cycles, observer) into the tick flow

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
