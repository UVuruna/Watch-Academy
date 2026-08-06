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

from config import constants, dial, pantheon

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
        "crown_face": load_choice(
            raw, "crown_face", tuple(dial.NUMERAL_OUTER_FACES),
            dial.CROWN_FACE_DEFAULT,
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


def load_choice(raw: dict, key: str, allowed: tuple, default: str) -> str:
    """A closed-vocabulary field: absent = the default; anything outside
    the vocabulary is corrupt (never a quiet fallback — a settings file
    naming a roster face that no longer exists must say so)."""
    value = str(raw.get(key, default))
    if value not in allowed:
        raise ValueError(f"{key} {value!r} unknown (known: {list(allowed)})")
    return value


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
    if value not in constants.EARTH_LABEL_MODES:
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
        for pointer in constants.POINTER_POINTS
        for style in constants.PALETTE_STYLES
    }
    palettes: dict = {}
    for key, hues in raw.items():
        if key not in valid_keys:
            raise ValueError(f"palettes key {key!r} unknown")
        pointer = key.rsplit("_", 1)[0]
        if len(hues) != constants.POINTER_POINTS[pointer]:
            raise ValueError(
                f"palettes[{key!r}] needs {constants.POINTER_POINTS[pointer]} hues"
            )
        for hue in hues:
            if not _HEX_COLOR.match(str(hue)):
                raise ValueError(f"palettes[{key!r}] bad color {hue!r}")
        palettes[key] = tuple(str(hue).upper() for hue in hues)
    return palettes
