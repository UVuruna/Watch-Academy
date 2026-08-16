# body_disc.py — the plate's own disc, measured

[← Render](../___render.md)

**Purpose.** Answer one question about a body plate: how much of its
frame does the BODY actually fill? Everything outside that — a corona,
a glory, a set of rays — is shine, and shine is not a size.

## Why it exists

THE DISC IS THE MEASURE, THE SHINE IS EXTRA (owner order 2026-08-16).
Every weekday plate is stamped to `slot_layout.weekday_body_size`, which
sizes the WHOLE PICTURE. An ordinary body fills its frame (Moon 0.99,
Sun 0.96) so the two are the same thing — but the eclipsed Sun is a
small black disc inside a wide corona (0.70 in the `_gpt` photo plate),
so it drew a body two thirds the size of the Moon beside it. His ruling:
the disc takes the roundel's dimensions and the shine goes over the top,
free to reach across the neighbouring sectors and the hands.

## What it measures

`filled_disc_fraction(asset)` — the largest radius, as a fraction of the
plate's half-size, at which a ring of samples is still (almost) entirely
opaque. A solid disc passes; the first radius where the ring breaks into
sparse rays ends it. That is exactly the boundary between body and
shine, and it needs no per-file constant to be maintained by hand.

Measured once per resolved path and cached for the process lifetime (THE
ONE COPY RULE's own pattern — a plate's geometry cannot change while the
program runs). A plate that will not decode answers
`BODY_DISC_REFERENCE_FILL`, which makes the correction a no-op rather
than a guess.

## What it corrects

`disc_match_scale(asset)` is `BODY_DISC_REFERENCE_FILL / measured`,
clamped to `[1.0, BODY_DISC_MATCH_MAX]` and returned as a flat `1.0` for
every plate whose stem is not listed in `dial.BODY_DISC_MATCH_PREFIXES`.

The list is the point. Matching EVERY body would resize the whole
instrument to fix one plate, and the planet SIGNS — a thin glyph in a
wide frame, 0.26 — would blow up fourfold. One entry today,
`Sun_Eclipse`, prefix-matched so the whole family (photo, art, gem, gpt)
is covered at once.

## Connections

- **Reads:** `config.dial` (the three constants), `config.paths.art_file`
  (the `.png` → `.webp` door — never a second one).
- **Read by:** `render.weekday_body.draw_weekday_body` and
  `render.layers.center_body` — the two places a weekday plate is
  stamped. Both multiply the roundel size by `disc_match_scale`, so the
  DISC lands at the roundel's diameter and the corona overhangs it.
- **Tooth:** `tests/test_body_disc.py`.
