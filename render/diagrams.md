# Diagrams

**Script:** [Diagrams (script)](diagrams.py)

## Purpose

The ONE door to every computed diagram. Two modules draw them —
[Cube Diagrams](cube_diagrams.md) for the Cube's geometry,
[Canon Diagrams](canon_diagrams.md) for the journeys and the tables —
and a page must not have to know which one answers.

A page declares `"diagram": (kind, key)`; this facade finds the drawer.

## Connections

### Uses
- [Cube Diagrams](cube_diagrams.md), [Canon Diagrams](canon_diagrams.md)

### Used by
- [Reader Screen](../app/encyclopedia/reader.md) — draws the plate and
  scales it to the page
- `tests/test_encyclopedia_tree.py` — `kinds()` is what makes "no page
  may name a drawer nobody wrote" checkable

## Design Decisions

- **An unknown kind returns a null pixmap**, and the reader then simply
  shows the article — the same graceful-absent path a plate whose art
  has not landed already takes (Rule #1's documented exception).
- **The facade holds no drawing code.** It exists so the two drawing
  modules can stay cohesive (Rule #20) without the reader learning both.
