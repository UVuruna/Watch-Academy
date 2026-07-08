"""skin.json loading, merging and serialization.

A pack folder holds a `skin.json` whose sections mirror the manifest
units. Packs may be PARTIAL: absent units inherit from the base skin
(DOMY), so e.g. MORPH ships only its ring. Validation is loud and
complete — SkinValidationError lists EVERY problem at once (Rule #1).
"""

import dataclasses
import json
from pathlib import Path

from config import constants
from skins import manifest

# JSON section name -> (SkinDefinition field, spec class)
_UNITS = {
    "background": ("background", manifest.BackgroundSpec),
    "star": ("star", manifest.StarSpec),
    "noon_marker": ("noon_marker", manifest.NoonMarkerSpec),
    "ring": ("ring", manifest.RingSpec),
    "weekday_set": ("weekday_set", manifest.WeekdaySpec),
    "year_marker": ("year_marker", manifest.YearMarkerSpec),
    "hands": ("hands", manifest.HandsSpec),
}

# Fields holding a single asset path (relative to the pack folder in
# JSON, absolute at runtime).
_PATH_FIELDS = {"base_asset", "asset", "moon_asset"}
# Dict fields whose VALUES are asset paths.
_PATH_DICT_FIELDS = {"bodies", "variants"}
# Dict fields keyed by ints in the dataclass but strings in JSON.
_INT_KEY_FIELDS = {"letters"}


class SkinValidationError(Exception):
    def __init__(self, folder: Path, problems: list[str]):
        listing = "\n".join(f"  - {problem}" for problem in problems)
        super().__init__(f"Invalid skin pack {folder}:\n{listing}")
        self.folder = folder
        self.problems = problems


def load_pack(folder: Path, base: manifest.SkinDefinition) -> manifest.SkinDefinition:
    """The pack's skin.json merged unit-by-unit onto `base`."""
    problems: list[str] = []
    manifest_path = folder / "skin.json"
    if not manifest_path.exists():
        raise SkinValidationError(folder, ["skin.json is missing"])
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkinValidationError(folder, [f"skin.json unreadable: {exc}"]) from exc

    merged = {"name": raw.get("name", folder.name)}
    if "z_order" in raw:
        merged["z_order"] = tuple(raw["z_order"])
    # Top-level scalar choices, validated against the product's closed sets.
    _SCALARS = (
        ("pointer", tuple(constants.POINTER_POINTS)),
        ("umbra_contrast", constants.UMBRA_CONTRAST_VARIANTS),
        ("palette_style", constants.PALETTE_STYLES),
        ("solar_rotation", (True, False)),
        ("octa_slot", constants.OCTA_SLOT_MODES),
    )
    for key, allowed in _SCALARS:
        if key in raw:
            if raw[key] in allowed:
                merged[key] = raw[key]
            else:
                problems.append(
                    f"{key}: unknown value {raw[key]!r} (expected one of {sorted(map(str, allowed))})"
                )
    scalar_keys = {key for key, _ in _SCALARS}
    for section, value in raw.items():
        if section in ("name", "z_order") or section in scalar_keys:
            continue
        if section not in _UNITS:
            problems.append(f"unknown section {section!r}")
            continue
        field_name, spec_class = _UNITS[section]
        spec = _build_spec(spec_class, value, folder, f"{section}.", problems)
        if spec is not None:
            merged[field_name] = spec
    if problems:
        raise SkinValidationError(folder, problems)
    return dataclasses.replace(base, **merged)


def _build_spec(spec_class, data: dict, folder: Path, prefix: str, problems: list[str]):
    if not isinstance(data, dict):
        problems.append(f"{prefix[:-1]}: expected an object")
        return None
    known = {field.name: field for field in dataclasses.fields(spec_class)}
    kwargs = {}
    for key, value in data.items():
        if key not in known:
            problems.append(f"{prefix}{key}: unknown field")
            continue
        if key in _PATH_FIELDS:
            value = _resolve_path(value, folder, f"{prefix}{key}", problems)
        elif key in _PATH_DICT_FIELDS and isinstance(value, dict):
            value = {
                name: _resolve_path(item, folder, f"{prefix}{key}.{name}", problems)
                for name, item in value.items()
            }
        elif key in _INT_KEY_FIELDS and isinstance(value, dict):
            value = {int(name): item for name, item in value.items()}
        elif isinstance(value, list):
            value = tuple(value)
        elif isinstance(value, dict) and dataclasses.is_dataclass(known[key].type):
            pass  # nested specs handled below
        kwargs[key] = value
    # Nested HandSpec objects inside HandsSpec.
    if spec_class is manifest.HandsSpec:
        for hand in ("hour", "minute", "second"):
            if isinstance(kwargs.get(hand), dict):
                kwargs[hand] = _build_spec(
                    manifest.HandSpec, kwargs[hand], folder, f"{prefix}{hand}.", problems
                )
    missing = [
        name
        for name, field in known.items()
        if name not in kwargs
        and field.default is dataclasses.MISSING
        and field.default_factory is dataclasses.MISSING
    ]
    for name in missing:
        problems.append(f"{prefix}{name}: required field missing")
    if missing:
        return None
    try:
        return spec_class(**kwargs)
    except TypeError as exc:
        problems.append(f"{prefix[:-1]}: {exc}")
        return None


def _resolve_path(value, folder: Path, label: str, problems: list[str]):
    if value is None:
        return None
    path = folder / str(value)
    if not path.exists():
        problems.append(f"{label}: asset not found: {value}")
        return None
    return path


def serialize_skin(skin: manifest.SkinDefinition, folder: Path) -> dict:
    """JSON-ready dict with asset paths relative to `folder` (used to
    extract the built-in DOMY skin into its pack)."""

    def portable(value, key=None):
        if isinstance(value, Path):
            return value.relative_to(folder).as_posix()
        if isinstance(value, tuple):
            return [portable(item) for item in value]
        if isinstance(value, dict):
            return {str(name): portable(item) for name, item in value.items()}
        if dataclasses.is_dataclass(value):
            # None stays as explicit null (e.g. a procedural noon marker).
            return {
                field.name: portable(getattr(value, field.name))
                for field in dataclasses.fields(value)
            }
        return value

    payload = {
        "name": skin.name,
        "z_order": list(skin.z_order),
        "pointer": skin.pointer,
        "umbra_contrast": skin.umbra_contrast,
        "palette_style": skin.palette_style,
        "solar_rotation": skin.solar_rotation,
        "octa_slot": skin.octa_slot,
    }
    for section, (field_name, _) in _UNITS.items():
        payload[section] = portable(getattr(skin, field_name))
    return payload
