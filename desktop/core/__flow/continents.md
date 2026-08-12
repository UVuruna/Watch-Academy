# Continents — Flow

**About:** [description](../__about/continents.md)

## Algorithm

```mermaid
flowchart TB
    A[has_eclipse] --> D{OR}
    B[is_turning_point] --> D
    C[is_principal_phase] --> D
    D -- true --> E[Ninth seat shows PANGEA]
    D -- false --> F[Ninth seat shows ZEALANDIA]
```

Two thin wrappers feed the same law from different data shapes:

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    subgraph DIAL["Dial form"]
        A1[DayContext.season_events] --> A3[date_has_turning_point]
        A2[DayContext.moon_events] --> A4[date_has_principal_phase]
        A5[TickState.eclipse_event] --> A6[has_eclipse]
    end
    subgraph ENC["Encyclopedia form"]
        B1[SeasonsRepository] --> B3[turning_point_on]
        B2[MoonPhaseRepository] --> B4[principal_phase_on]
        B5["has_eclipse = False (no live pack)"]
    end
    A3 & A4 & A6 --> L[pangea_over_zealandia]
    B3 & B4 & B5 --> L
```

Pseudocode (language-neutral):

    FUNCTION pangea_over_zealandia(has_eclipse, is_turning_point, is_principal_phase):
        RETURN has_eclipse OR is_turning_point OR is_principal_phase

    FUNCTION ninth_is_pangea_from_events(on_date, season_events, moon_events, has_eclipse):
        turning = ANY(instant.date == on_date FOR instant, _ IN season_events)
        principal = ANY(instant.date == on_date AND name IN PRINCIPAL_NAMES
                         FOR instant, name IN moon_events)
        RETURN pangea_over_zealandia(has_eclipse, turning, principal)

    FUNCTION ninth_is_pangea_from_repos(on_date, seasons_repo, moon_repo, has_eclipse=False):
        TRY: anchors = seasons_repo.year_anchors(on_date.year)
             turning = ANY(instant.date == on_date FOR instant IN anchors.instants)
        EXCEPT (not covered): turning = False
        TRY: window = moon_repo.moon_window(on_date.year)
             principal = ANY(instant.date == on_date AND fraction IN {0, 0.25, 0.5, 0.75}
                              FOR instant, fraction IN window.events)
        EXCEPT (not covered): principal = False
        RETURN pangea_over_zealandia(has_eclipse, turning, principal)
