# Seating Preview

**Script:** [Seating Preview (script)](../seating_preview.py) ·
**Flow:** [diagram](../__flow/seating_preview.md)

## Purpose

Offscreen QPainter previews of the two Session-26 seatings (CUBE.md §The
Seatings) — the Rose's three octa stars with all 24 human seats, and the
Calendar's twelve wedges with each axis's two ends by radius. Draws only
what `core.cube_seating` computes, so the pictures cannot disagree with the
golden tests. Not part of the app; no pointer is wired to either seating yet
— a research renderer for the owner's eyes only.

## Usage

```bash
python research/seating_preview.py
```

Writes `research/seating/rose_24.png` and `research/seating/calendar_12.png`.

## Connections

### Uses
- [Cube Seating](../../core/__about/cube_seating.md) —
  `rose_seating()`, `calendar_seating()`, `ray_star()`, `RAY_STEP_DEG`
- `config.constants`, `config.cube`, `config.defaults`, `config.palette` —
  arm geometry, the sacred-trio names, the Rose/Calendar palettes

### Used by
- Nobody in the runtime. Output feeds the
  [Seating (subfolder)](../seating/___seating.md) preview images the owner
  reviews before any pointer wiring

## Functions

- `_at`, `_diamond` — polar-to-Cartesian placement and the Rose's octa-arm
  polygon shape
- `_label`, `_radial_label` — text blocks hung on a point; the radial variant
  runs text along its arm and flips 180° in the lower half so nothing reads
  upside down
- `draw_rose()` / `draw_calendar()` — the two seatings, each with its own
  ladder/radial label layout to avoid overlap
- `_ensure_a_readable_font()` — works around an empty font database under
  the offscreen Qt platform plugin by loading a system TTF fallback
- `main()` — builds both images and saves them
