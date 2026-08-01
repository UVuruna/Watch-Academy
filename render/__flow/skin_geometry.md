# Skin Geometry — Flow

**About:** [description](../__about/skin_geometry.md)

## The Sunday duality seat resolution

The trickiest chain in this module: which arm the Ruler and Servant
each stand on, given a wheel's own axis and a theme's own flip.

```mermaid
flowchart TB
    A[ruler_seat_angle / servant_seat_angle] --> B{center_duality?}
    B -- yes --> C[no seats to swap — both live\nin ONE center image]
    B -- no --> D{horizontal_duality?}
    D -- yes --> E{theme in\nDUALITY_RULER_ON_COLD_POLE?}
    D -- no --> F{theme in\nDUALITY_SERVANT_ON_TOP?}
    E -- yes --> G[flipped: Ruler <-> Servant\nswap their default seats]
    E -- no --> H[unflipped: default seats]
    F -- yes --> G
    F -- no --> H
```

Pseudocode:

    FUNCTION ruler_seat_angle(skin):
        IF _duality_flipped(skin): RETURN servant's DEFAULT seat
        ELSE:                      RETURN ruler's DEFAULT seat

    FUNCTION _duality_flipped(skin):
        IF center_duality(skin): RETURN False        # nothing to swap
        IF horizontal_duality(skin):
            RETURN skin.weekday_theme in DUALITY_RULER_ON_COLD_POLE
        RETURN skin.weekday_theme in DUALITY_SERVANT_ON_TOP

The two faces swap ARMS only — never their names, plates or articles.
`weekday_slots(skin)` then applies THREE transforms in order: the
wheel's own arm offset, a center-duality pull (removes "sun" from every
seat), and — if flipped — relocates the Sun alone onto the Servant's
default seat (his slot-mates keep their arm).
