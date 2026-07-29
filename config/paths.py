"""Frozen-safe path resolution.

All paths derive from this module — never from the current working
directory. Handles both a source checkout and a PyInstaller --onedir
bundle (PyInstaller 6 places bundled data in _internal/ and exposes it
via sys._MEIPASS).
"""

import os
import sys
import threading
from contextlib import contextmanager
from functools import wraps
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from config import constants


def app_root() -> Path:
    """Root folder holding bundled resources (Database/, assets/)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def database_dir() -> Path:
    return app_root() / "Database"


def preview3d_gadget_dir() -> Path | None:
    """The sibling 3D Preview gadget's repo root (WORKPLAN Session 28) —
    a monorepo-relative guess (`Gadgets/3D Preview` beside `Gadgets/DOMY
    Watch`), never an absolute path baked in. `None` when it is not
    there: a checkout without the gadget, a renamed/moved folder, or a
    frozen build (the gadget is a dev-time sibling, never bundled data).
    `render.cube_preview3d` treats `None` as the documented fallback
    (root Rule #1) — the cube pages simply keep their computed 2D
    drawer; this function never raises."""
    if getattr(sys, "frozen", False):
        return None
    candidate = Path(__file__).resolve().parents[2] / "3D Preview"
    return candidate if candidate.is_dir() else None


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


# --- THE DISPLAY CONTEXT --------------------------------------------------------
# The artwork source (owner 2026-07-14: Gemini vs ChatGPT), the subdial
# plate set (owner decree 2026-07-21) and the metal shades (R8a, owner
# 2026-07-21 night) are ONE PER-WATCH bundle — not three process-wide
# switches.
#
# They used to be three module globals that `app.controller.
# apply_display_settings` overwrote on every skin install. With more than
# one watch open that was last-writer-wins: `AppController.__init__`
# builds EVERY watch before the first one paints, so all of them then
# rendered with the LAST watch's choices. The owner's report
# (2026-07-28): a DOMY watch and a PILOT watch, both on the `thematic`
# ring finish, came out THE SAME RED — DOMY's shade, because DOMY was
# built last. The `watch_manager` docstring had already flagged the same
# hazard for the art source and subdial set; `thematic` inherited it.
#
# Now: a watch owns a `DisplayContext`, carried on its SKIN, and every
# entry point that resolves art installs it for the duration of its work
# (`with paths.display(context)`). The current context is THREAD-LOCAL, so
# the background warm thread can build one watch's art while the GUI
# thread paints another's without either seeing the other's choices.


@dataclass(frozen=True)
class DisplayContext:
    """One watch's art choices. Immutable — a settings change builds a
    NEW context (via `display_context`, the validating factory) rather
    than mutating the live one, so a context captured by a background
    thread never changes underneath it."""

    art_source: str = constants.ART_SOURCE_DEFAULT
    subdial_set: str = constants.SUBDIAL_SET_DEFAULT
    metal_shades: Mapping[str, str] = MappingProxyType(
        dict(constants.METAL_SHADE_DEFAULT)
    )

    def shade(self, metal: str) -> str:
        return self.metal_shades.get(metal, constants.METAL_SHADE_DEFAULT[metal])


def display_context(
    art_source: str = constants.ART_SOURCE_DEFAULT,
    subdial_set: str = constants.SUBDIAL_SET_DEFAULT,
    metal_shades: Mapping[str, str] | None = None,
) -> DisplayContext:
    """Build a validated `DisplayContext` — the ONE door (the retired
    `set_*` functions each validated their own argument; that check lives
    here now, so an unknown source/set/shade still fails loudly at the
    point of choice rather than as missing art at paint time)."""
    if art_source not in constants.ART_SOURCES:
        raise ValueError(f"unknown art source: {art_source}")
    if subdial_set not in constants.SUBDIAL_SETS:
        raise ValueError(f"unknown subdial set: {subdial_set}")
    shades = dict(constants.METAL_SHADE_DEFAULT)
    for metal, shade in (metal_shades or {}).items():
        if metal not in constants.METAL_SHADE_NAMES:
            raise ValueError(f"unknown metal: {metal}")
        if shade not in constants.METAL_SHADE_NAMES[metal]:
            raise ValueError(f"unknown shade for {metal}: {shade}")
        shades[metal] = shade
    return DisplayContext(
        art_source=art_source,
        subdial_set=subdial_set,
        metal_shades=MappingProxyType(shades),
    )


#: What a caller outside any watch's scope sees — the shipped defaults.
DEFAULT_DISPLAY = DisplayContext()

_active_display = threading.local()


def current_display() -> DisplayContext:
    """The context in force on THIS thread."""
    context = getattr(_active_display, "context", None)
    return DEFAULT_DISPLAY if context is None else context


@contextmanager
def display(context: DisplayContext):
    """Install `context` for the duration of the block — the scope every
    paint, hover, tooltip and dialog build of ONE watch runs inside.
    Nests (a dialog opened mid-paint restores the painter's context on
    exit) and is thread-local (the warm thread never disturbs the GUI)."""
    previous = getattr(_active_display, "context", None)
    _active_display.context = context
    try:
        yield
    finally:
        _active_display.context = previous


def in_display(method):
    """Decorator for the entry points of objects that carry a SKIN —
    `render.compositor.Compositor` (every dial paint, hover, tooltip and
    hit test) and `app.controller.WatchController` (every dialog it
    opens): run the method inside `self._skin.display`, so every art path
    resolved below the call belongs to THAT watch.

    One definition for both (Rule #5): the two classes name the field
    identically, and this is exactly one thread-local set and restore per
    call — cheap enough for the paint path."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with display(self._skin.display):
            return method(self, *args, **kwargs)
    return wrapper


def art_source() -> str:
    return current_display().art_source


def subdial_set() -> str:
    return current_display().subdial_set


def metal_shade(metal: str) -> str:
    return current_display().shade(metal)


# The terminal filename suffix per art source (RESTRUCTURE Naming
# Convention, 2026-07-22): the Gemini/ChatGPT split moved OFF the folder
# tree and ONTO the filename — `<Figure>[_vN]_<src>.png`, source last.
ART_SUFFIX = {"gemini": "gem", "chatgpt": "gpt"}


def art_file(path: Path | None) -> Path | None:
    """Resolve a CANONICAL (suffix-less) art path to the file that
    actually exists, trying the source SUFFIX on the FILENAME (the folder
    tree is now source-free): the active source first, the other source
    as cross-source fallback (partial ChatGPT coverage; owner 2026-07-14),
    then the suffix-less name (owner hand-made art carries no suffix).
    A path already carrying a `_gem`/`_gpt` suffix, and any non-PNG
    (SVG logos, JSON), pass through untouched. When nothing is on disk
    the canonical path returns unchanged — the caller keeps its own
    missing-art fallback (documented, Rule #1: never a silent lie)."""
    if path is None:
        return None
    # Lexical normalization first: a few call sites still reach across
    # roots with a "../" step-up (the continents Servant reaches the
    # earth family) — collapse it before touching the filename.
    path = Path(os.path.normpath(path))
    if path.suffix.lower() != ".png":
        return path
    stem = path.stem
    if stem.endswith(("_gem", "_gpt")):
        return path
    parent, ext = path.parent, path.suffix
    active = ART_SUFFIX[art_source()]
    ordered = [active] + [s for s in ART_SUFFIX.values() if s != active]
    for suffix in ordered:
        candidate = parent / f"{stem}_{suffix}{ext}"
        if candidate.exists():
            return candidate
    if path.exists():
        return path
    return path
