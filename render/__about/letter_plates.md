# render/letter_plates.py

Turns a GLYPH into the drawable GOLD MASTER behind it — the one door
between a character and the owner's plate library at
`assets/instrument/letters/`.

## Purpose

**THE ONE PLATE LAW** (owner decree 2026-08-07): every GLYPH the dial
draws — wherever it stands — is a plate from this library, taken as the
GOLD master and recolored by the transformer into one of the app's metals
or thematic colours. One style, one source, one algorithm: never a font,
never a flat colour of its own.

Before this module the law held everywhere except one place. The live
crown's TIME drew its digits with `QFont` and filled them with a flat body
colour sampled off the metal ramp, because the library had no `0`–`9`
plates. The owner shipped the ten digits (and `symbols/colon.png` before
them, explicitly for this), and the font path was deleted.

## Why the failure was silent (the root cause worth keeping)

`numeral_fonts.assert_covers` proved that the picked FONT could draw the
glyph. Nothing ever proved that the PLATE existed. A missing plate was
therefore not an error at all — it was the trigger for a documented
fallback, so the renderer had nothing to report and reported nothing. The
tooth that replaces it is `plate_path`, which **raises** on an unresolvable
glyph, plus `tests/test_letter_plates.py`, which walks every glyph of
`constants.LETTER_PLATE_FILES` and every glyph the crown can compose and
asserts the file is on disk.

## What it resolves

| Input | Resolves to |
|-------|-------------|
| `A`–`Z` | `latin/<letter>.png` |
| `a`–`z` (the crown's `h`/`min` cut) | the SAME uppercase plate, drawn small |
| Γ Δ Θ Λ Ξ Π Σ Φ Ψ Ω | `greek/<Name>.png` |
| the other 14 Greek capitals | the LATIN twin's plate (`constants.GREEK_LATIN_TWINS`) |
| `0`–`9` | `numerals/<digit>.png` |
| `12` `15` `16` `18` `20` `21` | **composed** from two digit plates |
| `✠ $ & : @ ! ?` | `symbols/…` |
| the Eye variants | `emblems/…` |

### The Greek twins

Fourteen Greek capitals are drawn exactly like a Latin letter (Α=A, Β=B,
Ε=E, Ζ=Z, Η=H, Ι=I, Κ=K, Μ=M, Ν=N, Ο=O, Ρ=P, Τ=T, Υ=Y, Χ=X). They get an
ALIAS in `config.constants`, never a duplicate file — THE ONE COPY RULE:
one plate on disk cannot fall out of sync with itself, and a copy can.

### The composed numbers

The library holds single digits only (owner 2026-08-07: *"izbacio sam sve
one kompleksne brojeve koje kombinuju 1 ili više osnovnih"*). The six
two-digit hour seats — 12, 15, 16, 18, 20, 21 — are composed on first use
and cached as a gold master in the raster cache, so everything downstream
(the metal derivation, the ring's own `pixmap_by_height`) sees a single
ordinary plate file and needs no knowledge of the split.

Every digit master is 512 px tall and tightly cropped, so the digits share
a cap height and the composition is pure horizontal placement.

**The spacing is an INK gap, and it cost a grade to learn.** The first
version spaced the plate BOXES by the 8 px of fully-transparent columns
visible in the owner's retired `20.png`. That is a different quantity: it
is what two digits that never reach toward each other happen to leave. Two
that DO reach — a `1`'s flag serif and a `5`'s top bar — closed it, and the
same rule produced six different optical spacings (measured on the masters:
8 px of real clearance in "12", 23 in "15", 37 in "20"). An independent
grader saw the tightest of them on the live dial and scored the ruling
7/10.

`_ink_advance` measures per ROW instead — rightmost ink of the left glyph
against leftmost ink of the right — and the closest pair sets the advance,
so every pair wears the same clearance. The value
(`dial.LETTER_COMPOSE_INK_GAP_FRACTION`) is SOLVED, not chosen: it is the
clearance at which the composed `20` comes back at exactly the 730x512 the
owner drew. His kerning, applied evenly.

## Connections

### Uses
- `config.constants` — `LETTER_PLATE_FILES`, `GREEK_LATIN_TWINS`
- `config.dial` — `LETTER_ART_DIR`, `LETTER_COMPOSE_INK_GAP_FRACTION`
- `config.paths` — `art_file` (the `_gem`/`_gpt` source resolution)
- [Raster Store](raster_store.md) — the composed master's cache slot and
  its atomic write

### Used by
- `app.controller` — every ring jewel and crown-text seat's art path
- [Numeral Bands](numeral_bands.md) — the live crown's own glyph tiles
- `app.watch_face.thumbs` — the preset picker's mini previews
