"""The Themes & Slots CONTENT TREE (R-17/R-18, see theme_tree.md) — a
breadcrumb-navigated Level 1/2/3 picker, never a flat dump of every
theme. Shared by whichever slot `themes.py` has active, and by the
FULL-FACE weekday binding when no slot is enabled.
"""

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from app.watch_face.widgets import pill
from app.weekday_theme_grid import (
    build_weekday_group_grid,
    build_weekday_theme_tiles,
    weekday_group_titles,
)
from config import constants
from config.registry import pointers

_ZODIAC_STYLES = constants.ZODIAC_SLOT_STYLES + ("text",)
_CHINESE_STYLES = constants.CHINESE_SLOT_STYLES + ("text",)

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


def _clear(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            _clear(item.layout())


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
    tabs_row = QHBoxLayout()
    for key, title in available:
        tabs_row.addWidget(pill(
            tr(title), _nav.kind == key,
            lambda k=key: _select_kind(k, rebuild),
        ))
    if len(available) > 1:
        root.addLayout(tabs_row)
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
        layout.addWidget(build_weekday_group_grid(
            None, lambda group: _select_group(group, rebuild), tr,
        ))
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
    grid = QGridLayout()
    for index, (mode, title) in enumerate(
        constants.SLOT_COMPLICATION_TITLES.items()
    ):
        row, col = divmod(index, 2)
        grid.addWidget(
            pill(
                tr(title), active.mode_value == mode,
                lambda m=mode: active.set_mode(m),
            ),
            row, col,
        )
    widget = QWidget()
    widget.setLayout(grid)
    return widget


def _style_branch(active, family: str, styles: tuple[str, ...], tr) -> QWidget:
    grid = QGridLayout()
    for index, style in enumerate(styles):
        row, col = divmod(index, 3)
        checked = active.mode_value == family and active.style_value == style
        grid.addWidget(
            pill(
                tr(style.capitalize()), checked,
                lambda s=style: active.set_style_mode(family, s),
            ),
            row, col,
        )
    widget = QWidget()
    widget.setLayout(grid)
    return widget
