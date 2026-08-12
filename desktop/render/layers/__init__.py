"""The dial's layer stack — one module per layer, one responsibility each.

The compositor stacks these in Z order; every one of them subclasses
`Layer` from [Render Context](../__about/context.md) and declares the
`Cadence` at which its content changes. This package holds ONLY the
layers: the geometry, path and drawing helpers they share live beside it
in `render/` (painting, skin_geometry, shapes, slot_layout, ...).

Deliberately EMPTY of re-exports (Rule "No Backward Compatibility"):
import each layer from its own module, e.g.
`from render.layers.ring import RingLayer`.
"""
