# Long Envelope (Phase III — Laskar La2004)

**Script:** [Long Envelope (script)](../long_envelope.py) ·
**Flow:** [diagram](../__flow/long_envelope.md)

## Purpose

Phase III — the LONG ENVELOPE of the light/dark half-year amplitude. Reads
Laskar's La2004 orbital solution (eccentricity + longitude of perihelion,
1-kyr steps over −51 Myr…+21 Myr) and derives the northern LIGHT-minus-DARK
half-year duration over the full solution span, from Kepler's second law,
first order in eccentricity:

```
light - dark = (4T/pi) * e * sin(varpi)     [signed, days]
ENVELOPE     = (4T/pi) * e                   [|sin|=1 bound, days]
```

(`T` = 365.2422 d tropical year, `varpi` = heliocentric longitude of
perihelion). Then VALIDATES the signed curve against the DE441-measured
`season_halves.json` over their overlap — Pearson r 0.999991, mean deviation
0.96 h across ~30,000 years (see
[Ephemeris (subfolder)](../___ephemeris.md) for the full validation table
and headline findings: the coming eccentricity minimum ~+28,000 CE, the
recovery peak ~+86,000 CE, the major maximum ~+154,000 CE).

## Usage

```bash
# from the pipeline's own venv
python long_envelope.py validate   # deviation stats + near-future extrema
python long_envelope.py json       # long_envelope.json (columnar, full span)
python long_envelope.py plot       # long_envelope.png (two dark panels)
python long_envelope.py all        # validate -> json -> plot
```

## Connections

### Uses
- `research/ephemeris/laskar/INSOLN.LA2004.BTL.ASC` /
  `INSOLP.LA2004.BTL.ASC` (gitignored raw Laskar files; provenance in
  `laskar/la2004_extract.txt`)
- `season_halves.json` (from [Extract](extract.md)) — the DE441-measured
  series validated against

### Used by
- `research/ephemeris/test_ephemeris.py` — the overlap-agreement and
  `e(today)` golden checks read the committed `long_envelope.json`; a third
  check recomputes from the raw Laskar files and skips when they are absent

## Functions

- `_load_btl(path)`, `load_solution()` — parse and concatenate the past +
  future La2004 files into one t-ascending solution
- `derive(t, e, varpi)` — the signed light-minus-dark curve and its envelope
- `load_measured()`, `validate(verbose)` — interpolate the Laskar curve onto
  every DE441-measured year and report the deviation (max/mean/RMS hours,
  bias, Pearson r) plus spot checks
- `find_extrema()` — locates the coming eccentricity minimum, the first
  recovery peak, the major maximum within ±200 kyr, and the global envelope
  maximum over the whole fetched span
- `write_json()` — the columnar `long_envelope.json` (meta + full series)
- `build_plot()` — the two-panel dark chart (`long_envelope.png`)
