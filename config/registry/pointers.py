"""THE POINTER REGISTRY — what each pointer may carry, and per SHAPE.

Owner ruling 2026-08-04/05. Until now, "which kind of theme may this
pointer show" was knowledge nobody had written down: the dial simply
did what its render paths happened to support, the Watch Face picker
guessed from the global default, and every session that asked the
question had to re-derive the answer by reading four modules.

THE PERMISSION MATRIX, sealed with the owner:

  * a pointer carries some KINDS and not others — the Calendar is cut
    into twelve and a week theme brings nine members at most, so nine
    into twelve would leave three wedges to invent, and the registry
    invents nothing;
  * and the answer changes with the pointer's SHAPE. Drawn as a STAR,
    the Rose keeps the Compass in focus with its remaining rays behind
    it, so a second kind can be read off them. Drawn as DIAMONDS, each
    diamond is a seat in its own right and takes no guest: the pointer
    then shows only what is native to it — the cube on the Rose, a
    dozen on the Calendar.

Aurora carries no circular theme at all. It offers one to three
SUBDIALS instead, and a subdial shows only today's single item — for a
week theme, the plate of this one day. That is a separate mechanism and
no part of this matrix.

Layer: config — pure DATA, imports nothing. Documentation:
[pointers](__about/pointers.md).
"""

# ═══════════════════════════ THE KINDS ═══════════════════════════
# The four kinds of theme, by the count of seats each one fills. The
# names are the ones the owner uses, and they are what the matrix and
# the pickers both speak.
WEEK = "week"          # 6 weekdays + Ruler + Servant + Ninth
DOZEN = "dozen"        # 12 wedges + the axle
CUBE = "cube"          # 6 faces + 8 vertices + 12 edges; 24 ride, 3 in the axle
WHEEL = "wheel"        # 3/4/6/8 archetype figures + the throne

KINDS = (WEEK, DOZEN, CUBE, WHEEL)

# ═══════════════════════════ THE SHAPES ═══════════════════════════
# A pointer is drawn either as a STAR (arms radiating, art seated on
# them) or as a POLYGON of DIAMONDS (each face a seat of its own).
# `constants.POINTER_SHAPES` is the settings vocabulary; these are the
# same two words, kept here so the matrix reads without a second import.
STAR = "star"
POLYGON = "polygon"

# ═══════════════════════════ THE MATRIX ═══════════════════════════
# pointer -> shape -> the kinds it may carry, in the order a picker
# should offer them. An empty tuple is an ANSWER, not an omission: it
# says this pointer shows no circular theme in this shape.
POINTERS = {
    "trio": {
        "seats": 3,
        "carries": {STAR: (WEEK, WHEEL), POLYGON: (WEEK, WHEEL)},
    },
    "cross": {
        "seats": 4,
        "carries": {STAR: (WEEK, WHEEL), POLYGON: (WEEK, WHEEL)},
    },
    "hexa": {
        "seats": 6,
        "carries": {STAR: (WEEK, WHEEL), POLYGON: (WEEK, WHEEL)},
    },
    "octa": {
        "seats": 8,
        "carries": {STAR: (WEEK, WHEEL), POLYGON: (WEEK, WHEEL)},
    },
    # THE ROSE: eight hues on twenty-four rays. In star shape the
    # Compass stands in focus and the remaining rays sit behind it at a
    # lower depth — still there, still hoverable — so the week and the
    # cube can be read together. In diamond shape every one of the
    # twenty-four is a seat, and only the cube fills twenty-four.
    "rose": {
        "seats": 24,
        "carries": {STAR: (WEEK, CUBE, WHEEL), POLYGON: (CUBE,)},
    },
    # THE CALENDAR: twelve wedges in both shapes. It refuses the week in
    # either — nine into twelve leaves three wedges to invent. The cube
    # fits because a wedge holds a whole AXIS: the outward face and the
    # inward face of one opposition, which is how twenty-four lands on
    # twelve seats (`core.cube_seating.calendar_seating`).
    "calendar": {
        "seats": 12,
        "carries": {STAR: (DOZEN, CUBE), POLYGON: (DOZEN, CUBE)},
    },
    # AURORA: bands, not seats. No circular theme at all — its content
    # rides the subdials, which offer every kind and show only today.
    "aurora": {
        "seats": 7,
        "carries": {STAR: (), POLYGON: ()},
    },
}


def carries(pointer: str, shape: str = STAR) -> tuple[str, ...]:
    """The kinds `pointer` may show in `shape` — () when it shows none.
    An unknown pointer answers () rather than raising: a settings file
    from a future build must never detonate a picker."""
    entry = POINTERS.get(pointer)
    if entry is None:
        return ()
    return entry["carries"].get(shape, ())


def may_carry(pointer: str, kind: str, shape: str = STAR) -> bool:
    """THE PERMISSION MATRIX as one question — the form every picker and
    every validator should ask, so the answer lives in one place."""
    return kind in carries(pointer, shape)


def pointers_carrying(kind: str, shape: str = STAR) -> tuple[str, ...]:
    """Every pointer that may show `kind` in `shape`, in matrix order —
    the reverse lookup a theme picker needs when it starts from the
    theme rather than from the pointer."""
    return tuple(
        pointer for pointer in POINTERS if may_carry(pointer, kind, shape)
    )
