# Slot Layer — Flow

**About:** [description](../__about/slot.md)

## Algorithm

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[paint] --> B[FOR EACH index, seat IN slot_layout]
    B --> C{seat == classic?}
    C -- yes --> D[skip: WeekdayLayer's own seat]
    C -- no --> E{not lift AND (seat==center) != self._centered?}
    E -- yes --> F[skip: the OTHER instance draws it]
    E -- no --> G{gate element?}
    G -- no --> H[skip: hover z-lift will draw it]
    G -- yes --> I[position: hub if center, else dial_point at orbit*rotation]
    I --> J[size = base * slot_seat_scale * hover_factor]
    J --> K[_draw_slot]
    subgraph DISPATCH["_draw_slot: dispatch on mode"]
        M1{mode}
        M1 -- seconds --> M2[roundel + draw_small_seconds]
        M1 -- date --> M3[roundel + two-line: date, display_year]
        M1 -- time/day_length --> M4[roundel + fitted text]
        M1 -- weekday --> M5[_draw_weekday_slot]
        M1 -- zodiac/ascendant --> M6{style has art dir?}
        M6 -- yes --> M7[colored badge OR flat glyph on subdial]
        M6 -- no --> M8[roundel + text fallback]
        M1 -- chinese --> M9{style has art dir?}
        M9 -- yes --> M10[plate art, metal-swapped if applicable]
        M9 -- no --> M11[roundel + two-line: element, animal]
    end
    K --> DISPATCH
```

Pseudocode (language-neutral):

    FOR EACH (index, seat) IN slot_layout(skin):
        IF seat == "classic": CONTINUE           # WeekdayLayer's own seat
        IF NOT lift AND (seat == "center") != self.centered: CONTINUE
        element = f"slot:{index}"
        IF NOT gate(element): CONTINUE            # hover z-lift owns it now
        position = hub IF seat == "center" ELSE dial_point(seat + rotation, orbit)
        size = base_diamond_scale * slot_seat_scale * hover_factor(element)
        _draw_slot(index, position, size)

    FUNCTION _draw_slot(index, pos, size):
        mode, style, theme, metal, roster = slot_view(skin, index)
        SWITCH mode:
            "seconds": draw roundel; draw_small_seconds
            "date": draw roundel; two lines (date text, display_year)
            "time" / "day_length": draw roundel; fitted single line
            "weekday": _draw_weekday_slot(index, theme, metal, roster)
            "zodiac" / "ascendant":
                sign = ascendant_sign IF mode == ascendant ELSE zodiac_name
                IF style has an art directory:
                    colored → draw art directly; else → roundel + small glyph
                ELSE: roundel + text ("Ascendant"/sign, or just sign)
            default (chinese):
                animal = today's Chinese animal name
                IF style has an art directory: draw the plate (metal-swapped
                   if the style is a metal target)
                ELSE: roundel + two lines (element, animal)

    FUNCTION _draw_weekday_slot(index, theme, metal, roster):
        IF index == 1: draw today's body in the skin's own theme; RETURN
        seat = pantheon_seat(theme, today) IF roster == "pantheon" ELSE None
        asset = seat's plate IF seat found ELSE weekday_theme_body_art(...)
        asset = today's rotating _v2/alt sibling IF one exists ELSE asset
        IF asset file exists on disk:
            draw it (metal-swapped if applicable); optionally draw name label
        ELSE:
            roundel + fitted weekday-label text fallback
