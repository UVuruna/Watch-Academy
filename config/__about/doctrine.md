# Doctrine

**Script:** [Doctrine (script)](../doctrine.py) · **Flow:** [diagram](../__flow/doctrine.md)

## Purpose

The canon tables that are neither coordinates nor wheels.

[Character Cube](cube.md) holds the Character Cube as COORDINATES;
[Archetypes](archetypes.md) holds the dial's WHEELS. Two canon figures
fit neither and lived only in prose until the Session 27 diagram wave
needed them as data — because a drawing computed from the canon (root
Rule #19) must never parse an article to find its own content.

Every line is transcribed from the sealed text: `CUBE.md` §The Path of
Light, §The Path of Darkness and §The chiasm, plus the encyclopedia's
own *FALL and STAR*, *DOMY and SAFE* and *The Twenty-Four Fields*
articles.

Layer: config — pure, no Qt, no wall clock.

## Contents

- `Station` — one stop on a four-station journey: the dial hour it
  stands on, the station's own name, and the letter its cipher takes
  from it.
- `PATH_OF_LIGHT` / `PATH_OF_DARKNESS` — the two crosses, four stations
  each, in WALKING order on the hexagram's own arms.
- `FALL` / `STAR` — the English mnemonics (Loathing for Hate, Lament
  for Suffering, Spark for Hope — the same content in the letters the
  descent/ascent require).
- `DOMY` / `SAFE` — the assembled ciphers, built by ASSEMBLY rather
  than walking order (the application's own name is the dark cross;
  the word for its purpose is the bright cross read back down).
- `CROSS_PAGES` — (page name) → (bright reading, dark reading), naming
  which pair each Encyclopedia page draws.
- `Field` — one of the Twenty-Four Fields: an office (what the person
  DOES) paired with a process (what HAPPENS to the object).
- `UNION_FIELDS` — three persons (God, The Devil, Jesus), four offices
  each, every office paired with its process.
- `RING_LETTER_SEATS` — the four ring letters (Δ, M, Y, Ω) and the hour
  each stands on, per the Greek-alphabet-place arithmetic (Δ 4th at
  04h, M 12th at 12h, Y 20th at 20h, Ω 24th/last at 24h).

## Connections

### Used by
- [Canon Diagrams](../../render/__about/canon_diagrams.md) — draws all of it

## Design Decisions

- **A `Station` carries its hour, its name and its cipher letter.** One
  shape serves all six readings (the two crosses and their two
  alternate namings), so the drawer has no special cases.
- **The arm ANGLES are not computed here.** `core.angles.
  ring_position_angle` is the mapping every fixed ring hour already
  shares (Rule #5) — this module only says which hour a station stands
  on.
- **`RING_LETTER_SEATS` lives here because the article states it and
  the computed ring-letter diagram draws it** — one source, so the
  figure can never disagree with the prose it stands beside.
