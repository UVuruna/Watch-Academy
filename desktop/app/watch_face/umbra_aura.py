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

from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.watch_face import thumbs
from app.watch_face.controls import picture_group
from config import umbra

_FORM_BLURBS = {
    "fine": "Sixteen shade steps — the smoothest ladder, and the busiest.",
    "coarse": "Thirteen wider steps, so each shade band reads on its own.",
    "gradient": "No steps at all — one continuous sweep of shade.",
}


def build(settings, setters: dict, tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(picture_group(
        tr("Umbra form"),
        tr("How the shade ladder around the dial is stepped."),
        [
            (
                form, tr(title), tr(_FORM_BLURBS[form]),
                thumbs.umbra_icon(form, settings.umbra_contrast),
            )
            for form, title in (
                ("fine", "Fine (16 shades)"), ("coarse", "Coarse (13 shades)"),
                ("gradient", "Gradient"),
            )
        ],
        settings.umbra_form, setters["umbra_form"],
    ))
    layout.addWidget(picture_group(
        tr("Contrast"),
        tr("How far apart the lightest and darkest shades stand."),
        [
            (
                variant, tr(f"{variant.capitalize()} contrast"),
                tr("The umbra ladder at {variant} contrast, previewed under "
                   "the active form.").format(variant=variant),
                thumbs.umbra_icon(settings.umbra_form, variant),
            )
            for variant in umbra.UMBRA_CONTRAST_VARIANTS
        ],
        settings.umbra_contrast, setters["umbra_contrast"],
    ))
    widget = QWidget()
    widget.setLayout(layout)
    return widget
