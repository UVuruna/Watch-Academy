# Sky Tooltips — Flow

**About:** [description](../__about/tooltip_sky.md)

## The four families, and who calls into this one

```mermaid
flowchart TB
    W["ClockWidget / 17 test files"] --> D["TooltipComposer.tooltip_at()\nencyclopedia_target() · warm_hover_articles()"]
    D --> X["_tooltip_at — the dispatch"]
    X -->|sun, moon, eclipse, Earth,\ntwilight, period| S["SkyTooltips (this module)"]
    X -->|arms, jewels, words, crown,\ncentre seat| R[RingTooltips]
    X -->|wedges, mounts, weekdays,\ntick, signs| C[CalendarTooltips]
    D --> E[EncyclopediaTargets]
    R -.->|_wet_dry_block · _span_line\n_season_name_for · _anchor_instant| S
    C -.->|_greetings_tooltip| S
    E -.->|_season_topic_index| S
```

The dotted arrows are why this is a MIXIN and not a collaborator: they
are `self.` calls that cost nothing here and would each need a
hand-built back-channel if every family held its own dial.

## Building one sky hover

```mermaid
flowchart TB
    A["_tooltip_at names the element"] --> B{which sky element?}
    B -- sun face --> C["_sun_face_tooltip → the centre seat's own reading"]
    B -- moon marker --> D["_moon_text → phase + illumination"]
    D --> E["_lunation_ordinal → 'day N of the cycle'"]
    B -- eclipse --> F[_eclipse_text]
    F --> G["_eclipse_type_icon_tag → the inline badge"]
    F --> H["_eclipse_visibility_text → can the observer SEE it"]
    F --> I["_eclipse_article + _eclipse_emblem → the chapter"]
    B -- Earth marker --> J[_earth_text]
    J --> K["_season_row → the turning point that glows"]
    K --> L["_wet_dry_span_at → tropics read WET/DRY, not four seasons"]
    B -- twilight band --> M[_twilight_tooltip]
    B -- period window --> N[_period_tooltip]
    N --> O["_period_earth_html + _greetings_tooltip"]
```

Pseudocode:

    _earth_text():
        head  <- day/week ordinals + the date, through _ord/_month/_year
        row   <- _season_row()            # the event, while it glows
        key   <- _current_season_key()    # which season we are IN
        RETURN _label(head) + row

Every one of those helpers reads `self._dial.day` and
`self._dial.tick` live — the composer's single reference — so a new day
context can never leave a stale sentence behind.
