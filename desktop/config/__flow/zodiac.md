# Zodiac — Flow

**About:** [description](../__about/zodiac.md)

## Sections

```
📁 zodiac.py
  CHINESE   CHINESE_ANIMALS (12), CHINESE_ELEMENTS (5),
            CHINESE_NEW_YEAR_WINDOW, CHINA_UTC_OFFSET_HOURS,
            CHINESE_MONTH_BRANCH_ANIMALS, CHINESE_BRANCH_TERMS,
            chinese_branch_span()
  WESTERN   ZODIAC_SIGNS (12), ZODIAC_SPAN_DEG
  THE 13th  THIRTEENTHS, AXLE_ALWAYS_CENTERS,
            OPHIUCHUS_WINDOW, SOL_WINDOW, MODRENIK_WINDOW_HALF_DAYS
```

## The sexagenary year

```mermaid
flowchart TB
    A["a Gregorian date"] --> B{"before this year's new moon\nin CHINESE_NEW_YEAR_WINDOW (China time)?"}
    B -- yes --> C["the PREVIOUS Chinese year"]
    B -- no --> D["this Chinese year, N"]
    C --> E["animal = CHINESE_ANIMALS[(N - 4) mod 12]"]
    D --> E
    E --> F["element = CHINESE_ELEMENTS[((N - 4) mod 10) // 2]"]
    F --> G["e.g. 2026 → Fire Horse"]
```

The new-year instant is DERIVED from the bundled principal-phase
instants, shifted by `CHINA_UTC_OFFSET_HOURS` — never a hardcoded date,
so a Deep Time pack widens it for free.

## A thirteen-seat mount

```mermaid
flowchart TB
    A["a calendar mount with 13 seats"] --> B["12 wedges + the AXLE"]
    B --> C{"AXLE_ALWAYS_CENTERS?"}
    C -- yes --> D["THIRTEENTHS[system] takes the axle\n(Ophiuchus for astrology, Sol for the solar mount)"]
    C -- no --> E["the axle stays empty"]
    D --> F["it reads as current only inside its own window\n(OPHIUCHUS_WINDOW / SOL_WINDOW)"]
```

Pseudocode:

    branch_of(date):
        FOR animal, (start_term, end_term) IN CHINESE_BRANCH_TERMS:
            IF date IN chinese_branch_span(start_term, end_term, date.year):
                RETURN animal

`chinese_branch_span()` is the module's only function: the branch months
are bounded by SOLAR TERMS, not by calendar days, so the span has to be
computed per year rather than written down.
