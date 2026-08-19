"""Previews ASSEMBLED FROM THE THEME'S OWN ART FILES — the Subdial
plate set card and the Artwork cards.

Split out of `thumbs.py` on 2026-08-15, when the Artwork rework carried
that module past THE STRUCTURE LAW's threshold. The boundary is
responsibility, not line count: everything left in `thumbs.py` is
COMPUTED — an icon this app PAINTS through the render vocabulary
(moon faces, eclipse plates, marker marks, swatches). Everything here
READS PLATES OFF DISK and composes them side by side in one tile, so
one card can show everything a pick actually brings. `art_thumbnail`
(the single-plate case) stays in `thumbs.py` because the computed
side uses it too; this module borrows it rather than keeping a copy.
"""

import hashlib
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap

from app.watch_face.thumbs import (
    THUMB_SOURCE_PX, _THUMB_CACHE_VERSION, _cache_dir, art_thumbnail,
)
from config import identity, paths
from render import raster_store


def subdial_set_icon(set_name: str) -> QIcon | None:
    """One Subdial plate SET's preview — the set's OWN three metal
    plates (gold | bronze | silver) side by side in one icon (owner
    order 2026-08-09: "slicicu kako izgleda taj odabir za sve 3
    verzije"). Sets 1-4 read their three hand-drawn files; the solo
    set's gold/bronze are DERIVED from its silver master through the
    same recolor door the dial itself uses (`render.asset_variants.
    subdial_plate_file` under a per-set display context) — computed,
    never invented. Missing art -> None (honest blank tile)."""
    from render.asset_variants import subdial_plate_file

    sources = []
    for finish in ("gold", "bronze", "silver"):
        try:
            with paths.display(paths.display_context(subdial_set=set_name)):
                resolved = subdial_plate_file(finish)
        except Exception:
            resolved = None
        if resolved is None or not Path(resolved).exists():
            return None
        sources.append(Path(resolved))
    digest = hashlib.sha1("|".join(
        raster_store.source_prefix(source) for source in sources
    ).encode("utf-8")).hexdigest()[:16]
    cache_path = (
        _cache_dir()
        / f"subdial_set_{set_name}_{digest}_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    slot = THUMB_SOURCE_PX // 3
    canvas = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    for index, source in enumerate(sources):
        image = QImage(str(source))
        if image.isNull():
            painter.end()
            return None
        scaled = image.scaled(
            slot, THUMB_SOURCE_PX,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(
            QPointF(
                index * slot + (slot - scaled.width()) / 2.0,
                (THUMB_SOURCE_PX - scaled.height()) / 2.0,
            ),
            scaled,
        )
    painter.end()
    try:
        raster_store.atomic_save(canvas, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(canvas))
    return QIcon(str(cache_path))


def _body_plate(source: str, theme: str, body: str = "sun") -> Path | None:
    """The theme's plate for `body` resolved UNDER `source`, with the
    dial's OWN fallback to the generic planetary plate when the theme
    has none there."""
    from datetime import date

    from config import pantheon

    with paths.display(paths.display_context(art_source=source)):
        candidate = paths.art_file(pantheon.weekday_theme_body_art(
            theme, body, on_date=date.today(),
        ))
        if candidate is None or not candidate.exists():
            candidate = paths.art_file(
                pantheon.weekday_theme_body_art("planets", body)
            )
    if candidate is None or not candidate.exists():
        return None
    return candidate


def _dual_plate(source: str, theme: str, roster: str) -> Path | None:
    """The theme's SUNDAY DUAL under `source` AND `roster`, when one is
    on disk. The roster half is not decoration: Planetary and Pantheon
    do not share a Sunday (owner report 2026-08-15), and the answer
    comes from `pantheon.weekday_dual_rel` — the same door the
    compositor asks, never a second copy of the rule."""
    from config import pantheon

    rel = pantheon.weekday_dual_rel(theme, roster)
    if rel is None:
        return None
    with paths.display(paths.display_context(art_source=source)):
        return paths.existing_art_file(pantheon.weekday_art(f"{rel}.png"))


def theme_art_sources(theme: str) -> tuple[str, ...]:
    """The art sources this theme ACTUALLY has distinct plates for.

    THE CHOICELESS ROW IS NOT PRINTED (owner ballot verdict 8A, and his
    2026-08-15 report on Planets Photo: "PLANETS PHOTO nema GEMINI i
    CHATGPT kao 2 verzije vec samo taj jedan — zasto onda ima
    ARTWORK"). A theme whose plates carry no `_gem`/`_gpt` suffix
    resolves to the SAME file under every source, so the picker was
    offering four ways to pick one picture. Measured off disk through
    the app's own resolver, never a hand-kept list: one entry back
    means there is nothing to choose and the caller prints nothing."""
    seen: dict = {}
    for source in identity.ART_SOURCES:
        plate = _body_plate(source, theme)
        if plate is None:
            continue
        seen.setdefault(str(plate), source)
    if len(seen) < 2:
        return ()
    return tuple(seen.values())


def art_source_icon(
    source: str, theme: str, roster: str = "planetary",
) -> QIcon | None:
    """ONE card per source, carrying EVERYTHING that source draws for
    Sunday — the plain Sun plate and, when the theme has one, the
    Sunday dual beside it in the SAME image.

    Owner order 2026-08-15: "artwork treba da ima 2 OPCIJE po principu
    SUBDIAL gde u jednoj slici ima prikazane sve 3 opcije". The picker
    used to spend four cards on two picks — a source card plus a
    separate dual card per source, all four keyed back to two settings
    — which read as four choices where there were two. `subdial_set_
    icon` above already had the grammar; this is the same composition
    (equal slots, each plate centred in its own, aspect kept)."""
    plates = [plate for plate in (
        _body_plate(source, theme), _dual_plate(source, theme, roster),
    ) if plate is not None]
    if not plates:
        return None
    return _compose(plates, "art_source")


def _compose(plates: list, name: str) -> QIcon | None:
    """Several plates side by side in ONE tile — equal slots, each plate
    centred in its own, aspect kept. The grammar `subdial_set_icon`
    established, shared so every multi-plate preview composes the same
    way rather than three near-copies drifting apart."""
    if not plates:
        return None
    if len(plates) == 1:
        return art_thumbnail(plates[0])
    digest = hashlib.sha1("|".join(
        raster_store.source_prefix(plate) for plate in plates
    ).encode("utf-8")).hexdigest()[:16]
    cache_path = (
        _cache_dir() / f"{name}_{digest}_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    slot = THUMB_SOURCE_PX // len(plates)
    canvas = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    for index, plate in enumerate(plates):
        image = QImage(str(plate))
        if image.isNull():
            painter.end()
            return art_thumbnail(plates[0])      # honest single, never blank
        scaled = image.scaled(
            slot, THUMB_SOURCE_PX,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(
            QPointF(
                index * slot + (slot - scaled.width()) / 2.0,
                (THUMB_SOURCE_PX - scaled.height()) / 2.0,
            ),
            scaled,
        )
    painter.end()
    try:
        raster_store.atomic_save(canvas, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(canvas))
    return QIcon(str(cache_path))


#: The two bodies a style preview shows. TWO, not one, because the Sun
#: alone misrepresented the Signs look: a Sun SIGN is a ring with a dot,
#: which at tile size reads as a placeholder icon rather than as art (an
#: independent grader called it exactly that, 2026-08-15). Saturn's
#: glyph is the most drawn of the seven, so the pair shows a sign look
#: as the lettering it is — and the SAME pair serves every style, so the
#: three tiles stay a fair comparison.
_STYLE_PREVIEW_BODIES = ("sun", "saturn")


def theme_style_icon(theme: str) -> QIcon | None:
    """One STYLE's preview for the Variant panel — the theme's own
    plates in that look, so Photo, Art and Signs show the three
    pictures they actually are rather than three words."""
    plates = [
        plate for plate in (
            _body_plate(identity.ART_SOURCE_DEFAULT, theme, body)
            for body in _STYLE_PREVIEW_BODIES
        )
        if plate is not None
    ]
    return _compose(plates, f"theme_style_{theme}")
