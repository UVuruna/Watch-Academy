"""Frozen-safe path resolution.

All paths derive from this module — never from the current working
directory. Handles both a source checkout and a PyInstaller --onedir
bundle (PyInstaller 6 places bundled data in _internal/ and exposes it
via sys._MEIPASS).
"""

import os
import sys
from pathlib import Path

from config import constants


def app_root() -> Path:
    """Root folder holding bundled resources (Database/, assets/)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def database_dir() -> Path:
    return app_root() / "Database"


def deep_time_path() -> Path:
    """The OPTIONAL Deep Time pack (Session 16): present → Time Travel
    spans the full pack coverage; absent → the bundled span with the
    friendly clamp. Gitignored; built by setup/make_deep_time.py and
    bundled only with the FULL installation. Frozen-safe like every
    other bundled path."""
    return database_dir() / constants.DEEP_TIME_DB_FILENAME


def assets_dir() -> Path:
    """Shared app content (ring art, weekday themes, zodiac art) —
    NOT skin-specific: a skin is a dial design, the content is common."""
    return app_root() / "assets"


def bundled_skins_dir() -> Path:
    return assets_dir() / "skins"


def user_dir() -> Path:
    """Per-user writable folder: %APPDATA%/DOMY Watch (not auto-created)."""
    return Path(os.environ["APPDATA"]) / constants.APP_NAME


def settings_path(watch_index: int = 1) -> Path:
    """Watch 1 keeps the pre-multi-watch filename (existing installs
    keep working untouched); watch N (2+, ADD WATCH round, owner
    INSTRUCTION.txt item 2, sealed 2026-07-21) gets its OWN numbered
    file — see settings_store.md for the scheme."""
    if watch_index == 1:
        return user_dir() / "settings.json"
    return user_dir() / f"settings.{watch_index}.json"


def discover_watch_indices() -> list[int]:
    """Every watch whose settings file already exists on disk, sorted
    (ADD WATCH round): watch 1's plain `settings.json` (if present)
    plus every `settings.<N>.json`. A brand-new install (no user dir
    yet, or an empty one) yields `[1]` so the caller always has an
    anchor watch to build. Filesystem-scan cost is startup-only, never
    a hot path."""
    directory = user_dir()
    found = {1} if (directory / "settings.json").exists() else set()
    if directory.exists():
        for candidate in directory.glob("settings.*.json"):
            stem_parts = candidate.stem.split(".")   # "settings", "<N>"
            if len(stem_parts) == 2 and stem_parts[1].isdigit():
                found.add(int(stem_parts[1]))
    return sorted(found) or [1]


# The active artwork source (owner 2026-07-14: Gemini vs ChatGPT) —
# set once by apply_display_settings; every disk boundary resolves
# canonical paths through art_file.
_art_source = constants.ART_SOURCE_DEFAULT


def set_art_source(source: str) -> None:
    """Switch the active artwork source ("gemini" / "chatgpt")."""
    global _art_source
    if source not in constants.ART_SOURCES:
        raise ValueError(f"unknown art source: {source}")
    _art_source = source


def art_source() -> str:
    return _art_source


# The active SUBDIAL PLATE SET (owner decree 2026-07-21, Rsub round) —
# mirrors the art-source switch above exactly. `render.assets.
# subdial_plate_file` is the ONE reader, so a module global here avoids
# threading a new parameter through `render.layers.draw_slot_roundel`'s
# existing call site (the seat/finish/tint signature stays untouched).
_subdial_set = constants.SUBDIAL_SET_DEFAULT


def set_subdial_set(name: str) -> None:
    """Switch the active subdial plate set ("set1".."set4" or "solo")."""
    global _subdial_set
    if name not in constants.SUBDIAL_SETS:
        raise ValueError(f"unknown subdial set: {name}")
    _subdial_set = name


def subdial_set() -> str:
    return _subdial_set


def art_file(path: Path | None) -> Path | None:
    """Map a CANONICAL (source-less) asset path into the active source
    subtree — assets/<root>/<source>/<rest> — falling back to the OTHER
    source where the file is missing (the ChatGPT coverage is partial;
    owner 2026-07-14). Paths outside the sourced roots, and already
    source-qualified paths, pass through untouched."""
    if path is None:
        return None
    # Lexical normalization first: the Inner Wheel themes reach the
    # emblem art via a "../emblem/..." step-up — the source segment
    # must land under the REAL root (emblem/), not the literal one.
    path = Path(os.path.normpath(path))
    assets = assets_dir()
    try:
        rel = path.relative_to(assets)
    except ValueError:
        return path
    parts = rel.parts
    if len(parts) < 2 or parts[0] not in constants.ART_SOURCED_ROOTS:
        return path
    if parts[1] in constants.ART_SOURCES:
        return path
    ordered = (_art_source,) + tuple(
        source for source in constants.ART_SOURCES if source != _art_source
    )
    for source in ordered:
        candidate = assets.joinpath(parts[0], source, *parts[1:])
        if candidate.exists():
            return candidate
    return assets.joinpath(parts[0], ordered[0], *parts[1:])
