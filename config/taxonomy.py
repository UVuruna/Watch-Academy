"""The ONE hierarchy (RESTRUCTURE.md, owner-sealed 2026-07-22).

Five categories → groups → themes. The Encyclopedia halls, the Settings
panels and the `assets/` tree all mirror THIS module — halls/groups are
edited here, in one table, and read everywhere else.

Layer: config (pure — no Qt, no wall clock). Documentation:
config/taxonomy.md.
"""

from config import paths

# --- The five categories -----------------------------------------------------
# key -> display; the roots of the whole hierarchy.
CATEGORIES = {
    "calendars": "Calendars",      # the Dozens (12 + 13th)
    "weeks": "Weeks",              # every weekday theme
    "archetypes": "Archetypes",    # the pointer archetypes
    "celestial": "Celestial",      # sky mechanics: sun/moon/seasons/eclipses/eras/earth
    "instrument": "Instrument",    # dial furniture (outside the encyclopedia mirror)
}

# --- Category 2 (weeks) groups (owner-approved, balanced) --------------------
# group key -> (display, ordered theme-folder tuple). The theme FOLDER
# names are the on-disk register-parent folders (post-rename): the
# encyclopedia topic keys may differ where one folder carries several
# register-topics (bible → bible/bible_ii/bible_dark, creeds →
# creeds/ancient_religions).
WEEK_GROUPS = {
    "celestial_bodies": ("Celestial bodies",
                         ("planets", "cosmos", "continents")),
    "myth": ("Mythologies",
             ("greek", "norse", "egypt", "slavic",
              "age_of_heroes", "celestial_court")),
    "faith": ("Faith", ("bible", "creeds")),
    "crafts": ("Cultures & crafts",
               ("alchemy", "japan", "profession", "corporate")),
    "societies": ("Animal societies", ("wolf", "bee", "elephant")),
    "inner_wheel": ("The Inner Wheel",
                    ("virtue", "sin", "mood", "intelligence")),
    "gaming": ("Gaming",
               ("wow_alliance", "wow_horde", "wow_evil",
                "cp_gangs", "cp_street", "cp_corpo")),
    "films": ("Films", ("sw_jedi", "sw_sith", "sw_dyad")),
}

# theme FOLDER name -> its group folder (derived; the reverse of the
# table above). `weeks_dir` uses it to place a theme-relative art path
# under assets/weeks/<group>/<theme>/...
THEME_TO_GROUP = {
    theme: group
    for group, (_display, themes) in WEEK_GROUPS.items()
    for theme in themes
}

# --- Theme-key renames (RESTRUCTURE §Theme Renames) --------------------------
# Old settings/code theme KEY -> new key (keys, folders, display aligned).
# `app.settings_store` applies this on load (external user data — the
# documented migration pattern, not a Rule-#6 shim). The renamed keys
# whose art shares a folder with another key resolve their folder via
# THEME_FOLDER below.
THEME_KEY_RENAMES = {
    "religion": "creeds",
    "religion_alt": "ancient_religions",
    "bible2": "bible_ii",
    # art-only themes (not yet code-wired) renamed on disk only:
    "monsters": "age_of_heroes",
    "chinese_myth": "celestial_court",
}

# Code theme KEY -> its on-disk FOLDER name (where key ≠ folder because
# several register-topics share one folder). Absent key => folder == key.
THEME_FOLDER = {
    "ancient_religions": "creeds",   # creeds/secondary register
    "bible_ii": "bible",             # bible/secondary register
    "bible_dark": "bible",           # bible/dark register
    "planet_signs": "planets",       # planets/signs look
    "planets_art": "planets",        # planets/art look
}


def theme_folder(theme: str) -> str:
    """The on-disk folder name for a code theme key."""
    return THEME_FOLDER.get(theme, theme)


def weeks_root() -> "paths.Path":
    return paths.assets_dir() / "weeks"


def weeks_dir(theme_folder_name: str) -> "paths.Path":
    """assets/weeks/<group>/<theme_folder> for a theme FOLDER name — the
    group is fixed by THEME_TO_GROUP. Raises for an unknown folder so a
    typo fails loudly rather than resolving to a ghost path."""
    group = THEME_TO_GROUP[theme_folder_name]
    return weeks_root() / group / theme_folder_name


def inner_wheel_dir() -> "paths.Path":
    return weeks_root() / "inner_wheel"
