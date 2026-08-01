# Year Wheel — Flow

**About:** [description](../__about/year_wheel.md)

## Algorithm — `_unwrapped_angle` (forward interpolation)

```mermaid
flowchart TB
    A[now, anchors] --> B{now outside\ninstants[0]..instants[-1]?}
    B -- yes --> C[raise ValueError]
    B -- no --> D[binary-search the bracketing pair t0, t1]
    D --> E{now == last anchor exactly?}
    E -- yes --> F[return angles[-1]]
    E -- no --> G[fraction = (now - t0) / (t1 - t0)]
    G --> H[return a0 + fraction * (a1 - a0)]
```

## Algorithm — `zodiac_sign`

```mermaid
flowchart TB
    A[now, anchors] --> B[unwrapped = _unwrapped_angle]
    B --> C[start_angle = floor(unwrapped / 30) * 30]
    C --> D[name, symbol = ZODIAC_SIGNS at that 30-deg slot]
    D --> E[start = _instant_at(start_angle)]
    D --> F[end = _instant_at(start_angle + 30)]
```

Pseudocode (language-neutral):

    FUNCTION year_marker_angle(now, anchors):
        RETURN _unwrapped_angle(now, anchors) MOD 360

    FUNCTION _unwrapped_angle(now, anchors):
        ASSERT anchors.instants[0] <= now <= anchors.instants[-1]
        (t0, a0), (t1, a1) = the bracketing pair of (instant, angle) around `now`
        IF now == anchors.instants[-1]: RETURN anchors.angles[-1]
        fraction = (now - t0) / (t1 - t0)
        RETURN a0 + fraction * (a1 - a0)

    FUNCTION _instant_at(anchors, unwrapped_angle):
        (t0, a0), (t1, a1) = the bracketing pair of (angle, instant) around `unwrapped_angle`
        # last segment extrapolates for the edge-only cusp past the final anchor
        fraction = (unwrapped_angle - a0) / (a1 - a0)
        RETURN t0 + fraction * (t1 - t0)

    FUNCTION zodiac_sign(now, anchors):
        unwrapped = _unwrapped_angle(now, anchors)
        start_angle = floor(unwrapped / 30) * 30
        name, symbol = ZODIAC_SIGNS[ (start_angle MOD 360) / 30 ]
        RETURN name, symbol, _instant_at(anchors, start_angle), _instant_at(anchors, start_angle + 30)
