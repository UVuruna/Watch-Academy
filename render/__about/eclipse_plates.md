# Eclipse Plates

**Script:** [Eclipse Plates (script)](../eclipse_plates.py)

## Purpose

One drawn picture per `(kind, type, style)` for the Encyclopedia's own
look slider.

Owner order 2026-08-12: the Encyclopedia should explain every state and
every display the program can show, on the SAME slider that already
pages Colored / Bronze / Gold / Silver. So on the eclipse chapters that
existing look switcher (`app.encyclopedia.reader`'s arrows) pages the
DISPLAY STYLES of an eclipse instead — a total lunar eclipse shows the
umbra sweep, then the band's copper segment, then the halo darkening:
the same three pictures the dial itself can draw.

**The pictures are the DIAL'S OWN** (Rule #5). Nothing here
re-implements an eclipse — the glow comes from `render.eclipse_glow`,
the solar overlays from `render.marker_marks.draw_solar_eclipse`, and
the lunar face and its umbra from `render.moon_face`. If a style changes
on the dial, these plates change with it. A hand-drawn illustration
would have started lying the first time the owner corrected a style,
which is exactly how the twelve unwired figure casts happened
(THE THEME COMPLETION LAW).

## Connections

### Uses
- [Eclipse Glow](eclipse_glow.md) — `draw_event_glow`,
  `eclipse_state_glow_strength`
- [Marker Marks](marker_marks.md) — `draw_solar_eclipse`, the solar
  overlays
- [Moon Face](moon_face.md) — `draw_moon_disc`, `draw_umbra_sweep`
- [Layers (subfolder)](../layers/___layers.md) —
  `MoonBandLayer.draw_eclipse_segment`, called directly so the band
  segment has one home
- [Painting](painting.md) — `tinted_gray` (the halo multiply)
- [Raster Store](raster_store.md) — `atomic_save`
- [Config (folder)](../../config/___config.md) — `constants`,
  `defaults`, `glow`, `palette`, `paths`

### Used by
- `app.encyclopedia.pages` / `app.encyclopedia.reader` — the eclipse
  chapters' `looks` tuple, fed to the same reader control the metal
  looks use

## Constants

| Name | Meaning |
|------|---------|
| `PLATE_SIZE_PX` = 512 | the square plate; the body sits at `_BODY_FRACTION` (0.30) of it so the 1.5x halo and the solar rays are never clipped |
| `_GROUND_RADIUS_FRACTION` = 0.49 | the night field drawn under the body |
| `TYPES` | the catalog types each kind distinguishes, in the Encyclopedia's own chapter order — ONE roster, so a plate can never exist for a chapter that does not, or the other way round |
| `STYLES` | `constants.ECLIPSE_SOLAR_STYLES` / `ECLIPSE_LUNAR_STYLES` |
| `TYPICAL_MAGNITUDE` | a typical catalog magnitude per type — a documented approximation, stated here rather than hidden in the painter |

## Functions

### `style_label(style)`
The slider's caption: the style's own id read as words, deliberately NOT
a prettier invented name. The same word is what the Watch Face picker
shows and what the docs argue about, and two names for one style is how
a reader ends up unable to find the setting a page is describing.

### `plate_file(kind, type_, style)`
The drawn plate, disk-cached under a COMPUTED name — there is no source
file to fingerprint, the same convention
`asset_variants.calendar_sheet_icon_file` uses, so
`raster_store.collect_garbage` leaves it alone (its carve-out for names
whose first field is not a 16-hex stamp). Painted once per install and
reused. A failed save **RAISES**: an Encyclopedia page silently missing
the picture it is explaining is the failure this module exists to
prevent.

### `looks_for(kind, type_)`
The chapter's `looks` tuple — one look per display style, in the order
the Watch Face picker lists them, each a single-image row. Shaped
exactly like `_metal_looks`' Colored / Bronze / Gold / Silver, because
it feeds the SAME reader control.

### `_draw_plate` / `_draw_solar` / `_draw_lunar`
The painters. Both kinds get the dial's own night field underneath —
without it a bronze halo on the reader's pale page would be invisible,
and the page would claim to show a picture that cannot be seen.

## Design Decisions

- **A TYPICAL magnitude per type, not a real event.** The geometry
  styles (`bite`, `umbra_sweep`, `magnitude_arc`) are pictures OF a
  magnitude, so a plate without one would show the same picture for
  every type.
- **The lunar disc is always full (fraction 0.5).** A lunar eclipse only
  ever happens at full moon, so this is not a chosen illustration but
  the phase the event requires.
- **`horizon_shadow` draws the BAND, not the disc.** That style leaves
  the disc alone and writes the event where DURATION can be seen (owner
  placement 2026-08-10), so the plate shows the band arc with its copper
  segment rather than a second, contradicting disc treatment. Its angle
  is the plate's illustration choice, not a claim about any real
  eclipse: it stands where an evening event would, so the arc reads as a
  span of hours.
