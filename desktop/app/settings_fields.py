"""Field validators and stored-data migrations for `app.settings_store`.

Split out under THE STRUCTURE LAW: the settings module was holding two
responsibilities at once — the `Settings` TABLE plus its atomic file I/O,
and the per-field validation/migration rules every stored key passes
through. This file is the second of those: one small validator per field
SHAPE (a bool that must really be a JSON bool, a scale inside its range,
an opacity override, a `#RRGGBB` hex, a custom palette), plus the
external-data migrations that let a settings file written by an older
release load clean instead of reading as corrupt.

Nothing here knows the settings FILE exists; everything takes the raw
parsed dict and answers with a validated value, raising `ValueError` on
anything a hand edit could have broken (Rule #1: errors must be visible,
never silently defaulted).
"""

import re

from config import constants, dial, eras, pantheon, pointer_geometry
from data.locations import Place, default_place, place_from_mapping

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def load_numerals(raw: dict) -> dict:
    """The LIVE NUMERAL BANDS' own settings (ring_rework.md §5 +
    hour_numerals.md §8) as `Settings` kwargs.

    Every key defaults to its SETTLED value, so a file written before
    this round loads clean — an absent key is the ledger's default, an
    out-of-range or unknown one is corrupt and says so. The rosters and
    ranges are `config.dial`'s, never repeated here."""
    return {
        "numeral_outer_size": int(load_scale(
            raw, "numeral_outer_size", *dial.NUMERAL_SIZE_RANGE,
            dial.NUMERAL_OUTER_SIZE_DEFAULT,
        )),
        # One-release migration (MINUTES naming sweep, owner ruling
        # 2026-08-06): the old "numeral_inner_size"/"numeral_inner_face"
        # keys are read as the fallback default when the new keys are
        # absent.
        "minutes_size": int(load_scale(
            raw, "minutes_size", *dial.NUMERAL_SIZE_RANGE,
            load_scale(
                raw, "numeral_inner_size", *dial.NUMERAL_SIZE_RANGE,
                dial.MINUTES_SIZE_DEFAULT,
            ),
        )),
        "numeral_outer_ring_size": load_scale(
            raw, "numeral_outer_ring_size",
            *dial.NUMERAL_OUTER_RING_SIZE_RANGE,
            dial.NUMERAL_OUTER_RING_SIZE_DEFAULT,
        ),
        "numeral_face": load_choice(
            raw, "numeral_face", tuple(dial.NUMERAL_OUTER_FACES),
            dial.NUMERAL_OUTER_FACE_DEFAULT,
        ),
        "minutes_face": (
            load_choice(
                raw, "minutes_face", tuple(dial.MINUTES_FACES),
                dial.MINUTES_FACE_DEFAULT,
            ) if "minutes_face" in raw else
            load_choice(
                raw, "numeral_inner_face", tuple(dial.MINUTES_FACES),
                dial.MINUTES_FACE_DEFAULT,
            )
        ),
        "numeral_seating": load_choice(
            raw, "numeral_seating", dial.NUMERAL_SEATINGS,
            dial.NUMERAL_SEATING_DEFAULT,
        ),
        "numeral_relief": load_choice(
            raw, "numeral_relief", dial.NUMERAL_RELIEF_STYLES,
            dial.NUMERAL_RELIEF_DEFAULT,
        ),
        "numeral_depth": load_scale(
            raw, "numeral_depth", *dial.NUMERAL_DEPTH_RANGE,
            dial.NUMERAL_DEPTH_DEFAULT,
        ),
        "numeral_light": load_choice(
            raw, "numeral_light", dial.NUMERAL_LIGHTS,
            dial.NUMERAL_LIGHT_DEFAULT,
        ),
        "numeral_darkness": load_scale(
            raw, "numeral_darkness", *dial.NUMERAL_DARKNESS_RANGE,
            dial.NUMERAL_DARKNESS_DEFAULT,
        ),
        "numeral_contact_blur": load_scale(
            raw, "numeral_contact_blur", *dial.NUMERAL_CONTACT_BLUR_RANGE,
            dial.NUMERAL_CONTACT_BLUR_DEFAULT,
        ),
        "numeral_border": load_scale(
            raw, "numeral_border", *dial.NUMERAL_BORDER_RANGE,
            dial.NUMERAL_BORDER_DEFAULT,
        ),
        "crown_time_format": load_choice(
            raw, "crown_time_format", dial.CROWN_TIME_FORMATS,
            dial.CROWN_TIME_FORMAT_DEFAULT,
        ),
    }


def save_numerals(settings) -> dict:
    """The same keys on the way out — one list, so a field can never be
    loaded and then silently not saved."""
    return {
        key: getattr(settings, key) for key in load_numerals({})
    }


def load_moving_bodies(raw: dict) -> dict:
    """THE MOVING BODIES' eight menus (owner verdict 2026-08-10) as
    `Settings` kwargs, read straight off `constants.MOVING_BODY_MENUS`
    — the ONE roster the controller and the Watch Face section also
    read. Written as a roster walk rather than one hand-copied
    `load_choice` block per menu: the seven blocks it replaces pushed
    `settings_store` over THE STRUCTURE LAW's threshold, and a menu
    added to the roster now reaches storage with no edit here at all."""
    return {
        name: load_choice(raw, name, choices, default)
        for name, (choices, default) in constants.MOVING_BODY_MENUS.items()
    }


def save_moving_bodies(settings) -> dict:
    """The same eight menus on the way OUT — the mirror of
    `load_moving_bodies`, walking the same roster so a stored file can
    never carry a menu the loader does not read back."""
    return {
        name: getattr(settings, name) for name in constants.MOVING_BODY_MENUS
    }


def load_place(raw: dict) -> Place:
    """THE STORED LOCATION, and its migration (owner decree 2026-08-16).

    Every settings file ever written — by this version and by every
    version before it — arrives here, and goes through the ONE door
    `place_from_mapping`, which answers with a whole place or with
    nothing. An absent `location` block (a file older than the picker)
    and a location whose parts contradict each other land on the SAME
    repair: the Belgrade preset, whole. A location whose only fault is
    a path naming another city keeps its name, coordinates and zone and
    has the real path looked up for it — that is the owner's own live
    file, whose 44.82 / 20.46 / Europe/Belgrade were always right while
    the stored path said Burundi.

    TWO FAULTS, TWO ANSWERS — the distinction is who wrote the fault:

    - OURS: an absent block, or a whole place whose stored PATH names
      another city. This app wrote that into an otherwise valid file,
      and refusing to start over our own defect would punish the user
      for it. Repaired silently.
    - THEIRS: a location block that is PRESENT but not a usable place —
      a latitude of 200, an unknown IANA zone, a missing coordinate.
      That is a hand edit or a damaged file, and it is surfaced LOUDLY
      (Rule #1, no error masking) exactly as it was before this round.
      Quietly resetting someone's location to Belgrade because their
      file said 200 would be the masking that rule forbids."""
    stored = raw.get("location")
    if stored is None:
        return default_place()             # a file older than the picker
    place = place_from_mapping(stored)
    if place is None:
        raise ValueError(f"location is not a usable place: {stored!r}")
    return place


def place_json(place: Place) -> dict:
    """A place on its way to disk. The ONE writer of a location block —
    so the five keys can never again be written from five different
    sources, which is how "BELGRADE BURUNDI" was saved
    (`data.locations.Place`)."""
    return {
        "name": place.name,
        "path": list(place.path),
        "latitude": place.latitude,
        "longitude": place.longitude,
        "timezone": place.timezone,
    }


def jump_place(entry: object) -> Place:
    """One stored Quick Jump city, whole or not at all.

    Succeeded `normalized_jump_city`, which validated the same four
    values field by field and handed back a dict. It is gone: the
    wholeness rule now lives in `place_from_mapping`, and two validators
    for one fact is the shape of defect this round removed. Still raises
    where the HOME location repairs — an incoherent home location was
    this app's own bug, a hand-edited jump entry is not (Rule #1)."""
    place = place_from_mapping(entry)
    if place is None:
        raise ValueError(f"jump city is not a usable place: {entry!r}")
    return place


def load_choice(raw: dict, key: str, allowed: tuple, default: str) -> str:
    """A closed-vocabulary field: absent = the default; anything outside
    the vocabulary is corrupt (never a quiet fallback — a settings file
    naming a roster face that no longer exists must say so)."""
    value = str(raw.get(key, default))
    if value not in allowed:
        raise ValueError(f"{key} {value!r} unknown (known: {list(allowed)})")
    return value


def load_world_mode(raw: dict) -> str:
    """The world mode, with the one-time rename of 2026-08-13.

    The two modes used to be called `geocentric` and `heliocentric`, and
    those names said the OPPOSITE of what the modes did (see
    `config.dial.WORLD_MODES`). They are now named for their behaviour —
    `noon_up` and `sky_up` — and an older settings file is translated
    here rather than reset: the owner's standing order is that a rename
    goes all the way and never throws his own setting away on the way.
    A legacy key maps to the mode that BEHAVES the same, not to the one
    whose word matches."""
    value = raw.get("world_mode")
    if isinstance(value, str) and value in dial.WORLD_MODE_LEGACY_KEYS:
        return dial.WORLD_MODE_LEGACY_KEYS[value]
    return load_choice(
        raw, "world_mode", dial.WORLD_MODES, dial.WORLD_MODE_DEFAULT,
    )


def load_rotation_group(raw: dict) -> str:
    """The rotation dropdown value — with the one-time migration from
    the pre-2026-07-14 Enabled checkbox (external user data: enabled
    meant the checked list, i.e. today's "custom")."""
    value = raw.get("theme_rotation_group")
    if value is None:
        return "custom" if raw.get("theme_rotation") is True else "none"
    value = str(value)
    allowed = {"none", "custom"} | {
        title for title, _ in pantheon.WEEKDAY_MENU_GROUPS
    }
    if value not in allowed:
        raise ValueError(f"theme_rotation_group {value!r} unknown")
    return value


def load_bool(raw: dict, key: str, default: bool) -> bool:
    """A REAL JSON boolean or absent — a hand-edited "false" string
    would otherwise coerce to True silently (review finding; Rule #1:
    errors must be visible)."""
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} {value!r} is not true/false")
    return value


def load_earth_label(raw: dict) -> str:
    """The Earth marker's label enum (owner 2026-07-18, ROADMAP 15h):
    the new `earth_label` key wins outright when present; otherwise it
    is derived from the OLD bool pair (`show_earth_date`/`earth_weekday`,
    the latter falling back to the pre-rename `archetype_earth_day`
    key) — T,F -> "date"; F,T -> "weekday"; T,T -> "date_weekday" (the
    old combined "Full Date" meaning, before "full" meant date+year);
    F,F -> "off". External user data migration, not an API shim
    (Rule #6 — the old bool pair no longer exists anywhere else)."""
    if "earth_label" in raw:
        value = str(raw["earth_label"])
    else:
        old_date = load_bool(raw, "show_earth_date", True)
        old_weekday = load_bool(
            raw, "earth_weekday", load_bool(raw, "archetype_earth_day", False)
        )
        if old_date and old_weekday:
            value = "date_weekday"
        elif old_date:
            value = "date"
        elif old_weekday:
            value = "weekday"
        else:
            value = "off"
    if value not in eras.EARTH_LABEL_MODES:
        raise ValueError(f"earth_label {value!r} unknown")
    return value


def load_scale(raw: dict, key: str, low: float, high: float, default: float) -> float:
    """Size multiplier: absent = the default; out of range = corrupt."""
    value = float(raw.get(key, default))
    if not low <= value <= high:
        raise ValueError(f"{key} {value} outside {low}..{high}")
    return value


def load_alpha(raw: dict, key: str) -> float | None:
    """Opacity override: null/absent = use the skin's own value."""
    value = raw.get(key)
    if value is None:
        return None
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{key} {value} outside 0..1")
    return value


def load_hex(raw: dict, key: str) -> str | None:
    """A `#RRGGBB` override or None — the SAME validation `ring_tint`
    has always run inline (Watch Face Phase 4: shared here so the four
    new tint overrides do not each repeat it, Rule #5)."""
    value = raw.get(key)
    if value is None:
        return None
    value = str(value).upper()
    if not _HEX_COLOR.match(value):
        raise ValueError(f"{key} {value!r} not #RRGGBB")
    return value


# The wheel slots as they were named before 2026-07-28, mapped onto
# their positional successors. Read by the settings migration above —
# one table, so a stored file and a stored palette key cannot disagree.
RETIRED_SLOTS = {"paint": "primary", "light": "secondary", "cube": "tertiary"}

# Calendar mounts that MERGED into another (owner ruling 2026-08-05): the
# Vices are the Virtue Wheel's own paint face, one theme in two
# depictions, so a settings file that still selects the retired key lands
# on the wheel that absorbed it instead of failing validation and
# offering the user a reset. The documented external-data migration
# pattern — never a Rule-#6 shim.
MERGED_MOUNTS = {"vices": "virtues"}

# Slot MODES that were renamed, mapped onto the name in force today.
# "astrology" was a legal `weekday_slot` from 0.14.159 ("the weekday
# POSITION can now carry an astrology badge instead of the bodies —
# Bodies / Astrology / Ascendant"); the mode list later renamed it
# "zodiac" and nobody wrote the migration. Found 2026-08-16 in the
# OWNER'S OWN live settings file, which therefore read as corrupt on
# every launch and offered him a reset — the exact loss the comment on
# `RETIRED_SLOTS` above says this mechanism exists to prevent. Applied
# to all three slot keys because the rename is of the MODE, and the
# same vocabulary fills every slot.
RETIRED_SLOT_MODES = {"astrology": "zodiac"}


def migrate_palette_key(key: str) -> str:
    """"hexa_paint" -> "hexa_primary"; anything already positional (or
    unrecognizable) passes through untouched for the validator to
    judge."""
    pointer, _, slot = str(key).rpartition("_")
    if pointer and slot in RETIRED_SLOTS:
        return f"{pointer}_{RETIRED_SLOTS[slot]}"
    return key


def load_palettes(raw: dict) -> dict:
    """Custom palettes keyed "pointer_style"; every hue validated so a
    hand-edited color cannot detonate inside a paint pass."""
    if not isinstance(raw, dict):
        raise ValueError("palettes must be an object")
    valid_keys = {
        f"{pointer}_{style}"
        for pointer in pointer_geometry.POINTER_POINTS
        for style in constants.PALETTE_STYLES
    }
    palettes: dict = {}
    for key, hues in raw.items():
        if key not in valid_keys:
            raise ValueError(f"palettes key {key!r} unknown")
        pointer = key.rsplit("_", 1)[0]
        if len(hues) != pointer_geometry.POINTER_POINTS[pointer]:
            raise ValueError(
                f"palettes[{key!r}] needs {pointer_geometry.POINTER_POINTS[pointer]} hues"
            )
        for hue in hues:
            if not _HEX_COLOR.match(str(hue)):
                raise ValueError(f"palettes[{key!r}] bad color {hue!r}")
        palettes[key] = tuple(str(hue).upper() for hue in hues)
    return palettes
