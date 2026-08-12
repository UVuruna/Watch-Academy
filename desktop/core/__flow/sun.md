# Sun — Flow

**About:** [description](../__about/sun.md)

## Algorithm — `compute_sun_day`

```mermaid
flowchart TB
    A[observer, local_date, tz] --> B["try dawn (CIVIL_DEPRESSION)"]
    A --> C[try sunrise]
    A --> D[noon: never raises]
    D --> E{noon.date != local_date?\nUTC+13/14 edge case}
    E -- yes --> F[re-query noon for the\nneighboring UTC day]
    E -- no --> G[unchanged]
    A --> H[try sunset]
    A --> I["try dusk (CIVIL_DEPRESSION)"]
    B & C & F & G & H & I --> J[_classify -> DaylightRegime]
    J --> K[assemble SunDay, frozen]
```

## Algorithm — `_classify` (the regime decision tree)

```mermaid
flowchart TB
    A[dawn, sunrise, sunset, dusk, noon] --> B{sunrise or sunset exists?}
    B -- yes --> C{dawn or dusk exists?}
    C -- yes --> D[NORMAL]
    C -- no --> E[WHITE_NIGHTS]
    B -- no --> F{dawn or dusk exists?}
    F -- yes --> G[TWILIGHT_ONLY]
    F -- no --> H[noon elevation, geometric]
    H --> I{elevation > HORIZON_ELEVATION_DEG?}
    I -- yes --> J[POLAR_DAY]
    I -- no --> K{elevation > CIVIL_TWILIGHT_ELEVATION_DEG?}
    K -- yes --> L[TWILIGHT_ONLY]
    K -- no --> M[POLAR_NIGHT]
```

Pseudocode (language-neutral):

    FUNCTION compute_sun_day(observer, local_date, tz):
        dawn    = try astral.sun.dawn(depression=CIVIL_DEPRESSION), None on ValueError
        sunrise = try astral.sun.sunrise, None on ValueError
        noon    = astral.sun.noon(observer, local_date, tz)          # never raises
        IF noon.date != local_date:
            noon = astral.sun.noon(observer, local_date shifted by ±1 day, tz)
        sunset  = try astral.sun.sunset, None on ValueError
        dusk    = try astral.sun.dusk(depression=CIVIL_DEPRESSION), None on ValueError
        RETURN SunDay(dawn, sunrise, noon, sunset, dusk,
                       regime=_classify(observer, noon, dawn, sunrise, sunset, dusk))

    FUNCTION _classify(observer, noon, dawn, sunrise, sunset, dusk):
        IF sunrise is not None OR sunset is not None:
            RETURN NORMAL IF (dawn is not None OR dusk is not None) ELSE WHITE_NIGHTS
        IF dawn is not None OR dusk is not None:
            RETURN TWILIGHT_ONLY
        elevation = astral.sun.elevation(observer, noon, with_refraction=False)
        IF elevation > HORIZON_ELEVATION_DEG:        RETURN POLAR_DAY
        IF elevation > CIVIL_TWILIGHT_ELEVATION_DEG:  RETURN TWILIGHT_ONLY
        RETURN POLAR_NIGHT
