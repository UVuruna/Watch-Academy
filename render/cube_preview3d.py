"""Guarded bridge to the sibling 3D Preview gadget (WORKPLAN Session 28
— the amended page list: The Cube, The Thirteen Axes, each of the 12
human axis pages, and the Composure/Vigor poles).

THE FALLBACK LAW (root Rule #1's documented path): if the gadget cannot
be imported, its schema rejects the exported model, or a page asks for
a kind/key this module does not recognise, `build_widget()` answers
`None` and logs — never raises. The reader keeps its computed 2D plate
(`render.cube_diagrams`) as the automatic fallback in every one of
those cases. Nothing here does any work at import time (the
Encyclopedia never-block law): the gadget is imported, and the model
built and validated, only the first time a page actually asks for one.

Layer: render (Qt allowed — the gadget's `Preview3DLightWidget` IS a
QWidget). The MODEL itself comes from the Qt-free, gadget-free
`data.cube_model_export`; only the WIDGET half needs the guarded
gadget import.
"""

import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from config import paths
from data import cube_model_export

logger = logging.getLogger(__name__)

_gadget = None
_gadget_load_attempted = False
_model = None
_model_build_attempted = False

# The gadget kinds this bridge answers for — every other `(kind, key)`
# a page might carry (terms, sets, hexagram, banknote, ...) is out of
# this session's amended scope and always falls back to the 2D drawer.
_ELIGIBLE_KINDS = ("cube", "axes", "axis", "pole")

_TIER_VIEWS: tuple[tuple[str, str], ...] = (
    ("primary", "Primary"), ("secondary", "Secondary"), ("tertiary", "Tertiary"),
)


def _load_gadget():
    """Import the sibling gadget package once; `None` forever after on
    ANY failure — a missing folder, a missing dependency, an import-time
    exception inside the gadget itself. Never raises."""
    global _gadget, _gadget_load_attempted
    if _gadget_load_attempted:
        return _gadget
    _gadget_load_attempted = True
    gadget_dir = paths.preview3d_gadget_dir()
    if gadget_dir is None:
        logger.info(
            "3D Preview gadget not found beside this project — the Cube "
            "family keeps its computed 2D drawer."
        )
        return None
    gadget_path = str(gadget_dir)
    if gadget_path not in sys.path:
        # APPEND, never insert(0) (0.14.711): the gadget root carries
        # its own `main.py` and `tests/`, and at the FRONT of sys.path
        # they shadowed this project's same-named modules for the rest
        # of the process — `import main` after any Cube 3D page load
        # resolved to the GADGET's main (caught by the crash-log test).
        # The bridge only needs `preview3d`, a name this project does
        # not carry, and the package imports nothing but stdlib +
        # PySide6 (verified by AST walk) — so LAST in line is enough.
        sys.path.append(gadget_path)
    try:
        import preview3d
    except Exception:
        logger.exception(
            "3D Preview gadget failed to import — the Cube family keeps "
            "its computed 2D drawer."
        )
        return None
    _gadget = preview3d
    return _gadget


def available() -> bool:
    """Whether the gadget is usable — read by tests and by callers that
    want to short-circuit before building a page."""
    return _load_gadget() is not None


def _model_json():
    """The exported model, validated once and cached. `None` on ANY
    failure (import, build, or schema validation)."""
    global _model, _model_build_attempted
    if _model_build_attempted:
        return _model
    _model_build_attempted = True
    gadget = _load_gadget()
    if gadget is None:
        return None
    try:
        model = cube_model_export.build_model()
        gadget.validate(model)
    except Exception:
        logger.exception(
            "The Character-Cube model failed to build or validate — the "
            "Cube family keeps its computed 2D drawer."
        )
        return None
    _model = model
    return _model


class _CubePreviewPanel(QWidget):
    """A 3D stage, plus — only for The Thirteen Axes page — a small row
    of view buttons underneath it. One widget contract for every
    cube-family page: `reader.py` only ever asks for a widget and a
    target square size."""

    def __init__(self, stage, view_names: tuple[tuple[str, str], ...] = (), parent=None):
        super().__init__(parent)
        self._stage = stage
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(stage, alignment=Qt.AlignmentFlag.AlignHCenter)
        if view_names:
            row = QHBoxLayout()
            row.addStretch(1)
            for name, label in view_names:
                button = QPushButton(label)
                button.setStyleSheet(
                    "QPushButton { padding: 2px 10px; }"
                )
                button.clicked.connect(
                    lambda _checked=False, n=name: stage.set_model_view(n)
                )
                row.addWidget(button)
            row.addStretch(1)
            layout.addLayout(row)

    def set_square_size(self, side: int) -> None:
        """The stage is exactly `side x side`; a button row (if any)
        keeps its own natural height beneath it, and the panel's width
        is fixed to the stage so it never grows past its page."""
        self._stage.setFixedSize(side, side)
        self.setFixedWidth(side)


def _stage(gadget, model: dict, view_name: str):
    widget = gadget.Preview3DLightWidget()
    widget.set_background("transparent")
    widget.show_model(model, view_name)
    return widget


def build_widget(kind: str, key: str) -> QWidget | None:
    """A ready-to-show 3D panel for one Encyclopedia page, or `None` —
    the only two outcomes a page ever sees. `None` means: keep the
    static 2D plate, exactly as if this module did not exist."""
    if kind not in _ELIGIBLE_KINDS:
        return None
    model = _model_json()
    if model is None:
        return None
    gadget = _gadget
    try:
        if kind == "cube":
            return _CubePreviewPanel(_stage(gadget, model, "cube"))
        if kind == "axes":
            return _CubePreviewPanel(_stage(gadget, model, "primary"), _TIER_VIEWS)
        if kind == "axis":
            return _CubePreviewPanel(_stage(gadget, model, f"axis:{key}"))
        if kind == "pole":
            return _CubePreviewPanel(_stage(gadget, model, f"pole:{key}"))
    except Exception:
        logger.exception(
            "3D panel for (%r, %r) failed to build — falling back to "
            "the 2D drawer.", kind, key,
        )
        return None
    return None
