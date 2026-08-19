"""THE POINTER REGISTRY's guard — the permission matrix, kept honest.

Owner ruling 2026-08-04/05. "Which kind of theme may this pointer show"
was knowledge nobody had written down; the matrix now answers it, and
these tests keep it from drifting away from the rest of the program.

They pin three things: the matrix names exactly the pointers that
exist, the sealed rulings are the ones written down, and the SHAPE
dimension actually bites — because the shape half is the part a reader
would most easily drop.
"""

from config import pointer_geometry, registry
from config.registry import pointers


def test_the_matrix_names_every_pointer_and_only_those():
    """A pointer that exists but is not in the matrix has no declared
    permissions, which is how a picker ends up guessing."""
    assert set(pointers.POINTERS) == set(pointer_geometry.POINTER_POINTS)


def test_the_seat_counts_agree_with_what_the_dial_draws():
    """The matrix's `seats` is the count the READER counts on the dial
    (`pointer_geometry.POINTER_DIAL_COUNTS`) — the Rose's twenty-four rays, not
    its eight hues."""
    for pointer, entry in pointers.POINTERS.items():
        assert entry["seats"] == pointer_geometry.POINTER_DIAL_COUNTS[pointer], pointer


def test_the_calendar_refuses_the_week_in_both_shapes():
    """Sealed: the Calendar is cut into TWELVE and a week theme brings
    nine members at most — nine into twelve leaves three wedges to
    invent, and the registry invents nothing."""
    for shape in (pointers.STAR, pointers.POLYGON):
        assert not pointers.may_carry("calendar", pointers.WEEK, shape)
        assert pointers.may_carry("calendar", pointers.DOZEN, shape)


def test_the_dozen_belongs_to_the_calendar_alone():
    assert pointers.pointers_carrying(pointers.DOZEN) == ("calendar",)
    assert pointers.pointers_carrying(pointers.DOZEN, pointers.POLYGON) == (
        "calendar",
    )


def test_the_shape_dimension_bites_on_the_rose():
    """Drawn as a STAR the Rose keeps the Compass in focus with its
    other rays behind it, so the week can be read off them. Drawn as
    DIAMONDS every one of the twenty-four is a seat and takes no guest —
    only the cube fills twenty-four."""
    assert pointers.may_carry("rose", pointers.WEEK, pointers.STAR)
    assert not pointers.may_carry("rose", pointers.WEEK, pointers.POLYGON)
    assert pointers.carries("rose", pointers.POLYGON) == (pointers.CUBE,)


def test_the_cube_rides_the_rose_and_the_calendar_only():
    """Twenty-four seats or twelve axes — nothing else can hold it."""
    assert set(pointers.pointers_carrying(pointers.CUBE)) == {"rose", "calendar"}


def test_aurora_carries_no_circular_theme_at_all():
    """Its content rides the subdials, which show only today — a
    separate mechanism, deliberately outside this matrix."""
    for shape in (pointers.STAR, pointers.POLYGON):
        assert pointers.carries("aurora", shape) == ()


def test_every_wheel_pointer_actually_mounts_an_archetype():
    """A pointer that claims the WHEEL kind must have a real archetype
    grid entry — otherwise the matrix promises what the dial cannot
    draw."""
    from config import archetypes

    mounted = {pointer for pointer, _style in archetypes.ARCHETYPE_GRID}
    claimed = set(pointers.pointers_carrying(pointers.WHEEL))
    assert claimed <= mounted, claimed - mounted


def test_an_unknown_pointer_answers_empty_rather_than_raising():
    """A settings file from a future build must never detonate a
    picker — the graceful-absent law, applied to permissions."""
    assert pointers.carries("nonesuch") == ()
    assert not pointers.may_carry("nonesuch", pointers.WEEK)


def test_a_pointer_that_cannot_carry_the_week_has_no_default_theme():
    """The None is the point (owner debt, closed 2026-08-05). The Watch
    Face picker used to star the app's global default on EVERY pointer,
    including the two that can never show a week theme — telling the
    reader something untrue. A pointer with no permission has no
    default."""
    assert pointers.default_theme("hexa") == pointers.BOOTSTRAP_WEEK_THEME
    assert pointers.default_theme("rose") == pointers.BOOTSTRAP_WEEK_THEME
    assert pointers.default_theme("rose", shape=pointers.POLYGON) is None
    assert pointers.default_theme("calendar") is None
    assert pointers.default_theme("aurora") is None
    assert pointers.default_theme("nonesuch") is None


def test_the_bootstrap_default_is_a_real_week_theme():
    """It is the app's own `Settings.weekday_theme` default, not a
    per-pointer favourite — nobody has made that product decision, and
    the registry does not invent one."""

    assert pointers.BOOTSTRAP_WEEK_THEME in registry.THEMES
