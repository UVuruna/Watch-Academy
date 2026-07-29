"""THE CONTINENTS theme family, split out of pantheon.py by the
Session 36 deterministic fallback (WORKPLAN-STRUCTURE.md): the
region roster, Earth art resolution and the day/night face
resolvers the Continents weekday theme and its Sunday dual use.

Layer: config — pure, no Qt, no wall clock.
"""

from pathlib import Path

from config import paths


_CONTINENTS = (
    "europe", "north_america", "south_america", "africa", "asia",
    "oceania",
    # The polar views (owner 2026-07-15: the Quick Jump flips the
    # planet onto its poles, so the marker follows).
    "north_pole", "south_pole",
)
# Beyond this |latitude| the Earth marker wears the POLE art instead of
# the continent's — high enough that ordinary cities keep their
# continent view, low enough that the pole jumps (±89.99°) and the far
# polar settlements honestly see the pole.
EARTH_POLE_LATITUDE = 75.0

# THE CONTINENTS weekday theme (owner-sealed matrix 2026-07-21). The six
# weekday bodies ride the six continents — the dial's OWN Earth-marker
# faces are the theme's bodies (owner exception to the one-image-one-
# place law, sealed). Body -> earth REGION stem (Sunday's "sun" is the
# Ruler pole; the Servant pole is the dual, below). Column assignments
# straight from the sealed matrix: Moon/Oceania, Mars/Europe, Mercury/
# Asia, Jupiter/Africa, Venus/South America, Saturn/North America.
EARTH_ART_DIR = paths.assets_dir() / "celestial" / "earth"
CONTINENTS_REGIONS = {
    "moon": "oceania",
    "mars": "europe",
    "mercury": "asia",
    "jupiter": "africa",
    "venus": "south_america",
    "saturn": "north_america",
    "sun": "south_pole",          # Antarctica — the Ruler face
}
CONTINENTS_DUAL_REGION = "north_pole"   # the Arctic — the Servant face
# The still frame the Encyclopedia gallery/theme picker previews with,
# and the plate baked into the skin as a fallback (the live dial
# overrides both axes at render — see continents_body_art): the owner's
# atmosphere globes lit by day.
CONTINENTS_PREVIEW_STYLE = "atmo"
# THE CONTINENTS TITLE IMAGE (owner-sealed matrix 2026-07-21): the flat
# world map — the whole Earth seen at once, the week's field before it is
# walked. Copied from UV/earth map.jpg into the earth family as a PNG
# (setup/convert step), the canonical home for the theme's own art; the
# Encyclopedia topic uses it for both the gallery card and the title page.
CONTINENTS_TITLE_IMAGE = EARTH_ART_DIR / "world.png"


def earth_face_art(style: str, region: str, phase: str = "day") -> Path:
    """One Earth-marker face on disk — the SAME `{style}_{region}_
    {phase}` naming the YearMarkerSpec variants use (Rule #5), reused as
    the Continents theme's body art (owner exception, sealed 2026-07-21).
    Pure path construction; existence is the caller's concern."""
    return EARTH_ART_DIR / f"earth_{style}_{region}_{phase}.png"


def continents_body_art(body: str, earth_style: str, is_daylight: bool) -> Path:
    """The live Continents body plate for one weekday `body` — the
    earth face for its region in the user's `earth_style` (atmo/clean,
    one setting for the whole instrument) at the sky's current phase
    (`is_daylight` from the render tick — the SAME sun-elevation law the
    Earth marker already computes, never recomputed here). The Sunday
    center resolves through "sun" -> south_pole; the Arctic Servant uses
    `continents_dual_art`."""
    region = CONTINENTS_REGIONS[body]
    return earth_face_art(earth_style, region, "day" if is_daylight else "night")


def continents_dual_art(earth_style: str, is_daylight: bool) -> Path:
    """The live Continents SERVANT plate — the Arctic (north_pole) face,
    the Antarctic Ruler's eternal antiphase mirror — in the user's
    `earth_style` at the sky's current phase (same law as
    `continents_body_art`)."""
    return earth_face_art(
        earth_style, CONTINENTS_DUAL_REGION, "day" if is_daylight else "night"
    )
