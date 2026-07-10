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
    ring: str = "DOMY"                  # ring preset CARD name (bundled or custom)
    ring_tint: str | None = None        # #RRGGBB multiplying ring+hands+Umbra
    ring_finish: str = "gold"           # letter metals (triangle/12h rules)
    # The user's custom ring cards ({name, positions, letters}) — merged
    # with Database/ring_presets.json by data/rings.py.
    custom_rings: tuple = ()
    pointer: str = "hexa"
    umbra_form: str = "fine"
    umbra_contrast: str = "full"
    palette_style: str = "paint"
    solar_rotation: bool = True
    octa_slot: str = "time"
    earth_style: str = "clean"
    weekday_theme: str = "planets"
    legend: bool = True
    # Elements switches (owner spec, FINAL.txt #5): each removes one dial
    # element; the day/twilight indication itself always stays.
    show_earth: bool = True
    show_moon: bool = True
    show_weekday: bool = True
    show_pointer: bool = True
    colorful: bool = True               # off -> white Aura instead of hues
    show_seconds: bool = True
    show_octa_slot: bool = True         # the Compass info slot (octa only)
    language: str = "en"                # translation target (en = originals)
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
    weekday_scale: float = 1.0
    octa_slot_scale: float = 1.0
    ring_letter_scale: float = 1.0
    hover_enlarge: float = 1.2
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
            by_fold = {
                name.lower(): name for name in ring_presets(custom_rings)
            }
            ring_value = str(raw.get("ring", "DOMY"))
            ring = by_fold.get(ring_value.lower())
            if ring is None:
                raise ValueError(f"ring {ring_value!r} unknown")
            for key, default, allowed in (
                ("language", "en", tuple(constants.TRANSLATION_LANGUAGES)),
                ("ring_finish", "gold", constants.RING_FINISHES),
                ("pointer", "hexa", tuple(constants.POINTER_POINTS)),
                ("umbra_form", "fine", constants.UMBRA_FORMS),
                ("umbra_contrast", "full", constants.UMBRA_CONTRAST_VARIANTS),
                ("palette_style", "paint", constants.PALETTE_STYLES),
                ("octa_slot", "time", constants.OCTA_SLOT_MODES),
                ("earth_style", "clean", constants.EARTH_STYLES),
                ("weekday_theme", "planets", constants.WEEKDAY_THEMES),
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
            return Settings(
                schema_version=int(raw["schema_version"]),
                window_x=None if window["x"] is None else int(window["x"]),
                window_y=None if window["y"] is None else int(window["y"]),
                diameter=diameter,
                # Additive keys (still schema 1): absent in older files.
                click_through=_load_bool(raw, "click_through", False),
                solar_rotation=_load_bool(raw, "solar_rotation", True),
                legend=_load_bool(raw, "legend", True),
                show_earth=_load_bool(raw, "show_earth", True),
                show_moon=_load_bool(raw, "show_moon", True),
                show_weekday=_load_bool(raw, "show_weekday", True),
                show_pointer=_load_bool(raw, "show_pointer", True),
                colorful=_load_bool(raw, "colorful", True),
                show_seconds=_load_bool(raw, "show_seconds", True),
                show_octa_slot=_load_bool(raw, "show_octa_slot", True),
                city_name=str(location.get("name", defaults.DEFAULT_CITY["name"])),
                city_path=tuple(location.get("path", ())),
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                ring=ring,
                custom_rings=custom_rings,
                ring_tint=ring_tint,
                earth_scale=_load_scale(raw, "earth_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                moon_scale=_load_scale(raw, "moon_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                weekday_scale=_load_scale(raw, "weekday_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                octa_slot_scale=_load_scale(raw, "octa_slot_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                ring_letter_scale=_load_scale(raw, "ring_letter_scale", *constants.ELEMENT_SCALE_RANGE, 1.0),
                hover_enlarge=_load_scale(raw, "hover_enlarge", *constants.HOVER_ENLARGE_RANGE, 1.2),
                star_alpha=_load_alpha(raw, "star_alpha"),
                aura_day_alpha=_load_alpha(raw, "aura_day_alpha"),
                aura_twilight_alpha=_load_alpha(raw, "aura_twilight_alpha"),
                palettes=_load_palettes(raw.get("palettes", {})),
                **choices,
            )
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
            "pointer": settings.pointer,
            "umbra_form": settings.umbra_form,
            "umbra_contrast": settings.umbra_contrast,
            "palette_style": settings.palette_style,
            "solar_rotation": settings.solar_rotation,
            "octa_slot": settings.octa_slot,
            "earth_style": settings.earth_style,
            "weekday_theme": settings.weekday_theme,
            "legend": settings.legend,
            "show_earth": settings.show_earth,
            "show_moon": settings.show_moon,
            "show_weekday": settings.show_weekday,
            "show_pointer": settings.show_pointer,
            "colorful": settings.colorful,
            "show_seconds": settings.show_seconds,
            "show_octa_slot": settings.show_octa_slot,
            "language": settings.language,
            "location": {
                "name": settings.city_name,
                "path": list(settings.city_path),
                "latitude": settings.latitude,
                "longitude": settings.longitude,
                "timezone": settings.timezone,
            },
            "earth_scale": settings.earth_scale,
            "moon_scale": settings.moon_scale,
            "weekday_scale": settings.weekday_scale,
            "octa_slot_scale": settings.octa_slot_scale,
            "ring_letter_scale": settings.ring_letter_scale,
            "hover_enlarge": settings.hover_enlarge,
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


def _normalized_ring_card(entry: dict) -> dict:
    """One custom ring card, validated by the shared card validator and
    stored in its JSON-serializable shape."""
    card = validate_preset(entry)
    return {
        "name": card["name"],
        "positions": list(card["positions"]),
        "letters": list(card["letters"]),
    }


def _load_bool(raw: dict, key: str, default: bool) -> bool:
    """A REAL JSON boolean or absent — a hand-edited "false" string
    would otherwise coerce to True silently (review finding; Rule #1:
    errors must be visible)."""
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} {value!r} is not true/false")
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
