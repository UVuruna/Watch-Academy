# Calendar Tooltips — Flow

**About:** [description](../__about/tooltip_calendar.md)

## Sections

```
📁 tooltip_calendar.py
  THE WEDGES   _calendar_tooltip, _zodiac_wedge_html, _months_wedge_html,
               _chinese_mount_wedge_html
  THE MOUNTS   _mount_seat_html, _calendar_mount_tooltip
  THE WEEKDAY  _weekday_tooltip
  THE TICK     _tick_tooltip
  THE SIGNS    _zodiac_text, _zodiac_line, _zodiac_image_trio,
               _chinese_text, _ascendant_text
  MONTH NAMES  _MONTHS, _MONTHS_SHORT
```

## One wedge hover

```mermaid
flowchart TB
    A["the Calendar pointer's wedge under the cursor"] --> B{which wheel is mounted?}
    B -- zodiac --> C["_zodiac_wedge_html → the sign, its dates, its art"]
    B -- almanac / Chinese --> D[_chinese_mount_wedge_html]
    B -- Slavic months --> E[_months_wedge_html]
    C --> F[_calendar_tooltip assembles]
    D --> G[_calendar_mount_tooltip assembles]
    E --> G
    G --> H["_mount_seat_html → one seat's row inside the mount"]
```

## The tick readout — where the families meet

```mermaid
flowchart TB
    A["a hover on the ring band or the centre"] --> B[_tick_tooltip]
    B --> C["the date line — _year / _month / _ord (composer helpers)"]
    B --> D["_lunation_ordinal (SkyTooltips)"]
    B --> E["_period_word (SkyTooltips)"]
    B --> F["_ring_jewel_legend_tooltip (RingTooltips)"]
    B --> G["_ring_word_legend_tooltip (RingTooltips)"]
    B --> H["_live_crown_tooltip (RingTooltips)"]
    B --> I["_greetings_tooltip (SkyTooltips)"]
```

`_tick_tooltip` is the single strongest argument for the mixin shape:
it reaches into two other families and the composer's own helpers on one
call, and as a mixin every one of those is a plain `self.` — the same
lines it had before the cut.
