# Doctrine

**Script:** [Doctrine (script)](doctrine.py)

## Purpose

The canon tables that are neither coordinates nor wheels.

[Cube](cube.md) holds the Character Cube as COORDINATES;
[Archetypes](archetypes.md) holds the dial's WHEELS. Two canon figures
fit neither and lived only in prose until the Session 27 diagram wave
needed them as data — because a drawing computed from the canon (root
Rule #19) must never parse an article to find its own content.

Every line is transcribed from the sealed text: CUBE.md §The Path of
Light, §The Path of Darkness and §The chiasm, plus the encyclopedia's
own *FALL and STAR*, *DOMY and SAFE* and *The Twenty-Four Fields*.

## Connections

### Used by
- [Canon Diagrams](../render/canon_diagrams.md) — draws all of it

## What is here

### The two crosses
Four stations each, in WALKING order, on the hexagram's own arms:

```
PATH_OF_LIGHT     08h Hope -> 12h Faith -> 16h Love -> 24h Salvation
PATH_OF_DARKNESS  20h Fear -> 24h Anger -> 04h Hate  -> 12h Suffering
```

The order is the argument: each road ends in the other's hour.

### The three readings of those roads
- `FALL` / `STAR` — the English mnemonics (Loathing for Hate, Lament for
  Suffering, Spark for Hope: the same content in the letters the descent
  and the ascent require)
- `DOMY` / `SAFE` — the assembled ciphers, Latin and Greek mixed, built
  by ASSEMBLY rather than walking order

`CROSS_PAGES` names which pair each Encyclopedia page draws.

### The twenty-four fields
Three persons, four offices each, every office paired with the process
it works on its object — so each field reads as an act and its effect.

## Design Decisions

- **A `Station` carries its hour, its name and its cipher letter.** One
  shape serves all six readings, so the drawer has no special cases.
- **The arm ANGLES are not computed here.** `core.angles.
  ring_position_angle` is the mapping every fixed ring hour already
  shares (Rule #5) — this module only says which hour a station stands
  on.
