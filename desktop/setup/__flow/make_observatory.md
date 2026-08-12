# Observatory Series Generator — Flow

**About:** [description](../__about/make_observatory.md)

## Algorithm — three independent decimation passes

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[events.sqlite AND long_envelope.json exist?] -- no --> Z[[SystemExit: run the research pipeline first]]
    A -- yes --> B[Open events.sqlite read-only]

    subgraph SEASONS["_write_seasons"]
        S1[Walk sun_events ordered by jd_tt] --> S2["duration = gap between<br/>consecutive crossings,<br/>keyed by season-start year"]
        S2 --> S3[Keep only years with<br/>all 4 seasons present]
        S3 --> S4["Bin-mean into 20-year windows<br/>(skip sparse edge bins)"]
        S4 --> S5{"light/dark sums match<br/>season_halves.json<br/>at 3 spot-check years?"}
        S5 -- no --> S6[[ValueError: geometry drifted]]
        S5 -- yes --> S7[Write observatory_seasons.json<br/>+ eras block]
    end

    subgraph ECLIPSES["_write_eclipses"]
        E1[Walk solar_eclipses + lunar_eclipses] --> E2["Bucket by year // 500,<br/>count per type per bucket"]
        E2 --> E3[Write observatory_eclipses.json<br/>+ eclipses_summary.json meta]
    end

    subgraph ENVELOPE["_write_envelope"]
        V1[Read long_envelope.json] --> V2["Slice t_kyr to<br/>+/-200,000 years"]
        V2 --> V3["t_kyr -> calendar year<br/>(year = 2000 + 1000*t)"]
        V3 --> V4[Write observatory_envelope.json]
    end

    B --> SEASONS
    B --> ECLIPSES
    SEASONS --> ENVELOPE
    ECLIPSES --> ENVELOPE
    ENVELOPE --> DONE[[print done]]
```

Pseudocode (language-neutral):

    IF events.sqlite missing OR long_envelope.json missing:
        exit with instructions

    open events.sqlite read-only

    # --- seasons -----------------------------------------------------
    by_year = {}
    prev = None
    FOR EACH (jd_tt, iso_ut, crossing_type) IN sun_events ORDER BY jd_tt:
        IF prev is not None:
            season = SEASON_OF[prev.crossing_type]   # crossing -> season name
            by_year[year(prev.iso_ut)][season] = jd_tt - prev.jd_tt
        prev = (jd_tt, iso_ut, crossing_type)
    durations = { y: seasons FOR y, seasons IN by_year
                  IF all 4 seasons present }

    binned = bin-mean(durations, bin_size=20 years,
                       skip bins with < 10 of their 20 years measured)

    FOR spot_check_year IN (2026, 0, 1000):
        light = durations[year].spring + durations[year].summer
        dark  = durations[year].autumn + durations[year].winter
        IF |light - reference_light| > 1e-3 OR
           |dark  - reference_dark|  > 1e-3:
            RAISE ValueError (geometry drifted from season_halves.json)

    write observatory_seasons.json (binned series + eras block)

    # --- eclipses ------------------------------------------------------
    buckets = {}
    FOR EACH eclipse IN solar_eclipses + lunar_eclipses:
        key = year(eclipse.iso_ut) // 500
        buckets[key][eclipse.kind] += 1
    write observatory_eclipses.json (bucketed counts + summary meta)

    # --- envelope --------------------------------------------------------
    FOR EACH (t_kyr, signed, envelope) IN long_envelope.json:
        IF -200 <= t_kyr <= 200:
            year = 2000 + 1000 * t_kyr
            keep (year, signed, envelope)
    write observatory_envelope.json (sliced series)

    print "done"
