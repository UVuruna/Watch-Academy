"""Skin discovery and resolution.

Packs live in the bundled assets/skins/ and in the user's
%APPDATA%/DOMY Watch/skins/. "domy" is the built-in base (DEFAULT_SKIN);
every other pack merges its (possibly partial) skin.json onto that base.
"""

from pathlib import Path

from config import defaults, paths
from skins import manifest, packs

BASE_SKIN_NAME = "domy"


def discover() -> dict[str, Path]:
    """name -> pack folder for every folder carrying a skin.json, plus
    the built-in base (which needs no manifest on disk)."""
    found: dict[str, Path] = {BASE_SKIN_NAME: paths.bundled_skins_dir() / BASE_SKIN_NAME}
    for root in (paths.bundled_skins_dir(), paths.user_skins_dir()):
        if not root.exists():
            continue
        for folder in sorted(root.iterdir()):
            if folder.name != BASE_SKIN_NAME and (folder / "skin.json").exists():
                found[folder.name] = folder
    return found


def resolve(name: str) -> manifest.SkinDefinition:
    """The skin to render: the built-in base, or a pack merged onto it.
    Unknown names and broken packs raise (SkinValidationError/KeyError) —
    the caller surfaces them visibly, never falls back silently."""
    if name == BASE_SKIN_NAME:
        return defaults.DEFAULT_SKIN
    folders = discover()
    if name not in folders:
        raise KeyError(
            f"unknown skin {name!r}; available: {', '.join(sorted(folders))}"
        )
    return packs.load_pack(folders[name], defaults.DEFAULT_SKIN)
