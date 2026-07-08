# Symbolism Repository

**Script:** [Symbolism Repository (script)](symbolism.py)

## Purpose
Read-only access to `Database/symbolism.json` — the machine-readable
companion of [DOMY Symbolism](../SYMBOLISM.md). The hexa diamond hover
appends the active weekday theme's encyclopedic blurb (two-three
sentences weaving the god/religion/profession with its virtue, vice,
color and mood) below the two zodiac sign lines.

## Connections

### Uses
- [Data (folder)](___data.md) shared JSON loader
- `Database/symbolism.json` ([Database (folder)](../Database/___database.md))

### Used by
- [Compositor](../render/compositor.md) — the hexa arm hover text

## Classes

### SymbolismRepository
- `arm_blurbs(body) -> dict[str, str]`: the blurb texts of one weekday
  body ("day", "greek", "norse", "religion", "color", "virtue_vice",
  "profession"); the center (sun) and the six arms are all addressable
  by body name. Raises KeyError for an unknown body — loudly, per
  Rule #1.

The JSON also carries the `articles` set (35 encyclopedic texts, one
per entity per theme) — not yet surfaced in the app; the owner decides
where they display.
