"""THE VARIANT PANEL (owner ballot verdicts 3A + 8A, 2026-08-15).

His diagnosis on the ballot, which the code confirmed line for line:
"variant of a theme" was not one idea but FOUR scattered mechanisms —
(1) the Planets variants are separate registry keys, so the gallery
showed one card and hid the relatives; (2) the per-theme METAL was
chosen in combo boxes buried inside the Theme rotation group, and only
for themes that happened to be in the rotation; (3) the art SOURCE was
a group of its own; (4) the Pantheon/Planetary pair appeared and
vanished because it belonged to only some themes and had no permanent
seat. None of the four could see the other three.

Measured before writing a line: of the 34 registered themes, exactly
TWO — `planet_signs` and `planets_art` — are reachable from no picker
group at all. `planets_art` does not even carry a title. So the owner's
"the relatives are hidden" was not an impression; two of his themes had
no door.

**There is no settings migration, and that is deliberate.** A
`ThemeSelection` that became a new stored shape would have to rewrite
every existing profile. It does not need to: the coordinates (base,
style, metal, source, roster) already map onto keys the settings have
always held, so this module is a VIEW over them. Nothing on disk
changes, nothing can be lost in a rewrite, and a user who never opens
this panel keeps exactly the watch he had.

VERDICT 8A governs what the panel prints: a row with nothing to offer
is NOT printed at all — that is STRUCTURE, not state — while an option
that exists but cannot be taken right now is greyed with its reason in
a tooltip. That is the owner's own ruling on the ballot: grey it, or do
not write it at all.
"""

from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from app.ui_style import tooltip_wrap
from app.watch_face import theme_thumbs
from app.watch_face.controls import picture_group
from app.watch_face.widgets import flow_row, pill
from config import identity, pantheon, registry, ring
from config.registry.week import WEEK
from config.registry import week as week_registry

#: The style each `title_plate` look is called in front of a person.
#: The registry stores the FOLDER name; these are the words.
_STYLE_TITLES = {
    "photo": "Photo",
    "art": "Art",
    "sign": "Signs",
}


def family_members(theme: str) -> dict[str, str]:
    """The theme's whole family as {style: registry key}, in the
    registry's own order — themes that are the SAME entities in a
    different look.

    Kinship is DERIVED, never listed twice: two keys are relatives when
    they share an `articles` set (the same entities carry the same
    encyclopedia) and both declare a `title_plate` (the look they wear).
    A theme with no relatives answers a single-entry dict, and verdict
    8A then prints no Style row at all.
    """
    entry = WEEK.get(theme)
    if entry is None:
        return {}
    articles = entry.get("articles")
    plate = entry.get("title_plate")
    if not articles or not plate:
        return {theme: theme}
    members: dict[str, str] = {}
    for key, other in WEEK.items():
        if other.get("articles") != articles:
            continue
        other_plate = other.get("title_plate")
        if not other_plate:
            continue
        members[other_plate[-1]] = key
    return members


def style_title(style: str) -> str:
    """The word for a look — falling back to the folder name rather
    than inventing one, so a new look the owner adds shows up readable
    instead of not at all."""
    return _STYLE_TITLES.get(style, style.replace("_", " ").capitalize())


def build(active, settings, setters, tr) -> QWidget | None:
    """The permanent Variant panel for the ACTIVE SLOT's theme, or None
    when that theme has no variant of any kind to offer (verdict 8A:
    absent, not an empty box).

    `active` is the slot's `SlotDescriptor` — the panel varies THAT
    slot's theme, not a global one, which is the same thing the content
    tree beside it edits (a watch may wear a different theme per slot,
    and a panel that wrote a global key would silently retheme the
    wrong one)."""
    theme = active.theme_value
    rows = [
        row for row in (
            _style_row(theme, active, tr),
            _metal_row(theme, settings, setters, tr),
            _source_row(theme, settings, setters, tr, active.roster_value),
            _roster_row(theme, active, settings, tr),
        )
        if row is not None
    ]
    if not rows:
        return None
    group = QGroupBox(tr("Variant"))
    column = QVBoxLayout(group)
    # THE SENTENCE EARNS ITS BAND OR IT IS NOT PRINTED (ALG-7 ROW
    # OCCUPANCY, live-profile audit 2026-08-16). It explains that a row
    # with nothing to offer is hidden — which says something only when
    # there is more than one row to compare. On a theme that offers a
    # single row it became a half-empty text band stacked above another
    # half-empty one, with the cards continuing below: exactly the shape
    # the law's ladder answers at step 2, and the honest reflow here is
    # to stop printing a caption that carries no information.
    if len(rows) > 1:
        note = QLabel(tr(
            "What this theme can wear. A row it has nothing to offer is not "
            "shown at all."
        ))
        note.setWordWrap(True)
        column.addWidget(note)
    for row in rows:
        column.addWidget(row)
    return group


def _labelled(tr, title: str, members) -> QWidget:
    """One row: its name, then its pills, wrapping rather than running
    off the page (`flow_row` carries the uniform-width rule too)."""
    row = QWidget()
    layout = QVBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    caption = QLabel(tr(title))
    caption.setStyleSheet("font-weight: bold;")
    layout.addWidget(caption)
    layout.addWidget(flow_row(members))
    return row


def _style_row(theme, active, tr) -> QWidget | None:
    """PHOTO / ART / SIGNS — the row that gives `planet_signs` and
    `planets_art` a door at last. Picking a style stores the RELATIVE'S
    OWN registry key, which is why no migration is needed: the setting
    keeps holding exactly what it has always held.

    CARDS, not pills: these three ARE three pictures, and the owner's
    standing law is that a picker shows what it picks. The card group
    is the ordinary grammar (image, label, hover, resize)."""
    members = family_members(theme)
    if len(members) < 2:
        return None
    return picture_group(
        tr("Style"), "",
        [
            (
                key, tr(style_title(style)),
                tr("This theme's plates in the {style} look.").format(
                    style=tr(style_title(style)).lower()
                ),
                theme_thumbs.theme_style_icon(key),
            )
            for style, key in members.items()
        ],
        theme, lambda key: active.set_weekday(key),
    )


def _metal_row(theme, settings, setters, tr) -> QWidget | None:
    """THE METAL, out of its hiding place. It used to be a combo box
    inside the Theme rotation group — and only for themes that were in
    the rotation, so the same setting was reachable or not depending on
    an unrelated choice (verdict 5E moves it here and thins that group
    to what rotation actually is)."""
    if theme not in registry.METAL_THEMES:
        return None
    metals = ring.theme_metals(theme)
    if len(metals) < 2:
        return None
    current = settings.theme_metals.get(theme, "colored")
    row = _labelled(tr, "Metal", [
        pill(
            tr(metal.capitalize()), metal == current,
            lambda m=metal: setters["theme_metal"](theme, m),
        )
        for metal in metals
    ])
    if settings.theme_metal_follow_ring:
        # GREY WITH THE REASON, never hidden (verdict 8A's other half):
        # the metal still exists for this theme, it is simply not the
        # user's to pick while the ring colour is driving it.
        row.setEnabled(False)
        row.setToolTip(tooltip_wrap(tr(
            "Follow ring color is on, so the ring's colour picks the "
            "metal. Turn it off under Theme rotation to choose here."
        )))
    return row


def _source_row(theme, settings, setters, tr, roster: str) -> QWidget | None:
    """GEMINI / CHATGPT. The same measurement the Artwork group makes —
    one door, `theme_thumbs.theme_art_sources`, which answers nothing
    when every source resolves to the same plate on disk."""
    sources = theme_thumbs.theme_art_sources(theme)
    if len(sources) < 2:
        return None
    # CARDS, and the SAME composite the retired Artwork group drew:
    # one card per source carrying that source's Sun plate AND its
    # Sunday dual in one image. Folding Artwork into this panel must not
    # cost the owner the preview he asked for in the first place.
    apply_source = setters["art_source"]
    return picture_group(
        tr("Source"), "",
        [
            (
                source, tr(identity.ART_SOURCE_TITLES[source]),
                tr("The {source} cast of this theme's plates — its Sunday "
                   "dual included, when the theme carries one.").format(
                    source=identity.ART_SOURCE_TITLES[source]
                ),
                theme_thumbs.art_source_icon(source, theme, roster),
            )
            for source in sources
        ],
        settings.art_source, apply_source,
    )


def _roster_row(theme, active, settings, tr) -> QWidget | None:
    """PLANETARY / PANTHEON — the pair that used to appear and vanish.
    It is a variant of the theme like any other, so it has a permanent
    seat here; a theme that declares no pantheon block simply prints no
    row, which is the same rule every other row obeys."""
    if theme not in pantheon.WEEKDAY_PANTHEON:
        return None
    return _labelled(tr, "Roster", [
        pill(
            tr(roster.capitalize()), roster == active.roster_value,
            lambda r=roster: active.set_weekday(theme, roster=r),
        )
        for roster in week_registry.FIGURE_ROSTERS
    ])
