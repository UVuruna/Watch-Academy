"""Umbra & Aura section (see umbra_aura.md) — the umbra FORM pills
(Fine/Coarse/Gradient) and CONTRAST pills, moved verbatim from
`design_window.DesignDialog._umbra_tab`. Coloring lives in the Colors
section and opacity in the Opacity section (both later phases) — this
page carries only the form/contrast choice.
"""

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from app.watch_face.widgets import pill
from config import constants


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    # Named groups (design pass 2026-08-06): two bare pill rows read as
    # anonymous buttons — the user could not tell WHICH aspect of the
    # umbra either row controls.
    form_group = QGroupBox(tr("Umbra form"))
    form_row = QHBoxLayout(form_group)
    for form, title in (
        ("fine", "Fine (16 shades)"), ("coarse", "Coarse (13 shades)"),
        ("gradient", "Gradient"),
    ):
        form_row.addWidget(pill(
            tr(title), settings.umbra_form == form,
            lambda f=form: setters["umbra_form"](f),
        ))
    layout.addWidget(form_group)
    contrast_group = QGroupBox(tr("Contrast"))
    contrast_row = QHBoxLayout(contrast_group)
    for variant in constants.UMBRA_CONTRAST_VARIANTS:
        contrast_row.addWidget(pill(
            tr(f"{variant.capitalize()} contrast"),
            settings.umbra_contrast == variant,
            lambda v=variant: setters["umbra_contrast"](v),
        ))
    layout.addWidget(contrast_group)
    widget = QWidget()
    widget.setLayout(layout)
    return widget
