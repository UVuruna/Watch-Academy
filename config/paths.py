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
