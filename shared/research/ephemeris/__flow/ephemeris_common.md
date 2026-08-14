# Ephemeris Common — Flow

**About:** [description](../__about/ephemeris_common.md)

## Algorithm — Marcher.next_crossing

```mermaid
flowchart TB
    A["fn(jd0) -> anchor the unwrapped angle,\npick the next 90-degree target"] --> B[next_crossing jd]
    B --> C["undershoot bracket: step forward by\nestimated-gap / rate until the sign flips"]
    C --> D["secant step between the bracket ends,\nbisection fallback if it leaves the bracket"]
    D --> E{within 1e-6 deg tolerance?}
    E -- no --> D
    E -- yes --> F["re-anchor the unwrapper on the accepted root;\nadvance the target by 90 deg"]
    F --> G[return jd_cross, target mod 360]
```

Pseudocode (language-neutral):

    STATE: ref_u = unwrap(fn(jd0)); next_target = the next 90-degree
           multiple strictly above ref_u

    FUNCTION next_crossing(jd):
        target = next_target
        a = jd; fa = unwrap(fn(a)) - target        # <= 0 by construction
        ESTIMATE a forward step from the known angular rate; extend (a, b)
        forward, UNTIL unwrap(fn(b)) - target >= 0  (undershoot bracket)
        LOOP secant between (a, fa) and (b, fb), falling back to bisection
        whenever the secant point would land outside [a, b]:
            UNTIL the residual is within 1e-6 degrees
        RE-ANCHOR the unwrapper at the accepted root (so the next call's
        unwrapping stays continuous)
        next_target += 90
        RETURN (accepted_jd, target mod 360)
