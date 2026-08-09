"""Umbra & Aura section (see umbra_aura.md) — the umbra FORM gallery
(Fine/Coarse/Gradient) and CONTRAST gallery, moved verbatim from
`design_window.DesignDialog._umbra_tab` and given PREVIEWS in the
2026-08-09 round (owner order: every picker shows what it picks): each
tile's icon is the REAL umbra algorithm at thumbnail scale
(`thumbs.umbra_icon` — the same ladder, spans and conical gradient the
dial's BackgroundLayer paints), so a form tile previews the form under
the ACTIVE contrast and a contrast tile previews the active form under
that contrast. Coloring lives in the Colors section and opacity in the
Opacity section — this page carries only the form/contrast choice.
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from app.watch_face import thumbs
from app.watch_face.widgets import flow_gallery, tile
from config import constants


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    form_group = QGroupBox(tr("Umbra form"))
    form_column = QVBoxLayout(form_group)
    form_column.addWidget(flow_gallery([
        tile(
            tr(title),
            thumbs.umbra_icon(form, settings.umbra_contrast),
            settings.umbra_form == form,
            lambda f=form: setters["umbra_form"](f),
        )
        for form, title in (
            ("fine", "Fine (16 shades)"), ("coarse", "Coarse (13 shades)"),
            ("gradient", "Gradient"),
        )
    ]))
    layout.addWidget(form_group)
    contrast_group = QGroupBox(tr("Contrast"))
    contrast_column = QVBoxLayout(contrast_group)
    contrast_column.addWidget(flow_gallery([
        tile(
            tr(f"{variant.capitalize()} contrast"),
            thumbs.umbra_icon(settings.umbra_form, variant),
            settings.umbra_contrast == variant,
            lambda v=variant: setters["umbra_contrast"](v),
        )
        for variant in constants.UMBRA_CONTRAST_VARIANTS
    ]))
    layout.addWidget(contrast_group)
    widget = QWidget()
    widget.setLayout(layout)
    return widget
