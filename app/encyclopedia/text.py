"""The Encyclopedia's TEXT resolution — prose in, HTML out.

Four functions, all pure of widgets: the article ref -> text lookup, the
entry -> display name lookup, the reflowing article HTML and the image
tooltip. They were methods on the old dialog class; nothing about them
needed a window, and the reader, the download path and the tests all
want them, so they moved out here (Rule #5).

Layer: app. Documentation: text.md.
"""

import html as _html
from pathlib import Path

from config import defaults
from render.compositor import _HEX_NOTE, _SUBHEAD, _highlight_terms


def flow_html(text: str, tr=None) -> str:
    """Article prose that REFLOWS with the window (owner 2026-07-13: the
    paragraphs span the block and re-wrap live) — no fixed character
    wrap; QLabel's word wrap fills the width. The spine terms bolded
    (THE LEGEND BOLD LAW, owner 2026-07-26), hex notes stripped,
    JUSTIFIED like the legend, and [[Subhead]] markers drawn as bold
    headings (owner 2026-07-14; `tr` localizes the label)."""
    text = _HEX_NOTE.sub("", text)
    parts = []
    for paragraph in text.split("\n\n"):
        match = _SUBHEAD.match(paragraph)
        body_style = ""
        if match:
            label = match.group(1)
            if tr is not None:
                label = tr(label)
            # CENTERED, hugging its own paragraph (owner 2026-07-14
            # round two — same rule as the hover legends).
            parts.append(
                "<p align='center' style='"
                f"margin-top:{defaults.ARTICLE_SUBHEAD_GAP_ABOVE_PX}px;"
                f"margin-bottom:{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'>"
                f"<b>{_html.escape(label)}</b></p>"
            )
            paragraph = paragraph[match.end():]
            body_style = (
                f" style='margin-top:"
                f"{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'"
            )
        parts.append(
            f"<p align='justify'{body_style}>"
            + _highlight_terms(_html.escape(paragraph))
            + "</p>"
        )
    return "<div>" + "".join(parts) + "</div>"


def image_tooltip(path: Path) -> str:
    """IMAGE HOVER (owner spec, round R3: "posebno vazno kod onih gde
    ima više slika" — critical on multi-image pages like the era
    calendars): the filename stem, underscores opened to spaces. Stems
    already carrying a real capital somewhere (Byzantine, KaliYuga,
    Solar_Total) are left as drawn — a bare lowercase stem (sigma,
    swarm) is Title-Cased so every tooltip reads as a name, not a raw
    file token."""
    stem = path.stem.replace("_", " ")
    return stem.title() if stem.islower() else stem


def article_text(ref: tuple, symbolism, encyclopedia, tr=None) -> str:
    """The prose behind one entry's article ref — the ONE resolver every
    surface reads through (the page, the Download file, the tests)."""
    kind = ref[0]
    if kind == "verses":
        # The Four Greetings stay SERBIAN in every language (owner
        # 2026-07-14) — verses, their reading, then the watchmaker's
        # commentary.
        return "\n\n".join((
            ref[1]["verses"], ref[1]["explanation"], ref[1]["commentary"],
        ))
    if kind == "guide":
        # THE GUIDE carries its prose INLINE (the help book's own
        # captions.json, already localized by the builder) — the same
        # inline-data path the Four Greetings use.
        return ref[1]
    if kind == "article":
        return symbolism.article(ref[1], ref[2])["base"]
    if kind == "article_face":
        # The GOOD/EVIL split pages (owner verdict A, round R3b item 1):
        # ref = ("article_face", article_set, body, face) — resolves
        # through the SAME "faces" register the dial hover reads,
        # falling back to "base" for a theme whose split has not landed
        # (documented graceful path, Rule #1 — never a KeyError).
        node = symbolism.article(ref[1], ref[2])
        return node.get("faces", {}).get(ref[3]) or node["base"]
    if kind == "zodiac":
        return symbolism.zodiac_article(ref[1])["base"]
    if kind == "chinese":
        return symbolism.chinese_article(ref[1])["base"]
    if kind == "element":
        return symbolism.chinese_element(ref[1])["base"]
    if kind == "week":
        return encyclopedia.week(ref[1])["base"]
    if kind == "instrument":
        return encyclopedia.instrument(ref[1])["base"]
    if kind == "season":
        return encyclopedia.season(ref[1])["base"]
    if kind == "sun":
        return encyclopedia.sun(ref[1])["base"]
    if kind == "moon":
        return encyclopedia.moon(ref[1])["base"]
    if kind == "era":
        return encyclopedia.era(ref[1])["base"]
    if kind == "eclipse":
        return encyclopedia.eclipse(ref[1])["base"]
    if kind == "emblem":
        return encyclopedia.entry(ref[1], ref[2])["base"]
    if kind == "theme_title":
        return encyclopedia.theme_title(ref[1])["base"]
    if kind == "week_duality":
        return encyclopedia.week_duality(ref[1])["base"]
    return symbolism.trio_article(ref[1])["base"]


_DATABASE_TITLES = {
    "week_title": "week",
    "season_title": "season",
    "sun_title": "sun",
    "moon_title": "moon",
    "era_title": "era",
    "eclipse_title": "eclipse",
    "theme_title": "theme_title",
    "week_duality_title": "week_duality",
}


def entry_name(entry: dict, symbolism, encyclopedia, tr) -> str:
    """An entry's display name — THE ONE BUILD POINT (owner round R8b
    item 8: "Selene — Monday", every weekday-figure title shows its day;
    "encyclopedia builds titles centrally, do it at the ONE build
    point"): the database-titled pages take their titles from the
    encyclopedia database (localized there); everything else translates
    through the UI overlay. A `"weekday"` key on `entry` (set by the
    body/good/evil builders — never the title pages or the Ninth, which
    sits OUTSIDE the weekday, CANON.md) appends " — {Weekday}" here and
    ONLY here, so no other call site needs to know the convention
    exists."""
    name = entry["name"]
    if isinstance(name, tuple):
        # The tuple's head names the database section (the old
        # if/elif ladder, one table now — Rule #5); anything else is an
        # instrument article, which is what the ladder's `else` was.
        section = _DATABASE_TITLES.get(name[0], "instrument")
        base = getattr(encyclopedia, section)(name[1])["title"]
    else:
        base = tr(name)
    weekday = entry.get("weekday")
    if weekday:
        return f"{base} — {tr(weekday)}"
    return base
