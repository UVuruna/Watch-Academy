"""The Encyclopedia — the article browser, on three levels.

Home (nine wholes) -> Themes (one whole's cards) -> Article (the page
slider with its variant switcher). Owner rework, Session 27, sealed
2026-07-28; the old single 2,766-line module split into this package the
same round (root Rule #20). The home screen grew from six wholes to nine
in Session 35 (2026-07-29) — a reseating, not a rework.

The public surface is the dialog and the topic table — everything else
is internal to the package:

    from app.encyclopedia import EncyclopediaDialog

Documentation: ___encyclopedia.md.
"""

from app.encyclopedia.dialog import EncyclopediaDialog
from app.encyclopedia.tree import topics

__all__ = ["EncyclopediaDialog", "topics"]
