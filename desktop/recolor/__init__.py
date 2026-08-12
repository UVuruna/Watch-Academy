"""The metal transformer — one drawn master becomes ANY metal, live,
from rules instead of from files (Rule #19). Qt-free, numpy-only, and
deliberately standalone: this package is the seed of the Colorize SVG
port, so it carries no dependency that would have to be unwritten there.

See [Recolor (folder)](___recolor.md) for the full pipeline and for the
measured autopsy of the kernel it replaces.
"""

from recolor.recipe import Metal, Recipe, Specular, Tuning, load
from recolor.transform import recolor

__all__ = ["Metal", "Recipe", "Specular", "Tuning", "load", "recolor"]
