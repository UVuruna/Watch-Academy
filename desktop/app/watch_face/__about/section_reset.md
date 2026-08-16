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
  key. `opacity._knob` binds it at build time now.
- **THE HALF-FIX (owner bug 2026-08-16) — why the same mechanism came
  back, which is the first thing to record.** The 2026-08-15 round
  treated the deferred lookup as an OPACITY problem and fixed one
  module, then guarded it with
  `test_every_section_ends_with_a_reset` — a test that asks whether a
  page has a BUTTON, never whether the button MOVES anything. Eight
  other pages carried the identical shape and passed every gate. The
  owner saw it on Size, whose Reset moved exactly one knob
  (`numeral_outer_ring_size`, the single key that happened to be bound
  eagerly) and left the other eight where he had dragged them. The
  lesson is the rule now: a failure mode found in one module is a
  failure mode of the PATTERN, and the tooth must be written against
  the pattern, not against the module that revealed it.
  Every affected key is now bound in its builder's body — Size (9
  keys), Colors (umbra/aura modes, the four metal shades, five
  saturations), Ring (finish, crown time format / scale / visibility /
  custom text / orientation), Pointer (palette style, shape,
  curvature, edge, daylight), Themes (face layout, subdial plate,
  rotation group / roster / interval, archetype names), Bodies (the
  three crossing switches), plus the two shared row helpers
  (`numerals._choice_row`, `widgets._slider_row`).
- **The tooth is `tests/test_section_reset.py`**, an AST check: in any
  `app/watch_face/*.py`, a `setters[...]` subscript may not appear
  inside a lambda or a nested function, so a deferred lookup fails the
  suite in the session that writes it. Its allowlist holds only the
  keys the two filters above would drop anyway, and a second test keeps
  that allowlist honest. Where a control lives behind a branch (the
  Ring's custom-crown editor, the Pointer's curvature rows, the Themes
  rotation roster) the lookup sits ABOVE the branch — otherwise the
  Reset would own the key only on the screens that happen to show it.
- **No button when there is nothing to reset** — the same grammar as
  ballot verdict 8A: a control with nothing to offer is absent, not
  greyed.
