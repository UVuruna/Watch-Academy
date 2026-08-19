# Encyclopedia Targets — Flow

**About:** [description](../__about/encyclopedia_targets.md)

## Sections

```
📁 encyclopedia_targets.py
  THE DOOR'S BODY  encyclopedia_target
                    ├─ _element_encyclopedia_target ─┬─ _weekday_encyclopedia_target
                    │                                ├─ _eclipse_encyclopedia_target
                    │                                └─ _season_topic_index
                    ├─ _arm_encyclopedia_target ────── _sun_topic_index
                    └─ _calendar_wedge_target
  ORDER TABLES     _ENC_ZODIAC_ORDER, _ENC_WEEK_ORDER, _ENC_SEASON_ORDER,
                   _ENC_SUN_ORDER, _ENC_TRIO_ORDER,
                   _ENC_ECLIPSE_SOLAR_ORDER, _ENC_ECLIPSE_LUNAR_ORDER
  THE THIRTEENTHS  _ENC_OPHIUCHUS_INDEX, _ENC_CAT_INDEX, _ENC_SOL_INDEX,
                   _ENC_MODRENIK_INDEX → _ENC_THIRTEENTH_TARGET
```

## Element → (topic, index)

```mermaid
flowchart TB
    A["encyclopedia_target(x, y, size)"] --> B["the dial names the element\n(geometry only — the LEGEND may be OFF)"]
    B --> C{which kind?}
    C -- an arm --> D[_arm_encyclopedia_target]
    D --> E{"southern hemisphere?"}
    E -- yes --> F["anchor = _SOUTH_ANCHOR_FLIP[anchor]\n(borrowed from RingTooltips)"]
    E -- no --> G[anchor unchanged]
    F --> H["index into _ENC_SEASON_ORDER / _ENC_SUN_ORDER / _ENC_TRIO_ORDER"]
    G --> H
    C -- a calendar wedge --> I["_calendar_wedge_target → _ENC_ZODIAC_ORDER\nor the Chinese gallery order"]
    C -- anything else --> J[_element_encyclopedia_target]
    J --> K{weekday body?}
    K -- yes --> L["_weekday_encyclopedia_target → _ENC_WEEK_ORDER"]
    K -- no --> M{eclipse?}
    M -- yes --> N["_eclipse_encyclopedia_target →\n_ENC_ECLIPSE_SOLAR_ORDER / _LUNAR_ORDER"]
    M -- no --> O{a thirteenth?}
    O -- yes --> P["_ENC_THIRTEENTH_TARGET — Ophiuchus and The Cat close\ntheir galleries, Sol and Modrenik close 'months'"]
    O -- no --> Q["the season / sign / trio orders"]
    H --> R["(topic, index)"]
    I --> R
    L --> R
    N --> R
    P --> R
    Q --> R
```

Pseudocode:

    encyclopedia_target(x, y, size):
        element <- self._dial.element_at(x, y, size)     # geometry, not text
        FOR resolver IN (_arm_encyclopedia_target,
                         _calendar_wedge_target,
                         _element_encyclopedia_target):
            hit <- resolver(element)
            IF hit is not None: RETURN hit
        RETURN None

**It answers with the legend OFF.** That is the behavioural line between
this family and the other three: turn hovers off and every tooltip goes
silent, while the Spacebar jump still opens the right page — because
nothing here builds text.
