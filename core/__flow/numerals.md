# core/numerals.py — flow

## The band solve

```mermaid
flowchart TD
    Z["hour h (0..23)"] --> Y{"does the preset seat a LETTER here?"}
    Y -->|yes| X["draw NOTHING - one seat, one content"]
    Y -->|no| A["hour h + offset_deg"]
    A --> B["deg = fold((h-12)*15 + offset)"]
    B --> C{seating}
    C -->|upright| D["rot = 0"]
    C -->|arc| E{"deg mod 90 == 0 ?"}
    E -->|yes| D
    E -->|no| F{"abs(deg) > 90 ?"}
    F -->|yes| G["rot = deg + 180 (lower half)"]
    F -->|no| H["rot = deg (upper half)"]
    B --> I{light}
    I -->|radial| J["(dx, dy) = depth * (sin deg, cos deg)"]
    I -->|fixed| K["(dx, dy) = typed offset"]
    J --> L{relief style}
    K --> L
    L -->|cast| M["1 copy at (dx, dy)"]
    L -->|extrude| N["N = round(depth) copies at k/N"]
    L -->|emboss| O["dark at (dx,dy) + lit at -0.6*(dx,dy)"]
    B --> P{"int(label) % 2"}
    P -->|0| Q["role = even — white body, ring border"]
    P -->|1| R["role = odd — ring body, white border"]
```

## Pseudocode

```
fold(deg):                       # into (-180, 180]
    d = ((deg + 180) mod 360) - 180
    return 180 if d == -180 else d

hour_angle(h, offset):           return fold((h - 12) * 15 + offset)
minute_angle(m):                 return m * 6            # never rotates

seat_rotation(deg, seating):
    if seating == "upright":     return 0
    if deg mod 90 == 0:          return 0                # the square angles
    if abs(deg) > 90:            return deg + 180        # the lower half
    return deg                                           # the upper half

numeral_hours(letter_hours):     # THE COMPOSITION LAW
    seated = {h mod 24 for h in letter_hours}   # cards say 24, hours say 0
    return [h for h in 0..23 if h not in seated]

inner_number_seats(variant):     # the same law on the inner band
    return [(str(m), minute_angle(m))
            for m in RING_INNER_COMPOSITION[variant].numbers]

light_offset(deg, depth, light, fixed):
    if light == "fixed":         return fixed            # y positive UP
    return (depth * sin(deg), depth * cos(deg))

relief_offsets(style, depth, (dx, dy)):
    if style == "cast":          return [(dx, dy, SHADE)]
    if style == "extrude":
        n = max(1, round(depth))
        return [(dx*k/n, dy*k/n, SHADE) for k in 1..n]
    return [(dx, dy, SHADE), (-0.6*dx, -0.6*dy, LIT)]    # emboss

crown_sequence(hour, minute, fmt):
    hh = "%02d" % hour ; mm = "%02d" % minute
    if fmt == "hh:mm":           return hh + ":" + mm
    return str(hour) + "h" + " " + str(minute) + "min"   # small-cut h/min

arc_degrees(length, radius):     return 360 * length / (2*pi*radius)

crown_advance_angles(advances, orientation):     # THE CROWN ADVANCE LAW
    sign   = +1 if orientation == "top" else -1  # bottom reads the other way
    anchor =  0 if orientation == "top" else 180
    cursor = -sum(advances) / 2                  # the whole run, centred
    for a in advances:                           # each glyph in ITS OWN slot
        yield anchor + sign * (cursor + a / 2)
        cursor += a
```

## The crown advance (owner defect 2026-08-07)

```mermaid
flowchart LR
    A["glyph tile"] --> B["ink width px<br/>(the PATH, not the tile —<br/>the tile carries shadow padding)"]
    B --> C["+ tracking<br/>= box * CROWN_TRACKING_FRACTION"]
    C --> D["arc_degrees(width, crown radius)"]
    D --> E["crown_advance_angles(...)"]
    E --> F["each glyph centred in its own slot"]
    G["OLD: one fixed step for every glyph"] -.->|"a 0.22-wide colon got<br/>the arc of a 1.45-wide M"| H["'2 3 : 3 9' — scattered"]
```

## The inner band's tick vocabulary

```
LONG     the twelve five-minute strokes      (every 30 deg)
SHORT    the stroke beside a printed number  (paired with LONG)
POINTER  the four quarter arrows             (0/90/180/270)
SECOND   the sixty second marks              (every 6 deg)
DAY      the 360 day ticks                   (every 1 deg)
```

`inner_tick_plan()` walks 0..359 once and yields `(angle_deg, kind)` in a
fixed precedence — DAY under everything, then SECOND, then LONG/SHORT, then
POINTER — so a render pass never asks "which kind wins here".
