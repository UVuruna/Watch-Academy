# Per-Section Reset

**Script:** [Section reset (script)](../section_reset.py)

## Purpose
The Reset button that closes every Watch Face section (owner order
2026-08-15) and the machinery that makes it safe: which settings does a
section actually own?

## Connections

### Uses
- [Settings Store](../../__about/settings_store.md) — `Settings` for the
  factory values and for the field list that separates a SETTING from a
  data provider
- [UI Style](../../__about/ui_style.md) — `tooltip_wrap`

### Used by
- [Watch Face Window](window.md) — wires it ONCE for all nine pages in
  `_build`; no section module declares anything

## Design Decisions

- **The key list is RECORDED, never declared.** A hand-kept list of
  "which settings does the Ring page own" is exactly the kind of record
  that rots the first time somebody adds a control, and nothing would
  notice. `RecordingSetters` wraps the setters mapping the builder is
  handed and notes every key the builder ASKS FOR while it builds —
  whatever the page reached for is, by definition, what the page
  controls. It is a `dict` subclass rather than a proxy because the
  builders treat their `setters` as a plain mapping and pass it on.
- **Two exact filters, no guessing.** A key is resettable when it is a
  real `dataclasses.field` of `Settings` — which drops the data
  providers a page also asks for (`slot_descriptors`,
  `opacity_skin_defaults`, `ring_has_crown_text`, `open_custom_ring`) —
  AND its setter takes exactly one required positional value, which
  drops `palettes` (pointer, style, hues) and `theme_metal` (theme,
  metal). Those belong to compound controls and are left alone rather
  than reset wrongly.
- **Arity only works because the wrapper is signature-honest.**
  `WatchController._watch_face_setters` wraps every setter in a
  `(*args, **kwargs)` closure, under which every setter looks alike.
  That `wrap` now carries `functools.wraps`, so `__wrapped__` lets
  `inspect.signature` see the real arity. Its own tooth is
  `test_watch_face.py::test_the_controller_wrapper_reports_the_real_
  setter_signature` — without it the Reset would silently degrade to
  writing nothing.
- **A lookup deferred into a callback is invisible here.** The Opacity
  page grew no button on the first pass because its knobs looked their
  setter up inside the click callback, so the build never asked for the
  key. `opacity._knob` binds it at build time now, and
  `test_every_section_ends_with_a_reset` fails for any future section
  that defers the same way.
- **No button when there is nothing to reset** — the same grammar as
  ballot verdict 8A: a control with nothing to offer is absent, not
  greyed.
