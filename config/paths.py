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


def assets_dir() -> Path:
    """Shared app content (ring art, weekday themes, zodiac art) —
    NOT skin-specific: a skin is a dial design, the content is common."""
    return app_root() / "assets"


def bundled_skins_dir() -> Path:
    return assets_dir() / "skins"


def user_dir() -> Path:
    """Per-user writable folder: %APPDATA%/DOMY Watch (not auto-created)."""
    return Path(os.environ["APPDATA"]) / constants.APP_NAME


def settings_path() -> Path:
    return user_dir() / "settings.json"


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
