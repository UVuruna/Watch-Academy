"""THE ARTICLE HTML VOCABULARY — prose in, rich text out.

Every string this program shows a reader as an ARTICLE is built here: a
hover legend, the Encyclopedia's reflowing page, a downloaded .txt's
paragraph split. The rules are the owner's and they are shared —
THE LEGEND BOLD LAW (the spine terms in plain bold, hex notes stripped),
THE HOVER TEASER LAW (a hover speaks its thesis, never the whole
article), the [[Subhead]] marker, the justified column, the LEARN MORE
footer.

They lived inside `render/compositor.py` — a 3,800-line painting module
— which is why `app/encyclopedia/reader.py` and `text.py` had to import
PRIVATE names out of the render layer to reuse them (findings L1 and L2
of the OOP audit, 2026-08-18: "the article-HTML vocabulary lives inside
a painting module, which is WHY L1 exists"). Here they are public names
in a module that is about TEXT, and the encyclopedia imports them the
ordinary way.

Nothing here paints, measures a widget or knows a window: it takes an
article's text and returns HTML.

Layer: render (no Qt widgets; `paths`/`asset_variants` only to embed an
image the article shows). Documentation: article_html.md.
"""

import html
import re

from config import defaults, encyclopedia_ui, palette, paths
from render.asset_variants import scaled_variant_file


def centered(*lines: str) -> str:
    """Tooltip rich text with CENTERED lines (owner spec — QToolTip
    left-aligns plain text). Every line keeps its full width — QToolTip
    would otherwise wrap long lines at its own narrow heuristic (owner
    bug report: "Dusk 21:01" broke onto a new line)."""
    return centered_html(*(html.escape(line) for line in lines))


def centered_html(*lines: str) -> str:
    """Centered tooltip from lines that are ALREADY safe HTML (ordinal
    superscripts etc.) — the caller escapes any free-form data. Each
    line is wrapped in a no-wrap div so it owns one full-width row."""
    body = "".join(
        f"<div style='white-space:nowrap'>{line if line else '&nbsp;'}</div>"
        for line in lines
    )
    return f"<div align='center'>{body}</div>"


def ordinal(n: int) -> str:
    """"9<sup>th</sup>" — the raised ordinal suffix of the hover rework
    (owner spec: the suffix rides above the line)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}<sup>{suffix}</sup>"


# THE LEGEND BOLD LAW (owner 2026-07-26, CUBE.md §Display and Legend
# Laws — supersedes the 2026-07-12 rainbow): the web's SPINE pops in the
# article prose in plain BOLD, nothing else — the virtues, the vices,
# the emotions/moods and the WEEKDAYS, the terms that bind the abstract
# figures together. Color words read plain. Hex notes like " (#F8E600)"
# never display. Rules are owner-tunable in defaults; matching runs
# over the shipped ORIGINALS (English + Serbian) — machine-translated
# languages read plain.
HEX_NOTE = re.compile(r"\s*\(#[0-9A-Fa-f]{6}\)")
_TERM_RULES = [
    re.compile(
        rf"\b(?:{'|'.join(encyclopedia_ui.LEGEND_TERM_PATTERNS[category])})\b",
        re.IGNORECASE,
    )
    for category in ("virtue", "vice", "mood", "weekday")
]


def highlight_terms(escaped: str) -> str:
    """Wrap every spine term of an ESCAPED prose line in plain bold
    (the markup the rules insert never re-matches a rule)."""
    for pattern in _TERM_RULES:
        escaped = pattern.sub(
            lambda match: f"<b>{match.group(0)}</b>", escaped
        )
    return escaped


# Subheadings (owner 2026-07-14): article paragraphs may open with a
# [[Subhead]] marker from the FIXED vocabulary — rendered as a bold
# heading line, translated through the ui catalog.
SUBHEAD = re.compile(r"^\[\[(.+?)\]\]\s*")


def teaser(text: str) -> str:
    """THE HOVER TEASER LAW (owner 2026-07-26, CUBE.md §Display and
    Legend Laws): an article hover speaks only its THESIS — the first
    `LEGEND_TEASER_SENTENCES` of the first paragraph — never the whole
    article; the full text lives in the Encyclopedia (the LEARN MORE /
    SPACE footer rides in `tooltip_at`). A leading [[Subhead]] marker
    is dropped with the rest of the body."""
    first = text.split("\n\n", 1)[0]
    first = SUBHEAD.sub("", first).strip()
    sentences = re.split(r"(?<=[.!?])\s+", first)
    keep = encyclopedia_ui.LEGEND_TEASER_SENTENCES
    if len(sentences) <= keep and first == text.strip():
        return first
    return " ".join(sentences[:keep]).rstrip() + " …"


def learn_more_footer(tr) -> str:
    """THE HOVER TEASER LAW's footer (owner 2026-07-26 + the clickable
    amendment): every hover that owns an Encyclopedia page closes with
    a separated, underlined LEARN MORE link — the popup routes its
    click to the SAME jump SPACE makes — plus the SPACE hint for those
    who know it."""
    return (
        "<hr/><div align='center'>"
        f"<a href='domy:encyclopedia' "
        f"style='color:{palette.LEGEND_MORE_LINK_COLOR}'>"
        f"<u>{html.escape(tr('Learn more'))}</u></a>"
        f"&nbsp;&nbsp;<span style='color:{palette.LEGEND_MORE_HINT_COLOR}'>"
        f"{html.escape(tr('press SPACE'))}</span></div>"
    )


def article_paragraphs(text: str, tr=None) -> str:
    """The bare JUSTIFIED paragraphs of an article (owner 2026-07-13
    round two — clean edges on both sides, like a book column): the
    spine terms bolded (THE LEGEND BOLD LAW above), hex notes
    stripped, [[Subhead]] markers drawn as bold headings (owner
    2026-07-14; `tr` localizes the label). The caller provides the
    width-constrained cell."""
    text = HEX_NOTE.sub("", text)
    parts = []
    for p in text.split("\n\n"):
        match = SUBHEAD.match(p)
        body_style = ""
        if match:
            label = match.group(1)
            if tr is not None:
                label = tr(label)
            # CENTERED, hugging its own paragraph (owner 2026-07-14
            # round two: the gap above must beat the gap below).
            parts.append(
                "<p align='center' style='"
                f"margin-top:{encyclopedia_ui.ARTICLE_SUBHEAD_GAP_ABOVE_PX}px;"
                f"margin-bottom:{encyclopedia_ui.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'>"
                f"<b>{html.escape(label)}</b></p>"
            )
            p = p[match.end():]
            body_style = (
                f" style='margin-top:"
                f"{encyclopedia_ui.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'"
            )
        parts.append(
            f"<p align='justify'{body_style}>"
            f"{highlight_terms(html.escape(p))}</p>"
        )
    return "".join(parts)


def article_body_html(text: str, tr=None) -> str:
    """One article as a single fixed-width column: the paragraphs
    reflow inside the declared table cell (the legend popup measures
    the document and honors this width)."""
    return (
        f"<table><tr><td width='{encyclopedia_ui.ARTICLE_TEXT_WIDTH_PX}'>"
        f"{article_paragraphs(text, tr)}</td></tr></table>"
    )


def hover_title(text_html: str) -> str:
    """A hover TITLE line (owner 2026-07-13 round two): bigger and
    bold, centered — the phase name, the Ascendant word, the season
    and turning-point names all wear it."""
    return (
        f"<div align='center'><span style='font-size:"
        f"{encyclopedia_ui.ARTICLE_TITLE_PX}px; font-weight:bold'>"
        f"{text_html}</span></div>"
    )


def article_html(
    image, title_html: str | None, text: str, tr=None,
) -> str:
    """One ARTICLE hover: the entity's art on top (larger and
    clearer than on the dial — owner EXTRAS; a TUPLE draws the images
    side by side — the dual Sunday's two plates, owner 2026-07-13), an
    optional centered title line, then the article's TEASER (THE HOVER
    TEASER LAW — never the whole text; the Encyclopedia holds it)."""
    parts = []
    images = image if isinstance(image, tuple) else (image,)
    tags = "".join(
        f"<img src='"
        f"{scaled_variant_file(img, 2 * encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX).as_uri()}' "
        f"width='{encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX}'/>"
        for img in images
        if img is not None and paths.art_file(img).exists()
    )
    if tags:
        parts.append(f"<div align='center'>{tags}</div>")
    if title_html is not None:
        parts.append(f"<div align='center'>{title_html}</div><br/>")
    parts.append(article_body_html(teaser(text), tr))
    return "".join(parts)


def hover_badge(path) -> str:
    """The emblem above an arm hover (owner 2026-07-13: the trinity,
    season and turning-point badges ride their tooltips) — empty when
    the art is missing."""
    if path is None or not paths.art_file(path).exists():
        return ""
    small = scaled_variant_file(path, 2 * defaults.HOVER_BADGE_WIDTH_PX)
    return (
        f"<div align='center'><img src='{small.as_uri()}' "
        f"width='{defaults.HOVER_BADGE_WIDTH_PX}'/></div>"
    )
