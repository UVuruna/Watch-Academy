"""Umbra & Aura section (see umbra_aura.md) — the umbra FORM pills
(Fine/Coarse/Gradient) and CONTRAST pills, moved verbatim from
`design_window.DesignDialog._umbra_tab`. Coloring lives in the Colors
section and opacity in the Opacity section (both later phases) — this
page carries only the form/contrast choice.
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.watch_face.widgets import pill
from config import constants


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    form_row = QHBoxLayout()
    for form, title in (
        ("fine", "Fine (16 shades)"), ("coarse", "Coarse (13 shades)"),
        ("gradient", "Gradient"),
    ):
        form_row.addWidget(pill(
            tr(title), settings.umbra_form == form,
            lambda f=form: setters["umbra_form"](f),
        ))
    layout.addLayout(form_row)
    contrast_row = QHBoxLayout()
    for variant in constants.UMBRA_CONTRAST_VARIANTS:
        contrast_row.addWidget(pill(
            tr(f"{variant.capitalize()} contrast"),
            settings.umbra_contrast == variant,
            lambda v=variant: setters["umbra_contrast"](v),
        ))
    layout.addLayout(contrast_row)
    widget = QWidget()
    widget.setLayout(layout)
    return widget
