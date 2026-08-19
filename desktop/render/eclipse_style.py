"""THE ECLIPSE STYLE DOOR — one place every eclipse call site asks
before it paints: "can this style draw itself here, or must it fall
back, and to what, and why".

Born from the owner's 14th ballot item, 2026-08-13, his own words:
"Iskrenost: reci kad izabrani stil ne moze da se nacrta" (honesty: say
when the chosen style cannot be drawn).
lang-ok: the owner's own ballot sentence, quoted so the requirement
cannot be re-derived wrongly — same convention as `eclipse_plates.py`'s
module docstring.

Six new display styles were accepted the same round —
`totality_path`/`type_emblem`/`dial_shadow` on the solar side,
`blood_moon`/`danjon_scale`/`contact_marks` on the lunar side — and
shipped as PLUMBING first, with no painters. Both halves were painted
later the same day, so `_NOT_YET_PAINTED` below is now EMPTY and every
name resolves to itself; the mechanism stays exactly where it is,
because the next accepted style will land the same way and the table is
what makes "accepted but not yet drawn" a stated fact instead of a
silent alias. Routing a still-unpainted name through the SAME fallback the
pre-existing `horizon_shadow` already used (fall back to "halo" when
its band is absent) means a picker choice never silently turns into
"draws nothing" or "quietly draws the default and lies about it" — the
exact failure the ballot names.

Layer: render. Documentation: __about/eclipse_style.md.
"""

from config import umbra


# Every solar/lunar style this module can actually PAINT today, keyed
# by kind — everything else in `umbra.ECLIPSE_*_STYLES` is either
# one of these, or listed in `_NOT_YET_PAINTED` below with the painted
# style it currently borrows.
_NATIVE_STYLES = {
    "solar": frozenset({
        "bite", "magnitude_arc", "halo",
        # PAINTED 2026-08-13, the same day the plumbing landed — see
        # `render.solar_eclipse`. Their entries left `_NOT_YET_PAINTED`
        # below with them, which is exactly what that table is for.
        "totality_path", "type_emblem", "dial_shadow",
    }),
    "lunar": frozenset({
        "umbra_sweep", "horizon_shadow", "halo",
        # PAINTED 2026-08-13 (lunar painters round): "blood_moon" is
        # `render.moon_face.draw_blood_moon`, "danjon_scale" is
        # `render.eclipse_danjon.draw_danjon_scale`, "contact_marks" is
        # `MoonBandLayer.draw_contact_marks` laid over the segment
        # "horizon_shadow" already draws. Their entries left
        # `_NOT_YET_PAINTED` below with them.
        "blood_moon", "danjon_scale", "contact_marks",
    }),
}

# Styles that need the Moon Horizon Band (`moon_band_mode == "horizon"`)
# to have anything to draw on. Outside that mode they fall back to
# "halo" — the disc-side treatment that needs no band at all.
_BAND_ONLY_STYLES = frozenset({"horizon_shadow", "contact_marks"})

# THE BALLOT'S SIX, each mapped to the shipped style its picture
# currently borrows, and WHY — read by any caller that wants to say so
# rather than pretend. Removing an entry here (because a real painter
# landed) is the whole point of this table; adding one needs the same
# ballot discipline THE CONFIG SECTION LAW asks of `constants.py`.
_NOT_YET_PAINTED: dict[tuple[str, str], tuple[str, str]] = {
    # THE SOLAR THREE ARE GONE FROM HERE (2026-08-13): `totality_path`,
    # `type_emblem` and `dial_shadow` all have their own painters in
    # `render.solar_eclipse` now, so they resolve to themselves and
    # `tests/test_eclipse_distinctness.py` holds them to the same "no
    # two eclipse displays draw the same picture" bar as every other
    # style. This is what the table shrinking looks like.
    # THE LUNAR THREE ARE GONE FROM THIS TABLE, and their absence is the
    # deliverable (lunar painters round, 2026-08-13): `blood_moon`
    # (`render.moon_face.draw_blood_moon`), `danjon_scale`
    # (`render.eclipse_danjon.draw_danjon_scale`) and `contact_marks`
    # (`render.layers.moon_band.MoonBandLayer.draw_contact_marks`) now
    # paint themselves and are listed in `_NATIVE_STYLES` above.
    # `contact_marks` keeps its BAND requirement — it is still in
    # `_BAND_ONLY_STYLES`, which is a context fallback, not a missing
    # painter, and the two must not be confused.
}


# Public view of `_NOT_YET_PAINTED`'s keys — every (kind, style) that
# currently borrows another style's picture. Read by
# `tests/test_eclipse_distinctness.py` to exempt exactly these pairs
# from the "no two displays draw the same picture" law: their shared
# picture is this round's DECLARED, honest state, not the silent alias
# that law exists to catch. The exemption SHRINKS as painters land —
# removing a name from `_NOT_YET_PAINTED` above removes it from here
# too, and the distinctness test starts holding it to the same bar as
# every native style.
NOT_YET_PAINTED_STYLES = frozenset(_NOT_YET_PAINTED)


def resolve_eclipse_style(
    kind: str, style: str, *, band_available: bool = True,
) -> tuple[str, str | None]:
    """Answers, for one (kind, style, context): "draw it" (returns
    `(style, None)`) or "cannot draw here, fall back to X because Y"
    (returns `(X, "why")`).

    `kind` is "solar" or "lunar". `band_available` is whether the Moon
    Horizon Band is up (`moon_band_mode == "horizon"`) — the only piece
    of CONTEXT any style here currently needs; a future band-independent
    style needs no new parameter, a future context-dependent one adds
    one, kept keyword-only so every caller stays readable.

    Generalises the ONE mechanism `horizon_shadow` already used (fall
    back to "halo" without a band) rather than inventing a second one —
    the caller never has to know whether the fallback is "no band" or
    "no painter yet", only what to paint and, if it cares, why.

    Raises `ValueError` for a `style` outside `umbra.ECLIPSE_*_STYLES`
    — that is a real bug (a typo, a stale name), never a case this door
    should quietly paper over."""
    roster = (
        umbra.ECLIPSE_SOLAR_STYLES if kind == "solar"
        else umbra.ECLIPSE_LUNAR_STYLES
    )
    if style not in roster:
        raise ValueError(f"unknown {kind} eclipse style {style!r}")
    current = style
    reason: str | None = None
    seen: set[str] = set()
    while True:
        if current in seen:
            raise ValueError(
                f"eclipse style fallback cycle at {kind}/{current!r}"
            )
        seen.add(current)
        if current in _BAND_ONLY_STYLES and not band_available:
            current = "halo"
            reason = reason or (
                "needs moon_band_mode == \"horizon\"; the band is absent"
            )
            continue
        if (kind, current) in _NOT_YET_PAINTED:
            current, why = _NOT_YET_PAINTED[(kind, current)]
            reason = reason or why
            continue
        break
    assert current in _NATIVE_STYLES[kind], (
        f"{kind}/{style} resolved to {current!r}, which has no painter"
    )
    return current, reason
