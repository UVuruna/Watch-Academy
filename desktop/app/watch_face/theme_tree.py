"""The Themes & Slots CONTENT TREE (R-17/R-18, see theme_tree.md) — a
breadcrumb-navigated Level 1/2/3 picker, never a flat dump of every
theme. Shared by whichever slot `themes.py` has active, and by the
FULL-FACE weekday binding when no slot is enabled.
"""

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from app import rebuild
from app.watch_face import thumbs
from app.watch_face.controls import picture_group
from app.watch_face.widgets import flow_row, pill
from app.weekday_theme_grid import (
    build_weekday_group_grid,
    build_weekday_theme_tiles,
    weekday_group_titles,
)
from config import constants, defaults
from config.registry import pointers

# Order-preserving DEDUPE (owner review round 2026-08-09): the source
# tuples already end in "text", so the old `+ ("text",)` doubled that
# button in every style gallery.
_ZODIAC_STYLES = tuple(dict.fromkeys(constants.ZODIAC_SLOT_STYLES + ("text",)))
_CHINESE_STYLES = tuple(dict.fromkeys(constants.CHINESE_SLOT_STYLES + ("text",)))

#: The pointer's default weekday theme, asked of THE POINTER REGISTRY
#: (`config.registry.pointers.default_theme`) rather than assumed.
#:
#: It answers None where the pointer cannot carry a week theme at all —
#: the Calendar (twelve wedges against nine members) and Aurora (no
#: circular theme at all) — so the picker no longer stars an option
#: that pointer can never show. Where the week IS carried the answer is
#: the app's own bootstrap default: no pointer has ever asked for a
#: different one, and inventing per-pointer favourites is a product
#: decision nobody has made.
def default_weekday_theme(pointer: str, shape: str = pointers.STAR):
    return pointers.default_theme(pointer, pointers.WEEK, shape)

#: Level-1 kind keys, in menu order, and the human title each shows.
_KIND_TITLES = (
    ("weekday", "Weekday themes"),
    ("complications", "Complications"),
    ("astrology", "Astrology"),
    ("ascendant", "Ascendant"),
    ("chinese", "Chinese zodiac"),
)


@dataclass
class _Nav:
    """Breadcrumb path — module-level (see theme_tree.md Design
    Decisions): a drill-down click is pure navigation, never a
    setter, so it never triggers the window's live-apply rebuild —
    surviving THAT rebuild (triggered by an unrelated pick elsewhere)
    is all this state needs to do."""

    kind: str = "weekday"
    weekday_group: str | None = None


_nav = _Nav()


def reset_navigation() -> None:
    """Test-only reset — production code never calls this."""
    global _nav
    _nav = _Nav()


# ONE DOOR, not a private twin: this helper stood here and in
# `theme_tree.py` byte for byte, and both spelled a teardown that made a
# top-level window flash open mid-screen. The rule and the measurement
# live in `app.rebuild` — hide BEFORE unparenting.
_clear = rebuild.clear_layout


def build(active, full_face: bool, pointer: str, pointer_shape: str, tr) -> QWidget:
    """`active` is a `SlotDescriptor` (see `app.slot_descriptor`) —
    built fresh by `app.controller._slot_descriptors()` on every call.
    `full_face=True` filters Level 1 through `constants.watch_face_kinds`;
    a real subdial offers every kind (owner verdict P-4)."""
    root = QVBoxLayout()
    widget = QWidget()

    def rebuild() -> None:
        _clear(root)
        _populate(root, active, full_face, pointer, pointer_shape, tr, rebuild)

    rebuild()
    widget.setLayout(root)
    return widget


def _populate(root, active, full_face, pointer, pointer_shape, tr, rebuild) -> None:
    if full_face:
        # Only "weekday" maps onto a wired full-face kind today ("week"
        # — see themes.md's Design Decisions); Complications/Astrology/
        # Ascendant/Chinese have no full-face rendering path at all, so
        # they are never offered there — never a dead button.
        kinds = constants.watch_face_kinds(pointer, pointer_shape)
        available = (
            [("weekday", "Weekday themes")] if "week" in kinds else []
        )
    else:
        # SUBDIAL: every kind is offered (owner verdict P-4).
        available = list(_KIND_TITLES)
    if not available:
        note = QLabel(tr(_no_content_note(pointer, pointer_shape)))
        note.setWordWrap(True)
        root.addWidget(note)
        return
    if len(available) > 1:
        # WRAPS (Space & Legibility ladder step 2): five kind tabs ran
        # off the right edge at the 1280px minimum — measured, and the
        # same capture at the previous commit proves it predates the
        # CardGroup migration.
        root.addWidget(flow_row(
            pill(
                tr(title), _nav.kind == key,
                lambda k=key: _select_kind(k, rebuild),
            )
            for key, title in available
        ))
    active_kind = _nav.kind if _nav.kind in dict(available) else available[0][0]
    if active_kind == "weekday":
        root.addWidget(_weekday_branch(active, pointer, pointer_shape, tr, rebuild))
    elif active_kind == "complications":
        root.addWidget(_complications_branch(active, tr))
    else:
        family = active_kind
        styles = _ZODIAC_STYLES if family != "chinese" else _CHINESE_STYLES
        root.addWidget(_style_branch(active, family, styles, tr))


def _no_content_note(pointer: str, pointer_shape: str) -> str:
    if pointer == "aurora":
        return "Aurora carries no circular theme at full face — only subdials."
    if pointer == "rose" and pointer_shape == "polygon":
        return (
            "The Rose (polygon) carries only Cube content at full face — "
            "not wired here yet."
        )
    return (
        "This pointer carries no full-face theme content — pick a "
        "subdial layout above to reach one."
    )


def _select_kind(key: str, rebuild) -> None:
    _nav.kind = key
    if key != "weekday":
        _nav.weekday_group = None
    rebuild()


def _weekday_branch(active, pointer, pointer_shape, tr, rebuild) -> QWidget:
    layout = QVBoxLayout()
    if _nav.weekday_group is None:
        families = build_weekday_group_grid(
            None, lambda group: _select_group(group, rebuild), tr,
        )
        layout.addWidget(families)
        # (The Roster row used to be seated inside this card, a stop on
        # its way from a band of its own to where it actually belongs:
        # verdict 3A's Variant panel, beside every other thing a theme
        # can vary. `app.watch_face.theme_variants` owns it now.)
    else:
        crumb = QHBoxLayout()
        back = QPushButton(f"← {tr(_nav.weekday_group)}")
        back.clicked.connect(lambda: _clear_group(rebuild))
        crumb.addWidget(back)
        crumb.addStretch(1)
        layout.addLayout(crumb)
        layout.addWidget(build_weekday_theme_tiles(
            _nav.weekday_group, active.theme_value,
            default_weekday_theme(pointer, pointer_shape),
            lambda theme: active.set_weekday(theme), tr,
        ))
    widget = QWidget()
    widget.setLayout(layout)
    return widget


def _select_group(group: str, rebuild) -> None:
    _nav.weekday_group = group
    rebuild()


def _clear_group(rebuild) -> None:
    _nav.weekday_group = None
    rebuild()


def _complications_branch(active, tr) -> QWidget:
    """Tiles with SKETCH previews since the 2026-08-09 round (owner
    order: every picker shows what it picks; his instruction allows a
    sketch, and the recon proved complications have no bounded art
    door — they draw computed text/ticks on the dial)."""
    return picture_group(
        tr("Complication"), tr("What this subdial counts or shows."),
        [
            (
                mode, tr(title),
                tr("The {title} complication on this subdial.").format(
                    title=title
                ),
                thumbs.complication_icon(mode),
            )
            for mode, title in constants.SLOT_COMPLICATION_TITLES.items()
        ],
        active.mode_value, active.set_mode,
    )


def _style_icon(family: str, style: str):
    """One style's preview: the style's OWN representative plate (the
    art the dial would draw — Aries for the zodiac families, the Dragon
    for the Chinese one), or the computed name-sketch for the art-less
    "text" style."""
    figure = "Dragon" if family == "chinese" else "Aries"
    if style == "text":
        return thumbs.text_style_icon(figure)
    dirs = (
        constants.CHINESE_STYLE_ART_DIRS if family == "chinese"
        else constants.ZODIAC_STYLE_ART_DIRS
    )
    art_dir = dirs.get(style)
    if art_dir is None:
        return thumbs.text_style_icon(figure)
    return thumbs.art_thumbnail(
        defaults.ZODIAC_ART_DIR / art_dir / f"{figure}.png"
    )


def _style_branch(active, family: str, styles: tuple[str, ...], tr) -> QWidget:
    """Cards with the style's own art since the 2026-08-09 round."""
    current = active.style_value if active.mode_value == family else None
    return picture_group(
        tr("{family} style").format(family=family.capitalize()),
        tr("Which art draws this family's figures."),
        [
            (
                style, tr(style.capitalize()),
                tr("The {style} art for this family.").format(style=style),
                _style_icon(family, style),
            )
            for style in styles
        ],
        current, lambda style: active.set_style_mode(family, style),
    )
