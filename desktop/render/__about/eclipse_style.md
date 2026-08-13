# Eclipse Style Door

**Script:** [Eclipse Style Door (script)](../eclipse_style.py)

## Purpose

THE HONESTY DOOR (owner ballot 2026-08-13, item 14 — "say when the
chosen style cannot be drawn"). One function every eclipse call site
asks before it paints: for a given `(kind, style)`, can it draw itself
here, or must it fall back — and to what, and why.

Born because the same ballot round accepted six brand-new display
styles (`totality_path`/`type_emblem`/`dial_shadow` on the solar side,
`blood_moon`/`danjon_scale`/`contact_marks` on the lunar side) shipped
as plumbing first, with no painters. Both halves were painted later the
same day, so the `_NOT_YET_PAINTED` table is now EMPTY and every name
resolves to itself — the mechanism stays exactly where it is, because
the next accepted style will land the same way and this table is what
makes "accepted but not yet drawn" a stated fact instead of a silent
alias. Without this
module every one of the five call sites that dispatch on the style name
would have had to invent its own "what do I draw instead" answer, and
at least one of them would have gotten it wrong or silent, exactly the
failure the ballot names. Instead every one of them resolves through
`resolve_eclipse_style`, which generalises the ONE fallback
`horizon_shadow` already used (drop to `"halo"` without its band)
rather than adding a second mechanism.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.
  ECLIPSE_SOLAR_STYLES` / `ECLIPSE_LUNAR_STYLES`, the rosters a `style`
  is validated against

### Used by
- [Solar Eclipse](solar_eclipse.md) — `draw_solar_eclipse` resolves the
  solar style before dispatching to `_solar_eclipse_body`
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer.
  _draw_moon` resolves the lunar style before its umbra_sweep/halo
  branch; `MoonBandLayer.paint` resolves it before deciding whether to
  draw the band's copper segment
- [Eclipse Plates](eclipse_plates.md) — `_draw_lunar` resolves the
  style before its disc/band dispatch (the solar side goes through
  `draw_solar_eclipse` above, so it needs no call of its own)
- `app.watch_face.thumbs` — `eclipse_lunar_style_icon` resolves the
  style before choosing which real painter to preview
- `tests/test_eclipse_style_completion.py` — the roster completion
  tooth; `tests/test_eclipse_distinctness.py` — reads
  `NOT_YET_PAINTED_STYLES` to exempt declared, honest duplicates from
  the "no two displays draw the same picture" law

## Functions

### `resolve_eclipse_style(kind, style, *, band_available=True)`
Returns `(effective_style, reason)`. `reason is None` means `style`
draws itself unchanged; otherwise `effective_style` is what actually
gets painted and `reason` says why in plain English. Raises
`ValueError` for a `style` outside the kind's roster (a typo, never a
fallback case) and for a fallback cycle (a config bug, never reachable
today).

## Constants

| Name | Meaning |
|------|---------|
| `_NATIVE_STYLES` | the styles each kind can actually paint today |
| `_BAND_ONLY_STYLES` | `horizon_shadow`, `contact_marks` — need `moon_band_mode == "horizon"`, fall back to `halo` without it |
| `_NOT_YET_PAINTED` | the ballot's six new names -> `(borrowed style, reason)`; SHRINKS as painters land, one entry at a time |
| `NOT_YET_PAINTED_STYLES` | public `frozenset` view of `_NOT_YET_PAINTED`'s keys, read by the distinctness test |

## Design Decisions

- **One door, not five.** Before this module, `horizon_shadow`'s
  band-fallback lived only inside `MoonBandLayer`/`YearMarkerLayer`,
  each call site would otherwise have needed its own copy of "is this
  style even paintable here" — a second mechanism per ballot style
  instead of one shared answer.
- **The fallback table is the ONLY place a "borrows X" decision is
  made.** A call site never guesses; it asks the door and paints
  whatever comes back, so a change to which style a not-yet-painted
  name borrows never needs a second edit anywhere else.
- **`reason` is prose, not an enum**, because its only consumers today
  are a docstring-reading human and a test asserting non-emptiness —
  turning it into a coded reason would be a second vocabulary for
  nothing another module reads.
