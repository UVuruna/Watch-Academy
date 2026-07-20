"""User runtime state: %APPDATA%/DOMY Watch/settings.json.

Deliberately plain JSON (inspectable, diffable, survives reinstall) and
the ONLY module that reads or writes the settings file. Writes are
atomic (tmp + os.replace). A corrupt file raises SettingsCorruptError —
the caller must surface it visibly (monorepo Rule #1), never reset
silently.
"""

import dataclasses
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

from config import constants, defaults
from data.rings import ring_presets, validate_preset

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class SettingsCorruptError(Exception):
    """The settings file exists but cannot be parsed/validated."""

    def __init__(self, path: Path, cause: Exception):
        super().__init__(f"Settings file is corrupt: {path} ({cause})")
        self.path = path
        self.cause = cause


@dataclass(frozen=True)
class Settings:
    schema_version: int = defaults.SETTINGS_SCHEMA_VERSION
    # None means "never positioned" — first run centers on the primary screen.
    window_x: int | None = None
    window_y: int | None = None
    diameter: int = defaults.DEFAULT_DIAL_DIAMETER
    click_through: bool = False
    # Visibility Z mode (owner 2026-07-17, ROADMAP 15d): "bottom" — the
    # clock stays below every window except the desktop (the default);
    # "top" — always on top of everything (the always-visible small
    # clock). The widget swaps the window flags; not a render setting.
    z_mode: str = "bottom"
    ring: str = "DOMY"                  # ring preset CARD name (bundled or custom)
    ring_tint: str | None = None        # #RRGGBB multiplying ring+hands+Umbra
    ring_finish: str = "gold"           # letter metals (triangle/12h rules)
    # The user's custom ring cards ({name, positions, letters}) — merged
    # with Database/ring_presets.json by data/rings.py.
    custom_rings: tuple = ()
    # THE METAL-SPLIT OPTION (TASK 3, MASON/ICONS round, owner verdicts
    # 2026-07-19, third batch): per-preset choice between the 3-3
    # two-metal split and one finish on all six, for every seal preset
    # that carries its own `triangle` override (Mason/Omega/Templar
    # today) — keyed by preset name, like `theme_metals` below. A
    # preset absent here falls back to `constants.RING_TWO_METALS_DEFAULT`
    # (`app.controller._ring_two_metals` resolves both).
    ring_two_metals: dict = field(default_factory=dict)
    # Install defaults per the owner's 2026-07-12 list: hexa paint,
    # gradient-dark Umbra, atmosphere Earth, STEEL hands, 720 dial.
    pointer: str = "hexa"
    umbra_form: str = "gradient"
    umbra_contrast: str = "dark"
    palette_style: str = "paint"       # on Calendar: paint = Zodiac wheel,
                                        # light = Almanac wheel
    calendar_lighting: str = "hour"     # Calendar lit wedge: "hour" (the
                                        # shichen) | "year" (month/sign)
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the
    # diamonds carry the archetype figures and the weekday model and
    # all three slots switch OFF — at the RENDER level only, so the
    # slot keys below keep the user's choices untouched.
    archetype_mode: bool = False
    # Whether the ARCHETYPE FIGURES carry their display name (owner
    # 2026-07-18, ROADMAP 15h — Session 21-C): an INDEPENDENT Settings
    # switch, no longer piggybacking on `show_weekday_names` through a
    # menu twin — `ArchetypeLayer` reads THIS key for the figures' names
    # while the weekday Names switches (`show_weekday_names`,
    # `show_info_slot_names`) stay untouched for the weekday bodies.
    archetype_names: bool = True
    # The Earth marker's label MODE (owner 2026-07-18, ROADMAP 15h — the
    # Design ▸ Earth submenu's FOUR exclusive toggles: Date / Weekday /
    # Date & Weekday / Full Date, `constants.EARTH_LABEL_MODES`).
    # Replaces the old show_earth_date/earth_weekday bool pair (Rule #6 —
    # load() migrates an older file's pair, and the pre-rename
    # archetype_earth_day key, onto this single enum).
    earth_label: str = "date"
    solar_rotation: bool = True
    octa_slot: str = "time"             # South slot MODE
    day_slot_style: str = "sign"        # the DAY slot badge's own style
    info_slot_style: str = "sign"       # the INFO slot's own style
    info_slot_theme: str = "planets"    # the INFO slot's weekday theme
    weekday_slot: str = "weekday"       # the weekday POSITION: bodies, or
                                        # an astrology badge (hexa/aurora)
    # The THIRD slot (owner 2026-07-14: 1st/2nd/3rd Slot system) —
    # same shape as the other two; internal keys stay stable.
    third_slot: str = "date"
    third_slot_style: str = "sign"
    third_slot_theme: str = "planets"
    show_third_slot: bool = False
    earth_style: str = "atmo"
    weekday_theme: str = "planets"
    # The figure ROSTER is PER SLOT (owner 2026-07-15: "1. slot grcki
    # planetary, 2. slot grcki panteon") — picked inside each theme's
    # own dropdown, like the Pointer picks variant + palette.
    weekday_roster: str = "planetary"
    info_slot_roster: str = "planetary"
    third_slot_roster: str = "planetary"
    subdial_style: str = "black"        # complication plates (owner A/B
                                        # 2026-07-15): "theme" tints the
                                        # tapisserie field, "black" keeps
                                        # the standard dark AP field
    # Artwork source (owner 2026-07-14): the Gemini and ChatGPT
    # generations coexist on disk; this picks which one the dial and
    # the readers show (missing files fall back to the other source).
    art_source: str = constants.ART_SOURCE_DEFAULT
    legend: bool = True
    # Elements switches (owner spec, FINAL.txt #5): each removes one dial
    # element; the day/twilight indication itself always stays.
    show_earth: bool = True
    show_moon: bool = True
    show_weekday: bool = True
    show_pointer: bool = True
    colorful: bool = True               # off -> white Aura instead of hues
    show_seconds: bool = True
    show_octa_slot: bool = False        # canon 2026-07-14: ONE slot only
    show_weekday_names: bool = True     # the day-name text on the bodies
    show_info_slot_names: bool = True   # the day-name text on the info
                                        # slot's second body (owner bug
                                        # 2026-07-13: its OWN switch —
                                        # the two slots were linked)
    moon_hidden_alpha: float = 0.5      # Moon marker opacity below the horizon
    hands: str = "STEEL"                # the hand pack (Design ▸ Hands)
    # Theme rotation (owner spec 2026-07-12; group dropdown
    # 2026-07-14): "none" = the canon, no rotation; a kinship-group
    # title straight from the Weekday menu grouping cycles that whole
    # family; "custom" cycles the CHECKED themes.
    theme_rotation_group: str = "none"
    theme_rotation_minutes: int = 60
    theme_rotation_themes: tuple[str, ...] = constants.WEEKDAY_THEMES
    # The METAL each bronze-plate theme wears (owner 2026-07-12):
    # {"greek"/"norse"/"profession": "gold"/"bronze"/"silver"}; absent
    # theme = bronze (the art as drawn). follow_ring makes all three
    # wear the ring_finish metal instead.
    theme_metals: dict = field(default_factory=dict)
    theme_metal_follow_ring: bool = False
    language: str = "en"                # translation target (en = originals)
    # THE YEAR LINE (Session 16, owner amendment 2026-07-17): the
    # official form's era labels ("bce_ce" default / "bc_ad"), whether
    # positive years carry the suffix (default bare — "2026"), and the
    # optional THIRD calendar beside the always-shown Anno Lucis
    # (none/auc/byzantine/hebrew/hegirae/chinese/maya — maya is the
    # odd one out, a true day count rather than a year offset, MAYA
    # round, owner 2026-07-20).
    era_notation: str = "bce_ce"
    show_era_suffix: bool = False
    third_era: str = "none"
    # QUICK JUMP CITIES (owner slika 12): the user's own places in the
    # Quick Jump ▸ Location submenu — tuples of {name, latitude,
    # longitude, timezone} picked from the location database in
    # Settings; a jump moves the OBSERVER there, the moment stays.
    jump_cities: tuple = ()
    # Location (M6 picker; defaults = the Belgrade preset).
    city_name: str = defaults.DEFAULT_CITY["name"]
    city_path: tuple[str, ...] = ()     # picker combo restore; () = never picked
    latitude: float = defaults.DEFAULT_CITY["latitude"]
    longitude: float = defaults.DEFAULT_CITY["longitude"]
    timezone: str = defaults.DEFAULT_CITY["timezone"]
    # Element size multipliers + the shared hover-enlarge factor
    # (owner EXTRAS): 1.0 = the skin's own size; hovering an element
    # draws it hover_enlarge times larger (1.0 disables the effect).
    earth_scale: float = 1.0
    moon_scale: float = 1.0
    # ONE size for every slot (owner 2026-07-14: the weekday diamonds
    # and the subdials share the SLOT slider — the old separate
    # weekday/south-slot scales are gone).
    slot_scale: float = 1.0
    ring_letter_scale: float = 1.0
    hover_enlarge: float = 1.2
    # SATURATION (owner 2026-07-18, Settings ▸ Colors, Session 21-D —
    # moved out of Display/Element sizes into its OWN "Saturation" group
    # beside Palette + Ring tint, split into two independent sliders).
    # POINTER (renamed from "palette_saturation" — one release migrates
    # the old key, see SettingsStore.load): scales the Star+Aura
    # palette's HSV saturation at skin build (`render.layers.
    # palette_for`, the ONE spot the palette flows into both the
    # pointer AND the Aura wedges, so they stay in step) — 1.0 = the
    # owner preset unchanged, 0.0 = grayed to each hue's own brightness.
    pointer_saturation: float = 1.0
    # RING (new, Session 21-D): scales the ring band art's (the ring
    # plate + its letter overlay) HSV saturation, applied AFTER the
    # ring_tint recolor (`render.layers.RingLayer`) — 1.0 unchanged,
    # 0.0 grayed. The Umbra and hands do not read this.
    ring_saturation: float = 1.0
    # Display overrides (None = the skin's own value). The Aura's
    # sunlight and twilight opacities are INDEPENDENT (owner spec).
    star_alpha: float | None = None
    aura_day_alpha: float | None = None
    aura_twilight_alpha: float | None = None
    # Custom palettes keyed "pointer_style" -> tuple of #RRGGBB hues.
    palettes: dict = field(default_factory=dict)


class SettingsStore:
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Settings:
        """Missing file -> default Settings (documented first-run behavior).
        Corrupt file -> SettingsCorruptError."""
        if not self._path.exists():
            return Settings()
        try:
            # utf-8-sig: hand-edited files saved with a BOM must still parse
            raw = json.loads(self._path.read_text(encoding="utf-8-sig"))
            window = raw["window"]
            diameter = int(window["diameter"])
            if not defaults.MIN_DIAL_DIAMETER <= diameter <= defaults.MAX_DIAL_DIAMETER:
                raise ValueError(f"diameter {diameter} outside allowed range")
            # A bad value here would otherwise KeyError deep inside a
            # paint pass, where Qt swallows the exception.
            choices = {}
            ring_tint = raw.get("ring_tint")
            if ring_tint is not None:
                ring_tint = str(ring_tint).upper()
                if not _HEX_COLOR.match(ring_tint):
                    raise ValueError(f"ring_tint {ring_tint!r} not #RRGGBB")
            # Custom ring cards first — the chosen ring name is checked
            # against bundled + custom together; the name matches case-
            # insensitively (older files stored "domy").
            custom_rings = tuple(
                _normalized_ring_card(entry)
                for entry in raw.get("custom_rings", ())
            )
            jump_cities = tuple(
                _normalized_jump_city(entry)
                for entry in raw.get("jump_cities", ())
            )
            by_fold = {
                name.lower(): name for name in ring_presets(custom_rings)
            }
            ring_value = str(raw.get("ring", "DOMY"))
            ring = _fold_ring_name(ring_value, by_fold)
            if ring is None:
                raise ValueError(f"ring {ring_value!r} unknown")
            # THE METAL-SPLIT OPTION (TASK 3): per-preset dict, same
            # lenient policy `theme_metals` already uses below — a
            # non-bool value or a name that resolves to nothing loaded
            # (a stale bundled rename, a deleted custom ring) is simply
            # dropped rather than corrupting the whole file over one
            # stale entry.
            ring_two_metals = {}
            for raw_name, value in dict(raw.get("ring_two_metals", {})).items():
                if not isinstance(value, bool):
                    continue
                resolved = _fold_ring_name(str(raw_name), by_fold)
                if resolved is not None:
                    ring_two_metals[resolved] = value
            # One-time migration (2026-07-12): the South slot became a
            # MODE + per-family STYLE pair — the six old combined
            # values map onto it (external user data, not an API shim).
            legacy_slot = {
                "zodiac_sign": ("zodiac", "sign"),
                "zodiac_logo": ("zodiac", "logo"),
                "zodiac_constellation": ("zodiac", "constellation"),
                "zodiac_text": ("zodiac", "text"),
                "chinese_logo": ("chinese", "bronze"),
                "chinese_text": ("chinese", "text"),
            }
            if raw.get("octa_slot") in legacy_slot:
                mode, style = legacy_slot[raw["octa_slot"]]
                raw["octa_slot"] = mode
                raw.setdefault("info_slot_style", style)
            # Second migration (2026-07-12): the per-FAMILY style keys
            # became per-SLOT styles so the two slots stay independent.
            family_styles = {
                "zodiac": raw.get("zodiac_style"),
                "ascendant": raw.get("ascendant_style"),
                "chinese": raw.get("chinese_style"),
            }
            if "info_slot_style" not in raw:
                style = family_styles.get(raw.get("octa_slot"))
                if style:
                    raw["info_slot_style"] = style
            if "day_slot_style" not in raw:
                style = family_styles.get(raw.get("weekday_slot"))
                if style:
                    raw["day_slot_style"] = style
            for key, default, allowed in (
                ("language", "en", tuple(constants.TRANSLATION_LANGUAGES)),
                ("ring_finish", "gold", constants.RING_FINISHES),
                ("pointer", "hexa", tuple(constants.POINTER_POINTS)),
                ("umbra_form", "gradient", constants.UMBRA_FORMS),
                ("umbra_contrast", "dark", constants.UMBRA_CONTRAST_VARIANTS),
                ("palette_style", "paint", constants.PALETTE_STYLES),
                ("calendar_lighting", "hour",
                 constants.CALENDAR_LIGHTING_MODES),
                ("octa_slot", "time", constants.OCTA_SLOT_MODES),
                ("day_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("info_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("info_slot_theme", "planets", constants.WEEKDAY_THEMES),
                ("weekday_slot", "weekday", constants.WEEKDAY_SLOT_MODES),
                ("third_slot", "date", constants.OCTA_SLOT_MODES),
                ("third_slot_style", "sign", constants.SLOT_STYLE_VALUES),
                ("third_slot_theme", "planets", constants.WEEKDAY_THEMES),
                ("earth_style", "atmo", constants.EARTH_STYLES),
                ("weekday_theme", "planets", constants.WEEKDAY_THEMES),
                ("subdial_style", "black", constants.SUBDIAL_STYLES),
                ("weekday_roster", "planetary", constants.FIGURE_ROSTERS),
                ("info_slot_roster", "planetary", constants.FIGURE_ROSTERS),
                ("third_slot_roster", "planetary", constants.FIGURE_ROSTERS),
                ("art_source", constants.ART_SOURCE_DEFAULT,
                 constants.ART_SOURCES),
                ("era_notation", "bce_ce", constants.ERA_NOTATIONS),
                ("third_era", "none", constants.THIRD_ERAS),
                ("z_mode", "bottom", constants.Z_MODES),
            ):
                value = str(raw.get(key, default))
                if value not in allowed:
                    raise ValueError(f"{key} {value!r} unknown")
                choices[key] = value
            location = raw.get("location", {})
            latitude = float(location.get("latitude", defaults.DEFAULT_CITY["latitude"]))
            longitude = float(
                location.get("longitude", defaults.DEFAULT_CITY["longitude"])
            )
            if not constants.LATITUDE_RANGE[0] <= latitude <= constants.LATITUDE_RANGE[1]:
                raise ValueError(f"latitude {latitude} outside allowed range")
            if (
                not constants.LONGITUDE_RANGE[0]
                <= longitude
                <= constants.LONGITUDE_RANGE[1]
            ):
                raise ValueError(f"longitude {longitude} outside allowed range")
            timezone = str(location.get("timezone", defaults.DEFAULT_CITY["timezone"]))
            try:
                ZoneInfo(timezone)
            except Exception as exc:
                raise ValueError(f"timezone {timezone!r} unknown: {exc}") from exc
            loaded = Settings(
                schema_version=int(raw["schema_version"]),
                window_x=None if window["x"] is None else int(window["x"]),
                window_y=None if window["y"] is None else int(window["y"]),
                diameter=diameter,
                # Additive keys (still schema 1): absent in older files.
                click_through=_load_bool(raw, "click_through", False),
                show_era_suffix=_load_bool(raw, "show_era_suffix", False),
                archetype_mode=_load_bool(raw, "archetype_mode", False),
                archetype_names=_load_bool(raw, "archetype_names", True),
                earth_label=_load_earth_label(raw),
                solar_rotation=_load_bool(raw, "solar_rotation", True),
                legend=_load_bool(raw, "legend", True),
                show_earth=_load_bool(raw, "show_earth", True),
                show_moon=_load_bool(raw, "show_moon", True),
                show_weekday=_load_bool(raw, "show_weekday", True),
                show_pointer=_load_bool(raw, "show_pointer", True),
                colorful=_load_bool(raw, "colorful", True),
                show_seconds=_load_bool(raw, "show_seconds", True),
                # Canon (owner 2026-07-14): ONE slot out of the box.
                show_octa_slot=_load_bool(raw, "show_octa_slot", False),
                show_third_slot=_load_bool(raw, "show_third_slot", False),
                show_weekday_names=_load_bool(raw, "show_weekday_names", True),
                show_info_slot_names=_load_bool(
                    raw, "show_info_slot_names", True
                ),
                moon_hidden_alpha=_load_scale(
                    raw, "moon_hidden_alpha", 0.0, 1.0, 0.5
                ),
                hands=(
                    raw["hands"]
                    if isinstance(raw.get("hands"), str) and raw["hands"].strip()
                    else "STEEL"
                ),
                theme_rotation_group=_load_rotation_group(raw),
                theme_rotation_minutes=(
                    int(raw["theme_rotation_minutes"])
                    if isinstance(raw.get("theme_rotation_minutes"), int)
                    and 1 <= raw["theme_rotation_minutes"] <= 24 * 60
                    else 60
                ),
                theme_rotation_themes=tuple(
                    theme
                    for theme in raw.get(
                        "theme_rotation_themes", constants.WEEKDAY_THEMES
                    )
                    if theme in constants.WEEKDAY_THEMES
                ) or constants.WEEKDAY_THEMES,
                theme_metals={
                    str(theme): str(metal)
                    for theme, metal in dict(
                        raw.get("theme_metals", {})
                    ).items()
                    if str(theme) in constants.METAL_THEMES
                    # Per-theme allowed set (owner 2026-07-18): planets_art
                    # has no colored/ folder, so "colored" is rejected for
                    # it even though it is metal-capable.
                    and str(metal) in constants.theme_metals(str(theme))
                },
                theme_metal_follow_ring=_load_bool(
                    raw, "theme_metal_follow_ring", False
                ),
                city_name=str(location.get("name", defaults.DEFAULT_CITY["name"])),
                city_path=tuple(location.get("path", ())),
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                ring=ring,
                custom_rings=custom_rings,
                ring_two_metals=ring_two_metals,
                jump_cities=jump_cities,
                ring_tint=ring_tint,
                earth_scale=_load_scale(raw, "earth_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                moon_scale=_load_scale(raw, "moon_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                # One-time migration (2026-07-14): the separate weekday
                # and south-slot scales merged into slot_scale — older
                # files inherit their weekday value.
                slot_scale=_load_scale(
                    raw, "slot_scale", *constants.ELEMENT_SCALE_RANGE,
                    _load_scale(
                        raw, "weekday_scale",
                        *constants.ELEMENT_SCALE_RANGE, 1.0,
                    ),
                ),
                ring_letter_scale=_load_scale(raw, "ring_letter_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                hover_enlarge=_load_scale(raw, "hover_enlarge", *constants.HOVER_ENLARGE_RANGE, 1.2),
                # One-release migration (Session 21-D, owner rename for
                # clarity now that RING has its own saturation slider):
                # "palette_saturation" is read as the fallback default
                # when the new key is absent; the file is rewritten
                # under the new key on the next save.
                pointer_saturation=_load_scale(
                    raw, "pointer_saturation",
                    *constants.POINTER_SATURATION_RANGE,
                    _load_scale(
                        raw, "palette_saturation",
                        *constants.POINTER_SATURATION_RANGE, 1.0,
                    ),
                ),
                ring_saturation=_load_scale(
                    raw, "ring_saturation",
                    *constants.RING_SATURATION_RANGE, 1.0,
                ),
                star_alpha=_load_alpha(raw, "star_alpha"),
                aura_day_alpha=_load_alpha(raw, "aura_day_alpha"),
                aura_twilight_alpha=_load_alpha(raw, "aura_twilight_alpha"),
                palettes=_load_palettes(raw.get("palettes", {})),
                **choices,
            )
            return loaded
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise SettingsCorruptError(self._path, exc) from exc

    def save(self, settings: Settings) -> None:
        payload = {
            "schema_version": settings.schema_version,
            "window": {
                "x": settings.window_x,
                "y": settings.window_y,
                "diameter": settings.diameter,
            },
            "click_through": settings.click_through,
            "ring": settings.ring,
            "ring_tint": settings.ring_tint,
            "ring_finish": settings.ring_finish,
            "custom_rings": [dict(card) for card in settings.custom_rings],
            "ring_two_metals": dict(settings.ring_two_metals),
            "pointer": settings.pointer,
            "umbra_form": settings.umbra_form,
            "umbra_contrast": settings.umbra_contrast,
            "palette_style": settings.palette_style,
            "calendar_lighting": settings.calendar_lighting,
            "archetype_mode": settings.archetype_mode,
            "archetype_names": settings.archetype_names,
            "earth_label": settings.earth_label,
            "z_mode": settings.z_mode,
            "solar_rotation": settings.solar_rotation,
            "octa_slot": settings.octa_slot,
            "day_slot_style": settings.day_slot_style,
            "info_slot_style": settings.info_slot_style,
            "info_slot_theme": settings.info_slot_theme,
            "weekday_slot": settings.weekday_slot,
            "third_slot": settings.third_slot,
            "third_slot_style": settings.third_slot_style,
            "third_slot_theme": settings.third_slot_theme,
            "show_third_slot": settings.show_third_slot,
            "earth_style": settings.earth_style,
            "weekday_theme": settings.weekday_theme,
            "subdial_style": settings.subdial_style,
            "weekday_roster": settings.weekday_roster,
            "info_slot_roster": settings.info_slot_roster,
            "third_slot_roster": settings.third_slot_roster,
            "art_source": settings.art_source,
            "legend": settings.legend,
            "show_earth": settings.show_earth,
            "show_moon": settings.show_moon,
            "show_weekday": settings.show_weekday,
            "show_pointer": settings.show_pointer,
            "colorful": settings.colorful,
            "show_seconds": settings.show_seconds,
            "show_octa_slot": settings.show_octa_slot,
            "show_weekday_names": settings.show_weekday_names,
            "show_info_slot_names": settings.show_info_slot_names,
            "moon_hidden_alpha": settings.moon_hidden_alpha,
            "hands": settings.hands,
            "theme_rotation_group": settings.theme_rotation_group,
            "theme_rotation_minutes": settings.theme_rotation_minutes,
            "theme_rotation_themes": list(settings.theme_rotation_themes),
            "theme_metals": dict(settings.theme_metals),
            "theme_metal_follow_ring": settings.theme_metal_follow_ring,
            "language": settings.language,
            "era_notation": settings.era_notation,
            "show_era_suffix": settings.show_era_suffix,
            "third_era": settings.third_era,
            "jump_cities": [dict(city) for city in settings.jump_cities],
            "location": {
                "name": settings.city_name,
                "path": list(settings.city_path),
                "latitude": settings.latitude,
                "longitude": settings.longitude,
                "timezone": settings.timezone,
            },
            "earth_scale": settings.earth_scale,
            "moon_scale": settings.moon_scale,
            "slot_scale": settings.slot_scale,
            "ring_letter_scale": settings.ring_letter_scale,
            "hover_enlarge": settings.hover_enlarge,
            "pointer_saturation": settings.pointer_saturation,
            "ring_saturation": settings.ring_saturation,
            "star_alpha": settings.star_alpha,
            "aura_day_alpha": settings.aura_day_alpha,
            "aura_twilight_alpha": settings.aura_twilight_alpha,
            "palettes": {
                key: list(palette) for key, palette in settings.palettes.items()
            },
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, self._path)

    def quarantine(self) -> Path:
        """Rename the corrupt file to .bak (overwriting an older .bak) so a
        fresh default file can be seeded. Returns the backup path."""
        backup = self._path.with_suffix(".json.bak")
        os.replace(self._path, backup)
        return backup


# RING PRESET RENAMES (TASK 2, MASON/ICONS round, owner verdicts
# 2026-07-19, third batch): a stored settings file's OLD bundled preset
# name migrates onto its new one (external user data, not an API shim,
# Rule #6) — a bare case-insensitive fold alone cannot bridge these
# (unlike "MORPH" -> "Morph", a pure case change the existing fold
# already handles for free).
_LEGACY_RING_NAMES = {"mason g": "Mason", "numbers": "Omega"}


def _fold_ring_name(raw_name: str, by_fold: dict) -> str | None:
    """One stored ring name resolved to its CURRENT bundled/custom name
    — the TASK 2 rename migration first, then the existing case-
    insensitive fold (older files stored "domy") — or None when it
    names nothing loaded (a stale bundled rename, or a custom ring the
    user later deleted). Shared by the top-level `ring` field (which
    must raise on a miss) and `ring_two_metals`'s dict keys (which
    silently drop a miss, `theme_metals`'s own lenient policy)."""
    renamed = _LEGACY_RING_NAMES.get(raw_name.lower(), raw_name)
    return by_fold.get(renamed.lower())


def _normalized_ring_card(entry: dict) -> dict:
    """One custom ring card, validated by the shared card validator and
    stored in its JSON-serializable shape."""
    card = validate_preset(entry)
    return {
        "name": card["name"],
        "positions": list(card["positions"]),
        "letters": list(card["letters"]),
    }


def _normalized_jump_city(entry: dict) -> dict:
    """One Quick Jump city (Session 16), validated field by field — a
    hand-edited coordinate or timezone must fail HERE, not inside a
    jump (Rule #1)."""
    name = str(entry["name"]).strip()
    if not name:
        raise ValueError("jump city with an empty name")
    latitude = float(entry["latitude"])
    longitude = float(entry["longitude"])
    if not constants.LATITUDE_RANGE[0] <= latitude <= constants.LATITUDE_RANGE[1]:
        raise ValueError(f"jump city {name!r}: latitude {latitude} out of range")
    if not constants.LONGITUDE_RANGE[0] <= longitude <= constants.LONGITUDE_RANGE[1]:
        raise ValueError(f"jump city {name!r}: longitude {longitude} out of range")
    timezone = str(entry["timezone"])
    try:
        ZoneInfo(timezone)
    except Exception as exc:
        raise ValueError(
            f"jump city {name!r}: timezone {timezone!r} unknown: {exc}"
        ) from exc
    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
    }


def rotation_themes(settings: "Settings") -> tuple[str, ...]:
    """The themes the rotation cycles (owner 2026-07-14): a kinship
    GROUP straight from the Weekday menu grouping, the custom checkbox
    list — or nothing at all ("none", the canon: Planets forever)."""
    group = settings.theme_rotation_group
    if group == "custom":
        return settings.theme_rotation_themes
    for title, keys in defaults.WEEKDAY_MENU_GROUPS:
        if title == group:
            return keys
    return ()


def _load_rotation_group(raw: dict) -> str:
    """The rotation dropdown value — with the one-time migration from
    the pre-2026-07-14 Enabled checkbox (external user data: enabled
    meant the checked list, i.e. today's "custom")."""
    value = raw.get("theme_rotation_group")
    if value is None:
        return "custom" if raw.get("theme_rotation") is True else "none"
    value = str(value)
    allowed = {"none", "custom"} | {
        title for title, _ in defaults.WEEKDAY_MENU_GROUPS
    }
    if value not in allowed:
        raise ValueError(f"theme_rotation_group {value!r} unknown")
    return value


def _load_bool(raw: dict, key: str, default: bool) -> bool:
    """A REAL JSON boolean or absent — a hand-edited "false" string
    would otherwise coerce to True silently (review finding; Rule #1:
    errors must be visible)."""
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} {value!r} is not true/false")
    return value


def _load_earth_label(raw: dict) -> str:
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
        old_date = _load_bool(raw, "show_earth_date", True)
        old_weekday = _load_bool(
            raw, "earth_weekday", _load_bool(raw, "archetype_earth_day", False)
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


def _load_scale(raw: dict, key: str, low: float, high: float, default: float) -> float:
    """Size multiplier: absent = the default; out of range = corrupt."""
    value = float(raw.get(key, default))
    if not low <= value <= high:
        raise ValueError(f"{key} {value} outside {low}..{high}")
    return value


def _load_alpha(raw: dict, key: str) -> float | None:
    """Opacity override: null/absent = use the skin's own value."""
    value = raw.get(key)
    if value is None:
        return None
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{key} {value} outside 0..1")
    return value


def _load_palettes(raw: dict) -> dict:
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


def replace(settings: Settings, **changes) -> Settings:
    """Convenience wrapper over dataclasses.replace for frozen Settings."""
    return dataclasses.replace(settings, **changes)
